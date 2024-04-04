# -*- coding: utf-8 -*-
import os
import socket
import time
from ..utils.data import ResponseField, RequestField
from ..utils.utils import *
import json
from io import BytesIO
from devtools import debug
writer = codecs.lookup("utf-8")[3]


class ConnectSock:
    def __init__(self, unix_socket="/var/run/docker.sock", timeout=10, debug=False,
                 headers=None, wait_socket=False, retry=3, http_version="1.0"):
        self.r_body_string = None
        self.r_headers_string = None
        self.payload = None
        self.unix_socket = unix_socket
        self.timeout = timeout
        self.method = "GET"
        self.url = "/"
        self.wait_socket = wait_socket
        self.http_version = http_version

        self.response_headers = ""
        self.response_headers_dict = {}
        self.response_body = ""

        if isinstance(headers, dict):
            self.default_headers = headers
        else:
            self.headers = {
                "Host": "*",
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            self.default_headers = self.headers

        self.sock = None
        self.debug = debug
        self._initialize_vars()
        self.connect_error = None
        self.retry = retry

        if debug:
            self.about = {}
            here = os.path.abspath(os.path.dirname(__file__))
            print(here)
            with open(os.path.join(here + "/..", '__version__.py'), mode='r', encoding='utf-8') as f:
                exec(f.read(), self.about)
            # print(f"{self.about['__title__']} v{self.about['__version__']}")

    def _initialize_vars(self):
        # self.headers = self.default_headers
        self.headers = self.default_headers.copy()
        self.r_headers = []
        self.r_headers_string = ""
        self.r_body = []
        self.r_body_string = ""
        self.return_merged_values = {}
        self.state = {}
        self.payload = {}
        self.files = {}
        self.detail = False
        self.inspect = False
        self.response_headers = ""
        self.response_headers_dict = {}
        self.response_body = ""
        self.Response = ResponseField()

    # def _decorator_check_connect(func):
    #     def connect_health_sock(self, *args, **kwargs):
    #         if self.wait_socket:
    #             wait_count = 0
    #             # while os.path.exists(self.unix_socket) is False:
    #             while self.health_check() is False:
    #                 print(f"[{wait_count}] Wait for \'{self.unix_socket}\' to be created")
    #                 time.sleep(1)
    #                 wait_count += 1
    #             # print(f"Successfully \'{self.unix_socket}\' to be created")
    #         func(self, *args, **kwargs)
    #
    #         return
    #     return connect_health_sock

    def health_check(self):
        text = {}
        error_message = ""

        self.connect_error = None
        mandatory_items = ["buildVersion", "buildTags"]
        try:
            health = self._health_check()
            if health:
                res = self.request(url="/system", method="GET")
                status_code = 200
                text = res.get_json()

                for item in mandatory_items:
                    if text.get(item) is None:
                        error_message += f"{item} not found, "
                        status_code = 500
            else:
                status_code = 500
                error_message = self.connect_error
        except Exception as e:
            error_message = e
            status_code = 500

        if error_message:
            text['error'] = error_message

        return ResponseField(status_code=status_code, text=text)

    def _health_check(self):
        if os.path.exists(self.unix_socket) is False:
            self.connect_error = f"_health_check '{self.unix_socket}' socket file not found"
            # print(red(self.connect_error))
            return False
        try:
            self.sock = None
            self._connect_sock_with_exception()
            self.sock.close()
        except Exception as e:
            self.connect_error = f"_health_check cannot connect a socket: {e}"
            # print(red(self.connect_error))
            return False
        return True

    # @_decorator_check_connect
    def _connect_sock(self, timeout=None):
        if self.wait_socket or self.retry >= 0:
            wait_count = 1
            # while os.path.exists(self.unix_socket) is False:
            while self._health_check() is False:
                message = f"[{wait_count}/{self.retry}] Wait for \'{self.unix_socket}\' to be created"
                if self.logger:
                    self.logging(message)
                else:
                    print(message)
                time.sleep(1)
                wait_count += 1
                if self.retry and isinstance(self.retry, int) and self.retry < wait_count:
                    break

            # print(f"Successfully \'{self.unix_socket}\' to be created")
            self._connect_sock_with_exception(timeout=timeout)

        elif self._health_check():
            self._connect_sock_with_exception(timeout=timeout)

        else:
            return False

    def _connect_sock_with_exception(self, timeout=None):
        if timeout:
            connect_timeout = timeout
        else:
            connect_timeout = self.timeout

        if self.unix_socket and os.path.exists(self.unix_socket):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(connect_timeout)
            sock.connect(self.unix_socket)
            self.sock = sock
        else:
            raise Exception(red(f"[ERROR] Unix Domain Socket not found - '{self.unix_socket}', wait={self.wait_socket}"))

    def _dict_key_title(self, data):
        """
        A case-insensitive ``dict``-like object.
        content-type -> Content-Type
        :param data:
        :return:
        """
        if isinstance(data, dict):
            return {k.title(): self._dict_key_title(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._dict_key_title(v) for v in data]
        else:
            return data

    def _prepare_header(self):
        self.r_headers = [
            f"{self.method} http://*{self.url} HTTP/{self.http_version}",
            # f"{self.method} {self.url} HTTP/{self.http_version}",
        ]
        if "HTTP/1.1" in self.r_headers[0]:
            self.headers['Connection'] = "close"

        if self.headers:
            for header_k, header_v in self.headers.items():
                self.r_headers.append(f"{header_k}: {header_v}")
        self.r_headers_string = "\r\n".join(self.r_headers)
        self.r_headers_string = append_new_line(self.r_headers_string, "\r\n")

    def _prepare_body(self, payload=None, files=None):

        if files:
            self.r_body_string, content_type, content_length = self.encode_multipart_formdata(files)
            self.headers['Content-Type'] = content_type
            self.headers['Content-Length'] = content_length
            self.headers['Connection'] = "close"
        elif payload:
            try:
                payload = json.dumps(payload)
                is_json = True
            except:
                is_json = False
                pass

            body_bytes = payload.encode("utf-8")

            if is_json and self.headers.get('Content-Type') is None:
                self.headers['Content-Type'] = "application/json"
            self.headers['Content-Length'] = len(body_bytes)
            self.r_body = [
                f"",
                f"{payload}"
            ]
            self.r_body_string = "\r\n".join(self.r_body)

    def get_encoded_request_data(self):
        """
        Convert header and body into a string that contains "\r\n" and is encoded.
        :return:
        """
        if not isinstance(self.r_headers_string, bytes):
            # self.r_headers_string = f"{self.r_headers_string}\r\n".encode("utf-8")
            self.r_headers_string = f"{self.r_headers_string}".encode("utf-8")
        if not isinstance(self.r_body_string, bytes):
            self.r_body_string = f"{self.r_body_string}\r\n\r\n".encode("utf-8")
            # self.r_body_string = f"{self.r_body_string}".encode("utf-8")
        return self.r_headers_string + self.r_body_string

    def encode_multipart_formdata(self, fields, boundary=None):
        """
        Encode the multipart/form-data.
        Uploaded samples.

        --9bc00c50b8fde01d0cd1e50643dbc08c \r\n
        Content-Disposition: form-data; name="json" \r\n\r\n
        JSON data
        --9bc00c50b8fde01d0cd1e50643dbc08c \r\n
        Content-Disposition: form-data; name="genesisZip"; filename="gs.zip"\r\n\r\n
        --9bc00c50b8fde01d0cd1e50643dbc08c \r\n
        multipart/form-data; boundary=9bc00c50b8fde01d0cd1e50643dbc08c

        :param fields:
        :param boundary:
        :return:
        """
        body = BytesIO()
        if boundary is None:
            boundary = choose_boundary()
        for field in iter_field_objects(fields):
            body.write(b("\r\n--%s\r\n" % (boundary)))
            writer(body).write(field.render_headers())
            data = field.data
            if isinstance(data, int):
                data = str(data)  # Backwards compatibility

            if isinstance(data, str):
                writer(body).write(data)
            else:
                body.write(data)

            body.write(b"\r\n")
        body.write(b("--%s--\r\n" % (boundary)))
        content_type = str("multipart/form-data; boundary=%s" % boundary)
        content_length = body.__sizeof__()
        self.r_body_string = body.getvalue()
        return body.getvalue(), content_type, content_length

    def _decorator_timing(func):
        """
        Decorator to get the elapsed time.
        :return:
        """

        def from_kwargs(self, **kwargs):
            start_time = time.time()
            result = func(self, **kwargs)
            end_time = round(time.time() - start_time, 3)
            # print(f"elapsed = {end_time}")
            # print(f"result = {result} , {type(result)}")
            # if isinstance(result, dict):
            #     result['result']
            if isinstance(result, ResponseField):
                result.elapsed = end_time
                # result.state = self.state
            elif isinstance(result, dict):
                result['elapsed'] = end_time
            return result

        return from_kwargs

    @_decorator_timing
    def request(self, method="GET", url=None, headers={}, payload={}, files={}, return_dict=False, timeout=None):
        """
        Create an HTTP request and send it to the unix domain socket.
        :param method:
        :param url:
        :param headers:
        :param payload:
        :param files: upload the file using 'multipart/form-data'
        :param return_dict: if response is a list type, change to dictionary => e.g., [{"cid":"232"}]  -> {"cid": "232"}
        :return:
        """
        self._initialize_vars()
        self.payload = payload
        if self.debug:
            color_print(f"unix_socket={self.unix_socket}, url={url}, method={method}, headers={headers}, payload={payload}, files={files}", "green")

        self._connect_sock(timeout=timeout)
        if self.sock:
            self.method = method.upper()

            if url:
                self.url = url

            self.headers.update(self._dict_key_title(headers))
            self._prepare_body(payload, files)
            self._prepare_header()
            request_data = self.get_encoded_request_data()

            if self.debug:
                debug("<<< request_data >>>", request_data)
            self.sock.send(request_data)
            contents = ""
            contents_bytes = b""

            while True:
                response_data = self.sock.recv(1024)
                if not response_data:
                    break
                # print(response_data.decode('utf-8'))
                # contents += str(response_data.decode())
                try:
                    contents += str(response_data.decode())
                    contents_bytes += response_data
                except UnicodeDecodeError:
                    contents_bytes += response_data

            self.response_headers, self.response_body = contents_bytes.split(b'\r\n\r\n', 1)
            # headers_str = headers.decode('utf-8')
            # print(headers_str)

            self.sock.close()
            # debug(contents)
            return self._parsing_response(contents, return_dict=return_dict)
        else:
            return ResponseField(status_code=500, text=f"[ERROR] fail to connection, {self.connect_error}")

    def _parsing_header(self):
        _headers = self.response_headers.decode('utf-8').split("\r\n")
        status = 999
        self.response_headers_dict = {}
        for _header in _headers:
            if _header.startswith("HTTP/"):
                status = _header.split(" ")[1]
            elif ":" in _header:
                header_key, header_value = _header.split(":", 1)
                self.response_headers_dict[header_key.strip()] = header_value.strip()

        self.Response.status_code = int(status)
        # debug(self.response_headers_dict)
        # # print(_headers_list)
        # # print(status)

    def _guess_filename(self, default_filename=None):
        if self.response_headers_dict.get('Content-Disposition'):
            __filename_line  = self.response_headers_dict.get('Content-Disposition').split("filename=", 1)
            if len(__filename_line) > 1:
                return self.response_headers_dict.get('Content-Disposition').split("filename=", 1)[1].replace('"', '')
        return default_filename

    def _parsing_response(self, response, return_dict=False):
        """
        Parse the response value and returns it to a ResponseField model
        :param response: raw response data
        :param return_dict: if response is a list type, change to dictionary => e.g., [{"cid":"232"}]  -> {"cid": "232"}
        :return:
        """
        self._parsing_header()

        if self.response_headers_dict.get('Content-Type') == "application/zip" and self.response_body:
            if isinstance(self.payload, dict) and self.payload.get('filename'):
                _filename = self.payload.get('filename')
            else:
                _filename = self._guess_filename("icon_default.zip")
            with open(_filename, "wb") as binary_file:
                binary_file.write(self.response_body)
                pawn.console.log(f"Download  file - {_filename}")

        if response:
            response_lines = response.split('\r\n')
            if response_lines:
                try:
                    status = response_lines[0].split(" ")[1]
                    text = self.response_body.decode("utf-8").strip()
                except:
                    status = 999
                    text = ""

                try:
                    # json_dict = json.loads(response_lines[-1])
                    json_dict = json.loads(text)
                    if return_dict and isinstance(json_dict, list):
                        json_dict = json_dict[0]
                        if text.startswith("[") and text.endswith("]"):
                            text = text.strip("[]")
                except Exception as e:
                    json_dict = {}

                # self.Response.status_code = int(status)
                self.Response.json = json_dict
                self.Response.text = text

                if isinstance(self.Response.json, dict) and self.Response.json.get('error'):
                    self.Response.error = self.Response.json['error'].get('message')

                self.debug_resp_print(self.Response)
        return self.Response
        # return self.response

    def debug_print(self, text, color="blue"):
        if self.debug:
            # version_info = f"{self.about['__title__']} v{self.about['__version__']}"
            version_info = f"v{self.about['__version__']}"
            color_print(f"[{version_info}][DBG] {text}", color)

    def debug_resp_print(self, result):
        if self.debug:
            text = result.text.split("\n")
            if result.status_code == 200:
                color = "green"
                if result.json:
                    debug(result.json)
                elif result.text:
                    debug(result.text)
            else:
                color = "fail"
            self.debug_print(f"status_code={result.status_code} url={self.url}, payload={self.payload}, files={self.files}, result={text[0]}",
                             color)

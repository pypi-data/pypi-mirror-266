from functools import partial, wraps
from .connect_sock import ConnectSock
import requests
from functools import partial

try:
    from ..__version__ import __version__
except:
    from __version__ import __version__

from ..utils.data import ResponseField, RequestField
from ..utils.utils import *
from pawnlib.config import pawn
from pawnlib.typing import StackList, TimeCalculator, timestamp_to_string


def _make_json_rpc(method="", params: dict = {}):
    return {
        "jsonrpc": "2.0",
        "id": int(datetime.now().timestamp()),
        "method": method,
        "params": params
    }


class ControlChain(ConnectSock):
    success_state = {
        "backup": "backup done",
        "prune": "pruning done",
        # "reset": "started",
        "reset": "started",
        "restore": "success",
        "start": "started",
        "stop": "stopped",
        "_just_stop": "stopped",
        "import_stop": "import_icon finished"
    }

    def __init__(
            self,
            unix_socket="/app/goloop/data/cli.sock",
            url="/", cid=None, timeout=10,
            debug=False, auto_prepare=True, wait_state=True,
            increase_sec=0.5,
            wait_socket=False,
            logger=None,
            check_args=True,
            retry=3,
            endpoint=None,
            http_version="1.0"
    ):
        """
        ChainControl class init

        :param unix_socket: Path of file based unix domain socket
        :param url: reuqest url
        :param cid: channel id for goloop
        :param timeout: Maximum time in seconds that you allow the connection to the server to take
        :param debug: debug mode
        :param auto_prepare: Prepare before execution. e.g., Backup should be done after stopping.
        :param wait_state: Wait until the required state(success_state dict) is reached.
        """

        self.headers = {
            # "Host": "localhost",
            "Host": "*",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "socket-request",
            # "Accept-Encoding": "gzip",

        }
        self.http_version = http_version

        super().__init__(unix_socket=unix_socket, timeout=timeout, debug=debug, headers=self.headers, wait_socket=wait_socket, http_version=self.http_version)
        self.url = url
        self.unix_socket = unix_socket
        self.cid = cid
        # self.action_model = ChainActionModel()

        self.payload = {}
        self.files = {}
        self.detail = False
        self.debug = debug
        self.auto_prepare = auto_prepare
        self.wait_state = wait_state
        self.state = {}
        self.gs_file = None
        self.increase_sec = increase_sec
        self.logger = logger
        self.check_args = check_args
        self.blockheight = None
        self.restore_name = None
        self.seedAddress = []
        self.retry = retry

        self.last_blockheight_number = 0
        self.last_call_count = 0
        self.endpoint = endpoint
        self.last_block = {}

        self._tps_stack = StackList(max_length=100)

        self.logging(f"Load ControlChain Version={__version__}")

        self._inside_func = None

        if self.cid is None and self._health_check():
            self.debug_print("cid not found. Guess it will get the cid.")
            self.guess_cid()
            self.debug_print(f"guess_cid = {self.cid}")

    def logging(self, message=None, level="info"):
        if self.logger:
            if level == "info" and hasattr(self.logger, "info"):
                self.logger.info(f"[SR] {message}")
            elif level == "error" and hasattr(self.logger, "error"):
                self.logger.error(f"[SR] {message}")

    def _decorator_stop_start(func):
        def stop_start(self, *args, **kwargs):
            func_name = func.__name__
            self._inside_func = func_name
            pawn.console.log(f"Starting {self._inside_func}() {args} {kwargs}")
            if func_name == "restore" and self.check_backup_file(restore_name=kwargs.get("restore_name")) is False:
                return

            if func_name == "prune" and isinstance(kwargs.get("blockheight"), int) is False:
                raise Exception(red(f"Required blockheight {kwargs.get('blockheight')}"))

            if self.auto_prepare:
                # self.stop(*args, **kwargs)
                self.stop()
                ret = func(self, *args, **kwargs)

                if func_name == "restore":
                    exec_function = self.get_restore_status
                else:
                    exec_function = self.view_chain
                if self.wait_state and self.success_state.get(func_name):
                    wait_state_loop(
                        exec_function=exec_function,
                        check_key="state",
                        wait_state=self.success_state.get(func_name),
                        increase_sec=self.increase_sec,
                        description=f"'{func_name}'",
                        logger=self.logger
                    )
                # self.start(*args, **kwargs)
                self.start()
            else:
                ret = func(self, **kwargs)
            return ret
        return stop_start

    def _decorator_wait_state(func):
        def wait_state(self, *args, **kwargs):
            func_name = func.__name__
            force_retry_loop_functions = ['stop']

            ret = func(self, *args, **kwargs)

            if func_name in force_retry_loop_functions and getattr(ret, "status_code", None) and ret.status_code != 202:
                _ret = self._wait_state_loop_on_avail(
                    func=self._just_stop,
                    expected="stopped",
                    *args, **kwargs
                )

            if self.wait_state and self.success_state.get(func_name):
                wait_state_loop(
                    exec_function=self.view_chain,
                    check_key="state",
                    wait_state=self.success_state.get(func_name),
                    increase_sec=self.increase_sec,
                    description=f"'{func_name}'",
                    logger=self.logger
                )
            return ret
        return wait_state

    def _wait_state_loop_on_avail(self, func, expected, *args, **kwargs):
        while True:
            # pawn.console.log(f"Executing func={func.__name__}, expected={expected}")
            result = func(*args, **kwargs)
            if self._check_state_on_avail(expected):
                break;
            time.sleep(0.3)
        return result

    def _check_state_on_avail(self, expected=""):
        self.get_state()
        # pawn.console.log(f"{expected}, now:{self.state.get('state')} == expected:{expected}")
        if self.state and self.state.get('state') == expected:
            return True
        return False

    def get_restore_status(self):
        return self.request(url="/system/restore",  method="GET", return_dict=True)

    def _decorator_kwargs_checker(check_mandatory=True):
        def real_deco(func):
            @wraps(func)
            def from_kwargs(self, *args, **kwargs):
                func_name = func.__name__
                if func_name != "stop_start":
                    self.debug_print(f"Start '{func_name}' function", "WHITE")

                if self.auto_prepare:
                    if func_name not in ["view_chain", "join"]:
                        self.view_chain()

                    if self.state.get("state") and self.success_state.get(func_name) == self.state.get("state"):
                        return ResponseField(status_code=202, text=f"Already {self.state.get('state')}")

                if check_mandatory is not True:
                    func_params = get_function_parameters(func)
                    func_params['kwargs'].update(**kwargs)
                    for key, value in func_params.get("kwargs").items():
                        if value is not None:
                            setattr(self, key, value)
                        default_param = getattr(self, key)

                        if (self.check_args and check_mandatory and True) \
                                and value is None \
                                and (default_param is None
                                     or default_param == {} or default_param == []):

                            raise Exception(red(f"Required '{key}' parameter for {self._inside_func}, {func_name}(), "
                                                f"func_params={func_params}, "
                                                f"self.check_args={self.check_args}, "
                                                f"default_param={default_param}"))

                    self.debug_print(f"_decorator_kwargs_checker(), kwargs = {kwargs}")
                ret = func(self, *args, **kwargs)
                self.payload = {}
                self.files = []
                self.r_headers = []
                self.r_headers_string = ""
                self.r_body = []
                self.r_body_string = ""
                self.gs_file = ""
                return ret
            return from_kwargs
        return real_deco(check_mandatory) if callable(check_mandatory) else real_deco

    @_decorator_kwargs_checker(check_mandatory=False)
    def guess_cid(self):
        # res = self.view_chain()
        res = self.request(url="/chain", payload={}, method="GET", return_dict=True)

        if res.json and res.get_json("cid"):
            self.state = res.get_json()
            self.cid = res.get_json('cid')
            return self.cid

    @_decorator_kwargs_checker
    def _kwargs_test(self, cid=None):
        print(self.cid)

    def _is_cid(self, cid=None):
        if cid:
            self.cid = cid
        if self.cid:
            return self.cid
        else:
            print("[ERROR] Required cid")
            return False

    def get_state(self):
        result = self.view_chain()
        if result.status_code == 200:
            res = self.view_chain().get_json()
            if isinstance(res, list) and len(res) == 0:
                self.state = {}
            else:
                self.state = res
                if self.state.get("cid"):
                    self.cid = self.state["cid"]
        else:
            self.state['error'] = result.text
        return self.state

    @_decorator_kwargs_checker
    @_decorator_wait_state
    def start(self, cid=None, **kwargs):
        if cid:
            self.cid = cid
        if self.cid is None:
            self.guess_cid()
        res = self.request(url=f"/chain/{self.cid}/start", payload={}, method="POST")
        return res

    @_decorator_wait_state
    @_decorator_kwargs_checker
    def stop(self, cid=None, **kwargs):
        return self._just_stop(cid)

    def _just_stop(self, cid=None):
        if cid:
            self.cid = cid
        if self.cid is None:
            self.guess_cid()
        try:
            res = self.request(url=f"/chain/{self.cid}/stop", payload={}, method="POST")
        except Exception as e:
            pawn.console.log(f"[red] Failed to stop {e}")
        return res


    @_decorator_kwargs_checker
    def import_finish(self, cid=None, **kwargs):
        if cid:
            self.cid = cid
        if self.cid is None:
            self.guess_cid()

        stop_res_1 = None
        stop_res_2 = None

        try:
            stop_res_1 = self.import_stop()
            time.sleep(3)
            stop_res_2 = self.stop()
            time.sleep(3)
            if stop_res_1.status_code == 200 and stop_res_2.status_code == 200:
                color_print("Congrats! Successfully imported")
                color_print(f"{self.get_state()}")
            else:
                color_print(f"[FAIL] stop_res_1={stop_res_1}, stop_res_2={stop_res_2}", "red")
        except Exception as e:
            color_print(f"{self.get_state()}, e={e}")
        return stop_res_2

    @_decorator_wait_state
    @_decorator_kwargs_checker
    def import_stop(self, cid=None, **kwargs):
        if cid:
            self.cid = cid
        if self.cid is None:
            self.guess_cid()

        res = self.request(url=f"/chain/{self.cid}/stop", payload={}, method="POST")
        return res

    def rpc_call(self, payload: dict = {}):
        if self.endpoint:
            pawn.console.log(f"Fetching {self.endpoint}")
            res = requests.post(url=f"{self.endpoint}/api/v3", json=payload)
            res.json = res.json()
            if isinstance(res.json, dict) and res.json.get('error'):
                res.error = f"Endpoint returns error: {res.json['error'].get('message')}"
            return res

        return self.request(url="/api/v3/icon_dex", payload=payload, method="POST")

    def _get_last_block_height(self):

        blockheight = 0
        res = self.rpc_call(
            payload=_make_json_rpc(
                method="icx_getLastBlock",
            )
        )
        if isinstance(res.json, dict):
            blockheight = res.json['result'].get('height', 0)

        return blockheight

    def _get_block_hash(self, blockheight):
        res = self.rpc_call(
            payload=_make_json_rpc(
                method="icx_getBlockByHeight",
                params={'height': hex(blockheight)}
            )
        )
        if isinstance(res.json, dict) and res.json.get('result') and res.json['result'].get('block_hash'):
            pawn.console.log(f"<block_info> "
                             f"block_height={hex(blockheight)}({blockheight:,}), "
                             f"block_hash={res.json['result']['block_hash']}, "
                             f"time_stamp={timestamp_to_string(res.json['result']['time_stamp'])} ")
            return f"0x{res.json['result']['block_hash']}"
        else:
            raise ValueError(f"{res}")
            #raise ValueError(f"{res.error}")
        ##  TODO : It will be improve the result

    # def reset_test(self, blockheight=None, cid=None):
    #     payload = {
    #         'height': 100,
    #         'blockHash': f"0xcb63709d79dbc54c7b48033411b80d966524d9dc743cfad1d6c5d4b38bd7113f"
    #     }
    #     payload = {"height":100,"blockHash":"0xcb63709d79dbc54c7b48033411b80d966524d9dc743cfad1d6c5d4b38bd7113f"}
    #     res = self.request(
    #         url=f"/chain/{self.cid}/reset", payload=payload, method="POST")
    #     # self.start(cid)
    #     return res


    @_decorator_stop_start
    @_decorator_kwargs_checker
    def _reset(self, blockheight=None, block_hash=None):
        payload = {
            'height': blockheight,
            'blockHash': block_hash
        }
        color_print(f"Reset block_height={hex(blockheight)}({blockheight:,}), blockHash={payload.get('blockHash')}")
        # self.stop(cid)
        res = self.request(
            url=f"/chain/{self.cid}/reset", payload=payload, method="POST")
        # self.start(cid)
        return res

    def reset(self, blockheight=None, cid=None):
        if cid:
            self.cid = cid

        if not self.endpoint and not self.cid:
            self.guess_cid()

        block_hash = self._get_block_hash(blockheight)
        if not block_hash:
            raise ValueError(f"block_hash not found, blockheight={blockheight}")
        self._reset(blockheight=blockheight, block_hash=block_hash)

    def import_icon(self, payload=None):
        res = self.request(
            url=f"/chain/{self.cid}/import_icon",
            payload=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        self.guess_cid()
        return res

    @_decorator_kwargs_checker
    def join(self,
             seedAddress=[],
             role=3,
             maxBlockTxBytes=2048000,
             normalTxPool=10000,
             channel="icon_dex",
             autoStart=True,
             platform="icon",
             gs_file="config/icon_genesis.zip",
             dbType="rocksdb",
             txTimeout=60000,
             nodeCache="small"
             ):

        config_payload = dict(
            seedAddress=",".join(seedAddress),
            role=int(role),
            maxBlockTxBytes=int(maxBlockTxBytes),
            normalTxPool=int(normalTxPool),
            channel=channel,
            autoStart=autoStart,
            platform=platform,
            dbType=dbType,
            txTimeout=int(txTimeout),
            nodeCache=nodeCache
        )

        pawn.console.debug(config_payload, self.gs_file)

        if not seedAddress:
            raise Exception(red(f"[ERROR] seedAddress is None"))

        if not os.path.exists(self.gs_file):
            raise Exception(red(f"[ERROR] Genesis file not found - '{gs_file}'"))

        with open(gs_file, "rb") as genesis_fd:
            fd_data = genesis_fd.read()

        files = {
            "json": (None, json.dumps(config_payload)),
            "genesisZip": (os.path.basename(gs_file), fd_data)
        }

        res = self.request(url=f"/chain", payload={}, method="POST", files=files)
        self.guess_cid()
        debug(res.status_code)
        return res
        # else:
        #     print(f"[ERROR] Required files")

    # @_decorator_kwargs_checker
    def leave(self, cid=None):
        if cid:
            self.cid = cid
        if self.cid is None:
            self.guess_cid()

        if self.cid is None:
            return ResponseField(status_code=400, text=f"Already leave, cid not found")

        res = self.request(url=f"/chain/{self.cid}", payload={}, method="delete")
        return res

    @_decorator_kwargs_checker
    @_decorator_stop_start
    def backup(self, cid=None):
        res = self.request(url=f"/chain/{self.cid}/backup", payload={}, method="POST")
        return res

    @_decorator_kwargs_checker
    def backup_list(self, cid=None):
        res = self.request(url=f"/system/backup", payload={}, method="GET")
        return res

    def check_backup_file(self, restore_name):
        backup_list = self.backup_list()
        is_backup_file = False
        for backup_item in backup_list.json:
            if isinstance(backup_item, dict) and backup_item.get("name") == restore_name:
                is_backup_file = True

        if is_backup_file is False:
            raise Exception(red(f"[ERROR] Unable to restore file, backup file not found -> {restore_name}"))

        return is_backup_file


    @_decorator_kwargs_checker
    @_decorator_stop_start
    def restore(self, restore_name=None, cid=None):

        if restore_name:
            payload = {
                "name": restore_name,
                "overwrite": True
            }
            res = self.request(url=f"/system/restore", payload=payload, method="POST")
            return res
        else:
            print(f"[ERROR] restore_name not found")
            # sys.exit(127)

    @_decorator_kwargs_checker
    @_decorator_stop_start
    def prune(self, blockheight=None):
        if blockheight and blockheight >= 0:
            payload = {
                # "dbType": "rocksdb",
                # "dbType": "goleveldb",
                "height": blockheight
            }
            res = self.request(url=f"/chain/{self.cid}/prune", payload=payload, method="POST")
            return res
        else:
            print(f"[ERROR] height is {blockheight}")
            sys.exit(127)

    def genesis(self, blockheight=None):
        payload = {
            # "cid": self.cid,
            "filename": "genesis.zip"
        }

        res = self.request(url=f"/chain/{self.cid}/genesis", payload=payload, method="GET")
        return res

    def _append_compare_blockheight(self):
        if self.last_call_count % 20 == 0:
            self.last_blockheight_number = self._get_last_block_height()
            self.last_call_count = 0

        if self.state:
            self.state['left_height'] = self.last_blockheight_number - self.state['height']
            self.state['last_height'] = self.last_blockheight_number
            if self._tps_stack.mean() > 3:
                try:
                    self.state['left_time'] = TimeCalculator(self.state['left_height'] / self._tps_stack.mean())
                except Exception as e:
                    pawn.console.log(f"[red] exception - {e}")
            else:
                self.state['left_time'] = ""

        self.last_call_count += 1

    def view_chain(self, cid=None, detail=False, inspect=False, compare=False):

        payload = {}
        if cid:
            self.cid = cid

        if self.cid and inspect:
            url = f"/chain/{self.cid}"
            # payload = {"informal": "true"}
        elif self.cid and detail:
            url = f"/chain/{self.cid}/configure"

        else:
            url = f"/chain"
        res = self.request(url=url, payload=payload, method="GET", return_dict=True)

        if res.status_code != 200:
            self.logging(f"view_chain res.status_code={res.status_code}, res = {res.text}")
        if hasattr(res, 'json'):
            self.state = res.json
            try:
                self.get_tps()
                res.set_dict(self.state)
                if compare and self.endpoint:
                    self._append_compare_blockheight()

            except:
                pass
            # self.connect_error = res.get('error')
        else:
            self.state = {}
            self.connect_error = res.text
        return res

    def get_tps(self):
        if self.state.get("height"):
            if self.last_block.get('height') is None:
                self.last_block = {
                    "height": self.state.get("height"),
                    "time": time.time()
                }

            diff_block = self.state['height'] - self.last_block['height']
            diff_time = time.time() - self.last_block['time']
            tps = diff_block / diff_time
            # print(diff_block, diff_time, tps)
            self._tps_stack.push(tps)

            self.state['tps'] = round(tps)
            self.last_block = {
                "height": self.state.get("height"),
                "time": time.time()
            }

    def multi_payload_request(self, url=None, payload=None, method="POST"):
        result = {
            "state": "OK",
            "payload": payload,
            "error": []
        }
        status_code = 201

        if not isinstance(payload, dict):
            raise Exception(red(f"[ERROR] Invalid payload '{payload}'"))

        if payload.get("key") and payload.get("value"):
            return self.request(url=f"/chain/{self.cid}/configure",  payload=payload, method="POST")

        for key, value in payload.items():
            if isinstance(value, bool):
                value = bool2str(value)
            elif isinstance(value, int):
                value = str(value)
            elif isinstance(value, float):
                value = str(value)

            debug(key, value) if self.debug else False
            each_payload = {"key": key, "value": value}
            res = self.request(url=url, payload=each_payload,  method=method)
            debug(res) if self.debug else False

            if res.status_code != 200:
                if len(res.text) > 1:
                    return_text = res.text.split("\n")[0]
                else:
                    return_text = res.text
                result['error'].append({
                    "key": key,
                    "value": value,
                    "message": return_text
                })
                result['state'] = "FAIL"
                status_code = 400
        return ResponseField(status_code=status_code, text=result)

    @_decorator_kwargs_checker
    @_decorator_stop_start
    def chain_config(self, payload=None):
        return self.multi_payload_request(url=f"/chain/{self.cid}/configure", payload=payload, method="POST")

    # def view_system_config(self, detail=True, inspect=False):
    def view_system_config(self, detail=True):
        if detail:
            url = "/system"
        else:
            url = "/system/configure"
        res = self.request(url=url,  method="GET")
        return res

    @_decorator_kwargs_checker
    def system_config(self, payload=None):
        payload = payload_bool2string(payload)
        return self.multi_payload_request(url="/system/configure", payload=payload, method="POST")


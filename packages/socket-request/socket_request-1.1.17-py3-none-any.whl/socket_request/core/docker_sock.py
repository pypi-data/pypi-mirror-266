# -*- coding: utf-8 -*-
from .connect_sock import ConnectSock
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
# import pandas as pd
from devtools import debug
import concurrent.futures
# import aiometer
import asyncio
# from functools import partial

class DockerSock(ConnectSock):
    def __init__(
            self,
            unix_socket="/var/run/docker.sock",
            url="/",
            timeout=5,
            debug=False,
            auto_prepare=False,
            wait_state=False,
            simple_name=True,
            logger=None,
            default_return_keys=[]

    ):
        super().__init__(unix_socket=unix_socket, timeout=timeout, debug=debug)

        self.return_merged_values = None
        self.url = url
        self.unix_socket = unix_socket
        # self.action_model = ChainActionModel()
        self.headers = {
            "Host": "*",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "socket-request"
        }
        self.payload = {}
        self.files = {}
        self.detail = False
        self.debug = debug
        self.simple_name = simple_name
        self.auto_prepare = auto_prepare
        self.wait_state = wait_state
        self.logger = logger
        if default_return_keys:
            self.default_return_keys = default_return_keys
        else:
            self.default_return_keys = ["Image", "State", "Status"]
        self.container_list = []
        self.return_keys = list(set(self.default_return_keys) | {"Id", "Names"})
        self.return_lower_keys = [key.lower() for key in self.return_keys]
        self.stats_keys = ["used_memory", "available_memory", "memory_usage", "number_cpus", "cpu_usage"]
        self.columns = self.return_lower_keys + self.stats_keys


    ## TODO:  It will be REMOVE
    def get_docker_images(self, return_type="each", simple_name=True):
        return self.get_containers(return_type=return_type, simple_name=simple_name)

    def get_containers(self, return_type="each", simple_name=None, return_keys=[]):
        if simple_name is not None:
            self.simple_name = simple_name
        response = self.call_api(url="/containers/json")
        return_keys = list(set(self.default_return_keys) | set(return_keys))
        return_values = []
        # debug(self.Response.json)
        if response.json:
            for image in self.Response.json:
                image_info = {}
                for key in return_keys:
                    image_info[key.lower()] = image.get(key)
                return_values.append(image_info)

        if return_type == "merge" and len(return_values) > 0:
            self.return_merged_values = {key: "" for key in return_values[0].keys()}
            for values in return_values:
                for r_key, r_val in values.items():
                    # self._merge_value(r_key, self.get_simple_image_name(r_val))
                    self._merge_value(r_key, r_val)

            return self.return_merged_values

        return return_values

    def call_api(self, url=None, method="GET", headers={}, payload={}, files={}, return_dict=False, timeout=None):
        if len(headers) == 0 and self.headers:
            headers = self.headers
        response = self.request(url=url, method=method, headers=headers, payload=payload, files=files, return_dict=return_dict, timeout=timeout)
        if self.simple_name:
            # debug(self.Response.json)
            if isinstance(self.Response.json, list):
                for item_value in self.Response.json:
                    for k, v in item_value.items():
                        if isinstance(v, list):
                            # debug(k)
                            # debug(v)
                            if k == "Names":
                                item_value[k] = "".join(v)
                            else:
                                item_value[k] = "".join(str(v))

                        if isinstance(item_value[k], str) and "/" in item_value[k]:
                            item_value[k] = item_value[k].split("/")[-1]
                        if k.lower() == "id":
                            item_value[k] = v[:12]

        # return self.Response
        return response

    def get_stats(self, container_id=None):
        return_keys = list(set(self.default_return_keys) | {"Id", "Names"})
        return_lower_keys = [key.lower() for key in return_keys]
        stats_keys = ["used_memory", "available_memory", "memory_usage", "number_cpus", "cpu_usage"]
        # columns = return_lower_keys + stats_keys
        # df = pd.DataFrame(columns=columns)
        # df = []
        containers = self.get_containers(return_keys=return_keys)
        return_result = []

        for container in containers:
            response = self.call_api(url=f"/containers/{container['id']}/stats?stream=false")
            stats = response.json
            used_memory = stats['memory_stats']['usage'] - stats['memory_stats']['stats'].get('cache', 0)
            available_memory = stats['memory_stats']['limit']
            memory_usage = (used_memory / available_memory) * 100.0
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats'].get('system_cpu_usage', 0)
            number_cpus = stats['cpu_stats']['online_cpus']

            stats_dict = {
                "used_memory": used_memory,
                "available_memory": available_memory,
                "memory_usage": memory_usage,
                "number_cpus": number_cpus,
                "cpu_usage": (cpu_delta / system_cpu_delta) * number_cpus * 100.0
            }
            stats_dict = dict(stats_dict, **{key: container[key] for key in return_lower_keys if container.get(key)})
            return_result.append(stats_dict)

            # df = df.append(stats_dict)

        # if container_id:
        #     return df.query(f"id == '{container_id}'")
        return return_result

    def get_async_proc(self):
        asyncio.run(self.get_async_stats())

    async def get_async_stats(self, container_id=None):
        self.container_list = self.get_containers(return_keys=self.return_keys)
        tasks = []
        results = []
        t = debug.timer(name='foobar', verbose=True).start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            data = []
            future_to_url = {executor.submit(self.get_container_stats, container): container for container in self.container_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                # print(url)
                try:
                    data = future.result()
                except Exception as exc:
                    print(exc)
            results.append(data)

        t.summary(verbose=True)
        return results

    def get_container_stats(self, container):
        stats = self.call_api(url=f"/containers/{container['id']}/stats?stream=false")
        print(stats)
        used_memory = stats['memory_stats']['usage'] - stats['memory_stats']['stats'].get('cache', 0)
        available_memory = stats['memory_stats']['limit']
        memory_usage = (used_memory / available_memory) * 100.0
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats'].get('system_cpu_usage', 0)
        number_cpus = stats['cpu_stats']['online_cpus']

        stats_dict = {
            "used_memory": used_memory,
            "available_memory": available_memory,
            "memory_usage": memory_usage,
            "number_cpus": number_cpus,
            "cpu_usage": (cpu_delta / system_cpu_delta) * number_cpus * 100.0
        }
        stats_dict = dict(stats_dict, **{key: container[key] for key in self.return_lower_keys if container.get(key)})
        # return_result.append(stats_dict)
        # self.df = self.df.append(stats_dict, ignore_index=True)
        return stats_dict

    def get_simple_image_name(self, name):
        if self.simple_name:
            if isinstance(name, list):
                name = "".join(name)
            if "/" in name:
                name_arr = name.split("/")
                return name_arr[-1]
        return name

    def _merge_value(self, key, value, separator="|"):
        # jmon_lib.cprint(self.return_merged_values.get(key))
        prev_value = self.return_merged_values.get(key)
        if prev_value:
            self.return_merged_values[key] = f"{prev_value}{separator}{value}"
        else:
            self.return_merged_values[key] = f"{value}"

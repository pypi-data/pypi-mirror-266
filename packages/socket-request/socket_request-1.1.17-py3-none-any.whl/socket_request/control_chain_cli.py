# -*- coding: utf-8 -*-
import sys
import argparse
from pawnlib.config import pawn, pconf
from pawnlib.typing import sys_exit

import socket_request

import json
from devtools import debug
try:
    from .__version__ import __version__
except:
    from __version__ import __version__
import time

import os
from pawnlib.utils import NetworkInfo

is_docker = os.environ.get("IS_DOCKER", False)
AVAIL_PLATFORM = ["icon", "havah"]


def get_base_dir(args=None):
    if args and args.base_dir:
        base_dir = args.base_dir
    elif socket_request.str2bool(is_docker):
        base_dir = "/goloop"
    else:
        guess_sock = "data/cli.sock"
        if socket_request.ConnectSock(unix_socket=guess_sock)._health_check():
            return "."

        guess_base_dir = ["/app/icon2-node", "/app/goloop", "/app/havah-node", "/app/havah_node_docker"]

        base_dir = guess_base_dir[0]
        for dir_name in guess_base_dir:
            if os.path.exists(dir_name):
                base_dir = dir_name
    return base_dir


def get_parser():
    parser = argparse.ArgumentParser(
        description='Command Line Interface for control_chain',
        fromfile_prefix_chars='@'
    )
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'reset', 'leave', 'view_chain', 'view_system_config', 'join', 'backup', 'backup_list', 'restore',
                 'chain_config', 'system_config', 'ls', 'prune', 'genesis', 'rpc_call'],
        help='')

    parser.add_argument('-d', '--debug', action='store_true', help=f'debug mode. (default: False)', default=False)
    parser.add_argument('-t', '--timeout', metavar='timeout', type=int, help=f'timeout (default: 60)', default=60)

    parser.add_argument('-w', '--wait-state', metavar='wait_state', type=socket_request.str2bool, help=f'wait_state (default: True)', default=True)
    parser.add_argument('-r', '--retry', metavar='retry', type=int, help=f'wait_state (default: True)', default=0)

    parser.add_argument('-ws', '--wait-socket', action='store_false',  help=f'wait for unix domain socket',  default=True)
    parser.add_argument('-ap', '--auto_prepare', metavar='auto_prepare', help=f'auto_prepare (default: True)', default=True)

    parser.add_argument('-p', '--payload', metavar='payload_file', help=f'payload file', type=argparse.FileType('r'), default=None)
    parser.add_argument('-f', '--forever', action='store_true',  help=f'retry forever', default=False)
    parser.add_argument('-i', '--inspect', action='store_true',  help=f'inspect for view chain', default=False)
    parser.add_argument('--seedAddress', type=str, help=f'seed list string', default=None)
    parser.add_argument('-b', '--base-dir', type=str, help=f'base dir for goloop', default=None)
    parser.add_argument('-bh', '--blockheight', metavar="block height number", type=int, help=f'BlockHeight for pruning', default=None)
    parser.add_argument('-rn', '--restore-name', metavar="backed up file name", type=str, help=f'Restore filename for restore', default=None)
    # parser.add_argument('-gs',  metavar="gs", type=str, help=f'genesis file for join', default=None)

    parser.add_argument('-pd', '--payload-dict', metavar='payload dict', help=f'payload dict', type=json.loads, default=None)
    parser.add_argument('--interval', type=float,  help=f'retry interval time (seconds)', default=1)

    parser.add_argument('--endpoint', metavar='endpoint url', help=f'endpoint url', type=str, default=None)
    parser.add_argument('--cid', metavar='cid', help=f'cid', type=str, default=None)
    parser.add_argument('--gs-file', metavar='gs_file', help=f'genesis file', type=str, default=None)
    parser.add_argument('--platform', metavar='platform', help='platform of goloop', type=str, default=os.environ.get('PLATFORM', 'icon'), choices=AVAIL_PLATFORM)
    parser.add_argument('--channel', metavar='channel', help='channel name of goloop', type=str, default=os.environ.get('CHANNEL_NAME', 'icon_dex'))
    parser.add_argument('--role', metavar='role', help='role of goloop', type=int, default=os.environ.get('ROLE', 0), choices=[0, 1, 3])

    parser.add_argument('-c', '--compare',  help='compare blockheight endpoint', action='store_true', default=False)
    parser.add_argument('-s', '--unixsocket', metavar='unixsocket', help=f'unix domain socket path (default: {get_base_dir()}/data/cli.socket)',
                        default=f"{get_base_dir()}/data/cli.sock")

    return parser.parse_args()


def parse_environment():
    platform = os.getenv('PLATFORM', None)
    service = os.getenv('SERVICE', None)
    if platform:
        if platform not in AVAIL_PLATFORM:
            sys_exit(f"Invalid platform env, input={platform}, allows={AVAIL_PLATFORM}")
        pconf().args.platform = platform
    else:
        platform = pconf().args.platform

    if platform and service:
        service = service.lower()
        if service == "veganet":
            service = "vega"
        elif service == "denebnet":
            service = "deneb"
        network_info = NetworkInfo(platform=platform, network_name=service)
        if not pconf().args.endpoint:
            pconf().args.endpoint = network_info.network_api
            pawn.console.log(f"Set endpoint, service={service}")


def print_banner(args):
    text = """
    ╋╋╋╋╋╋╋╋╋┏┓╋╋╋╋╋┏┓╋╋╋╋┏┓
    ╋╋╋╋╋╋╋╋┏┛┗┓╋╋╋╋┃┃╋╋╋╋┃┃
    ┏━━┳━━┳━╋┓┏╋━┳━━┫┃╋┏━━┫┗━┳━━┳┳━┓
    ┃┏━┫┏┓┃┏┓┫┃┃┏┫┏┓┃┃╋┃┏━┫┏┓┃┏┓┣┫┏┓┓
    ┃┗━┫┗┛┃┃┃┃┗┫┃┃┗┛┃┗┓┃┗━┫┃┃┃┏┓┃┃┃┃┃
    ┗━━┻━━┻┛┗┻━┻┛┗━━┻━┛┗━━┻┛┗┻┛┗┻┻┛┗┛    
    """
    print(text)
    print(f"\t platform: {args.platform}\n")
    print(f"\t version : {__version__}")
    if socket_request.str2bool(is_docker):
        print(f"\t is_docker: {is_docker}")
    print(f"\t base_dir: {get_base_dir(args)}")
    print(f"\t unixsocket: {args.unixsocket}\n\n")


def check_required(command=None):
    required_params = {
        "payload": ["import_icon", "chain_config", "system_config", "rpc_call"],
        "inspect": ["view_chain", "view_system_config"],
        "seedAddress": ["join"],
        "role": ["join"],
        "channel": ["join"],
        "platform": ["join"],
        "compare": ["view_chain"],
        "gs_file": ["join"],
        "blockheight": ["prune", "reset"],
        "restore_name": ["restore"],

    }

    required_keys = []

    for required_key, required_cmd in required_params.items():
        if command in required_cmd:
            required_keys.append(required_key)

    return required_keys


def get_unixsocket(args):
    if os.environ.get("GOLOOP_NODE_SOCK") and os.path.isfile(os.environ.get("GOLOOP_NODE_SOCK")):
        return os.environ.get("GOLOOP_NODE_SOCK")


def run_function(func, required_keys, args):
    payload = None
    gs_file = None
    seedAddress = None
    result = None
    platform = None
    role = None

    if args.payload:
        if isinstance(args.payload, dict):
            inspect = args.payload
        else:
            json_data = args.payload.read()
            if json_data:
                try:
                    payload = json.loads(json_data)
                except Exception as e:
                    raise Exception(f"Invalid JSON - {e}, json_data={json_data}")

    if isinstance(args.payload_dict, dict):
        payload = args.payload_dict

    if args.seedAddress:
        seedAddress = args.seedAddress.split(",")
        if args.gs_file:
            gs_file = args.gs_file
        else:
            gs_file = f"{get_base_dir(args)}/config/icon_genesis.zip"

    if args.platform:
        platform = args.platform

    if args.role != "":
        role = args.role

    if args.channel != "":
        channel = args.channel

    if args.command == "view_chain":
        compare = args.compare

    must_have_params_command = ["prune", "restore", "reset", "chain_config", "system_config"]

    if required_keys:
        arguments = {}
        for required_arg in required_keys:
            if args.debug:
                debug(locals())
            if locals().get(required_arg, "__NOT_DEFINED__") != "__NOT_DEFINED__":
                arguments[required_arg] = locals()[required_arg]
            elif args.command in must_have_params_command:
                try:
                    arguments[required_arg] = getattr(locals().get("args"), required_arg)
                except Exception as e:
                    print(f"Exception -- {e}")
                    pass

        if args.debug:
            debug(required_arg)
            debug(arguments)

        if payload and func.__name__ in ['join']:
            arguments.update(payload)

        if len(arguments) > 0:
            result = func(**arguments)
        else:
            result = func()
    else:
        result = func()
    return result


def main():
    args = get_parser()
    pawn.set(args=args)

    view_table_format = ["backup_list"]

    try:
        parse_environment()
    except Exception as e:
        pawn.console.debug(f'[yellow] {e}')

    try:
        if args.debug:
            print(args)
        if os.environ.get("GOLOOP_NODE_SOCK"):
            args.unixsocket = os.environ.get("GOLOOP_NODE_SOCK")
        elif args.base_dir:
            args.unixsocket = f"{args.base_dir}/data/cli.sock"
        else:
            args.base_dir = get_base_dir()
        print_banner(args)
        if args.inspect:
            args.payload = {"inspect": args.inspect}
        if args.command == "import_icon" and args.payload is None:
            args.payload = open(f"{args.base_dir}/config/import_config.json")

        cc = socket_request.ControlChain(
            unix_socket=args.unixsocket,
            # cid=cid,
            debug=args.debug,
            auto_prepare=args.auto_prepare,
            wait_state=args.wait_state,
            timeout=args.timeout,
            wait_socket=args.wait_socket,
            retry=0,
            endpoint=args.endpoint
        )

        if args.command == "ls":
            args.command = "view_chain"

        func = getattr(cc, args.command)
        required_keys = check_required(args.command)
        pawn.console.log(f"command = {args.command}")
        if args.debug:
            print(f"command = {args.command},  required_keys = {required_keys}")
        while True:
            # if args.debug:
            #     debug(locals())
            result = run_function(func, required_keys, args)
            result_text = None
            if result:
                if args.inspect:
                    socket_request.dump(result.json)
                else:
                    if result:
                        if result.status_code >= 300:
                            text_color = "RED"
                        else:
                            text_color = "GREEN"

                        if result.json:
                            result_text = result.json
                        elif result.text:
                            result_text = result.text

                        if args.command in view_table_format:
                            socket_request.print_table(title=f"{args.command} result", source_dict=result_text)
                        else:
                            socket_request.color_print(f"{result_text}", text_color)
                        if text_color == "RED":
                            socket_request.color_print(str(cc.get_state()))
                    else:
                        socket_request.color_print(f"return {result}")

            else:
                print(cc.view_chain())
                print(result)
                socket_request.color_print(f"[ERROR] {args.command}, {result.text}", "FAIL")

            if args.forever is False:
                sys.exit()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        socket_request.color_print("KeyboardInterrupt", "FAIL")
    except Exception as e:
        if pawn.get("PAWN_DEBUG"):
            pawn.console.print_exception(show_locals=pawn.get("PAWN_DEBUG", False), width=160)
        else:
            pawn.console.log(cc.state)
            pawn.console.log(f"[red]Exception occurred[/red]: {e}")


if __name__ == "__main__":
    sys.exit(main())

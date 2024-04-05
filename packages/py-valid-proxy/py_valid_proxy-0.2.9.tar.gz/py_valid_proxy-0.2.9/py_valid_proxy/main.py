# -*- coding: utf-8 -*-
# @Author: Suvorinov Oleg
# @Date:   2023-11-13 11:20:47
# @Last Modified by:   Suvorinov Oleg
# @Last Modified time: 2024-04-04 10:46:27

import sys
import argparse
import pkg_resources
import re

from rich.console import Console

from py_valid_proxy import valid_proxy


def valid_proxy_ip(ip: str) -> bool:
    # regex = r"^(http|https|socks4|socks5):\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"  # noqa
    regex = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"  # noqa
    matches = re.findall(regex, ip, re.MULTILINE)
    if matches:
        return True
    return False


def main(args=None):

    _prog = "%(prog)s"
    _version = pkg_resources.get_distribution('py_valid_proxy').version
    _prog_version = f"{_prog} {_version}"

    parser = argparse.ArgumentParser(
        prog='valid_proxy',
        description="Valid the functionality of the proxy server"
    )

    parser.add_argument(
        '-ip',
        type=str,
        required=True,
        help='IP address of proxy server')

    parser.add_argument(
        '-p',
        type=int,
        required=True,
        help='PORT of proxy server')

    parser.add_argument(
        '-s',
        type=str,
        choices=['http', 'https'],
        default='http',
        help='SCHEME of proxy server')

    parser.add_argument(
        '-t',
        type=int,
        default=5,
        help='The connect timeout is the number of seconds')

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=_prog_version
    )

    args = parser.parse_args()

    console = Console()

    if args.ip:
        if not valid_proxy_ip(args.ip):
            console.print(
                f"Oops, something is wrong with the proxy IP {args.ip}",
                style="red"
            )
            sys.exit(1)

    timeout = 5
    if args.t:
        timeout = args.t

    try:
        with console.status("Validates..."):
            proxy = valid_proxy(args.ip, args.p, args.s, timeout)  # noqa
    except Exception:
        console.print(f"{args.s}://{args.ip}:{args.p} ... is dead", style="bold red") # noqa
    else:
        console.print(f"{args.s}://{args.ip}:{args.p} ... is alive", style="bold green") # noqa
        console.print(f"anonymity: {proxy.anonymity}")
        console.print(f"country: {proxy.country}")
        console.print(f"response time: {proxy.response_time} (secs)")


if __name__ == '__main__':
    main()

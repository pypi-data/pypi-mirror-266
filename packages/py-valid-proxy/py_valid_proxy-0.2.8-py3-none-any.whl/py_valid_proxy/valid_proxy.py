# -*- coding: utf-8 -*-
# @Author: Suvorinov Oleg
# @Date:   2023-11-19 13:52:25
# @Last Modified by:   Suvorinov Oleg
# @Last Modified time: 2024-04-04 10:39:33

import os
import time
import re
from typing import List
from datetime import datetime
import json
from dataclasses import dataclass, field

import geoip2.database
import requests
from dataclasses_json import dataclass_json

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"  # noqa


class ValidProxyException(
        requests.exceptions.MissingSchema,
        requests.exceptions.InvalidSchema,
        requests.exceptions.ReadTimeout,
        requests.exceptions.InvalidProxyURL,
        requests.exceptions.ProxyError,
        requests.exceptions.JSONDecodeError):
    pass


now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


@dataclass_json
@dataclass
class Proxy:
    scheme: str = field(default='http')
    host: str = field(default='')
    port: int = field(default=80)
    export_address: List[str] = field(default_factory=list)
    anonymity: str = field(default='transparent')
    country: str = field(default='US')
    response_time: float = field(default=0.0)
    to_from: str = field(default='')
    last_checked: str = field(default=now)


def get_origin_ip(timeout: int = 5) -> str:
    try:
        resp = requests.get(
            'http://httpbin.org/get',
            headers={"User-Agent": USER_AGENT},
            timeout=timeout
        ).json()
    except ValidProxyException:
        return ''
    return resp.get('origin', '')


def valid_proxy_ip(ip_address: str) -> bool:
    match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip_address) # noqa

    if not bool(match):
        return False

    bytes = ip_address.split(".")
    for ip_byte in bytes:
        if int(ip_byte) < 0 or int(ip_byte) > 255:
            return False
    return True


def valid_proxy(
        host: str,
        port: int,
        scheme: str = 'http',
        timeout: int = 5) -> Proxy:
    """Valid proxy server ('alive' or 'dead')

    Parameters
    ----------
    host : str
        IP Address
    port : int
        Port
    scheme: str, optional
        Scheme (default is 'http')
    timeout: int, optional
        Connect timeout is number of seconds (default is 5 sec.)
    Returns
    -------
        None if proxy is 'dead'
        class Proxy if proxy is 'alive'
    """
    _proxy = None
    if not valid_proxy_ip(host): 
        raise ValidProxyException

    origin_ip = get_origin_ip()

    def _anonymity(origin_ip, response) -> str:
        via = response.get('headers', {}).get('Via', '')

        if origin_ip in json.dumps(response):
            return 'transparent'
        elif via and via != "1.1 vegur":
            return 'anonymous'
        else:
            return 'high_anonymous'

    def _export_address(origin_ip, response) -> str:
        origin = response.get('origin', '').split(', ')
        if origin_ip in origin:
            origin.remove(origin_ip)
        return origin

    def _country(host):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        try:
            geoip_reader = geoip2.database.Reader(
                os.path.join(base_dir, 'data/GeoLite2-Country.mmdb')
            )
            country = geoip_reader.country(host).country.iso_code
        except Exception:
            country = "unknown"
        return country

    request_begin = time.time()

    request_proxies = {
        scheme: "%s:%s" % (host, port)
    }

    url = "%s://httpbin.org/get?show_env=1&cur=%s" % ('http', request_begin)
    try:
        _r = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            proxies=request_proxies,
            timeout=timeout
        ).json()
    except ValidProxyException:
        return _proxy

    request_end = time.time()
    _proxy = Proxy(
        scheme,
        host,
        port,
        _export_address(origin_ip, _r),
        _anonymity(origin_ip, _r),
        _country(host),
        round(request_end - request_begin, 2)  # response_time
    )

    return _proxy

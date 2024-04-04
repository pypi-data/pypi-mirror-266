# py-valid-proxy

### Installation

```
pip install py-valid-proxy
```

### Usage

``` python
import pprint
from py_valid_proxy import valid_proxy

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
proxy_info = valid_proxy('8.219.97.248', 80, 'https', 10)
if proxy_info:
	print('is alive')
	pprint(proxy_info)
else:
	print('is dead')
```

```shell
$ valid_proxy -ip 12.186.205.120 -p 80 -s http
http://12.186.205.120:80 ... is alive
anonymity: high_anonymous
country: US
response time: 4.71 (secs)

$ valid_proxy -ip 12.186.205.120 -p 80 -s https 
https://12.186.205.120:80 ... is alive
anonymity: transparent
country: US
response time: 0.5 (secs)

$ valid_proxy -ip 2.189.59.54 -p 80
http://2.189.59.54:80 ... is dead
```
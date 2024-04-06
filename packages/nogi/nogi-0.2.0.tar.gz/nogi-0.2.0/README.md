# Nogi

![Build](https://github.com/4383/nogi/actions/workflows/python-app.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/nogi.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nogi.svg)
![PyPI - Status](https://img.shields.io/pypi/status/nogi.svg)
[![Downloads](https://pepy.tech/badge/nogi)](https://pepy.tech/project/nogi)
[![Downloads](https://pepy.tech/badge/nogi/month)](https://pepy.tech/project/nogi/month)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

Toogleable events auditor for Python apps.

Live monitor Python events and user defined custome events in running
Python applications.

Nogi allow you to audit your code without adding debug tracing and invasive
prints. Just instantiate Nogi in your code and then send a signal to your
running app to start auditing it.

Nogi allow you to enable and disable audit without restarting your application
and so without loosing the context that you want to observe, by example a
occuring bug.

See the example below.

For further details please [read the official documentation](https://nogi.readthedocs.org)

## Install

`$ pip install nogi`

## Usages

Simply instanciate `Nogi` at the begining of your code:

```python
Nogi()
```

## Example

Here is a concret example (see [examples/sample.py](examples/sample.py)):

```python
# sample.py
import requests
import time

from nogi import Nogi

Nogi()

def main():
    for i in range(1000):
        r = requests.get(
            "https://en.wikipedia.org/wiki/Python_(programming_language)")
        print(r.status_code)
        time.sleep(1)

if __name__ == "__main__":
    main()
```

Run the previous code:

```
$ python examples/sample.py
200
200
...
200
...
```

Then enable the audit by sending the `SIGUSR1` to the process previously
launched:

```
$ ps ax | grep python | grep sample # to retrieve the process id (pid)
$ kill -SIGUSR1 <pid>
```

We are now able to collect events by running the Nogi client:

```
$ nogi
Starting the audit listener
Audit client listening...
event: socket.getaddrinfo
data: ('en.wikipedia.org', 443, 0, 1, 0)
event: socket.__new__
data: (<socket.socket fd=-1, family=0, type=0, proto=0>, 2, 1, 6)
event: socket.connect
data: (<socket.socket fd=4, family=2, type=1, proto=6, laddr=('0.0.0.0', 0)>, ('185.15.58.224', 443))
event: http.client.connect
data: (<urllib3.connection.HTTPSConnection object at 0x7f0b48fafbf0>, 'en.wikipedia.org', 443)
event: socket.__new__
data: (<ssl.SSLSocket fd=-1, family=0, type=0, proto=0>, 2, 1, 6)
event: http.client.send
data: (<urllib3.connection.HTTPSConnection object at 0x7f0b48fafbf0>, b'GET /wiki/Python_(programming_language) HTTP/1.1\r\nHost: en.wikipedia.org\r\nUser-Agent: python-requests/2.31.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n')
...
```

When you want to terminate your audit, simply send the ``SIGUSR2`` signal
to the same process id (pid) to stop forwarding events.

```
$ kill -SIGUSR2 <pid>
```

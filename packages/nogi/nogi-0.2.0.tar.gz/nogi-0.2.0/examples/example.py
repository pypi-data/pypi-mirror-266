import asyncio
import concurrent.futures
import http.server
import logging
import os
import sys
import threading
import time

import requests

import nogi

log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

nogi.Nogi()


def run_http_server():
    log.info("Starting the http server")
    port = 8080
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()


def run_parallel_http_server():
    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(run_http_server)
    executor.shutdown(wait=False)


def do_a_request():
    log.debug("doing a request")
    return requests.get("https://en.wikipedia.org/wiki/Python_(programming_language)")


log.debug(os.getpid())
run_parallel_http_server()
time.sleep(20)
do_a_request()


def in_thread():
    seq = 0

    while True:
        print(f"{os.getpid()}: {seq}")
        seq += 1
        time.sleep(1)


# threading.Thread(target=in_thread).start()

a = 1 + 1
log.debug(a)

do_a_request()
# os.fork()
time.sleep(10)
do_a_request()
# os.fork()
time.sleep(10)

do_a_request()
time.sleep(60)

do_a_request()

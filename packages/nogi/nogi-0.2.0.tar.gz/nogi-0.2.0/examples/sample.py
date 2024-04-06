import time

import requests

from nogi import Nogi

Nogi()


def main():
    for i in range(1000):
        r = requests.get("https://en.wikipedia.org/wiki/Python_(programming_language)")
        print(r.status_code)
        time.sleep(1)


if __name__ == "__main__":
    main()

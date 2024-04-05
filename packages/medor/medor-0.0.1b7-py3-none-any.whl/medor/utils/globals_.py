# coding: utf-8
from pathlib import Path

from halo import Halo

tor = {
    "tor_binary_path": "",
    "tor_port": "52158",
    "controller_port": 9051,
    "tor_plain": "",
    "tor_hashed": "",
}

tor["tor_proxy"] = {
    "http://": "socks5://127.0.0.1:" + tor["tor_port"],
    "https://": "socks5://127.0.0.1:" + tor["tor_port"],
}

spinner = Halo()


def check_globals() -> True:
    if tor["tor_binary_path"] and tor["tor_plain"] and tor["tor_hashed"]:
        return True

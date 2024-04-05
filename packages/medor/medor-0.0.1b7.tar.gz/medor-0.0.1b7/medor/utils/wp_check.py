# coding: utf-8
from colorama import Fore

from medor.utils import net
from medor.utils.globals_ import spinner
from medor.utils.tor import Tor
from medor.utils.util import success, failure


class WpCheck:
    def __init__(
        self, url: str, onion: bool = False, proxy: str or None = None
    ) -> None:
        self.onion = onion
        self.url_signatures = {
            "urls": {
                1: "/wp-login.php",
                2: "/wp-content/",
                3: "/wp-admin/",
                4: "/wp-cron.php",
                5: "/xmlrpc.php",
                6: "/wp-json/wp/v2/",
                7: "/wp-content/themes/",
                8: "/wp-content/plugins/",
            },
        }
        self.string_signatures = {
            "license": {1: "/license.txt", 2: "WordPress"},
            "readme": {1: "/readme.html", 2: "WordPress"},
            "meta generator": {
                1: "",
                2: """<meta name="generator" content="WordPress""",
            },
        }
        self.net = net.Net(onion=onion, proxy=proxy)
        if onion:
            Tor().launch()
        self.wp_check(url)

    def url_sig_check(self, url):
        spinner.text = "Checking URL signatures"
        for signature in self.url_signatures:
            for sig in self.url_signatures[signature]:
                surl = self.url_signatures[signature][sig]
                res = self.net.connect(url + surl)
                if res.status_code == 200:
                    spinner.stop_and_persist(
                        symbol=success,
                        text=f"""{Fore.GREEN}Looks like this website is built with WorPress.\n"""
                        f"""    URL signature {surl} has successfully been reached.""",
                    )
                    Tor().close(self.onion)
                    exit()

    def string_sig_check(self, url):
        spinner.text = "Checking string signatures"
        for signature in self.string_signatures:
            surl = self.string_signatures[signature][1]
            sig = self.string_signatures[signature][2]
            res = self.net.connect(url + surl)
            if sig in res.text:
                spinner.stop_and_persist(
                    symbol=success,
                    text=f"""{Fore.GREEN}Looks like this website is built with WorPress.\n"""
                    f""" String signature {signature} has successfully been reached.""",
                )
                Tor().close(self.onion)
                exit()

    def wp_check(self, url):
        spinner.start("Checking WordPress URL Signatures")
        if url.endswith("/"):
            url = url[:-1]
        self.net.valid_site_url(url)
        self.url_sig_check(url)
        self.string_sig_check(url)
        spinner.stop()
        spinner.stop_and_persist(
            symbol=failure,
            text=f"""{Fore.RED}{url} website doesn't seem to be built with WordPress.\n"""
                 f"   No WP signature found.",
        )
        Tor().close(self.onion)

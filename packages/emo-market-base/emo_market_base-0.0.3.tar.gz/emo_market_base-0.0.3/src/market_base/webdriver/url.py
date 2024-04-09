from typing import Dict
from urllib.parse import urlparse, parse_qs


class ParsedURL:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.scheme = self.parsed_url.scheme
        self.netloc = self.parsed_url.netloc
        self.path = self.parsed_url.path
        self.params = self.parsed_url.params
        self.query = self.parsed_url.query
        self.fragment = self.parsed_url.fragment
        self.query_params = parse_qs(self.query)

    def get_scheme(self) -> str:
        return self.scheme

    def get_netloc(self) -> str:
        return self.netloc

    def get_path(self) -> str:
        return self.path

    def get_params(self) -> str:
        return self.params

    def get_query_text(self) -> str:
        return self.query

    def get_query(self) -> Dict:
        return self.query_params

    def get_fragment(self) -> str:
        return self.fragment

    def get_query_param(self, param_name) -> str:
        return self.get_query().get(param_name, None)

    def get_home(self) -> str:
        return f"{self.get_scheme()}://{self.get_netloc()}"

    def make_adress(self, suffix: str) -> str:
        if suffix[0] == "/":
            suffix = suffix[1:]
        return f"{self.get_home()}/{suffix}"

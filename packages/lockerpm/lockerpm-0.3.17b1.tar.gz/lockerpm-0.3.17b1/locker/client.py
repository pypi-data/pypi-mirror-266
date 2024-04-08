import copy
import json
# import logging
import os
import platform
import stat
import sys
import tempfile
import traceback
from typing import Dict, Any

import requests

from locker import ROOT_PATH
from locker.ls_resources import Secret, Environment
# from locker.logger import Logger


class Locker:
    DEFAULT_OPTIONS = {
        "access_key_id": None,
        "secret_access_key": None,
        "api_base": "https://api.locker.io/locker_secrets",
        "api_version": "v1",
        "proxy": None,
        "log": "error",
        "max_network_retries": 0,
        "skip_cli_lines": 0,
        "headers": {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
        },
    }

    def __init__(
        self,
        access_key_id: str = None,
        secret_access_key: str = None,
        api_base: str = None,
        api_version: str = None,
        proxy: Any = None,
        log: str = None,
        max_network_retries: int = 0,
        resttime: int = 120,
        fetch: bool = False,
        options: Dict = None,
    ):
        # self.download_binary()
        if options is None:
            options = {}
        if api_base:
            options["api_base"] = api_base
        if api_version:
            options["api_version"] = api_version
        if proxy:
            options["proxy"] = proxy
        if log:
            options["log"] = log
        assert resttime >= -1
        options["resttime"] = resttime
        options["fetch"] = fetch

        if max_network_retries:
            options["max_network_retries"] = max_network_retries
        if access_key_id:
            options["access_key_id"] = access_key_id
        if secret_access_key:
            options["secret_access_key"] = secret_access_key

        self._options: dict[str, Any] = copy.deepcopy(Locker.DEFAULT_OPTIONS)

        # Set Headers
        if "headers" in options:
            headers = copy.copy(options["headers"])
        else:
            headers = {}

        self._options.update(options)
        self._options["headers"].update(headers)

        # Set Logger
        self._options["logger"] = None
        # self._options["logger"] = Logger(log_level=self._options.get("log"))

        # Rip off trailing slash since all urls depend on that
        assert isinstance(self._options["api_base"], str)
        if self._options["api_base"].endswith("/"):
            self._options["api_base"] = self._options["api_base"][:-1]

        # if access_key_basic_auth:
        #     self._create_access_key_basic_auth(*access_key_basic_auth)

    # ---- This method is DEPRECATED from 0.1.1b1 ------------------- #
    # def _create_access_key_basic_auth(self, access_key_id: str, secret_access_key: str):
    #     self._options["access_key"] = f"{access_key_id}:{secret_access_key}"

    # TODO: Download binary in __init__
    # def download_binary(self):
    #     _about_file = os.path.join(ROOT_PATH, "__about__.json")
    #     with open(_about_file, 'r') as fd:
    #         binary_version = json.load(fd).get("binary_version")
    #
    #     home_dir = os.path.expanduser("~")
    #     locker_dir = os.path.join(home_dir, ".locker")
    #     # Check if the .locker directory exists, and create it if not
    #     if not os.path.exists(locker_dir):
    #         try:
    #             os.makedirs(locker_dir)
    #         except PermissionError:
    #             home_dir = tempfile.gettempdir()
    #             locker_dir = os.path.join(home_dir, ".locker")
    #             if not os.path.exists(locker_dir):
    #                 os.makedirs(locker_dir)
    #
    #     binary_file_path = os.path.join(locker_dir, f"locker_binary-{binary_version}")
    #
    #     # Check os and get the binary url
    #     if sys.platform == "darwin":
    #         if platform.processor() == "arm":
    #             binary_url = f"https://s.locker.io/download/locker-cli-mac-arm64-{binary_version}"
    #         else:
    #             binary_url = f"https://s.locker.io/download/locker-cli-mac-x64-{binary_version}"
    #     elif sys.platform == "win32":
    #         # binary_version = "1.0.60"
    #         binary_url = f"https://s.locker.io/download/locker-cli-win-x64-{binary_version}.exe"
    #         binary_file_path = os.path.join(locker_dir, f"locker_binary-{binary_version}.exe")
    #     else:
    #         binary_url = f"https://s.locker.io/download/locker-cli-linux-x64-{binary_version}"
    #
    #     # Download binary file
    #     if not os.path.exists(binary_file_path):
    #         r = requests.get(binary_url, stream=True)
    #         if r.ok:
    #             print("saving to", os.path.abspath(binary_file_path))
    #             logging.warning(f"saving to {os.path.abspath(binary_file_path)}")
    #             with open(binary_file_path, 'wb') as f:
    #                 for chunk in r.iter_content(chunk_size=1024 * 8):
    #                     if chunk:
    #                         f.write(chunk)
    #                         f.flush()
    #                         os.fsync(f.fileno())
    #             logging.warning(f"saving ok {os.path.abspath(binary_file_path)}")
    #             try:
    #                 # Make the binary executable
    #                 logging.warning(f"starting set permission {binary_file_path}")
    #                 st = os.stat(binary_file_path)
    #                 os.chmod(binary_file_path, st.st_mode | stat.S_IEXEC)
    #                 logging.warning(f"set permission ok {binary_file_path}")
    #             except PermissionError as e:
    #                 tb = traceback.format_exc()
    #                 logging.error(f"set permission error {e} - {tb}")
    #                 pass
    #
    #         # HTTP status code 4XX/5XX
    #         else:
    #             logging.error("Download failed: status code {}\n{}".format(r.status_code, r.text))
    #             print("Download failed: status code {}\n{}".format(r.status_code, r.text))

    @property
    def access_key_id(self):
        return self._options.get("access_key_id")

    @access_key_id.setter
    def access_key_id(self, access_key_id_value):
        self._options.update({"access_key_id": access_key_id_value})

    @property
    def secret_access_key(self):
        return self._options.get("secret_access_key")

    @secret_access_key.setter
    def secret_access_key(self, secret_access_key_value):
        self._options.update({"secret_access_key": secret_access_key_value})

    @property
    def api_base(self):
        return str(self._options.get("api_base"))

    @api_base.setter
    def api_base(self, api_base_value):
        self._options.update({"api_base": api_base_value})

    @property
    def api_version(self):
        return str(self._options.get("api_version"))

    @property
    def log(self):
        return self._options.get("log")

    @log.setter
    def log(self, log_value):
        self._options.update({"log": log_value})
        self._options["logger"] = None
        # self._options["logger"] = Logger(log_level=self._options.get("log"))

    @property
    def resttime(self):
        return self._options.get("resttime")

    @resttime.setter
    def resttime(self, resttime_value):
        self._options.update({"resttime": resttime_value})

    @property
    def fetch(self):
        return self._options.get("fetch")

    @fetch.setter
    def fetch(self, fetch_value):
        self._options.update({"fetch": fetch_value})

    @property
    def skip_cli_lines(self):
        return self._options.get("skip_cli_lines")

    @property
    def headers(self):
        return self._options.get("headers")

    @headers.setter
    def headers(self, custom_headers):
        self._options.update({"headers": custom_headers})

    @property
    def max_network_retries(self):
        return self._options.get("max_network_retries")

    def _translate_options(self, params):
        _params = copy.deepcopy(self._options)
        _params.update(params)
        return _params

    def list(self, **params):
        return Secret.list(**self._translate_options(params))

    def get(self, key, environment_name=None, default_value=None, **params):
        return Secret.get_secret(
            key,
            environment_name=environment_name,
            default_value=default_value,
            **self._translate_options(params)
        )

    def get_secret(self, key, environment_name=None, default_value=None, **params):
        return Secret.get_secret(
            key,
            environment_name=environment_name,
            default_value=default_value,
            **self._translate_options(params)
        )

    def retrieve(self, key, environment_name=None, **params):
        return Secret.retrieve_secret(key, environment_name=environment_name, **self._translate_options(params))

    def create(self, **params):
        return Secret.create(**self._translate_options(params))

    def modify(self, **params):
        return Secret.modify(**self._translate_options(params))

    def list_environments(self, **params):
        return Environment.list(**self._translate_options(params))

    def get_environment(self, name, **params):
        return Environment.get_environment(
            name=name,
            **self._translate_options(params)
        )

    def retrieve_environment(self, name, **params):
        return Environment.retrieve_environment(
            name=name,
            **self._translate_options(params)
        )

    def create_environment(self, **params):
        return Environment.create(**self._translate_options(params))

    def modify_environment(self, **params):
        return Environment.modify(**self._translate_options(params))

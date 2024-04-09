#
# _zoo_accessor.py - DeGirum Python SDK: zoo accessors
# Copyright DeGirum Corp. 2022
#
# Contains DeGirum zoo accessors implementation
#

import json
import copy
import io
from pathlib import Path
import zipfile
import logging
from abc import ABC, abstractmethod
from urllib.parse import urlparse, quote


import requests
from requests.adapters import HTTPAdapter, Retry

from .exceptions import DegirumException
from .model import _ClientModel, _ServerModel, _CloudServerModel
from ._filter_models import _filter_models
from .aiclient import (
    ModelParams,
    get_modelzoo_list,
    system_info as server_system_info,
    trace_manage as server_trace_manage,
)
from .log import log_wrap

logger = logging.getLogger(__name__)


class _CommonZooAccessor(ABC):
    """Zoo Accessor abstract class"""

    @log_wrap
    def __init__(self, my_url: str):
        """Constructor

        -`my_url`: accessor-specific URL
        """
        self._assets: dict = {}
        self._url = my_url
        self.rescan_zoo()

    @property
    def url(self):
        return str(self._url)

    @log_wrap
    def list_models(self, *args, **kwargs):
        """List all available model matching to specified filter values.

        - `model_family`: model family name filter, used as search substring in model name: "yolo", "mobilenet1"
        - `device`: target inference device, string or list of strings of matching values: "orca", "orca1", "cpu", "gpu", "edgetpu", "dla", "dla_fallback", "myriad", "npu"
        - `precision`: model calculation precision, string or list of strings of matching values: "quant", "float"
        - `pruned`: model density, string or list of strings of matching values: "dense", "pruned"
        - `runtime`: runtime agent type, string or list of strings of matching values: "n2x", "tflite", "tensorrt", "openvino"

        Returns list of matching model names, sorted alphabetically
        """
        # explicitly recreate registry
        res = _filter_models(
            models=lambda n=None: self._assets[n] if n else self._assets.keys(),
            *args,
            **kwargs,
        )
        return sorted(res)

    @log_wrap
    def model_info(self, model: str):
        """Request model parameters for given model name.

        - `model`: model name

        Returns model parameter object
        """
        asset = self._assets.get(model, None)
        if asset:
            return copy.deepcopy(asset)
        else:
            raise DegirumException(
                f"Model '{model}' is not found in model zoo '{self.url}'"
            )

    @abstractmethod
    def load_model(self, model: str):
        """Create model object for given model name.

        - `model`: model name as returned by list_models()

        Returns model object corresponding to given model name
        """

    @abstractmethod
    def rescan_zoo(self):
        """Update list of assets according to current zoo contents"""

    @abstractmethod
    def system_info(self) -> dict:
        """Return host system information dictionary"""


class _LocalInferenceSingleFileZooAccessor(_CommonZooAccessor):
    """Local inference, single file zoo implementation"""

    @log_wrap
    def __init__(self, url):
        """Constructor.

        -`url`: path to the model JSON configuration file in the local filesystem.
        """
        super().__init__(url)

    @log_wrap
    def load_model(self, model: str):
        """Create model object for given model identifier.

        - `model`: model identifier

        Returns model object corresponding to model identifier.
        """

        # we ignore provided model name for single-model zoo
        model_params = next(iter(self._assets.values()))
        return _ClientModel(model, copy.deepcopy(model_params))

    @log_wrap
    def rescan_zoo(self):
        """Update list of assets"""

        self._assets = {Path(self.url).stem: _ClientModel.load_config_file(self.url)}

    @log_wrap
    def system_info(self) -> dict:
        """Return host system information dictionary"""
        from .CoreClient import system_info as core_system_info

        return core_system_info()


class _LocalInferenceLocalDirZooAccessor(_CommonZooAccessor):
    """Local inference, local directory zoo implementation"""

    @log_wrap
    def __init__(self, url):
        """Constructor.

        -`url`: local zoo directory path
        """
        super().__init__(url)

    @log_wrap
    def load_model(self, model: str):
        """Create model object for given model identifier.

        - `model`: model identifier

        Returns model object corresponding to model identifier.
        """

        model_params = self._assets.get(model, None)
        if model_params:
            return _ClientModel(model, copy.deepcopy(model_params))
        else:
            raise DegirumException(
                f"Model '{model}' is not found in the model zoo directory '{self.url}'"
            )

    @log_wrap
    def rescan_zoo(self):
        """Update list of assets"""

        # recursively iterate over all JSON files in zoo directory
        json_files = sorted(Path(self.url).rglob("*.json"))
        for f in json_files:
            try:
                mparams = _ClientModel.load_config_file(f)

                # accept only valid model configuration files, which have checksum and config version
                if mparams.Checksum and mparams.ConfigVersion > 0:
                    self._assets[f.stem] = mparams
            except Exception:
                pass  # ignore invalid model configuration files

    @log_wrap
    def system_info(self) -> dict:
        """Return host system information dictionary"""
        from .CoreClient import system_info as core_system_info

        return core_system_info()


class _AIServerLocalZooAccessor(_CommonZooAccessor):
    """AI server inference, local model zoo implementation"""

    @log_wrap
    def __init__(self, url):
        """Constructor.

        -`url`: AI server hostname or IP address
        """
        super().__init__(url)

    @log_wrap
    def rescan_zoo(self):
        """Update cached list of models according to the current server model zoo contents"""
        self._assets = {a.name: a.extended_params for a in get_modelzoo_list(self.url)}

    @log_wrap
    def load_model(self, model: str):
        """Create model object for given model name.

        - `model`: model name as returned by list_models()

        Returns model object corresponding to given model name
        """
        model_params = self._assets.get(model, None)
        if model_params:
            return _ServerModel(self.url, model, copy.deepcopy(model_params))
        else:
            raise DegirumException(
                f"Model '{model}' is not found in the model zoo on AI server '{self.url}'"
            )

    @log_wrap
    def system_info(self) -> dict:
        """Return host system information dictionary"""
        return server_system_info(self.url)


class _CloudZooAccessorBase(_CommonZooAccessor):
    """Cloud model zoo access: base implementation"""

    _default_cloud_server = "cs.degirum.com"
    """ DeGirum cloud server hostname """

    _default_cloud_zoo = "/degirum/public"
    """ DeGirum public zoo name. You can freely use all models available in this public model zoo """

    _default_cloud_url = "https://" + _default_cloud_server + _default_cloud_zoo
    """ Full DeGirum cloud public zoo URL. You can freely use all models available in this public model zoo """

    @log_wrap
    def __init__(self, url: str, token: str):
        """Constructor.

        -`url`: path to the cloud zoo in `"https://<cloud server URL>[/<zoo URL>]"` format
        -`token`: cloud zoo access token
        """
        url_parsed = urlparse(url)
        url = f"{url_parsed.scheme}://{url_parsed.hostname}" + (
            f":{url_parsed.port}" if url_parsed.port else ""
        )
        self._zoo_url = (
            quote(url_parsed.path)
            if url_parsed.path
            else _CloudZooAccessorBase._default_cloud_zoo
        )
        self._token = token
        self._timeout = 5
        super().__init__(url)

    @log_wrap
    def _cloud_server_request(self, api_url: str, is_octet_stream: bool = False):
        """Perform request to cloud server

        -`api_url`: api url request
        -`is_octet_stream`: true to request binary data, false to request JSON

        Returns response binary content
        """

        cloud_server_path_suffix = "/zoo/v1/public"

        try:
            retries = Retry(total=3)  # the number of retries for http/https requests
            s = requests.Session()
            for m in ["http://", "https://"]:
                s.mount(m, HTTPAdapter(max_retries=retries))
            headers = dict(token=self._token)
            if is_octet_stream:
                headers["accept"] = "application/octet-stream"
            logger.info(
                f"sending a request to {self.url}{cloud_server_path_suffix}{api_url}"
            )
            res = s.get(
                f"{self.url}{cloud_server_path_suffix}{api_url}",
                headers=headers,
                timeout=self._timeout,
            )
        except requests.RequestException as e:
            raise DegirumException(
                f"Unable to access server {self.url.split('://')[-1]}: {e}"
            ) from None
        if res.status_code == 401:
            response = res.json()
            reason = (
                response["detail"]
                if response and isinstance(response, dict) and "detail" in response
                else "invalid token value"
            )
            raise DegirumException(
                f"Unable to connect to server {self.url.split('://')[-1]}: {reason} {self._token}"
            )

        try:
            res.raise_for_status()
        except requests.RequestException as e:
            details = str(e)
            try:
                j = res.json()
                if "detail" in j:
                    details = f"{j['detail']}. (cloud server response: {str(e)})"
            except json.JSONDecodeError:
                pass
            raise DegirumException(details) from None

        # if we followed a redirect to https, update url
        if (
            len(res.history) == 1
            and res.url.startswith("https://")
            and self._url.startswith("http://")
        ):
            self._url = "https" + self._url[4:]

        if is_octet_stream:
            return res.content
        else:
            try:
                return res.json()
            except json.JSONDecodeError:
                raise DegirumException(
                    f"Unable to parse response from server {self.url.split('://')[-1]}: {res}"
                ) from None

    @log_wrap
    def ext_model_name(self, simple_model_name: str) -> str:
        """Construct extended cloud model name from simple model name and zoo path"""
        return f"{self._zoo_url[1:]}/{simple_model_name}"

    @log_wrap
    def label_dictionary(self, model: str):
        """Download model dictionary from cloud server.

        -`model`: extended model name
        """
        return self._cloud_server_request(f"/models/{model}/dictionary")

    @log_wrap
    def rescan_zoo(self):
        """Update cached list of models according to the current server model zoo contents"""

        # get list of supported models from cloud server
        models_info = self._cloud_server_request("/models" + self._zoo_url)

        if not isinstance(models_info, dict):
            raise DegirumException(
                f"Unable to get model list from server: {models_info}"
            )
        if "error" in models_info:
            raise DegirumException(
                f"Unable to get model list from server: {models_info['error']}"
            )

        self._assets = {k: ModelParams(json.dumps(v)) for k, v in models_info.items()}

    @log_wrap
    def download_model(self, model: str, dest_root_path: Path):
        """Download model from the cloud server.

        -`model`: model name as returned by list_models()
        -`dest_root_path`: root destination directory path
        """

        # download model archive from cloud zoo
        res = self._cloud_server_request(f"/models{self._zoo_url}/{model}", True)

        # unzip model archive into model directory
        with zipfile.ZipFile(io.BytesIO(res)) as z:
            z.extractall(dest_root_path)


class _LocalHWCloudZooAccessor(_CloudZooAccessorBase):
    """Local inference, cloud model zoo implementation"""

    @log_wrap
    def __init__(self, url: str, token: str):
        """Constructor.

        -`url`: path to the cloud zoo in `"https://<cloud server URL>[/<zoo URL>]"` format
        -`token`: cloud zoo access token
        """
        super().__init__(url, token)

    @log_wrap
    def load_model(self, model: str):
        """Create model object for given model name.

        - `model`: model name as returned by list_models()

        Returns model object corresponding to given model name
        """

        model_params = self._assets.get(model, None)
        if model_params:
            ext_model_name = self.ext_model_name(model)
            label_dict = lambda: self.label_dictionary(ext_model_name)

            model_params = copy.deepcopy(model_params)
            model_params.CloudModelName = ext_model_name
            model_params.CloudURL = self._url
            model_params.CloudToken = self._token
            return _ClientModel(model, model_params, label_dict)
        else:
            raise DegirumException(
                f"Model '{model}' is not found in the cloud model zoo '{self.url}{self._zoo_url}'"
            )

    @log_wrap
    def system_info(self) -> dict:
        """Return host system information dictionary"""
        from .CoreClient import system_info as core_system_info

        return core_system_info()


class _AIServerCloudZooAccessor(_CloudZooAccessorBase):
    """AI server inference, cloud model zoo implementation"""

    @log_wrap
    def __init__(self, host: str, url: str, token: str):
        """Constructor.

        -`host`: AI server hostname
        -`url`: path to the cloud zoo in `"https://<cloud server URL>[/<zoo URL>]"` format
        -`token`: cloud zoo access token
        """
        self._host = host
        super().__init__(url, token)

    @log_wrap
    def load_model(self, model: str):
        """Create model object for given model name.

        - `model`: model name as returned by list_models()

        Returns model object corresponding to given model name
        """
        model_params = self._assets.get(model, None)
        if model_params:
            ext_model_name = self.ext_model_name(model)
            label_dict = lambda: self.label_dictionary(ext_model_name)

            model_params = copy.deepcopy(model_params)
            model_params.CloudURL = self._url
            model_params.CloudToken = self._token
            return _ServerModel(self._host, ext_model_name, model_params, label_dict)
        else:
            raise DegirumException(
                f"Model '{model}' is not found in the cloud model zoo '{self.url}{self._zoo_url}'"
            )

    @log_wrap
    def system_info(self) -> dict:
        """Return host system information dictionary"""
        return server_system_info(self._host)


class _CloudServerZooAccessor(_CloudZooAccessorBase):
    """Cloud server inference, cloud model zoo implementation"""

    @log_wrap
    def __init__(self, url: str, token: str):
        """Constructor.

        -`url`: path to the cloud zoo in `"https://<cloud server URL>[/<zoo URL>]"` format
        -`token`: cloud zoo access token
        """
        super().__init__(url, token)

    @log_wrap
    def load_model(self, model: str):
        """Create model object for given model name.

        - `model`: model name as returned by list_models()

        Returns model object corresponding to given model name
        """
        model_params = self._assets.get(model, None)
        if model_params:
            ext_model_name = self.ext_model_name(model)
            label_dict = lambda: self.label_dictionary(ext_model_name)

            return _CloudServerModel(
                self.url,
                self._token,
                ext_model_name,
                copy.deepcopy(model_params),
                label_dict,
            )
        else:
            raise DegirumException(
                f"Model '{model}' is not found in the cloud model zoo '{self.url}{self._zoo_url}'"
            )

    @log_wrap
    def system_info(self) -> dict:
        """Return host system information dictionary"""
        return {}


def _system_info_run(args):
    """
    Execute system_info command
        - `args`: argparse command line arguments
    """

    import yaml

    if args.host:
        info = server_system_info(args.host)
    else:
        from .CoreClient import system_info as core_system_info

        info = core_system_info()

    # remove virtual devices
    if "Devices" in info:
        info["Devices"].pop("DUMMY/DUMMY", None)

    print(yaml.dump(info, sort_keys=False))


def _system_info_args(parser):
    """
    Define sys-info subcommand arguments
        - `parser`: argparse parser object to be stuffed with args
    """
    parser.add_argument(
        "--host",
        default="",
        help="remote AI server hostname/IP; omit for local info",
    )
    parser.set_defaults(func=_system_info_run)


def _trace_run(args):
    """
    Execute trace command
        - `args`: argparse command line arguments
    """

    import yaml

    if args.host:
        trace_mgr = lambda req: server_trace_manage(args.host, req)
    else:
        from .CoreClient import trace_manage as core_trace_manage

        trace_mgr = lambda req: core_trace_manage(req)

    if args.command == "list":
        ret = trace_mgr({"config_get": 1})["config_get"]
        print(yaml.dump(ret, sort_keys=False))

    elif args.command == "configure":
        groups = {}

        def apply(arg, level):
            if isinstance(arg, list):
                for gr in arg:
                    groups[gr] = level

        apply(args.basic, 1)
        apply(args.detailed, 2)
        apply(args.full, 3)
        trace_mgr({"config_set": groups})

    elif args.command == "read":
        ret = trace_mgr({"trace_read": {"size": args.filesize}})["trace_read"]
        if args.file:
            with open(args.file, "w") as f:
                f.write(ret)
        else:
            print(ret)


def _trace_args(parser):
    """
    Define trace subcommand arguments
        - `parser`: argparse parser object to be stuffed with args
    """

    parser.add_argument(
        "command",
        nargs="?",
        choices=["list", "configure", "read"],
        default="list",
        help="trace command: list all available trace groups; configure trace groups; read trace to file",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="[all] remote AI server hostname/IP (default is 'localhost')",
    )

    parser.add_argument(
        "--basic",
        nargs="+",
        metavar="TRACE-GROUP",
        help="[configure] trace groups to trace with Basic trace level",
    )

    parser.add_argument(
        "--detailed",
        nargs="+",
        metavar="TRACE-GROUP",
        help="[configure] trace groups to trace with Detailed trace level",
    )

    parser.add_argument(
        "--full",
        nargs="+",
        metavar="TRACE-GROUP",
        help="[configure] trace groups to trace with Full trace level",
    )

    parser.add_argument(
        "--file",
        default="",
        metavar="FILENAME",
        help="[read] filename to save trace data into (default is '': print to console)",
    )

    parser.add_argument(
        "--filesize",
        type=int,
        default=10000000,
        help="[read] max. trace data size to read (default is 10000000)",
    )

    parser.set_defaults(func=_trace_run)

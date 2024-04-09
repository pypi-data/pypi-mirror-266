#
# zoo_manager.py - DeGirum Python SDK: zoo manager implementation
# Copyright DeGirum Corp. 2022
#
# Implements DeGirum zoo manager class
#

from pathlib import Path
from typing import List
from urllib.parse import urlparse
import logging

from .log import log_wrap
from .exceptions import DegirumException
from .model import Model
from ._zoo_accessor import (
    _LocalInferenceSingleFileZooAccessor,
    _LocalInferenceLocalDirZooAccessor,
    _LocalHWCloudZooAccessor,
    _AIServerLocalZooAccessor,
    _AIServerCloudZooAccessor,
    _CloudServerZooAccessor,
    _CloudZooAccessorBase,
)
from .aiclient import ModelParams

logger = logging.getLogger(__name__)


class ZooManager:
    """Class that manages a model zoo.

    A _model zoo_ in terminology of PySDK is a collection of AI models and simultaneously an ML inference engine
    type and location.

    Depending on the deployment location, there are several types of model zoos supported by PySDK:

    - **Local** model zoo: Deployed on the local file system of the PySDK installation host. Inferences are performed on the
    same host using AI accelerators installed on that host.
    - AI **server** model zoo: Deployed on remote host with DeGirum AI server running on that host. Inferences are performed
    by DeGirum AI server on that remote host.
    - **Cloud** Platform model zoo: Deployed on DeGirum Cloud Platform. Inferences are performed by DeGirum Cloud Platform
    servers.

    The type of the model zoo is defined by the URL string which you pass as `zoo_url` parameter into the constructor.

    Zoo manager provides the following functionality:

    - List and search models available in the connected model zoo.
    - Create AI model handling objects to perform AI inferences.
    - Request various AI model parameters.
    """

    _default_cloud_url = _CloudZooAccessorBase._default_cloud_url
    """ DeGirum public zoo URL. You can freely use all models available in this public model zoo """

    _CLOUD: str = "@cloud"
    """ Cloud inference designator """

    _LOCAL: str = "@local"
    """ Local inference designator """

    def __dir__(self):
        return [
            "list_models",
            "load_model",
            "model_info",
        ]

    @log_wrap
    def __init__(self, inference_host_address: str, zoo_url: str, token: str):
        """Constructor.

        !!! note

            Typically, you never construct `ZooManager` objects yourself -- instead you call [degirum.connect][]
            function to create `ZooManager` instances for you.

        For the description of arguments see [degirum.connect][]
        """

        def validate_cloud_credentials(zoo_url: str, token: str):
            if not zoo_url:
                raise DegirumException("Cloud model zoo URL should not be empty")

            url_parsed = urlparse(zoo_url)
            if url_parsed.scheme != "https" and url_parsed.scheme != "http":
                raise DegirumException(
                    f"Cloud model zoo URL '{zoo_url}' should start with https:// or http:// prefix"
                )

            if not token:
                raise DegirumException("Cloud zoo API access token should not be empty")

        if inference_host_address[0] == "@":
            if inference_host_address == ZooManager._CLOUD:
                #
                # cloud inference
                #
                validate_cloud_credentials(zoo_url, token)
                logger.info(f"Cloud inference with cloud zoo at '{zoo_url}'")
                self._zoo = _CloudServerZooAccessor(zoo_url, token)

            elif inference_host_address == ZooManager._LOCAL:
                #
                # local inference
                #
                if zoo_url and zoo_url.lower().endswith(".json"):
                    # use local model
                    if Path(zoo_url).exists() and Path(zoo_url).is_file():
                        logger.info(f"Local inference with local model '{zoo_url}'")
                        self._zoo = _LocalInferenceSingleFileZooAccessor(zoo_url)
                    else:
                        raise DegirumException(
                            f"ZooManager: incorrect model file path '{zoo_url}'"
                        )
                elif zoo_url and Path(zoo_url).exists() and Path(zoo_url).is_dir():
                    logger.info(f"Local inference with local zoo from '{zoo_url}' dir")
                    self._zoo = _LocalInferenceLocalDirZooAccessor(zoo_url)
                else:
                    # use cloud model zoo
                    validate_cloud_credentials(zoo_url, token)
                    logger.info(f"Local inference with cloud zoo at '{zoo_url}'")
                    self._zoo = _LocalHWCloudZooAccessor(zoo_url, token)

            else:
                raise DegirumException(
                    f"Incorrect inference host address '{inference_host_address}'. "
                    + f"It should be either {ZooManager._LOCAL}, or {ZooManager._CLOUD}, or a valid AI server address"
                )

        else:
            #
            # AI server inference
            #
            if not zoo_url:
                # use AI server local model zoo
                logger.info(
                    f"AI server inference on '{inference_host_address}' host with local zoo"
                )
                self._zoo = _AIServerLocalZooAccessor(inference_host_address)
            else:
                validate_cloud_credentials(zoo_url, token)
                logger.info(
                    f"AI server inference on '{inference_host_address}' host with cloud zoo at '{zoo_url}'"
                )
                self._zoo = _AIServerCloudZooAccessor(
                    inference_host_address, zoo_url, token
                )

    @log_wrap
    def list_models(self, *args, **kwargs) -> List[str]:
        """Get a list of names of AI models available in the connected model zoo which match specified
        filtering criteria.

        Keyword Args:
            model_family (str): Model family name filter.

                - When you pass a string, it will be used as search substring in the model name. For example, `"yolo"`,
                `"mobilenet"`.
                - You may also pass `re.Pattern` object. In this case it will do regular expression pattern search.

            device (str): Target inference device -- string or list of strings of device names.

                Possible names: `"orca"`, `"orca1"`, `"cpu"`, `"gpu"`, `"edgetpu"`, `"dla"`, `"dla_fallback"`, `"myriad"`, `"npu"`.

            precision (str): Model calculation precision - string or list of strings of model precision labels.

                Possible labels: `"quant"`, `"float"`.

            pruned (str): Model density -- string or list of strings of model density labels.

                Possible labels: `"dense"`, `"pruned"`.

            runtime (str): Runtime agent type -- string or list of strings of runtime agent types.

                Possible types: `"n2x"`, `"tflite"`, `"tensorrt"`, `"openvino"`.

        Returns:
            The list of model name strings matching specified filtering criteria.
                Use a string from that list as a parameter of [degirum.zoo_manager.ZooManager.load_model][] method.

        Example:

            Find all models of `"yolo"` family capable to run either on CPU or on DeGirum Orca AI accelerator
            from all registered model zoos:
            ```python
                yolo_model_list = zoo_manager.list_models("yolo", device=["cpu", "orca"])
            ```
        """
        return self._zoo.list_models(*args, **kwargs)

    @log_wrap
    def load_model(self, model_name: str, **kwargs) -> Model:
        """Create and return the model handling object for given model name.

        Args:

            model_name:
                Model name string identifying the model to load.
                It should exactly match the model name as it is returned by
                [degirum.zoo_manager.ZooManager.list_models][] method.

            **kwargs:
                you may pass arbitrary model properties to be assigned to the model object in a form
                of property=value

        Returns:
            Model handling object.
                Using this object you perform AI inferences on this model and also configure various model properties,
                which define how to do input image preprocessing and inference result post-processing:

                - Call [degirum.model.Model.predict][] method to perform AI inference of a single frame.
                Inference result object is returned.
                - For more efficient pipelined batch predictions call [degirum.model.Model.predict_batch][]
                or [degirum.model.Model.predict_dir][] methods to perform AI inference of multiple frames
                - Configure the following image pre-processing properties:

                    - [degirum.model.Model.input_resize_method][] -- to set input image resize method.
                    - [degirum.model.Model.input_pad_method][] -- to set input image padding method.
                    - [degirum.model.Model.input_letterbox_fill_color][] -- to set letterbox padding color.
                    - [degirum.model.Model.image_backend][] -- to select image processing library.

                - Configure the following model post-processing properties:

                    - [degirum.model.Model.output_confidence_threshold][] -- to set confidence threshold.
                    - [degirum.model.Model.output_nms_threshold][] -- to set non-max suppression threshold.
                    - [degirum.model.Model.output_top_k][] -- to set top-K limit for classification models.
                    - [degirum.model.Model.output_pose_threshold][] -- to set pose detection threshold for
                    pose detection models.

                - Configure the following overlay image generation properties:

                    - [degirum.model.Model.overlay_color][] -- to set color for inference results drawing on overlay image.
                    - [degirum.model.Model.overlay_line_width][] -- to set line width for inference results drawing
                    on overlay image.
                    - [degirum.model.Model.overlay_show_labels][] -- to set flag to enable/disable drawing class labels
                    on overlay image.
                    - [degirum.model.Model.overlay_show_probabilities][] -- to set flag to enable/disable drawing class
                    probabilities on overlay image.
                    - [degirum.model.Model.overlay_alpha][] -- to set alpha-blend weight for inference results drawing
                    on overlay image.
                    - [degirum.model.Model.overlay_font_scale][] -- to set font scale for inference results drawing
                    on overlay image.

                Inference result object [degirum.postprocessor.InferenceResults][] returned by
                [degirum.model.Model.predict][] method allows you to access AI inference results:

                - Use [degirum.postprocessor.InferenceResults.image][] property to access original image.
                - Use [degirum.postprocessor.InferenceResults.image_overlay][] property to access image with
                inference results drawn on a top of it.
                - Use [degirum.postprocessor.InferenceResults.results][] property to access the list of numeric
                inference results.

        """
        model = self._zoo.load_model(model_name)
        for key, value in kwargs.items():
            if hasattr(Model, key):
                model_attr = getattr(Model, key)
                if isinstance(model_attr, property):
                    if model_attr.fset is not None:
                        setattr(model, key, value)
                    else:
                        raise DegirumException(
                            f"Cannot set model property '{key}': it is read-only"
                        )
                else:
                    raise DegirumException(
                        f"Cannot set model property '{key}': it is not a property"
                    )

            else:
                raise DegirumException(f"Model property '{key}' does not exist")
        return model

    @log_wrap
    def model_info(self, model_name: str) -> ModelParams:
        """Request model parameters for given model name.

        Args:
            model_name: Model name string. It should exactly match the model name as it is returned by
                [degirum.zoo_manager.ZooManager.list_models][] method.

        Returns:
            Model parameter object which provides read-only access to all model parameters.

        !!! note

            You cannot modify actual model parameters -- any changes of model parameter object returned by this
            method are not applied to the real model. Use properties of model handling objects returned by
            [degirum.zoo_manager.ZooManager.load_model][] method to change parameters of that particular model
            instance on the fly.
        """
        return self._zoo.model_info(model_name)

    @log_wrap
    def _rescan_zoo(self):
        """Rescan connected model zoo to update the list of available models."""
        self._zoo.rescan_zoo()

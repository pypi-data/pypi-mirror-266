"""
This module provides functionality related to Kubeflow Pipelines.
"""

import os
import time
from datetime import datetime
import kfp
from kfp import dsl
from kserve import (
    KServeClient,
    V1beta1InferenceService,
    V1beta1InferenceServiceSpec,
    V1beta1ModelFormat,
    V1beta1ModelSpec,
    V1beta1PredictorSpec,
    V1beta1SKLearnSpec,
    constants,
    utils,
)
from kubernetes import client
from kubernetes.client import V1ObjectMeta
from kubernetes.client.models import V1EnvVar
from app.plugins import plugin_config


class CogContainer(kfp.dsl._container_op.Container):
    """
    Subclass of Container to add model access environment variables.
    """

    def __init__(self):
        """
        Initializes the CogContainer class.
        """
        super().__init__(image=None, command=None, args=None)

    def add_model_access(self):
        """
        Adds model access environment variables to the container.

        Returns:
            CogContainer: Container instance with added environment variables.
        """
        return (
            self.add_env_variable(
                V1EnvVar(
                    name=plugin_config.TRACKING_URI,
                    value=os.getenv(plugin_config.TRACKING_URI),
                )
            )
            .add_env_variable(
                V1EnvVar(
                    name=plugin_config.S3_ENDPOINT_URL,
                    value=os.getenv(plugin_config.S3_ENDPOINT_URL),
                )
            )
            .add_env_variable(
                V1EnvVar(
                    name=plugin_config.ACCESS_KEY_ID,
                    value=os.getenv(plugin_config.ACCESS_KEY_ID),
                )
            )
            .add_env_variable(
                V1EnvVar(
                    name=plugin_config.SECRET_ACCESS_KEY,
                    value=os.getenv(plugin_config.SECRET_ACCESS_KEY),
                )
            )
        )


class KubeflowPlugin:
    """
    Class for defining reusable components.
    """

    def __init__(self, image=None, command=None, args=None):
        """
        Initializes the KubeflowPlugin class.
        """
        self.kfp = kfp
        self.kfp.dsl._container_op.Container.AddModelAccess = (
            CogContainer.add_model_access
        )
        self.kfp.dsl._container_op.ContainerOp.AddModelAccess = (
            CogContainer.add_model_access
        )

    @staticmethod
    def version():
        """
        Retrieve the version of the Kubeflow Pipelines SDK.

        Returns:
            str: Version of the Kubeflow Pipelines SDK.
        """
        return kfp.__version__

    @staticmethod
    def pipeline(name=None, description=None):
        """
        Decorator function to define Kubeflow Pipelines.

        Args:
            name (str, optional): Name of the pipeline. Defaults to None.
            description (str, optional): Description of the pipeline. Defaults to None.

        Returns:
            Callable: Decorator for defining Kubeflow Pipelines.
        """
        return dsl.pipeline(name=name, description=description)

    def create_component_from_func(
        self,
        func,
        output_component_file=None,
        base_image=None,
        packages_to_install=None,
    ):
        """
        Create a component from a Python function.

        Args:
            func (Callable): Python function to convert into a component.
            output_component_file (str, optional): Path to save the component YAML file. Defaults
            to None.
            base_image (str, optional): Base Docker image for the component. Defaults to None.
            packages_to_install (List[str], optional): List of additional Python packages
            to install in the component.
            Defaults to None.

        Returns:
            kfp.components.ComponentSpec: Component specification.
        """
        training_var = kfp.components.create_component_from_func(
            func=func,
            output_component_file=output_component_file,
            base_image=base_image,
            packages_to_install=packages_to_install,
        )
        self.kfp.dsl._container_op.ContainerOp.AddModelAccess = (
            CogContainer.add_model_access
        )
        return training_var

    @staticmethod
    def client():
        """
        Get the Kubeflow Pipeline client.

        Returns:
            kfp.Client: Kubeflow Pipeline client instance.
        """
        return kfp.Client()

    @staticmethod
    def load_component_from_url(url):
        """
        Load a component from a URL.

        Args:
            url (str): URL to load the component from.

        Returns:
            kfp.components.ComponentSpec: Loaded component specification.
        """
        return kfp.components.load_component_from_url(url)

    @staticmethod
    def input_path(label: str):
        """
        Create an InputPath component.

        Args:
            label (str): Label for the input path.

        Returns:
            InputPath: InputPath component instance.
        """
        return kfp.components.InputPath(label)

    @staticmethod
    def output_path(label: str):
        """
        Create an OutputPath component.

        Args:
            label (str): Label for the output path.

        Returns:
            OutputPath: OutputPath component instance.
        """
        return kfp.components.OutputPath(label)

    @staticmethod
    def serve_model_v2(model_uri: str, name: str = None):
        """
        Create a kserve instance.

        Args:
            model_uri (str): URI of the model.
            name (str, optional): Name of the kserve instance. If not provided,
            a default name will be generated.

        Returns:
            None
        """
        namespace = utils.get_default_target_namespace()
        if name is None:
            now = datetime.now()
            v = now.strftime("%d%M")
            name = f"predictor_model{v}"
        isvc_name = name
        predictor = V1beta1PredictorSpec(
            service_account_name="kserve-controller-s3",
            min_replicas=1,
            model=V1beta1ModelSpec(
                model_format=V1beta1ModelFormat(
                    name=plugin_config.ML_TOOL,
                ),
                storage_uri=model_uri,
                protocol_version="v2",
            ),
        )

        isvc = V1beta1InferenceService(
            api_version=constants.KSERVE_V1BETA1,
            kind=constants.KSERVE_KIND,
            metadata=client.V1ObjectMeta(
                name=isvc_name,
                namespace=namespace,
                annotations={"sidecar.istio.io/inject": "false"},
            ),
            spec=V1beta1InferenceServiceSpec(predictor=predictor),
        )
        kserve = KServeClient()
        kserve.create(isvc)
        time.sleep(plugin_config.TIMER_IN_SEC)

    @staticmethod
    def serve_model_v1(model_uri: str, name: str = None):
        """
        Create a kserve instance version1.

        Args:
            model_uri (str): URI of the model.
            name (str, optional): Name of the kserve instance. If not provided,
            a default name will be generated.

        Returns:
            None
        """

        isvc_name = name
        namespace = utils.get_default_target_namespace()
        isvc = V1beta1InferenceService(
            api_version=constants.KSERVE_V1BETA1,
            kind=constants.KSERVE_KIND,
            metadata=V1ObjectMeta(
                name=isvc_name,
                namespace=namespace,
                annotations={"sidecar.istio.io/inject": "false"},
            ),
            spec=V1beta1InferenceServiceSpec(
                predictor=V1beta1PredictorSpec(
                    service_account_name="kserve-controller-s3",
                    sklearn=V1beta1SKLearnSpec(storage_uri=model_uri),
                )
            ),
        )

        kclient = KServeClient()
        kclient.create(isvc)
        time.sleep(plugin_config.TIMER_IN_SEC)

    @staticmethod
    def get_model_url(model_name: str):
        """
        Retrieve the URL of a deployed model.

        Args:
            model_name (str): Name of the deployed model.

        Returns:
            str: URL of the deployed model.
        """
        kclient = KServeClient()

        time.sleep(plugin_config.TIMER_IN_SEC)
        isvc_resp = kclient.get(model_name)
        isvc_url = isvc_resp["status"]["address"]["url"]
        return isvc_url

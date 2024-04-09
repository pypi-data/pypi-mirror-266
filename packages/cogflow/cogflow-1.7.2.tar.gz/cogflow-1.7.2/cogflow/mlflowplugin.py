"""
This module provides functionality related to Mlflow.
"""

import os
from typing import Union

import mlflow as ml
import numpy as np
import pandas as pd
import requests
from mlflow.models.signature import ModelSignature
from mlflow.tracking import MlflowClient
from scipy.sparse import csr_matrix, csc_matrix

from cogflow import plugin_config


class CogModel(ml.pyfunc.PythonModel):
    """
    A custom Mlflow PythonModel implementation for demonstration purposes.
    """

    @staticmethod
    def fit():
        """
        Train the model.

        This method is called to train the model.
        """
        print("Fitting model...")

    def predict(self, model_input: [str]):  # type: ignore
        """
        Generate predictions.

        This method generates predictions based on the input data.

        Parameters:
            model_input (List[str]): List of input strings for prediction.

        Returns:
            None: This method prints the predictions instead of returning them.
        """
        print(self.get_prediction(model_input))

    def get_prediction(self, model_input: [str]):  # type: ignore
        """
        Generate predictions.

        This method generates predictions based on the input data.

        Parameters:
            model_input (List[str]): List of input strings for prediction.

        Returns:
            str: The concatenated uppercase version of the input strings.
        """

        return " ".join([w.upper() for w in model_input])


class MlflowPlugin:
    """
    Class for defining reusable components.
    """

    def __init__(self):
        """
        Initializes the MlFlowPlugin class.
        """
        self.mlflow = ml
        self.sklearn = ml.sklearn
        self.cogclient = MlflowClient()
        self.pyfunc = ml.pyfunc
        self.models = ml.models

    def is_alive(self):
        """
        Check if Mlflow UI is accessible.

        Returns:
            tuple: A tuple containing a boolean indicating if Mlflow UI is accessible
             and the status code of the response.
        """
        response = requests.get(os.getenv(plugin_config.TRACKING_URI))
        try:
            if response.status_code == 200:
                print("Tracking URI accessible")
            else:
                print(
                    f"Mlflow UI is not accessible. Status code: {response.status_code}, Message: {response.text}"
                )
        except Exception as e:
            print(
                f"An error occurred while accessing Mlflow UI: {str(e)}, "
                f"Status code: {response.status_code}, Message: {response.text}"
            )
        return True, response.status_code, response.text

    @staticmethod
    def version():
        """
        Retrieve the version of the Mlflow.

        Returns:
            str: Version of the Mlflow.
        """
        return ml.__version__

    def delete_registered_model(self, model_name):
        """
        Deletes a registered model with the given name.

        Args:
            model_name (str): The name of the registered model to delete.

        Returns:
            bool: True if the model was successfully deleted, False otherwise.
        """
        return self.cogclient.delete_registered_model(model_name)

    def search_registered_models(self):
        """
        Searches for registered models.

        Returns:
            list: A list of registered model objects matching the search criteria.
        """
        registered_models = self.cogclient.search_registered_models()
        return registered_models

    def load_model(self, model_name: str, model_version: int):
        """
        Loads a model from Mlflow.

        Args:
            model_name (str): The name of the registered Mlflow model.
            model_version (int): The version of the registered Mlflow model.

        Returns:
            loaded_model: The loaded model.
        """
        model_uri = f"models:/{model_name}/{model_version}"
        loaded_model = ml.sklearn.load_model(model_uri)
        return loaded_model

    def register_model(self, model, model_uri):
        """
        Registers the given model with Mlflow.

        Args:
            model: The model object to register.
            model_uri (str): The Mlflow model URI.
        """
        return ml.register_model(model, model_uri)

    def autolog(self):
        """
        Enable automatic logging of parameters, metrics, and models with Mlflow.

        Returns:
            None
        """
        return self.mlflow.autolog()

    def create_registered_model(self, name):
        """
        Create a registered model.

        Args:
            name (str): Name of the registered model.

        Returns:
            str: ID of the created registered model.
        """
        return self.cogclient.create_registered_model(name)

    def create_model_version(self, name, source):
        """
        Create a model version for a registered model.

        Args:
            name (str): Name of the registered model.
            source (str): Source path or URI of the model.

        Returns:
            str: ID of the created model version.
        """
        return self.cogclient.create_model_version(name, source)

    def set_tracking_uri(self, tracking_uri):
        """
        Set the Mlflow tracking URI.

        Args:
            tracking_uri (str): The URI of the Mlflow tracking server.

        Returns:
            None
        """
        return self.mlflow.set_tracking_uri(tracking_uri)

    def set_experiment(self, experiment_name):
        """
        Set the active MLflow experiment.

        Args:
            experiment_name (str): The name of the experiment to set as active.

        Returns:
            None
        """
        return self.mlflow.set_experiment(experiment_name)

    def get_artifact_uri(self, run_id=None):
        """
        Get the artifact URI of the current or specified Mlflow run.

        Args:
            run_id (str, optional): ID of the Mlflow run. If not provided,
            the current run's artifact URI is returned.

        Returns:
            str: Artifact URI of the specified Mlflow run.
        """
        return self.mlflow.get_artifact_uri(run_id)

    def start_run(self, run_name=None):
        """
        Start a Mlflow run.

        Args:
            run_name (str): Name of the Mlflow run.

        Returns:
            Mlflow Run object
        """
        return self.mlflow.start_run(run_name=run_name)

    def end_run(self):
        """
        End a Mlflow run.

        Returns:
            Mlflow Run object
        """
        return self.mlflow.end_run()

    def log_param(self, *args):
        """
        Log parameters to the Mlflow run.

        Args:
            run: Mlflow Run object returned by start_mlflow_run method.
            params (dict): Dictionary containing parameters to log.

        Returns:
            None
        """
        return self.mlflow.log_param(*args)

    def log_metric(self, *args):
        """
        Log metrics to the Mlflow run.

        Args:
            run: Mlflow Run object returned by start_mlflow_run method.
            metrics (dict): Dictionary containing metrics to log.

        Returns:
            None
        """
        return self.mlflow.log_metric(*args)

    def log_model(
        self,
        sk_model,
        artifact_path,
        conda_env=None,
        code_paths=None,
        serialization_format="cloudpickle",
        registered_model_name=None,
        signature: ModelSignature = None,
        input_example: Union[
            pd.DataFrame,
            np.ndarray,
            dict,
            list,
            csr_matrix,
            csc_matrix,
            str,
            bytes,
            tuple,
        ] = None,
        await_registration_for=300,
        pip_requirements=None,
        extra_pip_requirements=None,
        pyfunc_predict_fn="predict",
        metadata=None,
    ):
        """
        Log a scikit-learn model to Mlflow.

        Args:
            sk_model: The scikit-learn model to be logged.
            artifact_path (str): The run-relative artifact path to which the model artifacts will
            be saved.
            conda_env (str, optional): The path to a Conda environment YAML file. Defaults to None.
            code_paths (list, optional): A list of local filesystem paths to Python files that
            contain code to be
            included as part of the model's logged artifacts. Defaults to None.
            serialization_format (str, optional): The format used to serialize the model. Defaults
            to "cloudpickle".
            registered_model_name (str, optional): The name under which to register the model with
            Mlflow. Defaults to None.
            signature (ModelSignature, optional): The signature defining model input and output
            data types and shapes. Defaults to None.
            input_example (Union[pd.DataFrame, np.ndarray, dict, list, csr_matrix, csc_matrix, str,
            bytes, tuple], optional): An example input to the model. Defaults to None.
            await_registration_for (int, optional): The duration, in seconds, to wait for the
            model version to finish being created and is in the READY status. Defaults to 300.
            pip_requirements (str, optional): A file in pip requirements format specifying
            additional pip dependencies for the model environment. Defaults to None.
            extra_pip_requirements (str, optional): A string containing additional pip dependencies
            that should be added to the environment. Defaults to None.
            pyfunc_predict_fn (str, optional): The name of the function to invoke for prediction,
            when the model is a PyFunc model. Defaults to "predict".
            metadata (dict, optional): A dictionary of metadata to log with the model.
            Defaults to None.

        Returns:
            Model: The logged scikit-learn model.

        Raises:
            Exception: If an error occurs during the logging process.

        """
        return self.mlflow.sklearn.log_model(
            sk_model=sk_model,
            artifact_path=artifact_path,
            conda_env=conda_env,
            code_paths=code_paths,
            serialization_format=serialization_format,
            registered_model_name=registered_model_name,
            signature=signature,
            input_example=input_example,
            await_registration_for=await_registration_for,
            pip_requirements=pip_requirements,
            extra_pip_requirements=extra_pip_requirements,
            pyfunc_predict_fn=pyfunc_predict_fn,
            metadata=metadata,
        )

"""
Plugin Manager Module

This module provides a PluginManager class responsible for managing plugins such as MlflowPlugin,
KubeflowPlugin, and DatasetPlugin.
It also includes functions to activate, deactivate, and check the status of plugins.

Attributes:
    mlplugin (class): The Mlflow plugin class.
    kfplugin (class): The Kubeflow plugin class.
    dsplugin (class): The Dataset plugin class.
"""

import importlib
from cogflow.kubeflowplugin import KubeflowPlugin
from cogflow.mlflowplugin import MlflowPlugin
from cogflow.dataset_plugin import DatasetPlugin
from cogflow import plugin_status
from cogflow.plugin_status import plugin_statuses


class PluginManager:
    """
    Class responsible for managing plugins.

    Attributes:
        mlplugin (class): The Mlflow plugin class.
        kfplugin (class): The Kubeflow plugin class.
        dsplugin (class): The Dataset plugin class.
    """

    def __init__(self):
        """
        Initializes the PluginManager with plugin classes.
        """
        self.mlplugin = MlflowPlugin
        self.kfplugin = KubeflowPlugin
        self.dsplugin = DatasetPlugin

    @staticmethod
    def plugin_names():
        """
        Returns a list of plugin names.

        Returns:
            list: A list of plugin names.
        """
        return ["MlflowPlugin", "KubeflowPlugin", "DatasetPlugin"]

    def check_is_alive(self, name):
        """
        Checks if the plugin is alive.

        Args:
            name (str): The name of the plugin.

        Returns:
            tuple: A tuple containing the status and status code.
        """
        status, status_code = name.is_alive(self)
        print(f"ISAlive status of {name} : {status}, {status_code}")

    def version(self, name):
        """
        Gets the version of the plugin.

        Args:
            name (str): The name of the plugin.
        """
        current_version = name.version()
        print(f"current_version of {name} : {current_version}")

    @staticmethod
    def activate_all_plugins():
        """
        Activates all plugins.
        """
        plugins = PluginManager.plugin_names()
        for plugin_name in plugins:
            PluginManager.activate_plugin(plugin_name)

    @staticmethod
    def deactivate_all_plugins():
        """
        Deactivates all plugins.
        """
        plugins = PluginManager.plugin_names()
        for plugin_name in plugins:
            PluginManager.deactivate_plugin(plugin_name)

    @staticmethod
    def activate_plugin(name):
        """
        Activates a specific plugin.

        Args:
            name (str): The name of the plugin to activate.
        """
        if name not in plugin_statuses:
            print(f"{name} does not exist.")
            return
        if plugin_statuses.get(name) == "activated":
            print(f"{name} already in activated status")
        else:
            plugin_statuses[name] = "activated"
            # Reload plugin_status module to reflect changes
            importlib.reload(plugin_status)

            updated_dict = plugin_status.plugin_statuses

            updated_dict.update(plugin_statuses)

            print(f"{name} is now {plugin_statuses.get(name)}")

    @staticmethod
    def deactivate_plugin(name):
        """
        Deactivates a specific plugin.

        Args:
            name (str): The name of the plugin to deactivate.
        """
        if name not in plugin_statuses:
            print(f"{name} does not exist.")
            return
        if plugin_statuses.get(name) == "deactivated":
            print(f"{name} already in deactivated status")
        else:
            plugin_statuses[name] = "deactivated"
            # Reload plugin_status module to reflect changes
            importlib.reload(plugin_status)

            updated_dict = plugin_status.plugin_statuses

            updated_dict.update(plugin_statuses)

            print(f"{name} is now {plugin_statuses.get(name)}")

    @staticmethod
    def plugin_status():
        """
        Prints the status of all plugins.
        """
        print(plugin_statuses)

    def get_plugin(self, name):
        """
        Gets a specific plugin.

        Args:
            name (str): The name of the plugin to get.
        """
        try:
            PluginManager.version(self, name=name)
            PluginManager.check_is_alive(self, name=name)
        except Exception as e:
            print(f"Plugin error : {e}")

    def get_mlflow_plugin(self):
        """
        Gets the Mlflow plugin if activated.
        """
        if plugin_statuses.get("MlflowPlugin") == "activated":
            # If activated, get the plugin
            PluginManager.get_plugin(self, name=self.mlplugin)
            return self.mlplugin
        print("MlflowPlugin is in deactivated status")
        return None

    def get_kflow_plugin(self):
        """
        Gets the Kubeflow plugin if activated.
        """
        if plugin_statuses.get("KubeflowPlugin") == "activated":
            PluginManager.get_plugin(self, name=self.kfplugin)
            return self.kfplugin
        print("KubeflowPlugin is in deactivated status")
        return None

    def get_dataset_plugin(self):
        """
        Gets the Dataset plugin if activated.
        """
        if plugin_statuses.get("DatasetPlugin") == "activated":
            PluginManager.get_plugin(self, name=self.dsplugin)
            return self.dsplugin
        print("DatasetPlugin is in deactivated status")
        return None

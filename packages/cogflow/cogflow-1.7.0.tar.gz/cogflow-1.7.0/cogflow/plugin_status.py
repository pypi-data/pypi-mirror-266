"""
Dictionary representing the status of different plugins.

Keys:
    - "MlflowPlugin": Represents the status of the MLflow plugin.
    - "KubeflowPlugin": Represents the status of the Kubeflow plugin.
    - "DatasetPlugin": Represents the status of the Dataset plugin.

Values:
    - "activated": Indicates that the corresponding plugin is activated and operational.
    - "deactivated": Indicates that the corresponding plugin is deactivated and not operational.
"""

plugin_statuses = {
    "MlflowPlugin": "deactivated",
    "KubeflowPlugin": "deactivated",
    "DatasetPlugin": "deactivated",
}

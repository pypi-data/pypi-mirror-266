"""
Constants for configuring Mlflow and AWS S3.

Attributes:
    TRACKING_URI (str): The URI of the Mlflow tracking server.
    S3_ENDPOINT_URL (str): The endpoint URL of the AWS S3 service.
    ACCESS_KEY_ID (str): The access key ID for AWS S3 authentication.
    SECRET_ACCESS_KEY (str): The secret access key for AWS S3 authentication.
    TIMER_IN_SEC (int): The time interval in seconds for some operations.
    ML_TOOL (str): The name of the machine learning tool, in this case, Mlflow.
"""

TRACKING_URI = "MLFLOW_TRACKING_URI"
S3_ENDPOINT_URL = "MLFLOW_S3_ENDPOINT_URL"
ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
TIMER_IN_SEC = 10
ML_TOOL = "mlflow"

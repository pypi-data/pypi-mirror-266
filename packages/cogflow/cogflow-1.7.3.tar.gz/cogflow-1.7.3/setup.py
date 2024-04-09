from setuptools import setup, find_packages

setup(
    name="cogflow",
    version="1.7.3",
    author="Sai_kireeti",
    author_email="sai.kireeti@hiro-microdatacenters.nl",
    description="cog modules",
    packages=find_packages(),
    install_requires=[
        "mlflow==2.10.2",
        "kfp==1.8.22",
        "boto3",
        "tenacity",
        "pandas",
        "numpy",
        "kubernetes",
        "minio",
        "scikit-learn==1.4.0",
        "awscli",
        "s3fs",
        "setuptools",
        "kserve",
        "tensorflow",
        "ray==2.9.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

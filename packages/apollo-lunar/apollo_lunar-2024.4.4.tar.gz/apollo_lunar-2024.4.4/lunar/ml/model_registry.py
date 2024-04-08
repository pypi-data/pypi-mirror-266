import json
import shlex
import subprocess
from types import ModuleType
from typing import List
from pathlib import Path

import boto3
import cloudpickle
from botocore.exceptions import ClientError

from lunar.config import Config
from lunar.lunar_client import LunarError
from lunar.ml import EDDService, LunarModel


class ModelRegistryError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ModelRegistry:
    def __init__(self, config: Config):
        self.config = config

    def save(
        self,
        lunar_model: LunarModel,
        serialize_modules: List[ModuleType] = [],
        force: bool = False,
        to_local: bool = False,
    ) -> None:

        relative_path = Path("myfiles", "models") if self.config.RUNTIME_ENV == "EDD" else Path("models")
        relative_path = relative_path.joinpath(lunar_model.name, lunar_model.version)

        path = Path.home().joinpath(relative_path)
        path.mkdir(parents=True, exist_ok=True)

        if serialize_modules:
            for module in serialize_modules:
                cloudpickle.register_pickle_by_value(module)

        with open(path.joinpath("model.joblib"), "wb") as f:
            cloudpickle.dump(lunar_model, f)

        with path.joinpath("model.json").open("w") as f:
            json.dump(
                {
                    "name": lunar_model.name,
                    "version": lunar_model.version,
                    "models": [m.__class__.__name__ for m in lunar_model.models],
                    **lunar_model.attrs,
                },
                f,
            )

        if to_local:
            return

        bucket_name = f"lunar-model-registry-{self.config.ENV.lower()}"
        if self.config.RUNTIME_ENV == "EDD":
            res = EDDService(self.config).copy_model_to_s3(
                model_path=f"{relative_path}/", model_name=lunar_model.name, model_version=lunar_model.version
            )
            if res["status"] != 200:
                raise LunarError(code=400, msg=res["error"])

        elif self.config.RUNTIME_ENV == "AIDP":
            s3_path = f"s3a://{bucket_name}/{lunar_model.name}"

            force_option = "-f" if force else ""

            process_mkdir = subprocess.Popen(
                shlex.split(f"hdfs dfs -mkdir -p {s3_path}"),
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            process_mkdir.wait()
            if process_mkdir.returncode != 0:
                raise ModelRegistryError(f"Fail to create a BAP S3 folder: {lunar_model.name}/{lunar_model.version}")

            process_put = subprocess.Popen(
                shlex.split(f"hdfs dfs -put {force_option} {path} {s3_path}"),
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            process_put.wait()
            if process_put.returncode != 0:
                raise ModelRegistryError(f"Fail to dump a model binary: {lunar_model.name}/{lunar_model.version}")

        elif self.config.RUNTIME_ENV == "LOCAL":
            client = boto3.client("s3")

            try:
                client.head_bucket(Bucket=bucket_name)
            except ClientError:
                raise LunarError(code=400, msg=f"Bucket {bucket_name} does not exist.")

            model_path = f"{lunar_model.name}/{lunar_model.version}"

            if not force:
                paginator = client.get_paginator("list_objects_v2")
                for response in paginator.paginate(Bucket=bucket_name, Prefix=model_path):
                    if "Contents" in response:
                        raise LunarError(code=400, msg=f"Model binary & meta files already exist on {model_path}.")

            for file_name in ["model.joblib", "model.json"]:
                try:
                    client.upload_file(
                        Filename=f"{str(path)}/{file_name}", Bucket=bucket_name, Key=f"{model_path}/{file_name}"
                    )
                except ClientError as e:
                    raise LunarError(code=400, msg=str(e))

"""
This file contains the command line arguments for the vLLM's
OpenAI-compatible server. It is kept in a separate file for documentation
purposes.
"""

import argparse
import json
import ssl
import os
import boto3
import tqdm
from pathlib import Path

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", None)
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", None)

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.entrypoints.openai.serving_engine import LoRA

def download_object_from_s3(s3, *, bucket, key, version_id=None, filename):

    kwargs = {"Bucket": bucket, "Key": key}

    if version_id is not None:
        kwargs["VersionId"] = version_id

    object_size = s3.head_object(**kwargs)["ContentLength"]

    if version_id is not None:
        ExtraArgs = {"VersionId": version_id}
    else:
        ExtraArgs = None
    with tqdm.tqdm(total=object_size, unit="B", unit_scale=True, desc=filename) as pbar:
        s3.download_file(
            Bucket=bucket,
            Key=key,
            ExtraArgs=ExtraArgs,
            Filename=filename,
            Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
        )

class LoRAParserAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        lora_list = []
        for item in values:
            name, path = item.split('=')
            if path.startswith("s3://"):
                if AWS_ACCESS_KEY is None or AWS_SECRET_KEY is None:
                    raise Exception("AWS credentials are not set. Please set `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` in your environment variables and restart the command")
                session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
                fragments = list(filter(lambda x: x.__len__() != 0 and x != 's3:', path.split("/")))
                s3 = session.client("s3")
                bucket = fragments[0]
                model = fragments[-1]
                prefix = '/'.join(fragments[1:])
                objects = s3.list_objects_v2(Bucket=bucket, Prefix=f'{prefix}/')
                if objects['KeyCount'] == 0:
                    raise Exception("S3 folder looks empty. Are you sure if the s3 is right ?")
                files = objects['Contents']
                if files.__len__() == 0:
                    raise Exception("S3 folder looks empty. Are you sure if the s3 is right ?")
                # Creating all dirs to make sure that there will be no exception
                path = f'~/.cache/nextai/hub/{model}/'
                path_like = Path(Path.home(), ".cache", "nextai", "hub", model, "tmp")
                dir = os.path.dirname(path_like)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                for object in files:
                    key = object['Key']
                    if not key.endswith("/"):
                        destination_file_name = key.split("/")[-1]
                        destination = Path(Path.home(), ".cache", "nextai", "hub", model, destination_file_name)
                        download_object_from_s3(s3, bucket=bucket, key=key, version_id=None, filename=destination.__str__())
            lora_list.append(LoRA(name, path))
        setattr(namespace, self.dest, lora_list)


def make_arg_parser():
    parser = argparse.ArgumentParser(
        description="vLLM OpenAI-Compatible RESTful API server.")
    parser.add_argument("--host", type=str, default=None, help="host name")
    parser.add_argument("--port", type=int, default=8000, help="port number")
    parser.add_argument(
        "--uvicorn-log-level",
        type=str,
        default="info",
        choices=['debug', 'info', 'warning', 'error', 'critical', 'trace'],
        help="log level for uvicorn")
    parser.add_argument("--allow-credentials",
                        action="store_true",
                        help="allow credentials")
    parser.add_argument("--allowed-origins",
                        type=json.loads,
                        default=["*"],
                        help="allowed origins")
    parser.add_argument("--allowed-methods",
                        type=json.loads,
                        default=["*"],
                        help="allowed methods")
    parser.add_argument("--allowed-headers",
                        type=json.loads,
                        default=["*"],
                        help="allowed headers")
    parser.add_argument("--api-key",
                        type=str,
                        default=None,
                        help="If provided, the server will require this key "
                        "to be presented in the header.")
    parser.add_argument("--served-model-name",
                        type=str,
                        default=None,
                        help="The model name used in the API. If not "
                        "specified, the model name will be the same as "
                        "the huggingface name.")
    parser.add_argument(
        "--lora-modules",
        type=str,
        default=None,
        nargs='+',
        action=LoRAParserAction,
        help="LoRA module configurations in the format name=path. "
        "Multiple modules can be specified.")
    parser.add_argument("--chat-template",
                        type=str,
                        default=None,
                        help="The file path to the chat template, "
                        "or the template in single-line form "
                        "for the specified model")
    parser.add_argument("--response-role",
                        type=str,
                        default="assistant",
                        help="The role name to return if "
                        "`request.add_generation_prompt=true`.")
    parser.add_argument("--ssl-keyfile",
                        type=str,
                        default=None,
                        help="The file path to the SSL key file")
    parser.add_argument("--ssl-certfile",
                        type=str,
                        default=None,
                        help="The file path to the SSL cert file")
    parser.add_argument("--ssl-ca-certs",
                        type=str,
                        default=None,
                        help="The CA certificates file")
    parser.add_argument(
        "--ssl-cert-reqs",
        type=int,
        default=int(ssl.CERT_NONE),
        help="Whether client certificate is required (see stdlib ssl module's)"
    )
    parser.add_argument(
        "--root-path",
        type=str,
        default=None,
        help="FastAPI root_path when app is behind a path based routing proxy")
    parser.add_argument(
        "--middleware",
        type=str,
        action="append",
        default=[],
        help="Additional ASGI middleware to apply to the app. "
        "We accept multiple --middleware arguments. "
        "The value should be an import path. "
        "If a function is provided, vLLM will add it to the server "
        "using @app.middleware('http'). "
        "If a class is provided, vLLM will add it to the server "
        "using app.add_middleware(). ")

    parser = AsyncEngineArgs.add_cli_args(parser)
    return parser

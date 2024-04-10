import os
from pathlib import Path
from typing import Dict, Optional

import grpc
import yaml
from grpc import (
    ssl_channel_credentials,
)

from ._protobufs.bauplan_pb2_grpc import CommanderServiceStub

GRPC_METADATA_HEADER_API_KEY = 'x-bauplan-api-key'


def get_commander_and_metadata() -> (CommanderServiceStub, Dict[str, str]):
    conn: grpc.Channel = dial_commander()
    client: CommanderServiceStub = CommanderServiceStub(conn)
    api_key = load_default_config_profile().get('api_key', '')
    if api_key == '':
        api_key = os.getenv('BPLN_API_KEY', '')
    if api_key == '':
        raise Exception(
            'No API key found in environment. Please update your ~/.bauplan/config.yml or set BPLN_API_KEY.'
        )
    metadata = [(GRPC_METADATA_HEADER_API_KEY, api_key)]
    return client, metadata


def load_default_config_profile() -> dict:
    home_dir = Path.home()
    config_path = home_dir / '.bauplan' / 'config.yml'

    if not config_path.is_file():
        return {}

    with open(config_path, 'r') as config_file:
        config_data = yaml.safe_load(config_file)

    return config_data.get('profiles', {}).get('default', {})


def dial_commander() -> grpc.Channel:
    addr: str = ''
    env: Optional[str] = os.getenv('BPLN_ENV')
    if env == 'local':
        addr = 'localhost:2758'
    elif env == 'dev':
        addr = 'commander-poc.use1.adev.bauplanlabs.com:443'
    elif env == 'qa':
        addr = 'commander-poc.use1.aqa.bauplanlabs.com:443'
    elif env == 'fritzfood':
        addr = 'commander-poc.use1.afritzfood.bauplanlabs.com:443'
    else:
        addr = 'commander-poc.use1.aprod.bauplanlabs.com:443'
    creds: grpc.ChannelCredentials = ssl_channel_credentials()
    conn: grpc.Channel = grpc.secure_channel(addr, creds)
    return conn

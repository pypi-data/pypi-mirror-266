# IMPORTANT
# After changing this file, run `python3 -m missim_config.generate_schemas`
# To re-generate the json schemas

from dataclasses import dataclass
from enum import Enum
from dacite import from_dict, Config
from typing import Any
from dataclasses import asdict
import yaml
import os
from pathlib import Path


MISSIM_CONFIG_FILE_NAME = "missim.yml"
MISSIM_SCHEMA_URL = "https://greenroom-robotics.github.io/missim/schemas/missim.schema.json"


def join_lines(*lines: str) -> str:
    return "\n".join(lines)


class Mode(str, Enum):
    UE_EDITOR = "ue-editor"
    UE_STANDALONE = "ue-standalone"
    LOW_FIDELITY = "low-fidelity"


class LogLevel(str, Enum):
    INFO = "info"
    DEBUG = "debug"


class Network(str, Enum):
    SHARED = "shared"
    HOST = "host"


@dataclass
class MissimConfig:
    ros_domain_id: int = 0
    log_level: LogLevel = LogLevel.INFO
    mode: Mode = Mode.LOW_FIDELITY
    network: Network = Network.HOST
    sim_speed: float = 1.0
    use_https: bool = False


def find_config() -> Path:
    """Returns the path to the .config/greenroom directory"""
    return Path.home().joinpath(".config/greenroom")


def dacite_to_dict(obj: Any):
    def dict_factory(data: Any):
        def convert_value(obj: Any):
            if isinstance(obj, Enum):
                return obj.value
            return obj

        return {k: convert_value(v) for k, v in data}

    return asdict(obj, dict_factory=dict_factory)


def get_path():
    return find_config() / MISSIM_CONFIG_FILE_NAME


def parse(config: dict[str, Any]) -> MissimConfig:
    return from_dict(
        MissimConfig,
        config,
        config=Config(cast=[LogLevel, Mode, Network]),
    )


def read() -> MissimConfig:
    """Reads the missim.yml file and returns a MissimConfig object."""
    path = get_path()
    with open(path) as stream:
        return parse(yaml.safe_load(stream))


def read_env() -> MissimConfig:
    """Reads the MISSIM_CONFIG environment variable and returns a MissimConfig object."""
    missim_config_str = os.environ.get("MISSIM_CONFIG")
    if missim_config_str is None:
        raise ValueError("MISSIM_CONFIG environment variable is not set")
    return parse(yaml.safe_load(missim_config_str))


def write(config: MissimConfig):
    path = get_path()
    # Make the parent dir if it doesn't exist
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as stream:
        print(f"Writing: {path}")
        headers = f"# yaml-language-server: $schema={MISSIM_SCHEMA_URL}"
        data = "\n".join([headers, yaml.dump(dacite_to_dict(config))])
        stream.write(data)


def serialise(config: MissimConfig):
    return yaml.dump(dacite_to_dict(config))

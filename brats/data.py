from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml
from dacite import from_dict

PACKAGE_DIR = Path(__file__).parent
META_DATA_FILE = PACKAGE_DIR / "algorithms.yml"


@dataclass
class MetaData:
    """Dataclass for the meta data"""

    authors: str
    """The authors of the algorithm"""
    paper: str
    """If available, a url to the paper of the algorithm"""


@dataclass
class RunArgs:
    """Dataclass for the run arguments"""

    docker_image: str
    """The Docker image containing the algorithm"""
    shm_size: Optional[str] = "2gb"
    """The required shared memory size for the Docker container"""
    parameters_file: bool
    """Whether the algorithm requires a parameters file"""
    requires_root: bool
    """Whether the Docker container requires root access. This is !discouraged! but some submission do not work without it"""


@dataclass
class WeightsData:
    """Dataclass for the weights data"""

    record_id: str
    """The Zenodo record ID of the weights"""
    param_name: Optional[str] = "weights"
    """The parameter that specifies the weights folder in the algorithm execution, typically 'weights' but differs for some"""


@dataclass
class AlgorithmData:
    """Dataclass for the algorithm data"""

    meta: MetaData
    """The meta data of the algorithm"""
    run_args: RunArgs
    """The run arguments of the algorithm"""
    weights: Optional[WeightsData]
    """The weights data of the algorithm. Optional since some algorithms include weights in the docker image"""


@dataclass
class AlgorithmList:
    algorithms: Dict[str, AlgorithmData]


def load_algorithms() -> Dict[str, AlgorithmData]:
    """Load the algorithms data from the yaml data file

    Raises:
        FileNotFoundError: If the file is not found

    Returns:
        Dict[str, AlgorithmData]: Dict of algorithm key:AlgorithmData  pairs
    """
    try:
        with open(META_DATA_FILE, "r") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Algorithm meta data file not found")

    # Convert the dictionary to the dataclass
    return from_dict(data_class=AlgorithmList, data=data).algorithms

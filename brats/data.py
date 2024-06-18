from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml
from dacite import from_dict


@dataclass
class MetaData:
    """Dataclass for the meta data"""

    authors: str
    """The authors of the algorithm"""
    paper: str
    """If available, a url to the paper of the algorithm"""
    challenge: str
    """The challenge the algorithm was submitted to"""


@dataclass
class RunArgs:
    """Dataclass for the run arguments"""

    docker_image: str
    """The Docker image containing the algorithm"""
    parameters_file: bool
    """Whether the algorithm requires a parameters file"""
    requires_root: bool
    """Whether the Docker container requires root access. This is !discouraged! but some submission do not work without it"""
    shm_size: Optional[str] = "2gb"
    """The required shared memory size for the Docker container"""


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


def load_algorithms(file_path: str) -> Dict[str, AlgorithmData]:
    """Load the algorithms data from the yaml file

    Params:
        file_path (str): The path to the yaml file

    Raises:
        FileNotFoundError: If the file is not found

    Returns:
        Dict[str, AlgorithmData]: Dict of algorithm @AlgorithmKeys:@AlgorithmData  pairs
    """
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Algorithm meta data file not found")

    # Convert the dictionary to the dataclass
    return from_dict(data_class=AlgorithmList, data=data).algorithms

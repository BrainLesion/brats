from enum import Enum
from pathlib import Path


class Algorithms(str, Enum):
    """Parent class for constants of the available algorithms."""

    pass


class AdultGliomaAlgorithms(Algorithms):
    """Constants for the available adult glioma segmentation algorithms."""

    BraTS23_1 = "BraTS23_1"
    """BraTS23 Adult Glioma Segmentation 1st place (GPU only)"""
    BraTS23_2 = "BraTS23_2"
    """BraTS23 Adult Glioma Segmentation 2nd place (GPU only)"""
    BraTS23_3 = "BraTS23_3"
    """BraTS23 Adult Glioma Segmentation 3rd place (GPU only)"""


class MeningiomaAlgorithms(Algorithms):
    """Constants for the available meningioma segmentation algorithms."""

    BraTS23_1 = "BraTS23_1"
    """BraTS23 Meningioma Segmentation 1st place (GPU only)"""
    BraTS23_2 = "BraTS23_2"
    """BraTS23 Meningioma Segmentation 2nd place (GPU and CPU)"""
    BraTS23_3 = "BraTS23_3"
    """BraTS23 Meningioma Segmentation 3rd place (GPU only)"""


class PediatricAlgorithms(Algorithms):
    """Constants for the available pediatric segmentation algorithms."""

    BraTS23_1 = "BraTS23_1"
    """BraTS23 Pediatric Segmentation 1st place (GPU only)"""
    BraTS23_2 = "BraTS23_2"
    """BraTS23 Pediatric Segmentation 2nd place (GPU only)"""
    BraTS23_3 = "BraTS23_3"
    """BraTS23 Pediatric Segmentation 3rd place (GPU only)"""


class AfricaAlgorithms(Algorithms):
    """Constants for the available africa segmentation algorithms."""

    BraTS23_1 = "BraTS23_1"
    """BraTS23 BraTS-Africa Segmentation 1st place (GPU only)"""
    BraTS23_2 = "BraTS23_2"
    """BraTS23 BraTS-Africa Segmentation 2nd place (GPU only)"""
    BraTS23_3 = "BraTS23_3"
    """BraTS23 BraTS-Africa Segmentation 3rd place (GPU and CPU)"""


class MetastasesAlgorithms(Algorithms):
    """Constants for the available Brain Metastases segmentation algorithms."""

    BraTS23_1 = "BraTS23_1"
    """BraTS23  Brain Metastases Segmentation 1st place (GPU only)"""
    BraTS23_2 = "BraTS23_2"
    """BraTS23  Brain Metastases Segmentation 2nd place (GPU only)"""
    BraTS23_3 = "BraTS23_3"
    """BraTS23  Brain Metastases Segmentation 3rd place (GPU only)"""


# meta data file paths
ALGORITHM_DIR = Path(__file__).parent / "algorithms" / "meta"
PARAMETERS_DIR = ALGORITHM_DIR / "parameters"
DUMMY_PARAMETERS = PARAMETERS_DIR / "dummy.yml"
ADULT_GLIOMA_SEGMENTATION_ALGORITHMS = ALGORITHM_DIR / "adult_glioma.yml"
MENINGIOMA_SEGMENTATION_ALGORITHMS = ALGORITHM_DIR / "meningioma.yml"
PEDIATRIC_SEGMENTATION_ALGORITHMS = ALGORITHM_DIR / "pediatric.yml"
AFRICA_SEGMENTATION_ALGORITHMS = ALGORITHM_DIR / "africa.yml"
METASTASES_SEGMENTATION_ALGORITHMS = ALGORITHM_DIR / "metastases.yml"

WEIGHTS_FOLDER = Path(__file__).parent / "weights"
ZENODO_RECORD_BASE_URL = "https://zenodo.org/api/records"

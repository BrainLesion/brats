from __future__ import annotations

import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from loguru import logger

from brats.algorithm_config import load_algorithms
from brats.constants import (
    ADULT_GLIOMA_INPUT_NAME_SCHEMA,
    ADULT_GLIOMA_SEGMENTATION_ALGORITHMS,
    MENINGIOMA_INPUT_NAME_SCHEMA,
    MENINGIOMA_SEGMENTATION_ALGORITHMS,
    PEDIATRIC_INPUT_NAME_SCHEMA,
    PEDIATRIC_SEGMENTATION_ALGORITHMS,
    AdultGliomaAlgorithms,
    Algorithms,
    MeningiomaAlgorithms,
    PediatricAlgorithms,
)
from brats.docker import run_docker
from brats.utils import standardize_subject_inputs, handle_signals
import sys

# logger setup
logger.remove(0)  # remove default stderr logger in order to add custom
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
)
handle_signals()


class BraTSInferer:
    def __init__(
        self,
        algorithm: Algorithms,
        algorithms_file_path: Path,
        cuda_devices: Optional[str] = "0",
        force_cpu: bool = False,
    ):

        # inference device setup
        self.force_cpu = force_cpu
        self.cuda_devices = cuda_devices

        self.algorithm_list = load_algorithms(file_path=algorithms_file_path)
        # save algorithm identifier for logging etc.
        self.algorithm_key = algorithm.value
        # data for selected algorithm
        self.algorithm = self.algorithm_list[algorithm.value]

        logger.info(
            f"Instantiated {self.__class__.__name__} with algorithm: {self.algorithm_key} by {self.algorithm.meta.authors}"
        )

    def _log_algorithm_info(self):
        """Log information about the selected algorithm."""
        logger.opt(colors=True).info(
            f"Running algorithm: <light-green>{self.algorithm.meta.challenge}</>"
        )
        logger.opt(colors=True).info(
            f"<blue>(Docker image)</>: {self.algorithm.run_args.docker_image}"
        )
        logger.opt(colors=True).info(
            f"<blue>(Paper)</> Consider citing the corresponding paper: {self.algorithm.meta.paper} by {self.algorithm.meta.authors}"
        )

    def infer_single(
        self,
        t1c: Path | str,
        t1n: Path | str,
        t2f: Path | str,
        t2w: Path | str,
        output_file: Path | str,
        log_file: Optional[Path | str] = None,
    ):
        """Perform inference on a single subject with the provided images and save the result to the output file.

        Args:
            t1c (Path | str): Path to the T1c image
            t1n (Path | str): Path to the T1n image
            t2f (Path | str): Path to the T2f image
            t2w (Path | str): Path to the T2w image
            output_file (Path | str): Path to save the segmentation
            log_file (Path | str, optional): Save logs to this file
        """
        # setup temp input folder with the provided images
        temp_data_folder = Path(tempfile.mkdtemp())
        temp_output_folder = Path(tempfile.mkdtemp())
        if log_file is not None:
            inference_log_file = logger.add(log_file, level="INFO")
            logger.info(f"Logging to: {log_file}")

        try:
            logger.info(f"Performing single inference ")

            # the id here is arbitrary
            subject_id = self.algorithm.run_args.input_name_schema.format(id=0)

            standardize_subject_inputs(
                data_folder=temp_data_folder,
                subject_id=subject_id,
                t1c=t1c,
                t1n=t1n,
                t2f=t2f,
                t2w=t2w,
            )

            self._log_algorithm_info()
            run_docker(
                algorithm=self.algorithm,
                data_path=temp_data_folder,
                output_path=temp_output_folder,
                cuda_devices=self.cuda_devices,
                force_cpu=self.force_cpu,
            )
            # rename output
            segmentation = Path(temp_output_folder) / f"{subject_id}.nii.gz"

            # ensure path exists and rename output to the desired path
            output_file = Path(output_file).absolute()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(segmentation, output_file)
            logger.info(f"Saved segmentation to: {output_file}")

        finally:
            shutil.rmtree(temp_data_folder)
            shutil.rmtree(temp_output_folder)
            if log_file is not None:
                logger.remove(inference_log_file)

    def infer_batch(
        self,
        data_folder: Path | str,
        output_folder: Path | str,
        log_file: Optional[Path | str] = None,
    ):
        """Perform segmentation on a batch of subjects with the provided images and save the segmentations to the output folder. \n
        Requires the following structure:\n
        data_folder\n
        ┣ A\n
        ┃ ┣ A-t1c.nii.gz\n
        ┃ ┣ A-t1n.nii.gz\n
        ┃ ┣ A-t2f.nii.gz\n
        ┃ ┗ A-t2w.nii.gz\n
        ┣ B\n
        ┃ ┣ B-t1c.nii.gz\n
        ┃ ┣ ...\n


        Args:
            data_folder (Path | str): Folder containing the subjects with required structure
            output_folder (Path | str): Output folder to save the segmentations
            log_file (Path | str, optional): Save logs to this file
        """

        data_folder = Path(data_folder)
        output_folder = Path(output_folder)

        temp_data_folder = Path(tempfile.mkdtemp())
        temp_output_folder = Path(tempfile.mkdtemp())
        if log_file:
            inference_log_file = logger.add(log_file, level="INFO")
            logger.info(f"Logging to: {log_file}")
        try:
            self._log_algorithm_info()
            # find subjects
            subjects = [f for f in data_folder.iterdir() if f.is_dir()]
            logger.info(
                f"Found {len(subjects)} subjects: {', '.join([s.name for s in subjects][:5])} {' ...' if len(subjects) > 5 else '' }"
            )
            # map to brats names
            subject_id_name_map = {}
            for i, subject in enumerate(subjects):
                subject_id = self.algorithm.run_args.input_name_schema.format(id=i)
                subject_id_name_map[subject_id] = subject.name
                # TODO Add support for .nii files
                standardize_subject_inputs(
                    data_folder=temp_data_folder,
                    subject_id=subject_id,
                    t1c=subject / f"{subject.name}-t1c.nii.gz",
                    t1n=subject / f"{subject.name}-t1n.nii.gz",
                    t2f=subject / f"{subject.name}-t2f.nii.gz",
                    t2w=subject / f"{subject.name}-t2w.nii.gz",
                )

            # infer
            run_docker(
                algorithm=self.algorithm,
                data_path=temp_data_folder,
                output_path=temp_output_folder,
                cuda_devices=self.cuda_devices,
                force_cpu=self.force_cpu,
            )
            # move outputs and change name
            count = 0
            for subject_id, subject_name in subject_id_name_map.items():
                segmentation = Path(temp_output_folder) / f"{subject_id}.nii.gz"
                output_file = output_folder / f"{subject_name}.nii.gz"
                shutil.move(segmentation, output_file)
                count += 1
            logger.info(f"Saved segmentations to: {output_folder}")
        finally:
            shutil.rmtree(temp_data_folder)
            shutil.rmtree(temp_output_folder)
            if log_file:
                logger.remove(inference_log_file)


class AdultGliomaInferer(BraTSInferer):

    def __init__(
        self,
        algorithm: AdultGliomaAlgorithms = AdultGliomaAlgorithms.BraTS23_1,
        cuda_devices: Optional[str] = "0",
        force_cpu: bool = False,
    ):
        super().__init__(
            algorithm=algorithm,
            algorithms_file_path=ADULT_GLIOMA_SEGMENTATION_ALGORITHMS,
            cuda_devices=cuda_devices,
            force_cpu=force_cpu,
        )


class MeningiomaInferer(BraTSInferer):

    def __init__(
        self,
        algorithm: MeningiomaAlgorithms = MeningiomaAlgorithms.BraTS23_1,
        cuda_devices: Optional[str] = "0",
        force_cpu: bool = False,
    ):
        super().__init__(
            algorithm=algorithm,
            algorithms_file_path=MENINGIOMA_SEGMENTATION_ALGORITHMS,
            cuda_devices=cuda_devices,
            force_cpu=force_cpu,
        )


class PediatricInferer(BraTSInferer):

    def __init__(
        self,
        algorithm: PediatricAlgorithms = PediatricAlgorithms.BraTS23_1,
        cuda_devices: Optional[str] = "0",
        force_cpu: bool = False,
    ):
        super().__init__(
            algorithm=algorithm,
            algorithms_file_path=PEDIATRIC_SEGMENTATION_ALGORITHMS,
            cuda_devices=cuda_devices,
            force_cpu=force_cpu,
        )

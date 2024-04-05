"""Tasks for transferring scratch data to custom location for post-pipeline analysis."""
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.globus import GlobusTransferItem
from dkist_processing_common.tasks.trial_output_data import TransferTrialDataBase

__all__ = ["TransferCryoTrialData"]

from dkist_processing_cryonirsp.models.task_name import CryonirspTaskName


class TransferCryoTrialData(TransferTrialDataBase):
    """Transfer DEBUG, Intermediate, and/or output data to the trial location."""

    @property
    def intermediate_task_names(self) -> list[str]:
        """Grab all the Calibration products used to calibrate science data."""
        return [
            TaskName.dark.value,
            TaskName.lamp_gain.value,
            TaskName.geometric_angle.value,
            TaskName.geometric_offsets.value,
            TaskName.geometric_spectral_shifts.value,
            TaskName.solar_gain.value,
            TaskName.demodulation_matrices.value,
            CryonirspTaskName.spectral_corrected_solar_array.value,
        ]

    def build_transfer_list(self) -> list[GlobusTransferItem]:
        """
        Build a list containing all files we want to transfer to the trial environment.

        The classes of/specific files to transfer are defined in the switches that look at the recipe run configuration.
        """
        transfer_list = []

        if self.debug_frame_switch:
            transfer_list += self.build_debug_frame_transfer_list()

        if self.intermediate_frame_switch:
            transfer_list += self.build_intermediate_frame_transfer_list()

        if self.output_frame_switch:
            transfer_list += self.build_output_frame_transfer_list()
            transfer_list += self.build_output_movie_transfer_list()

        if self.specific_frame_tag_lists:
            transfer_list += self.build_transfer_list_from_tag_lists(self.specific_frame_tag_lists)

        if self.output_dataset_inventory_switch:
            transfer_list += self.build_output_dataset_inventory_transfer_list()

        if self.output_asdf_switch:
            transfer_list += self.build_output_asdf_transfer_list()

        return transfer_list

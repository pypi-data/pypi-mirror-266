"""Buds to parse exposure time."""
from typing import Hashable

from dkist_processing_common.models.flower_pot import Stem

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspRampFitsAccess


class CryonirspTimeObsBud(Stem):
    """
    Produce a tuple of all time_obs values present in the dataset.

    The time_obs is a unique identifier for all raw frames in a single ramp. Hence, this list identifies all
    the ramps that must be processed in a data set.
    """

    def __init__(self):
        super().__init__(stem_name=CryonirspBudName.time_obs_list.value)

    def setter(self, fits_obj: CryonirspRampFitsAccess):
        """
        Set the time_obs for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The time_obs value associated with this fits object
        """
        return fits_obj.time_obs

    def getter(self, key: Hashable) -> tuple:
        """
        Get the sorted tuple of time_obs values.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        A tuple of exposure times
        """
        time_obs_tup = tuple(sorted(set(self.key_to_petal_dict.values())))
        return time_obs_tup

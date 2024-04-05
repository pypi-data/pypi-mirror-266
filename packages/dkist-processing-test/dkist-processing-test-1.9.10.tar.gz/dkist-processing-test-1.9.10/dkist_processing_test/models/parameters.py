import numpy as np
from astropy.io import fits
from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.parameters import ParameterWavelengthMixin


class TestParameters(ParameterBase, ParameterWavelengthMixin):
    """Class to test loading parameters from a file."""

    @property
    def randomness(self) -> (float, float):
        """A dummy parameter that requires loading a file."""
        with open(self._find_most_recent_past_value("test_random_data")["param_path"], "rb") as f:
            data = fits.open(f)[0].data
            mean = np.nanmean(data)
            std = np.nanstd(data)

        return mean, std

    @property
    def constant(self) -> float:
        """A dummy parameter that depends on the same file as a different parameter."""
        with open(self._find_most_recent_past_value("test_random_data")["param_path"], "rb") as f:
            data = fits.open(f)[1].data
            constant = np.median(data)

        return float(constant)

    @property
    def wavelength_category(self) -> str:
        """A dummy parameter that depends on wavelength."""
        return self._find_parameter_closest_wavelength("test_wavelength_category")

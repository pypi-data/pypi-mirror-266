from datetime import datetime

import numpy as np
import pytest
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetParameterValue

from dkist_processing_test.models.parameters import TestParameters


@pytest.fixture(scope="session")
def file_parameter(
    tmp_path_factory, random_parameter_hdulist, parameter_file_object_key
) -> tuple[InputDatasetParameterValue, float, float, float]:
    hdul, mu, std, const = random_parameter_hdulist
    file_path = tmp_path_factory.mktemp("parameters") / parameter_file_object_key
    hdul.writeto(file_path)

    value = {
        "bucket": "raw",
        "objectKey": parameter_file_object_key,
        "param_path": file_path,
        "is_file": True,
    }

    parameter_value = InputDatasetParameterValue(
        parameter_value_id=1,
        parameter_value=value,
        parameter_value_start_date=datetime(1946, 11, 20),
    )
    return parameter_value, mu, std, const


@pytest.fixture(scope="session")
def wavelength_parameter() -> InputDatasetParameterValue:
    value = {"wavelength": [1.0, 2.0, 3.0], "values": ["one", "two", "three"]}

    parameter_value = InputDatasetParameterValue(
        parameter_value_id=2,
        parameter_value=value,
        parameter_value_start_date=datetime(1946, 11, 20),
    )
    return parameter_value


@pytest.fixture(scope="session")
def parameter_dict_with_path(file_parameter, wavelength_parameter):
    """Enough of an input dataset parameters part to exercise file loading parameters."""
    file_parameter_value, _, _, _ = file_parameter

    param_dict = {
        "test_random_data": [file_parameter_value],
        "test_wavelength_category": [wavelength_parameter],
    }

    return param_dict


@pytest.fixture(scope="session")
def task_with_parameters(parameter_dict_with_path):
    class TaskWithParameters(WorkflowTaskBase):
        def __init__(
            self,
            recipe_run_id: int,
            workflow_name: str,
            workflow_version: str,
        ):
            super().__init__(
                recipe_run_id=recipe_run_id,
                workflow_name=workflow_name,
                workflow_version=workflow_version,
            )
            self.parameters = TestParameters(parameter_dict_with_path, wavelength=2.0)

        def run(self):
            """Do stuff."""
            pass

    task = TaskWithParameters(
        recipe_run_id=0,
        workflow_name="do_stuff",
        workflow_version="VX.Y",
    )

    return task


def test_parameter(task_with_parameters, file_parameter):
    """
    Given: A task with parameters that depend on files
    When: Accessing those parameters
    Then: The correct values are returned
    """
    task = task_with_parameters
    _, mu, std, const = file_parameter

    assert type(task.parameters.randomness) is tuple
    np.testing.assert_allclose(np.array(task.parameters.randomness), np.array([mu, std]), rtol=1)

    assert task.parameters.constant == const
    assert task.parameters.wavelength_category == "two"

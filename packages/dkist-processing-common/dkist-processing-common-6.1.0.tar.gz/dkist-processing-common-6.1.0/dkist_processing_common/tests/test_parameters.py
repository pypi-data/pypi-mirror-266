"""
HOW TO WRITE TESTS FOR NEW PARAMETER SUBCLASSES :

1. Add parameters to INPUT_DATASET that exercise the necessary logic (this won't be needed in all cases)
2. Create a Parameter object that subclasses `FilledParameters` and the new subclass
3. Create a helper function that returns the `partial` of the new class with the new kwargs already filled in
4. Add a `pytest.param` with this helper function to `test_parameters` to make sure none of the default stuff broke
5. Write a new test that only uses the helper function to test the new functionality.
"""
import json
from datetime import datetime
from datetime import timedelta
from functools import partial
from typing import Any
from typing import Type

import pytest

from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.parameters import ParameterWavelengthMixin
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin

INPUT_DATASET = [
    {
        "parameterName": "basic_param",
        "parameterValues": [
            {
                "parameterValueId": 1,
                "parameterValue": json.dumps([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                "parameterValueStartDate": "2000-01-01",
            }
        ],
    },
    {
        "parameterName": "no_date",
        "parameterValues": [{"parameterValueId": 1, "parameterValue": json.dumps(4)}],
    },
    {
        "parameterName": "three_values",
        "parameterValues": [
            {
                "parameterValueId": 1,
                "parameterValue": json.dumps(4),
                "parameterValueStartDate": "2020-03-13",
            },
            {
                "parameterValueId": 2,
                "parameterValue": json.dumps(6),
                "parameterValueStartDate": "1955-01-02",
            },
            {
                "parameterValueId": 3,
                "parameterValue": json.dumps(5),
                "parameterValueStartDate": (
                    datetime.now() + timedelta(days=365)
                ).isoformat(),  # Guaranteed to be in the future!
            },
        ],
    },
    {
        "parameterName": "two_values_one_date",
        "parameterValues": [
            {"parameterValueId": 1, "parameterValue": json.dumps(4)},
            {
                "parameterValueId": 2,
                "parameterValue": json.dumps(6),
                "parameterValueStartDate": "1955-01-02",
            },
        ],
    },
    {
        "parameterName": "wavelength_param",
        "parameterValues": [
            {
                "parameterValueId": 1,
                "parameterValue": json.dumps(
                    {"wavelength": [10, 20, 30, 40], "values": [1, 2, 3, 4]}
                ),
            }
        ],
    },
]


@pytest.fixture()
def input_dataset_parts() -> tuple[Any, str]:
    return (INPUT_DATASET, Tag.input_dataset_parameters())


@pytest.fixture()
def task_class_with_parameters(parameter_class) -> Type[WorkflowTaskBase]:
    class TaskWithParameters(WorkflowTaskBase, InputDatasetMixin):
        def __init__(self, recipe_run_id: int, workflow_name: str, workflow_version: str):
            super().__init__(
                recipe_run_id=recipe_run_id,
                workflow_name=workflow_name,
                workflow_version=workflow_version,
            )
            self.parameters = parameter_class(
                input_dataset_parameters=self.input_dataset_parameters
            )

        def run(self) -> None:
            pass

    return TaskWithParameters


@pytest.fixture()
def task_with_parameters(task_with_input_dataset, task_class_with_parameters):
    task_class = task_class_with_parameters
    return task_class(
        recipe_run_id=task_with_input_dataset.recipe_run_id,
        workflow_name=task_with_input_dataset.workflow_name,
        workflow_version=task_with_input_dataset.workflow_version,
    )


class FilledParameters(ParameterBase):
    @property
    def basic_parameter(self):
        return self._find_most_recent_past_value("basic_param")

    @property
    def no_date_parameter(self):
        return self._find_most_recent_past_value("no_date")

    @property
    def three_values_parameter(self):
        return self._find_most_recent_past_value("three_values")

    @property
    def two_values_one_date_parameter(self):
        return self._find_most_recent_past_value("two_values_one_date")


class FilledParametersWithObsTime(FilledParameters):
    @property
    def test_parameter_based_on_obs_time(self):
        return self._find_most_recent_past_value(
            "three_values", start_date=self._obs_ip_start_datetime
        )


def parameter_class_with_obs_ip_start_time():
    obs_ip_start_time = "1955-02-03"
    return partial(FilledParametersWithObsTime, obs_ip_start_time=obs_ip_start_time)


class FilledWavelengthParameters(FilledParameters, ParameterWavelengthMixin):
    @property
    def wavelength_parameter(self):
        return self._find_parameter_closest_wavelength("wavelength_param")

    @property
    def interpolated_wavelength_parameter(self):
        return self._interpolate_wavelength_parameter("wavelength_param", method="linear")


def parameter_class_with_wavelength():
    wavelength = 25  # Exactly halfway between 20 and 30
    return partial(FilledWavelengthParameters, wavelength=wavelength)


@pytest.mark.parametrize(
    "parameter_class",
    [
        pytest.param(FilledParameters, id="Basic Parameters"),
        pytest.param(
            parameter_class_with_obs_ip_start_time(),
            id="Parameters with OBS IP start time",
        ),
        pytest.param(parameter_class_with_wavelength(), id="Wavelength parameters"),
    ],
)
def test_parameters(task_with_parameters, input_dataset_parts: tuple[Any, str]):
    """ "
    Given: a task with a ParameterBase subclass and populated parameters
    When: asking for specific parameter values
    Then: the correct values are returned
    """
    assert task_with_parameters.parameters.basic_parameter == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert task_with_parameters.parameters.no_date_parameter == 4

    # Make sure the most recent value is returned, but not from the future
    assert task_with_parameters.parameters.three_values_parameter == 4

    # Make sure the value with *any* date is returned
    assert task_with_parameters.parameters.two_values_one_date_parameter == 6

    # Raise an error if all values in the db are in the "future"
    with pytest.raises(ValueError):
        task_with_parameters.parameters._find_most_recent_past_value(
            "basic_param", start_date=datetime(1776, 7, 4)
        )


@pytest.mark.parametrize(
    "parameter_class",
    [
        pytest.param(
            parameter_class_with_obs_ip_start_time(),
            id="Parameters with OBS IP start time",
        ),
    ],
)
def test_parameters_with_obs_ip_start_time(
    task_with_parameters, input_dataset_parts: tuple[Any, str]
):
    """
    Given: a task with a ParameterBase subclass that uses the obs_ip_start_time kwarg
    When: asking for a parameter that needs the obs ip start time
    Then: the correct value is returned
    """
    assert task_with_parameters.parameters.test_parameter_based_on_obs_time == 6


@pytest.mark.parametrize(
    "parameter_class",
    [
        pytest.param(
            parameter_class_with_wavelength(),
            id="Wavelength parameters",
        ),
    ],
)
def test_wavelength_parameters(task_with_parameters, input_dataset_parts: tuple[Any, str]):
    """
    Given: a task with a parameter class that subclasses ParameterWavelengthMixin
    When: asking for a parameter that needs the wavelength
    Then: the correct value is returned
    """
    assert task_with_parameters.parameters.wavelength_parameter == 2
    assert task_with_parameters.parameters.interpolated_wavelength_parameter == 2.5


def test_mixins_error_with_no_arg():
    """
    Given: A Parameter class based on a ParameterMixin
    When: Instantiating that class withOUT an arg required by the mixin
    Then: An error is raised
    """
    with pytest.raises(TypeError):
        parameters = FilledWavelengthParameters(input_dataset_parameters={"foo": []})

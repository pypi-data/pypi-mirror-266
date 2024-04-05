import json

import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tests.conftest import FakeGQLClient

from dkist_processing_visp.tasks.quality_metrics import VispL1QualityMetrics
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import write_full_sci_outputs_to_task


@pytest.fixture(scope="function")
def visp_quality_task(tmp_path, pol_mode, recipe_run_id, init_visp_constants_db):
    num_map_scans = 3
    num_raster_steps = 2
    num_stokes = 4
    if pol_mode == "observe_intensity":
        num_stokes = 1
    constants_db = VispConstantsDb(
        POLARIMETER_MODE=pol_mode,
        NUM_MAP_SCANS=num_map_scans,
        NUM_RASTER_STEPS=num_raster_steps,
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with VispL1QualityMetrics(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path)

        yield task, num_map_scans, num_raster_steps, num_stokes
        task._purge()


@pytest.mark.parametrize("pol_mode", ["observe_polarimetric", "observe_intensity"])
def test_quality_task(visp_quality_task, pol_mode, mocker):
    """
    Given: A VISPQualityMetrics task
    When: Calling the task instance
    Then: A single sensitivity measurement and datetime is recorded for each map scan for each Stokes Q, U, and V,
            and a single noise measurement and datetime is recorded for L1 file for each Stokes Q, U, and V
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    # When
    task, num_maps, num_steps, num_stokes = visp_quality_task
    write_full_sci_outputs_to_task(
        task, num_maps=num_maps, num_steps=num_steps, data_shape=(10, 10), pol_mode=pol_mode
    )

    task()
    # Then
    num_map_scans = task.constants.num_map_scans
    num_steps = task.constants.num_raster_steps
    sensitivity_files = list(task.read(tags=[Tag.quality("SENSITIVITY")]))
    assert len(sensitivity_files) == num_stokes
    for file in sensitivity_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            for time in range(len(data["x_values"])):
                assert type(data["x_values"][time]) == str
            for noise in range(len(data["y_values"])):
                assert type(data["y_values"][noise]) == float
            assert len(data["x_values"]) == len(data["y_values"]) == num_map_scans

    noise_files = list(task.read(tags=[Tag.quality("NOISE")]))
    assert len(noise_files) == num_stokes
    for file in noise_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            for time in range(len(data["x_values"])):
                assert type(data["x_values"][time]) == str
            for noise in range(len(data["y_values"])):
                assert type(data["y_values"][noise]) == float
            assert len(data["x_values"]) == len(data["y_values"]) == num_map_scans * num_steps

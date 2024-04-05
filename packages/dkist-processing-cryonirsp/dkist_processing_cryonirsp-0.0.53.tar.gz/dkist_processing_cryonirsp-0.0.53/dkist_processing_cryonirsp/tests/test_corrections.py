import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin
from dkist_processing_common.tests.conftest import FakeGQLClient

from dkist_processing_cryonirsp.models.constants import CryonirspConstants
from dkist_processing_cryonirsp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb

base_bad_pixel_map = np.zeros(shape=(10, 10))

normal_bad_pixel_map = base_bad_pixel_map.copy()
normal_bad_pixel_map[1, 6] = 1

column_error_bad_pixel_map = base_bad_pixel_map.copy()
column_error_bad_pixel_map[:, 6] = 1


class BadPixelMapTask(WorkflowTaskBase, CorrectionsMixin, InputDatasetMixin):
    constants: CryonirspConstants

    @property
    def constants_model_class(self):
        """Get CryoNIRSP pipeline constants."""
        return CryonirspConstants

    def run(self):
        pass


@pytest.fixture(params=["CI", "SP"])
def bad_pixel_mask_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    mocker,
    request,
    init_cryonirsp_constants_db,
):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    constants_db = CryonirspConstantsDb(
        ARM_ID=request.param,
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with BadPixelMapTask(
        recipe_run_id=recipe_run_id,
        workflow_name="bad_pixel_mask",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(param_path=tmp_path)
            assign_input_dataset_doc_to_task(task, param_class())
            yield task
        finally:
            task._purge()


@pytest.mark.parametrize(
    "bad_pixel_map, algorithm_type",
    [
        pytest.param(normal_bad_pixel_map, "normal", id="normal algorithm"),
        pytest.param(column_error_bad_pixel_map, "fast", id="fast algorithm"),
    ],
)
def test_corrections_correct_bad_pixels(bad_pixel_map, algorithm_type, bad_pixel_mask_task):
    t = bad_pixel_mask_task
    bad_pixel_x = 1
    bad_pixel_y = 6
    array_to_fix = np.random.random(size=(10, 10))
    # Assign a single bad pixel to check against
    array_to_fix[bad_pixel_x, bad_pixel_y] = 0
    corrected_array = t.corrections_correct_bad_pixels(
        array_to_fix=array_to_fix, bad_pixel_map=bad_pixel_map
    )
    if algorithm_type == "fast":
        for val in corrected_array[:, bad_pixel_y]:
            assert val == np.nanmedian(array_to_fix)
        assert corrected_array[bad_pixel_x, bad_pixel_y] != 0
    if algorithm_type == "normal":
        x, y = np.meshgrid(np.arange(10), np.arange(10))
        idx = np.where((x != bad_pixel_x) | (y != bad_pixel_y))
        np.testing.assert_array_equal(corrected_array[idx], array_to_fix[idx])
        assert corrected_array[bad_pixel_x, bad_pixel_y] != np.nanmedian(array_to_fix)
        assert corrected_array[bad_pixel_x, bad_pixel_y] != 0

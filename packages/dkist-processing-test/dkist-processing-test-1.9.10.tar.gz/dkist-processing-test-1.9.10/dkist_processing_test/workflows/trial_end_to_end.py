"""
Workflow which exercises the common tasks end to end in a trial scenario
"""
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import Workflow

from dkist_processing_test.tasks import AssembleTestMovie
from dkist_processing_test.tasks import GenerateCalibratedData
from dkist_processing_test.tasks import MakeTestMovieFrames
from dkist_processing_test.tasks import ParseL0TestInputData
from dkist_processing_test.tasks import TransferTestTrialData
from dkist_processing_test.tasks import WriteL1Data

trial = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="trial-e2e",
    workflow_package=__package__,
)
trial.add_node(task=TransferL0Data, upstreams=None)
trial.add_node(task=ParseL0TestInputData, upstreams=TransferL0Data)
trial.add_node(task=GenerateCalibratedData, upstreams=ParseL0TestInputData)
trial.add_node(task=WriteL1Data, upstreams=GenerateCalibratedData)
trial.add_node(task=MakeTestMovieFrames, upstreams=WriteL1Data)
trial.add_node(task=AssembleTestMovie, upstreams=MakeTestMovieFrames)
trial.add_node(task=CreateTrialDatasetInventory, upstreams=WriteL1Data, pip_extras=["inventory"])
trial.add_node(task=CreateTrialAsdf, upstreams=WriteL1Data, pip_extras=["asdf"])
trial.add_node(
    task=TransferTestTrialData,
    upstreams=[CreateTrialDatasetInventory, CreateTrialAsdf, AssembleTestMovie],
)
trial.add_node(task=TrialTeardown, upstreams=TransferTestTrialData)

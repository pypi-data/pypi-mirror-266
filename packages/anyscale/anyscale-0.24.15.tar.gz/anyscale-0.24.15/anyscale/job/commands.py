from anyscale._private.sdk import sdk_command
from anyscale.job._private.job_sdk import JobSDK
from anyscale.job.models import JobConfig


_JOB_SDK_SINGLETON_KEY = "job_sdk"

_SUBMIT_EXAMPLE = """\
import anyscale
from anyscale.job.models import JobConfig

anyscale.job.submit(
    JobConfig(
        name="my-job",
        entrypoint="python main.py",
        working_dir=".",
    ),
)
"""


@sdk_command(
    _JOB_SDK_SINGLETON_KEY,
    JobSDK,
    doc_py_example=_SUBMIT_EXAMPLE,
    arg_docstrings={"config": "The config options defining the job.",},
)
def submit(config: JobConfig, *, _sdk: JobSDK) -> str:
    """Submit a job."""
    return _sdk.submit(config)

import copy
import pathlib
import re
from typing import List, Optional, Tuple, Union

from common import (
    MULTI_LINE_REQUIREMENTS,
    OPENAPI_NO_VALIDATION,
    RequirementsFile,
    SINGLE_LINE_REQUIREMENTS,
    TEST_COMPUTE_CONFIG_DICT,
    TEST_CONTAINERFILE,
    TEST_REQUIREMENTS_FILES,
)
import pytest

from anyscale._private.anyscale_client import (
    FakeAnyscaleClient,
    WORKSPACE_CLUSTER_NAME_PREFIX,
)
from anyscale._private.models.image_uri import ImageURI
from anyscale.client.openapi_client.models import (
    ComputeTemplate,
    ComputeTemplateConfig,
    CreateInternalProductionJob,
    ProductionJobConfig,
)
from anyscale.job._private.job_sdk import JobSDK
from anyscale.job.models import JobConfig


@pytest.fixture()
def sdk_with_fake_client() -> Tuple[JobSDK, FakeAnyscaleClient]:
    fake_client = FakeAnyscaleClient()
    return JobSDK(client=fake_client), fake_client


class TestSubmit:
    def test_basic(self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]):
        sdk, fake_client = sdk_with_fake_client

        config = JobConfig(entrypoint="python hello.py", name="test-job-name",)
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

    def test_default_name(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client

        config = JobConfig(entrypoint="python hello.py",)
        sdk.submit(config)
        assert fake_client.submitted_job.name
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name=fake_client.submitted_job.name,
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

    def test_custom_image_from_containerfile(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_containerfile = pathlib.Path(TEST_CONTAINERFILE).read_text()
        fake_client.set_containerfile_mapping(fake_containerfile, "bld_1234")

        config = JobConfig(
            entrypoint="python hello.py",
            name="test-job-name",
            containerfile=TEST_CONTAINERFILE,
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id="bld_1234",
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

    def test_custom_image_from_image_uri(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.set_image_uri_mapping(
            ImageURI.from_str("docker.io/user/my-custom-image:latest"), "bld_123"
        )

        config = JobConfig(
            entrypoint="python hello.py",
            name="test-job-name",
            image_uri="docker.io/user/my-custom-image:latest",
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id="bld_123",
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

        with pytest.raises(
            ValueError,
            match="The image_uri 'docker.io/user/does-not-exist:latest' does not exist.",
        ):
            sdk.submit(config.options(image_uri="docker.io/user/does-not-exist:latest"))

    def test_custom_compute_config_name(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client

        fake_client.add_compute_config(
            ComputeTemplate(
                id="compute_id123",
                name="my-custom-compute-config",
                config=ComputeTemplateConfig(
                    cloud_id="test-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config = JobConfig(
            entrypoint="python hello.py",
            name="test-job-name",
            compute_config="my-custom-compute-config",
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id="compute_id123",
            ),
        )

        with pytest.raises(
            ValueError, match="The compute config 'does-not-exist' does not exist."
        ):
            sdk.submit(config.options(compute_config="does-not-exist"))

    def test_custom_compute_config_dict(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client

        # Specify a compute config as a dictionary (anonymous).
        config = JobConfig(
            entrypoint="python hello.py",
            name="test-job-name",
            compute_config=TEST_COMPUTE_CONFIG_DICT,
        )
        sdk.submit(config)
        anonymous_compute_config_id = fake_client.submitted_job.config.compute_config_id
        anonymous_compute_config = fake_client.get_compute_config(
            anonymous_compute_config_id
        )
        assert anonymous_compute_config.anonymous
        assert anonymous_compute_config.id == anonymous_compute_config_id
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=anonymous_compute_config_id,
            ),
        )

        # Test an invalid dict.
        with pytest.raises(
            TypeError,
            match=re.escape("__init__() got an unexpected keyword argument 'bad'"),
        ):
            sdk.submit(
                JobConfig(
                    entrypoint="python hello.py",
                    name="test-job-name",
                    compute_config={"bad": "config"},
                )
            )

    def test_max_retries(self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]):
        sdk, fake_client = sdk_with_fake_client

        config = JobConfig(
            entrypoint="python hello.py", name="test-job-name", max_retries=10,
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=10,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )


class TestDeployWorkspaceDefaults:
    def test_name_defaults_to_workspace_name(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client

        # Happy path: workspace cluster name has the expected prefix.
        fake_client.set_inside_workspace(
            True,
            cluster_name=WORKSPACE_CLUSTER_NAME_PREFIX + "super-special-workspace-name",
        )
        sdk.submit(JobConfig(entrypoint="python hello.py"))
        assert fake_client.submitted_job.name == "job-super-special-workspace-name"

        # Defensive path: workspace cluster name doesn't have the expected prefix.
        fake_client.set_inside_workspace(
            True, cluster_name="not-sure-how-this-happened"
        )
        sdk.submit(JobConfig(entrypoint="python hello.py"))
        assert fake_client.submitted_job.name == "job-not-sure-how-this-happened"

    def test_pick_up_cluster_configs(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.set_inside_workspace(True)

        sdk.submit(
            JobConfig(
                entrypoint="python hello.py",
                name="test-job-name",
                working_dir="s3://remote.zip",
            )
        )
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.WORKSPACE_PROJECT_ID,
            workspace_id=fake_client.WORKSPACE_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env={"working_dir": "s3://remote.zip"},
                max_retries=1,
                build_id=fake_client.WORKSPACE_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.WORKSPACE_CLUSTER_COMPUTE_ID,
            ),
        )


class TestOverrideApplicationRuntimeEnvs:
    @pytest.mark.parametrize("excludes_override", [None, ["override"]])
    @pytest.mark.parametrize(
        "working_dir_override", [None, "./some-local-path", "s3://some-remote-path.zip"]
    )
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_override_working_dir_excludes(
        self,
        sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient],
        inside_workspace: bool,
        working_dir_override: Optional[str],
        excludes_override: Optional[List[str]],
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.set_inside_workspace(inside_workspace)

        job = JobConfig(
            name="test-job-name",
            entrypoint="python hello.py",
            working_dir=working_dir_override,
            excludes=excludes_override,
        )

        sdk.submit(job)
        submitted_runtime_env = fake_client.submitted_job.config.runtime_env

        cloud_id = (
            FakeAnyscaleClient.WORKSPACE_CLOUD_ID
            if inside_workspace
            else FakeAnyscaleClient.DEFAULT_CLOUD_ID
        )
        cwd_uri = fake_client.upload_local_dir_to_cloud_storage(".", cloud_id=cloud_id)
        if working_dir_override is None and not inside_workspace:
            assert (
                submitted_runtime_env is None
                or "working_dir" not in submitted_runtime_env
            )
        elif working_dir_override is None and inside_workspace:
            assert submitted_runtime_env["working_dir"] == cwd_uri
        elif working_dir_override is not None and working_dir_override.startswith("s3"):
            assert submitted_runtime_env["working_dir"] == working_dir_override
        else:
            fake_client.upload_local_dir_to_cloud_storage(
                "./some-local-path", cloud_id=cloud_id
            )

        if excludes_override is None:
            assert (
                submitted_runtime_env is None or "excludes" not in submitted_runtime_env
            )
        else:
            assert submitted_runtime_env["excludes"] == ["override"]

    @pytest.mark.parametrize(
        "requirements_override",
        [None, MULTI_LINE_REQUIREMENTS.get_path(), ["override"]],
    )
    @pytest.mark.parametrize("workspace_tracking_enabled", [False, True])
    @pytest.mark.parametrize(
        "enable_image_build_for_tracked_requirements", [False, True]
    )
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_override_requirements(
        self,
        sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient],
        inside_workspace: bool,
        workspace_tracking_enabled: bool,
        enable_image_build_for_tracked_requirements: bool,
        requirements_override: Union[None, str, List[str]],
    ):
        sdk, fake_client = sdk_with_fake_client
        sdk._enable_image_build_for_tracked_requirements = (
            enable_image_build_for_tracked_requirements
        )
        fake_client.set_inside_workspace(
            inside_workspace,
            requirements_path=SINGLE_LINE_REQUIREMENTS.get_path()
            if workspace_tracking_enabled
            else None,
        )

        if inside_workspace and enable_image_build_for_tracked_requirements:
            fake_client.set_image_uri_mapping(
                ImageURI.from_str("docker.io/user/my-default-image:latest"),
                fake_client.WORKSPACE_CLUSTER_ENV_BUILD_ID,
            )
            fake_client.set_containerfile_mapping(
                '# syntax=docker/dockerfile:1\nFROM docker.io/user/my-default-image:latest\nRUN pip install "pip-install-test"',
                "bld_123",
            )

        job = JobConfig(
            name="test-job-name",
            entrypoint="python hello.py",
            requirements=requirements_override,
        )

        sdk.submit(job)
        submitted_runtime_env = fake_client.submitted_job.config.runtime_env

        if isinstance(requirements_override, str):
            # Override with a file.
            pass
        elif isinstance(requirements_override, list):
            # Override with a list.
            pass
        elif (
            inside_workspace
            and workspace_tracking_enabled
            and not enable_image_build_for_tracked_requirements
        ):
            # Workspace default.
            expected_workspace_pip = SINGLE_LINE_REQUIREMENTS.expected_pip_list
            assert submitted_runtime_env["pip"] == expected_workspace_pip
        else:
            # No overrides.
            assert submitted_runtime_env is None or "pip" not in submitted_runtime_env


class TestDeployUploadDirs:
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_upload_basic_working_dir(
        self,
        sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient],
        inside_workspace: bool,
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.set_inside_workspace(inside_workspace)

        config = JobConfig(entrypoint="python test.py", working_dir=".",)
        original_config = copy.deepcopy(config)

        sdk.submit(config)
        # The original config should not be modified.
        assert config == original_config

        # Check that the correct cloud_id was used for the upload.
        expected_cloud_id = (
            FakeAnyscaleClient.WORKSPACE_CLOUD_ID
            if inside_workspace
            else FakeAnyscaleClient.DEFAULT_CLOUD_ID
        )
        assert fake_client.submitted_job.config.runtime_env["working_dir"].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(cloud_id=expected_cloud_id)
        )

    def test_upload_uses_cloud_from_compute_config(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.add_compute_config(
            ComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config",
                config=ComputeTemplateConfig(
                    cloud_id="compute-config-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config = JobConfig(
            entrypoint="python test.py",
            working_dir=".",
            compute_config="fake-compute-config",
        )
        sdk.submit(config)

        # Check that the correct cloud_id was used for the upload.
        expected_cloud_id = "compute-config-cloud-id"
        assert fake_client.submitted_job.config.runtime_env["working_dir"].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(cloud_id=expected_cloud_id)
        )

    def test_upload_with_no_local_dirs(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        """Configs should be left unchanged if there are no local dirs."""
        sdk, fake_client = sdk_with_fake_client

        basic_config = JobConfig(entrypoint="python test.py",)
        sdk.submit(basic_config)
        assert fake_client.submitted_job.config.runtime_env is None

        config_with_requirements = JobConfig(
            entrypoint="python test.py", requirements=["pip-install-test"],
        )
        sdk.submit(config_with_requirements)
        assert fake_client.submitted_job.config.runtime_env == {
            "pip": ["pip-install-test"]
        }

    def test_no_upload_remote_working_dir(
        self, sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient]
    ):
        sdk, fake_client = sdk_with_fake_client
        config = JobConfig(
            entrypoint="python test.py", working_dir="s3://some-remote-uri.zip",
        )

        sdk.submit(config)
        assert (
            fake_client.submitted_job.config.runtime_env["working_dir"]
            == "s3://some-remote-uri.zip"
        )


class TestLoadRequirementsFiles:
    @pytest.mark.parametrize("requirements", [None, *TEST_REQUIREMENTS_FILES])
    def test_override_requirements_file(
        self,
        sdk_with_fake_client: Tuple[JobSDK, FakeAnyscaleClient],
        requirements: Optional[RequirementsFile],
    ):
        sdk, fake_client = sdk_with_fake_client

        job = JobConfig(entrypoint="python hello.py")
        if requirements is not None:
            job = job.options(requirements=requirements.get_path())

        if requirements is not None and requirements.expected_pip_list is None:
            with pytest.raises(FileNotFoundError):
                sdk.submit(job)

            return
        else:
            sdk.submit(job)

        if requirements is None:
            assert fake_client.submitted_job.config.runtime_env is None
        else:
            assert (
                fake_client.submitted_job.config.runtime_env["pip"]
                == requirements.expected_pip_list
            )

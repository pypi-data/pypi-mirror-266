from typing import Any, Dict, Optional
import uuid

from anyscale._private.models.image_uri import ImageURI
from anyscale._private.workload import WorkloadSDK
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import (
    CreateInternalProductionJob,
    InternalProductionJob,
    ProductionJobConfig,
)
from anyscale.job.models import JobConfig
from anyscale.utils.runtime_env import parse_requirements_file


logger = BlockLogger()


class JobSDK(WorkloadSDK):
    def _populate_runtime_env(
        self,
        config: JobConfig,
        *,
        autopopulate_in_workspace: bool = True,
        cloud_id: Optional[str] = None,
        workspace_requirements_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Populates a runtime_env from the config.

        Local directories specified in the 'working_dir' will be uploaded and
        replaced with the resulting remote URIs.

        Requirements files will be loaded and populated into the 'pip' field.

        If autopopulate_from_workspace is passed and this code is running inside a
        workspace, the following defaults will be applied:
            - 'working_dir' will be set to '.'.
            - 'pip' will be set to the workspace-managed requirements file.
        """
        runtime_env: Dict[str, Any] = {}
        [runtime_env] = self.override_and_upload_local_dirs(
            [runtime_env],
            working_dir_override=config.working_dir,
            excludes_override=config.excludes,
            cloud_id=cloud_id,
            autopopulate_in_workspace=autopopulate_in_workspace,
        )
        [runtime_env] = self.override_and_load_requirements_files(
            [runtime_env],
            requirements_override=config.requirements,
            workspace_requirements_path=workspace_requirements_path,
        )
        [runtime_env] = self.update_env_vars(
            [runtime_env], env_vars_updates=config.env_vars,
        )

        return runtime_env or None

    def _get_default_name(self) -> str:
        """Get a default name for the job.

        If running inside a workspace, this is generated from the workspace name,
        else it generates a random name.
        """
        # TODO(edoakes): generate two random words instead of UUID here.
        name = f"job-{self.get_current_workspace_name() or str(uuid.uuid4())}"
        self.logger.info(f"No name was specified, using default: '{name}'.")
        return name

    def submit(self, config: JobConfig) -> str:
        name = config.name or self._get_default_name()

        build_id = None
        if config.containerfile is not None:
            build_id = self.client.get_cluster_env_build_id_from_containerfile(
                cluster_env_name=f"image-for-job-{name}",
                containerfile=self.get_containerfile_contents(config.containerfile),
            )
        elif config.image_uri is not None:
            build_id = self.client.get_cluster_env_build_id_from_image_uri(
                image_uri=ImageURI.from_str(config.image_uri)
            )

        if self.enable_image_build_for_tracked_requirements:
            requirements_path_to_be_populated_in_runtime_env = None
            requirements_path = self.client.get_workspace_requirements_path()
            if requirements_path is not None:
                requirements = parse_requirements_file(requirements_path)
                if requirements:
                    build_id = self.client.build_image_from_requirements(
                        cluster_env_name=f"image-for-job-{name}",
                        base_build_id=self.client.get_default_build_id(),
                        requirements=requirements,
                    )
        else:
            requirements_path_to_be_populated_in_runtime_env = (
                self.client.get_workspace_requirements_path()
            )

        if build_id is None:
            build_id = self.client.get_default_build_id()

        compute_config_id = self.resolve_compute_config_to_id(config.compute_config)

        # If a compute config was specified, we need to make sure to used the correct
        # cloud_id when uploading local directories.
        cloud_id = self.client.get_cloud_id(
            compute_config_id=None
            if config.compute_config is None
            else compute_config_id
        )
        env_vars_from_workspace = self.client.get_workspace_env_vars()
        if env_vars_from_workspace:
            if config.env_vars:
                # the precedence should be cli > workspace
                env_vars_from_workspace.update(config.env_vars)
                config = config.options(env_vars=env_vars_from_workspace)
            else:
                config = config.options(env_vars=env_vars_from_workspace)

        runtime_env = self._populate_runtime_env(
            config,
            cloud_id=cloud_id,
            workspace_requirements_path=requirements_path_to_be_populated_in_runtime_env,
        )

        job: InternalProductionJob = self.client.submit_job(
            CreateInternalProductionJob(
                name=name,
                project_id=self.client.get_project_id(parent_cloud_id=cloud_id),
                workspace_id=self.client.get_current_workspace_id(),
                config=ProductionJobConfig(
                    entrypoint=config.entrypoint,
                    runtime_env=runtime_env,
                    build_id=build_id,
                    compute_config_id=compute_config_id,
                    max_retries=config.max_retries,
                ),
                # TODO(edoakes): support job queue config.
                job_queue_config=None,
            )
        )

        self.logger.info(f"Job '{name}' submitted, ID: '{job.id}'.")
        self.logger.info(
            f"View the job in the UI: {self.client.get_job_ui_url(job.id)}"
        )
        return job.id

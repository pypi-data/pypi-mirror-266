from copy import deepcopy
from typing import Dict, List, Optional, Union

from anyscale._private.sdk.base_sdk import BaseSDK
from anyscale.client.openapi_client.models import (
    ComputeNodeType,
    ComputeTemplateConfig,
    DecoratedComputeTemplate,
    DecoratedComputeTemplateConfig,
    Resources,
    WorkerNodeType,
)
from anyscale.compute_config.models import (
    ComputeConfig,
    HeadNodeConfig,
    MarketType,
    WorkerNodeGroupConfig,
)
from anyscale.sdk.anyscale_client.models import ClusterComputeConfig


# Used to explicitly make the head node unschedulable.
# We can't leave resources empty because the backend will fill in CPU and GPU
# to match the instance type hardware.
UNSCHEDULABLE_RESOURCES = Resources(cpu=0, gpu=0)


class ComputeConfigSDK(BaseSDK):
    def _convert_resource_dict_to_api_model(
        self, resource_dict: Optional[Dict[str, float]]
    ) -> Optional[Resources]:
        if resource_dict is None:
            return None

        resource_dict = deepcopy(resource_dict)
        return Resources(
            cpu=resource_dict.pop("CPU", None),
            gpu=resource_dict.pop("GPU", None),
            memory=resource_dict.pop("memory", None),
            object_store_memory=resource_dict.pop("object_store_memory", None),
            custom_resources=resource_dict or None,
        )

    def _convert_head_node_config_to_api_model(
        self,
        config: Union[None, Dict, HeadNodeConfig],
        *,
        cloud_id: str,
        schedulable_by_default: bool,
    ) -> ComputeNodeType:
        if config is None:
            # If no head node config is provided, use the cloud default.
            default: ClusterComputeConfig = self._client.get_default_compute_config(
                cloud_id=cloud_id
            ).config

            api_model = ComputeNodeType(
                name="head-node",
                instance_type=default.head_node_type.instance_type,
                # Let the backend populate the physical resources
                # (regardless of what the default compute config says).
                resources=None if schedulable_by_default else UNSCHEDULABLE_RESOURCES,
            )
        else:
            # Make mypy happy.
            assert isinstance(config, HeadNodeConfig)

            if config.advanced_instance_config is not None:
                raise NotImplementedError(
                    "'advanced_instance_config' not implemented yet."
                )

            api_model = ComputeNodeType(
                name="head-node",
                instance_type=config.instance_type,
                resources=self._convert_resource_dict_to_api_model(config.resources)
                if config.resources is not None or schedulable_by_default
                else UNSCHEDULABLE_RESOURCES,
            )

        return api_model

    def _convert_worker_node_group_configs_to_api_models(
        self, configs: Optional[List[Union[Dict, WorkerNodeGroupConfig]]]
    ) -> Optional[List[WorkerNodeType]]:
        if configs is None:
            return None

        api_models = []
        for config in configs:
            # Make mypy happy.
            assert isinstance(config, WorkerNodeGroupConfig)
            if config.advanced_instance_config is not None:
                raise NotImplementedError(
                    "'advanced_instance_config' not implemented yet."
                )

            api_models.append(
                WorkerNodeType(
                    name=config.name,
                    instance_type=config.instance_type,
                    resources=self._convert_resource_dict_to_api_model(
                        config.resources
                    ),
                    min_workers=config.min_nodes,
                    max_workers=config.max_nodes,
                    use_spot=config.market_type
                    in {MarketType.SPOT, MarketType.PREFER_SPOT},
                    fallback_to_ondemand=config.market_type == MarketType.PREFER_SPOT,
                )
            )

        return api_models

    def _convert_compute_config_to_api_model(
        self, compute_config: ComputeConfig
    ) -> ComputeTemplateConfig:
        # We should only make the head node schedulable when it's the *only* node in the cluster.
        # `worker_nodes=None` uses the default serverless config, so this only happens if `worker_nodes`
        # is explicitly set to an empty list.
        if compute_config.advanced_instance_config is not None:
            raise NotImplementedError("'advanced_instance_config' not implemented yet.")

        head_node_schedulable_by_default = compute_config.worker_nodes == []
        cloud_id = self.client.get_cloud_id(cloud_name=compute_config.cloud)
        return ComputeTemplateConfig(
            cloud_id=cloud_id,
            allowed_azs=compute_config.zones,
            region="",
            head_node_type=self._convert_head_node_config_to_api_model(
                compute_config.head_node,
                cloud_id=cloud_id,
                schedulable_by_default=head_node_schedulable_by_default,
            ),
            worker_node_types=self._convert_worker_node_group_configs_to_api_models(
                compute_config.worker_nodes
            ),
            auto_select_worker_config=compute_config.worker_nodes is None,
            flags={
                "allow-cross-zone-autoscaling": compute_config.enable_cross_zone_scaling,
            },
        )

    def create_compute_config(
        self, compute_config: ComputeConfig, *, name: Optional[str] = None
    ) -> str:
        """Register the provided compute config and return its internal ID."""
        # TODO(edoakes): implement this once Shomil adds support for it.
        if compute_config.max_resources is not None:
            raise NotImplementedError("'max_resources' is not supported yet.")

        compute_config_api_model = self._convert_compute_config_to_api_model(
            compute_config
        )
        return self.client.create_compute_config(compute_config_api_model, name=name,)

    def _convert_api_model_to_resource_dict(
        self, resources: Optional[Resources]
    ) -> Optional[Dict[str, float]]:
        # Flatten the resource dict returned by the API and strip `None` values.
        if resources is None:
            return None

        return {
            k: v
            for k, v in {
                "CPU": resources.cpu,
                "GPU": resources.gpu,
                "memory": resources.memory,
                "object_store_memory": resources.object_store_memory,
                **(resources.custom_resources or {}),
            }.items()
            if v is not None
        }

    def _convert_api_model_to_head_node_config(
        self, api_model: ComputeNodeType,
    ) -> HeadNodeConfig:
        # TODO(edoakes): support advanced_instance_config.
        return HeadNodeConfig(
            instance_type=api_model.instance_type,
            resources=self._convert_api_model_to_resource_dict(api_model.resources),
        )

    def _convert_api_models_to_worker_node_group_configs(
        self, api_models: List[WorkerNodeType],
    ) -> List[WorkerNodeGroupConfig]:
        # TODO(edoakes): support advanced_instance_config.
        configs = []
        for api_model in api_models:
            if api_model.use_spot and api_model.fallback_to_ondemand:
                market_type = MarketType.PREFER_SPOT
            elif api_model.use_spot:
                market_type = MarketType.SPOT
            else:
                market_type = MarketType.ON_DEMAND

            min_nodes = api_model.min_workers
            if min_nodes is None:
                min_nodes = 0

            max_nodes = api_model.max_workers
            if max_nodes is None:
                # TODO(edoakes): this defaulting to 10 seems like really strange
                # behavior here but I'm copying what the UI does. In Shomil's new
                # API let's not make these optional.
                max_nodes = 10

            configs.append(
                WorkerNodeGroupConfig(
                    name=api_model.name,
                    instance_type=api_model.instance_type,
                    resources=self._convert_api_model_to_resource_dict(
                        api_model.resources
                    ),
                    min_nodes=min_nodes,
                    max_nodes=max_nodes,
                    market_type=market_type,
                )
            )

        return configs

    def _convert_api_model_to_compute_config(
        self, api_model: DecoratedComputeTemplate  # noqa: ARG002
    ) -> ComputeConfig:
        api_model_config: DecoratedComputeTemplateConfig = api_model.config
        # TODO(edoakes): support max_resources.
        # TODO(edoakes): support advanced_resources.

        worker_nodes = None
        if not api_model_config.auto_select_worker_config:
            worker_nodes = self._convert_api_models_to_worker_node_group_configs(
                api_model_config.worker_node_types
            )

        zones = None
        # NOTE(edoakes): the API returns '["any"]' if no AZs are passed in on the creation path.
        if api_model_config.allowed_azs not in [["any"], []]:
            zones = api_model_config.allowed_azs

        enable_cross_zone_scaling = False
        if api_model_config.flags is not None:
            enable_cross_zone_scaling = api_model_config.flags.get(
                "allow-cross-zone-autoscaling", False
            )

        cloud = self.client.get_cloud(cloud_id=api_model_config.cloud_id)
        if cloud is None:
            raise RuntimeError(
                f"Cloud with ID '{api_model_config.cloud_id}' not found. "
                "This should never happen; please reach out to Anyscale support."
            )

        return ComputeConfig(
            cloud=cloud.name,
            zones=zones,
            enable_cross_zone_scaling=enable_cross_zone_scaling,
            head_node=self._convert_api_model_to_head_node_config(
                api_model_config.head_node_type
            ),
            worker_nodes=worker_nodes,  # type: ignore
        )

    def get_compute_config(self, name: str) -> ComputeConfig:
        """Get the compute config for the provided name.

        The name can contain an optional version, e.g., '<name>:<version>'.
        If no version is provided, the latest one will be returned.
        """
        compute_config_id = self.client.get_compute_config_id(compute_config_name=name)
        if compute_config_id is None:
            raise RuntimeError(f"Compute config '{name}' not found.")

        return self._convert_api_model_to_compute_config(
            self.client.get_compute_config(compute_config_id)
        )

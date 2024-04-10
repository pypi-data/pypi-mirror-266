from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from common import OPENAPI_NO_VALIDATION
import pytest

from anyscale._private.anyscale_client import FakeAnyscaleClient
from anyscale.client.openapi_client.models import (
    Cloud,
    ComputeNodeType as InternalApiComputeNodeType,
    ComputeTemplateConfig,
    DecoratedComputeTemplate,
    Resources,
    WorkerNodeType as InternalApiWorkerNodeType,
)
from anyscale.compute_config._private.compute_config_sdk import ComputeConfigSDK
from anyscale.compute_config.models import (
    ComputeConfig,
    HeadNodeConfig,
    MarketType,
    WorkerNodeGroupConfig,
)
from anyscale.sdk.anyscale_client.models import (
    ClusterCompute,
    ClusterComputeConfig,
    ComputeNodeType,
)


@pytest.fixture()
def sdk_with_fake_client() -> Tuple[ComputeConfigSDK, FakeAnyscaleClient]:
    fake_client = FakeAnyscaleClient()
    return ComputeConfigSDK(client=fake_client), fake_client


class TestCreateComputeConfig:
    def test_unsupported_features(
        self, sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client
        with pytest.raises(NotImplementedError):
            sdk.create_compute_config(ComputeConfig(max_resources={"foo": 123}))

        with pytest.raises(NotImplementedError):
            sdk.create_compute_config(
                ComputeConfig(advanced_instance_config={"foo": "bar"})
            )

        with pytest.raises(NotImplementedError):
            sdk.create_compute_config(
                ComputeConfig(
                    head_node=HeadNodeConfig(
                        instance_type="instance",
                        advanced_instance_config={"foo": "bar"},
                    )
                )
            )

        with pytest.raises(NotImplementedError):
            sdk.create_compute_config(
                ComputeConfig(
                    worker_nodes=[
                        WorkerNodeGroupConfig(
                            instance_type="instance",
                            advanced_instance_config={"foo": "bar"},
                        )
                    ]
                )
            )

    def test_name(
        self, sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client
        compute_config_id = sdk.create_compute_config(
            ComputeConfig(), name="test-compute-config-name"
        )
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None
        assert created_compute_config.name == "test-compute-config-name"

    @pytest.mark.parametrize("use_custom_cloud", [False, True])
    @pytest.mark.parametrize("has_no_worker_nodes", [False, True])
    def test_no_head_node_uses_cloud_default(
        self,
        sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        use_custom_cloud: bool,
        has_no_worker_nodes: bool,
    ):
        sdk, fake_client = sdk_with_fake_client

        custom_cloud = "test-non-default-cloud"
        custom_cloud_id = fake_client.get_cloud_id(cloud_name=custom_cloud)
        fake_client.set_default_compute_config(
            ClusterCompute(
                id="test-custom-compute-config-id",
                config=ClusterComputeConfig(
                    cloud_id=custom_cloud_id,
                    head_node_type=ComputeNodeType(
                        name="non-default-head",
                        instance_type="custom-instance-type",
                        resources={"CPU": 24, "GPU": 2, "custom": 1},
                    ),
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            cloud_id=custom_cloud_id,
        )

        config = ComputeConfig()
        if has_no_worker_nodes:
            # Explicitly set no worker nodes.
            # Only in this case should the head node be schedulable.
            config = config.options(worker_nodes=[])
        if use_custom_cloud:
            config = config.options(cloud="test-non-default-cloud")

        compute_config_id = sdk.create_compute_config(config)
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config
        # Serverless worker config should only be set if worker_nodes is `None`.
        assert created.auto_select_worker_config is not has_no_worker_nodes

        if use_custom_cloud:
            assert created.cloud_id == custom_cloud_id
            assert created.head_node_type.instance_type == "custom-instance-type"
        else:
            assert created.cloud_id == fake_client.DEFAULT_CLOUD_ID
            default_compute_config = fake_client.get_default_compute_config(
                cloud_id=fake_client.DEFAULT_CLOUD_ID
            )
            assert (
                created.head_node_type.instance_type
                == default_compute_config.config.head_node_type.instance_type
            )

        if has_no_worker_nodes:
            assert created.head_node_type.resources is None
        else:
            assert created.head_node_type.resources == Resources(cpu=0, gpu=0)

    @pytest.mark.parametrize("use_custom_cloud", [False, True])
    @pytest.mark.parametrize("has_no_worker_nodes", [False, True])
    @pytest.mark.parametrize("has_resources", [False, True])
    def test_custom_head_node(
        self,
        sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        use_custom_cloud: bool,
        has_no_worker_nodes: bool,
        has_resources: bool,
    ):
        sdk, fake_client = sdk_with_fake_client

        custom_cloud = "test-non-default-cloud"
        custom_cloud_id = fake_client.get_cloud_id(cloud_name=custom_cloud)

        head_node_config = HeadNodeConfig(instance_type="head-node-instance-type",)
        if has_resources:
            head_node_config = head_node_config.options(
                resources={"CPU": 1, "head_node": 1}
            )

        config = ComputeConfig(head_node=head_node_config)
        if has_no_worker_nodes:
            # Explicitly set no worker nodes.
            # Only in this case should the head node be schedulable.
            config = config.options(worker_nodes=[])
        if use_custom_cloud:
            config = config.options(cloud="test-non-default-cloud")

        compute_config_id = sdk.create_compute_config(config)
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config
        if use_custom_cloud:
            assert created.cloud_id == custom_cloud_id
        else:
            assert created.cloud_id == fake_client.DEFAULT_CLOUD_ID

        assert created.head_node_type.instance_type == "head-node-instance-type"

        # Serverless worker config should only be set if worker_nodes is `None`.
        assert created.auto_select_worker_config is not has_no_worker_nodes

        # If the user explicitly provides resources, they should always be set.
        if has_resources:
            assert created.head_node_type.resources == Resources(
                cpu=1, custom_resources={"head_node": 1}
            )
        # If there are no worker nodes, resources should be empty (populated by backend).
        elif has_no_worker_nodes:
            assert created.head_node_type.resources is None
        # Otherwise, head node is unschedulable by default.
        else:
            assert created.head_node_type.resources == Resources(cpu=0, gpu=0)

    @pytest.mark.parametrize("use_custom_cloud", [False, True])
    @pytest.mark.parametrize("enable_cross_zone_scaling", [False, True])
    @pytest.mark.parametrize("zones", [None, ["zone1", "zone2"]])
    def test_top_level_flags(
        self,
        sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        use_custom_cloud: bool,
        enable_cross_zone_scaling: bool,
        zones: Optional[List[str]],
    ):
        sdk, fake_client = sdk_with_fake_client

        custom_cloud = "test-non-default-cloud"
        custom_cloud_id = fake_client.get_cloud_id(cloud_name=custom_cloud)

        head_node_config = HeadNodeConfig(instance_type="head-node-instance-type",)
        config = ComputeConfig(head_node=head_node_config, zones=zones)
        if use_custom_cloud:
            config = config.options(cloud="test-non-default-cloud")
        if enable_cross_zone_scaling:
            config = config.options(enable_cross_zone_scaling=True)

        compute_config_id = sdk.create_compute_config(config)
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config
        if use_custom_cloud:
            assert created.cloud_id == custom_cloud_id
        else:
            assert created.cloud_id == fake_client.DEFAULT_CLOUD_ID

        assert created.head_node_type.instance_type == "head-node-instance-type"
        assert (
            created.flags["allow-cross-zone-autoscaling"] == enable_cross_zone_scaling
        )
        assert created.allowed_azs == zones
        assert created.auto_select_worker_config is True

    def test_custom_worker_nodes(
        self, sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client
        config = ComputeConfig(
            worker_nodes=[
                WorkerNodeGroupConfig(instance_type="instance-type-1",),
                WorkerNodeGroupConfig(
                    name="group2",
                    instance_type="instance-type-2",
                    min_nodes=0,
                    max_nodes=100,
                    market_type=MarketType.SPOT,
                ),
                WorkerNodeGroupConfig(
                    name="group3",
                    instance_type="instance-type-2",
                    min_nodes=0,
                    max_nodes=100,
                    resources={"CPU": 1000, "custom": 1},
                    market_type=MarketType.PREFER_SPOT,
                ),
            ],
        )

        compute_config_id = sdk.create_compute_config(config)
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config

        # Serverless worker config should not be set if worker nodes are provided.
        assert created.auto_select_worker_config is False

        assert created.worker_node_types[0].name == "instance-type-1"
        assert created.worker_node_types[0].instance_type == "instance-type-1"
        assert created.worker_node_types[0].resources is None
        assert created.worker_node_types[0].min_workers == 0
        assert created.worker_node_types[0].max_workers == 10
        assert created.worker_node_types[0].use_spot is False
        assert created.worker_node_types[0].fallback_to_ondemand is False

        assert created.worker_node_types[1].name == "group2"
        assert created.worker_node_types[1].instance_type == "instance-type-2"
        assert created.worker_node_types[1].resources is None
        assert created.worker_node_types[1].min_workers == 0
        assert created.worker_node_types[1].max_workers == 100
        assert created.worker_node_types[1].use_spot is True
        assert created.worker_node_types[1].fallback_to_ondemand is False

        assert created.worker_node_types[2].name == "group3"
        assert created.worker_node_types[2].instance_type == "instance-type-2"
        assert created.worker_node_types[2].resources == Resources(
            cpu=1000, custom_resources={"custom": 1}
        )
        assert created.worker_node_types[2].min_workers == 0
        assert created.worker_node_types[2].max_workers == 100
        assert created.worker_node_types[2].use_spot is True
        assert created.worker_node_types[2].fallback_to_ondemand is True


@dataclass
class ResourcesTestCase:
    api_resources: Optional[Resources]
    expected_resources_dict: Optional[Dict[str, float]]


RESOURCES_TEST_CASES = [
    ResourcesTestCase(None, None),
    ResourcesTestCase(Resources(), {}),
    ResourcesTestCase(Resources(cpu=1), {"CPU": 1}),
    ResourcesTestCase(
        Resources(cpu=1, gpu=2, memory=1024, object_store_memory=1024 ** 2),
        {"CPU": 1, "GPU": 2, "memory": 1024, "object_store_memory": 1024 ** 2},
    ),
    # Keys with `None` values should be omitted.
    ResourcesTestCase(Resources(cpu=1, gpu=None), {"CPU": 1}),
    # custom_resources field should be flattened.
    ResourcesTestCase(
        Resources(cpu=1, custom_resources={"custom": 123}), {"CPU": 1, "custom": 123}
    ),
]


class TestGetComputeConfig:
    def test_not_found(
        self, sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client
        with pytest.raises(
            RuntimeError, match="Compute config 'does-not-exist' not found."
        ):
            sdk.get_compute_config("does-not-exist")

    def test_cloud_name(
        self, sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="default-cloud-compute-config-id",
                name="default-cloud-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        default_cloud_config: ComputeConfig = sdk.get_compute_config(
            "default-cloud-compute-config-name"
        )
        assert default_cloud_config.cloud == fake_client.DEFAULT_CLOUD_NAME

        fake_client.add_cloud(
            Cloud(
                id="fake-custom-cloud-id",
                name="fake-custom-cloud",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="custom-cloud-compute-config-id",
                name="custom-cloud-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id="fake-custom-cloud-id",
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        custom_cloud_config: ComputeConfig = sdk.get_compute_config(
            "custom-cloud-compute-config-name"
        )
        assert custom_cloud_config.cloud == "fake-custom-cloud"

    @pytest.mark.parametrize(
        ("api_zones", "expected_zones"),
        [
            (None, None),
            ([], None),
            # API returns ["any"] if no zones are passed in.
            (["any"], None),
            (["az1"], ["az1"]),
            (["az1", "az2"], ["az1", "az2"]),
        ],
    )
    def test_zones(
        self,
        sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        api_zones: Optional[List[str]],
        expected_zones: Optional[List[str]],
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    allowed_azs=api_zones,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get_compute_config("fake-compute-config-name")
        assert config.zones == expected_zones

    @pytest.mark.parametrize(
        ("flags", "expected"),
        [
            (None, False),
            ({}, False),
            ({"something-else": "foobar"}, False),
            ({"allow-cross-zone-autoscaling": False}, False),
            ({"allow-cross-zone-autoscaling": True}, True),
        ],
    )
    def test_enable_cross_zone_scaling(
        self,
        sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        flags: Optional[Dict],
        expected: bool,
    ):
        sdk, fake_client = sdk_with_fake_client
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    flags=flags,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get_compute_config("fake-compute-config-name")
        assert config.enable_cross_zone_scaling == expected

    def test_auto_select_worker_config(
        self, sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="serverless-compute-config-id",
                name="serverless-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    auto_select_worker_config=True,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        serverless_config: ComputeConfig = sdk.get_compute_config(
            "serverless-compute-config-name"
        )
        assert serverless_config.worker_nodes is None

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="non-serverless-compute-config-id",
                name="non-serverless-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    auto_select_worker_config=False,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        non_serverless_config: ComputeConfig = sdk.get_compute_config(
            "non-serverless-compute-config-name"
        )
        assert non_serverless_config.worker_nodes == []

    @pytest.mark.parametrize("test_case", RESOURCES_TEST_CASES)
    def test_convert_head_node(
        self,
        sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        test_case: ResourcesTestCase,
    ):
        sdk, fake_client = sdk_with_fake_client

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name",
                        instance_type="head-node-instance-type",
                        resources=test_case.api_resources,
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get_compute_config("fake-compute-config-name")
        assert config.head_node == HeadNodeConfig(
            instance_type="head-node-instance-type",
            resources=test_case.expected_resources_dict,
        )

    @pytest.mark.parametrize("test_case", RESOURCES_TEST_CASES)
    def test_convert_worker_nodes(
        self,
        sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        test_case: ResourcesTestCase,
    ):
        sdk, fake_client = sdk_with_fake_client

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[
                        InternalApiWorkerNodeType(
                            name="basic",
                            instance_type="instance-type-1",
                            min_workers=0,
                            max_workers=10,
                        ),
                        InternalApiWorkerNodeType(
                            name="custom-resources",
                            instance_type="instance-type-2",
                            resources=test_case.api_resources,
                            min_workers=1,
                            max_workers=1,
                        ),
                        InternalApiWorkerNodeType(
                            name="min-workers-none",
                            instance_type="instance-type-3",
                            min_workers=None,
                            max_workers=1,
                        ),
                        InternalApiWorkerNodeType(
                            name="max-workers-none",
                            instance_type="instance-type-4",
                            min_workers=0,
                            max_workers=None,
                        ),
                    ],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get_compute_config("fake-compute-config-name")
        assert config.worker_nodes == [
            WorkerNodeGroupConfig(
                name="basic",
                instance_type="instance-type-1",
                min_nodes=0,
                max_nodes=10,
            ),
            WorkerNodeGroupConfig(
                name="custom-resources",
                instance_type="instance-type-2",
                resources=test_case.expected_resources_dict,
                min_nodes=1,
                max_nodes=1,
            ),
            WorkerNodeGroupConfig(
                name="min-workers-none",
                instance_type="instance-type-3",
                min_nodes=0,
                max_nodes=1,
            ),
            WorkerNodeGroupConfig(
                name="max-workers-none",
                instance_type="instance-type-4",
                min_nodes=0,
                max_nodes=10,
            ),
        ]

    def test_worker_node_market_type(
        self, sdk_with_fake_client: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[
                        InternalApiWorkerNodeType(
                            name="on-demand-worker-node-group",
                            instance_type="on-demand-worker-node-group",
                            min_workers=1,
                            max_workers=1,
                            use_spot=False,
                            fallback_to_ondemand=False,
                        ),
                        InternalApiWorkerNodeType(
                            name="spot-worker-node-group",
                            instance_type="spot-worker-node-group",
                            min_workers=1,
                            max_workers=1,
                            use_spot=True,
                            fallback_to_ondemand=False,
                        ),
                        InternalApiWorkerNodeType(
                            name="prefer-spot-worker-node-group",
                            instance_type="prefer-spot-worker-node-group",
                            min_workers=1,
                            max_workers=1,
                            use_spot=True,
                            fallback_to_ondemand=True,
                        ),
                    ],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get_compute_config("fake-compute-config-name")
        assert config.worker_nodes == [
            WorkerNodeGroupConfig(
                name="on-demand-worker-node-group",
                instance_type="on-demand-worker-node-group",
                min_nodes=1,
                max_nodes=1,
                market_type=MarketType.ON_DEMAND,
            ),
            WorkerNodeGroupConfig(
                name="spot-worker-node-group",
                instance_type="spot-worker-node-group",
                min_nodes=1,
                max_nodes=1,
                market_type=MarketType.SPOT,
            ),
            WorkerNodeGroupConfig(
                name="prefer-spot-worker-node-group",
                instance_type="prefer-spot-worker-node-group",
                min_nodes=1,
                max_nodes=1,
                market_type=MarketType.PREFER_SPOT,
            ),
        ]

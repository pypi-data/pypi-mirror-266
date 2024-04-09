"""
Type annotations for mgn service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_mgn.client import mgnClient

    session = Session()
    client: mgnClient = session.client("mgn")
    ```
"""

import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    ActionCategoryType,
    BootModeType,
    LaunchDispositionType,
    ReplicationConfigurationDataPlaneRoutingType,
    ReplicationConfigurationDefaultLargeStagingDiskTypeType,
    ReplicationConfigurationEbsEncryptionType,
    ReplicationTypeType,
    TargetInstanceTypeRightSizingMethodType,
)
from .paginator import (
    DescribeJobLogItemsPaginator,
    DescribeJobsPaginator,
    DescribeLaunchConfigurationTemplatesPaginator,
    DescribeReplicationConfigurationTemplatesPaginator,
    DescribeSourceServersPaginator,
    DescribeVcenterClientsPaginator,
    ListApplicationsPaginator,
    ListConnectorsPaginator,
    ListExportErrorsPaginator,
    ListExportsPaginator,
    ListImportErrorsPaginator,
    ListImportsPaginator,
    ListManagedAccountsPaginator,
    ListSourceServerActionsPaginator,
    ListTemplateActionsPaginator,
    ListWavesPaginator,
)
from .type_defs import (
    ApplicationResponseTypeDef,
    ChangeServerLifeCycleStateSourceServerLifecycleTypeDef,
    ConnectorResponseTypeDef,
    ConnectorSsmCommandConfigTypeDef,
    DescribeJobLogItemsResponseTypeDef,
    DescribeJobsRequestFiltersTypeDef,
    DescribeJobsResponseTypeDef,
    DescribeLaunchConfigurationTemplatesResponseTypeDef,
    DescribeReplicationConfigurationTemplatesResponseTypeDef,
    DescribeSourceServersRequestFiltersTypeDef,
    DescribeSourceServersResponseTypeDef,
    DescribeVcenterClientsResponseTypeDef,
    EmptyResponseMetadataTypeDef,
    LaunchConfigurationTemplateResponseTypeDef,
    LaunchConfigurationTypeDef,
    LaunchTemplateDiskConfTypeDef,
    LicensingTypeDef,
    ListApplicationsRequestFiltersTypeDef,
    ListApplicationsResponseTypeDef,
    ListConnectorsRequestFiltersTypeDef,
    ListConnectorsResponseTypeDef,
    ListExportErrorsResponseTypeDef,
    ListExportsRequestFiltersTypeDef,
    ListExportsResponseTypeDef,
    ListImportErrorsResponseTypeDef,
    ListImportsRequestFiltersTypeDef,
    ListImportsResponseTypeDef,
    ListManagedAccountsResponseTypeDef,
    ListSourceServerActionsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListTemplateActionsResponseTypeDef,
    ListWavesRequestFiltersTypeDef,
    ListWavesResponseTypeDef,
    PostLaunchActionsTypeDef,
    ReplicationConfigurationReplicatedDiskTypeDef,
    ReplicationConfigurationTemplateResponseTypeDef,
    ReplicationConfigurationTypeDef,
    S3BucketSourceTypeDef,
    SourceServerActionDocumentResponseTypeDef,
    SourceServerActionsRequestFiltersTypeDef,
    SourceServerConnectorActionTypeDef,
    SourceServerResponseTypeDef,
    SsmExternalParameterTypeDef,
    SsmParameterStoreParameterTypeDef,
    StartCutoverResponseTypeDef,
    StartExportResponseTypeDef,
    StartImportResponseTypeDef,
    StartTestResponseTypeDef,
    TemplateActionDocumentResponseTypeDef,
    TemplateActionsRequestFiltersTypeDef,
    TerminateTargetInstancesResponseTypeDef,
    WaveResponseTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("mgnClient",)

class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str

class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    UninitializedAccountException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]

class mgnClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        mgnClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#exceptions)
        """

    def archive_application(
        self, *, applicationID: str, accountID: str = ...
    ) -> ApplicationResponseTypeDef:
        """
        Archive application.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.archive_application)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#archive_application)
        """

    def archive_wave(self, *, waveID: str, accountID: str = ...) -> WaveResponseTypeDef:
        """
        Archive wave.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.archive_wave)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#archive_wave)
        """

    def associate_applications(
        self, *, applicationIDs: Sequence[str], waveID: str, accountID: str = ...
    ) -> Dict[str, Any]:
        """
        Associate applications to wave.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.associate_applications)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#associate_applications)
        """

    def associate_source_servers(
        self, *, applicationID: str, sourceServerIDs: Sequence[str], accountID: str = ...
    ) -> Dict[str, Any]:
        """
        Associate source servers to application.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.associate_source_servers)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#associate_source_servers)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#can_paginate)
        """

    def change_server_life_cycle_state(
        self,
        *,
        lifeCycle: ChangeServerLifeCycleStateSourceServerLifecycleTypeDef,
        sourceServerID: str,
        accountID: str = ...,
    ) -> SourceServerResponseTypeDef:
        """
        Allows the user to set the SourceServer.LifeCycle.state property for specific
        Source Server IDs to one of the following: READY_FOR_TEST or
        READY_FOR_CUTOVER.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.change_server_life_cycle_state)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#change_server_life_cycle_state)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#close)
        """

    def create_application(
        self,
        *,
        name: str,
        accountID: str = ...,
        description: str = ...,
        tags: Mapping[str, str] = ...,
    ) -> ApplicationResponseTypeDef:
        """
        Create application.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.create_application)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#create_application)
        """

    def create_connector(
        self,
        *,
        name: str,
        ssmInstanceID: str,
        ssmCommandConfig: ConnectorSsmCommandConfigTypeDef = ...,
        tags: Mapping[str, str] = ...,
    ) -> ConnectorResponseTypeDef:
        """
        Create Connector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.create_connector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#create_connector)
        """

    def create_launch_configuration_template(
        self,
        *,
        associatePublicIpAddress: bool = ...,
        bootMode: BootModeType = ...,
        copyPrivateIp: bool = ...,
        copyTags: bool = ...,
        enableMapAutoTagging: bool = ...,
        largeVolumeConf: LaunchTemplateDiskConfTypeDef = ...,
        launchDisposition: LaunchDispositionType = ...,
        licensing: LicensingTypeDef = ...,
        mapAutoTaggingMpeID: str = ...,
        postLaunchActions: PostLaunchActionsTypeDef = ...,
        smallVolumeConf: LaunchTemplateDiskConfTypeDef = ...,
        smallVolumeMaxSize: int = ...,
        tags: Mapping[str, str] = ...,
        targetInstanceTypeRightSizingMethod: TargetInstanceTypeRightSizingMethodType = ...,
    ) -> LaunchConfigurationTemplateResponseTypeDef:
        """
        Creates a new Launch Configuration Template.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.create_launch_configuration_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#create_launch_configuration_template)
        """

    def create_replication_configuration_template(
        self,
        *,
        associateDefaultSecurityGroup: bool,
        bandwidthThrottling: int,
        createPublicIP: bool,
        dataPlaneRouting: ReplicationConfigurationDataPlaneRoutingType,
        defaultLargeStagingDiskType: ReplicationConfigurationDefaultLargeStagingDiskTypeType,
        ebsEncryption: ReplicationConfigurationEbsEncryptionType,
        replicationServerInstanceType: str,
        replicationServersSecurityGroupsIDs: Sequence[str],
        stagingAreaSubnetId: str,
        stagingAreaTags: Mapping[str, str],
        useDedicatedReplicationServer: bool,
        ebsEncryptionKeyArn: str = ...,
        tags: Mapping[str, str] = ...,
        useFipsEndpoint: bool = ...,
    ) -> ReplicationConfigurationTemplateResponseTypeDef:
        """
        Creates a new ReplicationConfigurationTemplate.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.create_replication_configuration_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#create_replication_configuration_template)
        """

    def create_wave(
        self,
        *,
        name: str,
        accountID: str = ...,
        description: str = ...,
        tags: Mapping[str, str] = ...,
    ) -> WaveResponseTypeDef:
        """
        Create wave.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.create_wave)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#create_wave)
        """

    def delete_application(self, *, applicationID: str, accountID: str = ...) -> Dict[str, Any]:
        """
        Delete application.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_application)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_application)
        """

    def delete_connector(self, *, connectorID: str) -> EmptyResponseMetadataTypeDef:
        """
        Delete Connector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_connector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_connector)
        """

    def delete_job(self, *, jobID: str, accountID: str = ...) -> Dict[str, Any]:
        """
        Deletes a single Job by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_job)
        """

    def delete_launch_configuration_template(
        self, *, launchConfigurationTemplateID: str
    ) -> Dict[str, Any]:
        """
        Deletes a single Launch Configuration Template by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_launch_configuration_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_launch_configuration_template)
        """

    def delete_replication_configuration_template(
        self, *, replicationConfigurationTemplateID: str
    ) -> Dict[str, Any]:
        """
        Deletes a single Replication Configuration Template by ID See also: [AWS API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/mgn-2020-02-26/DeleteReplicationConfigurationTemplate).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_replication_configuration_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_replication_configuration_template)
        """

    def delete_source_server(self, *, sourceServerID: str, accountID: str = ...) -> Dict[str, Any]:
        """
        Deletes a single source server by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_source_server)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_source_server)
        """

    def delete_vcenter_client(self, *, vcenterClientID: str) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a given vCenter client by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_vcenter_client)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_vcenter_client)
        """

    def delete_wave(self, *, waveID: str, accountID: str = ...) -> Dict[str, Any]:
        """
        Delete wave.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.delete_wave)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#delete_wave)
        """

    def describe_job_log_items(
        self, *, jobID: str, accountID: str = ..., maxResults: int = ..., nextToken: str = ...
    ) -> DescribeJobLogItemsResponseTypeDef:
        """
        Retrieves detailed job log items with paging.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.describe_job_log_items)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#describe_job_log_items)
        """

    def describe_jobs(
        self,
        *,
        accountID: str = ...,
        filters: DescribeJobsRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> DescribeJobsResponseTypeDef:
        """
        Returns a list of Jobs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.describe_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#describe_jobs)
        """

    def describe_launch_configuration_templates(
        self,
        *,
        launchConfigurationTemplateIDs: Sequence[str] = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> DescribeLaunchConfigurationTemplatesResponseTypeDef:
        """
        Lists all Launch Configuration Templates, filtered by Launch Configuration
        Template IDs See also: [AWS API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/mgn-2020-02-26/DescribeLaunchConfigurationTemplates).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.describe_launch_configuration_templates)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#describe_launch_configuration_templates)
        """

    def describe_replication_configuration_templates(
        self,
        *,
        maxResults: int = ...,
        nextToken: str = ...,
        replicationConfigurationTemplateIDs: Sequence[str] = ...,
    ) -> DescribeReplicationConfigurationTemplatesResponseTypeDef:
        """
        Lists all ReplicationConfigurationTemplates, filtered by Source Server IDs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.describe_replication_configuration_templates)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#describe_replication_configuration_templates)
        """

    def describe_source_servers(
        self,
        *,
        accountID: str = ...,
        filters: DescribeSourceServersRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> DescribeSourceServersResponseTypeDef:
        """
        Retrieves all SourceServers or multiple SourceServers by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.describe_source_servers)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#describe_source_servers)
        """

    def describe_vcenter_clients(
        self, *, maxResults: int = ..., nextToken: str = ...
    ) -> DescribeVcenterClientsResponseTypeDef:
        """
        Returns a list of the installed vCenter clients.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.describe_vcenter_clients)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#describe_vcenter_clients)
        """

    def disassociate_applications(
        self, *, applicationIDs: Sequence[str], waveID: str, accountID: str = ...
    ) -> Dict[str, Any]:
        """
        Disassociate applications from wave.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.disassociate_applications)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#disassociate_applications)
        """

    def disassociate_source_servers(
        self, *, applicationID: str, sourceServerIDs: Sequence[str], accountID: str = ...
    ) -> Dict[str, Any]:
        """
        Disassociate source servers from application.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.disassociate_source_servers)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#disassociate_source_servers)
        """

    def disconnect_from_service(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Disconnects specific Source Servers from Application Migration Service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.disconnect_from_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#disconnect_from_service)
        """

    def finalize_cutover(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Finalizes the cutover immediately for specific Source Servers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.finalize_cutover)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#finalize_cutover)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#generate_presigned_url)
        """

    def get_launch_configuration(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> LaunchConfigurationTypeDef:
        """
        Lists all LaunchConfigurations available, filtered by Source Server IDs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_launch_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_launch_configuration)
        """

    def get_replication_configuration(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> ReplicationConfigurationTypeDef:
        """
        Lists all ReplicationConfigurations, filtered by Source Server ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_replication_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_replication_configuration)
        """

    def initialize_service(self) -> Dict[str, Any]:
        """
        Initialize Application Migration Service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.initialize_service)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#initialize_service)
        """

    def list_applications(
        self,
        *,
        accountID: str = ...,
        filters: ListApplicationsRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListApplicationsResponseTypeDef:
        """
        Retrieves all applications or multiple applications by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_applications)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_applications)
        """

    def list_connectors(
        self,
        *,
        filters: ListConnectorsRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListConnectorsResponseTypeDef:
        """
        List Connectors.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_connectors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_connectors)
        """

    def list_export_errors(
        self, *, exportID: str, maxResults: int = ..., nextToken: str = ...
    ) -> ListExportErrorsResponseTypeDef:
        """
        List export errors.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_export_errors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_export_errors)
        """

    def list_exports(
        self,
        *,
        filters: ListExportsRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListExportsResponseTypeDef:
        """
        List exports.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_exports)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_exports)
        """

    def list_import_errors(
        self, *, importID: str, maxResults: int = ..., nextToken: str = ...
    ) -> ListImportErrorsResponseTypeDef:
        """
        List import errors.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_import_errors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_import_errors)
        """

    def list_imports(
        self,
        *,
        filters: ListImportsRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListImportsResponseTypeDef:
        """
        List imports.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_imports)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_imports)
        """

    def list_managed_accounts(
        self, *, maxResults: int = ..., nextToken: str = ...
    ) -> ListManagedAccountsResponseTypeDef:
        """
        List Managed Accounts.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_managed_accounts)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_managed_accounts)
        """

    def list_source_server_actions(
        self,
        *,
        sourceServerID: str,
        accountID: str = ...,
        filters: SourceServerActionsRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListSourceServerActionsResponseTypeDef:
        """
        List source server post migration custom actions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_source_server_actions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_source_server_actions)
        """

    def list_tags_for_resource(self, *, resourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        List all tags for your Application Migration Service resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_tags_for_resource)
        """

    def list_template_actions(
        self,
        *,
        launchConfigurationTemplateID: str,
        filters: TemplateActionsRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListTemplateActionsResponseTypeDef:
        """
        List template post migration custom actions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_template_actions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_template_actions)
        """

    def list_waves(
        self,
        *,
        accountID: str = ...,
        filters: ListWavesRequestFiltersTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListWavesResponseTypeDef:
        """
        Retrieves all waves or multiple waves by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.list_waves)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#list_waves)
        """

    def mark_as_archived(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Archives specific Source Servers by setting the SourceServer.isArchived
        property to true for specified SourceServers by
        ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.mark_as_archived)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#mark_as_archived)
        """

    def pause_replication(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Pause Replication.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.pause_replication)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#pause_replication)
        """

    def put_source_server_action(
        self,
        *,
        actionID: str,
        actionName: str,
        documentIdentifier: str,
        order: int,
        sourceServerID: str,
        accountID: str = ...,
        active: bool = ...,
        category: ActionCategoryType = ...,
        description: str = ...,
        documentVersion: str = ...,
        externalParameters: Mapping[str, SsmExternalParameterTypeDef] = ...,
        mustSucceedForCutover: bool = ...,
        parameters: Mapping[str, Sequence[SsmParameterStoreParameterTypeDef]] = ...,
        timeoutSeconds: int = ...,
    ) -> SourceServerActionDocumentResponseTypeDef:
        """
        Put source server post migration custom action.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.put_source_server_action)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#put_source_server_action)
        """

    def put_template_action(
        self,
        *,
        actionID: str,
        actionName: str,
        documentIdentifier: str,
        launchConfigurationTemplateID: str,
        order: int,
        active: bool = ...,
        category: ActionCategoryType = ...,
        description: str = ...,
        documentVersion: str = ...,
        externalParameters: Mapping[str, SsmExternalParameterTypeDef] = ...,
        mustSucceedForCutover: bool = ...,
        operatingSystem: str = ...,
        parameters: Mapping[str, Sequence[SsmParameterStoreParameterTypeDef]] = ...,
        timeoutSeconds: int = ...,
    ) -> TemplateActionDocumentResponseTypeDef:
        """
        Put template post migration custom action.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.put_template_action)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#put_template_action)
        """

    def remove_source_server_action(
        self, *, actionID: str, sourceServerID: str, accountID: str = ...
    ) -> Dict[str, Any]:
        """
        Remove source server post migration custom action.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.remove_source_server_action)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#remove_source_server_action)
        """

    def remove_template_action(
        self, *, actionID: str, launchConfigurationTemplateID: str
    ) -> Dict[str, Any]:
        """
        Remove template post migration custom action.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.remove_template_action)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#remove_template_action)
        """

    def resume_replication(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Resume Replication.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.resume_replication)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#resume_replication)
        """

    def retry_data_replication(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Causes the data replication initiation sequence to begin immediately upon next
        Handshake for specified SourceServer IDs, regardless of when the previous
        initiation
        started.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.retry_data_replication)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#retry_data_replication)
        """

    def start_cutover(
        self, *, sourceServerIDs: Sequence[str], accountID: str = ..., tags: Mapping[str, str] = ...
    ) -> StartCutoverResponseTypeDef:
        """
        Launches a Cutover Instance for specific Source Servers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.start_cutover)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#start_cutover)
        """

    def start_export(
        self, *, s3Bucket: str, s3Key: str, s3BucketOwner: str = ...
    ) -> StartExportResponseTypeDef:
        """
        Start export.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.start_export)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#start_export)
        """

    def start_import(
        self, *, s3BucketSource: S3BucketSourceTypeDef, clientToken: str = ...
    ) -> StartImportResponseTypeDef:
        """
        Start import.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.start_import)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#start_import)
        """

    def start_replication(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Starts replication for SNAPSHOT_SHIPPING agents.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.start_replication)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#start_replication)
        """

    def start_test(
        self, *, sourceServerIDs: Sequence[str], accountID: str = ..., tags: Mapping[str, str] = ...
    ) -> StartTestResponseTypeDef:
        """
        Launches a Test Instance for specific Source Servers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.start_test)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#start_test)
        """

    def stop_replication(
        self, *, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Stop Replication.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.stop_replication)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#stop_replication)
        """

    def tag_resource(
        self, *, resourceArn: str, tags: Mapping[str, str]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Adds or overwrites only the specified tags for the specified Application
        Migration Service resource or
        resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#tag_resource)
        """

    def terminate_target_instances(
        self, *, sourceServerIDs: Sequence[str], accountID: str = ..., tags: Mapping[str, str] = ...
    ) -> TerminateTargetInstancesResponseTypeDef:
        """
        Starts a job that terminates specific launched EC2 Test and Cutover instances.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.terminate_target_instances)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#terminate_target_instances)
        """

    def unarchive_application(
        self, *, applicationID: str, accountID: str = ...
    ) -> ApplicationResponseTypeDef:
        """
        Unarchive application.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.unarchive_application)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#unarchive_application)
        """

    def unarchive_wave(self, *, waveID: str, accountID: str = ...) -> WaveResponseTypeDef:
        """
        Unarchive wave.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.unarchive_wave)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#unarchive_wave)
        """

    def untag_resource(
        self, *, resourceArn: str, tagKeys: Sequence[str]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified set of tags from the specified set of Application
        Migration Service
        resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#untag_resource)
        """

    def update_application(
        self, *, applicationID: str, accountID: str = ..., description: str = ..., name: str = ...
    ) -> ApplicationResponseTypeDef:
        """
        Update application.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_application)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_application)
        """

    def update_connector(
        self,
        *,
        connectorID: str,
        name: str = ...,
        ssmCommandConfig: ConnectorSsmCommandConfigTypeDef = ...,
    ) -> ConnectorResponseTypeDef:
        """
        Update Connector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_connector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_connector)
        """

    def update_launch_configuration(
        self,
        *,
        sourceServerID: str,
        accountID: str = ...,
        bootMode: BootModeType = ...,
        copyPrivateIp: bool = ...,
        copyTags: bool = ...,
        enableMapAutoTagging: bool = ...,
        launchDisposition: LaunchDispositionType = ...,
        licensing: LicensingTypeDef = ...,
        mapAutoTaggingMpeID: str = ...,
        name: str = ...,
        postLaunchActions: PostLaunchActionsTypeDef = ...,
        targetInstanceTypeRightSizingMethod: TargetInstanceTypeRightSizingMethodType = ...,
    ) -> LaunchConfigurationTypeDef:
        """
        Updates multiple LaunchConfigurations by Source Server ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_launch_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_launch_configuration)
        """

    def update_launch_configuration_template(
        self,
        *,
        launchConfigurationTemplateID: str,
        associatePublicIpAddress: bool = ...,
        bootMode: BootModeType = ...,
        copyPrivateIp: bool = ...,
        copyTags: bool = ...,
        enableMapAutoTagging: bool = ...,
        largeVolumeConf: LaunchTemplateDiskConfTypeDef = ...,
        launchDisposition: LaunchDispositionType = ...,
        licensing: LicensingTypeDef = ...,
        mapAutoTaggingMpeID: str = ...,
        postLaunchActions: PostLaunchActionsTypeDef = ...,
        smallVolumeConf: LaunchTemplateDiskConfTypeDef = ...,
        smallVolumeMaxSize: int = ...,
        targetInstanceTypeRightSizingMethod: TargetInstanceTypeRightSizingMethodType = ...,
    ) -> LaunchConfigurationTemplateResponseTypeDef:
        """
        Updates an existing Launch Configuration Template by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_launch_configuration_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_launch_configuration_template)
        """

    def update_replication_configuration(
        self,
        *,
        sourceServerID: str,
        accountID: str = ...,
        associateDefaultSecurityGroup: bool = ...,
        bandwidthThrottling: int = ...,
        createPublicIP: bool = ...,
        dataPlaneRouting: ReplicationConfigurationDataPlaneRoutingType = ...,
        defaultLargeStagingDiskType: ReplicationConfigurationDefaultLargeStagingDiskTypeType = ...,
        ebsEncryption: ReplicationConfigurationEbsEncryptionType = ...,
        ebsEncryptionKeyArn: str = ...,
        name: str = ...,
        replicatedDisks: Sequence[ReplicationConfigurationReplicatedDiskTypeDef] = ...,
        replicationServerInstanceType: str = ...,
        replicationServersSecurityGroupsIDs: Sequence[str] = ...,
        stagingAreaSubnetId: str = ...,
        stagingAreaTags: Mapping[str, str] = ...,
        useDedicatedReplicationServer: bool = ...,
        useFipsEndpoint: bool = ...,
    ) -> ReplicationConfigurationTypeDef:
        """
        Allows you to update multiple ReplicationConfigurations by Source Server ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_replication_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_replication_configuration)
        """

    def update_replication_configuration_template(
        self,
        *,
        replicationConfigurationTemplateID: str,
        arn: str = ...,
        associateDefaultSecurityGroup: bool = ...,
        bandwidthThrottling: int = ...,
        createPublicIP: bool = ...,
        dataPlaneRouting: ReplicationConfigurationDataPlaneRoutingType = ...,
        defaultLargeStagingDiskType: ReplicationConfigurationDefaultLargeStagingDiskTypeType = ...,
        ebsEncryption: ReplicationConfigurationEbsEncryptionType = ...,
        ebsEncryptionKeyArn: str = ...,
        replicationServerInstanceType: str = ...,
        replicationServersSecurityGroupsIDs: Sequence[str] = ...,
        stagingAreaSubnetId: str = ...,
        stagingAreaTags: Mapping[str, str] = ...,
        useDedicatedReplicationServer: bool = ...,
        useFipsEndpoint: bool = ...,
    ) -> ReplicationConfigurationTemplateResponseTypeDef:
        """
        Updates multiple ReplicationConfigurationTemplates by ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_replication_configuration_template)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_replication_configuration_template)
        """

    def update_source_server(
        self,
        *,
        sourceServerID: str,
        accountID: str = ...,
        connectorAction: SourceServerConnectorActionTypeDef = ...,
    ) -> SourceServerResponseTypeDef:
        """
        Update Source Server.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_source_server)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_source_server)
        """

    def update_source_server_replication_type(
        self, *, replicationType: ReplicationTypeType, sourceServerID: str, accountID: str = ...
    ) -> SourceServerResponseTypeDef:
        """
        Allows you to change between the AGENT_BASED replication type and the
        SNAPSHOT_SHIPPING replication
        type.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_source_server_replication_type)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_source_server_replication_type)
        """

    def update_wave(
        self, *, waveID: str, accountID: str = ..., description: str = ..., name: str = ...
    ) -> WaveResponseTypeDef:
        """
        Update wave.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.update_wave)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#update_wave)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_job_log_items"]
    ) -> DescribeJobLogItemsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["describe_jobs"]) -> DescribeJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_launch_configuration_templates"]
    ) -> DescribeLaunchConfigurationTemplatesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_replication_configuration_templates"]
    ) -> DescribeReplicationConfigurationTemplatesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_source_servers"]
    ) -> DescribeSourceServersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_vcenter_clients"]
    ) -> DescribeVcenterClientsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_applications"]
    ) -> ListApplicationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_connectors"]) -> ListConnectorsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_export_errors"]
    ) -> ListExportErrorsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_exports"]) -> ListExportsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_import_errors"]
    ) -> ListImportErrorsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_imports"]) -> ListImportsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_managed_accounts"]
    ) -> ListManagedAccountsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_source_server_actions"]
    ) -> ListSourceServerActionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_template_actions"]
    ) -> ListTemplateActionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_waves"]) -> ListWavesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mgn.html#mgn.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/client/#get_paginator)
        """

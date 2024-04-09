"""
Type annotations for mgn service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mgn/type_defs/)

Usage::

    ```python
    from mypy_boto3_mgn.type_defs import ApplicationAggregatedStatusTypeDef

    data: ApplicationAggregatedStatusTypeDef = ...
    ```
"""

import sys
from typing import Dict, List, Mapping, Sequence

from .literals import (
    ActionCategoryType,
    ApplicationHealthStatusType,
    ApplicationProgressStatusType,
    BootModeType,
    ChangeServerLifeCycleStateSourceServerLifecycleStateType,
    DataReplicationErrorStringType,
    DataReplicationInitiationStepNameType,
    DataReplicationInitiationStepStatusType,
    DataReplicationStateType,
    ExportStatusType,
    FirstBootType,
    ImportErrorTypeType,
    ImportStatusType,
    InitiatedByType,
    JobLogEventType,
    JobStatusType,
    JobTypeType,
    LaunchDispositionType,
    LaunchStatusType,
    LifeCycleStateType,
    PostLaunchActionExecutionStatusType,
    PostLaunchActionsDeploymentTypeType,
    ReplicationConfigurationDataPlaneRoutingType,
    ReplicationConfigurationDefaultLargeStagingDiskTypeType,
    ReplicationConfigurationEbsEncryptionType,
    ReplicationConfigurationReplicatedDiskStagingDiskTypeType,
    ReplicationTypeType,
    SsmDocumentTypeType,
    TargetInstanceTypeRightSizingMethodType,
    VolumeTypeType,
    WaveHealthStatusType,
    WaveProgressStatusType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "ApplicationAggregatedStatusTypeDef",
    "ResponseMetadataTypeDef",
    "ArchiveApplicationRequestRequestTypeDef",
    "ArchiveWaveRequestRequestTypeDef",
    "AssociateApplicationsRequestRequestTypeDef",
    "AssociateSourceServersRequestRequestTypeDef",
    "CPUTypeDef",
    "ChangeServerLifeCycleStateSourceServerLifecycleTypeDef",
    "ConnectorSsmCommandConfigTypeDef",
    "CreateApplicationRequestRequestTypeDef",
    "LaunchTemplateDiskConfTypeDef",
    "LicensingTypeDef",
    "CreateReplicationConfigurationTemplateRequestRequestTypeDef",
    "CreateWaveRequestRequestTypeDef",
    "DataReplicationErrorTypeDef",
    "DataReplicationInfoReplicatedDiskTypeDef",
    "DataReplicationInitiationStepTypeDef",
    "DeleteApplicationRequestRequestTypeDef",
    "DeleteConnectorRequestRequestTypeDef",
    "DeleteJobRequestRequestTypeDef",
    "DeleteLaunchConfigurationTemplateRequestRequestTypeDef",
    "DeleteReplicationConfigurationTemplateRequestRequestTypeDef",
    "DeleteSourceServerRequestRequestTypeDef",
    "DeleteVcenterClientRequestRequestTypeDef",
    "DeleteWaveRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeJobLogItemsRequestRequestTypeDef",
    "DescribeJobsRequestFiltersTypeDef",
    "DescribeLaunchConfigurationTemplatesRequestRequestTypeDef",
    "DescribeReplicationConfigurationTemplatesRequestRequestTypeDef",
    "ReplicationConfigurationTemplateTypeDef",
    "DescribeSourceServersRequestFiltersTypeDef",
    "DescribeVcenterClientsRequestRequestTypeDef",
    "VcenterClientTypeDef",
    "DisassociateApplicationsRequestRequestTypeDef",
    "DisassociateSourceServersRequestRequestTypeDef",
    "DisconnectFromServiceRequestRequestTypeDef",
    "DiskTypeDef",
    "ExportErrorDataTypeDef",
    "ExportTaskSummaryTypeDef",
    "FinalizeCutoverRequestRequestTypeDef",
    "GetLaunchConfigurationRequestRequestTypeDef",
    "GetReplicationConfigurationRequestRequestTypeDef",
    "IdentificationHintsTypeDef",
    "ImportErrorDataTypeDef",
    "ImportTaskSummaryApplicationsTypeDef",
    "ImportTaskSummaryServersTypeDef",
    "ImportTaskSummaryWavesTypeDef",
    "S3BucketSourceTypeDef",
    "JobLogEventDataTypeDef",
    "LaunchedInstanceTypeDef",
    "LifeCycleLastCutoverFinalizedTypeDef",
    "LifeCycleLastCutoverInitiatedTypeDef",
    "LifeCycleLastCutoverRevertedTypeDef",
    "LifeCycleLastTestFinalizedTypeDef",
    "LifeCycleLastTestInitiatedTypeDef",
    "LifeCycleLastTestRevertedTypeDef",
    "ListApplicationsRequestFiltersTypeDef",
    "ListConnectorsRequestFiltersTypeDef",
    "ListExportErrorsRequestRequestTypeDef",
    "ListExportsRequestFiltersTypeDef",
    "ListImportErrorsRequestRequestTypeDef",
    "ListImportsRequestFiltersTypeDef",
    "ListManagedAccountsRequestRequestTypeDef",
    "ManagedAccountTypeDef",
    "SourceServerActionsRequestFiltersTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "TemplateActionsRequestFiltersTypeDef",
    "ListWavesRequestFiltersTypeDef",
    "MarkAsArchivedRequestRequestTypeDef",
    "NetworkInterfaceTypeDef",
    "OSTypeDef",
    "PauseReplicationRequestRequestTypeDef",
    "SsmExternalParameterTypeDef",
    "SsmParameterStoreParameterTypeDef",
    "RemoveSourceServerActionRequestRequestTypeDef",
    "RemoveTemplateActionRequestRequestTypeDef",
    "ReplicationConfigurationReplicatedDiskTypeDef",
    "ResumeReplicationRequestRequestTypeDef",
    "RetryDataReplicationRequestRequestTypeDef",
    "SourceServerConnectorActionTypeDef",
    "StartCutoverRequestRequestTypeDef",
    "StartExportRequestRequestTypeDef",
    "StartReplicationRequestRequestTypeDef",
    "StartTestRequestRequestTypeDef",
    "StopReplicationRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TerminateTargetInstancesRequestRequestTypeDef",
    "UnarchiveApplicationRequestRequestTypeDef",
    "UnarchiveWaveRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateApplicationRequestRequestTypeDef",
    "UpdateReplicationConfigurationTemplateRequestRequestTypeDef",
    "UpdateSourceServerReplicationTypeRequestRequestTypeDef",
    "UpdateWaveRequestRequestTypeDef",
    "WaveAggregatedStatusTypeDef",
    "ApplicationTypeDef",
    "ApplicationResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ReplicationConfigurationTemplateResponseTypeDef",
    "ChangeServerLifeCycleStateRequestRequestTypeDef",
    "ConnectorResponseTypeDef",
    "ConnectorTypeDef",
    "CreateConnectorRequestRequestTypeDef",
    "UpdateConnectorRequestRequestTypeDef",
    "DataReplicationInitiationTypeDef",
    "DescribeJobLogItemsRequestDescribeJobLogItemsPaginateTypeDef",
    "DescribeLaunchConfigurationTemplatesRequestDescribeLaunchConfigurationTemplatesPaginateTypeDef",
    "DescribeReplicationConfigurationTemplatesRequestDescribeReplicationConfigurationTemplatesPaginateTypeDef",
    "DescribeVcenterClientsRequestDescribeVcenterClientsPaginateTypeDef",
    "ListExportErrorsRequestListExportErrorsPaginateTypeDef",
    "ListImportErrorsRequestListImportErrorsPaginateTypeDef",
    "ListManagedAccountsRequestListManagedAccountsPaginateTypeDef",
    "DescribeJobsRequestDescribeJobsPaginateTypeDef",
    "DescribeJobsRequestRequestTypeDef",
    "DescribeReplicationConfigurationTemplatesResponseTypeDef",
    "DescribeSourceServersRequestDescribeSourceServersPaginateTypeDef",
    "DescribeSourceServersRequestRequestTypeDef",
    "DescribeVcenterClientsResponseTypeDef",
    "ExportTaskErrorTypeDef",
    "ExportTaskTypeDef",
    "ImportTaskErrorTypeDef",
    "ImportTaskSummaryTypeDef",
    "StartImportRequestRequestTypeDef",
    "JobLogTypeDef",
    "LifeCycleLastCutoverTypeDef",
    "LifeCycleLastTestTypeDef",
    "ListApplicationsRequestListApplicationsPaginateTypeDef",
    "ListApplicationsRequestRequestTypeDef",
    "ListConnectorsRequestListConnectorsPaginateTypeDef",
    "ListConnectorsRequestRequestTypeDef",
    "ListExportsRequestListExportsPaginateTypeDef",
    "ListExportsRequestRequestTypeDef",
    "ListImportsRequestListImportsPaginateTypeDef",
    "ListImportsRequestRequestTypeDef",
    "ListManagedAccountsResponseTypeDef",
    "ListSourceServerActionsRequestListSourceServerActionsPaginateTypeDef",
    "ListSourceServerActionsRequestRequestTypeDef",
    "ListTemplateActionsRequestListTemplateActionsPaginateTypeDef",
    "ListTemplateActionsRequestRequestTypeDef",
    "ListWavesRequestListWavesPaginateTypeDef",
    "ListWavesRequestRequestTypeDef",
    "SourcePropertiesTypeDef",
    "PutSourceServerActionRequestRequestTypeDef",
    "PutTemplateActionRequestRequestTypeDef",
    "SourceServerActionDocumentResponseTypeDef",
    "SourceServerActionDocumentTypeDef",
    "SsmDocumentPaginatorTypeDef",
    "SsmDocumentTypeDef",
    "TemplateActionDocumentResponseTypeDef",
    "TemplateActionDocumentTypeDef",
    "ReplicationConfigurationTypeDef",
    "UpdateReplicationConfigurationRequestRequestTypeDef",
    "UpdateSourceServerRequestRequestTypeDef",
    "WaveResponseTypeDef",
    "WaveTypeDef",
    "ListApplicationsResponseTypeDef",
    "ListConnectorsResponseTypeDef",
    "DataReplicationInfoTypeDef",
    "ListExportErrorsResponseTypeDef",
    "ListExportsResponseTypeDef",
    "StartExportResponseTypeDef",
    "ListImportErrorsResponseTypeDef",
    "ImportTaskTypeDef",
    "DescribeJobLogItemsResponseTypeDef",
    "LifeCycleTypeDef",
    "ListSourceServerActionsResponseTypeDef",
    "JobPostLaunchActionsLaunchStatusPaginatorTypeDef",
    "PostLaunchActionsPaginatorTypeDef",
    "JobPostLaunchActionsLaunchStatusTypeDef",
    "PostLaunchActionsTypeDef",
    "ListTemplateActionsResponseTypeDef",
    "ListWavesResponseTypeDef",
    "ListImportsResponseTypeDef",
    "StartImportResponseTypeDef",
    "SourceServerResponseTypeDef",
    "SourceServerTypeDef",
    "PostLaunchActionsStatusPaginatorTypeDef",
    "LaunchConfigurationTemplatePaginatorTypeDef",
    "PostLaunchActionsStatusTypeDef",
    "CreateLaunchConfigurationTemplateRequestRequestTypeDef",
    "LaunchConfigurationTemplateResponseTypeDef",
    "LaunchConfigurationTemplateTypeDef",
    "LaunchConfigurationTypeDef",
    "UpdateLaunchConfigurationRequestRequestTypeDef",
    "UpdateLaunchConfigurationTemplateRequestRequestTypeDef",
    "DescribeSourceServersResponseTypeDef",
    "ParticipatingServerPaginatorTypeDef",
    "DescribeLaunchConfigurationTemplatesResponsePaginatorTypeDef",
    "ParticipatingServerTypeDef",
    "DescribeLaunchConfigurationTemplatesResponseTypeDef",
    "JobPaginatorTypeDef",
    "JobTypeDef",
    "DescribeJobsResponsePaginatorTypeDef",
    "DescribeJobsResponseTypeDef",
    "StartCutoverResponseTypeDef",
    "StartTestResponseTypeDef",
    "TerminateTargetInstancesResponseTypeDef",
)

ApplicationAggregatedStatusTypeDef = TypedDict(
    "ApplicationAggregatedStatusTypeDef",
    {
        "healthStatus": NotRequired[ApplicationHealthStatusType],
        "lastUpdateDateTime": NotRequired[str],
        "progressStatus": NotRequired[ApplicationProgressStatusType],
        "totalSourceServers": NotRequired[int],
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
        "HostId": NotRequired[str],
    },
)
ArchiveApplicationRequestRequestTypeDef = TypedDict(
    "ArchiveApplicationRequestRequestTypeDef",
    {
        "applicationID": str,
        "accountID": NotRequired[str],
    },
)
ArchiveWaveRequestRequestTypeDef = TypedDict(
    "ArchiveWaveRequestRequestTypeDef",
    {
        "waveID": str,
        "accountID": NotRequired[str],
    },
)
AssociateApplicationsRequestRequestTypeDef = TypedDict(
    "AssociateApplicationsRequestRequestTypeDef",
    {
        "applicationIDs": Sequence[str],
        "waveID": str,
        "accountID": NotRequired[str],
    },
)
AssociateSourceServersRequestRequestTypeDef = TypedDict(
    "AssociateSourceServersRequestRequestTypeDef",
    {
        "applicationID": str,
        "sourceServerIDs": Sequence[str],
        "accountID": NotRequired[str],
    },
)
CPUTypeDef = TypedDict(
    "CPUTypeDef",
    {
        "cores": NotRequired[int],
        "modelName": NotRequired[str],
    },
)
ChangeServerLifeCycleStateSourceServerLifecycleTypeDef = TypedDict(
    "ChangeServerLifeCycleStateSourceServerLifecycleTypeDef",
    {
        "state": ChangeServerLifeCycleStateSourceServerLifecycleStateType,
    },
)
ConnectorSsmCommandConfigTypeDef = TypedDict(
    "ConnectorSsmCommandConfigTypeDef",
    {
        "cloudWatchOutputEnabled": bool,
        "s3OutputEnabled": bool,
        "cloudWatchLogGroupName": NotRequired[str],
        "outputS3BucketName": NotRequired[str],
    },
)
CreateApplicationRequestRequestTypeDef = TypedDict(
    "CreateApplicationRequestRequestTypeDef",
    {
        "name": str,
        "accountID": NotRequired[str],
        "description": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
LaunchTemplateDiskConfTypeDef = TypedDict(
    "LaunchTemplateDiskConfTypeDef",
    {
        "iops": NotRequired[int],
        "throughput": NotRequired[int],
        "volumeType": NotRequired[VolumeTypeType],
    },
)
LicensingTypeDef = TypedDict(
    "LicensingTypeDef",
    {
        "osByol": NotRequired[bool],
    },
)
CreateReplicationConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "CreateReplicationConfigurationTemplateRequestRequestTypeDef",
    {
        "associateDefaultSecurityGroup": bool,
        "bandwidthThrottling": int,
        "createPublicIP": bool,
        "dataPlaneRouting": ReplicationConfigurationDataPlaneRoutingType,
        "defaultLargeStagingDiskType": ReplicationConfigurationDefaultLargeStagingDiskTypeType,
        "ebsEncryption": ReplicationConfigurationEbsEncryptionType,
        "replicationServerInstanceType": str,
        "replicationServersSecurityGroupsIDs": Sequence[str],
        "stagingAreaSubnetId": str,
        "stagingAreaTags": Mapping[str, str],
        "useDedicatedReplicationServer": bool,
        "ebsEncryptionKeyArn": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "useFipsEndpoint": NotRequired[bool],
    },
)
CreateWaveRequestRequestTypeDef = TypedDict(
    "CreateWaveRequestRequestTypeDef",
    {
        "name": str,
        "accountID": NotRequired[str],
        "description": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
DataReplicationErrorTypeDef = TypedDict(
    "DataReplicationErrorTypeDef",
    {
        "error": NotRequired[DataReplicationErrorStringType],
        "rawError": NotRequired[str],
    },
)
DataReplicationInfoReplicatedDiskTypeDef = TypedDict(
    "DataReplicationInfoReplicatedDiskTypeDef",
    {
        "backloggedStorageBytes": NotRequired[int],
        "deviceName": NotRequired[str],
        "replicatedStorageBytes": NotRequired[int],
        "rescannedStorageBytes": NotRequired[int],
        "totalStorageBytes": NotRequired[int],
    },
)
DataReplicationInitiationStepTypeDef = TypedDict(
    "DataReplicationInitiationStepTypeDef",
    {
        "name": NotRequired[DataReplicationInitiationStepNameType],
        "status": NotRequired[DataReplicationInitiationStepStatusType],
    },
)
DeleteApplicationRequestRequestTypeDef = TypedDict(
    "DeleteApplicationRequestRequestTypeDef",
    {
        "applicationID": str,
        "accountID": NotRequired[str],
    },
)
DeleteConnectorRequestRequestTypeDef = TypedDict(
    "DeleteConnectorRequestRequestTypeDef",
    {
        "connectorID": str,
    },
)
DeleteJobRequestRequestTypeDef = TypedDict(
    "DeleteJobRequestRequestTypeDef",
    {
        "jobID": str,
        "accountID": NotRequired[str],
    },
)
DeleteLaunchConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "DeleteLaunchConfigurationTemplateRequestRequestTypeDef",
    {
        "launchConfigurationTemplateID": str,
    },
)
DeleteReplicationConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "DeleteReplicationConfigurationTemplateRequestRequestTypeDef",
    {
        "replicationConfigurationTemplateID": str,
    },
)
DeleteSourceServerRequestRequestTypeDef = TypedDict(
    "DeleteSourceServerRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
DeleteVcenterClientRequestRequestTypeDef = TypedDict(
    "DeleteVcenterClientRequestRequestTypeDef",
    {
        "vcenterClientID": str,
    },
)
DeleteWaveRequestRequestTypeDef = TypedDict(
    "DeleteWaveRequestRequestTypeDef",
    {
        "waveID": str,
        "accountID": NotRequired[str],
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
DescribeJobLogItemsRequestRequestTypeDef = TypedDict(
    "DescribeJobLogItemsRequestRequestTypeDef",
    {
        "jobID": str,
        "accountID": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
DescribeJobsRequestFiltersTypeDef = TypedDict(
    "DescribeJobsRequestFiltersTypeDef",
    {
        "fromDate": NotRequired[str],
        "jobIDs": NotRequired[Sequence[str]],
        "toDate": NotRequired[str],
    },
)
DescribeLaunchConfigurationTemplatesRequestRequestTypeDef = TypedDict(
    "DescribeLaunchConfigurationTemplatesRequestRequestTypeDef",
    {
        "launchConfigurationTemplateIDs": NotRequired[Sequence[str]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
DescribeReplicationConfigurationTemplatesRequestRequestTypeDef = TypedDict(
    "DescribeReplicationConfigurationTemplatesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "replicationConfigurationTemplateIDs": NotRequired[Sequence[str]],
    },
)
ReplicationConfigurationTemplateTypeDef = TypedDict(
    "ReplicationConfigurationTemplateTypeDef",
    {
        "replicationConfigurationTemplateID": str,
        "arn": NotRequired[str],
        "associateDefaultSecurityGroup": NotRequired[bool],
        "bandwidthThrottling": NotRequired[int],
        "createPublicIP": NotRequired[bool],
        "dataPlaneRouting": NotRequired[ReplicationConfigurationDataPlaneRoutingType],
        "defaultLargeStagingDiskType": NotRequired[
            ReplicationConfigurationDefaultLargeStagingDiskTypeType
        ],
        "ebsEncryption": NotRequired[ReplicationConfigurationEbsEncryptionType],
        "ebsEncryptionKeyArn": NotRequired[str],
        "replicationServerInstanceType": NotRequired[str],
        "replicationServersSecurityGroupsIDs": NotRequired[List[str]],
        "stagingAreaSubnetId": NotRequired[str],
        "stagingAreaTags": NotRequired[Dict[str, str]],
        "tags": NotRequired[Dict[str, str]],
        "useDedicatedReplicationServer": NotRequired[bool],
        "useFipsEndpoint": NotRequired[bool],
    },
)
DescribeSourceServersRequestFiltersTypeDef = TypedDict(
    "DescribeSourceServersRequestFiltersTypeDef",
    {
        "applicationIDs": NotRequired[Sequence[str]],
        "isArchived": NotRequired[bool],
        "lifeCycleStates": NotRequired[Sequence[LifeCycleStateType]],
        "replicationTypes": NotRequired[Sequence[ReplicationTypeType]],
        "sourceServerIDs": NotRequired[Sequence[str]],
    },
)
DescribeVcenterClientsRequestRequestTypeDef = TypedDict(
    "DescribeVcenterClientsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
VcenterClientTypeDef = TypedDict(
    "VcenterClientTypeDef",
    {
        "arn": NotRequired[str],
        "datacenterName": NotRequired[str],
        "hostname": NotRequired[str],
        "lastSeenDatetime": NotRequired[str],
        "sourceServerTags": NotRequired[Dict[str, str]],
        "tags": NotRequired[Dict[str, str]],
        "vcenterClientID": NotRequired[str],
        "vcenterUUID": NotRequired[str],
    },
)
DisassociateApplicationsRequestRequestTypeDef = TypedDict(
    "DisassociateApplicationsRequestRequestTypeDef",
    {
        "applicationIDs": Sequence[str],
        "waveID": str,
        "accountID": NotRequired[str],
    },
)
DisassociateSourceServersRequestRequestTypeDef = TypedDict(
    "DisassociateSourceServersRequestRequestTypeDef",
    {
        "applicationID": str,
        "sourceServerIDs": Sequence[str],
        "accountID": NotRequired[str],
    },
)
DisconnectFromServiceRequestRequestTypeDef = TypedDict(
    "DisconnectFromServiceRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
DiskTypeDef = TypedDict(
    "DiskTypeDef",
    {
        "bytes": NotRequired[int],
        "deviceName": NotRequired[str],
    },
)
ExportErrorDataTypeDef = TypedDict(
    "ExportErrorDataTypeDef",
    {
        "rawError": NotRequired[str],
    },
)
ExportTaskSummaryTypeDef = TypedDict(
    "ExportTaskSummaryTypeDef",
    {
        "applicationsCount": NotRequired[int],
        "serversCount": NotRequired[int],
        "wavesCount": NotRequired[int],
    },
)
FinalizeCutoverRequestRequestTypeDef = TypedDict(
    "FinalizeCutoverRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
GetLaunchConfigurationRequestRequestTypeDef = TypedDict(
    "GetLaunchConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
GetReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "GetReplicationConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
IdentificationHintsTypeDef = TypedDict(
    "IdentificationHintsTypeDef",
    {
        "awsInstanceID": NotRequired[str],
        "fqdn": NotRequired[str],
        "hostname": NotRequired[str],
        "vmPath": NotRequired[str],
        "vmWareUuid": NotRequired[str],
    },
)
ImportErrorDataTypeDef = TypedDict(
    "ImportErrorDataTypeDef",
    {
        "accountID": NotRequired[str],
        "applicationID": NotRequired[str],
        "ec2LaunchTemplateID": NotRequired[str],
        "rawError": NotRequired[str],
        "rowNumber": NotRequired[int],
        "sourceServerID": NotRequired[str],
        "waveID": NotRequired[str],
    },
)
ImportTaskSummaryApplicationsTypeDef = TypedDict(
    "ImportTaskSummaryApplicationsTypeDef",
    {
        "createdCount": NotRequired[int],
        "modifiedCount": NotRequired[int],
    },
)
ImportTaskSummaryServersTypeDef = TypedDict(
    "ImportTaskSummaryServersTypeDef",
    {
        "createdCount": NotRequired[int],
        "modifiedCount": NotRequired[int],
    },
)
ImportTaskSummaryWavesTypeDef = TypedDict(
    "ImportTaskSummaryWavesTypeDef",
    {
        "createdCount": NotRequired[int],
        "modifiedCount": NotRequired[int],
    },
)
S3BucketSourceTypeDef = TypedDict(
    "S3BucketSourceTypeDef",
    {
        "s3Bucket": str,
        "s3Key": str,
        "s3BucketOwner": NotRequired[str],
    },
)
JobLogEventDataTypeDef = TypedDict(
    "JobLogEventDataTypeDef",
    {
        "conversionServerID": NotRequired[str],
        "rawError": NotRequired[str],
        "sourceServerID": NotRequired[str],
        "targetInstanceID": NotRequired[str],
    },
)
LaunchedInstanceTypeDef = TypedDict(
    "LaunchedInstanceTypeDef",
    {
        "ec2InstanceID": NotRequired[str],
        "firstBoot": NotRequired[FirstBootType],
        "jobID": NotRequired[str],
    },
)
LifeCycleLastCutoverFinalizedTypeDef = TypedDict(
    "LifeCycleLastCutoverFinalizedTypeDef",
    {
        "apiCallDateTime": NotRequired[str],
    },
)
LifeCycleLastCutoverInitiatedTypeDef = TypedDict(
    "LifeCycleLastCutoverInitiatedTypeDef",
    {
        "apiCallDateTime": NotRequired[str],
        "jobID": NotRequired[str],
    },
)
LifeCycleLastCutoverRevertedTypeDef = TypedDict(
    "LifeCycleLastCutoverRevertedTypeDef",
    {
        "apiCallDateTime": NotRequired[str],
    },
)
LifeCycleLastTestFinalizedTypeDef = TypedDict(
    "LifeCycleLastTestFinalizedTypeDef",
    {
        "apiCallDateTime": NotRequired[str],
    },
)
LifeCycleLastTestInitiatedTypeDef = TypedDict(
    "LifeCycleLastTestInitiatedTypeDef",
    {
        "apiCallDateTime": NotRequired[str],
        "jobID": NotRequired[str],
    },
)
LifeCycleLastTestRevertedTypeDef = TypedDict(
    "LifeCycleLastTestRevertedTypeDef",
    {
        "apiCallDateTime": NotRequired[str],
    },
)
ListApplicationsRequestFiltersTypeDef = TypedDict(
    "ListApplicationsRequestFiltersTypeDef",
    {
        "applicationIDs": NotRequired[Sequence[str]],
        "isArchived": NotRequired[bool],
        "waveIDs": NotRequired[Sequence[str]],
    },
)
ListConnectorsRequestFiltersTypeDef = TypedDict(
    "ListConnectorsRequestFiltersTypeDef",
    {
        "connectorIDs": NotRequired[Sequence[str]],
    },
)
ListExportErrorsRequestRequestTypeDef = TypedDict(
    "ListExportErrorsRequestRequestTypeDef",
    {
        "exportID": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListExportsRequestFiltersTypeDef = TypedDict(
    "ListExportsRequestFiltersTypeDef",
    {
        "exportIDs": NotRequired[Sequence[str]],
    },
)
ListImportErrorsRequestRequestTypeDef = TypedDict(
    "ListImportErrorsRequestRequestTypeDef",
    {
        "importID": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListImportsRequestFiltersTypeDef = TypedDict(
    "ListImportsRequestFiltersTypeDef",
    {
        "importIDs": NotRequired[Sequence[str]],
    },
)
ListManagedAccountsRequestRequestTypeDef = TypedDict(
    "ListManagedAccountsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ManagedAccountTypeDef = TypedDict(
    "ManagedAccountTypeDef",
    {
        "accountId": NotRequired[str],
    },
)
SourceServerActionsRequestFiltersTypeDef = TypedDict(
    "SourceServerActionsRequestFiltersTypeDef",
    {
        "actionIDs": NotRequired[Sequence[str]],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
TemplateActionsRequestFiltersTypeDef = TypedDict(
    "TemplateActionsRequestFiltersTypeDef",
    {
        "actionIDs": NotRequired[Sequence[str]],
    },
)
ListWavesRequestFiltersTypeDef = TypedDict(
    "ListWavesRequestFiltersTypeDef",
    {
        "isArchived": NotRequired[bool],
        "waveIDs": NotRequired[Sequence[str]],
    },
)
MarkAsArchivedRequestRequestTypeDef = TypedDict(
    "MarkAsArchivedRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "ips": NotRequired[List[str]],
        "isPrimary": NotRequired[bool],
        "macAddress": NotRequired[str],
    },
)
OSTypeDef = TypedDict(
    "OSTypeDef",
    {
        "fullString": NotRequired[str],
    },
)
PauseReplicationRequestRequestTypeDef = TypedDict(
    "PauseReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
SsmExternalParameterTypeDef = TypedDict(
    "SsmExternalParameterTypeDef",
    {
        "dynamicPath": NotRequired[str],
    },
)
SsmParameterStoreParameterTypeDef = TypedDict(
    "SsmParameterStoreParameterTypeDef",
    {
        "parameterName": str,
        "parameterType": Literal["STRING"],
    },
)
RemoveSourceServerActionRequestRequestTypeDef = TypedDict(
    "RemoveSourceServerActionRequestRequestTypeDef",
    {
        "actionID": str,
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
RemoveTemplateActionRequestRequestTypeDef = TypedDict(
    "RemoveTemplateActionRequestRequestTypeDef",
    {
        "actionID": str,
        "launchConfigurationTemplateID": str,
    },
)
ReplicationConfigurationReplicatedDiskTypeDef = TypedDict(
    "ReplicationConfigurationReplicatedDiskTypeDef",
    {
        "deviceName": NotRequired[str],
        "iops": NotRequired[int],
        "isBootDisk": NotRequired[bool],
        "stagingDiskType": NotRequired[ReplicationConfigurationReplicatedDiskStagingDiskTypeType],
        "throughput": NotRequired[int],
    },
)
ResumeReplicationRequestRequestTypeDef = TypedDict(
    "ResumeReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
RetryDataReplicationRequestRequestTypeDef = TypedDict(
    "RetryDataReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
SourceServerConnectorActionTypeDef = TypedDict(
    "SourceServerConnectorActionTypeDef",
    {
        "connectorArn": NotRequired[str],
        "credentialsSecretArn": NotRequired[str],
    },
)
StartCutoverRequestRequestTypeDef = TypedDict(
    "StartCutoverRequestRequestTypeDef",
    {
        "sourceServerIDs": Sequence[str],
        "accountID": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
StartExportRequestRequestTypeDef = TypedDict(
    "StartExportRequestRequestTypeDef",
    {
        "s3Bucket": str,
        "s3Key": str,
        "s3BucketOwner": NotRequired[str],
    },
)
StartReplicationRequestRequestTypeDef = TypedDict(
    "StartReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
StartTestRequestRequestTypeDef = TypedDict(
    "StartTestRequestRequestTypeDef",
    {
        "sourceServerIDs": Sequence[str],
        "accountID": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
StopReplicationRequestRequestTypeDef = TypedDict(
    "StopReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
TerminateTargetInstancesRequestRequestTypeDef = TypedDict(
    "TerminateTargetInstancesRequestRequestTypeDef",
    {
        "sourceServerIDs": Sequence[str],
        "accountID": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
UnarchiveApplicationRequestRequestTypeDef = TypedDict(
    "UnarchiveApplicationRequestRequestTypeDef",
    {
        "applicationID": str,
        "accountID": NotRequired[str],
    },
)
UnarchiveWaveRequestRequestTypeDef = TypedDict(
    "UnarchiveWaveRequestRequestTypeDef",
    {
        "waveID": str,
        "accountID": NotRequired[str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateApplicationRequestRequestTypeDef = TypedDict(
    "UpdateApplicationRequestRequestTypeDef",
    {
        "applicationID": str,
        "accountID": NotRequired[str],
        "description": NotRequired[str],
        "name": NotRequired[str],
    },
)
UpdateReplicationConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "UpdateReplicationConfigurationTemplateRequestRequestTypeDef",
    {
        "replicationConfigurationTemplateID": str,
        "arn": NotRequired[str],
        "associateDefaultSecurityGroup": NotRequired[bool],
        "bandwidthThrottling": NotRequired[int],
        "createPublicIP": NotRequired[bool],
        "dataPlaneRouting": NotRequired[ReplicationConfigurationDataPlaneRoutingType],
        "defaultLargeStagingDiskType": NotRequired[
            ReplicationConfigurationDefaultLargeStagingDiskTypeType
        ],
        "ebsEncryption": NotRequired[ReplicationConfigurationEbsEncryptionType],
        "ebsEncryptionKeyArn": NotRequired[str],
        "replicationServerInstanceType": NotRequired[str],
        "replicationServersSecurityGroupsIDs": NotRequired[Sequence[str]],
        "stagingAreaSubnetId": NotRequired[str],
        "stagingAreaTags": NotRequired[Mapping[str, str]],
        "useDedicatedReplicationServer": NotRequired[bool],
        "useFipsEndpoint": NotRequired[bool],
    },
)
UpdateSourceServerReplicationTypeRequestRequestTypeDef = TypedDict(
    "UpdateSourceServerReplicationTypeRequestRequestTypeDef",
    {
        "replicationType": ReplicationTypeType,
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
UpdateWaveRequestRequestTypeDef = TypedDict(
    "UpdateWaveRequestRequestTypeDef",
    {
        "waveID": str,
        "accountID": NotRequired[str],
        "description": NotRequired[str],
        "name": NotRequired[str],
    },
)
WaveAggregatedStatusTypeDef = TypedDict(
    "WaveAggregatedStatusTypeDef",
    {
        "healthStatus": NotRequired[WaveHealthStatusType],
        "lastUpdateDateTime": NotRequired[str],
        "progressStatus": NotRequired[WaveProgressStatusType],
        "replicationStartedDateTime": NotRequired[str],
        "totalApplications": NotRequired[int],
    },
)
ApplicationTypeDef = TypedDict(
    "ApplicationTypeDef",
    {
        "applicationAggregatedStatus": NotRequired[ApplicationAggregatedStatusTypeDef],
        "applicationID": NotRequired[str],
        "arn": NotRequired[str],
        "creationDateTime": NotRequired[str],
        "description": NotRequired[str],
        "isArchived": NotRequired[bool],
        "lastModifiedDateTime": NotRequired[str],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "waveID": NotRequired[str],
    },
)
ApplicationResponseTypeDef = TypedDict(
    "ApplicationResponseTypeDef",
    {
        "applicationAggregatedStatus": ApplicationAggregatedStatusTypeDef,
        "applicationID": str,
        "arn": str,
        "creationDateTime": str,
        "description": str,
        "isArchived": bool,
        "lastModifiedDateTime": str,
        "name": str,
        "tags": Dict[str, str],
        "waveID": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ReplicationConfigurationTemplateResponseTypeDef = TypedDict(
    "ReplicationConfigurationTemplateResponseTypeDef",
    {
        "arn": str,
        "associateDefaultSecurityGroup": bool,
        "bandwidthThrottling": int,
        "createPublicIP": bool,
        "dataPlaneRouting": ReplicationConfigurationDataPlaneRoutingType,
        "defaultLargeStagingDiskType": ReplicationConfigurationDefaultLargeStagingDiskTypeType,
        "ebsEncryption": ReplicationConfigurationEbsEncryptionType,
        "ebsEncryptionKeyArn": str,
        "replicationConfigurationTemplateID": str,
        "replicationServerInstanceType": str,
        "replicationServersSecurityGroupsIDs": List[str],
        "stagingAreaSubnetId": str,
        "stagingAreaTags": Dict[str, str],
        "tags": Dict[str, str],
        "useDedicatedReplicationServer": bool,
        "useFipsEndpoint": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ChangeServerLifeCycleStateRequestRequestTypeDef = TypedDict(
    "ChangeServerLifeCycleStateRequestRequestTypeDef",
    {
        "lifeCycle": ChangeServerLifeCycleStateSourceServerLifecycleTypeDef,
        "sourceServerID": str,
        "accountID": NotRequired[str],
    },
)
ConnectorResponseTypeDef = TypedDict(
    "ConnectorResponseTypeDef",
    {
        "arn": str,
        "connectorID": str,
        "name": str,
        "ssmCommandConfig": ConnectorSsmCommandConfigTypeDef,
        "ssmInstanceID": str,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ConnectorTypeDef = TypedDict(
    "ConnectorTypeDef",
    {
        "arn": NotRequired[str],
        "connectorID": NotRequired[str],
        "name": NotRequired[str],
        "ssmCommandConfig": NotRequired[ConnectorSsmCommandConfigTypeDef],
        "ssmInstanceID": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
CreateConnectorRequestRequestTypeDef = TypedDict(
    "CreateConnectorRequestRequestTypeDef",
    {
        "name": str,
        "ssmInstanceID": str,
        "ssmCommandConfig": NotRequired[ConnectorSsmCommandConfigTypeDef],
        "tags": NotRequired[Mapping[str, str]],
    },
)
UpdateConnectorRequestRequestTypeDef = TypedDict(
    "UpdateConnectorRequestRequestTypeDef",
    {
        "connectorID": str,
        "name": NotRequired[str],
        "ssmCommandConfig": NotRequired[ConnectorSsmCommandConfigTypeDef],
    },
)
DataReplicationInitiationTypeDef = TypedDict(
    "DataReplicationInitiationTypeDef",
    {
        "nextAttemptDateTime": NotRequired[str],
        "startDateTime": NotRequired[str],
        "steps": NotRequired[List[DataReplicationInitiationStepTypeDef]],
    },
)
DescribeJobLogItemsRequestDescribeJobLogItemsPaginateTypeDef = TypedDict(
    "DescribeJobLogItemsRequestDescribeJobLogItemsPaginateTypeDef",
    {
        "jobID": str,
        "accountID": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeLaunchConfigurationTemplatesRequestDescribeLaunchConfigurationTemplatesPaginateTypeDef = TypedDict(
    "DescribeLaunchConfigurationTemplatesRequestDescribeLaunchConfigurationTemplatesPaginateTypeDef",
    {
        "launchConfigurationTemplateIDs": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeReplicationConfigurationTemplatesRequestDescribeReplicationConfigurationTemplatesPaginateTypeDef = TypedDict(
    "DescribeReplicationConfigurationTemplatesRequestDescribeReplicationConfigurationTemplatesPaginateTypeDef",
    {
        "replicationConfigurationTemplateIDs": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeVcenterClientsRequestDescribeVcenterClientsPaginateTypeDef = TypedDict(
    "DescribeVcenterClientsRequestDescribeVcenterClientsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListExportErrorsRequestListExportErrorsPaginateTypeDef = TypedDict(
    "ListExportErrorsRequestListExportErrorsPaginateTypeDef",
    {
        "exportID": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListImportErrorsRequestListImportErrorsPaginateTypeDef = TypedDict(
    "ListImportErrorsRequestListImportErrorsPaginateTypeDef",
    {
        "importID": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListManagedAccountsRequestListManagedAccountsPaginateTypeDef = TypedDict(
    "ListManagedAccountsRequestListManagedAccountsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeJobsRequestDescribeJobsPaginateTypeDef = TypedDict(
    "DescribeJobsRequestDescribeJobsPaginateTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[DescribeJobsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeJobsRequestRequestTypeDef = TypedDict(
    "DescribeJobsRequestRequestTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[DescribeJobsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
DescribeReplicationConfigurationTemplatesResponseTypeDef = TypedDict(
    "DescribeReplicationConfigurationTemplatesResponseTypeDef",
    {
        "items": List[ReplicationConfigurationTemplateTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeSourceServersRequestDescribeSourceServersPaginateTypeDef = TypedDict(
    "DescribeSourceServersRequestDescribeSourceServersPaginateTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[DescribeSourceServersRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeSourceServersRequestRequestTypeDef = TypedDict(
    "DescribeSourceServersRequestRequestTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[DescribeSourceServersRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
DescribeVcenterClientsResponseTypeDef = TypedDict(
    "DescribeVcenterClientsResponseTypeDef",
    {
        "items": List[VcenterClientTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ExportTaskErrorTypeDef = TypedDict(
    "ExportTaskErrorTypeDef",
    {
        "errorData": NotRequired[ExportErrorDataTypeDef],
        "errorDateTime": NotRequired[str],
    },
)
ExportTaskTypeDef = TypedDict(
    "ExportTaskTypeDef",
    {
        "creationDateTime": NotRequired[str],
        "endDateTime": NotRequired[str],
        "exportID": NotRequired[str],
        "progressPercentage": NotRequired[float],
        "s3Bucket": NotRequired[str],
        "s3BucketOwner": NotRequired[str],
        "s3Key": NotRequired[str],
        "status": NotRequired[ExportStatusType],
        "summary": NotRequired[ExportTaskSummaryTypeDef],
    },
)
ImportTaskErrorTypeDef = TypedDict(
    "ImportTaskErrorTypeDef",
    {
        "errorData": NotRequired[ImportErrorDataTypeDef],
        "errorDateTime": NotRequired[str],
        "errorType": NotRequired[ImportErrorTypeType],
    },
)
ImportTaskSummaryTypeDef = TypedDict(
    "ImportTaskSummaryTypeDef",
    {
        "applications": NotRequired[ImportTaskSummaryApplicationsTypeDef],
        "servers": NotRequired[ImportTaskSummaryServersTypeDef],
        "waves": NotRequired[ImportTaskSummaryWavesTypeDef],
    },
)
StartImportRequestRequestTypeDef = TypedDict(
    "StartImportRequestRequestTypeDef",
    {
        "s3BucketSource": S3BucketSourceTypeDef,
        "clientToken": NotRequired[str],
    },
)
JobLogTypeDef = TypedDict(
    "JobLogTypeDef",
    {
        "event": NotRequired[JobLogEventType],
        "eventData": NotRequired[JobLogEventDataTypeDef],
        "logDateTime": NotRequired[str],
    },
)
LifeCycleLastCutoverTypeDef = TypedDict(
    "LifeCycleLastCutoverTypeDef",
    {
        "finalized": NotRequired[LifeCycleLastCutoverFinalizedTypeDef],
        "initiated": NotRequired[LifeCycleLastCutoverInitiatedTypeDef],
        "reverted": NotRequired[LifeCycleLastCutoverRevertedTypeDef],
    },
)
LifeCycleLastTestTypeDef = TypedDict(
    "LifeCycleLastTestTypeDef",
    {
        "finalized": NotRequired[LifeCycleLastTestFinalizedTypeDef],
        "initiated": NotRequired[LifeCycleLastTestInitiatedTypeDef],
        "reverted": NotRequired[LifeCycleLastTestRevertedTypeDef],
    },
)
ListApplicationsRequestListApplicationsPaginateTypeDef = TypedDict(
    "ListApplicationsRequestListApplicationsPaginateTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[ListApplicationsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListApplicationsRequestRequestTypeDef = TypedDict(
    "ListApplicationsRequestRequestTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[ListApplicationsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListConnectorsRequestListConnectorsPaginateTypeDef = TypedDict(
    "ListConnectorsRequestListConnectorsPaginateTypeDef",
    {
        "filters": NotRequired[ListConnectorsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListConnectorsRequestRequestTypeDef = TypedDict(
    "ListConnectorsRequestRequestTypeDef",
    {
        "filters": NotRequired[ListConnectorsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListExportsRequestListExportsPaginateTypeDef = TypedDict(
    "ListExportsRequestListExportsPaginateTypeDef",
    {
        "filters": NotRequired[ListExportsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListExportsRequestRequestTypeDef = TypedDict(
    "ListExportsRequestRequestTypeDef",
    {
        "filters": NotRequired[ListExportsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListImportsRequestListImportsPaginateTypeDef = TypedDict(
    "ListImportsRequestListImportsPaginateTypeDef",
    {
        "filters": NotRequired[ListImportsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListImportsRequestRequestTypeDef = TypedDict(
    "ListImportsRequestRequestTypeDef",
    {
        "filters": NotRequired[ListImportsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListManagedAccountsResponseTypeDef = TypedDict(
    "ListManagedAccountsResponseTypeDef",
    {
        "items": List[ManagedAccountTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSourceServerActionsRequestListSourceServerActionsPaginateTypeDef = TypedDict(
    "ListSourceServerActionsRequestListSourceServerActionsPaginateTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
        "filters": NotRequired[SourceServerActionsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSourceServerActionsRequestRequestTypeDef = TypedDict(
    "ListSourceServerActionsRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
        "filters": NotRequired[SourceServerActionsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListTemplateActionsRequestListTemplateActionsPaginateTypeDef = TypedDict(
    "ListTemplateActionsRequestListTemplateActionsPaginateTypeDef",
    {
        "launchConfigurationTemplateID": str,
        "filters": NotRequired[TemplateActionsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTemplateActionsRequestRequestTypeDef = TypedDict(
    "ListTemplateActionsRequestRequestTypeDef",
    {
        "launchConfigurationTemplateID": str,
        "filters": NotRequired[TemplateActionsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListWavesRequestListWavesPaginateTypeDef = TypedDict(
    "ListWavesRequestListWavesPaginateTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[ListWavesRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListWavesRequestRequestTypeDef = TypedDict(
    "ListWavesRequestRequestTypeDef",
    {
        "accountID": NotRequired[str],
        "filters": NotRequired[ListWavesRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
SourcePropertiesTypeDef = TypedDict(
    "SourcePropertiesTypeDef",
    {
        "cpus": NotRequired[List[CPUTypeDef]],
        "disks": NotRequired[List[DiskTypeDef]],
        "identificationHints": NotRequired[IdentificationHintsTypeDef],
        "lastUpdatedDateTime": NotRequired[str],
        "networkInterfaces": NotRequired[List[NetworkInterfaceTypeDef]],
        "os": NotRequired[OSTypeDef],
        "ramBytes": NotRequired[int],
        "recommendedInstanceType": NotRequired[str],
    },
)
PutSourceServerActionRequestRequestTypeDef = TypedDict(
    "PutSourceServerActionRequestRequestTypeDef",
    {
        "actionID": str,
        "actionName": str,
        "documentIdentifier": str,
        "order": int,
        "sourceServerID": str,
        "accountID": NotRequired[str],
        "active": NotRequired[bool],
        "category": NotRequired[ActionCategoryType],
        "description": NotRequired[str],
        "documentVersion": NotRequired[str],
        "externalParameters": NotRequired[Mapping[str, SsmExternalParameterTypeDef]],
        "mustSucceedForCutover": NotRequired[bool],
        "parameters": NotRequired[Mapping[str, Sequence[SsmParameterStoreParameterTypeDef]]],
        "timeoutSeconds": NotRequired[int],
    },
)
PutTemplateActionRequestRequestTypeDef = TypedDict(
    "PutTemplateActionRequestRequestTypeDef",
    {
        "actionID": str,
        "actionName": str,
        "documentIdentifier": str,
        "launchConfigurationTemplateID": str,
        "order": int,
        "active": NotRequired[bool],
        "category": NotRequired[ActionCategoryType],
        "description": NotRequired[str],
        "documentVersion": NotRequired[str],
        "externalParameters": NotRequired[Mapping[str, SsmExternalParameterTypeDef]],
        "mustSucceedForCutover": NotRequired[bool],
        "operatingSystem": NotRequired[str],
        "parameters": NotRequired[Mapping[str, Sequence[SsmParameterStoreParameterTypeDef]]],
        "timeoutSeconds": NotRequired[int],
    },
)
SourceServerActionDocumentResponseTypeDef = TypedDict(
    "SourceServerActionDocumentResponseTypeDef",
    {
        "actionID": str,
        "actionName": str,
        "active": bool,
        "category": ActionCategoryType,
        "description": str,
        "documentIdentifier": str,
        "documentVersion": str,
        "externalParameters": Dict[str, SsmExternalParameterTypeDef],
        "mustSucceedForCutover": bool,
        "order": int,
        "parameters": Dict[str, List[SsmParameterStoreParameterTypeDef]],
        "timeoutSeconds": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SourceServerActionDocumentTypeDef = TypedDict(
    "SourceServerActionDocumentTypeDef",
    {
        "actionID": NotRequired[str],
        "actionName": NotRequired[str],
        "active": NotRequired[bool],
        "category": NotRequired[ActionCategoryType],
        "description": NotRequired[str],
        "documentIdentifier": NotRequired[str],
        "documentVersion": NotRequired[str],
        "externalParameters": NotRequired[Dict[str, SsmExternalParameterTypeDef]],
        "mustSucceedForCutover": NotRequired[bool],
        "order": NotRequired[int],
        "parameters": NotRequired[Dict[str, List[SsmParameterStoreParameterTypeDef]]],
        "timeoutSeconds": NotRequired[int],
    },
)
SsmDocumentPaginatorTypeDef = TypedDict(
    "SsmDocumentPaginatorTypeDef",
    {
        "actionName": str,
        "ssmDocumentName": str,
        "externalParameters": NotRequired[Dict[str, SsmExternalParameterTypeDef]],
        "mustSucceedForCutover": NotRequired[bool],
        "parameters": NotRequired[Dict[str, List[SsmParameterStoreParameterTypeDef]]],
        "timeoutSeconds": NotRequired[int],
    },
)
SsmDocumentTypeDef = TypedDict(
    "SsmDocumentTypeDef",
    {
        "actionName": str,
        "ssmDocumentName": str,
        "externalParameters": NotRequired[Mapping[str, SsmExternalParameterTypeDef]],
        "mustSucceedForCutover": NotRequired[bool],
        "parameters": NotRequired[Mapping[str, Sequence[SsmParameterStoreParameterTypeDef]]],
        "timeoutSeconds": NotRequired[int],
    },
)
TemplateActionDocumentResponseTypeDef = TypedDict(
    "TemplateActionDocumentResponseTypeDef",
    {
        "actionID": str,
        "actionName": str,
        "active": bool,
        "category": ActionCategoryType,
        "description": str,
        "documentIdentifier": str,
        "documentVersion": str,
        "externalParameters": Dict[str, SsmExternalParameterTypeDef],
        "mustSucceedForCutover": bool,
        "operatingSystem": str,
        "order": int,
        "parameters": Dict[str, List[SsmParameterStoreParameterTypeDef]],
        "timeoutSeconds": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TemplateActionDocumentTypeDef = TypedDict(
    "TemplateActionDocumentTypeDef",
    {
        "actionID": NotRequired[str],
        "actionName": NotRequired[str],
        "active": NotRequired[bool],
        "category": NotRequired[ActionCategoryType],
        "description": NotRequired[str],
        "documentIdentifier": NotRequired[str],
        "documentVersion": NotRequired[str],
        "externalParameters": NotRequired[Dict[str, SsmExternalParameterTypeDef]],
        "mustSucceedForCutover": NotRequired[bool],
        "operatingSystem": NotRequired[str],
        "order": NotRequired[int],
        "parameters": NotRequired[Dict[str, List[SsmParameterStoreParameterTypeDef]]],
        "timeoutSeconds": NotRequired[int],
    },
)
ReplicationConfigurationTypeDef = TypedDict(
    "ReplicationConfigurationTypeDef",
    {
        "associateDefaultSecurityGroup": bool,
        "bandwidthThrottling": int,
        "createPublicIP": bool,
        "dataPlaneRouting": ReplicationConfigurationDataPlaneRoutingType,
        "defaultLargeStagingDiskType": ReplicationConfigurationDefaultLargeStagingDiskTypeType,
        "ebsEncryption": ReplicationConfigurationEbsEncryptionType,
        "ebsEncryptionKeyArn": str,
        "name": str,
        "replicatedDisks": List[ReplicationConfigurationReplicatedDiskTypeDef],
        "replicationServerInstanceType": str,
        "replicationServersSecurityGroupsIDs": List[str],
        "sourceServerID": str,
        "stagingAreaSubnetId": str,
        "stagingAreaTags": Dict[str, str],
        "useDedicatedReplicationServer": bool,
        "useFipsEndpoint": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateReplicationConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
        "associateDefaultSecurityGroup": NotRequired[bool],
        "bandwidthThrottling": NotRequired[int],
        "createPublicIP": NotRequired[bool],
        "dataPlaneRouting": NotRequired[ReplicationConfigurationDataPlaneRoutingType],
        "defaultLargeStagingDiskType": NotRequired[
            ReplicationConfigurationDefaultLargeStagingDiskTypeType
        ],
        "ebsEncryption": NotRequired[ReplicationConfigurationEbsEncryptionType],
        "ebsEncryptionKeyArn": NotRequired[str],
        "name": NotRequired[str],
        "replicatedDisks": NotRequired[Sequence[ReplicationConfigurationReplicatedDiskTypeDef]],
        "replicationServerInstanceType": NotRequired[str],
        "replicationServersSecurityGroupsIDs": NotRequired[Sequence[str]],
        "stagingAreaSubnetId": NotRequired[str],
        "stagingAreaTags": NotRequired[Mapping[str, str]],
        "useDedicatedReplicationServer": NotRequired[bool],
        "useFipsEndpoint": NotRequired[bool],
    },
)
UpdateSourceServerRequestRequestTypeDef = TypedDict(
    "UpdateSourceServerRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
        "connectorAction": NotRequired[SourceServerConnectorActionTypeDef],
    },
)
WaveResponseTypeDef = TypedDict(
    "WaveResponseTypeDef",
    {
        "arn": str,
        "creationDateTime": str,
        "description": str,
        "isArchived": bool,
        "lastModifiedDateTime": str,
        "name": str,
        "tags": Dict[str, str],
        "waveAggregatedStatus": WaveAggregatedStatusTypeDef,
        "waveID": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
WaveTypeDef = TypedDict(
    "WaveTypeDef",
    {
        "arn": NotRequired[str],
        "creationDateTime": NotRequired[str],
        "description": NotRequired[str],
        "isArchived": NotRequired[bool],
        "lastModifiedDateTime": NotRequired[str],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "waveAggregatedStatus": NotRequired[WaveAggregatedStatusTypeDef],
        "waveID": NotRequired[str],
    },
)
ListApplicationsResponseTypeDef = TypedDict(
    "ListApplicationsResponseTypeDef",
    {
        "items": List[ApplicationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListConnectorsResponseTypeDef = TypedDict(
    "ListConnectorsResponseTypeDef",
    {
        "items": List[ConnectorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DataReplicationInfoTypeDef = TypedDict(
    "DataReplicationInfoTypeDef",
    {
        "dataReplicationError": NotRequired[DataReplicationErrorTypeDef],
        "dataReplicationInitiation": NotRequired[DataReplicationInitiationTypeDef],
        "dataReplicationState": NotRequired[DataReplicationStateType],
        "etaDateTime": NotRequired[str],
        "lagDuration": NotRequired[str],
        "lastSnapshotDateTime": NotRequired[str],
        "replicatedDisks": NotRequired[List[DataReplicationInfoReplicatedDiskTypeDef]],
    },
)
ListExportErrorsResponseTypeDef = TypedDict(
    "ListExportErrorsResponseTypeDef",
    {
        "items": List[ExportTaskErrorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListExportsResponseTypeDef = TypedDict(
    "ListExportsResponseTypeDef",
    {
        "items": List[ExportTaskTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartExportResponseTypeDef = TypedDict(
    "StartExportResponseTypeDef",
    {
        "exportTask": ExportTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListImportErrorsResponseTypeDef = TypedDict(
    "ListImportErrorsResponseTypeDef",
    {
        "items": List[ImportTaskErrorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportTaskTypeDef = TypedDict(
    "ImportTaskTypeDef",
    {
        "creationDateTime": NotRequired[str],
        "endDateTime": NotRequired[str],
        "importID": NotRequired[str],
        "progressPercentage": NotRequired[float],
        "s3BucketSource": NotRequired[S3BucketSourceTypeDef],
        "status": NotRequired[ImportStatusType],
        "summary": NotRequired[ImportTaskSummaryTypeDef],
    },
)
DescribeJobLogItemsResponseTypeDef = TypedDict(
    "DescribeJobLogItemsResponseTypeDef",
    {
        "items": List[JobLogTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LifeCycleTypeDef = TypedDict(
    "LifeCycleTypeDef",
    {
        "addedToServiceDateTime": NotRequired[str],
        "elapsedReplicationDuration": NotRequired[str],
        "firstByteDateTime": NotRequired[str],
        "lastCutover": NotRequired[LifeCycleLastCutoverTypeDef],
        "lastSeenByServiceDateTime": NotRequired[str],
        "lastTest": NotRequired[LifeCycleLastTestTypeDef],
        "state": NotRequired[LifeCycleStateType],
    },
)
ListSourceServerActionsResponseTypeDef = TypedDict(
    "ListSourceServerActionsResponseTypeDef",
    {
        "items": List[SourceServerActionDocumentTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
JobPostLaunchActionsLaunchStatusPaginatorTypeDef = TypedDict(
    "JobPostLaunchActionsLaunchStatusPaginatorTypeDef",
    {
        "executionID": NotRequired[str],
        "executionStatus": NotRequired[PostLaunchActionExecutionStatusType],
        "failureReason": NotRequired[str],
        "ssmDocument": NotRequired[SsmDocumentPaginatorTypeDef],
        "ssmDocumentType": NotRequired[SsmDocumentTypeType],
    },
)
PostLaunchActionsPaginatorTypeDef = TypedDict(
    "PostLaunchActionsPaginatorTypeDef",
    {
        "cloudWatchLogGroupName": NotRequired[str],
        "deployment": NotRequired[PostLaunchActionsDeploymentTypeType],
        "s3LogBucket": NotRequired[str],
        "s3OutputKeyPrefix": NotRequired[str],
        "ssmDocuments": NotRequired[List[SsmDocumentPaginatorTypeDef]],
    },
)
JobPostLaunchActionsLaunchStatusTypeDef = TypedDict(
    "JobPostLaunchActionsLaunchStatusTypeDef",
    {
        "executionID": NotRequired[str],
        "executionStatus": NotRequired[PostLaunchActionExecutionStatusType],
        "failureReason": NotRequired[str],
        "ssmDocument": NotRequired[SsmDocumentTypeDef],
        "ssmDocumentType": NotRequired[SsmDocumentTypeType],
    },
)
PostLaunchActionsTypeDef = TypedDict(
    "PostLaunchActionsTypeDef",
    {
        "cloudWatchLogGroupName": NotRequired[str],
        "deployment": NotRequired[PostLaunchActionsDeploymentTypeType],
        "s3LogBucket": NotRequired[str],
        "s3OutputKeyPrefix": NotRequired[str],
        "ssmDocuments": NotRequired[Sequence[SsmDocumentTypeDef]],
    },
)
ListTemplateActionsResponseTypeDef = TypedDict(
    "ListTemplateActionsResponseTypeDef",
    {
        "items": List[TemplateActionDocumentTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListWavesResponseTypeDef = TypedDict(
    "ListWavesResponseTypeDef",
    {
        "items": List[WaveTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListImportsResponseTypeDef = TypedDict(
    "ListImportsResponseTypeDef",
    {
        "items": List[ImportTaskTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartImportResponseTypeDef = TypedDict(
    "StartImportResponseTypeDef",
    {
        "importTask": ImportTaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SourceServerResponseTypeDef = TypedDict(
    "SourceServerResponseTypeDef",
    {
        "applicationID": str,
        "arn": str,
        "connectorAction": SourceServerConnectorActionTypeDef,
        "dataReplicationInfo": DataReplicationInfoTypeDef,
        "fqdnForActionFramework": str,
        "isArchived": bool,
        "launchedInstance": LaunchedInstanceTypeDef,
        "lifeCycle": LifeCycleTypeDef,
        "replicationType": ReplicationTypeType,
        "sourceProperties": SourcePropertiesTypeDef,
        "sourceServerID": str,
        "tags": Dict[str, str],
        "userProvidedID": str,
        "vcenterClientID": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SourceServerTypeDef = TypedDict(
    "SourceServerTypeDef",
    {
        "applicationID": NotRequired[str],
        "arn": NotRequired[str],
        "connectorAction": NotRequired[SourceServerConnectorActionTypeDef],
        "dataReplicationInfo": NotRequired[DataReplicationInfoTypeDef],
        "fqdnForActionFramework": NotRequired[str],
        "isArchived": NotRequired[bool],
        "launchedInstance": NotRequired[LaunchedInstanceTypeDef],
        "lifeCycle": NotRequired[LifeCycleTypeDef],
        "replicationType": NotRequired[ReplicationTypeType],
        "sourceProperties": NotRequired[SourcePropertiesTypeDef],
        "sourceServerID": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "userProvidedID": NotRequired[str],
        "vcenterClientID": NotRequired[str],
    },
)
PostLaunchActionsStatusPaginatorTypeDef = TypedDict(
    "PostLaunchActionsStatusPaginatorTypeDef",
    {
        "postLaunchActionsLaunchStatusList": NotRequired[
            List[JobPostLaunchActionsLaunchStatusPaginatorTypeDef]
        ],
        "ssmAgentDiscoveryDatetime": NotRequired[str],
    },
)
LaunchConfigurationTemplatePaginatorTypeDef = TypedDict(
    "LaunchConfigurationTemplatePaginatorTypeDef",
    {
        "launchConfigurationTemplateID": str,
        "arn": NotRequired[str],
        "associatePublicIpAddress": NotRequired[bool],
        "bootMode": NotRequired[BootModeType],
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "ec2LaunchTemplateID": NotRequired[str],
        "enableMapAutoTagging": NotRequired[bool],
        "largeVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "mapAutoTaggingMpeID": NotRequired[str],
        "postLaunchActions": NotRequired[PostLaunchActionsPaginatorTypeDef],
        "smallVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "smallVolumeMaxSize": NotRequired[int],
        "tags": NotRequired[Dict[str, str]],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)
PostLaunchActionsStatusTypeDef = TypedDict(
    "PostLaunchActionsStatusTypeDef",
    {
        "postLaunchActionsLaunchStatusList": NotRequired[
            List[JobPostLaunchActionsLaunchStatusTypeDef]
        ],
        "ssmAgentDiscoveryDatetime": NotRequired[str],
    },
)
CreateLaunchConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "CreateLaunchConfigurationTemplateRequestRequestTypeDef",
    {
        "associatePublicIpAddress": NotRequired[bool],
        "bootMode": NotRequired[BootModeType],
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "enableMapAutoTagging": NotRequired[bool],
        "largeVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "mapAutoTaggingMpeID": NotRequired[str],
        "postLaunchActions": NotRequired[PostLaunchActionsTypeDef],
        "smallVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "smallVolumeMaxSize": NotRequired[int],
        "tags": NotRequired[Mapping[str, str]],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)
LaunchConfigurationTemplateResponseTypeDef = TypedDict(
    "LaunchConfigurationTemplateResponseTypeDef",
    {
        "arn": str,
        "associatePublicIpAddress": bool,
        "bootMode": BootModeType,
        "copyPrivateIp": bool,
        "copyTags": bool,
        "ec2LaunchTemplateID": str,
        "enableMapAutoTagging": bool,
        "largeVolumeConf": LaunchTemplateDiskConfTypeDef,
        "launchConfigurationTemplateID": str,
        "launchDisposition": LaunchDispositionType,
        "licensing": LicensingTypeDef,
        "mapAutoTaggingMpeID": str,
        "postLaunchActions": PostLaunchActionsTypeDef,
        "smallVolumeConf": LaunchTemplateDiskConfTypeDef,
        "smallVolumeMaxSize": int,
        "tags": Dict[str, str],
        "targetInstanceTypeRightSizingMethod": TargetInstanceTypeRightSizingMethodType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LaunchConfigurationTemplateTypeDef = TypedDict(
    "LaunchConfigurationTemplateTypeDef",
    {
        "launchConfigurationTemplateID": str,
        "arn": NotRequired[str],
        "associatePublicIpAddress": NotRequired[bool],
        "bootMode": NotRequired[BootModeType],
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "ec2LaunchTemplateID": NotRequired[str],
        "enableMapAutoTagging": NotRequired[bool],
        "largeVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "mapAutoTaggingMpeID": NotRequired[str],
        "postLaunchActions": NotRequired[PostLaunchActionsTypeDef],
        "smallVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "smallVolumeMaxSize": NotRequired[int],
        "tags": NotRequired[Dict[str, str]],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)
LaunchConfigurationTypeDef = TypedDict(
    "LaunchConfigurationTypeDef",
    {
        "bootMode": BootModeType,
        "copyPrivateIp": bool,
        "copyTags": bool,
        "ec2LaunchTemplateID": str,
        "enableMapAutoTagging": bool,
        "launchDisposition": LaunchDispositionType,
        "licensing": LicensingTypeDef,
        "mapAutoTaggingMpeID": str,
        "name": str,
        "postLaunchActions": PostLaunchActionsTypeDef,
        "sourceServerID": str,
        "targetInstanceTypeRightSizingMethod": TargetInstanceTypeRightSizingMethodType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateLaunchConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateLaunchConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "accountID": NotRequired[str],
        "bootMode": NotRequired[BootModeType],
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "enableMapAutoTagging": NotRequired[bool],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "mapAutoTaggingMpeID": NotRequired[str],
        "name": NotRequired[str],
        "postLaunchActions": NotRequired[PostLaunchActionsTypeDef],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)
UpdateLaunchConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "UpdateLaunchConfigurationTemplateRequestRequestTypeDef",
    {
        "launchConfigurationTemplateID": str,
        "associatePublicIpAddress": NotRequired[bool],
        "bootMode": NotRequired[BootModeType],
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "enableMapAutoTagging": NotRequired[bool],
        "largeVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "mapAutoTaggingMpeID": NotRequired[str],
        "postLaunchActions": NotRequired[PostLaunchActionsTypeDef],
        "smallVolumeConf": NotRequired[LaunchTemplateDiskConfTypeDef],
        "smallVolumeMaxSize": NotRequired[int],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)
DescribeSourceServersResponseTypeDef = TypedDict(
    "DescribeSourceServersResponseTypeDef",
    {
        "items": List[SourceServerTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ParticipatingServerPaginatorTypeDef = TypedDict(
    "ParticipatingServerPaginatorTypeDef",
    {
        "sourceServerID": str,
        "launchStatus": NotRequired[LaunchStatusType],
        "launchedEc2InstanceID": NotRequired[str],
        "postLaunchActionsStatus": NotRequired[PostLaunchActionsStatusPaginatorTypeDef],
    },
)
DescribeLaunchConfigurationTemplatesResponsePaginatorTypeDef = TypedDict(
    "DescribeLaunchConfigurationTemplatesResponsePaginatorTypeDef",
    {
        "items": List[LaunchConfigurationTemplatePaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ParticipatingServerTypeDef = TypedDict(
    "ParticipatingServerTypeDef",
    {
        "sourceServerID": str,
        "launchStatus": NotRequired[LaunchStatusType],
        "launchedEc2InstanceID": NotRequired[str],
        "postLaunchActionsStatus": NotRequired[PostLaunchActionsStatusTypeDef],
    },
)
DescribeLaunchConfigurationTemplatesResponseTypeDef = TypedDict(
    "DescribeLaunchConfigurationTemplatesResponseTypeDef",
    {
        "items": List[LaunchConfigurationTemplateTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
JobPaginatorTypeDef = TypedDict(
    "JobPaginatorTypeDef",
    {
        "jobID": str,
        "arn": NotRequired[str],
        "creationDateTime": NotRequired[str],
        "endDateTime": NotRequired[str],
        "initiatedBy": NotRequired[InitiatedByType],
        "participatingServers": NotRequired[List[ParticipatingServerPaginatorTypeDef]],
        "status": NotRequired[JobStatusType],
        "tags": NotRequired[Dict[str, str]],
        "type": NotRequired[JobTypeType],
    },
)
JobTypeDef = TypedDict(
    "JobTypeDef",
    {
        "jobID": str,
        "arn": NotRequired[str],
        "creationDateTime": NotRequired[str],
        "endDateTime": NotRequired[str],
        "initiatedBy": NotRequired[InitiatedByType],
        "participatingServers": NotRequired[List[ParticipatingServerTypeDef]],
        "status": NotRequired[JobStatusType],
        "tags": NotRequired[Dict[str, str]],
        "type": NotRequired[JobTypeType],
    },
)
DescribeJobsResponsePaginatorTypeDef = TypedDict(
    "DescribeJobsResponsePaginatorTypeDef",
    {
        "items": List[JobPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeJobsResponseTypeDef = TypedDict(
    "DescribeJobsResponseTypeDef",
    {
        "items": List[JobTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartCutoverResponseTypeDef = TypedDict(
    "StartCutoverResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTestResponseTypeDef = TypedDict(
    "StartTestResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TerminateTargetInstancesResponseTypeDef = TypedDict(
    "TerminateTargetInstancesResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

"""
Type annotations for codebuild service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_codebuild/type_defs/)

Usage::

    ```python
    from mypy_boto3_codebuild.type_defs import BatchDeleteBuildsInputRequestTypeDef

    data: BatchDeleteBuildsInputRequestTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Sequence

from .literals import (
    ArtifactNamespaceType,
    ArtifactPackagingType,
    ArtifactsTypeType,
    AuthTypeType,
    BatchReportModeTypeType,
    BucketOwnerAccessType,
    BuildBatchPhaseTypeType,
    BuildPhaseTypeType,
    CacheModeType,
    CacheTypeType,
    ComputeTypeType,
    EnvironmentTypeType,
    EnvironmentVariableTypeType,
    FleetContextCodeType,
    FleetOverflowBehaviorType,
    FleetSortByTypeType,
    FleetStatusCodeType,
    ImagePullCredentialsTypeType,
    LanguageTypeType,
    LogsConfigStatusTypeType,
    PlatformTypeType,
    ProjectSortByTypeType,
    ProjectVisibilityTypeType,
    ReportCodeCoverageSortByTypeType,
    ReportExportConfigTypeType,
    ReportGroupSortByTypeType,
    ReportGroupStatusTypeType,
    ReportGroupTrendFieldTypeType,
    ReportPackagingTypeType,
    ReportStatusTypeType,
    ReportTypeType,
    RetryBuildBatchTypeType,
    ServerTypeType,
    SharedResourceSortByTypeType,
    SortOrderTypeType,
    SourceAuthTypeType,
    SourceTypeType,
    StatusTypeType,
    WebhookBuildTypeType,
    WebhookFilterTypeType,
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
    "BatchDeleteBuildsInputRequestTypeDef",
    "BuildNotDeletedTypeDef",
    "ResponseMetadataTypeDef",
    "BatchGetBuildBatchesInputRequestTypeDef",
    "BatchGetBuildsInputRequestTypeDef",
    "BatchGetFleetsInputRequestTypeDef",
    "BatchGetProjectsInputRequestTypeDef",
    "BatchGetReportGroupsInputRequestTypeDef",
    "BatchGetReportsInputRequestTypeDef",
    "BatchRestrictionsTypeDef",
    "BuildArtifactsTypeDef",
    "BuildBatchFilterTypeDef",
    "PhaseContextTypeDef",
    "ProjectCacheTypeDef",
    "ProjectFileSystemLocationTypeDef",
    "ProjectSourceVersionTypeDef",
    "VpcConfigTypeDef",
    "BuildStatusConfigTypeDef",
    "ResolvedArtifactTypeDef",
    "DebugSessionTypeDef",
    "ExportedEnvironmentVariableTypeDef",
    "NetworkInterfaceTypeDef",
    "CloudWatchLogsConfigTypeDef",
    "CodeCoverageReportSummaryTypeDef",
    "CodeCoverageTypeDef",
    "TagTypeDef",
    "ProjectArtifactsTypeDef",
    "WebhookFilterTypeDef",
    "DeleteBuildBatchInputRequestTypeDef",
    "DeleteFleetInputRequestTypeDef",
    "DeleteProjectInputRequestTypeDef",
    "DeleteReportGroupInputRequestTypeDef",
    "DeleteReportInputRequestTypeDef",
    "DeleteResourcePolicyInputRequestTypeDef",
    "DeleteSourceCredentialsInputRequestTypeDef",
    "DeleteWebhookInputRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeCodeCoveragesInputRequestTypeDef",
    "TestCaseFilterTypeDef",
    "TestCaseTypeDef",
    "EnvironmentImageTypeDef",
    "EnvironmentVariableTypeDef",
    "FleetStatusTypeDef",
    "GetReportGroupTrendInputRequestTypeDef",
    "ReportGroupTrendStatsTypeDef",
    "ReportWithRawDataTypeDef",
    "GetResourcePolicyInputRequestTypeDef",
    "GitSubmodulesConfigTypeDef",
    "ImportSourceCredentialsInputRequestTypeDef",
    "InvalidateProjectCacheInputRequestTypeDef",
    "ListBuildsForProjectInputRequestTypeDef",
    "ListBuildsInputRequestTypeDef",
    "ListFleetsInputRequestTypeDef",
    "ListProjectsInputRequestTypeDef",
    "ListReportGroupsInputRequestTypeDef",
    "ReportFilterTypeDef",
    "ListSharedProjectsInputRequestTypeDef",
    "ListSharedReportGroupsInputRequestTypeDef",
    "SourceCredentialsInfoTypeDef",
    "S3LogsConfigTypeDef",
    "ProjectBadgeTypeDef",
    "ProjectFleetTypeDef",
    "RegistryCredentialTypeDef",
    "SourceAuthTypeDef",
    "PutResourcePolicyInputRequestTypeDef",
    "S3ReportExportConfigTypeDef",
    "TestReportSummaryTypeDef",
    "RetryBuildBatchInputRequestTypeDef",
    "RetryBuildInputRequestTypeDef",
    "TargetTrackingScalingConfigurationTypeDef",
    "StopBuildBatchInputRequestTypeDef",
    "StopBuildInputRequestTypeDef",
    "UpdateProjectVisibilityInputRequestTypeDef",
    "BatchDeleteBuildsOutputTypeDef",
    "DeleteBuildBatchOutputTypeDef",
    "DeleteSourceCredentialsOutputTypeDef",
    "GetResourcePolicyOutputTypeDef",
    "ImportSourceCredentialsOutputTypeDef",
    "ListBuildBatchesForProjectOutputTypeDef",
    "ListBuildBatchesOutputTypeDef",
    "ListBuildsForProjectOutputTypeDef",
    "ListBuildsOutputTypeDef",
    "ListFleetsOutputTypeDef",
    "ListProjectsOutputTypeDef",
    "ListReportGroupsOutputTypeDef",
    "ListReportsForReportGroupOutputTypeDef",
    "ListReportsOutputTypeDef",
    "ListSharedProjectsOutputTypeDef",
    "ListSharedReportGroupsOutputTypeDef",
    "PutResourcePolicyOutputTypeDef",
    "UpdateProjectVisibilityOutputTypeDef",
    "ProjectBuildBatchConfigTypeDef",
    "ListBuildBatchesForProjectInputRequestTypeDef",
    "ListBuildBatchesInputRequestTypeDef",
    "BuildBatchPhaseTypeDef",
    "BuildPhaseTypeDef",
    "BuildSummaryTypeDef",
    "DescribeCodeCoveragesOutputTypeDef",
    "CreateWebhookInputRequestTypeDef",
    "UpdateWebhookInputRequestTypeDef",
    "WebhookTypeDef",
    "DescribeCodeCoveragesInputDescribeCodeCoveragesPaginateTypeDef",
    "ListBuildBatchesForProjectInputListBuildBatchesForProjectPaginateTypeDef",
    "ListBuildBatchesInputListBuildBatchesPaginateTypeDef",
    "ListBuildsForProjectInputListBuildsForProjectPaginateTypeDef",
    "ListBuildsInputListBuildsPaginateTypeDef",
    "ListProjectsInputListProjectsPaginateTypeDef",
    "ListReportGroupsInputListReportGroupsPaginateTypeDef",
    "ListSharedProjectsInputListSharedProjectsPaginateTypeDef",
    "ListSharedReportGroupsInputListSharedReportGroupsPaginateTypeDef",
    "DescribeTestCasesInputDescribeTestCasesPaginateTypeDef",
    "DescribeTestCasesInputRequestTypeDef",
    "DescribeTestCasesOutputTypeDef",
    "EnvironmentLanguageTypeDef",
    "GetReportGroupTrendOutputTypeDef",
    "ListReportsForReportGroupInputListReportsForReportGroupPaginateTypeDef",
    "ListReportsForReportGroupInputRequestTypeDef",
    "ListReportsInputListReportsPaginateTypeDef",
    "ListReportsInputRequestTypeDef",
    "ListSourceCredentialsOutputTypeDef",
    "LogsConfigTypeDef",
    "LogsLocationTypeDef",
    "ProjectEnvironmentTypeDef",
    "ProjectSourceTypeDef",
    "ReportExportConfigTypeDef",
    "ScalingConfigurationInputTypeDef",
    "ScalingConfigurationOutputTypeDef",
    "BuildGroupTypeDef",
    "CreateWebhookOutputTypeDef",
    "UpdateWebhookOutputTypeDef",
    "EnvironmentPlatformTypeDef",
    "BuildTypeDef",
    "CreateProjectInputRequestTypeDef",
    "ProjectTypeDef",
    "StartBuildBatchInputRequestTypeDef",
    "StartBuildInputRequestTypeDef",
    "UpdateProjectInputRequestTypeDef",
    "CreateReportGroupInputRequestTypeDef",
    "ReportGroupTypeDef",
    "ReportTypeDef",
    "UpdateReportGroupInputRequestTypeDef",
    "CreateFleetInputRequestTypeDef",
    "UpdateFleetInputRequestTypeDef",
    "FleetTypeDef",
    "BuildBatchTypeDef",
    "ListCuratedEnvironmentImagesOutputTypeDef",
    "BatchGetBuildsOutputTypeDef",
    "RetryBuildOutputTypeDef",
    "StartBuildOutputTypeDef",
    "StopBuildOutputTypeDef",
    "BatchGetProjectsOutputTypeDef",
    "CreateProjectOutputTypeDef",
    "UpdateProjectOutputTypeDef",
    "BatchGetReportGroupsOutputTypeDef",
    "CreateReportGroupOutputTypeDef",
    "UpdateReportGroupOutputTypeDef",
    "BatchGetReportsOutputTypeDef",
    "BatchGetFleetsOutputTypeDef",
    "CreateFleetOutputTypeDef",
    "UpdateFleetOutputTypeDef",
    "BatchGetBuildBatchesOutputTypeDef",
    "RetryBuildBatchOutputTypeDef",
    "StartBuildBatchOutputTypeDef",
    "StopBuildBatchOutputTypeDef",
)

BatchDeleteBuildsInputRequestTypeDef = TypedDict(
    "BatchDeleteBuildsInputRequestTypeDef",
    {
        "ids": Sequence[str],
    },
)
BuildNotDeletedTypeDef = TypedDict(
    "BuildNotDeletedTypeDef",
    {
        "id": NotRequired[str],
        "statusCode": NotRequired[str],
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
BatchGetBuildBatchesInputRequestTypeDef = TypedDict(
    "BatchGetBuildBatchesInputRequestTypeDef",
    {
        "ids": Sequence[str],
    },
)
BatchGetBuildsInputRequestTypeDef = TypedDict(
    "BatchGetBuildsInputRequestTypeDef",
    {
        "ids": Sequence[str],
    },
)
BatchGetFleetsInputRequestTypeDef = TypedDict(
    "BatchGetFleetsInputRequestTypeDef",
    {
        "names": Sequence[str],
    },
)
BatchGetProjectsInputRequestTypeDef = TypedDict(
    "BatchGetProjectsInputRequestTypeDef",
    {
        "names": Sequence[str],
    },
)
BatchGetReportGroupsInputRequestTypeDef = TypedDict(
    "BatchGetReportGroupsInputRequestTypeDef",
    {
        "reportGroupArns": Sequence[str],
    },
)
BatchGetReportsInputRequestTypeDef = TypedDict(
    "BatchGetReportsInputRequestTypeDef",
    {
        "reportArns": Sequence[str],
    },
)
BatchRestrictionsTypeDef = TypedDict(
    "BatchRestrictionsTypeDef",
    {
        "maximumBuildsAllowed": NotRequired[int],
        "computeTypesAllowed": NotRequired[List[str]],
    },
)
BuildArtifactsTypeDef = TypedDict(
    "BuildArtifactsTypeDef",
    {
        "location": NotRequired[str],
        "sha256sum": NotRequired[str],
        "md5sum": NotRequired[str],
        "overrideArtifactName": NotRequired[bool],
        "encryptionDisabled": NotRequired[bool],
        "artifactIdentifier": NotRequired[str],
        "bucketOwnerAccess": NotRequired[BucketOwnerAccessType],
    },
)
BuildBatchFilterTypeDef = TypedDict(
    "BuildBatchFilterTypeDef",
    {
        "status": NotRequired[StatusTypeType],
    },
)
PhaseContextTypeDef = TypedDict(
    "PhaseContextTypeDef",
    {
        "statusCode": NotRequired[str],
        "message": NotRequired[str],
    },
)
ProjectCacheTypeDef = TypedDict(
    "ProjectCacheTypeDef",
    {
        "type": CacheTypeType,
        "location": NotRequired[str],
        "modes": NotRequired[List[CacheModeType]],
    },
)
ProjectFileSystemLocationTypeDef = TypedDict(
    "ProjectFileSystemLocationTypeDef",
    {
        "type": NotRequired[Literal["EFS"]],
        "location": NotRequired[str],
        "mountPoint": NotRequired[str],
        "identifier": NotRequired[str],
        "mountOptions": NotRequired[str],
    },
)
ProjectSourceVersionTypeDef = TypedDict(
    "ProjectSourceVersionTypeDef",
    {
        "sourceIdentifier": str,
        "sourceVersion": str,
    },
)
VpcConfigTypeDef = TypedDict(
    "VpcConfigTypeDef",
    {
        "vpcId": NotRequired[str],
        "subnets": NotRequired[List[str]],
        "securityGroupIds": NotRequired[List[str]],
    },
)
BuildStatusConfigTypeDef = TypedDict(
    "BuildStatusConfigTypeDef",
    {
        "context": NotRequired[str],
        "targetUrl": NotRequired[str],
    },
)
ResolvedArtifactTypeDef = TypedDict(
    "ResolvedArtifactTypeDef",
    {
        "type": NotRequired[ArtifactsTypeType],
        "location": NotRequired[str],
        "identifier": NotRequired[str],
    },
)
DebugSessionTypeDef = TypedDict(
    "DebugSessionTypeDef",
    {
        "sessionEnabled": NotRequired[bool],
        "sessionTarget": NotRequired[str],
    },
)
ExportedEnvironmentVariableTypeDef = TypedDict(
    "ExportedEnvironmentVariableTypeDef",
    {
        "name": NotRequired[str],
        "value": NotRequired[str],
    },
)
NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "subnetId": NotRequired[str],
        "networkInterfaceId": NotRequired[str],
    },
)
CloudWatchLogsConfigTypeDef = TypedDict(
    "CloudWatchLogsConfigTypeDef",
    {
        "status": LogsConfigStatusTypeType,
        "groupName": NotRequired[str],
        "streamName": NotRequired[str],
    },
)
CodeCoverageReportSummaryTypeDef = TypedDict(
    "CodeCoverageReportSummaryTypeDef",
    {
        "lineCoveragePercentage": NotRequired[float],
        "linesCovered": NotRequired[int],
        "linesMissed": NotRequired[int],
        "branchCoveragePercentage": NotRequired[float],
        "branchesCovered": NotRequired[int],
        "branchesMissed": NotRequired[int],
    },
)
CodeCoverageTypeDef = TypedDict(
    "CodeCoverageTypeDef",
    {
        "id": NotRequired[str],
        "reportARN": NotRequired[str],
        "filePath": NotRequired[str],
        "lineCoveragePercentage": NotRequired[float],
        "linesCovered": NotRequired[int],
        "linesMissed": NotRequired[int],
        "branchCoveragePercentage": NotRequired[float],
        "branchesCovered": NotRequired[int],
        "branchesMissed": NotRequired[int],
        "expired": NotRequired[datetime],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": NotRequired[str],
        "value": NotRequired[str],
    },
)
ProjectArtifactsTypeDef = TypedDict(
    "ProjectArtifactsTypeDef",
    {
        "type": ArtifactsTypeType,
        "location": NotRequired[str],
        "path": NotRequired[str],
        "namespaceType": NotRequired[ArtifactNamespaceType],
        "name": NotRequired[str],
        "packaging": NotRequired[ArtifactPackagingType],
        "overrideArtifactName": NotRequired[bool],
        "encryptionDisabled": NotRequired[bool],
        "artifactIdentifier": NotRequired[str],
        "bucketOwnerAccess": NotRequired[BucketOwnerAccessType],
    },
)
WebhookFilterTypeDef = TypedDict(
    "WebhookFilterTypeDef",
    {
        "type": WebhookFilterTypeType,
        "pattern": str,
        "excludeMatchedPattern": NotRequired[bool],
    },
)
DeleteBuildBatchInputRequestTypeDef = TypedDict(
    "DeleteBuildBatchInputRequestTypeDef",
    {
        "id": str,
    },
)
DeleteFleetInputRequestTypeDef = TypedDict(
    "DeleteFleetInputRequestTypeDef",
    {
        "arn": str,
    },
)
DeleteProjectInputRequestTypeDef = TypedDict(
    "DeleteProjectInputRequestTypeDef",
    {
        "name": str,
    },
)
DeleteReportGroupInputRequestTypeDef = TypedDict(
    "DeleteReportGroupInputRequestTypeDef",
    {
        "arn": str,
        "deleteReports": NotRequired[bool],
    },
)
DeleteReportInputRequestTypeDef = TypedDict(
    "DeleteReportInputRequestTypeDef",
    {
        "arn": str,
    },
)
DeleteResourcePolicyInputRequestTypeDef = TypedDict(
    "DeleteResourcePolicyInputRequestTypeDef",
    {
        "resourceArn": str,
    },
)
DeleteSourceCredentialsInputRequestTypeDef = TypedDict(
    "DeleteSourceCredentialsInputRequestTypeDef",
    {
        "arn": str,
    },
)
DeleteWebhookInputRequestTypeDef = TypedDict(
    "DeleteWebhookInputRequestTypeDef",
    {
        "projectName": str,
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
DescribeCodeCoveragesInputRequestTypeDef = TypedDict(
    "DescribeCodeCoveragesInputRequestTypeDef",
    {
        "reportArn": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "sortOrder": NotRequired[SortOrderTypeType],
        "sortBy": NotRequired[ReportCodeCoverageSortByTypeType],
        "minLineCoveragePercentage": NotRequired[float],
        "maxLineCoveragePercentage": NotRequired[float],
    },
)
TestCaseFilterTypeDef = TypedDict(
    "TestCaseFilterTypeDef",
    {
        "status": NotRequired[str],
        "keyword": NotRequired[str],
    },
)
TestCaseTypeDef = TypedDict(
    "TestCaseTypeDef",
    {
        "reportArn": NotRequired[str],
        "testRawDataPath": NotRequired[str],
        "prefix": NotRequired[str],
        "name": NotRequired[str],
        "status": NotRequired[str],
        "durationInNanoSeconds": NotRequired[int],
        "message": NotRequired[str],
        "expired": NotRequired[datetime],
    },
)
EnvironmentImageTypeDef = TypedDict(
    "EnvironmentImageTypeDef",
    {
        "name": NotRequired[str],
        "description": NotRequired[str],
        "versions": NotRequired[List[str]],
    },
)
EnvironmentVariableTypeDef = TypedDict(
    "EnvironmentVariableTypeDef",
    {
        "name": str,
        "value": str,
        "type": NotRequired[EnvironmentVariableTypeType],
    },
)
FleetStatusTypeDef = TypedDict(
    "FleetStatusTypeDef",
    {
        "statusCode": NotRequired[FleetStatusCodeType],
        "context": NotRequired[FleetContextCodeType],
        "message": NotRequired[str],
    },
)
GetReportGroupTrendInputRequestTypeDef = TypedDict(
    "GetReportGroupTrendInputRequestTypeDef",
    {
        "reportGroupArn": str,
        "trendField": ReportGroupTrendFieldTypeType,
        "numOfReports": NotRequired[int],
    },
)
ReportGroupTrendStatsTypeDef = TypedDict(
    "ReportGroupTrendStatsTypeDef",
    {
        "average": NotRequired[str],
        "max": NotRequired[str],
        "min": NotRequired[str],
    },
)
ReportWithRawDataTypeDef = TypedDict(
    "ReportWithRawDataTypeDef",
    {
        "reportArn": NotRequired[str],
        "data": NotRequired[str],
    },
)
GetResourcePolicyInputRequestTypeDef = TypedDict(
    "GetResourcePolicyInputRequestTypeDef",
    {
        "resourceArn": str,
    },
)
GitSubmodulesConfigTypeDef = TypedDict(
    "GitSubmodulesConfigTypeDef",
    {
        "fetchSubmodules": bool,
    },
)
ImportSourceCredentialsInputRequestTypeDef = TypedDict(
    "ImportSourceCredentialsInputRequestTypeDef",
    {
        "token": str,
        "serverType": ServerTypeType,
        "authType": AuthTypeType,
        "username": NotRequired[str],
        "shouldOverwrite": NotRequired[bool],
    },
)
InvalidateProjectCacheInputRequestTypeDef = TypedDict(
    "InvalidateProjectCacheInputRequestTypeDef",
    {
        "projectName": str,
    },
)
ListBuildsForProjectInputRequestTypeDef = TypedDict(
    "ListBuildsForProjectInputRequestTypeDef",
    {
        "projectName": str,
        "sortOrder": NotRequired[SortOrderTypeType],
        "nextToken": NotRequired[str],
    },
)
ListBuildsInputRequestTypeDef = TypedDict(
    "ListBuildsInputRequestTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "nextToken": NotRequired[str],
    },
)
ListFleetsInputRequestTypeDef = TypedDict(
    "ListFleetsInputRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "sortOrder": NotRequired[SortOrderTypeType],
        "sortBy": NotRequired[FleetSortByTypeType],
    },
)
ListProjectsInputRequestTypeDef = TypedDict(
    "ListProjectsInputRequestTypeDef",
    {
        "sortBy": NotRequired[ProjectSortByTypeType],
        "sortOrder": NotRequired[SortOrderTypeType],
        "nextToken": NotRequired[str],
    },
)
ListReportGroupsInputRequestTypeDef = TypedDict(
    "ListReportGroupsInputRequestTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "sortBy": NotRequired[ReportGroupSortByTypeType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ReportFilterTypeDef = TypedDict(
    "ReportFilterTypeDef",
    {
        "status": NotRequired[ReportStatusTypeType],
    },
)
ListSharedProjectsInputRequestTypeDef = TypedDict(
    "ListSharedProjectsInputRequestTypeDef",
    {
        "sortBy": NotRequired[SharedResourceSortByTypeType],
        "sortOrder": NotRequired[SortOrderTypeType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListSharedReportGroupsInputRequestTypeDef = TypedDict(
    "ListSharedReportGroupsInputRequestTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "sortBy": NotRequired[SharedResourceSortByTypeType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
SourceCredentialsInfoTypeDef = TypedDict(
    "SourceCredentialsInfoTypeDef",
    {
        "arn": NotRequired[str],
        "serverType": NotRequired[ServerTypeType],
        "authType": NotRequired[AuthTypeType],
        "resource": NotRequired[str],
    },
)
S3LogsConfigTypeDef = TypedDict(
    "S3LogsConfigTypeDef",
    {
        "status": LogsConfigStatusTypeType,
        "location": NotRequired[str],
        "encryptionDisabled": NotRequired[bool],
        "bucketOwnerAccess": NotRequired[BucketOwnerAccessType],
    },
)
ProjectBadgeTypeDef = TypedDict(
    "ProjectBadgeTypeDef",
    {
        "badgeEnabled": NotRequired[bool],
        "badgeRequestUrl": NotRequired[str],
    },
)
ProjectFleetTypeDef = TypedDict(
    "ProjectFleetTypeDef",
    {
        "fleetArn": NotRequired[str],
    },
)
RegistryCredentialTypeDef = TypedDict(
    "RegistryCredentialTypeDef",
    {
        "credential": str,
        "credentialProvider": Literal["SECRETS_MANAGER"],
    },
)
SourceAuthTypeDef = TypedDict(
    "SourceAuthTypeDef",
    {
        "type": SourceAuthTypeType,
        "resource": NotRequired[str],
    },
)
PutResourcePolicyInputRequestTypeDef = TypedDict(
    "PutResourcePolicyInputRequestTypeDef",
    {
        "policy": str,
        "resourceArn": str,
    },
)
S3ReportExportConfigTypeDef = TypedDict(
    "S3ReportExportConfigTypeDef",
    {
        "bucket": NotRequired[str],
        "bucketOwner": NotRequired[str],
        "path": NotRequired[str],
        "packaging": NotRequired[ReportPackagingTypeType],
        "encryptionKey": NotRequired[str],
        "encryptionDisabled": NotRequired[bool],
    },
)
TestReportSummaryTypeDef = TypedDict(
    "TestReportSummaryTypeDef",
    {
        "total": int,
        "statusCounts": Dict[str, int],
        "durationInNanoSeconds": int,
    },
)
RetryBuildBatchInputRequestTypeDef = TypedDict(
    "RetryBuildBatchInputRequestTypeDef",
    {
        "id": NotRequired[str],
        "idempotencyToken": NotRequired[str],
        "retryType": NotRequired[RetryBuildBatchTypeType],
    },
)
RetryBuildInputRequestTypeDef = TypedDict(
    "RetryBuildInputRequestTypeDef",
    {
        "id": NotRequired[str],
        "idempotencyToken": NotRequired[str],
    },
)
TargetTrackingScalingConfigurationTypeDef = TypedDict(
    "TargetTrackingScalingConfigurationTypeDef",
    {
        "metricType": NotRequired[Literal["FLEET_UTILIZATION_RATE"]],
        "targetValue": NotRequired[float],
    },
)
StopBuildBatchInputRequestTypeDef = TypedDict(
    "StopBuildBatchInputRequestTypeDef",
    {
        "id": str,
    },
)
StopBuildInputRequestTypeDef = TypedDict(
    "StopBuildInputRequestTypeDef",
    {
        "id": str,
    },
)
UpdateProjectVisibilityInputRequestTypeDef = TypedDict(
    "UpdateProjectVisibilityInputRequestTypeDef",
    {
        "projectArn": str,
        "projectVisibility": ProjectVisibilityTypeType,
        "resourceAccessRole": NotRequired[str],
    },
)
BatchDeleteBuildsOutputTypeDef = TypedDict(
    "BatchDeleteBuildsOutputTypeDef",
    {
        "buildsDeleted": List[str],
        "buildsNotDeleted": List[BuildNotDeletedTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteBuildBatchOutputTypeDef = TypedDict(
    "DeleteBuildBatchOutputTypeDef",
    {
        "statusCode": str,
        "buildsDeleted": List[str],
        "buildsNotDeleted": List[BuildNotDeletedTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteSourceCredentialsOutputTypeDef = TypedDict(
    "DeleteSourceCredentialsOutputTypeDef",
    {
        "arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetResourcePolicyOutputTypeDef = TypedDict(
    "GetResourcePolicyOutputTypeDef",
    {
        "policy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportSourceCredentialsOutputTypeDef = TypedDict(
    "ImportSourceCredentialsOutputTypeDef",
    {
        "arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBuildBatchesForProjectOutputTypeDef = TypedDict(
    "ListBuildBatchesForProjectOutputTypeDef",
    {
        "ids": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBuildBatchesOutputTypeDef = TypedDict(
    "ListBuildBatchesOutputTypeDef",
    {
        "ids": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBuildsForProjectOutputTypeDef = TypedDict(
    "ListBuildsForProjectOutputTypeDef",
    {
        "ids": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBuildsOutputTypeDef = TypedDict(
    "ListBuildsOutputTypeDef",
    {
        "ids": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListFleetsOutputTypeDef = TypedDict(
    "ListFleetsOutputTypeDef",
    {
        "nextToken": str,
        "fleets": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListProjectsOutputTypeDef = TypedDict(
    "ListProjectsOutputTypeDef",
    {
        "nextToken": str,
        "projects": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListReportGroupsOutputTypeDef = TypedDict(
    "ListReportGroupsOutputTypeDef",
    {
        "nextToken": str,
        "reportGroups": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListReportsForReportGroupOutputTypeDef = TypedDict(
    "ListReportsForReportGroupOutputTypeDef",
    {
        "nextToken": str,
        "reports": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListReportsOutputTypeDef = TypedDict(
    "ListReportsOutputTypeDef",
    {
        "nextToken": str,
        "reports": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSharedProjectsOutputTypeDef = TypedDict(
    "ListSharedProjectsOutputTypeDef",
    {
        "nextToken": str,
        "projects": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSharedReportGroupsOutputTypeDef = TypedDict(
    "ListSharedReportGroupsOutputTypeDef",
    {
        "nextToken": str,
        "reportGroups": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutResourcePolicyOutputTypeDef = TypedDict(
    "PutResourcePolicyOutputTypeDef",
    {
        "resourceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateProjectVisibilityOutputTypeDef = TypedDict(
    "UpdateProjectVisibilityOutputTypeDef",
    {
        "projectArn": str,
        "publicProjectAlias": str,
        "projectVisibility": ProjectVisibilityTypeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ProjectBuildBatchConfigTypeDef = TypedDict(
    "ProjectBuildBatchConfigTypeDef",
    {
        "serviceRole": NotRequired[str],
        "combineArtifacts": NotRequired[bool],
        "restrictions": NotRequired[BatchRestrictionsTypeDef],
        "timeoutInMins": NotRequired[int],
        "batchReportMode": NotRequired[BatchReportModeTypeType],
    },
)
ListBuildBatchesForProjectInputRequestTypeDef = TypedDict(
    "ListBuildBatchesForProjectInputRequestTypeDef",
    {
        "projectName": NotRequired[str],
        "filter": NotRequired[BuildBatchFilterTypeDef],
        "maxResults": NotRequired[int],
        "sortOrder": NotRequired[SortOrderTypeType],
        "nextToken": NotRequired[str],
    },
)
ListBuildBatchesInputRequestTypeDef = TypedDict(
    "ListBuildBatchesInputRequestTypeDef",
    {
        "filter": NotRequired[BuildBatchFilterTypeDef],
        "maxResults": NotRequired[int],
        "sortOrder": NotRequired[SortOrderTypeType],
        "nextToken": NotRequired[str],
    },
)
BuildBatchPhaseTypeDef = TypedDict(
    "BuildBatchPhaseTypeDef",
    {
        "phaseType": NotRequired[BuildBatchPhaseTypeType],
        "phaseStatus": NotRequired[StatusTypeType],
        "startTime": NotRequired[datetime],
        "endTime": NotRequired[datetime],
        "durationInSeconds": NotRequired[int],
        "contexts": NotRequired[List[PhaseContextTypeDef]],
    },
)
BuildPhaseTypeDef = TypedDict(
    "BuildPhaseTypeDef",
    {
        "phaseType": NotRequired[BuildPhaseTypeType],
        "phaseStatus": NotRequired[StatusTypeType],
        "startTime": NotRequired[datetime],
        "endTime": NotRequired[datetime],
        "durationInSeconds": NotRequired[int],
        "contexts": NotRequired[List[PhaseContextTypeDef]],
    },
)
BuildSummaryTypeDef = TypedDict(
    "BuildSummaryTypeDef",
    {
        "arn": NotRequired[str],
        "requestedOn": NotRequired[datetime],
        "buildStatus": NotRequired[StatusTypeType],
        "primaryArtifact": NotRequired[ResolvedArtifactTypeDef],
        "secondaryArtifacts": NotRequired[List[ResolvedArtifactTypeDef]],
    },
)
DescribeCodeCoveragesOutputTypeDef = TypedDict(
    "DescribeCodeCoveragesOutputTypeDef",
    {
        "nextToken": str,
        "codeCoverages": List[CodeCoverageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateWebhookInputRequestTypeDef = TypedDict(
    "CreateWebhookInputRequestTypeDef",
    {
        "projectName": str,
        "branchFilter": NotRequired[str],
        "filterGroups": NotRequired[Sequence[Sequence[WebhookFilterTypeDef]]],
        "buildType": NotRequired[WebhookBuildTypeType],
    },
)
UpdateWebhookInputRequestTypeDef = TypedDict(
    "UpdateWebhookInputRequestTypeDef",
    {
        "projectName": str,
        "branchFilter": NotRequired[str],
        "rotateSecret": NotRequired[bool],
        "filterGroups": NotRequired[Sequence[Sequence[WebhookFilterTypeDef]]],
        "buildType": NotRequired[WebhookBuildTypeType],
    },
)
WebhookTypeDef = TypedDict(
    "WebhookTypeDef",
    {
        "url": NotRequired[str],
        "payloadUrl": NotRequired[str],
        "secret": NotRequired[str],
        "branchFilter": NotRequired[str],
        "filterGroups": NotRequired[List[List[WebhookFilterTypeDef]]],
        "buildType": NotRequired[WebhookBuildTypeType],
        "lastModifiedSecret": NotRequired[datetime],
    },
)
DescribeCodeCoveragesInputDescribeCodeCoveragesPaginateTypeDef = TypedDict(
    "DescribeCodeCoveragesInputDescribeCodeCoveragesPaginateTypeDef",
    {
        "reportArn": str,
        "sortOrder": NotRequired[SortOrderTypeType],
        "sortBy": NotRequired[ReportCodeCoverageSortByTypeType],
        "minLineCoveragePercentage": NotRequired[float],
        "maxLineCoveragePercentage": NotRequired[float],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListBuildBatchesForProjectInputListBuildBatchesForProjectPaginateTypeDef = TypedDict(
    "ListBuildBatchesForProjectInputListBuildBatchesForProjectPaginateTypeDef",
    {
        "projectName": NotRequired[str],
        "filter": NotRequired[BuildBatchFilterTypeDef],
        "sortOrder": NotRequired[SortOrderTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListBuildBatchesInputListBuildBatchesPaginateTypeDef = TypedDict(
    "ListBuildBatchesInputListBuildBatchesPaginateTypeDef",
    {
        "filter": NotRequired[BuildBatchFilterTypeDef],
        "sortOrder": NotRequired[SortOrderTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListBuildsForProjectInputListBuildsForProjectPaginateTypeDef = TypedDict(
    "ListBuildsForProjectInputListBuildsForProjectPaginateTypeDef",
    {
        "projectName": str,
        "sortOrder": NotRequired[SortOrderTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListBuildsInputListBuildsPaginateTypeDef = TypedDict(
    "ListBuildsInputListBuildsPaginateTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListProjectsInputListProjectsPaginateTypeDef = TypedDict(
    "ListProjectsInputListProjectsPaginateTypeDef",
    {
        "sortBy": NotRequired[ProjectSortByTypeType],
        "sortOrder": NotRequired[SortOrderTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListReportGroupsInputListReportGroupsPaginateTypeDef = TypedDict(
    "ListReportGroupsInputListReportGroupsPaginateTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "sortBy": NotRequired[ReportGroupSortByTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSharedProjectsInputListSharedProjectsPaginateTypeDef = TypedDict(
    "ListSharedProjectsInputListSharedProjectsPaginateTypeDef",
    {
        "sortBy": NotRequired[SharedResourceSortByTypeType],
        "sortOrder": NotRequired[SortOrderTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSharedReportGroupsInputListSharedReportGroupsPaginateTypeDef = TypedDict(
    "ListSharedReportGroupsInputListSharedReportGroupsPaginateTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "sortBy": NotRequired[SharedResourceSortByTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeTestCasesInputDescribeTestCasesPaginateTypeDef = TypedDict(
    "DescribeTestCasesInputDescribeTestCasesPaginateTypeDef",
    {
        "reportArn": str,
        "filter": NotRequired[TestCaseFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeTestCasesInputRequestTypeDef = TypedDict(
    "DescribeTestCasesInputRequestTypeDef",
    {
        "reportArn": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "filter": NotRequired[TestCaseFilterTypeDef],
    },
)
DescribeTestCasesOutputTypeDef = TypedDict(
    "DescribeTestCasesOutputTypeDef",
    {
        "nextToken": str,
        "testCases": List[TestCaseTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EnvironmentLanguageTypeDef = TypedDict(
    "EnvironmentLanguageTypeDef",
    {
        "language": NotRequired[LanguageTypeType],
        "images": NotRequired[List[EnvironmentImageTypeDef]],
    },
)
GetReportGroupTrendOutputTypeDef = TypedDict(
    "GetReportGroupTrendOutputTypeDef",
    {
        "stats": ReportGroupTrendStatsTypeDef,
        "rawData": List[ReportWithRawDataTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListReportsForReportGroupInputListReportsForReportGroupPaginateTypeDef = TypedDict(
    "ListReportsForReportGroupInputListReportsForReportGroupPaginateTypeDef",
    {
        "reportGroupArn": str,
        "sortOrder": NotRequired[SortOrderTypeType],
        "filter": NotRequired[ReportFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListReportsForReportGroupInputRequestTypeDef = TypedDict(
    "ListReportsForReportGroupInputRequestTypeDef",
    {
        "reportGroupArn": str,
        "nextToken": NotRequired[str],
        "sortOrder": NotRequired[SortOrderTypeType],
        "maxResults": NotRequired[int],
        "filter": NotRequired[ReportFilterTypeDef],
    },
)
ListReportsInputListReportsPaginateTypeDef = TypedDict(
    "ListReportsInputListReportsPaginateTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "filter": NotRequired[ReportFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListReportsInputRequestTypeDef = TypedDict(
    "ListReportsInputRequestTypeDef",
    {
        "sortOrder": NotRequired[SortOrderTypeType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "filter": NotRequired[ReportFilterTypeDef],
    },
)
ListSourceCredentialsOutputTypeDef = TypedDict(
    "ListSourceCredentialsOutputTypeDef",
    {
        "sourceCredentialsInfos": List[SourceCredentialsInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LogsConfigTypeDef = TypedDict(
    "LogsConfigTypeDef",
    {
        "cloudWatchLogs": NotRequired[CloudWatchLogsConfigTypeDef],
        "s3Logs": NotRequired[S3LogsConfigTypeDef],
    },
)
LogsLocationTypeDef = TypedDict(
    "LogsLocationTypeDef",
    {
        "groupName": NotRequired[str],
        "streamName": NotRequired[str],
        "deepLink": NotRequired[str],
        "s3DeepLink": NotRequired[str],
        "cloudWatchLogsArn": NotRequired[str],
        "s3LogsArn": NotRequired[str],
        "cloudWatchLogs": NotRequired[CloudWatchLogsConfigTypeDef],
        "s3Logs": NotRequired[S3LogsConfigTypeDef],
    },
)
ProjectEnvironmentTypeDef = TypedDict(
    "ProjectEnvironmentTypeDef",
    {
        "type": EnvironmentTypeType,
        "image": str,
        "computeType": ComputeTypeType,
        "fleet": NotRequired[ProjectFleetTypeDef],
        "environmentVariables": NotRequired[List[EnvironmentVariableTypeDef]],
        "privilegedMode": NotRequired[bool],
        "certificate": NotRequired[str],
        "registryCredential": NotRequired[RegistryCredentialTypeDef],
        "imagePullCredentialsType": NotRequired[ImagePullCredentialsTypeType],
    },
)
ProjectSourceTypeDef = TypedDict(
    "ProjectSourceTypeDef",
    {
        "type": SourceTypeType,
        "location": NotRequired[str],
        "gitCloneDepth": NotRequired[int],
        "gitSubmodulesConfig": NotRequired[GitSubmodulesConfigTypeDef],
        "buildspec": NotRequired[str],
        "auth": NotRequired[SourceAuthTypeDef],
        "reportBuildStatus": NotRequired[bool],
        "buildStatusConfig": NotRequired[BuildStatusConfigTypeDef],
        "insecureSsl": NotRequired[bool],
        "sourceIdentifier": NotRequired[str],
    },
)
ReportExportConfigTypeDef = TypedDict(
    "ReportExportConfigTypeDef",
    {
        "exportConfigType": NotRequired[ReportExportConfigTypeType],
        "s3Destination": NotRequired[S3ReportExportConfigTypeDef],
    },
)
ScalingConfigurationInputTypeDef = TypedDict(
    "ScalingConfigurationInputTypeDef",
    {
        "scalingType": NotRequired[Literal["TARGET_TRACKING_SCALING"]],
        "targetTrackingScalingConfigs": NotRequired[
            Sequence[TargetTrackingScalingConfigurationTypeDef]
        ],
        "maxCapacity": NotRequired[int],
    },
)
ScalingConfigurationOutputTypeDef = TypedDict(
    "ScalingConfigurationOutputTypeDef",
    {
        "scalingType": NotRequired[Literal["TARGET_TRACKING_SCALING"]],
        "targetTrackingScalingConfigs": NotRequired[
            List[TargetTrackingScalingConfigurationTypeDef]
        ],
        "maxCapacity": NotRequired[int],
        "desiredCapacity": NotRequired[int],
    },
)
BuildGroupTypeDef = TypedDict(
    "BuildGroupTypeDef",
    {
        "identifier": NotRequired[str],
        "dependsOn": NotRequired[List[str]],
        "ignoreFailure": NotRequired[bool],
        "currentBuildSummary": NotRequired[BuildSummaryTypeDef],
        "priorBuildSummaryList": NotRequired[List[BuildSummaryTypeDef]],
    },
)
CreateWebhookOutputTypeDef = TypedDict(
    "CreateWebhookOutputTypeDef",
    {
        "webhook": WebhookTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateWebhookOutputTypeDef = TypedDict(
    "UpdateWebhookOutputTypeDef",
    {
        "webhook": WebhookTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EnvironmentPlatformTypeDef = TypedDict(
    "EnvironmentPlatformTypeDef",
    {
        "platform": NotRequired[PlatformTypeType],
        "languages": NotRequired[List[EnvironmentLanguageTypeDef]],
    },
)
BuildTypeDef = TypedDict(
    "BuildTypeDef",
    {
        "id": NotRequired[str],
        "arn": NotRequired[str],
        "buildNumber": NotRequired[int],
        "startTime": NotRequired[datetime],
        "endTime": NotRequired[datetime],
        "currentPhase": NotRequired[str],
        "buildStatus": NotRequired[StatusTypeType],
        "sourceVersion": NotRequired[str],
        "resolvedSourceVersion": NotRequired[str],
        "projectName": NotRequired[str],
        "phases": NotRequired[List[BuildPhaseTypeDef]],
        "source": NotRequired[ProjectSourceTypeDef],
        "secondarySources": NotRequired[List[ProjectSourceTypeDef]],
        "secondarySourceVersions": NotRequired[List[ProjectSourceVersionTypeDef]],
        "artifacts": NotRequired[BuildArtifactsTypeDef],
        "secondaryArtifacts": NotRequired[List[BuildArtifactsTypeDef]],
        "cache": NotRequired[ProjectCacheTypeDef],
        "environment": NotRequired[ProjectEnvironmentTypeDef],
        "serviceRole": NotRequired[str],
        "logs": NotRequired[LogsLocationTypeDef],
        "timeoutInMinutes": NotRequired[int],
        "queuedTimeoutInMinutes": NotRequired[int],
        "buildComplete": NotRequired[bool],
        "initiator": NotRequired[str],
        "vpcConfig": NotRequired[VpcConfigTypeDef],
        "networkInterface": NotRequired[NetworkInterfaceTypeDef],
        "encryptionKey": NotRequired[str],
        "exportedEnvironmentVariables": NotRequired[List[ExportedEnvironmentVariableTypeDef]],
        "reportArns": NotRequired[List[str]],
        "fileSystemLocations": NotRequired[List[ProjectFileSystemLocationTypeDef]],
        "debugSession": NotRequired[DebugSessionTypeDef],
        "buildBatchArn": NotRequired[str],
    },
)
CreateProjectInputRequestTypeDef = TypedDict(
    "CreateProjectInputRequestTypeDef",
    {
        "name": str,
        "source": ProjectSourceTypeDef,
        "artifacts": ProjectArtifactsTypeDef,
        "environment": ProjectEnvironmentTypeDef,
        "serviceRole": str,
        "description": NotRequired[str],
        "secondarySources": NotRequired[Sequence[ProjectSourceTypeDef]],
        "sourceVersion": NotRequired[str],
        "secondarySourceVersions": NotRequired[Sequence[ProjectSourceVersionTypeDef]],
        "secondaryArtifacts": NotRequired[Sequence[ProjectArtifactsTypeDef]],
        "cache": NotRequired[ProjectCacheTypeDef],
        "timeoutInMinutes": NotRequired[int],
        "queuedTimeoutInMinutes": NotRequired[int],
        "encryptionKey": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "vpcConfig": NotRequired[VpcConfigTypeDef],
        "badgeEnabled": NotRequired[bool],
        "logsConfig": NotRequired[LogsConfigTypeDef],
        "fileSystemLocations": NotRequired[Sequence[ProjectFileSystemLocationTypeDef]],
        "buildBatchConfig": NotRequired[ProjectBuildBatchConfigTypeDef],
        "concurrentBuildLimit": NotRequired[int],
    },
)
ProjectTypeDef = TypedDict(
    "ProjectTypeDef",
    {
        "name": NotRequired[str],
        "arn": NotRequired[str],
        "description": NotRequired[str],
        "source": NotRequired[ProjectSourceTypeDef],
        "secondarySources": NotRequired[List[ProjectSourceTypeDef]],
        "sourceVersion": NotRequired[str],
        "secondarySourceVersions": NotRequired[List[ProjectSourceVersionTypeDef]],
        "artifacts": NotRequired[ProjectArtifactsTypeDef],
        "secondaryArtifacts": NotRequired[List[ProjectArtifactsTypeDef]],
        "cache": NotRequired[ProjectCacheTypeDef],
        "environment": NotRequired[ProjectEnvironmentTypeDef],
        "serviceRole": NotRequired[str],
        "timeoutInMinutes": NotRequired[int],
        "queuedTimeoutInMinutes": NotRequired[int],
        "encryptionKey": NotRequired[str],
        "tags": NotRequired[List[TagTypeDef]],
        "created": NotRequired[datetime],
        "lastModified": NotRequired[datetime],
        "webhook": NotRequired[WebhookTypeDef],
        "vpcConfig": NotRequired[VpcConfigTypeDef],
        "badge": NotRequired[ProjectBadgeTypeDef],
        "logsConfig": NotRequired[LogsConfigTypeDef],
        "fileSystemLocations": NotRequired[List[ProjectFileSystemLocationTypeDef]],
        "buildBatchConfig": NotRequired[ProjectBuildBatchConfigTypeDef],
        "concurrentBuildLimit": NotRequired[int],
        "projectVisibility": NotRequired[ProjectVisibilityTypeType],
        "publicProjectAlias": NotRequired[str],
        "resourceAccessRole": NotRequired[str],
    },
)
StartBuildBatchInputRequestTypeDef = TypedDict(
    "StartBuildBatchInputRequestTypeDef",
    {
        "projectName": str,
        "secondarySourcesOverride": NotRequired[Sequence[ProjectSourceTypeDef]],
        "secondarySourcesVersionOverride": NotRequired[Sequence[ProjectSourceVersionTypeDef]],
        "sourceVersion": NotRequired[str],
        "artifactsOverride": NotRequired[ProjectArtifactsTypeDef],
        "secondaryArtifactsOverride": NotRequired[Sequence[ProjectArtifactsTypeDef]],
        "environmentVariablesOverride": NotRequired[Sequence[EnvironmentVariableTypeDef]],
        "sourceTypeOverride": NotRequired[SourceTypeType],
        "sourceLocationOverride": NotRequired[str],
        "sourceAuthOverride": NotRequired[SourceAuthTypeDef],
        "gitCloneDepthOverride": NotRequired[int],
        "gitSubmodulesConfigOverride": NotRequired[GitSubmodulesConfigTypeDef],
        "buildspecOverride": NotRequired[str],
        "insecureSslOverride": NotRequired[bool],
        "reportBuildBatchStatusOverride": NotRequired[bool],
        "environmentTypeOverride": NotRequired[EnvironmentTypeType],
        "imageOverride": NotRequired[str],
        "computeTypeOverride": NotRequired[ComputeTypeType],
        "certificateOverride": NotRequired[str],
        "cacheOverride": NotRequired[ProjectCacheTypeDef],
        "serviceRoleOverride": NotRequired[str],
        "privilegedModeOverride": NotRequired[bool],
        "buildTimeoutInMinutesOverride": NotRequired[int],
        "queuedTimeoutInMinutesOverride": NotRequired[int],
        "encryptionKeyOverride": NotRequired[str],
        "idempotencyToken": NotRequired[str],
        "logsConfigOverride": NotRequired[LogsConfigTypeDef],
        "registryCredentialOverride": NotRequired[RegistryCredentialTypeDef],
        "imagePullCredentialsTypeOverride": NotRequired[ImagePullCredentialsTypeType],
        "buildBatchConfigOverride": NotRequired[ProjectBuildBatchConfigTypeDef],
        "debugSessionEnabled": NotRequired[bool],
    },
)
StartBuildInputRequestTypeDef = TypedDict(
    "StartBuildInputRequestTypeDef",
    {
        "projectName": str,
        "secondarySourcesOverride": NotRequired[Sequence[ProjectSourceTypeDef]],
        "secondarySourcesVersionOverride": NotRequired[Sequence[ProjectSourceVersionTypeDef]],
        "sourceVersion": NotRequired[str],
        "artifactsOverride": NotRequired[ProjectArtifactsTypeDef],
        "secondaryArtifactsOverride": NotRequired[Sequence[ProjectArtifactsTypeDef]],
        "environmentVariablesOverride": NotRequired[Sequence[EnvironmentVariableTypeDef]],
        "sourceTypeOverride": NotRequired[SourceTypeType],
        "sourceLocationOverride": NotRequired[str],
        "sourceAuthOverride": NotRequired[SourceAuthTypeDef],
        "gitCloneDepthOverride": NotRequired[int],
        "gitSubmodulesConfigOverride": NotRequired[GitSubmodulesConfigTypeDef],
        "buildspecOverride": NotRequired[str],
        "insecureSslOverride": NotRequired[bool],
        "reportBuildStatusOverride": NotRequired[bool],
        "buildStatusConfigOverride": NotRequired[BuildStatusConfigTypeDef],
        "environmentTypeOverride": NotRequired[EnvironmentTypeType],
        "imageOverride": NotRequired[str],
        "computeTypeOverride": NotRequired[ComputeTypeType],
        "certificateOverride": NotRequired[str],
        "cacheOverride": NotRequired[ProjectCacheTypeDef],
        "serviceRoleOverride": NotRequired[str],
        "privilegedModeOverride": NotRequired[bool],
        "timeoutInMinutesOverride": NotRequired[int],
        "queuedTimeoutInMinutesOverride": NotRequired[int],
        "encryptionKeyOverride": NotRequired[str],
        "idempotencyToken": NotRequired[str],
        "logsConfigOverride": NotRequired[LogsConfigTypeDef],
        "registryCredentialOverride": NotRequired[RegistryCredentialTypeDef],
        "imagePullCredentialsTypeOverride": NotRequired[ImagePullCredentialsTypeType],
        "debugSessionEnabled": NotRequired[bool],
        "fleetOverride": NotRequired[ProjectFleetTypeDef],
    },
)
UpdateProjectInputRequestTypeDef = TypedDict(
    "UpdateProjectInputRequestTypeDef",
    {
        "name": str,
        "description": NotRequired[str],
        "source": NotRequired[ProjectSourceTypeDef],
        "secondarySources": NotRequired[Sequence[ProjectSourceTypeDef]],
        "sourceVersion": NotRequired[str],
        "secondarySourceVersions": NotRequired[Sequence[ProjectSourceVersionTypeDef]],
        "artifacts": NotRequired[ProjectArtifactsTypeDef],
        "secondaryArtifacts": NotRequired[Sequence[ProjectArtifactsTypeDef]],
        "cache": NotRequired[ProjectCacheTypeDef],
        "environment": NotRequired[ProjectEnvironmentTypeDef],
        "serviceRole": NotRequired[str],
        "timeoutInMinutes": NotRequired[int],
        "queuedTimeoutInMinutes": NotRequired[int],
        "encryptionKey": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "vpcConfig": NotRequired[VpcConfigTypeDef],
        "badgeEnabled": NotRequired[bool],
        "logsConfig": NotRequired[LogsConfigTypeDef],
        "fileSystemLocations": NotRequired[Sequence[ProjectFileSystemLocationTypeDef]],
        "buildBatchConfig": NotRequired[ProjectBuildBatchConfigTypeDef],
        "concurrentBuildLimit": NotRequired[int],
    },
)
CreateReportGroupInputRequestTypeDef = TypedDict(
    "CreateReportGroupInputRequestTypeDef",
    {
        "name": str,
        "type": ReportTypeType,
        "exportConfig": ReportExportConfigTypeDef,
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ReportGroupTypeDef = TypedDict(
    "ReportGroupTypeDef",
    {
        "arn": NotRequired[str],
        "name": NotRequired[str],
        "type": NotRequired[ReportTypeType],
        "exportConfig": NotRequired[ReportExportConfigTypeDef],
        "created": NotRequired[datetime],
        "lastModified": NotRequired[datetime],
        "tags": NotRequired[List[TagTypeDef]],
        "status": NotRequired[ReportGroupStatusTypeType],
    },
)
ReportTypeDef = TypedDict(
    "ReportTypeDef",
    {
        "arn": NotRequired[str],
        "type": NotRequired[ReportTypeType],
        "name": NotRequired[str],
        "reportGroupArn": NotRequired[str],
        "executionId": NotRequired[str],
        "status": NotRequired[ReportStatusTypeType],
        "created": NotRequired[datetime],
        "expired": NotRequired[datetime],
        "exportConfig": NotRequired[ReportExportConfigTypeDef],
        "truncated": NotRequired[bool],
        "testSummary": NotRequired[TestReportSummaryTypeDef],
        "codeCoverageSummary": NotRequired[CodeCoverageReportSummaryTypeDef],
    },
)
UpdateReportGroupInputRequestTypeDef = TypedDict(
    "UpdateReportGroupInputRequestTypeDef",
    {
        "arn": str,
        "exportConfig": NotRequired[ReportExportConfigTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateFleetInputRequestTypeDef = TypedDict(
    "CreateFleetInputRequestTypeDef",
    {
        "name": str,
        "baseCapacity": int,
        "environmentType": EnvironmentTypeType,
        "computeType": ComputeTypeType,
        "scalingConfiguration": NotRequired[ScalingConfigurationInputTypeDef],
        "overflowBehavior": NotRequired[FleetOverflowBehaviorType],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateFleetInputRequestTypeDef = TypedDict(
    "UpdateFleetInputRequestTypeDef",
    {
        "arn": str,
        "baseCapacity": NotRequired[int],
        "environmentType": NotRequired[EnvironmentTypeType],
        "computeType": NotRequired[ComputeTypeType],
        "scalingConfiguration": NotRequired[ScalingConfigurationInputTypeDef],
        "overflowBehavior": NotRequired[FleetOverflowBehaviorType],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
FleetTypeDef = TypedDict(
    "FleetTypeDef",
    {
        "arn": NotRequired[str],
        "name": NotRequired[str],
        "id": NotRequired[str],
        "created": NotRequired[datetime],
        "lastModified": NotRequired[datetime],
        "status": NotRequired[FleetStatusTypeDef],
        "baseCapacity": NotRequired[int],
        "environmentType": NotRequired[EnvironmentTypeType],
        "computeType": NotRequired[ComputeTypeType],
        "scalingConfiguration": NotRequired[ScalingConfigurationOutputTypeDef],
        "overflowBehavior": NotRequired[FleetOverflowBehaviorType],
        "tags": NotRequired[List[TagTypeDef]],
    },
)
BuildBatchTypeDef = TypedDict(
    "BuildBatchTypeDef",
    {
        "id": NotRequired[str],
        "arn": NotRequired[str],
        "startTime": NotRequired[datetime],
        "endTime": NotRequired[datetime],
        "currentPhase": NotRequired[str],
        "buildBatchStatus": NotRequired[StatusTypeType],
        "sourceVersion": NotRequired[str],
        "resolvedSourceVersion": NotRequired[str],
        "projectName": NotRequired[str],
        "phases": NotRequired[List[BuildBatchPhaseTypeDef]],
        "source": NotRequired[ProjectSourceTypeDef],
        "secondarySources": NotRequired[List[ProjectSourceTypeDef]],
        "secondarySourceVersions": NotRequired[List[ProjectSourceVersionTypeDef]],
        "artifacts": NotRequired[BuildArtifactsTypeDef],
        "secondaryArtifacts": NotRequired[List[BuildArtifactsTypeDef]],
        "cache": NotRequired[ProjectCacheTypeDef],
        "environment": NotRequired[ProjectEnvironmentTypeDef],
        "serviceRole": NotRequired[str],
        "logConfig": NotRequired[LogsConfigTypeDef],
        "buildTimeoutInMinutes": NotRequired[int],
        "queuedTimeoutInMinutes": NotRequired[int],
        "complete": NotRequired[bool],
        "initiator": NotRequired[str],
        "vpcConfig": NotRequired[VpcConfigTypeDef],
        "encryptionKey": NotRequired[str],
        "buildBatchNumber": NotRequired[int],
        "fileSystemLocations": NotRequired[List[ProjectFileSystemLocationTypeDef]],
        "buildBatchConfig": NotRequired[ProjectBuildBatchConfigTypeDef],
        "buildGroups": NotRequired[List[BuildGroupTypeDef]],
        "debugSessionEnabled": NotRequired[bool],
    },
)
ListCuratedEnvironmentImagesOutputTypeDef = TypedDict(
    "ListCuratedEnvironmentImagesOutputTypeDef",
    {
        "platforms": List[EnvironmentPlatformTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetBuildsOutputTypeDef = TypedDict(
    "BatchGetBuildsOutputTypeDef",
    {
        "builds": List[BuildTypeDef],
        "buildsNotFound": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RetryBuildOutputTypeDef = TypedDict(
    "RetryBuildOutputTypeDef",
    {
        "build": BuildTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartBuildOutputTypeDef = TypedDict(
    "StartBuildOutputTypeDef",
    {
        "build": BuildTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopBuildOutputTypeDef = TypedDict(
    "StopBuildOutputTypeDef",
    {
        "build": BuildTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetProjectsOutputTypeDef = TypedDict(
    "BatchGetProjectsOutputTypeDef",
    {
        "projects": List[ProjectTypeDef],
        "projectsNotFound": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProjectOutputTypeDef = TypedDict(
    "CreateProjectOutputTypeDef",
    {
        "project": ProjectTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateProjectOutputTypeDef = TypedDict(
    "UpdateProjectOutputTypeDef",
    {
        "project": ProjectTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetReportGroupsOutputTypeDef = TypedDict(
    "BatchGetReportGroupsOutputTypeDef",
    {
        "reportGroups": List[ReportGroupTypeDef],
        "reportGroupsNotFound": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateReportGroupOutputTypeDef = TypedDict(
    "CreateReportGroupOutputTypeDef",
    {
        "reportGroup": ReportGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateReportGroupOutputTypeDef = TypedDict(
    "UpdateReportGroupOutputTypeDef",
    {
        "reportGroup": ReportGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetReportsOutputTypeDef = TypedDict(
    "BatchGetReportsOutputTypeDef",
    {
        "reports": List[ReportTypeDef],
        "reportsNotFound": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetFleetsOutputTypeDef = TypedDict(
    "BatchGetFleetsOutputTypeDef",
    {
        "fleets": List[FleetTypeDef],
        "fleetsNotFound": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateFleetOutputTypeDef = TypedDict(
    "CreateFleetOutputTypeDef",
    {
        "fleet": FleetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateFleetOutputTypeDef = TypedDict(
    "UpdateFleetOutputTypeDef",
    {
        "fleet": FleetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetBuildBatchesOutputTypeDef = TypedDict(
    "BatchGetBuildBatchesOutputTypeDef",
    {
        "buildBatches": List[BuildBatchTypeDef],
        "buildBatchesNotFound": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RetryBuildBatchOutputTypeDef = TypedDict(
    "RetryBuildBatchOutputTypeDef",
    {
        "buildBatch": BuildBatchTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartBuildBatchOutputTypeDef = TypedDict(
    "StartBuildBatchOutputTypeDef",
    {
        "buildBatch": BuildBatchTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopBuildBatchOutputTypeDef = TypedDict(
    "StopBuildBatchOutputTypeDef",
    {
        "buildBatch": BuildBatchTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

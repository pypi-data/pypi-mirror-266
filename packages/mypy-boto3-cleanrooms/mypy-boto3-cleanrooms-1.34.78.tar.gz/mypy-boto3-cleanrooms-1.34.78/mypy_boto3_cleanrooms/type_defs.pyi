"""
Type annotations for cleanrooms service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cleanrooms/type_defs/)

Usage::

    ```python
    from mypy_boto3_cleanrooms.type_defs import AggregateColumnTypeDef

    data: AggregateColumnTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    AggregateFunctionNameType,
    AnalysisRuleTypeType,
    CollaborationQueryLogStatusType,
    ConfiguredTableAnalysisRuleTypeType,
    DifferentialPrivacyAggregationTypeType,
    FilterableMemberStatusType,
    JoinOperatorType,
    MemberAbilityType,
    MembershipQueryLogStatusType,
    MembershipStatusType,
    MemberStatusType,
    ParameterTypeType,
    PrivacyBudgetTemplateAutoRefreshType,
    ProtectedQueryStatusType,
    ResultFormatType,
    ScalarFunctionsType,
    SchemaStatusReasonCodeType,
    SchemaStatusType,
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
    "AggregateColumnTypeDef",
    "AggregationConstraintTypeDef",
    "AnalysisParameterTypeDef",
    "AnalysisRuleListTypeDef",
    "AnalysisSchemaTypeDef",
    "AnalysisSourceTypeDef",
    "AnalysisTemplateSummaryTypeDef",
    "BatchGetCollaborationAnalysisTemplateErrorTypeDef",
    "BatchGetCollaborationAnalysisTemplateInputRequestTypeDef",
    "ResponseMetadataTypeDef",
    "BatchGetSchemaAnalysisRuleErrorTypeDef",
    "SchemaAnalysisRuleRequestTypeDef",
    "BatchGetSchemaErrorTypeDef",
    "BatchGetSchemaInputRequestTypeDef",
    "CollaborationAnalysisTemplateSummaryTypeDef",
    "CollaborationConfiguredAudienceModelAssociationSummaryTypeDef",
    "CollaborationConfiguredAudienceModelAssociationTypeDef",
    "CollaborationPrivacyBudgetTemplateSummaryTypeDef",
    "CollaborationSummaryTypeDef",
    "DataEncryptionMetadataTypeDef",
    "ColumnTypeDef",
    "ConfiguredAudienceModelAssociationSummaryTypeDef",
    "ConfiguredAudienceModelAssociationTypeDef",
    "ConfiguredTableAssociationSummaryTypeDef",
    "ConfiguredTableAssociationTypeDef",
    "ConfiguredTableSummaryTypeDef",
    "CreateConfiguredAudienceModelAssociationInputRequestTypeDef",
    "CreateConfiguredTableAssociationInputRequestTypeDef",
    "DeleteAnalysisTemplateInputRequestTypeDef",
    "DeleteCollaborationInputRequestTypeDef",
    "DeleteConfiguredAudienceModelAssociationInputRequestTypeDef",
    "DeleteConfiguredTableAnalysisRuleInputRequestTypeDef",
    "DeleteConfiguredTableAssociationInputRequestTypeDef",
    "DeleteConfiguredTableInputRequestTypeDef",
    "DeleteMemberInputRequestTypeDef",
    "DeleteMembershipInputRequestTypeDef",
    "DeletePrivacyBudgetTemplateInputRequestTypeDef",
    "DifferentialPrivacyColumnTypeDef",
    "DifferentialPrivacySensitivityParametersTypeDef",
    "DifferentialPrivacyPreviewAggregationTypeDef",
    "DifferentialPrivacyPreviewParametersInputTypeDef",
    "DifferentialPrivacyPrivacyBudgetAggregationTypeDef",
    "DifferentialPrivacyTemplateParametersInputTypeDef",
    "DifferentialPrivacyTemplateParametersOutputTypeDef",
    "DifferentialPrivacyTemplateUpdateParametersTypeDef",
    "GetAnalysisTemplateInputRequestTypeDef",
    "GetCollaborationAnalysisTemplateInputRequestTypeDef",
    "GetCollaborationConfiguredAudienceModelAssociationInputRequestTypeDef",
    "GetCollaborationInputRequestTypeDef",
    "GetCollaborationPrivacyBudgetTemplateInputRequestTypeDef",
    "GetConfiguredAudienceModelAssociationInputRequestTypeDef",
    "GetConfiguredTableAnalysisRuleInputRequestTypeDef",
    "GetConfiguredTableAssociationInputRequestTypeDef",
    "GetConfiguredTableInputRequestTypeDef",
    "GetMembershipInputRequestTypeDef",
    "GetPrivacyBudgetTemplateInputRequestTypeDef",
    "GetProtectedQueryInputRequestTypeDef",
    "GetSchemaAnalysisRuleInputRequestTypeDef",
    "GetSchemaInputRequestTypeDef",
    "GlueTableReferenceTypeDef",
    "PaginatorConfigTypeDef",
    "ListAnalysisTemplatesInputRequestTypeDef",
    "ListCollaborationAnalysisTemplatesInputRequestTypeDef",
    "ListCollaborationConfiguredAudienceModelAssociationsInputRequestTypeDef",
    "ListCollaborationPrivacyBudgetTemplatesInputRequestTypeDef",
    "ListCollaborationPrivacyBudgetsInputRequestTypeDef",
    "ListCollaborationsInputRequestTypeDef",
    "ListConfiguredAudienceModelAssociationsInputRequestTypeDef",
    "ListConfiguredTableAssociationsInputRequestTypeDef",
    "ListConfiguredTablesInputRequestTypeDef",
    "ListMembersInputRequestTypeDef",
    "ListMembershipsInputRequestTypeDef",
    "ListPrivacyBudgetTemplatesInputRequestTypeDef",
    "PrivacyBudgetTemplateSummaryTypeDef",
    "ListPrivacyBudgetsInputRequestTypeDef",
    "ListProtectedQueriesInputRequestTypeDef",
    "ProtectedQuerySummaryTypeDef",
    "ListSchemasInputRequestTypeDef",
    "SchemaSummaryTypeDef",
    "ListTagsForResourceInputRequestTypeDef",
    "MembershipQueryComputePaymentConfigTypeDef",
    "ProtectedQueryS3OutputConfigurationTypeDef",
    "QueryComputePaymentConfigTypeDef",
    "ProtectedQueryErrorTypeDef",
    "ProtectedQueryS3OutputTypeDef",
    "ProtectedQuerySingleMemberOutputTypeDef",
    "ProtectedQuerySQLParametersTypeDef",
    "ProtectedQueryStatisticsTypeDef",
    "SchemaStatusReasonTypeDef",
    "TagResourceInputRequestTypeDef",
    "UntagResourceInputRequestTypeDef",
    "UpdateAnalysisTemplateInputRequestTypeDef",
    "UpdateCollaborationInputRequestTypeDef",
    "UpdateConfiguredAudienceModelAssociationInputRequestTypeDef",
    "UpdateConfiguredTableAssociationInputRequestTypeDef",
    "UpdateConfiguredTableInputRequestTypeDef",
    "UpdateProtectedQueryInputRequestTypeDef",
    "AnalysisRuleAggregationTypeDef",
    "AnalysisTemplateTypeDef",
    "CollaborationAnalysisTemplateTypeDef",
    "CreateAnalysisTemplateInputRequestTypeDef",
    "ListAnalysisTemplatesOutputTypeDef",
    "ListTagsForResourceOutputTypeDef",
    "BatchGetSchemaAnalysisRuleInputRequestTypeDef",
    "ListCollaborationAnalysisTemplatesOutputTypeDef",
    "ListCollaborationConfiguredAudienceModelAssociationsOutputTypeDef",
    "GetCollaborationConfiguredAudienceModelAssociationOutputTypeDef",
    "ListCollaborationPrivacyBudgetTemplatesOutputTypeDef",
    "ListCollaborationsOutputTypeDef",
    "CollaborationTypeDef",
    "ListConfiguredAudienceModelAssociationsOutputTypeDef",
    "CreateConfiguredAudienceModelAssociationOutputTypeDef",
    "GetConfiguredAudienceModelAssociationOutputTypeDef",
    "UpdateConfiguredAudienceModelAssociationOutputTypeDef",
    "ListConfiguredTableAssociationsOutputTypeDef",
    "CreateConfiguredTableAssociationOutputTypeDef",
    "GetConfiguredTableAssociationOutputTypeDef",
    "UpdateConfiguredTableAssociationOutputTypeDef",
    "ListConfiguredTablesOutputTypeDef",
    "DifferentialPrivacyConfigurationTypeDef",
    "DifferentialPrivacyParametersTypeDef",
    "DifferentialPrivacyPrivacyImpactTypeDef",
    "PreviewPrivacyImpactParametersInputTypeDef",
    "DifferentialPrivacyPrivacyBudgetTypeDef",
    "PrivacyBudgetTemplateParametersInputTypeDef",
    "PrivacyBudgetTemplateParametersOutputTypeDef",
    "PrivacyBudgetTemplateUpdateParametersTypeDef",
    "TableReferenceTypeDef",
    "ListAnalysisTemplatesInputListAnalysisTemplatesPaginateTypeDef",
    "ListCollaborationAnalysisTemplatesInputListCollaborationAnalysisTemplatesPaginateTypeDef",
    "ListCollaborationConfiguredAudienceModelAssociationsInputListCollaborationConfiguredAudienceModelAssociationsPaginateTypeDef",
    "ListCollaborationPrivacyBudgetTemplatesInputListCollaborationPrivacyBudgetTemplatesPaginateTypeDef",
    "ListCollaborationPrivacyBudgetsInputListCollaborationPrivacyBudgetsPaginateTypeDef",
    "ListCollaborationsInputListCollaborationsPaginateTypeDef",
    "ListConfiguredAudienceModelAssociationsInputListConfiguredAudienceModelAssociationsPaginateTypeDef",
    "ListConfiguredTableAssociationsInputListConfiguredTableAssociationsPaginateTypeDef",
    "ListConfiguredTablesInputListConfiguredTablesPaginateTypeDef",
    "ListMembersInputListMembersPaginateTypeDef",
    "ListMembershipsInputListMembershipsPaginateTypeDef",
    "ListPrivacyBudgetTemplatesInputListPrivacyBudgetTemplatesPaginateTypeDef",
    "ListPrivacyBudgetsInputListPrivacyBudgetsPaginateTypeDef",
    "ListProtectedQueriesInputListProtectedQueriesPaginateTypeDef",
    "ListSchemasInputListSchemasPaginateTypeDef",
    "ListPrivacyBudgetTemplatesOutputTypeDef",
    "ListProtectedQueriesOutputTypeDef",
    "ListSchemasOutputTypeDef",
    "MembershipPaymentConfigurationTypeDef",
    "MembershipProtectedQueryOutputConfigurationTypeDef",
    "ProtectedQueryOutputConfigurationTypeDef",
    "PaymentConfigurationTypeDef",
    "ProtectedQueryOutputTypeDef",
    "SchemaStatusDetailTypeDef",
    "CreateAnalysisTemplateOutputTypeDef",
    "GetAnalysisTemplateOutputTypeDef",
    "UpdateAnalysisTemplateOutputTypeDef",
    "BatchGetCollaborationAnalysisTemplateOutputTypeDef",
    "GetCollaborationAnalysisTemplateOutputTypeDef",
    "CreateCollaborationOutputTypeDef",
    "GetCollaborationOutputTypeDef",
    "UpdateCollaborationOutputTypeDef",
    "AnalysisRuleCustomTypeDef",
    "PrivacyImpactTypeDef",
    "PreviewPrivacyImpactInputRequestTypeDef",
    "PrivacyBudgetTypeDef",
    "CreatePrivacyBudgetTemplateInputRequestTypeDef",
    "CollaborationPrivacyBudgetTemplateTypeDef",
    "PrivacyBudgetTemplateTypeDef",
    "UpdatePrivacyBudgetTemplateInputRequestTypeDef",
    "ConfiguredTableTypeDef",
    "CreateConfiguredTableInputRequestTypeDef",
    "MembershipSummaryTypeDef",
    "MembershipProtectedQueryResultConfigurationTypeDef",
    "ProtectedQueryResultConfigurationTypeDef",
    "MemberSpecificationTypeDef",
    "MemberSummaryTypeDef",
    "ProtectedQueryResultTypeDef",
    "SchemaTypeDef",
    "AnalysisRulePolicyV1TypeDef",
    "ConfiguredTableAnalysisRulePolicyV1TypeDef",
    "PreviewPrivacyImpactOutputTypeDef",
    "CollaborationPrivacyBudgetSummaryTypeDef",
    "PrivacyBudgetSummaryTypeDef",
    "GetCollaborationPrivacyBudgetTemplateOutputTypeDef",
    "CreatePrivacyBudgetTemplateOutputTypeDef",
    "GetPrivacyBudgetTemplateOutputTypeDef",
    "UpdatePrivacyBudgetTemplateOutputTypeDef",
    "CreateConfiguredTableOutputTypeDef",
    "GetConfiguredTableOutputTypeDef",
    "UpdateConfiguredTableOutputTypeDef",
    "ListMembershipsOutputTypeDef",
    "CreateMembershipInputRequestTypeDef",
    "MembershipTypeDef",
    "UpdateMembershipInputRequestTypeDef",
    "StartProtectedQueryInputRequestTypeDef",
    "CreateCollaborationInputRequestTypeDef",
    "ListMembersOutputTypeDef",
    "ProtectedQueryTypeDef",
    "BatchGetSchemaOutputTypeDef",
    "GetSchemaOutputTypeDef",
    "AnalysisRulePolicyTypeDef",
    "ConfiguredTableAnalysisRulePolicyTypeDef",
    "ListCollaborationPrivacyBudgetsOutputTypeDef",
    "ListPrivacyBudgetsOutputTypeDef",
    "CreateMembershipOutputTypeDef",
    "GetMembershipOutputTypeDef",
    "UpdateMembershipOutputTypeDef",
    "GetProtectedQueryOutputTypeDef",
    "StartProtectedQueryOutputTypeDef",
    "UpdateProtectedQueryOutputTypeDef",
    "AnalysisRuleTypeDef",
    "ConfiguredTableAnalysisRuleTypeDef",
    "CreateConfiguredTableAnalysisRuleInputRequestTypeDef",
    "UpdateConfiguredTableAnalysisRuleInputRequestTypeDef",
    "BatchGetSchemaAnalysisRuleOutputTypeDef",
    "GetSchemaAnalysisRuleOutputTypeDef",
    "CreateConfiguredTableAnalysisRuleOutputTypeDef",
    "GetConfiguredTableAnalysisRuleOutputTypeDef",
    "UpdateConfiguredTableAnalysisRuleOutputTypeDef",
)

AggregateColumnTypeDef = TypedDict(
    "AggregateColumnTypeDef",
    {
        "columnNames": List[str],
        "function": AggregateFunctionNameType,
    },
)
AggregationConstraintTypeDef = TypedDict(
    "AggregationConstraintTypeDef",
    {
        "columnName": str,
        "minimum": int,
        "type": Literal["COUNT_DISTINCT"],
    },
)
AnalysisParameterTypeDef = TypedDict(
    "AnalysisParameterTypeDef",
    {
        "name": str,
        "type": ParameterTypeType,
        "defaultValue": NotRequired[str],
    },
)
AnalysisRuleListTypeDef = TypedDict(
    "AnalysisRuleListTypeDef",
    {
        "joinColumns": List[str],
        "listColumns": List[str],
        "allowedJoinOperators": NotRequired[List[JoinOperatorType]],
    },
)
AnalysisSchemaTypeDef = TypedDict(
    "AnalysisSchemaTypeDef",
    {
        "referencedTables": NotRequired[List[str]],
    },
)
AnalysisSourceTypeDef = TypedDict(
    "AnalysisSourceTypeDef",
    {
        "text": NotRequired[str],
    },
)
AnalysisTemplateSummaryTypeDef = TypedDict(
    "AnalysisTemplateSummaryTypeDef",
    {
        "arn": str,
        "createTime": datetime,
        "id": str,
        "name": str,
        "updateTime": datetime,
        "membershipArn": str,
        "membershipId": str,
        "collaborationArn": str,
        "collaborationId": str,
        "description": NotRequired[str],
    },
)
BatchGetCollaborationAnalysisTemplateErrorTypeDef = TypedDict(
    "BatchGetCollaborationAnalysisTemplateErrorTypeDef",
    {
        "arn": str,
        "code": str,
        "message": str,
    },
)
BatchGetCollaborationAnalysisTemplateInputRequestTypeDef = TypedDict(
    "BatchGetCollaborationAnalysisTemplateInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "analysisTemplateArns": Sequence[str],
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
BatchGetSchemaAnalysisRuleErrorTypeDef = TypedDict(
    "BatchGetSchemaAnalysisRuleErrorTypeDef",
    {
        "name": str,
        "type": AnalysisRuleTypeType,
        "code": str,
        "message": str,
    },
)
SchemaAnalysisRuleRequestTypeDef = TypedDict(
    "SchemaAnalysisRuleRequestTypeDef",
    {
        "name": str,
        "type": AnalysisRuleTypeType,
    },
)
BatchGetSchemaErrorTypeDef = TypedDict(
    "BatchGetSchemaErrorTypeDef",
    {
        "name": str,
        "code": str,
        "message": str,
    },
)
BatchGetSchemaInputRequestTypeDef = TypedDict(
    "BatchGetSchemaInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "names": Sequence[str],
    },
)
CollaborationAnalysisTemplateSummaryTypeDef = TypedDict(
    "CollaborationAnalysisTemplateSummaryTypeDef",
    {
        "arn": str,
        "createTime": datetime,
        "id": str,
        "name": str,
        "updateTime": datetime,
        "collaborationArn": str,
        "collaborationId": str,
        "creatorAccountId": str,
        "description": NotRequired[str],
    },
)
CollaborationConfiguredAudienceModelAssociationSummaryTypeDef = TypedDict(
    "CollaborationConfiguredAudienceModelAssociationSummaryTypeDef",
    {
        "arn": str,
        "createTime": datetime,
        "id": str,
        "name": str,
        "updateTime": datetime,
        "collaborationArn": str,
        "collaborationId": str,
        "creatorAccountId": str,
        "description": NotRequired[str],
    },
)
CollaborationConfiguredAudienceModelAssociationTypeDef = TypedDict(
    "CollaborationConfiguredAudienceModelAssociationTypeDef",
    {
        "id": str,
        "arn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "configuredAudienceModelArn": str,
        "name": str,
        "creatorAccountId": str,
        "createTime": datetime,
        "updateTime": datetime,
        "description": NotRequired[str],
    },
)
CollaborationPrivacyBudgetTemplateSummaryTypeDef = TypedDict(
    "CollaborationPrivacyBudgetTemplateSummaryTypeDef",
    {
        "id": str,
        "arn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "creatorAccountId": str,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "createTime": datetime,
        "updateTime": datetime,
    },
)
CollaborationSummaryTypeDef = TypedDict(
    "CollaborationSummaryTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "creatorAccountId": str,
        "creatorDisplayName": str,
        "createTime": datetime,
        "updateTime": datetime,
        "memberStatus": MemberStatusType,
        "membershipId": NotRequired[str],
        "membershipArn": NotRequired[str],
    },
)
DataEncryptionMetadataTypeDef = TypedDict(
    "DataEncryptionMetadataTypeDef",
    {
        "allowCleartext": bool,
        "allowDuplicates": bool,
        "allowJoinsOnColumnsWithDifferentNames": bool,
        "preserveNulls": bool,
    },
)
ColumnTypeDef = TypedDict(
    "ColumnTypeDef",
    {
        "name": str,
        "type": str,
    },
)
ConfiguredAudienceModelAssociationSummaryTypeDef = TypedDict(
    "ConfiguredAudienceModelAssociationSummaryTypeDef",
    {
        "membershipId": str,
        "membershipArn": str,
        "collaborationArn": str,
        "collaborationId": str,
        "createTime": datetime,
        "updateTime": datetime,
        "id": str,
        "arn": str,
        "name": str,
        "configuredAudienceModelArn": str,
        "description": NotRequired[str],
    },
)
ConfiguredAudienceModelAssociationTypeDef = TypedDict(
    "ConfiguredAudienceModelAssociationTypeDef",
    {
        "id": str,
        "arn": str,
        "configuredAudienceModelArn": str,
        "membershipId": str,
        "membershipArn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "name": str,
        "manageResourcePolicies": bool,
        "createTime": datetime,
        "updateTime": datetime,
        "description": NotRequired[str],
    },
)
ConfiguredTableAssociationSummaryTypeDef = TypedDict(
    "ConfiguredTableAssociationSummaryTypeDef",
    {
        "configuredTableId": str,
        "membershipId": str,
        "membershipArn": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "id": str,
        "arn": str,
    },
)
ConfiguredTableAssociationTypeDef = TypedDict(
    "ConfiguredTableAssociationTypeDef",
    {
        "arn": str,
        "id": str,
        "configuredTableId": str,
        "configuredTableArn": str,
        "membershipId": str,
        "membershipArn": str,
        "roleArn": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "description": NotRequired[str],
    },
)
ConfiguredTableSummaryTypeDef = TypedDict(
    "ConfiguredTableSummaryTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "analysisRuleTypes": List[ConfiguredTableAnalysisRuleTypeType],
        "analysisMethod": Literal["DIRECT_QUERY"],
    },
)
CreateConfiguredAudienceModelAssociationInputRequestTypeDef = TypedDict(
    "CreateConfiguredAudienceModelAssociationInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "configuredAudienceModelArn": str,
        "configuredAudienceModelAssociationName": str,
        "manageResourcePolicies": bool,
        "tags": NotRequired[Mapping[str, str]],
        "description": NotRequired[str],
    },
)
CreateConfiguredTableAssociationInputRequestTypeDef = TypedDict(
    "CreateConfiguredTableAssociationInputRequestTypeDef",
    {
        "name": str,
        "membershipIdentifier": str,
        "configuredTableIdentifier": str,
        "roleArn": str,
        "description": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
DeleteAnalysisTemplateInputRequestTypeDef = TypedDict(
    "DeleteAnalysisTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "analysisTemplateIdentifier": str,
    },
)
DeleteCollaborationInputRequestTypeDef = TypedDict(
    "DeleteCollaborationInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
    },
)
DeleteConfiguredAudienceModelAssociationInputRequestTypeDef = TypedDict(
    "DeleteConfiguredAudienceModelAssociationInputRequestTypeDef",
    {
        "configuredAudienceModelAssociationIdentifier": str,
        "membershipIdentifier": str,
    },
)
DeleteConfiguredTableAnalysisRuleInputRequestTypeDef = TypedDict(
    "DeleteConfiguredTableAnalysisRuleInputRequestTypeDef",
    {
        "configuredTableIdentifier": str,
        "analysisRuleType": ConfiguredTableAnalysisRuleTypeType,
    },
)
DeleteConfiguredTableAssociationInputRequestTypeDef = TypedDict(
    "DeleteConfiguredTableAssociationInputRequestTypeDef",
    {
        "configuredTableAssociationIdentifier": str,
        "membershipIdentifier": str,
    },
)
DeleteConfiguredTableInputRequestTypeDef = TypedDict(
    "DeleteConfiguredTableInputRequestTypeDef",
    {
        "configuredTableIdentifier": str,
    },
)
DeleteMemberInputRequestTypeDef = TypedDict(
    "DeleteMemberInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "accountId": str,
    },
)
DeleteMembershipInputRequestTypeDef = TypedDict(
    "DeleteMembershipInputRequestTypeDef",
    {
        "membershipIdentifier": str,
    },
)
DeletePrivacyBudgetTemplateInputRequestTypeDef = TypedDict(
    "DeletePrivacyBudgetTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "privacyBudgetTemplateIdentifier": str,
    },
)
DifferentialPrivacyColumnTypeDef = TypedDict(
    "DifferentialPrivacyColumnTypeDef",
    {
        "name": str,
    },
)
DifferentialPrivacySensitivityParametersTypeDef = TypedDict(
    "DifferentialPrivacySensitivityParametersTypeDef",
    {
        "aggregationType": DifferentialPrivacyAggregationTypeType,
        "aggregationExpression": str,
        "userContributionLimit": int,
        "minColumnValue": NotRequired[float],
        "maxColumnValue": NotRequired[float],
    },
)
DifferentialPrivacyPreviewAggregationTypeDef = TypedDict(
    "DifferentialPrivacyPreviewAggregationTypeDef",
    {
        "type": DifferentialPrivacyAggregationTypeType,
        "maxCount": int,
    },
)
DifferentialPrivacyPreviewParametersInputTypeDef = TypedDict(
    "DifferentialPrivacyPreviewParametersInputTypeDef",
    {
        "epsilon": int,
        "usersNoisePerQuery": int,
    },
)
DifferentialPrivacyPrivacyBudgetAggregationTypeDef = TypedDict(
    "DifferentialPrivacyPrivacyBudgetAggregationTypeDef",
    {
        "type": DifferentialPrivacyAggregationTypeType,
        "maxCount": int,
        "remainingCount": int,
    },
)
DifferentialPrivacyTemplateParametersInputTypeDef = TypedDict(
    "DifferentialPrivacyTemplateParametersInputTypeDef",
    {
        "epsilon": int,
        "usersNoisePerQuery": int,
    },
)
DifferentialPrivacyTemplateParametersOutputTypeDef = TypedDict(
    "DifferentialPrivacyTemplateParametersOutputTypeDef",
    {
        "epsilon": int,
        "usersNoisePerQuery": int,
    },
)
DifferentialPrivacyTemplateUpdateParametersTypeDef = TypedDict(
    "DifferentialPrivacyTemplateUpdateParametersTypeDef",
    {
        "epsilon": NotRequired[int],
        "usersNoisePerQuery": NotRequired[int],
    },
)
GetAnalysisTemplateInputRequestTypeDef = TypedDict(
    "GetAnalysisTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "analysisTemplateIdentifier": str,
    },
)
GetCollaborationAnalysisTemplateInputRequestTypeDef = TypedDict(
    "GetCollaborationAnalysisTemplateInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "analysisTemplateArn": str,
    },
)
GetCollaborationConfiguredAudienceModelAssociationInputRequestTypeDef = TypedDict(
    "GetCollaborationConfiguredAudienceModelAssociationInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "configuredAudienceModelAssociationIdentifier": str,
    },
)
GetCollaborationInputRequestTypeDef = TypedDict(
    "GetCollaborationInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
    },
)
GetCollaborationPrivacyBudgetTemplateInputRequestTypeDef = TypedDict(
    "GetCollaborationPrivacyBudgetTemplateInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "privacyBudgetTemplateIdentifier": str,
    },
)
GetConfiguredAudienceModelAssociationInputRequestTypeDef = TypedDict(
    "GetConfiguredAudienceModelAssociationInputRequestTypeDef",
    {
        "configuredAudienceModelAssociationIdentifier": str,
        "membershipIdentifier": str,
    },
)
GetConfiguredTableAnalysisRuleInputRequestTypeDef = TypedDict(
    "GetConfiguredTableAnalysisRuleInputRequestTypeDef",
    {
        "configuredTableIdentifier": str,
        "analysisRuleType": ConfiguredTableAnalysisRuleTypeType,
    },
)
GetConfiguredTableAssociationInputRequestTypeDef = TypedDict(
    "GetConfiguredTableAssociationInputRequestTypeDef",
    {
        "configuredTableAssociationIdentifier": str,
        "membershipIdentifier": str,
    },
)
GetConfiguredTableInputRequestTypeDef = TypedDict(
    "GetConfiguredTableInputRequestTypeDef",
    {
        "configuredTableIdentifier": str,
    },
)
GetMembershipInputRequestTypeDef = TypedDict(
    "GetMembershipInputRequestTypeDef",
    {
        "membershipIdentifier": str,
    },
)
GetPrivacyBudgetTemplateInputRequestTypeDef = TypedDict(
    "GetPrivacyBudgetTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "privacyBudgetTemplateIdentifier": str,
    },
)
GetProtectedQueryInputRequestTypeDef = TypedDict(
    "GetProtectedQueryInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "protectedQueryIdentifier": str,
    },
)
GetSchemaAnalysisRuleInputRequestTypeDef = TypedDict(
    "GetSchemaAnalysisRuleInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "name": str,
        "type": AnalysisRuleTypeType,
    },
)
GetSchemaInputRequestTypeDef = TypedDict(
    "GetSchemaInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "name": str,
    },
)
GlueTableReferenceTypeDef = TypedDict(
    "GlueTableReferenceTypeDef",
    {
        "tableName": str,
        "databaseName": str,
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
ListAnalysisTemplatesInputRequestTypeDef = TypedDict(
    "ListAnalysisTemplatesInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListCollaborationAnalysisTemplatesInputRequestTypeDef = TypedDict(
    "ListCollaborationAnalysisTemplatesInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListCollaborationConfiguredAudienceModelAssociationsInputRequestTypeDef = TypedDict(
    "ListCollaborationConfiguredAudienceModelAssociationsInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListCollaborationPrivacyBudgetTemplatesInputRequestTypeDef = TypedDict(
    "ListCollaborationPrivacyBudgetTemplatesInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListCollaborationPrivacyBudgetsInputRequestTypeDef = TypedDict(
    "ListCollaborationPrivacyBudgetsInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListCollaborationsInputRequestTypeDef = TypedDict(
    "ListCollaborationsInputRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "memberStatus": NotRequired[FilterableMemberStatusType],
    },
)
ListConfiguredAudienceModelAssociationsInputRequestTypeDef = TypedDict(
    "ListConfiguredAudienceModelAssociationsInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListConfiguredTableAssociationsInputRequestTypeDef = TypedDict(
    "ListConfiguredTableAssociationsInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListConfiguredTablesInputRequestTypeDef = TypedDict(
    "ListConfiguredTablesInputRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListMembersInputRequestTypeDef = TypedDict(
    "ListMembersInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListMembershipsInputRequestTypeDef = TypedDict(
    "ListMembershipsInputRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "status": NotRequired[MembershipStatusType],
    },
)
ListPrivacyBudgetTemplatesInputRequestTypeDef = TypedDict(
    "ListPrivacyBudgetTemplatesInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
PrivacyBudgetTemplateSummaryTypeDef = TypedDict(
    "PrivacyBudgetTemplateSummaryTypeDef",
    {
        "id": str,
        "arn": str,
        "membershipId": str,
        "membershipArn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "createTime": datetime,
        "updateTime": datetime,
    },
)
ListPrivacyBudgetsInputRequestTypeDef = TypedDict(
    "ListPrivacyBudgetsInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListProtectedQueriesInputRequestTypeDef = TypedDict(
    "ListProtectedQueriesInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "status": NotRequired[ProtectedQueryStatusType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ProtectedQuerySummaryTypeDef = TypedDict(
    "ProtectedQuerySummaryTypeDef",
    {
        "id": str,
        "membershipId": str,
        "membershipArn": str,
        "createTime": datetime,
        "status": ProtectedQueryStatusType,
    },
)
ListSchemasInputRequestTypeDef = TypedDict(
    "ListSchemasInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "schemaType": NotRequired[Literal["TABLE"]],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
SchemaSummaryTypeDef = TypedDict(
    "SchemaSummaryTypeDef",
    {
        "name": str,
        "type": Literal["TABLE"],
        "creatorAccountId": str,
        "createTime": datetime,
        "updateTime": datetime,
        "collaborationId": str,
        "collaborationArn": str,
        "analysisRuleTypes": List[AnalysisRuleTypeType],
        "analysisMethod": NotRequired[Literal["DIRECT_QUERY"]],
    },
)
ListTagsForResourceInputRequestTypeDef = TypedDict(
    "ListTagsForResourceInputRequestTypeDef",
    {
        "resourceArn": str,
    },
)
MembershipQueryComputePaymentConfigTypeDef = TypedDict(
    "MembershipQueryComputePaymentConfigTypeDef",
    {
        "isResponsible": bool,
    },
)
ProtectedQueryS3OutputConfigurationTypeDef = TypedDict(
    "ProtectedQueryS3OutputConfigurationTypeDef",
    {
        "resultFormat": ResultFormatType,
        "bucket": str,
        "keyPrefix": NotRequired[str],
    },
)
QueryComputePaymentConfigTypeDef = TypedDict(
    "QueryComputePaymentConfigTypeDef",
    {
        "isResponsible": bool,
    },
)
ProtectedQueryErrorTypeDef = TypedDict(
    "ProtectedQueryErrorTypeDef",
    {
        "message": str,
        "code": str,
    },
)
ProtectedQueryS3OutputTypeDef = TypedDict(
    "ProtectedQueryS3OutputTypeDef",
    {
        "location": str,
    },
)
ProtectedQuerySingleMemberOutputTypeDef = TypedDict(
    "ProtectedQuerySingleMemberOutputTypeDef",
    {
        "accountId": str,
    },
)
ProtectedQuerySQLParametersTypeDef = TypedDict(
    "ProtectedQuerySQLParametersTypeDef",
    {
        "queryString": NotRequired[str],
        "analysisTemplateArn": NotRequired[str],
        "parameters": NotRequired[Dict[str, str]],
    },
)
ProtectedQueryStatisticsTypeDef = TypedDict(
    "ProtectedQueryStatisticsTypeDef",
    {
        "totalDurationInMillis": NotRequired[int],
    },
)
SchemaStatusReasonTypeDef = TypedDict(
    "SchemaStatusReasonTypeDef",
    {
        "code": SchemaStatusReasonCodeType,
        "message": str,
    },
)
TagResourceInputRequestTypeDef = TypedDict(
    "TagResourceInputRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
UntagResourceInputRequestTypeDef = TypedDict(
    "UntagResourceInputRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateAnalysisTemplateInputRequestTypeDef = TypedDict(
    "UpdateAnalysisTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "analysisTemplateIdentifier": str,
        "description": NotRequired[str],
    },
)
UpdateCollaborationInputRequestTypeDef = TypedDict(
    "UpdateCollaborationInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "name": NotRequired[str],
        "description": NotRequired[str],
    },
)
UpdateConfiguredAudienceModelAssociationInputRequestTypeDef = TypedDict(
    "UpdateConfiguredAudienceModelAssociationInputRequestTypeDef",
    {
        "configuredAudienceModelAssociationIdentifier": str,
        "membershipIdentifier": str,
        "description": NotRequired[str],
        "name": NotRequired[str],
    },
)
UpdateConfiguredTableAssociationInputRequestTypeDef = TypedDict(
    "UpdateConfiguredTableAssociationInputRequestTypeDef",
    {
        "configuredTableAssociationIdentifier": str,
        "membershipIdentifier": str,
        "description": NotRequired[str],
        "roleArn": NotRequired[str],
    },
)
UpdateConfiguredTableInputRequestTypeDef = TypedDict(
    "UpdateConfiguredTableInputRequestTypeDef",
    {
        "configuredTableIdentifier": str,
        "name": NotRequired[str],
        "description": NotRequired[str],
    },
)
UpdateProtectedQueryInputRequestTypeDef = TypedDict(
    "UpdateProtectedQueryInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "protectedQueryIdentifier": str,
        "targetStatus": Literal["CANCELLED"],
    },
)
AnalysisRuleAggregationTypeDef = TypedDict(
    "AnalysisRuleAggregationTypeDef",
    {
        "aggregateColumns": List[AggregateColumnTypeDef],
        "joinColumns": List[str],
        "dimensionColumns": List[str],
        "scalarFunctions": List[ScalarFunctionsType],
        "outputConstraints": List[AggregationConstraintTypeDef],
        "joinRequired": NotRequired[Literal["QUERY_RUNNER"]],
        "allowedJoinOperators": NotRequired[List[JoinOperatorType]],
    },
)
AnalysisTemplateTypeDef = TypedDict(
    "AnalysisTemplateTypeDef",
    {
        "id": str,
        "arn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "membershipId": str,
        "membershipArn": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "schema": AnalysisSchemaTypeDef,
        "format": Literal["SQL"],
        "source": AnalysisSourceTypeDef,
        "description": NotRequired[str],
        "analysisParameters": NotRequired[List[AnalysisParameterTypeDef]],
    },
)
CollaborationAnalysisTemplateTypeDef = TypedDict(
    "CollaborationAnalysisTemplateTypeDef",
    {
        "id": str,
        "arn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "creatorAccountId": str,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "schema": AnalysisSchemaTypeDef,
        "format": Literal["SQL"],
        "source": AnalysisSourceTypeDef,
        "description": NotRequired[str],
        "analysisParameters": NotRequired[List[AnalysisParameterTypeDef]],
    },
)
CreateAnalysisTemplateInputRequestTypeDef = TypedDict(
    "CreateAnalysisTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "name": str,
        "format": Literal["SQL"],
        "source": AnalysisSourceTypeDef,
        "description": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "analysisParameters": NotRequired[Sequence[AnalysisParameterTypeDef]],
    },
)
ListAnalysisTemplatesOutputTypeDef = TypedDict(
    "ListAnalysisTemplatesOutputTypeDef",
    {
        "nextToken": str,
        "analysisTemplateSummaries": List[AnalysisTemplateSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceOutputTypeDef = TypedDict(
    "ListTagsForResourceOutputTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetSchemaAnalysisRuleInputRequestTypeDef = TypedDict(
    "BatchGetSchemaAnalysisRuleInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "schemaAnalysisRuleRequests": Sequence[SchemaAnalysisRuleRequestTypeDef],
    },
)
ListCollaborationAnalysisTemplatesOutputTypeDef = TypedDict(
    "ListCollaborationAnalysisTemplatesOutputTypeDef",
    {
        "nextToken": str,
        "collaborationAnalysisTemplateSummaries": List[CollaborationAnalysisTemplateSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCollaborationConfiguredAudienceModelAssociationsOutputTypeDef = TypedDict(
    "ListCollaborationConfiguredAudienceModelAssociationsOutputTypeDef",
    {
        "collaborationConfiguredAudienceModelAssociationSummaries": List[
            CollaborationConfiguredAudienceModelAssociationSummaryTypeDef
        ],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetCollaborationConfiguredAudienceModelAssociationOutputTypeDef = TypedDict(
    "GetCollaborationConfiguredAudienceModelAssociationOutputTypeDef",
    {
        "collaborationConfiguredAudienceModelAssociation": CollaborationConfiguredAudienceModelAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCollaborationPrivacyBudgetTemplatesOutputTypeDef = TypedDict(
    "ListCollaborationPrivacyBudgetTemplatesOutputTypeDef",
    {
        "nextToken": str,
        "collaborationPrivacyBudgetTemplateSummaries": List[
            CollaborationPrivacyBudgetTemplateSummaryTypeDef
        ],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCollaborationsOutputTypeDef = TypedDict(
    "ListCollaborationsOutputTypeDef",
    {
        "nextToken": str,
        "collaborationList": List[CollaborationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CollaborationTypeDef = TypedDict(
    "CollaborationTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "creatorAccountId": str,
        "creatorDisplayName": str,
        "createTime": datetime,
        "updateTime": datetime,
        "memberStatus": MemberStatusType,
        "queryLogStatus": CollaborationQueryLogStatusType,
        "description": NotRequired[str],
        "membershipId": NotRequired[str],
        "membershipArn": NotRequired[str],
        "dataEncryptionMetadata": NotRequired[DataEncryptionMetadataTypeDef],
    },
)
ListConfiguredAudienceModelAssociationsOutputTypeDef = TypedDict(
    "ListConfiguredAudienceModelAssociationsOutputTypeDef",
    {
        "configuredAudienceModelAssociationSummaries": List[
            ConfiguredAudienceModelAssociationSummaryTypeDef
        ],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateConfiguredAudienceModelAssociationOutputTypeDef = TypedDict(
    "CreateConfiguredAudienceModelAssociationOutputTypeDef",
    {
        "configuredAudienceModelAssociation": ConfiguredAudienceModelAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetConfiguredAudienceModelAssociationOutputTypeDef = TypedDict(
    "GetConfiguredAudienceModelAssociationOutputTypeDef",
    {
        "configuredAudienceModelAssociation": ConfiguredAudienceModelAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateConfiguredAudienceModelAssociationOutputTypeDef = TypedDict(
    "UpdateConfiguredAudienceModelAssociationOutputTypeDef",
    {
        "configuredAudienceModelAssociation": ConfiguredAudienceModelAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListConfiguredTableAssociationsOutputTypeDef = TypedDict(
    "ListConfiguredTableAssociationsOutputTypeDef",
    {
        "configuredTableAssociationSummaries": List[ConfiguredTableAssociationSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateConfiguredTableAssociationOutputTypeDef = TypedDict(
    "CreateConfiguredTableAssociationOutputTypeDef",
    {
        "configuredTableAssociation": ConfiguredTableAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetConfiguredTableAssociationOutputTypeDef = TypedDict(
    "GetConfiguredTableAssociationOutputTypeDef",
    {
        "configuredTableAssociation": ConfiguredTableAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateConfiguredTableAssociationOutputTypeDef = TypedDict(
    "UpdateConfiguredTableAssociationOutputTypeDef",
    {
        "configuredTableAssociation": ConfiguredTableAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListConfiguredTablesOutputTypeDef = TypedDict(
    "ListConfiguredTablesOutputTypeDef",
    {
        "configuredTableSummaries": List[ConfiguredTableSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DifferentialPrivacyConfigurationTypeDef = TypedDict(
    "DifferentialPrivacyConfigurationTypeDef",
    {
        "columns": List[DifferentialPrivacyColumnTypeDef],
    },
)
DifferentialPrivacyParametersTypeDef = TypedDict(
    "DifferentialPrivacyParametersTypeDef",
    {
        "sensitivityParameters": List[DifferentialPrivacySensitivityParametersTypeDef],
    },
)
DifferentialPrivacyPrivacyImpactTypeDef = TypedDict(
    "DifferentialPrivacyPrivacyImpactTypeDef",
    {
        "aggregations": List[DifferentialPrivacyPreviewAggregationTypeDef],
    },
)
PreviewPrivacyImpactParametersInputTypeDef = TypedDict(
    "PreviewPrivacyImpactParametersInputTypeDef",
    {
        "differentialPrivacy": NotRequired[DifferentialPrivacyPreviewParametersInputTypeDef],
    },
)
DifferentialPrivacyPrivacyBudgetTypeDef = TypedDict(
    "DifferentialPrivacyPrivacyBudgetTypeDef",
    {
        "aggregations": List[DifferentialPrivacyPrivacyBudgetAggregationTypeDef],
        "epsilon": int,
    },
)
PrivacyBudgetTemplateParametersInputTypeDef = TypedDict(
    "PrivacyBudgetTemplateParametersInputTypeDef",
    {
        "differentialPrivacy": NotRequired[DifferentialPrivacyTemplateParametersInputTypeDef],
    },
)
PrivacyBudgetTemplateParametersOutputTypeDef = TypedDict(
    "PrivacyBudgetTemplateParametersOutputTypeDef",
    {
        "differentialPrivacy": NotRequired[DifferentialPrivacyTemplateParametersOutputTypeDef],
    },
)
PrivacyBudgetTemplateUpdateParametersTypeDef = TypedDict(
    "PrivacyBudgetTemplateUpdateParametersTypeDef",
    {
        "differentialPrivacy": NotRequired[DifferentialPrivacyTemplateUpdateParametersTypeDef],
    },
)
TableReferenceTypeDef = TypedDict(
    "TableReferenceTypeDef",
    {
        "glue": NotRequired[GlueTableReferenceTypeDef],
    },
)
ListAnalysisTemplatesInputListAnalysisTemplatesPaginateTypeDef = TypedDict(
    "ListAnalysisTemplatesInputListAnalysisTemplatesPaginateTypeDef",
    {
        "membershipIdentifier": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCollaborationAnalysisTemplatesInputListCollaborationAnalysisTemplatesPaginateTypeDef = (
    TypedDict(
        "ListCollaborationAnalysisTemplatesInputListCollaborationAnalysisTemplatesPaginateTypeDef",
        {
            "collaborationIdentifier": str,
            "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
        },
    )
)
ListCollaborationConfiguredAudienceModelAssociationsInputListCollaborationConfiguredAudienceModelAssociationsPaginateTypeDef = TypedDict(
    "ListCollaborationConfiguredAudienceModelAssociationsInputListCollaborationConfiguredAudienceModelAssociationsPaginateTypeDef",
    {
        "collaborationIdentifier": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCollaborationPrivacyBudgetTemplatesInputListCollaborationPrivacyBudgetTemplatesPaginateTypeDef = TypedDict(
    "ListCollaborationPrivacyBudgetTemplatesInputListCollaborationPrivacyBudgetTemplatesPaginateTypeDef",
    {
        "collaborationIdentifier": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCollaborationPrivacyBudgetsInputListCollaborationPrivacyBudgetsPaginateTypeDef = TypedDict(
    "ListCollaborationPrivacyBudgetsInputListCollaborationPrivacyBudgetsPaginateTypeDef",
    {
        "collaborationIdentifier": str,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCollaborationsInputListCollaborationsPaginateTypeDef = TypedDict(
    "ListCollaborationsInputListCollaborationsPaginateTypeDef",
    {
        "memberStatus": NotRequired[FilterableMemberStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListConfiguredAudienceModelAssociationsInputListConfiguredAudienceModelAssociationsPaginateTypeDef = TypedDict(
    "ListConfiguredAudienceModelAssociationsInputListConfiguredAudienceModelAssociationsPaginateTypeDef",
    {
        "membershipIdentifier": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListConfiguredTableAssociationsInputListConfiguredTableAssociationsPaginateTypeDef = TypedDict(
    "ListConfiguredTableAssociationsInputListConfiguredTableAssociationsPaginateTypeDef",
    {
        "membershipIdentifier": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListConfiguredTablesInputListConfiguredTablesPaginateTypeDef = TypedDict(
    "ListConfiguredTablesInputListConfiguredTablesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMembersInputListMembersPaginateTypeDef = TypedDict(
    "ListMembersInputListMembersPaginateTypeDef",
    {
        "collaborationIdentifier": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMembershipsInputListMembershipsPaginateTypeDef = TypedDict(
    "ListMembershipsInputListMembershipsPaginateTypeDef",
    {
        "status": NotRequired[MembershipStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPrivacyBudgetTemplatesInputListPrivacyBudgetTemplatesPaginateTypeDef = TypedDict(
    "ListPrivacyBudgetTemplatesInputListPrivacyBudgetTemplatesPaginateTypeDef",
    {
        "membershipIdentifier": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPrivacyBudgetsInputListPrivacyBudgetsPaginateTypeDef = TypedDict(
    "ListPrivacyBudgetsInputListPrivacyBudgetsPaginateTypeDef",
    {
        "membershipIdentifier": str,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListProtectedQueriesInputListProtectedQueriesPaginateTypeDef = TypedDict(
    "ListProtectedQueriesInputListProtectedQueriesPaginateTypeDef",
    {
        "membershipIdentifier": str,
        "status": NotRequired[ProtectedQueryStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSchemasInputListSchemasPaginateTypeDef = TypedDict(
    "ListSchemasInputListSchemasPaginateTypeDef",
    {
        "collaborationIdentifier": str,
        "schemaType": NotRequired[Literal["TABLE"]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPrivacyBudgetTemplatesOutputTypeDef = TypedDict(
    "ListPrivacyBudgetTemplatesOutputTypeDef",
    {
        "nextToken": str,
        "privacyBudgetTemplateSummaries": List[PrivacyBudgetTemplateSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListProtectedQueriesOutputTypeDef = TypedDict(
    "ListProtectedQueriesOutputTypeDef",
    {
        "nextToken": str,
        "protectedQueries": List[ProtectedQuerySummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSchemasOutputTypeDef = TypedDict(
    "ListSchemasOutputTypeDef",
    {
        "schemaSummaries": List[SchemaSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MembershipPaymentConfigurationTypeDef = TypedDict(
    "MembershipPaymentConfigurationTypeDef",
    {
        "queryCompute": MembershipQueryComputePaymentConfigTypeDef,
    },
)
MembershipProtectedQueryOutputConfigurationTypeDef = TypedDict(
    "MembershipProtectedQueryOutputConfigurationTypeDef",
    {
        "s3": NotRequired[ProtectedQueryS3OutputConfigurationTypeDef],
    },
)
ProtectedQueryOutputConfigurationTypeDef = TypedDict(
    "ProtectedQueryOutputConfigurationTypeDef",
    {
        "s3": NotRequired[ProtectedQueryS3OutputConfigurationTypeDef],
    },
)
PaymentConfigurationTypeDef = TypedDict(
    "PaymentConfigurationTypeDef",
    {
        "queryCompute": QueryComputePaymentConfigTypeDef,
    },
)
ProtectedQueryOutputTypeDef = TypedDict(
    "ProtectedQueryOutputTypeDef",
    {
        "s3": NotRequired[ProtectedQueryS3OutputTypeDef],
        "memberList": NotRequired[List[ProtectedQuerySingleMemberOutputTypeDef]],
    },
)
SchemaStatusDetailTypeDef = TypedDict(
    "SchemaStatusDetailTypeDef",
    {
        "status": SchemaStatusType,
        "reasons": NotRequired[List[SchemaStatusReasonTypeDef]],
        "analysisRuleType": NotRequired[AnalysisRuleTypeType],
        "configurations": NotRequired[List[Literal["DIFFERENTIAL_PRIVACY"]]],
    },
)
CreateAnalysisTemplateOutputTypeDef = TypedDict(
    "CreateAnalysisTemplateOutputTypeDef",
    {
        "analysisTemplate": AnalysisTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetAnalysisTemplateOutputTypeDef = TypedDict(
    "GetAnalysisTemplateOutputTypeDef",
    {
        "analysisTemplate": AnalysisTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateAnalysisTemplateOutputTypeDef = TypedDict(
    "UpdateAnalysisTemplateOutputTypeDef",
    {
        "analysisTemplate": AnalysisTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetCollaborationAnalysisTemplateOutputTypeDef = TypedDict(
    "BatchGetCollaborationAnalysisTemplateOutputTypeDef",
    {
        "collaborationAnalysisTemplates": List[CollaborationAnalysisTemplateTypeDef],
        "errors": List[BatchGetCollaborationAnalysisTemplateErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetCollaborationAnalysisTemplateOutputTypeDef = TypedDict(
    "GetCollaborationAnalysisTemplateOutputTypeDef",
    {
        "collaborationAnalysisTemplate": CollaborationAnalysisTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCollaborationOutputTypeDef = TypedDict(
    "CreateCollaborationOutputTypeDef",
    {
        "collaboration": CollaborationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetCollaborationOutputTypeDef = TypedDict(
    "GetCollaborationOutputTypeDef",
    {
        "collaboration": CollaborationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCollaborationOutputTypeDef = TypedDict(
    "UpdateCollaborationOutputTypeDef",
    {
        "collaboration": CollaborationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AnalysisRuleCustomTypeDef = TypedDict(
    "AnalysisRuleCustomTypeDef",
    {
        "allowedAnalyses": List[str],
        "allowedAnalysisProviders": NotRequired[List[str]],
        "differentialPrivacy": NotRequired[DifferentialPrivacyConfigurationTypeDef],
    },
)
PrivacyImpactTypeDef = TypedDict(
    "PrivacyImpactTypeDef",
    {
        "differentialPrivacy": NotRequired[DifferentialPrivacyPrivacyImpactTypeDef],
    },
)
PreviewPrivacyImpactInputRequestTypeDef = TypedDict(
    "PreviewPrivacyImpactInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "parameters": PreviewPrivacyImpactParametersInputTypeDef,
    },
)
PrivacyBudgetTypeDef = TypedDict(
    "PrivacyBudgetTypeDef",
    {
        "differentialPrivacy": NotRequired[DifferentialPrivacyPrivacyBudgetTypeDef],
    },
)
CreatePrivacyBudgetTemplateInputRequestTypeDef = TypedDict(
    "CreatePrivacyBudgetTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "autoRefresh": PrivacyBudgetTemplateAutoRefreshType,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "parameters": PrivacyBudgetTemplateParametersInputTypeDef,
        "tags": NotRequired[Mapping[str, str]],
    },
)
CollaborationPrivacyBudgetTemplateTypeDef = TypedDict(
    "CollaborationPrivacyBudgetTemplateTypeDef",
    {
        "id": str,
        "arn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "creatorAccountId": str,
        "createTime": datetime,
        "updateTime": datetime,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "autoRefresh": PrivacyBudgetTemplateAutoRefreshType,
        "parameters": PrivacyBudgetTemplateParametersOutputTypeDef,
    },
)
PrivacyBudgetTemplateTypeDef = TypedDict(
    "PrivacyBudgetTemplateTypeDef",
    {
        "id": str,
        "arn": str,
        "membershipId": str,
        "membershipArn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "createTime": datetime,
        "updateTime": datetime,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "autoRefresh": PrivacyBudgetTemplateAutoRefreshType,
        "parameters": PrivacyBudgetTemplateParametersOutputTypeDef,
    },
)
UpdatePrivacyBudgetTemplateInputRequestTypeDef = TypedDict(
    "UpdatePrivacyBudgetTemplateInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "privacyBudgetTemplateIdentifier": str,
        "privacyBudgetType": Literal["DIFFERENTIAL_PRIVACY"],
        "parameters": NotRequired[PrivacyBudgetTemplateUpdateParametersTypeDef],
    },
)
ConfiguredTableTypeDef = TypedDict(
    "ConfiguredTableTypeDef",
    {
        "id": str,
        "arn": str,
        "name": str,
        "tableReference": TableReferenceTypeDef,
        "createTime": datetime,
        "updateTime": datetime,
        "analysisRuleTypes": List[ConfiguredTableAnalysisRuleTypeType],
        "analysisMethod": Literal["DIRECT_QUERY"],
        "allowedColumns": List[str],
        "description": NotRequired[str],
    },
)
CreateConfiguredTableInputRequestTypeDef = TypedDict(
    "CreateConfiguredTableInputRequestTypeDef",
    {
        "name": str,
        "tableReference": TableReferenceTypeDef,
        "allowedColumns": Sequence[str],
        "analysisMethod": Literal["DIRECT_QUERY"],
        "description": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
MembershipSummaryTypeDef = TypedDict(
    "MembershipSummaryTypeDef",
    {
        "id": str,
        "arn": str,
        "collaborationArn": str,
        "collaborationId": str,
        "collaborationCreatorAccountId": str,
        "collaborationCreatorDisplayName": str,
        "collaborationName": str,
        "createTime": datetime,
        "updateTime": datetime,
        "status": MembershipStatusType,
        "memberAbilities": List[MemberAbilityType],
        "paymentConfiguration": MembershipPaymentConfigurationTypeDef,
    },
)
MembershipProtectedQueryResultConfigurationTypeDef = TypedDict(
    "MembershipProtectedQueryResultConfigurationTypeDef",
    {
        "outputConfiguration": MembershipProtectedQueryOutputConfigurationTypeDef,
        "roleArn": NotRequired[str],
    },
)
ProtectedQueryResultConfigurationTypeDef = TypedDict(
    "ProtectedQueryResultConfigurationTypeDef",
    {
        "outputConfiguration": ProtectedQueryOutputConfigurationTypeDef,
    },
)
MemberSpecificationTypeDef = TypedDict(
    "MemberSpecificationTypeDef",
    {
        "accountId": str,
        "memberAbilities": Sequence[MemberAbilityType],
        "displayName": str,
        "paymentConfiguration": NotRequired[PaymentConfigurationTypeDef],
    },
)
MemberSummaryTypeDef = TypedDict(
    "MemberSummaryTypeDef",
    {
        "accountId": str,
        "status": MemberStatusType,
        "displayName": str,
        "abilities": List[MemberAbilityType],
        "createTime": datetime,
        "updateTime": datetime,
        "paymentConfiguration": PaymentConfigurationTypeDef,
        "membershipId": NotRequired[str],
        "membershipArn": NotRequired[str],
    },
)
ProtectedQueryResultTypeDef = TypedDict(
    "ProtectedQueryResultTypeDef",
    {
        "output": ProtectedQueryOutputTypeDef,
    },
)
SchemaTypeDef = TypedDict(
    "SchemaTypeDef",
    {
        "columns": List[ColumnTypeDef],
        "partitionKeys": List[ColumnTypeDef],
        "analysisRuleTypes": List[AnalysisRuleTypeType],
        "creatorAccountId": str,
        "name": str,
        "collaborationId": str,
        "collaborationArn": str,
        "description": str,
        "createTime": datetime,
        "updateTime": datetime,
        "type": Literal["TABLE"],
        "schemaStatusDetails": List[SchemaStatusDetailTypeDef],
        "analysisMethod": NotRequired[Literal["DIRECT_QUERY"]],
    },
)
AnalysisRulePolicyV1TypeDef = TypedDict(
    "AnalysisRulePolicyV1TypeDef",
    {
        "list": NotRequired[AnalysisRuleListTypeDef],
        "aggregation": NotRequired[AnalysisRuleAggregationTypeDef],
        "custom": NotRequired[AnalysisRuleCustomTypeDef],
    },
)
ConfiguredTableAnalysisRulePolicyV1TypeDef = TypedDict(
    "ConfiguredTableAnalysisRulePolicyV1TypeDef",
    {
        "list": NotRequired[AnalysisRuleListTypeDef],
        "aggregation": NotRequired[AnalysisRuleAggregationTypeDef],
        "custom": NotRequired[AnalysisRuleCustomTypeDef],
    },
)
PreviewPrivacyImpactOutputTypeDef = TypedDict(
    "PreviewPrivacyImpactOutputTypeDef",
    {
        "privacyImpact": PrivacyImpactTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CollaborationPrivacyBudgetSummaryTypeDef = TypedDict(
    "CollaborationPrivacyBudgetSummaryTypeDef",
    {
        "id": str,
        "privacyBudgetTemplateId": str,
        "privacyBudgetTemplateArn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "creatorAccountId": str,
        "type": Literal["DIFFERENTIAL_PRIVACY"],
        "createTime": datetime,
        "updateTime": datetime,
        "budget": PrivacyBudgetTypeDef,
    },
)
PrivacyBudgetSummaryTypeDef = TypedDict(
    "PrivacyBudgetSummaryTypeDef",
    {
        "id": str,
        "privacyBudgetTemplateId": str,
        "privacyBudgetTemplateArn": str,
        "membershipId": str,
        "membershipArn": str,
        "collaborationId": str,
        "collaborationArn": str,
        "type": Literal["DIFFERENTIAL_PRIVACY"],
        "createTime": datetime,
        "updateTime": datetime,
        "budget": PrivacyBudgetTypeDef,
    },
)
GetCollaborationPrivacyBudgetTemplateOutputTypeDef = TypedDict(
    "GetCollaborationPrivacyBudgetTemplateOutputTypeDef",
    {
        "collaborationPrivacyBudgetTemplate": CollaborationPrivacyBudgetTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePrivacyBudgetTemplateOutputTypeDef = TypedDict(
    "CreatePrivacyBudgetTemplateOutputTypeDef",
    {
        "privacyBudgetTemplate": PrivacyBudgetTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPrivacyBudgetTemplateOutputTypeDef = TypedDict(
    "GetPrivacyBudgetTemplateOutputTypeDef",
    {
        "privacyBudgetTemplate": PrivacyBudgetTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePrivacyBudgetTemplateOutputTypeDef = TypedDict(
    "UpdatePrivacyBudgetTemplateOutputTypeDef",
    {
        "privacyBudgetTemplate": PrivacyBudgetTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateConfiguredTableOutputTypeDef = TypedDict(
    "CreateConfiguredTableOutputTypeDef",
    {
        "configuredTable": ConfiguredTableTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetConfiguredTableOutputTypeDef = TypedDict(
    "GetConfiguredTableOutputTypeDef",
    {
        "configuredTable": ConfiguredTableTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateConfiguredTableOutputTypeDef = TypedDict(
    "UpdateConfiguredTableOutputTypeDef",
    {
        "configuredTable": ConfiguredTableTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListMembershipsOutputTypeDef = TypedDict(
    "ListMembershipsOutputTypeDef",
    {
        "nextToken": str,
        "membershipSummaries": List[MembershipSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateMembershipInputRequestTypeDef = TypedDict(
    "CreateMembershipInputRequestTypeDef",
    {
        "collaborationIdentifier": str,
        "queryLogStatus": MembershipQueryLogStatusType,
        "tags": NotRequired[Mapping[str, str]],
        "defaultResultConfiguration": NotRequired[
            MembershipProtectedQueryResultConfigurationTypeDef
        ],
        "paymentConfiguration": NotRequired[MembershipPaymentConfigurationTypeDef],
    },
)
MembershipTypeDef = TypedDict(
    "MembershipTypeDef",
    {
        "id": str,
        "arn": str,
        "collaborationArn": str,
        "collaborationId": str,
        "collaborationCreatorAccountId": str,
        "collaborationCreatorDisplayName": str,
        "collaborationName": str,
        "createTime": datetime,
        "updateTime": datetime,
        "status": MembershipStatusType,
        "memberAbilities": List[MemberAbilityType],
        "queryLogStatus": MembershipQueryLogStatusType,
        "paymentConfiguration": MembershipPaymentConfigurationTypeDef,
        "defaultResultConfiguration": NotRequired[
            MembershipProtectedQueryResultConfigurationTypeDef
        ],
    },
)
UpdateMembershipInputRequestTypeDef = TypedDict(
    "UpdateMembershipInputRequestTypeDef",
    {
        "membershipIdentifier": str,
        "queryLogStatus": NotRequired[MembershipQueryLogStatusType],
        "defaultResultConfiguration": NotRequired[
            MembershipProtectedQueryResultConfigurationTypeDef
        ],
    },
)
StartProtectedQueryInputRequestTypeDef = TypedDict(
    "StartProtectedQueryInputRequestTypeDef",
    {
        "type": Literal["SQL"],
        "membershipIdentifier": str,
        "sqlParameters": ProtectedQuerySQLParametersTypeDef,
        "resultConfiguration": NotRequired[ProtectedQueryResultConfigurationTypeDef],
    },
)
CreateCollaborationInputRequestTypeDef = TypedDict(
    "CreateCollaborationInputRequestTypeDef",
    {
        "members": Sequence[MemberSpecificationTypeDef],
        "name": str,
        "description": str,
        "creatorMemberAbilities": Sequence[MemberAbilityType],
        "creatorDisplayName": str,
        "queryLogStatus": CollaborationQueryLogStatusType,
        "dataEncryptionMetadata": NotRequired[DataEncryptionMetadataTypeDef],
        "tags": NotRequired[Mapping[str, str]],
        "creatorPaymentConfiguration": NotRequired[PaymentConfigurationTypeDef],
    },
)
ListMembersOutputTypeDef = TypedDict(
    "ListMembersOutputTypeDef",
    {
        "nextToken": str,
        "memberSummaries": List[MemberSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ProtectedQueryTypeDef = TypedDict(
    "ProtectedQueryTypeDef",
    {
        "id": str,
        "membershipId": str,
        "membershipArn": str,
        "createTime": datetime,
        "status": ProtectedQueryStatusType,
        "sqlParameters": NotRequired[ProtectedQuerySQLParametersTypeDef],
        "resultConfiguration": NotRequired[ProtectedQueryResultConfigurationTypeDef],
        "statistics": NotRequired[ProtectedQueryStatisticsTypeDef],
        "result": NotRequired[ProtectedQueryResultTypeDef],
        "error": NotRequired[ProtectedQueryErrorTypeDef],
        "differentialPrivacy": NotRequired[DifferentialPrivacyParametersTypeDef],
    },
)
BatchGetSchemaOutputTypeDef = TypedDict(
    "BatchGetSchemaOutputTypeDef",
    {
        "schemas": List[SchemaTypeDef],
        "errors": List[BatchGetSchemaErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSchemaOutputTypeDef = TypedDict(
    "GetSchemaOutputTypeDef",
    {
        "schema": SchemaTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AnalysisRulePolicyTypeDef = TypedDict(
    "AnalysisRulePolicyTypeDef",
    {
        "v1": NotRequired[AnalysisRulePolicyV1TypeDef],
    },
)
ConfiguredTableAnalysisRulePolicyTypeDef = TypedDict(
    "ConfiguredTableAnalysisRulePolicyTypeDef",
    {
        "v1": NotRequired[ConfiguredTableAnalysisRulePolicyV1TypeDef],
    },
)
ListCollaborationPrivacyBudgetsOutputTypeDef = TypedDict(
    "ListCollaborationPrivacyBudgetsOutputTypeDef",
    {
        "collaborationPrivacyBudgetSummaries": List[CollaborationPrivacyBudgetSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPrivacyBudgetsOutputTypeDef = TypedDict(
    "ListPrivacyBudgetsOutputTypeDef",
    {
        "privacyBudgetSummaries": List[PrivacyBudgetSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateMembershipOutputTypeDef = TypedDict(
    "CreateMembershipOutputTypeDef",
    {
        "membership": MembershipTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetMembershipOutputTypeDef = TypedDict(
    "GetMembershipOutputTypeDef",
    {
        "membership": MembershipTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateMembershipOutputTypeDef = TypedDict(
    "UpdateMembershipOutputTypeDef",
    {
        "membership": MembershipTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetProtectedQueryOutputTypeDef = TypedDict(
    "GetProtectedQueryOutputTypeDef",
    {
        "protectedQuery": ProtectedQueryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartProtectedQueryOutputTypeDef = TypedDict(
    "StartProtectedQueryOutputTypeDef",
    {
        "protectedQuery": ProtectedQueryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateProtectedQueryOutputTypeDef = TypedDict(
    "UpdateProtectedQueryOutputTypeDef",
    {
        "protectedQuery": ProtectedQueryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AnalysisRuleTypeDef = TypedDict(
    "AnalysisRuleTypeDef",
    {
        "collaborationId": str,
        "type": AnalysisRuleTypeType,
        "name": str,
        "createTime": datetime,
        "updateTime": datetime,
        "policy": AnalysisRulePolicyTypeDef,
    },
)
ConfiguredTableAnalysisRuleTypeDef = TypedDict(
    "ConfiguredTableAnalysisRuleTypeDef",
    {
        "configuredTableId": str,
        "configuredTableArn": str,
        "policy": ConfiguredTableAnalysisRulePolicyTypeDef,
        "type": ConfiguredTableAnalysisRuleTypeType,
        "createTime": datetime,
        "updateTime": datetime,
    },
)
CreateConfiguredTableAnalysisRuleInputRequestTypeDef = TypedDict(
    "CreateConfiguredTableAnalysisRuleInputRequestTypeDef",
    {
        "configuredTableIdentifier": str,
        "analysisRuleType": ConfiguredTableAnalysisRuleTypeType,
        "analysisRulePolicy": ConfiguredTableAnalysisRulePolicyTypeDef,
    },
)
UpdateConfiguredTableAnalysisRuleInputRequestTypeDef = TypedDict(
    "UpdateConfiguredTableAnalysisRuleInputRequestTypeDef",
    {
        "configuredTableIdentifier": str,
        "analysisRuleType": ConfiguredTableAnalysisRuleTypeType,
        "analysisRulePolicy": ConfiguredTableAnalysisRulePolicyTypeDef,
    },
)
BatchGetSchemaAnalysisRuleOutputTypeDef = TypedDict(
    "BatchGetSchemaAnalysisRuleOutputTypeDef",
    {
        "analysisRules": List[AnalysisRuleTypeDef],
        "errors": List[BatchGetSchemaAnalysisRuleErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSchemaAnalysisRuleOutputTypeDef = TypedDict(
    "GetSchemaAnalysisRuleOutputTypeDef",
    {
        "analysisRule": AnalysisRuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateConfiguredTableAnalysisRuleOutputTypeDef = TypedDict(
    "CreateConfiguredTableAnalysisRuleOutputTypeDef",
    {
        "analysisRule": ConfiguredTableAnalysisRuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetConfiguredTableAnalysisRuleOutputTypeDef = TypedDict(
    "GetConfiguredTableAnalysisRuleOutputTypeDef",
    {
        "analysisRule": ConfiguredTableAnalysisRuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateConfiguredTableAnalysisRuleOutputTypeDef = TypedDict(
    "UpdateConfiguredTableAnalysisRuleOutputTypeDef",
    {
        "analysisRule": ConfiguredTableAnalysisRuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

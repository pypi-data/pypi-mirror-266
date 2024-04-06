"""
Type annotations for verifiedpermissions service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/type_defs/)

Usage::

    ```python
    from mypy_boto3_verifiedpermissions.type_defs import ActionIdentifierTypeDef

    data: ActionIdentifierTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence

from .literals import DecisionType, PolicyTypeType, ValidationModeType

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
    "ActionIdentifierTypeDef",
    "EntityIdentifierTypeDef",
    "ContextDefinitionTypeDef",
    "DeterminingPolicyItemTypeDef",
    "EvaluationErrorItemTypeDef",
    "ResponseMetadataTypeDef",
    "CognitoGroupConfigurationDetailTypeDef",
    "CognitoGroupConfigurationItemTypeDef",
    "CognitoGroupConfigurationTypeDef",
    "ValidationSettingsTypeDef",
    "CreatePolicyTemplateInputRequestTypeDef",
    "DeleteIdentitySourceInputRequestTypeDef",
    "DeletePolicyInputRequestTypeDef",
    "DeletePolicyStoreInputRequestTypeDef",
    "DeletePolicyTemplateInputRequestTypeDef",
    "GetIdentitySourceInputRequestTypeDef",
    "IdentitySourceDetailsTypeDef",
    "GetPolicyInputRequestTypeDef",
    "GetPolicyStoreInputRequestTypeDef",
    "GetPolicyTemplateInputRequestTypeDef",
    "GetSchemaInputRequestTypeDef",
    "IdentitySourceFilterTypeDef",
    "IdentitySourceItemDetailsTypeDef",
    "PaginatorConfigTypeDef",
    "ListPolicyStoresInputRequestTypeDef",
    "PolicyStoreItemTypeDef",
    "ListPolicyTemplatesInputRequestTypeDef",
    "PolicyTemplateItemTypeDef",
    "StaticPolicyDefinitionDetailTypeDef",
    "StaticPolicyDefinitionItemTypeDef",
    "StaticPolicyDefinitionTypeDef",
    "SchemaDefinitionTypeDef",
    "UpdateCognitoGroupConfigurationTypeDef",
    "UpdateStaticPolicyDefinitionTypeDef",
    "UpdatePolicyTemplateInputRequestTypeDef",
    "AttributeValueTypeDef",
    "EntityItemTypeDef",
    "EntityReferenceTypeDef",
    "TemplateLinkedPolicyDefinitionDetailTypeDef",
    "TemplateLinkedPolicyDefinitionItemTypeDef",
    "TemplateLinkedPolicyDefinitionTypeDef",
    "BatchIsAuthorizedInputItemTypeDef",
    "BatchIsAuthorizedWithTokenInputItemTypeDef",
    "CreateIdentitySourceOutputTypeDef",
    "CreatePolicyOutputTypeDef",
    "CreatePolicyStoreOutputTypeDef",
    "CreatePolicyTemplateOutputTypeDef",
    "GetPolicyTemplateOutputTypeDef",
    "GetSchemaOutputTypeDef",
    "IsAuthorizedOutputTypeDef",
    "IsAuthorizedWithTokenOutputTypeDef",
    "PutSchemaOutputTypeDef",
    "UpdateIdentitySourceOutputTypeDef",
    "UpdatePolicyOutputTypeDef",
    "UpdatePolicyStoreOutputTypeDef",
    "UpdatePolicyTemplateOutputTypeDef",
    "CognitoUserPoolConfigurationDetailTypeDef",
    "CognitoUserPoolConfigurationItemTypeDef",
    "CognitoUserPoolConfigurationTypeDef",
    "CreatePolicyStoreInputRequestTypeDef",
    "GetPolicyStoreOutputTypeDef",
    "UpdatePolicyStoreInputRequestTypeDef",
    "ListIdentitySourcesInputRequestTypeDef",
    "ListIdentitySourcesInputListIdentitySourcesPaginateTypeDef",
    "ListPolicyStoresInputListPolicyStoresPaginateTypeDef",
    "ListPolicyTemplatesInputListPolicyTemplatesPaginateTypeDef",
    "ListPolicyStoresOutputTypeDef",
    "ListPolicyTemplatesOutputTypeDef",
    "PutSchemaInputRequestTypeDef",
    "UpdateCognitoUserPoolConfigurationTypeDef",
    "UpdatePolicyDefinitionTypeDef",
    "EntitiesDefinitionTypeDef",
    "PolicyFilterTypeDef",
    "PolicyDefinitionDetailTypeDef",
    "PolicyDefinitionItemTypeDef",
    "PolicyDefinitionTypeDef",
    "BatchIsAuthorizedOutputItemTypeDef",
    "BatchIsAuthorizedWithTokenOutputItemTypeDef",
    "ConfigurationDetailTypeDef",
    "ConfigurationItemTypeDef",
    "ConfigurationTypeDef",
    "UpdateConfigurationTypeDef",
    "UpdatePolicyInputRequestTypeDef",
    "BatchIsAuthorizedInputRequestTypeDef",
    "BatchIsAuthorizedWithTokenInputRequestTypeDef",
    "IsAuthorizedInputRequestTypeDef",
    "IsAuthorizedWithTokenInputRequestTypeDef",
    "ListPoliciesInputListPoliciesPaginateTypeDef",
    "ListPoliciesInputRequestTypeDef",
    "GetPolicyOutputTypeDef",
    "PolicyItemTypeDef",
    "CreatePolicyInputRequestTypeDef",
    "BatchIsAuthorizedOutputTypeDef",
    "BatchIsAuthorizedWithTokenOutputTypeDef",
    "GetIdentitySourceOutputTypeDef",
    "IdentitySourceItemTypeDef",
    "CreateIdentitySourceInputRequestTypeDef",
    "UpdateIdentitySourceInputRequestTypeDef",
    "ListPoliciesOutputTypeDef",
    "ListIdentitySourcesOutputTypeDef",
)

ActionIdentifierTypeDef = TypedDict(
    "ActionIdentifierTypeDef",
    {
        "actionType": str,
        "actionId": str,
    },
)
EntityIdentifierTypeDef = TypedDict(
    "EntityIdentifierTypeDef",
    {
        "entityType": str,
        "entityId": str,
    },
)
ContextDefinitionTypeDef = TypedDict(
    "ContextDefinitionTypeDef",
    {
        "contextMap": NotRequired[Mapping[str, "AttributeValueTypeDef"]],
    },
)
DeterminingPolicyItemTypeDef = TypedDict(
    "DeterminingPolicyItemTypeDef",
    {
        "policyId": str,
    },
)
EvaluationErrorItemTypeDef = TypedDict(
    "EvaluationErrorItemTypeDef",
    {
        "errorDescription": str,
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
CognitoGroupConfigurationDetailTypeDef = TypedDict(
    "CognitoGroupConfigurationDetailTypeDef",
    {
        "groupEntityType": NotRequired[str],
    },
)
CognitoGroupConfigurationItemTypeDef = TypedDict(
    "CognitoGroupConfigurationItemTypeDef",
    {
        "groupEntityType": NotRequired[str],
    },
)
CognitoGroupConfigurationTypeDef = TypedDict(
    "CognitoGroupConfigurationTypeDef",
    {
        "groupEntityType": str,
    },
)
ValidationSettingsTypeDef = TypedDict(
    "ValidationSettingsTypeDef",
    {
        "mode": ValidationModeType,
    },
)
CreatePolicyTemplateInputRequestTypeDef = TypedDict(
    "CreatePolicyTemplateInputRequestTypeDef",
    {
        "policyStoreId": str,
        "statement": str,
        "clientToken": NotRequired[str],
        "description": NotRequired[str],
    },
)
DeleteIdentitySourceInputRequestTypeDef = TypedDict(
    "DeleteIdentitySourceInputRequestTypeDef",
    {
        "policyStoreId": str,
        "identitySourceId": str,
    },
)
DeletePolicyInputRequestTypeDef = TypedDict(
    "DeletePolicyInputRequestTypeDef",
    {
        "policyStoreId": str,
        "policyId": str,
    },
)
DeletePolicyStoreInputRequestTypeDef = TypedDict(
    "DeletePolicyStoreInputRequestTypeDef",
    {
        "policyStoreId": str,
    },
)
DeletePolicyTemplateInputRequestTypeDef = TypedDict(
    "DeletePolicyTemplateInputRequestTypeDef",
    {
        "policyStoreId": str,
        "policyTemplateId": str,
    },
)
GetIdentitySourceInputRequestTypeDef = TypedDict(
    "GetIdentitySourceInputRequestTypeDef",
    {
        "policyStoreId": str,
        "identitySourceId": str,
    },
)
IdentitySourceDetailsTypeDef = TypedDict(
    "IdentitySourceDetailsTypeDef",
    {
        "clientIds": NotRequired[List[str]],
        "userPoolArn": NotRequired[str],
        "discoveryUrl": NotRequired[str],
        "openIdIssuer": NotRequired[Literal["COGNITO"]],
    },
)
GetPolicyInputRequestTypeDef = TypedDict(
    "GetPolicyInputRequestTypeDef",
    {
        "policyStoreId": str,
        "policyId": str,
    },
)
GetPolicyStoreInputRequestTypeDef = TypedDict(
    "GetPolicyStoreInputRequestTypeDef",
    {
        "policyStoreId": str,
    },
)
GetPolicyTemplateInputRequestTypeDef = TypedDict(
    "GetPolicyTemplateInputRequestTypeDef",
    {
        "policyStoreId": str,
        "policyTemplateId": str,
    },
)
GetSchemaInputRequestTypeDef = TypedDict(
    "GetSchemaInputRequestTypeDef",
    {
        "policyStoreId": str,
    },
)
IdentitySourceFilterTypeDef = TypedDict(
    "IdentitySourceFilterTypeDef",
    {
        "principalEntityType": NotRequired[str],
    },
)
IdentitySourceItemDetailsTypeDef = TypedDict(
    "IdentitySourceItemDetailsTypeDef",
    {
        "clientIds": NotRequired[List[str]],
        "userPoolArn": NotRequired[str],
        "discoveryUrl": NotRequired[str],
        "openIdIssuer": NotRequired[Literal["COGNITO"]],
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
ListPolicyStoresInputRequestTypeDef = TypedDict(
    "ListPolicyStoresInputRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
PolicyStoreItemTypeDef = TypedDict(
    "PolicyStoreItemTypeDef",
    {
        "policyStoreId": str,
        "arn": str,
        "createdDate": datetime,
        "lastUpdatedDate": NotRequired[datetime],
        "description": NotRequired[str],
    },
)
ListPolicyTemplatesInputRequestTypeDef = TypedDict(
    "ListPolicyTemplatesInputRequestTypeDef",
    {
        "policyStoreId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
PolicyTemplateItemTypeDef = TypedDict(
    "PolicyTemplateItemTypeDef",
    {
        "policyStoreId": str,
        "policyTemplateId": str,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "description": NotRequired[str],
    },
)
StaticPolicyDefinitionDetailTypeDef = TypedDict(
    "StaticPolicyDefinitionDetailTypeDef",
    {
        "statement": str,
        "description": NotRequired[str],
    },
)
StaticPolicyDefinitionItemTypeDef = TypedDict(
    "StaticPolicyDefinitionItemTypeDef",
    {
        "description": NotRequired[str],
    },
)
StaticPolicyDefinitionTypeDef = TypedDict(
    "StaticPolicyDefinitionTypeDef",
    {
        "statement": str,
        "description": NotRequired[str],
    },
)
SchemaDefinitionTypeDef = TypedDict(
    "SchemaDefinitionTypeDef",
    {
        "cedarJson": NotRequired[str],
    },
)
UpdateCognitoGroupConfigurationTypeDef = TypedDict(
    "UpdateCognitoGroupConfigurationTypeDef",
    {
        "groupEntityType": str,
    },
)
UpdateStaticPolicyDefinitionTypeDef = TypedDict(
    "UpdateStaticPolicyDefinitionTypeDef",
    {
        "statement": str,
        "description": NotRequired[str],
    },
)
UpdatePolicyTemplateInputRequestTypeDef = TypedDict(
    "UpdatePolicyTemplateInputRequestTypeDef",
    {
        "policyStoreId": str,
        "policyTemplateId": str,
        "statement": str,
        "description": NotRequired[str],
    },
)
AttributeValueTypeDef = TypedDict(
    "AttributeValueTypeDef",
    {
        "boolean": NotRequired[bool],
        "entityIdentifier": NotRequired[EntityIdentifierTypeDef],
        "long": NotRequired[int],
        "string": NotRequired[str],
        "set": NotRequired[Sequence[Dict[str, Any]]],
        "record": NotRequired[Mapping[str, Dict[str, Any]]],
    },
)
EntityItemTypeDef = TypedDict(
    "EntityItemTypeDef",
    {
        "identifier": EntityIdentifierTypeDef,
        "attributes": NotRequired[Mapping[str, "AttributeValueTypeDef"]],
        "parents": NotRequired[Sequence[EntityIdentifierTypeDef]],
    },
)
EntityReferenceTypeDef = TypedDict(
    "EntityReferenceTypeDef",
    {
        "unspecified": NotRequired[bool],
        "identifier": NotRequired[EntityIdentifierTypeDef],
    },
)
TemplateLinkedPolicyDefinitionDetailTypeDef = TypedDict(
    "TemplateLinkedPolicyDefinitionDetailTypeDef",
    {
        "policyTemplateId": str,
        "principal": NotRequired[EntityIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
    },
)
TemplateLinkedPolicyDefinitionItemTypeDef = TypedDict(
    "TemplateLinkedPolicyDefinitionItemTypeDef",
    {
        "policyTemplateId": str,
        "principal": NotRequired[EntityIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
    },
)
TemplateLinkedPolicyDefinitionTypeDef = TypedDict(
    "TemplateLinkedPolicyDefinitionTypeDef",
    {
        "policyTemplateId": str,
        "principal": NotRequired[EntityIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
    },
)
BatchIsAuthorizedInputItemTypeDef = TypedDict(
    "BatchIsAuthorizedInputItemTypeDef",
    {
        "principal": NotRequired[EntityIdentifierTypeDef],
        "action": NotRequired[ActionIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
        "context": NotRequired[ContextDefinitionTypeDef],
    },
)
BatchIsAuthorizedWithTokenInputItemTypeDef = TypedDict(
    "BatchIsAuthorizedWithTokenInputItemTypeDef",
    {
        "action": NotRequired[ActionIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
        "context": NotRequired[ContextDefinitionTypeDef],
    },
)
CreateIdentitySourceOutputTypeDef = TypedDict(
    "CreateIdentitySourceOutputTypeDef",
    {
        "createdDate": datetime,
        "identitySourceId": str,
        "lastUpdatedDate": datetime,
        "policyStoreId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePolicyOutputTypeDef = TypedDict(
    "CreatePolicyOutputTypeDef",
    {
        "policyStoreId": str,
        "policyId": str,
        "policyType": PolicyTypeType,
        "principal": EntityIdentifierTypeDef,
        "resource": EntityIdentifierTypeDef,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePolicyStoreOutputTypeDef = TypedDict(
    "CreatePolicyStoreOutputTypeDef",
    {
        "policyStoreId": str,
        "arn": str,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePolicyTemplateOutputTypeDef = TypedDict(
    "CreatePolicyTemplateOutputTypeDef",
    {
        "policyStoreId": str,
        "policyTemplateId": str,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPolicyTemplateOutputTypeDef = TypedDict(
    "GetPolicyTemplateOutputTypeDef",
    {
        "policyStoreId": str,
        "policyTemplateId": str,
        "description": str,
        "statement": str,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSchemaOutputTypeDef = TypedDict(
    "GetSchemaOutputTypeDef",
    {
        "policyStoreId": str,
        "schema": str,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "namespaces": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IsAuthorizedOutputTypeDef = TypedDict(
    "IsAuthorizedOutputTypeDef",
    {
        "decision": DecisionType,
        "determiningPolicies": List[DeterminingPolicyItemTypeDef],
        "errors": List[EvaluationErrorItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IsAuthorizedWithTokenOutputTypeDef = TypedDict(
    "IsAuthorizedWithTokenOutputTypeDef",
    {
        "decision": DecisionType,
        "determiningPolicies": List[DeterminingPolicyItemTypeDef],
        "errors": List[EvaluationErrorItemTypeDef],
        "principal": EntityIdentifierTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutSchemaOutputTypeDef = TypedDict(
    "PutSchemaOutputTypeDef",
    {
        "policyStoreId": str,
        "namespaces": List[str],
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateIdentitySourceOutputTypeDef = TypedDict(
    "UpdateIdentitySourceOutputTypeDef",
    {
        "createdDate": datetime,
        "identitySourceId": str,
        "lastUpdatedDate": datetime,
        "policyStoreId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePolicyOutputTypeDef = TypedDict(
    "UpdatePolicyOutputTypeDef",
    {
        "policyStoreId": str,
        "policyId": str,
        "policyType": PolicyTypeType,
        "principal": EntityIdentifierTypeDef,
        "resource": EntityIdentifierTypeDef,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePolicyStoreOutputTypeDef = TypedDict(
    "UpdatePolicyStoreOutputTypeDef",
    {
        "policyStoreId": str,
        "arn": str,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePolicyTemplateOutputTypeDef = TypedDict(
    "UpdatePolicyTemplateOutputTypeDef",
    {
        "policyStoreId": str,
        "policyTemplateId": str,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CognitoUserPoolConfigurationDetailTypeDef = TypedDict(
    "CognitoUserPoolConfigurationDetailTypeDef",
    {
        "userPoolArn": str,
        "clientIds": List[str],
        "issuer": str,
        "groupConfiguration": NotRequired[CognitoGroupConfigurationDetailTypeDef],
    },
)
CognitoUserPoolConfigurationItemTypeDef = TypedDict(
    "CognitoUserPoolConfigurationItemTypeDef",
    {
        "userPoolArn": str,
        "clientIds": List[str],
        "issuer": str,
        "groupConfiguration": NotRequired[CognitoGroupConfigurationItemTypeDef],
    },
)
CognitoUserPoolConfigurationTypeDef = TypedDict(
    "CognitoUserPoolConfigurationTypeDef",
    {
        "userPoolArn": str,
        "clientIds": NotRequired[Sequence[str]],
        "groupConfiguration": NotRequired[CognitoGroupConfigurationTypeDef],
    },
)
CreatePolicyStoreInputRequestTypeDef = TypedDict(
    "CreatePolicyStoreInputRequestTypeDef",
    {
        "validationSettings": ValidationSettingsTypeDef,
        "clientToken": NotRequired[str],
        "description": NotRequired[str],
    },
)
GetPolicyStoreOutputTypeDef = TypedDict(
    "GetPolicyStoreOutputTypeDef",
    {
        "policyStoreId": str,
        "arn": str,
        "validationSettings": ValidationSettingsTypeDef,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "description": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePolicyStoreInputRequestTypeDef = TypedDict(
    "UpdatePolicyStoreInputRequestTypeDef",
    {
        "policyStoreId": str,
        "validationSettings": ValidationSettingsTypeDef,
        "description": NotRequired[str],
    },
)
ListIdentitySourcesInputRequestTypeDef = TypedDict(
    "ListIdentitySourcesInputRequestTypeDef",
    {
        "policyStoreId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "filters": NotRequired[Sequence[IdentitySourceFilterTypeDef]],
    },
)
ListIdentitySourcesInputListIdentitySourcesPaginateTypeDef = TypedDict(
    "ListIdentitySourcesInputListIdentitySourcesPaginateTypeDef",
    {
        "policyStoreId": str,
        "filters": NotRequired[Sequence[IdentitySourceFilterTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPolicyStoresInputListPolicyStoresPaginateTypeDef = TypedDict(
    "ListPolicyStoresInputListPolicyStoresPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPolicyTemplatesInputListPolicyTemplatesPaginateTypeDef = TypedDict(
    "ListPolicyTemplatesInputListPolicyTemplatesPaginateTypeDef",
    {
        "policyStoreId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPolicyStoresOutputTypeDef = TypedDict(
    "ListPolicyStoresOutputTypeDef",
    {
        "nextToken": str,
        "policyStores": List[PolicyStoreItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPolicyTemplatesOutputTypeDef = TypedDict(
    "ListPolicyTemplatesOutputTypeDef",
    {
        "nextToken": str,
        "policyTemplates": List[PolicyTemplateItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutSchemaInputRequestTypeDef = TypedDict(
    "PutSchemaInputRequestTypeDef",
    {
        "policyStoreId": str,
        "definition": SchemaDefinitionTypeDef,
    },
)
UpdateCognitoUserPoolConfigurationTypeDef = TypedDict(
    "UpdateCognitoUserPoolConfigurationTypeDef",
    {
        "userPoolArn": str,
        "clientIds": NotRequired[Sequence[str]],
        "groupConfiguration": NotRequired[UpdateCognitoGroupConfigurationTypeDef],
    },
)
UpdatePolicyDefinitionTypeDef = TypedDict(
    "UpdatePolicyDefinitionTypeDef",
    {
        "static": NotRequired[UpdateStaticPolicyDefinitionTypeDef],
    },
)
EntitiesDefinitionTypeDef = TypedDict(
    "EntitiesDefinitionTypeDef",
    {
        "entityList": NotRequired[Sequence[EntityItemTypeDef]],
    },
)
PolicyFilterTypeDef = TypedDict(
    "PolicyFilterTypeDef",
    {
        "principal": NotRequired[EntityReferenceTypeDef],
        "resource": NotRequired[EntityReferenceTypeDef],
        "policyType": NotRequired[PolicyTypeType],
        "policyTemplateId": NotRequired[str],
    },
)
PolicyDefinitionDetailTypeDef = TypedDict(
    "PolicyDefinitionDetailTypeDef",
    {
        "static": NotRequired[StaticPolicyDefinitionDetailTypeDef],
        "templateLinked": NotRequired[TemplateLinkedPolicyDefinitionDetailTypeDef],
    },
)
PolicyDefinitionItemTypeDef = TypedDict(
    "PolicyDefinitionItemTypeDef",
    {
        "static": NotRequired[StaticPolicyDefinitionItemTypeDef],
        "templateLinked": NotRequired[TemplateLinkedPolicyDefinitionItemTypeDef],
    },
)
PolicyDefinitionTypeDef = TypedDict(
    "PolicyDefinitionTypeDef",
    {
        "static": NotRequired[StaticPolicyDefinitionTypeDef],
        "templateLinked": NotRequired[TemplateLinkedPolicyDefinitionTypeDef],
    },
)
BatchIsAuthorizedOutputItemTypeDef = TypedDict(
    "BatchIsAuthorizedOutputItemTypeDef",
    {
        "request": BatchIsAuthorizedInputItemTypeDef,
        "decision": DecisionType,
        "determiningPolicies": List[DeterminingPolicyItemTypeDef],
        "errors": List[EvaluationErrorItemTypeDef],
    },
)
BatchIsAuthorizedWithTokenOutputItemTypeDef = TypedDict(
    "BatchIsAuthorizedWithTokenOutputItemTypeDef",
    {
        "request": BatchIsAuthorizedWithTokenInputItemTypeDef,
        "decision": DecisionType,
        "determiningPolicies": List[DeterminingPolicyItemTypeDef],
        "errors": List[EvaluationErrorItemTypeDef],
    },
)
ConfigurationDetailTypeDef = TypedDict(
    "ConfigurationDetailTypeDef",
    {
        "cognitoUserPoolConfiguration": NotRequired[CognitoUserPoolConfigurationDetailTypeDef],
    },
)
ConfigurationItemTypeDef = TypedDict(
    "ConfigurationItemTypeDef",
    {
        "cognitoUserPoolConfiguration": NotRequired[CognitoUserPoolConfigurationItemTypeDef],
    },
)
ConfigurationTypeDef = TypedDict(
    "ConfigurationTypeDef",
    {
        "cognitoUserPoolConfiguration": NotRequired[CognitoUserPoolConfigurationTypeDef],
    },
)
UpdateConfigurationTypeDef = TypedDict(
    "UpdateConfigurationTypeDef",
    {
        "cognitoUserPoolConfiguration": NotRequired[UpdateCognitoUserPoolConfigurationTypeDef],
    },
)
UpdatePolicyInputRequestTypeDef = TypedDict(
    "UpdatePolicyInputRequestTypeDef",
    {
        "policyStoreId": str,
        "policyId": str,
        "definition": UpdatePolicyDefinitionTypeDef,
    },
)
BatchIsAuthorizedInputRequestTypeDef = TypedDict(
    "BatchIsAuthorizedInputRequestTypeDef",
    {
        "policyStoreId": str,
        "requests": Sequence[BatchIsAuthorizedInputItemTypeDef],
        "entities": NotRequired[EntitiesDefinitionTypeDef],
    },
)
BatchIsAuthorizedWithTokenInputRequestTypeDef = TypedDict(
    "BatchIsAuthorizedWithTokenInputRequestTypeDef",
    {
        "policyStoreId": str,
        "requests": Sequence[BatchIsAuthorizedWithTokenInputItemTypeDef],
        "identityToken": NotRequired[str],
        "accessToken": NotRequired[str],
        "entities": NotRequired[EntitiesDefinitionTypeDef],
    },
)
IsAuthorizedInputRequestTypeDef = TypedDict(
    "IsAuthorizedInputRequestTypeDef",
    {
        "policyStoreId": str,
        "principal": NotRequired[EntityIdentifierTypeDef],
        "action": NotRequired[ActionIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
        "context": NotRequired[ContextDefinitionTypeDef],
        "entities": NotRequired[EntitiesDefinitionTypeDef],
    },
)
IsAuthorizedWithTokenInputRequestTypeDef = TypedDict(
    "IsAuthorizedWithTokenInputRequestTypeDef",
    {
        "policyStoreId": str,
        "identityToken": NotRequired[str],
        "accessToken": NotRequired[str],
        "action": NotRequired[ActionIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
        "context": NotRequired[ContextDefinitionTypeDef],
        "entities": NotRequired[EntitiesDefinitionTypeDef],
    },
)
ListPoliciesInputListPoliciesPaginateTypeDef = TypedDict(
    "ListPoliciesInputListPoliciesPaginateTypeDef",
    {
        "policyStoreId": str,
        "filter": NotRequired[PolicyFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPoliciesInputRequestTypeDef = TypedDict(
    "ListPoliciesInputRequestTypeDef",
    {
        "policyStoreId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "filter": NotRequired[PolicyFilterTypeDef],
    },
)
GetPolicyOutputTypeDef = TypedDict(
    "GetPolicyOutputTypeDef",
    {
        "policyStoreId": str,
        "policyId": str,
        "policyType": PolicyTypeType,
        "principal": EntityIdentifierTypeDef,
        "resource": EntityIdentifierTypeDef,
        "definition": PolicyDefinitionDetailTypeDef,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PolicyItemTypeDef = TypedDict(
    "PolicyItemTypeDef",
    {
        "policyStoreId": str,
        "policyId": str,
        "policyType": PolicyTypeType,
        "definition": PolicyDefinitionItemTypeDef,
        "createdDate": datetime,
        "lastUpdatedDate": datetime,
        "principal": NotRequired[EntityIdentifierTypeDef],
        "resource": NotRequired[EntityIdentifierTypeDef],
    },
)
CreatePolicyInputRequestTypeDef = TypedDict(
    "CreatePolicyInputRequestTypeDef",
    {
        "policyStoreId": str,
        "definition": PolicyDefinitionTypeDef,
        "clientToken": NotRequired[str],
    },
)
BatchIsAuthorizedOutputTypeDef = TypedDict(
    "BatchIsAuthorizedOutputTypeDef",
    {
        "results": List[BatchIsAuthorizedOutputItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchIsAuthorizedWithTokenOutputTypeDef = TypedDict(
    "BatchIsAuthorizedWithTokenOutputTypeDef",
    {
        "principal": EntityIdentifierTypeDef,
        "results": List[BatchIsAuthorizedWithTokenOutputItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetIdentitySourceOutputTypeDef = TypedDict(
    "GetIdentitySourceOutputTypeDef",
    {
        "createdDate": datetime,
        "details": IdentitySourceDetailsTypeDef,
        "identitySourceId": str,
        "lastUpdatedDate": datetime,
        "policyStoreId": str,
        "principalEntityType": str,
        "configuration": ConfigurationDetailTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IdentitySourceItemTypeDef = TypedDict(
    "IdentitySourceItemTypeDef",
    {
        "createdDate": datetime,
        "identitySourceId": str,
        "lastUpdatedDate": datetime,
        "policyStoreId": str,
        "principalEntityType": str,
        "details": NotRequired[IdentitySourceItemDetailsTypeDef],
        "configuration": NotRequired[ConfigurationItemTypeDef],
    },
)
CreateIdentitySourceInputRequestTypeDef = TypedDict(
    "CreateIdentitySourceInputRequestTypeDef",
    {
        "policyStoreId": str,
        "configuration": ConfigurationTypeDef,
        "clientToken": NotRequired[str],
        "principalEntityType": NotRequired[str],
    },
)
UpdateIdentitySourceInputRequestTypeDef = TypedDict(
    "UpdateIdentitySourceInputRequestTypeDef",
    {
        "policyStoreId": str,
        "identitySourceId": str,
        "updateConfiguration": UpdateConfigurationTypeDef,
        "principalEntityType": NotRequired[str],
    },
)
ListPoliciesOutputTypeDef = TypedDict(
    "ListPoliciesOutputTypeDef",
    {
        "nextToken": str,
        "policies": List[PolicyItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListIdentitySourcesOutputTypeDef = TypedDict(
    "ListIdentitySourcesOutputTypeDef",
    {
        "nextToken": str,
        "identitySources": List[IdentitySourceItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

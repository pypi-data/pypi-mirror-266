"""
Type annotations for b2bi service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_b2bi/type_defs/)

Usage::

    ```python
    from mypy_boto3_b2bi.type_defs import CapabilitySummaryTypeDef

    data: CapabilitySummaryTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Sequence

from .literals import (
    FileFormatType,
    LoggingType,
    TransformerJobStatusType,
    TransformerStatusType,
    X12TransactionSetType,
    X12VersionType,
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
    "CapabilitySummaryTypeDef",
    "S3LocationTypeDef",
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "DeleteCapabilityRequestRequestTypeDef",
    "DeletePartnershipRequestRequestTypeDef",
    "DeleteProfileRequestRequestTypeDef",
    "DeleteTransformerRequestRequestTypeDef",
    "X12DetailsTypeDef",
    "GetCapabilityRequestRequestTypeDef",
    "GetPartnershipRequestRequestTypeDef",
    "GetProfileRequestRequestTypeDef",
    "GetTransformerJobRequestRequestTypeDef",
    "GetTransformerRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "ListCapabilitiesRequestRequestTypeDef",
    "ListPartnershipsRequestRequestTypeDef",
    "PartnershipSummaryTypeDef",
    "ListProfilesRequestRequestTypeDef",
    "ProfileSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTransformersRequestRequestTypeDef",
    "TestMappingRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdatePartnershipRequestRequestTypeDef",
    "UpdateProfileRequestRequestTypeDef",
    "StartTransformerJobRequestRequestTypeDef",
    "CreatePartnershipRequestRequestTypeDef",
    "CreateProfileRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreatePartnershipResponseTypeDef",
    "CreateProfileResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetPartnershipResponseTypeDef",
    "GetProfileResponseTypeDef",
    "GetTransformerJobResponseTypeDef",
    "ListCapabilitiesResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "StartTransformerJobResponseTypeDef",
    "TestMappingResponseTypeDef",
    "TestParsingResponseTypeDef",
    "UpdatePartnershipResponseTypeDef",
    "UpdateProfileResponseTypeDef",
    "EdiTypeTypeDef",
    "ListCapabilitiesRequestListCapabilitiesPaginateTypeDef",
    "ListPartnershipsRequestListPartnershipsPaginateTypeDef",
    "ListProfilesRequestListProfilesPaginateTypeDef",
    "ListTransformersRequestListTransformersPaginateTypeDef",
    "ListPartnershipsResponseTypeDef",
    "ListProfilesResponseTypeDef",
    "CreateTransformerRequestRequestTypeDef",
    "CreateTransformerResponseTypeDef",
    "EdiConfigurationTypeDef",
    "GetTransformerResponseTypeDef",
    "TestParsingRequestRequestTypeDef",
    "TransformerSummaryTypeDef",
    "UpdateTransformerRequestRequestTypeDef",
    "UpdateTransformerResponseTypeDef",
    "CapabilityConfigurationTypeDef",
    "ListTransformersResponseTypeDef",
    "CreateCapabilityRequestRequestTypeDef",
    "CreateCapabilityResponseTypeDef",
    "GetCapabilityResponseTypeDef",
    "UpdateCapabilityRequestRequestTypeDef",
    "UpdateCapabilityResponseTypeDef",
)

CapabilitySummaryTypeDef = TypedDict(
    "CapabilitySummaryTypeDef",
    {
        "capabilityId": str,
        "name": str,
        "type": Literal["edi"],
        "createdAt": datetime,
        "modifiedAt": NotRequired[datetime],
    },
)
S3LocationTypeDef = TypedDict(
    "S3LocationTypeDef",
    {
        "bucketName": NotRequired[str],
        "key": NotRequired[str],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
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
DeleteCapabilityRequestRequestTypeDef = TypedDict(
    "DeleteCapabilityRequestRequestTypeDef",
    {
        "capabilityId": str,
    },
)
DeletePartnershipRequestRequestTypeDef = TypedDict(
    "DeletePartnershipRequestRequestTypeDef",
    {
        "partnershipId": str,
    },
)
DeleteProfileRequestRequestTypeDef = TypedDict(
    "DeleteProfileRequestRequestTypeDef",
    {
        "profileId": str,
    },
)
DeleteTransformerRequestRequestTypeDef = TypedDict(
    "DeleteTransformerRequestRequestTypeDef",
    {
        "transformerId": str,
    },
)
X12DetailsTypeDef = TypedDict(
    "X12DetailsTypeDef",
    {
        "transactionSet": NotRequired[X12TransactionSetType],
        "version": NotRequired[X12VersionType],
    },
)
GetCapabilityRequestRequestTypeDef = TypedDict(
    "GetCapabilityRequestRequestTypeDef",
    {
        "capabilityId": str,
    },
)
GetPartnershipRequestRequestTypeDef = TypedDict(
    "GetPartnershipRequestRequestTypeDef",
    {
        "partnershipId": str,
    },
)
GetProfileRequestRequestTypeDef = TypedDict(
    "GetProfileRequestRequestTypeDef",
    {
        "profileId": str,
    },
)
GetTransformerJobRequestRequestTypeDef = TypedDict(
    "GetTransformerJobRequestRequestTypeDef",
    {
        "transformerJobId": str,
        "transformerId": str,
    },
)
GetTransformerRequestRequestTypeDef = TypedDict(
    "GetTransformerRequestRequestTypeDef",
    {
        "transformerId": str,
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
ListCapabilitiesRequestRequestTypeDef = TypedDict(
    "ListCapabilitiesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListPartnershipsRequestRequestTypeDef = TypedDict(
    "ListPartnershipsRequestRequestTypeDef",
    {
        "profileId": NotRequired[str],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
PartnershipSummaryTypeDef = TypedDict(
    "PartnershipSummaryTypeDef",
    {
        "profileId": str,
        "partnershipId": str,
        "createdAt": datetime,
        "name": NotRequired[str],
        "capabilities": NotRequired[List[str]],
        "tradingPartnerId": NotRequired[str],
        "modifiedAt": NotRequired[datetime],
    },
)
ListProfilesRequestRequestTypeDef = TypedDict(
    "ListProfilesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ProfileSummaryTypeDef = TypedDict(
    "ProfileSummaryTypeDef",
    {
        "profileId": str,
        "name": str,
        "businessName": str,
        "createdAt": datetime,
        "logging": NotRequired[LoggingType],
        "logGroupName": NotRequired[str],
        "modifiedAt": NotRequired[datetime],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
    },
)
ListTransformersRequestRequestTypeDef = TypedDict(
    "ListTransformersRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
TestMappingRequestRequestTypeDef = TypedDict(
    "TestMappingRequestRequestTypeDef",
    {
        "inputFileContent": str,
        "mappingTemplate": str,
        "fileFormat": FileFormatType,
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "TagKeys": Sequence[str],
    },
)
UpdatePartnershipRequestRequestTypeDef = TypedDict(
    "UpdatePartnershipRequestRequestTypeDef",
    {
        "partnershipId": str,
        "name": NotRequired[str],
        "capabilities": NotRequired[Sequence[str]],
    },
)
UpdateProfileRequestRequestTypeDef = TypedDict(
    "UpdateProfileRequestRequestTypeDef",
    {
        "profileId": str,
        "name": NotRequired[str],
        "email": NotRequired[str],
        "phone": NotRequired[str],
        "businessName": NotRequired[str],
    },
)
StartTransformerJobRequestRequestTypeDef = TypedDict(
    "StartTransformerJobRequestRequestTypeDef",
    {
        "inputFile": S3LocationTypeDef,
        "outputLocation": S3LocationTypeDef,
        "transformerId": str,
        "clientToken": NotRequired[str],
    },
)
CreatePartnershipRequestRequestTypeDef = TypedDict(
    "CreatePartnershipRequestRequestTypeDef",
    {
        "profileId": str,
        "name": str,
        "email": str,
        "phone": NotRequired[str],
        "capabilities": NotRequired[Sequence[str]],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateProfileRequestRequestTypeDef = TypedDict(
    "CreateProfileRequestRequestTypeDef",
    {
        "name": str,
        "phone": str,
        "businessName": str,
        "logging": LoggingType,
        "email": NotRequired[str],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "Tags": Sequence[TagTypeDef],
    },
)
CreatePartnershipResponseTypeDef = TypedDict(
    "CreatePartnershipResponseTypeDef",
    {
        "profileId": str,
        "partnershipId": str,
        "partnershipArn": str,
        "name": str,
        "email": str,
        "phone": str,
        "capabilities": List[str],
        "tradingPartnerId": str,
        "createdAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProfileResponseTypeDef = TypedDict(
    "CreateProfileResponseTypeDef",
    {
        "profileId": str,
        "profileArn": str,
        "name": str,
        "businessName": str,
        "phone": str,
        "email": str,
        "logging": LoggingType,
        "logGroupName": str,
        "createdAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPartnershipResponseTypeDef = TypedDict(
    "GetPartnershipResponseTypeDef",
    {
        "profileId": str,
        "partnershipId": str,
        "partnershipArn": str,
        "name": str,
        "email": str,
        "phone": str,
        "capabilities": List[str],
        "tradingPartnerId": str,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetProfileResponseTypeDef = TypedDict(
    "GetProfileResponseTypeDef",
    {
        "profileId": str,
        "profileArn": str,
        "name": str,
        "email": str,
        "phone": str,
        "businessName": str,
        "logging": LoggingType,
        "logGroupName": str,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetTransformerJobResponseTypeDef = TypedDict(
    "GetTransformerJobResponseTypeDef",
    {
        "status": TransformerJobStatusType,
        "outputFiles": List[S3LocationTypeDef],
        "message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCapabilitiesResponseTypeDef = TypedDict(
    "ListCapabilitiesResponseTypeDef",
    {
        "capabilities": List[CapabilitySummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTransformerJobResponseTypeDef = TypedDict(
    "StartTransformerJobResponseTypeDef",
    {
        "transformerJobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestMappingResponseTypeDef = TypedDict(
    "TestMappingResponseTypeDef",
    {
        "mappedFileContent": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestParsingResponseTypeDef = TypedDict(
    "TestParsingResponseTypeDef",
    {
        "parsedFileContent": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePartnershipResponseTypeDef = TypedDict(
    "UpdatePartnershipResponseTypeDef",
    {
        "profileId": str,
        "partnershipId": str,
        "partnershipArn": str,
        "name": str,
        "email": str,
        "phone": str,
        "capabilities": List[str],
        "tradingPartnerId": str,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateProfileResponseTypeDef = TypedDict(
    "UpdateProfileResponseTypeDef",
    {
        "profileId": str,
        "profileArn": str,
        "name": str,
        "email": str,
        "phone": str,
        "businessName": str,
        "logging": LoggingType,
        "logGroupName": str,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EdiTypeTypeDef = TypedDict(
    "EdiTypeTypeDef",
    {
        "x12Details": NotRequired[X12DetailsTypeDef],
    },
)
ListCapabilitiesRequestListCapabilitiesPaginateTypeDef = TypedDict(
    "ListCapabilitiesRequestListCapabilitiesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPartnershipsRequestListPartnershipsPaginateTypeDef = TypedDict(
    "ListPartnershipsRequestListPartnershipsPaginateTypeDef",
    {
        "profileId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListProfilesRequestListProfilesPaginateTypeDef = TypedDict(
    "ListProfilesRequestListProfilesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTransformersRequestListTransformersPaginateTypeDef = TypedDict(
    "ListTransformersRequestListTransformersPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPartnershipsResponseTypeDef = TypedDict(
    "ListPartnershipsResponseTypeDef",
    {
        "partnerships": List[PartnershipSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListProfilesResponseTypeDef = TypedDict(
    "ListProfilesResponseTypeDef",
    {
        "profiles": List[ProfileSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTransformerRequestRequestTypeDef = TypedDict(
    "CreateTransformerRequestRequestTypeDef",
    {
        "name": str,
        "fileFormat": FileFormatType,
        "mappingTemplate": str,
        "ediType": EdiTypeTypeDef,
        "sampleDocument": NotRequired[str],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateTransformerResponseTypeDef = TypedDict(
    "CreateTransformerResponseTypeDef",
    {
        "transformerId": str,
        "transformerArn": str,
        "name": str,
        "fileFormat": FileFormatType,
        "mappingTemplate": str,
        "status": TransformerStatusType,
        "ediType": EdiTypeTypeDef,
        "sampleDocument": str,
        "createdAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EdiConfigurationTypeDef = TypedDict(
    "EdiConfigurationTypeDef",
    {
        "type": EdiTypeTypeDef,
        "inputLocation": S3LocationTypeDef,
        "outputLocation": S3LocationTypeDef,
        "transformerId": str,
    },
)
GetTransformerResponseTypeDef = TypedDict(
    "GetTransformerResponseTypeDef",
    {
        "transformerId": str,
        "transformerArn": str,
        "name": str,
        "fileFormat": FileFormatType,
        "mappingTemplate": str,
        "status": TransformerStatusType,
        "ediType": EdiTypeTypeDef,
        "sampleDocument": str,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestParsingRequestRequestTypeDef = TypedDict(
    "TestParsingRequestRequestTypeDef",
    {
        "inputFile": S3LocationTypeDef,
        "fileFormat": FileFormatType,
        "ediType": EdiTypeTypeDef,
    },
)
TransformerSummaryTypeDef = TypedDict(
    "TransformerSummaryTypeDef",
    {
        "transformerId": str,
        "name": str,
        "fileFormat": FileFormatType,
        "mappingTemplate": str,
        "status": TransformerStatusType,
        "ediType": EdiTypeTypeDef,
        "createdAt": datetime,
        "sampleDocument": NotRequired[str],
        "modifiedAt": NotRequired[datetime],
    },
)
UpdateTransformerRequestRequestTypeDef = TypedDict(
    "UpdateTransformerRequestRequestTypeDef",
    {
        "transformerId": str,
        "name": NotRequired[str],
        "fileFormat": NotRequired[FileFormatType],
        "mappingTemplate": NotRequired[str],
        "status": NotRequired[TransformerStatusType],
        "ediType": NotRequired[EdiTypeTypeDef],
        "sampleDocument": NotRequired[str],
    },
)
UpdateTransformerResponseTypeDef = TypedDict(
    "UpdateTransformerResponseTypeDef",
    {
        "transformerId": str,
        "transformerArn": str,
        "name": str,
        "fileFormat": FileFormatType,
        "mappingTemplate": str,
        "status": TransformerStatusType,
        "ediType": EdiTypeTypeDef,
        "sampleDocument": str,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CapabilityConfigurationTypeDef = TypedDict(
    "CapabilityConfigurationTypeDef",
    {
        "edi": NotRequired[EdiConfigurationTypeDef],
    },
)
ListTransformersResponseTypeDef = TypedDict(
    "ListTransformersResponseTypeDef",
    {
        "transformers": List[TransformerSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCapabilityRequestRequestTypeDef = TypedDict(
    "CreateCapabilityRequestRequestTypeDef",
    {
        "name": str,
        "type": Literal["edi"],
        "configuration": CapabilityConfigurationTypeDef,
        "instructionsDocuments": NotRequired[Sequence[S3LocationTypeDef]],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateCapabilityResponseTypeDef = TypedDict(
    "CreateCapabilityResponseTypeDef",
    {
        "capabilityId": str,
        "capabilityArn": str,
        "name": str,
        "type": Literal["edi"],
        "configuration": CapabilityConfigurationTypeDef,
        "instructionsDocuments": List[S3LocationTypeDef],
        "createdAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetCapabilityResponseTypeDef = TypedDict(
    "GetCapabilityResponseTypeDef",
    {
        "capabilityId": str,
        "capabilityArn": str,
        "name": str,
        "type": Literal["edi"],
        "configuration": CapabilityConfigurationTypeDef,
        "instructionsDocuments": List[S3LocationTypeDef],
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCapabilityRequestRequestTypeDef = TypedDict(
    "UpdateCapabilityRequestRequestTypeDef",
    {
        "capabilityId": str,
        "name": NotRequired[str],
        "configuration": NotRequired[CapabilityConfigurationTypeDef],
        "instructionsDocuments": NotRequired[Sequence[S3LocationTypeDef]],
    },
)
UpdateCapabilityResponseTypeDef = TypedDict(
    "UpdateCapabilityResponseTypeDef",
    {
        "capabilityId": str,
        "capabilityArn": str,
        "name": str,
        "type": Literal["edi"],
        "configuration": CapabilityConfigurationTypeDef,
        "instructionsDocuments": List[S3LocationTypeDef],
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

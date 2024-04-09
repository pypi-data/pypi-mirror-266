"""
Type annotations for controlcatalog service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/type_defs/)

Usage::

    ```python
    from mypy_boto3_controlcatalog.type_defs import AssociatedDomainSummaryTypeDef

    data: AssociatedDomainSummaryTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Sequence

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AssociatedDomainSummaryTypeDef",
    "AssociatedObjectiveSummaryTypeDef",
    "ObjectiveResourceFilterTypeDef",
    "DomainResourceFilterTypeDef",
    "DomainSummaryTypeDef",
    "PaginatorConfigTypeDef",
    "ResponseMetadataTypeDef",
    "ListDomainsRequestRequestTypeDef",
    "ObjectiveSummaryTypeDef",
    "CommonControlSummaryTypeDef",
    "CommonControlFilterTypeDef",
    "ObjectiveFilterTypeDef",
    "ListDomainsRequestListDomainsPaginateTypeDef",
    "ListDomainsResponseTypeDef",
    "ListObjectivesResponseTypeDef",
    "ListCommonControlsResponseTypeDef",
    "ListCommonControlsRequestListCommonControlsPaginateTypeDef",
    "ListCommonControlsRequestRequestTypeDef",
    "ListObjectivesRequestListObjectivesPaginateTypeDef",
    "ListObjectivesRequestRequestTypeDef",
)

AssociatedDomainSummaryTypeDef = TypedDict(
    "AssociatedDomainSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)
AssociatedObjectiveSummaryTypeDef = TypedDict(
    "AssociatedObjectiveSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)
ObjectiveResourceFilterTypeDef = TypedDict(
    "ObjectiveResourceFilterTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
DomainResourceFilterTypeDef = TypedDict(
    "DomainResourceFilterTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
DomainSummaryTypeDef = TypedDict(
    "DomainSummaryTypeDef",
    {
        "Arn": str,
        "CreateTime": datetime,
        "Description": str,
        "LastUpdateTime": datetime,
        "Name": str,
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
ListDomainsRequestRequestTypeDef = TypedDict(
    "ListDomainsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ObjectiveSummaryTypeDef = TypedDict(
    "ObjectiveSummaryTypeDef",
    {
        "Arn": str,
        "CreateTime": datetime,
        "Description": str,
        "Domain": AssociatedDomainSummaryTypeDef,
        "LastUpdateTime": datetime,
        "Name": str,
    },
)
CommonControlSummaryTypeDef = TypedDict(
    "CommonControlSummaryTypeDef",
    {
        "Arn": str,
        "CreateTime": datetime,
        "Description": str,
        "Domain": AssociatedDomainSummaryTypeDef,
        "LastUpdateTime": datetime,
        "Name": str,
        "Objective": AssociatedObjectiveSummaryTypeDef,
    },
)
CommonControlFilterTypeDef = TypedDict(
    "CommonControlFilterTypeDef",
    {
        "Objectives": NotRequired[Sequence[ObjectiveResourceFilterTypeDef]],
    },
)
ObjectiveFilterTypeDef = TypedDict(
    "ObjectiveFilterTypeDef",
    {
        "Domains": NotRequired[Sequence[DomainResourceFilterTypeDef]],
    },
)
ListDomainsRequestListDomainsPaginateTypeDef = TypedDict(
    "ListDomainsRequestListDomainsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDomainsResponseTypeDef = TypedDict(
    "ListDomainsResponseTypeDef",
    {
        "Domains": List[DomainSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListObjectivesResponseTypeDef = TypedDict(
    "ListObjectivesResponseTypeDef",
    {
        "NextToken": str,
        "Objectives": List[ObjectiveSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCommonControlsResponseTypeDef = TypedDict(
    "ListCommonControlsResponseTypeDef",
    {
        "CommonControls": List[CommonControlSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCommonControlsRequestListCommonControlsPaginateTypeDef = TypedDict(
    "ListCommonControlsRequestListCommonControlsPaginateTypeDef",
    {
        "CommonControlFilter": NotRequired[CommonControlFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCommonControlsRequestRequestTypeDef = TypedDict(
    "ListCommonControlsRequestRequestTypeDef",
    {
        "CommonControlFilter": NotRequired[CommonControlFilterTypeDef],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListObjectivesRequestListObjectivesPaginateTypeDef = TypedDict(
    "ListObjectivesRequestListObjectivesPaginateTypeDef",
    {
        "ObjectiveFilter": NotRequired[ObjectiveFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListObjectivesRequestRequestTypeDef = TypedDict(
    "ListObjectivesRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "ObjectiveFilter": NotRequired[ObjectiveFilterTypeDef],
    },
)

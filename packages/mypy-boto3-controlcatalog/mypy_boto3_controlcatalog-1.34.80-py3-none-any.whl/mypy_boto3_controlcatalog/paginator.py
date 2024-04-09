"""
Type annotations for controlcatalog service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_controlcatalog.client import ControlCatalogClient
    from mypy_boto3_controlcatalog.paginator import (
        ListCommonControlsPaginator,
        ListDomainsPaginator,
        ListObjectivesPaginator,
    )

    session = Session()
    client: ControlCatalogClient = session.client("controlcatalog")

    list_common_controls_paginator: ListCommonControlsPaginator = client.get_paginator("list_common_controls")
    list_domains_paginator: ListDomainsPaginator = client.get_paginator("list_domains")
    list_objectives_paginator: ListObjectivesPaginator = client.get_paginator("list_objectives")
    ```
"""

from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator, Paginator

from .type_defs import (
    CommonControlFilterTypeDef,
    ListCommonControlsResponseTypeDef,
    ListDomainsResponseTypeDef,
    ListObjectivesResponseTypeDef,
    ObjectiveFilterTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = ("ListCommonControlsPaginator", "ListDomainsPaginator", "ListObjectivesPaginator")

_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListCommonControlsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/controlcatalog.html#ControlCatalog.Paginator.ListCommonControls)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/paginators/#listcommoncontrolspaginator)
    """

    def paginate(
        self,
        *,
        CommonControlFilter: CommonControlFilterTypeDef = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListCommonControlsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/controlcatalog.html#ControlCatalog.Paginator.ListCommonControls.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/paginators/#listcommoncontrolspaginator)
        """


class ListDomainsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/controlcatalog.html#ControlCatalog.Paginator.ListDomains)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/paginators/#listdomainspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListDomainsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/controlcatalog.html#ControlCatalog.Paginator.ListDomains.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/paginators/#listdomainspaginator)
        """


class ListObjectivesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/controlcatalog.html#ControlCatalog.Paginator.ListObjectives)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/paginators/#listobjectivespaginator)
    """

    def paginate(
        self,
        *,
        ObjectiveFilter: ObjectiveFilterTypeDef = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListObjectivesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/controlcatalog.html#ControlCatalog.Paginator.ListObjectives.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_controlcatalog/paginators/#listobjectivespaginator)
        """

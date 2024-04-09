"""
Type annotations for networkmonitor service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmonitor/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_networkmonitor.client import CloudWatchNetworkMonitorClient
    from mypy_boto3_networkmonitor.paginator import (
        ListMonitorsPaginator,
    )

    session = Session()
    client: CloudWatchNetworkMonitorClient = session.client("networkmonitor")

    list_monitors_paginator: ListMonitorsPaginator = client.get_paginator("list_monitors")
    ```
"""

from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator, Paginator

from .type_defs import ListMonitorsOutputTypeDef, PaginatorConfigTypeDef

__all__ = ("ListMonitorsPaginator",)

_ItemTypeDef = TypeVar("_ItemTypeDef")

class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """

class ListMonitorsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmonitor.html#CloudWatchNetworkMonitor.Paginator.ListMonitors)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmonitor/paginators/#listmonitorspaginator)
    """

    def paginate(
        self, *, state: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListMonitorsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmonitor.html#CloudWatchNetworkMonitor.Paginator.ListMonitors.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmonitor/paginators/#listmonitorspaginator)
        """

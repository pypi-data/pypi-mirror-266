"""
Type annotations for networkmonitor service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_networkmonitor/type_defs/)

Usage::

    ```python
    from mypy_boto3_networkmonitor.type_defs import CreateMonitorProbeInputTypeDef

    data: CreateMonitorProbeInputTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import AddressFamilyType, MonitorStateType, ProbeStateType, ProtocolType

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "CreateMonitorProbeInputTypeDef",
    "ResponseMetadataTypeDef",
    "ProbeInputTypeDef",
    "DeleteMonitorInputRequestTypeDef",
    "DeleteProbeInputRequestTypeDef",
    "GetMonitorInputRequestTypeDef",
    "ProbeTypeDef",
    "GetProbeInputRequestTypeDef",
    "PaginatorConfigTypeDef",
    "ListMonitorsInputRequestTypeDef",
    "MonitorSummaryTypeDef",
    "ListTagsForResourceInputRequestTypeDef",
    "TagResourceInputRequestTypeDef",
    "UntagResourceInputRequestTypeDef",
    "UpdateMonitorInputRequestTypeDef",
    "UpdateProbeInputRequestTypeDef",
    "CreateMonitorInputRequestTypeDef",
    "CreateMonitorOutputTypeDef",
    "CreateProbeOutputTypeDef",
    "GetProbeOutputTypeDef",
    "ListTagsForResourceOutputTypeDef",
    "UpdateMonitorOutputTypeDef",
    "UpdateProbeOutputTypeDef",
    "CreateProbeInputRequestTypeDef",
    "GetMonitorOutputTypeDef",
    "ListMonitorsInputListMonitorsPaginateTypeDef",
    "ListMonitorsOutputTypeDef",
)

CreateMonitorProbeInputTypeDef = TypedDict(
    "CreateMonitorProbeInputTypeDef",
    {
        "sourceArn": str,
        "destination": str,
        "protocol": ProtocolType,
        "destinationPort": NotRequired[int],
        "packetSize": NotRequired[int],
        "probeTags": NotRequired[Mapping[str, str]],
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
ProbeInputTypeDef = TypedDict(
    "ProbeInputTypeDef",
    {
        "sourceArn": str,
        "destination": str,
        "protocol": ProtocolType,
        "destinationPort": NotRequired[int],
        "packetSize": NotRequired[int],
        "tags": NotRequired[Mapping[str, str]],
    },
)
DeleteMonitorInputRequestTypeDef = TypedDict(
    "DeleteMonitorInputRequestTypeDef",
    {
        "monitorName": str,
    },
)
DeleteProbeInputRequestTypeDef = TypedDict(
    "DeleteProbeInputRequestTypeDef",
    {
        "monitorName": str,
        "probeId": str,
    },
)
GetMonitorInputRequestTypeDef = TypedDict(
    "GetMonitorInputRequestTypeDef",
    {
        "monitorName": str,
    },
)
ProbeTypeDef = TypedDict(
    "ProbeTypeDef",
    {
        "sourceArn": str,
        "destination": str,
        "protocol": ProtocolType,
        "probeId": NotRequired[str],
        "probeArn": NotRequired[str],
        "destinationPort": NotRequired[int],
        "packetSize": NotRequired[int],
        "addressFamily": NotRequired[AddressFamilyType],
        "vpcId": NotRequired[str],
        "state": NotRequired[ProbeStateType],
        "createdAt": NotRequired[datetime],
        "modifiedAt": NotRequired[datetime],
        "tags": NotRequired[Dict[str, str]],
    },
)
GetProbeInputRequestTypeDef = TypedDict(
    "GetProbeInputRequestTypeDef",
    {
        "monitorName": str,
        "probeId": str,
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
ListMonitorsInputRequestTypeDef = TypedDict(
    "ListMonitorsInputRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "state": NotRequired[str],
    },
)
MonitorSummaryTypeDef = TypedDict(
    "MonitorSummaryTypeDef",
    {
        "monitorArn": str,
        "monitorName": str,
        "state": MonitorStateType,
        "aggregationPeriod": NotRequired[int],
        "tags": NotRequired[Dict[str, str]],
    },
)
ListTagsForResourceInputRequestTypeDef = TypedDict(
    "ListTagsForResourceInputRequestTypeDef",
    {
        "resourceArn": str,
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
UpdateMonitorInputRequestTypeDef = TypedDict(
    "UpdateMonitorInputRequestTypeDef",
    {
        "monitorName": str,
        "aggregationPeriod": int,
    },
)
UpdateProbeInputRequestTypeDef = TypedDict(
    "UpdateProbeInputRequestTypeDef",
    {
        "monitorName": str,
        "probeId": str,
        "state": NotRequired[ProbeStateType],
        "destination": NotRequired[str],
        "destinationPort": NotRequired[int],
        "protocol": NotRequired[ProtocolType],
        "packetSize": NotRequired[int],
    },
)
CreateMonitorInputRequestTypeDef = TypedDict(
    "CreateMonitorInputRequestTypeDef",
    {
        "monitorName": str,
        "probes": NotRequired[Sequence[CreateMonitorProbeInputTypeDef]],
        "aggregationPeriod": NotRequired[int],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
CreateMonitorOutputTypeDef = TypedDict(
    "CreateMonitorOutputTypeDef",
    {
        "monitorArn": str,
        "monitorName": str,
        "state": MonitorStateType,
        "aggregationPeriod": int,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProbeOutputTypeDef = TypedDict(
    "CreateProbeOutputTypeDef",
    {
        "probeId": str,
        "probeArn": str,
        "sourceArn": str,
        "destination": str,
        "destinationPort": int,
        "protocol": ProtocolType,
        "packetSize": int,
        "addressFamily": AddressFamilyType,
        "vpcId": str,
        "state": ProbeStateType,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetProbeOutputTypeDef = TypedDict(
    "GetProbeOutputTypeDef",
    {
        "probeId": str,
        "probeArn": str,
        "sourceArn": str,
        "destination": str,
        "destinationPort": int,
        "protocol": ProtocolType,
        "packetSize": int,
        "addressFamily": AddressFamilyType,
        "vpcId": str,
        "state": ProbeStateType,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "tags": Dict[str, str],
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
UpdateMonitorOutputTypeDef = TypedDict(
    "UpdateMonitorOutputTypeDef",
    {
        "monitorArn": str,
        "monitorName": str,
        "state": MonitorStateType,
        "aggregationPeriod": int,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateProbeOutputTypeDef = TypedDict(
    "UpdateProbeOutputTypeDef",
    {
        "probeId": str,
        "probeArn": str,
        "sourceArn": str,
        "destination": str,
        "destinationPort": int,
        "protocol": ProtocolType,
        "packetSize": int,
        "addressFamily": AddressFamilyType,
        "vpcId": str,
        "state": ProbeStateType,
        "createdAt": datetime,
        "modifiedAt": datetime,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProbeInputRequestTypeDef = TypedDict(
    "CreateProbeInputRequestTypeDef",
    {
        "monitorName": str,
        "probe": ProbeInputTypeDef,
        "clientToken": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
GetMonitorOutputTypeDef = TypedDict(
    "GetMonitorOutputTypeDef",
    {
        "monitorArn": str,
        "monitorName": str,
        "state": MonitorStateType,
        "aggregationPeriod": int,
        "tags": Dict[str, str],
        "probes": List[ProbeTypeDef],
        "createdAt": datetime,
        "modifiedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListMonitorsInputListMonitorsPaginateTypeDef = TypedDict(
    "ListMonitorsInputListMonitorsPaginateTypeDef",
    {
        "state": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMonitorsOutputTypeDef = TypedDict(
    "ListMonitorsOutputTypeDef",
    {
        "monitors": List[MonitorSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

"""
Type annotations for ivs service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivs/type_defs/)

Usage::

    ```python
    from mypy_boto3_ivs.type_defs import AudioConfigurationTypeDef

    data: AudioConfigurationTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    ChannelLatencyModeType,
    ChannelTypeType,
    RecordingConfigurationStateType,
    RecordingModeType,
    RenditionConfigurationRenditionSelectionType,
    RenditionConfigurationRenditionType,
    StreamHealthType,
    StreamStateType,
    ThumbnailConfigurationResolutionType,
    ThumbnailConfigurationStorageType,
    TranscodePresetType,
)

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AudioConfigurationTypeDef",
    "BatchErrorTypeDef",
    "BatchGetChannelRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "BatchGetStreamKeyRequestRequestTypeDef",
    "StreamKeyTypeDef",
    "BatchStartViewerSessionRevocationErrorTypeDef",
    "BatchStartViewerSessionRevocationViewerSessionTypeDef",
    "ChannelSummaryTypeDef",
    "SrtTypeDef",
    "CreateChannelRequestRequestTypeDef",
    "CreatePlaybackRestrictionPolicyRequestRequestTypeDef",
    "PlaybackRestrictionPolicyTypeDef",
    "RenditionConfigurationTypeDef",
    "ThumbnailConfigurationTypeDef",
    "CreateStreamKeyRequestRequestTypeDef",
    "DeleteChannelRequestRequestTypeDef",
    "DeletePlaybackKeyPairRequestRequestTypeDef",
    "DeletePlaybackRestrictionPolicyRequestRequestTypeDef",
    "DeleteRecordingConfigurationRequestRequestTypeDef",
    "DeleteStreamKeyRequestRequestTypeDef",
    "S3DestinationConfigurationTypeDef",
    "GetChannelRequestRequestTypeDef",
    "GetPlaybackKeyPairRequestRequestTypeDef",
    "PlaybackKeyPairTypeDef",
    "GetPlaybackRestrictionPolicyRequestRequestTypeDef",
    "GetRecordingConfigurationRequestRequestTypeDef",
    "GetStreamKeyRequestRequestTypeDef",
    "GetStreamRequestRequestTypeDef",
    "StreamTypeDef",
    "GetStreamSessionRequestRequestTypeDef",
    "ImportPlaybackKeyPairRequestRequestTypeDef",
    "VideoConfigurationTypeDef",
    "PaginatorConfigTypeDef",
    "ListChannelsRequestRequestTypeDef",
    "ListPlaybackKeyPairsRequestRequestTypeDef",
    "PlaybackKeyPairSummaryTypeDef",
    "ListPlaybackRestrictionPoliciesRequestRequestTypeDef",
    "PlaybackRestrictionPolicySummaryTypeDef",
    "ListRecordingConfigurationsRequestRequestTypeDef",
    "ListStreamKeysRequestRequestTypeDef",
    "StreamKeySummaryTypeDef",
    "ListStreamSessionsRequestRequestTypeDef",
    "StreamSessionSummaryTypeDef",
    "StreamFiltersTypeDef",
    "StreamSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "PutMetadataRequestRequestTypeDef",
    "StartViewerSessionRevocationRequestRequestTypeDef",
    "StopStreamRequestRequestTypeDef",
    "StreamEventTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateChannelRequestRequestTypeDef",
    "UpdatePlaybackRestrictionPolicyRequestRequestTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "BatchGetStreamKeyResponseTypeDef",
    "CreateStreamKeyResponseTypeDef",
    "GetStreamKeyResponseTypeDef",
    "BatchStartViewerSessionRevocationResponseTypeDef",
    "BatchStartViewerSessionRevocationRequestRequestTypeDef",
    "ListChannelsResponseTypeDef",
    "ChannelTypeDef",
    "CreatePlaybackRestrictionPolicyResponseTypeDef",
    "GetPlaybackRestrictionPolicyResponseTypeDef",
    "UpdatePlaybackRestrictionPolicyResponseTypeDef",
    "DestinationConfigurationTypeDef",
    "GetPlaybackKeyPairResponseTypeDef",
    "ImportPlaybackKeyPairResponseTypeDef",
    "GetStreamResponseTypeDef",
    "IngestConfigurationTypeDef",
    "ListChannelsRequestListChannelsPaginateTypeDef",
    "ListPlaybackKeyPairsRequestListPlaybackKeyPairsPaginateTypeDef",
    "ListRecordingConfigurationsRequestListRecordingConfigurationsPaginateTypeDef",
    "ListStreamKeysRequestListStreamKeysPaginateTypeDef",
    "ListPlaybackKeyPairsResponseTypeDef",
    "ListPlaybackRestrictionPoliciesResponseTypeDef",
    "ListStreamKeysResponseTypeDef",
    "ListStreamSessionsResponseTypeDef",
    "ListStreamsRequestListStreamsPaginateTypeDef",
    "ListStreamsRequestRequestTypeDef",
    "ListStreamsResponseTypeDef",
    "BatchGetChannelResponseTypeDef",
    "CreateChannelResponseTypeDef",
    "GetChannelResponseTypeDef",
    "UpdateChannelResponseTypeDef",
    "CreateRecordingConfigurationRequestRequestTypeDef",
    "RecordingConfigurationSummaryTypeDef",
    "RecordingConfigurationTypeDef",
    "ListRecordingConfigurationsResponseTypeDef",
    "CreateRecordingConfigurationResponseTypeDef",
    "GetRecordingConfigurationResponseTypeDef",
    "StreamSessionTypeDef",
    "GetStreamSessionResponseTypeDef",
)

AudioConfigurationTypeDef = TypedDict(
    "AudioConfigurationTypeDef",
    {
        "channels": NotRequired[int],
        "codec": NotRequired[str],
        "sampleRate": NotRequired[int],
        "targetBitrate": NotRequired[int],
    },
)
BatchErrorTypeDef = TypedDict(
    "BatchErrorTypeDef",
    {
        "arn": NotRequired[str],
        "code": NotRequired[str],
        "message": NotRequired[str],
    },
)
BatchGetChannelRequestRequestTypeDef = TypedDict(
    "BatchGetChannelRequestRequestTypeDef",
    {
        "arns": Sequence[str],
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
BatchGetStreamKeyRequestRequestTypeDef = TypedDict(
    "BatchGetStreamKeyRequestRequestTypeDef",
    {
        "arns": Sequence[str],
    },
)
StreamKeyTypeDef = TypedDict(
    "StreamKeyTypeDef",
    {
        "arn": NotRequired[str],
        "channelArn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "value": NotRequired[str],
    },
)
BatchStartViewerSessionRevocationErrorTypeDef = TypedDict(
    "BatchStartViewerSessionRevocationErrorTypeDef",
    {
        "channelArn": str,
        "viewerId": str,
        "code": NotRequired[str],
        "message": NotRequired[str],
    },
)
BatchStartViewerSessionRevocationViewerSessionTypeDef = TypedDict(
    "BatchStartViewerSessionRevocationViewerSessionTypeDef",
    {
        "channelArn": str,
        "viewerId": str,
        "viewerSessionVersionsLessThanOrEqualTo": NotRequired[int],
    },
)
ChannelSummaryTypeDef = TypedDict(
    "ChannelSummaryTypeDef",
    {
        "arn": NotRequired[str],
        "authorized": NotRequired[bool],
        "insecureIngest": NotRequired[bool],
        "latencyMode": NotRequired[ChannelLatencyModeType],
        "name": NotRequired[str],
        "playbackRestrictionPolicyArn": NotRequired[str],
        "preset": NotRequired[TranscodePresetType],
        "recordingConfigurationArn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "type": NotRequired[ChannelTypeType],
    },
)
SrtTypeDef = TypedDict(
    "SrtTypeDef",
    {
        "endpoint": NotRequired[str],
        "passphrase": NotRequired[str],
    },
)
CreateChannelRequestRequestTypeDef = TypedDict(
    "CreateChannelRequestRequestTypeDef",
    {
        "authorized": NotRequired[bool],
        "insecureIngest": NotRequired[bool],
        "latencyMode": NotRequired[ChannelLatencyModeType],
        "name": NotRequired[str],
        "playbackRestrictionPolicyArn": NotRequired[str],
        "preset": NotRequired[TranscodePresetType],
        "recordingConfigurationArn": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "type": NotRequired[ChannelTypeType],
    },
)
CreatePlaybackRestrictionPolicyRequestRequestTypeDef = TypedDict(
    "CreatePlaybackRestrictionPolicyRequestRequestTypeDef",
    {
        "allowedCountries": NotRequired[Sequence[str]],
        "allowedOrigins": NotRequired[Sequence[str]],
        "enableStrictOriginEnforcement": NotRequired[bool],
        "name": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
PlaybackRestrictionPolicyTypeDef = TypedDict(
    "PlaybackRestrictionPolicyTypeDef",
    {
        "allowedCountries": List[str],
        "allowedOrigins": List[str],
        "arn": str,
        "enableStrictOriginEnforcement": NotRequired[bool],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
RenditionConfigurationTypeDef = TypedDict(
    "RenditionConfigurationTypeDef",
    {
        "renditionSelection": NotRequired[RenditionConfigurationRenditionSelectionType],
        "renditions": NotRequired[Sequence[RenditionConfigurationRenditionType]],
    },
)
ThumbnailConfigurationTypeDef = TypedDict(
    "ThumbnailConfigurationTypeDef",
    {
        "recordingMode": NotRequired[RecordingModeType],
        "resolution": NotRequired[ThumbnailConfigurationResolutionType],
        "storage": NotRequired[Sequence[ThumbnailConfigurationStorageType]],
        "targetIntervalSeconds": NotRequired[int],
    },
)
CreateStreamKeyRequestRequestTypeDef = TypedDict(
    "CreateStreamKeyRequestRequestTypeDef",
    {
        "channelArn": str,
        "tags": NotRequired[Mapping[str, str]],
    },
)
DeleteChannelRequestRequestTypeDef = TypedDict(
    "DeleteChannelRequestRequestTypeDef",
    {
        "arn": str,
    },
)
DeletePlaybackKeyPairRequestRequestTypeDef = TypedDict(
    "DeletePlaybackKeyPairRequestRequestTypeDef",
    {
        "arn": str,
    },
)
DeletePlaybackRestrictionPolicyRequestRequestTypeDef = TypedDict(
    "DeletePlaybackRestrictionPolicyRequestRequestTypeDef",
    {
        "arn": str,
    },
)
DeleteRecordingConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteRecordingConfigurationRequestRequestTypeDef",
    {
        "arn": str,
    },
)
DeleteStreamKeyRequestRequestTypeDef = TypedDict(
    "DeleteStreamKeyRequestRequestTypeDef",
    {
        "arn": str,
    },
)
S3DestinationConfigurationTypeDef = TypedDict(
    "S3DestinationConfigurationTypeDef",
    {
        "bucketName": str,
    },
)
GetChannelRequestRequestTypeDef = TypedDict(
    "GetChannelRequestRequestTypeDef",
    {
        "arn": str,
    },
)
GetPlaybackKeyPairRequestRequestTypeDef = TypedDict(
    "GetPlaybackKeyPairRequestRequestTypeDef",
    {
        "arn": str,
    },
)
PlaybackKeyPairTypeDef = TypedDict(
    "PlaybackKeyPairTypeDef",
    {
        "arn": NotRequired[str],
        "fingerprint": NotRequired[str],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
GetPlaybackRestrictionPolicyRequestRequestTypeDef = TypedDict(
    "GetPlaybackRestrictionPolicyRequestRequestTypeDef",
    {
        "arn": str,
    },
)
GetRecordingConfigurationRequestRequestTypeDef = TypedDict(
    "GetRecordingConfigurationRequestRequestTypeDef",
    {
        "arn": str,
    },
)
GetStreamKeyRequestRequestTypeDef = TypedDict(
    "GetStreamKeyRequestRequestTypeDef",
    {
        "arn": str,
    },
)
GetStreamRequestRequestTypeDef = TypedDict(
    "GetStreamRequestRequestTypeDef",
    {
        "channelArn": str,
    },
)
StreamTypeDef = TypedDict(
    "StreamTypeDef",
    {
        "channelArn": NotRequired[str],
        "health": NotRequired[StreamHealthType],
        "playbackUrl": NotRequired[str],
        "startTime": NotRequired[datetime],
        "state": NotRequired[StreamStateType],
        "streamId": NotRequired[str],
        "viewerCount": NotRequired[int],
    },
)
GetStreamSessionRequestRequestTypeDef = TypedDict(
    "GetStreamSessionRequestRequestTypeDef",
    {
        "channelArn": str,
        "streamId": NotRequired[str],
    },
)
ImportPlaybackKeyPairRequestRequestTypeDef = TypedDict(
    "ImportPlaybackKeyPairRequestRequestTypeDef",
    {
        "publicKeyMaterial": str,
        "name": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
VideoConfigurationTypeDef = TypedDict(
    "VideoConfigurationTypeDef",
    {
        "avcLevel": NotRequired[str],
        "avcProfile": NotRequired[str],
        "codec": NotRequired[str],
        "encoder": NotRequired[str],
        "targetBitrate": NotRequired[int],
        "targetFramerate": NotRequired[int],
        "videoHeight": NotRequired[int],
        "videoWidth": NotRequired[int],
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
ListChannelsRequestRequestTypeDef = TypedDict(
    "ListChannelsRequestRequestTypeDef",
    {
        "filterByName": NotRequired[str],
        "filterByPlaybackRestrictionPolicyArn": NotRequired[str],
        "filterByRecordingConfigurationArn": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListPlaybackKeyPairsRequestRequestTypeDef = TypedDict(
    "ListPlaybackKeyPairsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
PlaybackKeyPairSummaryTypeDef = TypedDict(
    "PlaybackKeyPairSummaryTypeDef",
    {
        "arn": NotRequired[str],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
ListPlaybackRestrictionPoliciesRequestRequestTypeDef = TypedDict(
    "ListPlaybackRestrictionPoliciesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
PlaybackRestrictionPolicySummaryTypeDef = TypedDict(
    "PlaybackRestrictionPolicySummaryTypeDef",
    {
        "allowedCountries": List[str],
        "allowedOrigins": List[str],
        "arn": str,
        "enableStrictOriginEnforcement": NotRequired[bool],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
ListRecordingConfigurationsRequestRequestTypeDef = TypedDict(
    "ListRecordingConfigurationsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListStreamKeysRequestRequestTypeDef = TypedDict(
    "ListStreamKeysRequestRequestTypeDef",
    {
        "channelArn": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
StreamKeySummaryTypeDef = TypedDict(
    "StreamKeySummaryTypeDef",
    {
        "arn": NotRequired[str],
        "channelArn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
ListStreamSessionsRequestRequestTypeDef = TypedDict(
    "ListStreamSessionsRequestRequestTypeDef",
    {
        "channelArn": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
StreamSessionSummaryTypeDef = TypedDict(
    "StreamSessionSummaryTypeDef",
    {
        "endTime": NotRequired[datetime],
        "hasErrorEvent": NotRequired[bool],
        "startTime": NotRequired[datetime],
        "streamId": NotRequired[str],
    },
)
StreamFiltersTypeDef = TypedDict(
    "StreamFiltersTypeDef",
    {
        "health": NotRequired[StreamHealthType],
    },
)
StreamSummaryTypeDef = TypedDict(
    "StreamSummaryTypeDef",
    {
        "channelArn": NotRequired[str],
        "health": NotRequired[StreamHealthType],
        "startTime": NotRequired[datetime],
        "state": NotRequired[StreamStateType],
        "streamId": NotRequired[str],
        "viewerCount": NotRequired[int],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
PutMetadataRequestRequestTypeDef = TypedDict(
    "PutMetadataRequestRequestTypeDef",
    {
        "channelArn": str,
        "metadata": str,
    },
)
StartViewerSessionRevocationRequestRequestTypeDef = TypedDict(
    "StartViewerSessionRevocationRequestRequestTypeDef",
    {
        "channelArn": str,
        "viewerId": str,
        "viewerSessionVersionsLessThanOrEqualTo": NotRequired[int],
    },
)
StopStreamRequestRequestTypeDef = TypedDict(
    "StopStreamRequestRequestTypeDef",
    {
        "channelArn": str,
    },
)
StreamEventTypeDef = TypedDict(
    "StreamEventTypeDef",
    {
        "eventTime": NotRequired[datetime],
        "name": NotRequired[str],
        "type": NotRequired[str],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateChannelRequestRequestTypeDef = TypedDict(
    "UpdateChannelRequestRequestTypeDef",
    {
        "arn": str,
        "authorized": NotRequired[bool],
        "insecureIngest": NotRequired[bool],
        "latencyMode": NotRequired[ChannelLatencyModeType],
        "name": NotRequired[str],
        "playbackRestrictionPolicyArn": NotRequired[str],
        "preset": NotRequired[TranscodePresetType],
        "recordingConfigurationArn": NotRequired[str],
        "type": NotRequired[ChannelTypeType],
    },
)
UpdatePlaybackRestrictionPolicyRequestRequestTypeDef = TypedDict(
    "UpdatePlaybackRestrictionPolicyRequestRequestTypeDef",
    {
        "arn": str,
        "allowedCountries": NotRequired[Sequence[str]],
        "allowedOrigins": NotRequired[Sequence[str]],
        "enableStrictOriginEnforcement": NotRequired[bool],
        "name": NotRequired[str],
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
BatchGetStreamKeyResponseTypeDef = TypedDict(
    "BatchGetStreamKeyResponseTypeDef",
    {
        "errors": List[BatchErrorTypeDef],
        "streamKeys": List[StreamKeyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateStreamKeyResponseTypeDef = TypedDict(
    "CreateStreamKeyResponseTypeDef",
    {
        "streamKey": StreamKeyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetStreamKeyResponseTypeDef = TypedDict(
    "GetStreamKeyResponseTypeDef",
    {
        "streamKey": StreamKeyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchStartViewerSessionRevocationResponseTypeDef = TypedDict(
    "BatchStartViewerSessionRevocationResponseTypeDef",
    {
        "errors": List[BatchStartViewerSessionRevocationErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchStartViewerSessionRevocationRequestRequestTypeDef = TypedDict(
    "BatchStartViewerSessionRevocationRequestRequestTypeDef",
    {
        "viewerSessions": Sequence[BatchStartViewerSessionRevocationViewerSessionTypeDef],
    },
)
ListChannelsResponseTypeDef = TypedDict(
    "ListChannelsResponseTypeDef",
    {
        "channels": List[ChannelSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ChannelTypeDef = TypedDict(
    "ChannelTypeDef",
    {
        "arn": NotRequired[str],
        "authorized": NotRequired[bool],
        "ingestEndpoint": NotRequired[str],
        "insecureIngest": NotRequired[bool],
        "latencyMode": NotRequired[ChannelLatencyModeType],
        "name": NotRequired[str],
        "playbackRestrictionPolicyArn": NotRequired[str],
        "playbackUrl": NotRequired[str],
        "preset": NotRequired[TranscodePresetType],
        "recordingConfigurationArn": NotRequired[str],
        "srt": NotRequired[SrtTypeDef],
        "tags": NotRequired[Dict[str, str]],
        "type": NotRequired[ChannelTypeType],
    },
)
CreatePlaybackRestrictionPolicyResponseTypeDef = TypedDict(
    "CreatePlaybackRestrictionPolicyResponseTypeDef",
    {
        "playbackRestrictionPolicy": PlaybackRestrictionPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPlaybackRestrictionPolicyResponseTypeDef = TypedDict(
    "GetPlaybackRestrictionPolicyResponseTypeDef",
    {
        "playbackRestrictionPolicy": PlaybackRestrictionPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePlaybackRestrictionPolicyResponseTypeDef = TypedDict(
    "UpdatePlaybackRestrictionPolicyResponseTypeDef",
    {
        "playbackRestrictionPolicy": PlaybackRestrictionPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DestinationConfigurationTypeDef = TypedDict(
    "DestinationConfigurationTypeDef",
    {
        "s3": NotRequired[S3DestinationConfigurationTypeDef],
    },
)
GetPlaybackKeyPairResponseTypeDef = TypedDict(
    "GetPlaybackKeyPairResponseTypeDef",
    {
        "keyPair": PlaybackKeyPairTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportPlaybackKeyPairResponseTypeDef = TypedDict(
    "ImportPlaybackKeyPairResponseTypeDef",
    {
        "keyPair": PlaybackKeyPairTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetStreamResponseTypeDef = TypedDict(
    "GetStreamResponseTypeDef",
    {
        "stream": StreamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IngestConfigurationTypeDef = TypedDict(
    "IngestConfigurationTypeDef",
    {
        "audio": NotRequired[AudioConfigurationTypeDef],
        "video": NotRequired[VideoConfigurationTypeDef],
    },
)
ListChannelsRequestListChannelsPaginateTypeDef = TypedDict(
    "ListChannelsRequestListChannelsPaginateTypeDef",
    {
        "filterByName": NotRequired[str],
        "filterByPlaybackRestrictionPolicyArn": NotRequired[str],
        "filterByRecordingConfigurationArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPlaybackKeyPairsRequestListPlaybackKeyPairsPaginateTypeDef = TypedDict(
    "ListPlaybackKeyPairsRequestListPlaybackKeyPairsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRecordingConfigurationsRequestListRecordingConfigurationsPaginateTypeDef = TypedDict(
    "ListRecordingConfigurationsRequestListRecordingConfigurationsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListStreamKeysRequestListStreamKeysPaginateTypeDef = TypedDict(
    "ListStreamKeysRequestListStreamKeysPaginateTypeDef",
    {
        "channelArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPlaybackKeyPairsResponseTypeDef = TypedDict(
    "ListPlaybackKeyPairsResponseTypeDef",
    {
        "keyPairs": List[PlaybackKeyPairSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPlaybackRestrictionPoliciesResponseTypeDef = TypedDict(
    "ListPlaybackRestrictionPoliciesResponseTypeDef",
    {
        "nextToken": str,
        "playbackRestrictionPolicies": List[PlaybackRestrictionPolicySummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListStreamKeysResponseTypeDef = TypedDict(
    "ListStreamKeysResponseTypeDef",
    {
        "nextToken": str,
        "streamKeys": List[StreamKeySummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListStreamSessionsResponseTypeDef = TypedDict(
    "ListStreamSessionsResponseTypeDef",
    {
        "nextToken": str,
        "streamSessions": List[StreamSessionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListStreamsRequestListStreamsPaginateTypeDef = TypedDict(
    "ListStreamsRequestListStreamsPaginateTypeDef",
    {
        "filterBy": NotRequired[StreamFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListStreamsRequestRequestTypeDef = TypedDict(
    "ListStreamsRequestRequestTypeDef",
    {
        "filterBy": NotRequired[StreamFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListStreamsResponseTypeDef = TypedDict(
    "ListStreamsResponseTypeDef",
    {
        "nextToken": str,
        "streams": List[StreamSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetChannelResponseTypeDef = TypedDict(
    "BatchGetChannelResponseTypeDef",
    {
        "channels": List[ChannelTypeDef],
        "errors": List[BatchErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateChannelResponseTypeDef = TypedDict(
    "CreateChannelResponseTypeDef",
    {
        "channel": ChannelTypeDef,
        "streamKey": StreamKeyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetChannelResponseTypeDef = TypedDict(
    "GetChannelResponseTypeDef",
    {
        "channel": ChannelTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateChannelResponseTypeDef = TypedDict(
    "UpdateChannelResponseTypeDef",
    {
        "channel": ChannelTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRecordingConfigurationRequestRequestTypeDef = TypedDict(
    "CreateRecordingConfigurationRequestRequestTypeDef",
    {
        "destinationConfiguration": DestinationConfigurationTypeDef,
        "name": NotRequired[str],
        "recordingReconnectWindowSeconds": NotRequired[int],
        "renditionConfiguration": NotRequired[RenditionConfigurationTypeDef],
        "tags": NotRequired[Mapping[str, str]],
        "thumbnailConfiguration": NotRequired[ThumbnailConfigurationTypeDef],
    },
)
RecordingConfigurationSummaryTypeDef = TypedDict(
    "RecordingConfigurationSummaryTypeDef",
    {
        "arn": str,
        "destinationConfiguration": DestinationConfigurationTypeDef,
        "state": RecordingConfigurationStateType,
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
RecordingConfigurationTypeDef = TypedDict(
    "RecordingConfigurationTypeDef",
    {
        "arn": str,
        "destinationConfiguration": DestinationConfigurationTypeDef,
        "state": RecordingConfigurationStateType,
        "name": NotRequired[str],
        "recordingReconnectWindowSeconds": NotRequired[int],
        "renditionConfiguration": NotRequired[RenditionConfigurationTypeDef],
        "tags": NotRequired[Dict[str, str]],
        "thumbnailConfiguration": NotRequired[ThumbnailConfigurationTypeDef],
    },
)
ListRecordingConfigurationsResponseTypeDef = TypedDict(
    "ListRecordingConfigurationsResponseTypeDef",
    {
        "nextToken": str,
        "recordingConfigurations": List[RecordingConfigurationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRecordingConfigurationResponseTypeDef = TypedDict(
    "CreateRecordingConfigurationResponseTypeDef",
    {
        "recordingConfiguration": RecordingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetRecordingConfigurationResponseTypeDef = TypedDict(
    "GetRecordingConfigurationResponseTypeDef",
    {
        "recordingConfiguration": RecordingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StreamSessionTypeDef = TypedDict(
    "StreamSessionTypeDef",
    {
        "channel": NotRequired[ChannelTypeDef],
        "endTime": NotRequired[datetime],
        "ingestConfiguration": NotRequired[IngestConfigurationTypeDef],
        "recordingConfiguration": NotRequired[RecordingConfigurationTypeDef],
        "startTime": NotRequired[datetime],
        "streamId": NotRequired[str],
        "truncatedEvents": NotRequired[List[StreamEventTypeDef]],
    },
)
GetStreamSessionResponseTypeDef = TypedDict(
    "GetStreamSessionResponseTypeDef",
    {
        "streamSession": StreamSessionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

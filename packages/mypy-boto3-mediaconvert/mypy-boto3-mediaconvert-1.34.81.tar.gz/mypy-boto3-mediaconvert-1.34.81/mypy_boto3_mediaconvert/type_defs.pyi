"""
Type annotations for mediaconvert service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/type_defs/)

Usage::

    ```python
    from mypy_boto3_mediaconvert.type_defs import AacSettingsTypeDef

    data: AacSettingsTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    AacAudioDescriptionBroadcasterMixType,
    AacCodecProfileType,
    AacCodingModeType,
    AacRateControlModeType,
    AacRawFormatType,
    AacSpecificationType,
    AacVbrQualityType,
    Ac3BitstreamModeType,
    Ac3CodingModeType,
    Ac3DynamicRangeCompressionLineType,
    Ac3DynamicRangeCompressionProfileType,
    Ac3DynamicRangeCompressionRfType,
    Ac3LfeFilterType,
    Ac3MetadataControlType,
    AccelerationModeType,
    AccelerationStatusType,
    AdvancedInputFilterAddTextureType,
    AdvancedInputFilterSharpenType,
    AdvancedInputFilterType,
    AfdSignalingType,
    AlphaBehaviorType,
    AncillaryConvert608To708Type,
    AncillaryTerminateCaptionsType,
    AntiAliasType,
    AudioChannelTagType,
    AudioCodecType,
    AudioDefaultSelectionType,
    AudioDurationCorrectionType,
    AudioLanguageCodeControlType,
    AudioNormalizationAlgorithmControlType,
    AudioNormalizationAlgorithmType,
    AudioNormalizationLoudnessLoggingType,
    AudioNormalizationPeakCalculationType,
    AudioSelectorTypeType,
    AudioTypeControlType,
    Av1AdaptiveQuantizationType,
    Av1BitDepthType,
    Av1FilmGrainSynthesisType,
    Av1FramerateControlType,
    Av1FramerateConversionAlgorithmType,
    Av1SpatialAdaptiveQuantizationType,
    AvcIntraClassType,
    AvcIntraFramerateControlType,
    AvcIntraFramerateConversionAlgorithmType,
    AvcIntraInterlaceModeType,
    AvcIntraScanTypeConversionModeType,
    AvcIntraSlowPalType,
    AvcIntraTelecineType,
    AvcIntraUhdQualityTuningLevelType,
    BandwidthReductionFilterSharpeningType,
    BandwidthReductionFilterStrengthType,
    BillingTagsSourceType,
    BurninSubtitleAlignmentType,
    BurninSubtitleApplyFontColorType,
    BurninSubtitleBackgroundColorType,
    BurninSubtitleFallbackFontType,
    BurninSubtitleFontColorType,
    BurninSubtitleOutlineColorType,
    BurninSubtitleShadowColorType,
    BurnInSubtitleStylePassthroughType,
    BurninSubtitleTeletextSpacingType,
    CaptionDestinationTypeType,
    CaptionSourceConvertPaintOnToPopOnType,
    CaptionSourceTypeType,
    CmafClientCacheType,
    CmafCodecSpecificationType,
    CmafEncryptionTypeType,
    CmafImageBasedTrickPlayType,
    CmafInitializationVectorInManifestType,
    CmafIntervalCadenceType,
    CmafKeyProviderTypeType,
    CmafManifestCompressionType,
    CmafManifestDurationFormatType,
    CmafMpdManifestBandwidthTypeType,
    CmafMpdProfileType,
    CmafPtsOffsetHandlingForBFramesType,
    CmafSegmentControlType,
    CmafSegmentLengthControlType,
    CmafStreamInfResolutionType,
    CmafTargetDurationCompatibilityModeType,
    CmafVideoCompositionOffsetsType,
    CmafWriteDASHManifestType,
    CmafWriteHLSManifestType,
    CmafWriteSegmentTimelineInRepresentationType,
    CmfcAudioDurationType,
    CmfcAudioTrackTypeType,
    CmfcDescriptiveVideoServiceFlagType,
    CmfcIFrameOnlyManifestType,
    CmfcKlvMetadataType,
    CmfcManifestMetadataSignalingType,
    CmfcScte35EsamType,
    CmfcScte35SourceType,
    CmfcTimedMetadataBoxVersionType,
    CmfcTimedMetadataType,
    ColorMetadataType,
    ColorSpaceConversionType,
    ColorSpaceType,
    ColorSpaceUsageType,
    ContainerTypeType,
    CopyProtectionActionType,
    DashIsoGroupAudioChannelConfigSchemeIdUriType,
    DashIsoHbbtvComplianceType,
    DashIsoImageBasedTrickPlayType,
    DashIsoIntervalCadenceType,
    DashIsoMpdManifestBandwidthTypeType,
    DashIsoMpdProfileType,
    DashIsoPlaybackDeviceCompatibilityType,
    DashIsoPtsOffsetHandlingForBFramesType,
    DashIsoSegmentControlType,
    DashIsoSegmentLengthControlType,
    DashIsoVideoCompositionOffsetsType,
    DashIsoWriteSegmentTimelineInRepresentationType,
    DashManifestStyleType,
    DecryptionModeType,
    DeinterlaceAlgorithmType,
    DeinterlacerControlType,
    DeinterlacerModeType,
    DescribeEndpointsModeType,
    DolbyVisionLevel6ModeType,
    DolbyVisionMappingType,
    DolbyVisionProfileType,
    DropFrameTimecodeType,
    DvbddsHandlingType,
    DvbSubSubtitleFallbackFontType,
    DvbSubtitleAlignmentType,
    DvbSubtitleApplyFontColorType,
    DvbSubtitleBackgroundColorType,
    DvbSubtitleFontColorType,
    DvbSubtitleOutlineColorType,
    DvbSubtitleShadowColorType,
    DvbSubtitleStylePassthroughType,
    DvbSubtitleTeletextSpacingType,
    DvbSubtitlingTypeType,
    Eac3AtmosCodingModeType,
    Eac3AtmosDialogueIntelligenceType,
    Eac3AtmosDownmixControlType,
    Eac3AtmosDynamicRangeCompressionLineType,
    Eac3AtmosDynamicRangeCompressionRfType,
    Eac3AtmosDynamicRangeControlType,
    Eac3AtmosMeteringModeType,
    Eac3AtmosStereoDownmixType,
    Eac3AtmosSurroundExModeType,
    Eac3AttenuationControlType,
    Eac3BitstreamModeType,
    Eac3CodingModeType,
    Eac3DcFilterType,
    Eac3DynamicRangeCompressionLineType,
    Eac3DynamicRangeCompressionRfType,
    Eac3LfeControlType,
    Eac3LfeFilterType,
    Eac3MetadataControlType,
    Eac3PassthroughControlType,
    Eac3PhaseControlType,
    Eac3StereoDownmixType,
    Eac3SurroundExModeType,
    Eac3SurroundModeType,
    EmbeddedConvert608To708Type,
    EmbeddedTerminateCaptionsType,
    EmbeddedTimecodeOverrideType,
    F4vMoovPlacementType,
    FileSourceConvert608To708Type,
    FileSourceTimeDeltaUnitsType,
    FontScriptType,
    H264AdaptiveQuantizationType,
    H264CodecLevelType,
    H264CodecProfileType,
    H264DynamicSubGopType,
    H264EndOfStreamMarkersType,
    H264EntropyEncodingType,
    H264FieldEncodingType,
    H264FlickerAdaptiveQuantizationType,
    H264FramerateControlType,
    H264FramerateConversionAlgorithmType,
    H264GopBReferenceType,
    H264GopSizeUnitsType,
    H264InterlaceModeType,
    H264ParControlType,
    H264QualityTuningLevelType,
    H264RateControlModeType,
    H264RepeatPpsType,
    H264ScanTypeConversionModeType,
    H264SceneChangeDetectType,
    H264SlowPalType,
    H264SpatialAdaptiveQuantizationType,
    H264SyntaxType,
    H264TelecineType,
    H264TemporalAdaptiveQuantizationType,
    H264UnregisteredSeiTimecodeType,
    H265AdaptiveQuantizationType,
    H265AlternateTransferFunctionSeiType,
    H265CodecLevelType,
    H265CodecProfileType,
    H265DynamicSubGopType,
    H265EndOfStreamMarkersType,
    H265FlickerAdaptiveQuantizationType,
    H265FramerateControlType,
    H265FramerateConversionAlgorithmType,
    H265GopBReferenceType,
    H265GopSizeUnitsType,
    H265InterlaceModeType,
    H265ParControlType,
    H265QualityTuningLevelType,
    H265RateControlModeType,
    H265SampleAdaptiveOffsetFilterModeType,
    H265ScanTypeConversionModeType,
    H265SceneChangeDetectType,
    H265SlowPalType,
    H265SpatialAdaptiveQuantizationType,
    H265TelecineType,
    H265TemporalAdaptiveQuantizationType,
    H265TemporalIdsType,
    H265TilesType,
    H265UnregisteredSeiTimecodeType,
    H265WriteMp4PackagingTypeType,
    HDRToSDRToneMapperType,
    HlsAdMarkersType,
    HlsAudioOnlyContainerType,
    HlsAudioOnlyHeaderType,
    HlsAudioTrackTypeType,
    HlsCaptionLanguageSettingType,
    HlsCaptionSegmentLengthControlType,
    HlsClientCacheType,
    HlsCodecSpecificationType,
    HlsDescriptiveVideoServiceFlagType,
    HlsDirectoryStructureType,
    HlsEncryptionTypeType,
    HlsIFrameOnlyManifestType,
    HlsImageBasedTrickPlayType,
    HlsInitializationVectorInManifestType,
    HlsIntervalCadenceType,
    HlsKeyProviderTypeType,
    HlsManifestCompressionType,
    HlsManifestDurationFormatType,
    HlsOfflineEncryptedType,
    HlsOutputSelectionType,
    HlsProgramDateTimeType,
    HlsProgressiveWriteHlsManifestType,
    HlsSegmentControlType,
    HlsSegmentLengthControlType,
    HlsStreamInfResolutionType,
    HlsTargetDurationCompatibilityModeType,
    HlsTimedMetadataId3FrameType,
    ImscAccessibilitySubsType,
    ImscStylePassthroughType,
    InputDeblockFilterType,
    InputDenoiseFilterType,
    InputFilterEnableType,
    InputPolicyType,
    InputPsiControlType,
    InputRotateType,
    InputSampleRangeType,
    InputScanTypeType,
    InputTimecodeSourceType,
    JobPhaseType,
    JobStatusType,
    JobTemplateListByType,
    LanguageCodeType,
    M2tsAudioBufferModelType,
    M2tsAudioDurationType,
    M2tsBufferModelType,
    M2tsDataPtsControlType,
    M2tsEbpAudioIntervalType,
    M2tsEbpPlacementType,
    M2tsEsRateInPesType,
    M2tsForceTsVideoEbpOrderType,
    M2tsKlvMetadataType,
    M2tsNielsenId3Type,
    M2tsPcrControlType,
    M2tsPreventBufferUnderflowType,
    M2tsRateModeType,
    M2tsScte35SourceType,
    M2tsSegmentationMarkersType,
    M2tsSegmentationStyleType,
    M3u8AudioDurationType,
    M3u8DataPtsControlType,
    M3u8NielsenId3Type,
    M3u8PcrControlType,
    M3u8Scte35SourceType,
    MotionImageInsertionModeType,
    MotionImagePlaybackType,
    MovClapAtomType,
    MovCslgAtomType,
    MovMpeg2FourCCControlType,
    MovPaddingControlType,
    MovReferenceType,
    Mp3RateControlModeType,
    Mp4CslgAtomType,
    Mp4FreeSpaceBoxType,
    Mp4MoovPlacementType,
    MpdAccessibilityCaptionHintsType,
    MpdAudioDurationType,
    MpdCaptionContainerTypeType,
    MpdKlvMetadataType,
    MpdManifestMetadataSignalingType,
    MpdScte35EsamType,
    MpdScte35SourceType,
    MpdTimedMetadataBoxVersionType,
    MpdTimedMetadataType,
    Mpeg2AdaptiveQuantizationType,
    Mpeg2CodecLevelType,
    Mpeg2CodecProfileType,
    Mpeg2DynamicSubGopType,
    Mpeg2FramerateControlType,
    Mpeg2FramerateConversionAlgorithmType,
    Mpeg2GopSizeUnitsType,
    Mpeg2InterlaceModeType,
    Mpeg2IntraDcPrecisionType,
    Mpeg2ParControlType,
    Mpeg2QualityTuningLevelType,
    Mpeg2RateControlModeType,
    Mpeg2ScanTypeConversionModeType,
    Mpeg2SceneChangeDetectType,
    Mpeg2SlowPalType,
    Mpeg2SpatialAdaptiveQuantizationType,
    Mpeg2SyntaxType,
    Mpeg2TelecineType,
    Mpeg2TemporalAdaptiveQuantizationType,
    MsSmoothAudioDeduplicationType,
    MsSmoothFragmentLengthControlType,
    MsSmoothManifestEncodingType,
    MxfAfdSignalingType,
    MxfProfileType,
    MxfXavcDurationModeType,
    NielsenActiveWatermarkProcessTypeType,
    NielsenSourceWatermarkStatusTypeType,
    NielsenUniqueTicPerAudioTrackTypeType,
    NoiseFilterPostTemporalSharpeningStrengthType,
    NoiseFilterPostTemporalSharpeningType,
    NoiseReducerFilterType,
    OrderType,
    OutputGroupTypeType,
    OutputSdtType,
    PadVideoType,
    PresetListByType,
    PricingPlanType,
    ProresChromaSamplingType,
    ProresCodecProfileType,
    ProresFramerateControlType,
    ProresFramerateConversionAlgorithmType,
    ProresInterlaceModeType,
    ProresParControlType,
    ProresScanTypeConversionModeType,
    ProresSlowPalType,
    ProresTelecineType,
    QueueListByType,
    QueueStatusType,
    RenewalTypeType,
    RequiredFlagType,
    ReservationPlanStatusType,
    RespondToAfdType,
    RuleTypeType,
    S3ObjectCannedAclType,
    S3ServerSideEncryptionTypeType,
    S3StorageClassType,
    SampleRangeConversionType,
    ScalingBehaviorType,
    SccDestinationFramerateType,
    SimulateReservedQueueType,
    SrtStylePassthroughType,
    StatusUpdateIntervalType,
    TeletextPageTypeType,
    TimecodeBurninPositionType,
    TimecodeSourceType,
    TimedMetadataType,
    TsPtsOffsetType,
    TtmlStylePassthroughType,
    TypeType,
    UncompressedFourccType,
    UncompressedFramerateControlType,
    UncompressedFramerateConversionAlgorithmType,
    UncompressedInterlaceModeType,
    UncompressedScanTypeConversionModeType,
    UncompressedSlowPalType,
    UncompressedTelecineType,
    Vc3ClassType,
    Vc3FramerateControlType,
    Vc3FramerateConversionAlgorithmType,
    Vc3InterlaceModeType,
    Vc3ScanTypeConversionModeType,
    Vc3SlowPalType,
    Vc3TelecineType,
    VchipActionType,
    VideoCodecType,
    VideoTimecodeInsertionType,
    Vp8FramerateControlType,
    Vp8FramerateConversionAlgorithmType,
    Vp8ParControlType,
    Vp8QualityTuningLevelType,
    Vp9FramerateControlType,
    Vp9FramerateConversionAlgorithmType,
    Vp9ParControlType,
    Vp9QualityTuningLevelType,
    WatermarkingStrengthType,
    WavFormatType,
    WebvttAccessibilitySubsType,
    WebvttStylePassthroughType,
    Xavc4kIntraCbgProfileClassType,
    Xavc4kIntraVbrProfileClassType,
    Xavc4kProfileBitrateClassType,
    Xavc4kProfileCodecProfileType,
    Xavc4kProfileQualityTuningLevelType,
    XavcAdaptiveQuantizationType,
    XavcEntropyEncodingType,
    XavcFlickerAdaptiveQuantizationType,
    XavcFramerateControlType,
    XavcFramerateConversionAlgorithmType,
    XavcGopBReferenceType,
    XavcHdIntraCbgProfileClassType,
    XavcHdProfileBitrateClassType,
    XavcHdProfileQualityTuningLevelType,
    XavcHdProfileTelecineType,
    XavcInterlaceModeType,
    XavcProfileType,
    XavcSlowPalType,
    XavcSpatialAdaptiveQuantizationType,
    XavcTemporalAdaptiveQuantizationType,
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
    "AacSettingsTypeDef",
    "Ac3SettingsTypeDef",
    "AccelerationSettingsTypeDef",
    "AdvancedInputFilterSettingsTypeDef",
    "AiffSettingsTypeDef",
    "AllowedRenditionSizeTypeDef",
    "AncillarySourceSettingsTypeDef",
    "AssociateCertificateRequestRequestTypeDef",
    "AudioChannelTaggingSettingsPaginatorTypeDef",
    "AudioChannelTaggingSettingsTypeDef",
    "Eac3AtmosSettingsTypeDef",
    "Eac3SettingsTypeDef",
    "FlacSettingsTypeDef",
    "Mp2SettingsTypeDef",
    "Mp3SettingsTypeDef",
    "OpusSettingsTypeDef",
    "VorbisSettingsTypeDef",
    "WavSettingsTypeDef",
    "AudioNormalizationSettingsTypeDef",
    "AudioSelectorGroupPaginatorTypeDef",
    "AudioSelectorGroupTypeDef",
    "HlsRenditionGroupSettingsTypeDef",
    "ForceIncludeRenditionSizeTypeDef",
    "MinBottomRenditionSizeTypeDef",
    "MinTopRenditionSizeTypeDef",
    "Av1QvbrSettingsTypeDef",
    "AvailBlankingTypeDef",
    "AvcIntraUhdSettingsTypeDef",
    "BandwidthReductionFilterTypeDef",
    "BurninDestinationSettingsTypeDef",
    "CancelJobRequestRequestTypeDef",
    "DvbSubDestinationSettingsTypeDef",
    "EmbeddedDestinationSettingsTypeDef",
    "ImscDestinationSettingsTypeDef",
    "SccDestinationSettingsTypeDef",
    "SrtDestinationSettingsTypeDef",
    "TeletextDestinationSettingsPaginatorTypeDef",
    "TtmlDestinationSettingsTypeDef",
    "WebvttDestinationSettingsTypeDef",
    "TeletextDestinationSettingsTypeDef",
    "CaptionSourceFramerateTypeDef",
    "DvbSubSourceSettingsTypeDef",
    "EmbeddedSourceSettingsTypeDef",
    "TeletextSourceSettingsTypeDef",
    "TrackSourceSettingsTypeDef",
    "WebvttHlsSourceSettingsTypeDef",
    "OutputChannelMappingPaginatorTypeDef",
    "OutputChannelMappingTypeDef",
    "ClipLimitsTypeDef",
    "CmafAdditionalManifestPaginatorTypeDef",
    "CmafAdditionalManifestTypeDef",
    "SpekeKeyProviderCmafPaginatorTypeDef",
    "StaticKeyProviderTypeDef",
    "SpekeKeyProviderCmafTypeDef",
    "CmafImageBasedTrickPlaySettingsTypeDef",
    "CmfcSettingsTypeDef",
    "ColorConversion3DLUTSettingTypeDef",
    "Hdr10MetadataTypeDef",
    "F4vSettingsTypeDef",
    "M3u8SettingsPaginatorTypeDef",
    "MovSettingsTypeDef",
    "Mp4SettingsTypeDef",
    "MpdSettingsTypeDef",
    "M3u8SettingsTypeDef",
    "HopDestinationTypeDef",
    "ResponseMetadataTypeDef",
    "ReservationPlanSettingsTypeDef",
    "DashAdditionalManifestPaginatorTypeDef",
    "DashAdditionalManifestTypeDef",
    "SpekeKeyProviderPaginatorTypeDef",
    "SpekeKeyProviderTypeDef",
    "DashIsoImageBasedTrickPlaySettingsTypeDef",
    "DeinterlacerTypeDef",
    "DeleteJobTemplateRequestRequestTypeDef",
    "DeletePresetRequestRequestTypeDef",
    "DeleteQueueRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeEndpointsRequestRequestTypeDef",
    "EndpointTypeDef",
    "DisassociateCertificateRequestRequestTypeDef",
    "DolbyVisionLevel6MetadataTypeDef",
    "DvbNitSettingsTypeDef",
    "DvbSdtSettingsTypeDef",
    "DvbTdtSettingsTypeDef",
    "EsamManifestConfirmConditionNotificationTypeDef",
    "EsamSignalProcessingNotificationTypeDef",
    "ExtendedDataServicesTypeDef",
    "FrameCaptureSettingsTypeDef",
    "GetJobRequestRequestTypeDef",
    "GetJobTemplateRequestRequestTypeDef",
    "PolicyTypeDef",
    "GetPresetRequestRequestTypeDef",
    "GetQueueRequestRequestTypeDef",
    "H264QvbrSettingsTypeDef",
    "H265QvbrSettingsTypeDef",
    "Hdr10PlusTypeDef",
    "HlsAdditionalManifestPaginatorTypeDef",
    "HlsAdditionalManifestTypeDef",
    "HlsCaptionLanguageMappingTypeDef",
    "HlsImageBasedTrickPlaySettingsTypeDef",
    "HlsSettingsTypeDef",
    "Id3InsertionTypeDef",
    "InsertableImageTypeDef",
    "InputClippingTypeDef",
    "InputDecryptionSettingsTypeDef",
    "InputVideoGeneratorTypeDef",
    "RectangleTypeDef",
    "JobMessagesTypeDef",
    "QueueTransitionTypeDef",
    "TimingTypeDef",
    "WarningGroupTypeDef",
    "KantarWatermarkSettingsTypeDef",
    "NielsenConfigurationTypeDef",
    "NielsenNonLinearWatermarkSettingsTypeDef",
    "TimecodeConfigTypeDef",
    "ListJobTemplatesRequestRequestTypeDef",
    "ListJobsRequestRequestTypeDef",
    "ListPresetsRequestRequestTypeDef",
    "ListQueuesRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ResourceTagsTypeDef",
    "M2tsScte35EsamTypeDef",
    "MotionImageInsertionFramerateTypeDef",
    "MotionImageInsertionOffsetTypeDef",
    "Mpeg2SettingsTypeDef",
    "MsSmoothAdditionalManifestPaginatorTypeDef",
    "MsSmoothAdditionalManifestTypeDef",
    "MxfXavcProfileSettingsTypeDef",
    "NexGuardFileMarkerSettingsTypeDef",
    "NoiseReducerFilterSettingsTypeDef",
    "NoiseReducerSpatialFilterSettingsTypeDef",
    "NoiseReducerTemporalFilterSettingsTypeDef",
    "VideoDetailTypeDef",
    "ProresSettingsTypeDef",
    "ReservationPlanTypeDef",
    "S3DestinationAccessControlTypeDef",
    "S3EncryptionSettingsTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TimecodeBurninTypeDef",
    "UncompressedSettingsTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "Vc3SettingsTypeDef",
    "Vp8SettingsTypeDef",
    "Vp9SettingsTypeDef",
    "VideoOverlayInputClippingTypeDef",
    "Xavc4kIntraCbgProfileSettingsTypeDef",
    "Xavc4kIntraVbrProfileSettingsTypeDef",
    "Xavc4kProfileSettingsTypeDef",
    "XavcHdIntraCbgProfileSettingsTypeDef",
    "XavcHdProfileSettingsTypeDef",
    "AudioCodecSettingsTypeDef",
    "AutomatedAbrRulePaginatorTypeDef",
    "AutomatedAbrRuleTypeDef",
    "Av1SettingsTypeDef",
    "AvcIntraSettingsTypeDef",
    "CaptionDestinationSettingsPaginatorTypeDef",
    "CaptionDestinationSettingsTypeDef",
    "FileSourceSettingsTypeDef",
    "ChannelMappingPaginatorTypeDef",
    "ChannelMappingTypeDef",
    "CmafEncryptionSettingsPaginatorTypeDef",
    "CmafEncryptionSettingsTypeDef",
    "ColorCorrectorTypeDef",
    "VideoSelectorTypeDef",
    "CreateQueueRequestRequestTypeDef",
    "UpdateQueueRequestRequestTypeDef",
    "DashIsoEncryptionSettingsPaginatorTypeDef",
    "HlsEncryptionSettingsPaginatorTypeDef",
    "MsSmoothEncryptionSettingsPaginatorTypeDef",
    "DashIsoEncryptionSettingsTypeDef",
    "HlsEncryptionSettingsTypeDef",
    "MsSmoothEncryptionSettingsTypeDef",
    "DescribeEndpointsRequestDescribeEndpointsPaginateTypeDef",
    "ListJobTemplatesRequestListJobTemplatesPaginateTypeDef",
    "ListJobsRequestListJobsPaginateTypeDef",
    "ListPresetsRequestListPresetsPaginateTypeDef",
    "ListQueuesRequestListQueuesPaginateTypeDef",
    "DescribeEndpointsResponseTypeDef",
    "DolbyVisionTypeDef",
    "EsamSettingsTypeDef",
    "GetPolicyResponseTypeDef",
    "PutPolicyRequestRequestTypeDef",
    "PutPolicyResponseTypeDef",
    "H264SettingsTypeDef",
    "H265SettingsTypeDef",
    "OutputSettingsTypeDef",
    "TimedMetadataInsertionPaginatorTypeDef",
    "TimedMetadataInsertionTypeDef",
    "ImageInserterPaginatorTypeDef",
    "ImageInserterTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "M2tsSettingsPaginatorTypeDef",
    "M2tsSettingsTypeDef",
    "MotionImageInserterTypeDef",
    "MxfSettingsTypeDef",
    "PartnerWatermarkingTypeDef",
    "NoiseReducerTypeDef",
    "OutputDetailTypeDef",
    "QueueTypeDef",
    "S3DestinationSettingsTypeDef",
    "VideoOverlayInputPaginatorTypeDef",
    "VideoOverlayInputTypeDef",
    "XavcSettingsTypeDef",
    "AutomatedAbrSettingsPaginatorTypeDef",
    "AutomatedAbrSettingsTypeDef",
    "CaptionDescriptionPaginatorTypeDef",
    "CaptionDescriptionPresetPaginatorTypeDef",
    "CaptionDescriptionPresetTypeDef",
    "CaptionDescriptionTypeDef",
    "CaptionSourceSettingsTypeDef",
    "RemixSettingsPaginatorTypeDef",
    "RemixSettingsTypeDef",
    "ContainerSettingsPaginatorTypeDef",
    "ContainerSettingsTypeDef",
    "VideoPreprocessorPaginatorTypeDef",
    "VideoPreprocessorTypeDef",
    "OutputGroupDetailTypeDef",
    "CreateQueueResponseTypeDef",
    "GetQueueResponseTypeDef",
    "ListQueuesResponseTypeDef",
    "UpdateQueueResponseTypeDef",
    "DestinationSettingsTypeDef",
    "VideoOverlayPaginatorTypeDef",
    "VideoOverlayTypeDef",
    "VideoCodecSettingsTypeDef",
    "AutomatedEncodingSettingsPaginatorTypeDef",
    "AutomatedEncodingSettingsTypeDef",
    "CaptionSelectorTypeDef",
    "AudioDescriptionPaginatorTypeDef",
    "AudioSelectorPaginatorTypeDef",
    "AudioDescriptionTypeDef",
    "AudioSelectorTypeDef",
    "CmafGroupSettingsPaginatorTypeDef",
    "CmafGroupSettingsTypeDef",
    "DashIsoGroupSettingsPaginatorTypeDef",
    "DashIsoGroupSettingsTypeDef",
    "FileGroupSettingsTypeDef",
    "HlsGroupSettingsPaginatorTypeDef",
    "HlsGroupSettingsTypeDef",
    "MsSmoothGroupSettingsPaginatorTypeDef",
    "MsSmoothGroupSettingsTypeDef",
    "VideoDescriptionPaginatorTypeDef",
    "VideoDescriptionTypeDef",
    "InputPaginatorTypeDef",
    "InputTemplatePaginatorTypeDef",
    "InputTemplateTypeDef",
    "InputTypeDef",
    "OutputGroupSettingsPaginatorTypeDef",
    "OutputGroupSettingsTypeDef",
    "OutputPaginatorTypeDef",
    "PresetSettingsPaginatorTypeDef",
    "OutputTypeDef",
    "PresetSettingsTypeDef",
    "OutputGroupPaginatorTypeDef",
    "PresetPaginatorTypeDef",
    "OutputGroupTypeDef",
    "CreatePresetRequestRequestTypeDef",
    "PresetTypeDef",
    "UpdatePresetRequestRequestTypeDef",
    "JobSettingsPaginatorTypeDef",
    "JobTemplateSettingsPaginatorTypeDef",
    "ListPresetsResponsePaginatorTypeDef",
    "JobSettingsTypeDef",
    "JobTemplateSettingsTypeDef",
    "CreatePresetResponseTypeDef",
    "GetPresetResponseTypeDef",
    "ListPresetsResponseTypeDef",
    "UpdatePresetResponseTypeDef",
    "JobPaginatorTypeDef",
    "JobTemplatePaginatorTypeDef",
    "CreateJobRequestRequestTypeDef",
    "JobTypeDef",
    "CreateJobTemplateRequestRequestTypeDef",
    "JobTemplateTypeDef",
    "UpdateJobTemplateRequestRequestTypeDef",
    "ListJobsResponsePaginatorTypeDef",
    "ListJobTemplatesResponsePaginatorTypeDef",
    "CreateJobResponseTypeDef",
    "GetJobResponseTypeDef",
    "ListJobsResponseTypeDef",
    "CreateJobTemplateResponseTypeDef",
    "GetJobTemplateResponseTypeDef",
    "ListJobTemplatesResponseTypeDef",
    "UpdateJobTemplateResponseTypeDef",
)

AacSettingsTypeDef = TypedDict(
    "AacSettingsTypeDef",
    {
        "AudioDescriptionBroadcasterMix": NotRequired[AacAudioDescriptionBroadcasterMixType],
        "Bitrate": NotRequired[int],
        "CodecProfile": NotRequired[AacCodecProfileType],
        "CodingMode": NotRequired[AacCodingModeType],
        "RateControlMode": NotRequired[AacRateControlModeType],
        "RawFormat": NotRequired[AacRawFormatType],
        "SampleRate": NotRequired[int],
        "Specification": NotRequired[AacSpecificationType],
        "VbrQuality": NotRequired[AacVbrQualityType],
    },
)
Ac3SettingsTypeDef = TypedDict(
    "Ac3SettingsTypeDef",
    {
        "Bitrate": NotRequired[int],
        "BitstreamMode": NotRequired[Ac3BitstreamModeType],
        "CodingMode": NotRequired[Ac3CodingModeType],
        "Dialnorm": NotRequired[int],
        "DynamicRangeCompressionLine": NotRequired[Ac3DynamicRangeCompressionLineType],
        "DynamicRangeCompressionProfile": NotRequired[Ac3DynamicRangeCompressionProfileType],
        "DynamicRangeCompressionRf": NotRequired[Ac3DynamicRangeCompressionRfType],
        "LfeFilter": NotRequired[Ac3LfeFilterType],
        "MetadataControl": NotRequired[Ac3MetadataControlType],
        "SampleRate": NotRequired[int],
    },
)
AccelerationSettingsTypeDef = TypedDict(
    "AccelerationSettingsTypeDef",
    {
        "Mode": AccelerationModeType,
    },
)
AdvancedInputFilterSettingsTypeDef = TypedDict(
    "AdvancedInputFilterSettingsTypeDef",
    {
        "AddTexture": NotRequired[AdvancedInputFilterAddTextureType],
        "Sharpening": NotRequired[AdvancedInputFilterSharpenType],
    },
)
AiffSettingsTypeDef = TypedDict(
    "AiffSettingsTypeDef",
    {
        "BitDepth": NotRequired[int],
        "Channels": NotRequired[int],
        "SampleRate": NotRequired[int],
    },
)
AllowedRenditionSizeTypeDef = TypedDict(
    "AllowedRenditionSizeTypeDef",
    {
        "Height": NotRequired[int],
        "Required": NotRequired[RequiredFlagType],
        "Width": NotRequired[int],
    },
)
AncillarySourceSettingsTypeDef = TypedDict(
    "AncillarySourceSettingsTypeDef",
    {
        "Convert608To708": NotRequired[AncillaryConvert608To708Type],
        "SourceAncillaryChannelNumber": NotRequired[int],
        "TerminateCaptions": NotRequired[AncillaryTerminateCaptionsType],
    },
)
AssociateCertificateRequestRequestTypeDef = TypedDict(
    "AssociateCertificateRequestRequestTypeDef",
    {
        "Arn": str,
    },
)
AudioChannelTaggingSettingsPaginatorTypeDef = TypedDict(
    "AudioChannelTaggingSettingsPaginatorTypeDef",
    {
        "ChannelTag": NotRequired[AudioChannelTagType],
        "ChannelTags": NotRequired[List[AudioChannelTagType]],
    },
)
AudioChannelTaggingSettingsTypeDef = TypedDict(
    "AudioChannelTaggingSettingsTypeDef",
    {
        "ChannelTag": NotRequired[AudioChannelTagType],
        "ChannelTags": NotRequired[Sequence[AudioChannelTagType]],
    },
)
Eac3AtmosSettingsTypeDef = TypedDict(
    "Eac3AtmosSettingsTypeDef",
    {
        "Bitrate": NotRequired[int],
        "BitstreamMode": NotRequired[Literal["COMPLETE_MAIN"]],
        "CodingMode": NotRequired[Eac3AtmosCodingModeType],
        "DialogueIntelligence": NotRequired[Eac3AtmosDialogueIntelligenceType],
        "DownmixControl": NotRequired[Eac3AtmosDownmixControlType],
        "DynamicRangeCompressionLine": NotRequired[Eac3AtmosDynamicRangeCompressionLineType],
        "DynamicRangeCompressionRf": NotRequired[Eac3AtmosDynamicRangeCompressionRfType],
        "DynamicRangeControl": NotRequired[Eac3AtmosDynamicRangeControlType],
        "LoRoCenterMixLevel": NotRequired[float],
        "LoRoSurroundMixLevel": NotRequired[float],
        "LtRtCenterMixLevel": NotRequired[float],
        "LtRtSurroundMixLevel": NotRequired[float],
        "MeteringMode": NotRequired[Eac3AtmosMeteringModeType],
        "SampleRate": NotRequired[int],
        "SpeechThreshold": NotRequired[int],
        "StereoDownmix": NotRequired[Eac3AtmosStereoDownmixType],
        "SurroundExMode": NotRequired[Eac3AtmosSurroundExModeType],
    },
)
Eac3SettingsTypeDef = TypedDict(
    "Eac3SettingsTypeDef",
    {
        "AttenuationControl": NotRequired[Eac3AttenuationControlType],
        "Bitrate": NotRequired[int],
        "BitstreamMode": NotRequired[Eac3BitstreamModeType],
        "CodingMode": NotRequired[Eac3CodingModeType],
        "DcFilter": NotRequired[Eac3DcFilterType],
        "Dialnorm": NotRequired[int],
        "DynamicRangeCompressionLine": NotRequired[Eac3DynamicRangeCompressionLineType],
        "DynamicRangeCompressionRf": NotRequired[Eac3DynamicRangeCompressionRfType],
        "LfeControl": NotRequired[Eac3LfeControlType],
        "LfeFilter": NotRequired[Eac3LfeFilterType],
        "LoRoCenterMixLevel": NotRequired[float],
        "LoRoSurroundMixLevel": NotRequired[float],
        "LtRtCenterMixLevel": NotRequired[float],
        "LtRtSurroundMixLevel": NotRequired[float],
        "MetadataControl": NotRequired[Eac3MetadataControlType],
        "PassthroughControl": NotRequired[Eac3PassthroughControlType],
        "PhaseControl": NotRequired[Eac3PhaseControlType],
        "SampleRate": NotRequired[int],
        "StereoDownmix": NotRequired[Eac3StereoDownmixType],
        "SurroundExMode": NotRequired[Eac3SurroundExModeType],
        "SurroundMode": NotRequired[Eac3SurroundModeType],
    },
)
FlacSettingsTypeDef = TypedDict(
    "FlacSettingsTypeDef",
    {
        "BitDepth": NotRequired[int],
        "Channels": NotRequired[int],
        "SampleRate": NotRequired[int],
    },
)
Mp2SettingsTypeDef = TypedDict(
    "Mp2SettingsTypeDef",
    {
        "Bitrate": NotRequired[int],
        "Channels": NotRequired[int],
        "SampleRate": NotRequired[int],
    },
)
Mp3SettingsTypeDef = TypedDict(
    "Mp3SettingsTypeDef",
    {
        "Bitrate": NotRequired[int],
        "Channels": NotRequired[int],
        "RateControlMode": NotRequired[Mp3RateControlModeType],
        "SampleRate": NotRequired[int],
        "VbrQuality": NotRequired[int],
    },
)
OpusSettingsTypeDef = TypedDict(
    "OpusSettingsTypeDef",
    {
        "Bitrate": NotRequired[int],
        "Channels": NotRequired[int],
        "SampleRate": NotRequired[int],
    },
)
VorbisSettingsTypeDef = TypedDict(
    "VorbisSettingsTypeDef",
    {
        "Channels": NotRequired[int],
        "SampleRate": NotRequired[int],
        "VbrQuality": NotRequired[int],
    },
)
WavSettingsTypeDef = TypedDict(
    "WavSettingsTypeDef",
    {
        "BitDepth": NotRequired[int],
        "Channels": NotRequired[int],
        "Format": NotRequired[WavFormatType],
        "SampleRate": NotRequired[int],
    },
)
AudioNormalizationSettingsTypeDef = TypedDict(
    "AudioNormalizationSettingsTypeDef",
    {
        "Algorithm": NotRequired[AudioNormalizationAlgorithmType],
        "AlgorithmControl": NotRequired[AudioNormalizationAlgorithmControlType],
        "CorrectionGateLevel": NotRequired[int],
        "LoudnessLogging": NotRequired[AudioNormalizationLoudnessLoggingType],
        "PeakCalculation": NotRequired[AudioNormalizationPeakCalculationType],
        "TargetLkfs": NotRequired[float],
        "TruePeakLimiterThreshold": NotRequired[float],
    },
)
AudioSelectorGroupPaginatorTypeDef = TypedDict(
    "AudioSelectorGroupPaginatorTypeDef",
    {
        "AudioSelectorNames": NotRequired[List[str]],
    },
)
AudioSelectorGroupTypeDef = TypedDict(
    "AudioSelectorGroupTypeDef",
    {
        "AudioSelectorNames": NotRequired[Sequence[str]],
    },
)
HlsRenditionGroupSettingsTypeDef = TypedDict(
    "HlsRenditionGroupSettingsTypeDef",
    {
        "RenditionGroupId": NotRequired[str],
        "RenditionLanguageCode": NotRequired[LanguageCodeType],
        "RenditionName": NotRequired[str],
    },
)
ForceIncludeRenditionSizeTypeDef = TypedDict(
    "ForceIncludeRenditionSizeTypeDef",
    {
        "Height": NotRequired[int],
        "Width": NotRequired[int],
    },
)
MinBottomRenditionSizeTypeDef = TypedDict(
    "MinBottomRenditionSizeTypeDef",
    {
        "Height": NotRequired[int],
        "Width": NotRequired[int],
    },
)
MinTopRenditionSizeTypeDef = TypedDict(
    "MinTopRenditionSizeTypeDef",
    {
        "Height": NotRequired[int],
        "Width": NotRequired[int],
    },
)
Av1QvbrSettingsTypeDef = TypedDict(
    "Av1QvbrSettingsTypeDef",
    {
        "QvbrQualityLevel": NotRequired[int],
        "QvbrQualityLevelFineTune": NotRequired[float],
    },
)
AvailBlankingTypeDef = TypedDict(
    "AvailBlankingTypeDef",
    {
        "AvailBlankingImage": NotRequired[str],
    },
)
AvcIntraUhdSettingsTypeDef = TypedDict(
    "AvcIntraUhdSettingsTypeDef",
    {
        "QualityTuningLevel": NotRequired[AvcIntraUhdQualityTuningLevelType],
    },
)
BandwidthReductionFilterTypeDef = TypedDict(
    "BandwidthReductionFilterTypeDef",
    {
        "Sharpening": NotRequired[BandwidthReductionFilterSharpeningType],
        "Strength": NotRequired[BandwidthReductionFilterStrengthType],
    },
)
BurninDestinationSettingsTypeDef = TypedDict(
    "BurninDestinationSettingsTypeDef",
    {
        "Alignment": NotRequired[BurninSubtitleAlignmentType],
        "ApplyFontColor": NotRequired[BurninSubtitleApplyFontColorType],
        "BackgroundColor": NotRequired[BurninSubtitleBackgroundColorType],
        "BackgroundOpacity": NotRequired[int],
        "FallbackFont": NotRequired[BurninSubtitleFallbackFontType],
        "FontColor": NotRequired[BurninSubtitleFontColorType],
        "FontFileBold": NotRequired[str],
        "FontFileBoldItalic": NotRequired[str],
        "FontFileItalic": NotRequired[str],
        "FontFileRegular": NotRequired[str],
        "FontOpacity": NotRequired[int],
        "FontResolution": NotRequired[int],
        "FontScript": NotRequired[FontScriptType],
        "FontSize": NotRequired[int],
        "HexFontColor": NotRequired[str],
        "OutlineColor": NotRequired[BurninSubtitleOutlineColorType],
        "OutlineSize": NotRequired[int],
        "ShadowColor": NotRequired[BurninSubtitleShadowColorType],
        "ShadowOpacity": NotRequired[int],
        "ShadowXOffset": NotRequired[int],
        "ShadowYOffset": NotRequired[int],
        "StylePassthrough": NotRequired[BurnInSubtitleStylePassthroughType],
        "TeletextSpacing": NotRequired[BurninSubtitleTeletextSpacingType],
        "XPosition": NotRequired[int],
        "YPosition": NotRequired[int],
    },
)
CancelJobRequestRequestTypeDef = TypedDict(
    "CancelJobRequestRequestTypeDef",
    {
        "Id": str,
    },
)
DvbSubDestinationSettingsTypeDef = TypedDict(
    "DvbSubDestinationSettingsTypeDef",
    {
        "Alignment": NotRequired[DvbSubtitleAlignmentType],
        "ApplyFontColor": NotRequired[DvbSubtitleApplyFontColorType],
        "BackgroundColor": NotRequired[DvbSubtitleBackgroundColorType],
        "BackgroundOpacity": NotRequired[int],
        "DdsHandling": NotRequired[DvbddsHandlingType],
        "DdsXCoordinate": NotRequired[int],
        "DdsYCoordinate": NotRequired[int],
        "FallbackFont": NotRequired[DvbSubSubtitleFallbackFontType],
        "FontColor": NotRequired[DvbSubtitleFontColorType],
        "FontFileBold": NotRequired[str],
        "FontFileBoldItalic": NotRequired[str],
        "FontFileItalic": NotRequired[str],
        "FontFileRegular": NotRequired[str],
        "FontOpacity": NotRequired[int],
        "FontResolution": NotRequired[int],
        "FontScript": NotRequired[FontScriptType],
        "FontSize": NotRequired[int],
        "Height": NotRequired[int],
        "HexFontColor": NotRequired[str],
        "OutlineColor": NotRequired[DvbSubtitleOutlineColorType],
        "OutlineSize": NotRequired[int],
        "ShadowColor": NotRequired[DvbSubtitleShadowColorType],
        "ShadowOpacity": NotRequired[int],
        "ShadowXOffset": NotRequired[int],
        "ShadowYOffset": NotRequired[int],
        "StylePassthrough": NotRequired[DvbSubtitleStylePassthroughType],
        "SubtitlingType": NotRequired[DvbSubtitlingTypeType],
        "TeletextSpacing": NotRequired[DvbSubtitleTeletextSpacingType],
        "Width": NotRequired[int],
        "XPosition": NotRequired[int],
        "YPosition": NotRequired[int],
    },
)
EmbeddedDestinationSettingsTypeDef = TypedDict(
    "EmbeddedDestinationSettingsTypeDef",
    {
        "Destination608ChannelNumber": NotRequired[int],
        "Destination708ServiceNumber": NotRequired[int],
    },
)
ImscDestinationSettingsTypeDef = TypedDict(
    "ImscDestinationSettingsTypeDef",
    {
        "Accessibility": NotRequired[ImscAccessibilitySubsType],
        "StylePassthrough": NotRequired[ImscStylePassthroughType],
    },
)
SccDestinationSettingsTypeDef = TypedDict(
    "SccDestinationSettingsTypeDef",
    {
        "Framerate": NotRequired[SccDestinationFramerateType],
    },
)
SrtDestinationSettingsTypeDef = TypedDict(
    "SrtDestinationSettingsTypeDef",
    {
        "StylePassthrough": NotRequired[SrtStylePassthroughType],
    },
)
TeletextDestinationSettingsPaginatorTypeDef = TypedDict(
    "TeletextDestinationSettingsPaginatorTypeDef",
    {
        "PageNumber": NotRequired[str],
        "PageTypes": NotRequired[List[TeletextPageTypeType]],
    },
)
TtmlDestinationSettingsTypeDef = TypedDict(
    "TtmlDestinationSettingsTypeDef",
    {
        "StylePassthrough": NotRequired[TtmlStylePassthroughType],
    },
)
WebvttDestinationSettingsTypeDef = TypedDict(
    "WebvttDestinationSettingsTypeDef",
    {
        "Accessibility": NotRequired[WebvttAccessibilitySubsType],
        "StylePassthrough": NotRequired[WebvttStylePassthroughType],
    },
)
TeletextDestinationSettingsTypeDef = TypedDict(
    "TeletextDestinationSettingsTypeDef",
    {
        "PageNumber": NotRequired[str],
        "PageTypes": NotRequired[Sequence[TeletextPageTypeType]],
    },
)
CaptionSourceFramerateTypeDef = TypedDict(
    "CaptionSourceFramerateTypeDef",
    {
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
    },
)
DvbSubSourceSettingsTypeDef = TypedDict(
    "DvbSubSourceSettingsTypeDef",
    {
        "Pid": NotRequired[int],
    },
)
EmbeddedSourceSettingsTypeDef = TypedDict(
    "EmbeddedSourceSettingsTypeDef",
    {
        "Convert608To708": NotRequired[EmbeddedConvert608To708Type],
        "Source608ChannelNumber": NotRequired[int],
        "Source608TrackNumber": NotRequired[int],
        "TerminateCaptions": NotRequired[EmbeddedTerminateCaptionsType],
    },
)
TeletextSourceSettingsTypeDef = TypedDict(
    "TeletextSourceSettingsTypeDef",
    {
        "PageNumber": NotRequired[str],
    },
)
TrackSourceSettingsTypeDef = TypedDict(
    "TrackSourceSettingsTypeDef",
    {
        "TrackNumber": NotRequired[int],
    },
)
WebvttHlsSourceSettingsTypeDef = TypedDict(
    "WebvttHlsSourceSettingsTypeDef",
    {
        "RenditionGroupId": NotRequired[str],
        "RenditionLanguageCode": NotRequired[LanguageCodeType],
        "RenditionName": NotRequired[str],
    },
)
OutputChannelMappingPaginatorTypeDef = TypedDict(
    "OutputChannelMappingPaginatorTypeDef",
    {
        "InputChannels": NotRequired[List[int]],
        "InputChannelsFineTune": NotRequired[List[float]],
    },
)
OutputChannelMappingTypeDef = TypedDict(
    "OutputChannelMappingTypeDef",
    {
        "InputChannels": NotRequired[Sequence[int]],
        "InputChannelsFineTune": NotRequired[Sequence[float]],
    },
)
ClipLimitsTypeDef = TypedDict(
    "ClipLimitsTypeDef",
    {
        "MaximumRGBTolerance": NotRequired[int],
        "MaximumYUV": NotRequired[int],
        "MinimumRGBTolerance": NotRequired[int],
        "MinimumYUV": NotRequired[int],
    },
)
CmafAdditionalManifestPaginatorTypeDef = TypedDict(
    "CmafAdditionalManifestPaginatorTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[List[str]],
    },
)
CmafAdditionalManifestTypeDef = TypedDict(
    "CmafAdditionalManifestTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[Sequence[str]],
    },
)
SpekeKeyProviderCmafPaginatorTypeDef = TypedDict(
    "SpekeKeyProviderCmafPaginatorTypeDef",
    {
        "CertificateArn": NotRequired[str],
        "DashSignaledSystemIds": NotRequired[List[str]],
        "HlsSignaledSystemIds": NotRequired[List[str]],
        "ResourceId": NotRequired[str],
        "Url": NotRequired[str],
    },
)
StaticKeyProviderTypeDef = TypedDict(
    "StaticKeyProviderTypeDef",
    {
        "KeyFormat": NotRequired[str],
        "KeyFormatVersions": NotRequired[str],
        "StaticKeyValue": NotRequired[str],
        "Url": NotRequired[str],
    },
)
SpekeKeyProviderCmafTypeDef = TypedDict(
    "SpekeKeyProviderCmafTypeDef",
    {
        "CertificateArn": NotRequired[str],
        "DashSignaledSystemIds": NotRequired[Sequence[str]],
        "HlsSignaledSystemIds": NotRequired[Sequence[str]],
        "ResourceId": NotRequired[str],
        "Url": NotRequired[str],
    },
)
CmafImageBasedTrickPlaySettingsTypeDef = TypedDict(
    "CmafImageBasedTrickPlaySettingsTypeDef",
    {
        "IntervalCadence": NotRequired[CmafIntervalCadenceType],
        "ThumbnailHeight": NotRequired[int],
        "ThumbnailInterval": NotRequired[float],
        "ThumbnailWidth": NotRequired[int],
        "TileHeight": NotRequired[int],
        "TileWidth": NotRequired[int],
    },
)
CmfcSettingsTypeDef = TypedDict(
    "CmfcSettingsTypeDef",
    {
        "AudioDuration": NotRequired[CmfcAudioDurationType],
        "AudioGroupId": NotRequired[str],
        "AudioRenditionSets": NotRequired[str],
        "AudioTrackType": NotRequired[CmfcAudioTrackTypeType],
        "DescriptiveVideoServiceFlag": NotRequired[CmfcDescriptiveVideoServiceFlagType],
        "IFrameOnlyManifest": NotRequired[CmfcIFrameOnlyManifestType],
        "KlvMetadata": NotRequired[CmfcKlvMetadataType],
        "ManifestMetadataSignaling": NotRequired[CmfcManifestMetadataSignalingType],
        "Scte35Esam": NotRequired[CmfcScte35EsamType],
        "Scte35Source": NotRequired[CmfcScte35SourceType],
        "TimedMetadata": NotRequired[CmfcTimedMetadataType],
        "TimedMetadataBoxVersion": NotRequired[CmfcTimedMetadataBoxVersionType],
        "TimedMetadataSchemeIdUri": NotRequired[str],
        "TimedMetadataValue": NotRequired[str],
    },
)
ColorConversion3DLUTSettingTypeDef = TypedDict(
    "ColorConversion3DLUTSettingTypeDef",
    {
        "FileInput": NotRequired[str],
        "InputColorSpace": NotRequired[ColorSpaceType],
        "InputMasteringLuminance": NotRequired[int],
        "OutputColorSpace": NotRequired[ColorSpaceType],
        "OutputMasteringLuminance": NotRequired[int],
    },
)
Hdr10MetadataTypeDef = TypedDict(
    "Hdr10MetadataTypeDef",
    {
        "BluePrimaryX": NotRequired[int],
        "BluePrimaryY": NotRequired[int],
        "GreenPrimaryX": NotRequired[int],
        "GreenPrimaryY": NotRequired[int],
        "MaxContentLightLevel": NotRequired[int],
        "MaxFrameAverageLightLevel": NotRequired[int],
        "MaxLuminance": NotRequired[int],
        "MinLuminance": NotRequired[int],
        "RedPrimaryX": NotRequired[int],
        "RedPrimaryY": NotRequired[int],
        "WhitePointX": NotRequired[int],
        "WhitePointY": NotRequired[int],
    },
)
F4vSettingsTypeDef = TypedDict(
    "F4vSettingsTypeDef",
    {
        "MoovPlacement": NotRequired[F4vMoovPlacementType],
    },
)
M3u8SettingsPaginatorTypeDef = TypedDict(
    "M3u8SettingsPaginatorTypeDef",
    {
        "AudioDuration": NotRequired[M3u8AudioDurationType],
        "AudioFramesPerPes": NotRequired[int],
        "AudioPids": NotRequired[List[int]],
        "DataPTSControl": NotRequired[M3u8DataPtsControlType],
        "MaxPcrInterval": NotRequired[int],
        "NielsenId3": NotRequired[M3u8NielsenId3Type],
        "PatInterval": NotRequired[int],
        "PcrControl": NotRequired[M3u8PcrControlType],
        "PcrPid": NotRequired[int],
        "PmtInterval": NotRequired[int],
        "PmtPid": NotRequired[int],
        "PrivateMetadataPid": NotRequired[int],
        "ProgramNumber": NotRequired[int],
        "PtsOffset": NotRequired[int],
        "PtsOffsetMode": NotRequired[TsPtsOffsetType],
        "Scte35Pid": NotRequired[int],
        "Scte35Source": NotRequired[M3u8Scte35SourceType],
        "TimedMetadata": NotRequired[TimedMetadataType],
        "TimedMetadataPid": NotRequired[int],
        "TransportStreamId": NotRequired[int],
        "VideoPid": NotRequired[int],
    },
)
MovSettingsTypeDef = TypedDict(
    "MovSettingsTypeDef",
    {
        "ClapAtom": NotRequired[MovClapAtomType],
        "CslgAtom": NotRequired[MovCslgAtomType],
        "Mpeg2FourCCControl": NotRequired[MovMpeg2FourCCControlType],
        "PaddingControl": NotRequired[MovPaddingControlType],
        "Reference": NotRequired[MovReferenceType],
    },
)
Mp4SettingsTypeDef = TypedDict(
    "Mp4SettingsTypeDef",
    {
        "AudioDuration": NotRequired[CmfcAudioDurationType],
        "CslgAtom": NotRequired[Mp4CslgAtomType],
        "CttsVersion": NotRequired[int],
        "FreeSpaceBox": NotRequired[Mp4FreeSpaceBoxType],
        "MoovPlacement": NotRequired[Mp4MoovPlacementType],
        "Mp4MajorBrand": NotRequired[str],
    },
)
MpdSettingsTypeDef = TypedDict(
    "MpdSettingsTypeDef",
    {
        "AccessibilityCaptionHints": NotRequired[MpdAccessibilityCaptionHintsType],
        "AudioDuration": NotRequired[MpdAudioDurationType],
        "CaptionContainerType": NotRequired[MpdCaptionContainerTypeType],
        "KlvMetadata": NotRequired[MpdKlvMetadataType],
        "ManifestMetadataSignaling": NotRequired[MpdManifestMetadataSignalingType],
        "Scte35Esam": NotRequired[MpdScte35EsamType],
        "Scte35Source": NotRequired[MpdScte35SourceType],
        "TimedMetadata": NotRequired[MpdTimedMetadataType],
        "TimedMetadataBoxVersion": NotRequired[MpdTimedMetadataBoxVersionType],
        "TimedMetadataSchemeIdUri": NotRequired[str],
        "TimedMetadataValue": NotRequired[str],
    },
)
M3u8SettingsTypeDef = TypedDict(
    "M3u8SettingsTypeDef",
    {
        "AudioDuration": NotRequired[M3u8AudioDurationType],
        "AudioFramesPerPes": NotRequired[int],
        "AudioPids": NotRequired[Sequence[int]],
        "DataPTSControl": NotRequired[M3u8DataPtsControlType],
        "MaxPcrInterval": NotRequired[int],
        "NielsenId3": NotRequired[M3u8NielsenId3Type],
        "PatInterval": NotRequired[int],
        "PcrControl": NotRequired[M3u8PcrControlType],
        "PcrPid": NotRequired[int],
        "PmtInterval": NotRequired[int],
        "PmtPid": NotRequired[int],
        "PrivateMetadataPid": NotRequired[int],
        "ProgramNumber": NotRequired[int],
        "PtsOffset": NotRequired[int],
        "PtsOffsetMode": NotRequired[TsPtsOffsetType],
        "Scte35Pid": NotRequired[int],
        "Scte35Source": NotRequired[M3u8Scte35SourceType],
        "TimedMetadata": NotRequired[TimedMetadataType],
        "TimedMetadataPid": NotRequired[int],
        "TransportStreamId": NotRequired[int],
        "VideoPid": NotRequired[int],
    },
)
HopDestinationTypeDef = TypedDict(
    "HopDestinationTypeDef",
    {
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "WaitMinutes": NotRequired[int],
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
ReservationPlanSettingsTypeDef = TypedDict(
    "ReservationPlanSettingsTypeDef",
    {
        "Commitment": Literal["ONE_YEAR"],
        "RenewalType": RenewalTypeType,
        "ReservedSlots": int,
    },
)
DashAdditionalManifestPaginatorTypeDef = TypedDict(
    "DashAdditionalManifestPaginatorTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[List[str]],
    },
)
DashAdditionalManifestTypeDef = TypedDict(
    "DashAdditionalManifestTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[Sequence[str]],
    },
)
SpekeKeyProviderPaginatorTypeDef = TypedDict(
    "SpekeKeyProviderPaginatorTypeDef",
    {
        "CertificateArn": NotRequired[str],
        "ResourceId": NotRequired[str],
        "SystemIds": NotRequired[List[str]],
        "Url": NotRequired[str],
    },
)
SpekeKeyProviderTypeDef = TypedDict(
    "SpekeKeyProviderTypeDef",
    {
        "CertificateArn": NotRequired[str],
        "ResourceId": NotRequired[str],
        "SystemIds": NotRequired[Sequence[str]],
        "Url": NotRequired[str],
    },
)
DashIsoImageBasedTrickPlaySettingsTypeDef = TypedDict(
    "DashIsoImageBasedTrickPlaySettingsTypeDef",
    {
        "IntervalCadence": NotRequired[DashIsoIntervalCadenceType],
        "ThumbnailHeight": NotRequired[int],
        "ThumbnailInterval": NotRequired[float],
        "ThumbnailWidth": NotRequired[int],
        "TileHeight": NotRequired[int],
        "TileWidth": NotRequired[int],
    },
)
DeinterlacerTypeDef = TypedDict(
    "DeinterlacerTypeDef",
    {
        "Algorithm": NotRequired[DeinterlaceAlgorithmType],
        "Control": NotRequired[DeinterlacerControlType],
        "Mode": NotRequired[DeinterlacerModeType],
    },
)
DeleteJobTemplateRequestRequestTypeDef = TypedDict(
    "DeleteJobTemplateRequestRequestTypeDef",
    {
        "Name": str,
    },
)
DeletePresetRequestRequestTypeDef = TypedDict(
    "DeletePresetRequestRequestTypeDef",
    {
        "Name": str,
    },
)
DeleteQueueRequestRequestTypeDef = TypedDict(
    "DeleteQueueRequestRequestTypeDef",
    {
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
DescribeEndpointsRequestRequestTypeDef = TypedDict(
    "DescribeEndpointsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "Mode": NotRequired[DescribeEndpointsModeType],
        "NextToken": NotRequired[str],
    },
)
EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "Url": NotRequired[str],
    },
)
DisassociateCertificateRequestRequestTypeDef = TypedDict(
    "DisassociateCertificateRequestRequestTypeDef",
    {
        "Arn": str,
    },
)
DolbyVisionLevel6MetadataTypeDef = TypedDict(
    "DolbyVisionLevel6MetadataTypeDef",
    {
        "MaxCll": NotRequired[int],
        "MaxFall": NotRequired[int],
    },
)
DvbNitSettingsTypeDef = TypedDict(
    "DvbNitSettingsTypeDef",
    {
        "NetworkId": NotRequired[int],
        "NetworkName": NotRequired[str],
        "NitInterval": NotRequired[int],
    },
)
DvbSdtSettingsTypeDef = TypedDict(
    "DvbSdtSettingsTypeDef",
    {
        "OutputSdt": NotRequired[OutputSdtType],
        "SdtInterval": NotRequired[int],
        "ServiceName": NotRequired[str],
        "ServiceProviderName": NotRequired[str],
    },
)
DvbTdtSettingsTypeDef = TypedDict(
    "DvbTdtSettingsTypeDef",
    {
        "TdtInterval": NotRequired[int],
    },
)
EsamManifestConfirmConditionNotificationTypeDef = TypedDict(
    "EsamManifestConfirmConditionNotificationTypeDef",
    {
        "MccXml": NotRequired[str],
    },
)
EsamSignalProcessingNotificationTypeDef = TypedDict(
    "EsamSignalProcessingNotificationTypeDef",
    {
        "SccXml": NotRequired[str],
    },
)
ExtendedDataServicesTypeDef = TypedDict(
    "ExtendedDataServicesTypeDef",
    {
        "CopyProtectionAction": NotRequired[CopyProtectionActionType],
        "VchipAction": NotRequired[VchipActionType],
    },
)
FrameCaptureSettingsTypeDef = TypedDict(
    "FrameCaptureSettingsTypeDef",
    {
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "MaxCaptures": NotRequired[int],
        "Quality": NotRequired[int],
    },
)
GetJobRequestRequestTypeDef = TypedDict(
    "GetJobRequestRequestTypeDef",
    {
        "Id": str,
    },
)
GetJobTemplateRequestRequestTypeDef = TypedDict(
    "GetJobTemplateRequestRequestTypeDef",
    {
        "Name": str,
    },
)
PolicyTypeDef = TypedDict(
    "PolicyTypeDef",
    {
        "HttpInputs": NotRequired[InputPolicyType],
        "HttpsInputs": NotRequired[InputPolicyType],
        "S3Inputs": NotRequired[InputPolicyType],
    },
)
GetPresetRequestRequestTypeDef = TypedDict(
    "GetPresetRequestRequestTypeDef",
    {
        "Name": str,
    },
)
GetQueueRequestRequestTypeDef = TypedDict(
    "GetQueueRequestRequestTypeDef",
    {
        "Name": str,
    },
)
H264QvbrSettingsTypeDef = TypedDict(
    "H264QvbrSettingsTypeDef",
    {
        "MaxAverageBitrate": NotRequired[int],
        "QvbrQualityLevel": NotRequired[int],
        "QvbrQualityLevelFineTune": NotRequired[float],
    },
)
H265QvbrSettingsTypeDef = TypedDict(
    "H265QvbrSettingsTypeDef",
    {
        "MaxAverageBitrate": NotRequired[int],
        "QvbrQualityLevel": NotRequired[int],
        "QvbrQualityLevelFineTune": NotRequired[float],
    },
)
Hdr10PlusTypeDef = TypedDict(
    "Hdr10PlusTypeDef",
    {
        "MasteringMonitorNits": NotRequired[int],
        "TargetMonitorNits": NotRequired[int],
    },
)
HlsAdditionalManifestPaginatorTypeDef = TypedDict(
    "HlsAdditionalManifestPaginatorTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[List[str]],
    },
)
HlsAdditionalManifestTypeDef = TypedDict(
    "HlsAdditionalManifestTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[Sequence[str]],
    },
)
HlsCaptionLanguageMappingTypeDef = TypedDict(
    "HlsCaptionLanguageMappingTypeDef",
    {
        "CaptionChannel": NotRequired[int],
        "CustomLanguageCode": NotRequired[str],
        "LanguageCode": NotRequired[LanguageCodeType],
        "LanguageDescription": NotRequired[str],
    },
)
HlsImageBasedTrickPlaySettingsTypeDef = TypedDict(
    "HlsImageBasedTrickPlaySettingsTypeDef",
    {
        "IntervalCadence": NotRequired[HlsIntervalCadenceType],
        "ThumbnailHeight": NotRequired[int],
        "ThumbnailInterval": NotRequired[float],
        "ThumbnailWidth": NotRequired[int],
        "TileHeight": NotRequired[int],
        "TileWidth": NotRequired[int],
    },
)
HlsSettingsTypeDef = TypedDict(
    "HlsSettingsTypeDef",
    {
        "AudioGroupId": NotRequired[str],
        "AudioOnlyContainer": NotRequired[HlsAudioOnlyContainerType],
        "AudioRenditionSets": NotRequired[str],
        "AudioTrackType": NotRequired[HlsAudioTrackTypeType],
        "DescriptiveVideoServiceFlag": NotRequired[HlsDescriptiveVideoServiceFlagType],
        "IFrameOnlyManifest": NotRequired[HlsIFrameOnlyManifestType],
        "SegmentModifier": NotRequired[str],
    },
)
Id3InsertionTypeDef = TypedDict(
    "Id3InsertionTypeDef",
    {
        "Id3": NotRequired[str],
        "Timecode": NotRequired[str],
    },
)
InsertableImageTypeDef = TypedDict(
    "InsertableImageTypeDef",
    {
        "Duration": NotRequired[int],
        "FadeIn": NotRequired[int],
        "FadeOut": NotRequired[int],
        "Height": NotRequired[int],
        "ImageInserterInput": NotRequired[str],
        "ImageX": NotRequired[int],
        "ImageY": NotRequired[int],
        "Layer": NotRequired[int],
        "Opacity": NotRequired[int],
        "StartTime": NotRequired[str],
        "Width": NotRequired[int],
    },
)
InputClippingTypeDef = TypedDict(
    "InputClippingTypeDef",
    {
        "EndTimecode": NotRequired[str],
        "StartTimecode": NotRequired[str],
    },
)
InputDecryptionSettingsTypeDef = TypedDict(
    "InputDecryptionSettingsTypeDef",
    {
        "DecryptionMode": NotRequired[DecryptionModeType],
        "EncryptedDecryptionKey": NotRequired[str],
        "InitializationVector": NotRequired[str],
        "KmsKeyRegion": NotRequired[str],
    },
)
InputVideoGeneratorTypeDef = TypedDict(
    "InputVideoGeneratorTypeDef",
    {
        "Duration": NotRequired[int],
    },
)
RectangleTypeDef = TypedDict(
    "RectangleTypeDef",
    {
        "Height": NotRequired[int],
        "Width": NotRequired[int],
        "X": NotRequired[int],
        "Y": NotRequired[int],
    },
)
JobMessagesTypeDef = TypedDict(
    "JobMessagesTypeDef",
    {
        "Info": NotRequired[List[str]],
        "Warning": NotRequired[List[str]],
    },
)
QueueTransitionTypeDef = TypedDict(
    "QueueTransitionTypeDef",
    {
        "DestinationQueue": NotRequired[str],
        "SourceQueue": NotRequired[str],
        "Timestamp": NotRequired[datetime],
    },
)
TimingTypeDef = TypedDict(
    "TimingTypeDef",
    {
        "FinishTime": NotRequired[datetime],
        "StartTime": NotRequired[datetime],
        "SubmitTime": NotRequired[datetime],
    },
)
WarningGroupTypeDef = TypedDict(
    "WarningGroupTypeDef",
    {
        "Code": int,
        "Count": int,
    },
)
KantarWatermarkSettingsTypeDef = TypedDict(
    "KantarWatermarkSettingsTypeDef",
    {
        "ChannelName": NotRequired[str],
        "ContentReference": NotRequired[str],
        "CredentialsSecretName": NotRequired[str],
        "FileOffset": NotRequired[float],
        "KantarLicenseId": NotRequired[int],
        "KantarServerUrl": NotRequired[str],
        "LogDestination": NotRequired[str],
        "Metadata3": NotRequired[str],
        "Metadata4": NotRequired[str],
        "Metadata5": NotRequired[str],
        "Metadata6": NotRequired[str],
        "Metadata7": NotRequired[str],
        "Metadata8": NotRequired[str],
    },
)
NielsenConfigurationTypeDef = TypedDict(
    "NielsenConfigurationTypeDef",
    {
        "BreakoutCode": NotRequired[int],
        "DistributorId": NotRequired[str],
    },
)
NielsenNonLinearWatermarkSettingsTypeDef = TypedDict(
    "NielsenNonLinearWatermarkSettingsTypeDef",
    {
        "ActiveWatermarkProcess": NotRequired[NielsenActiveWatermarkProcessTypeType],
        "AdiFilename": NotRequired[str],
        "AssetId": NotRequired[str],
        "AssetName": NotRequired[str],
        "CbetSourceId": NotRequired[str],
        "EpisodeId": NotRequired[str],
        "MetadataDestination": NotRequired[str],
        "SourceId": NotRequired[int],
        "SourceWatermarkStatus": NotRequired[NielsenSourceWatermarkStatusTypeType],
        "TicServerUrl": NotRequired[str],
        "UniqueTicPerAudioTrack": NotRequired[NielsenUniqueTicPerAudioTrackTypeType],
    },
)
TimecodeConfigTypeDef = TypedDict(
    "TimecodeConfigTypeDef",
    {
        "Anchor": NotRequired[str],
        "Source": NotRequired[TimecodeSourceType],
        "Start": NotRequired[str],
        "TimestampOffset": NotRequired[str],
    },
)
ListJobTemplatesRequestRequestTypeDef = TypedDict(
    "ListJobTemplatesRequestRequestTypeDef",
    {
        "Category": NotRequired[str],
        "ListBy": NotRequired[JobTemplateListByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Order": NotRequired[OrderType],
    },
)
ListJobsRequestRequestTypeDef = TypedDict(
    "ListJobsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Order": NotRequired[OrderType],
        "Queue": NotRequired[str],
        "Status": NotRequired[JobStatusType],
    },
)
ListPresetsRequestRequestTypeDef = TypedDict(
    "ListPresetsRequestRequestTypeDef",
    {
        "Category": NotRequired[str],
        "ListBy": NotRequired[PresetListByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Order": NotRequired[OrderType],
    },
)
ListQueuesRequestRequestTypeDef = TypedDict(
    "ListQueuesRequestRequestTypeDef",
    {
        "ListBy": NotRequired[QueueListByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Order": NotRequired[OrderType],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "Arn": str,
    },
)
ResourceTagsTypeDef = TypedDict(
    "ResourceTagsTypeDef",
    {
        "Arn": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)
M2tsScte35EsamTypeDef = TypedDict(
    "M2tsScte35EsamTypeDef",
    {
        "Scte35EsamPid": NotRequired[int],
    },
)
MotionImageInsertionFramerateTypeDef = TypedDict(
    "MotionImageInsertionFramerateTypeDef",
    {
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
    },
)
MotionImageInsertionOffsetTypeDef = TypedDict(
    "MotionImageInsertionOffsetTypeDef",
    {
        "ImageX": NotRequired[int],
        "ImageY": NotRequired[int],
    },
)
Mpeg2SettingsTypeDef = TypedDict(
    "Mpeg2SettingsTypeDef",
    {
        "AdaptiveQuantization": NotRequired[Mpeg2AdaptiveQuantizationType],
        "Bitrate": NotRequired[int],
        "CodecLevel": NotRequired[Mpeg2CodecLevelType],
        "CodecProfile": NotRequired[Mpeg2CodecProfileType],
        "DynamicSubGop": NotRequired[Mpeg2DynamicSubGopType],
        "FramerateControl": NotRequired[Mpeg2FramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[Mpeg2FramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopClosedCadence": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[Mpeg2GopSizeUnitsType],
        "HrdBufferFinalFillPercentage": NotRequired[int],
        "HrdBufferInitialFillPercentage": NotRequired[int],
        "HrdBufferSize": NotRequired[int],
        "InterlaceMode": NotRequired[Mpeg2InterlaceModeType],
        "IntraDcPrecision": NotRequired[Mpeg2IntraDcPrecisionType],
        "MaxBitrate": NotRequired[int],
        "MinIInterval": NotRequired[int],
        "NumberBFramesBetweenReferenceFrames": NotRequired[int],
        "ParControl": NotRequired[Mpeg2ParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "QualityTuningLevel": NotRequired[Mpeg2QualityTuningLevelType],
        "RateControlMode": NotRequired[Mpeg2RateControlModeType],
        "ScanTypeConversionMode": NotRequired[Mpeg2ScanTypeConversionModeType],
        "SceneChangeDetect": NotRequired[Mpeg2SceneChangeDetectType],
        "SlowPal": NotRequired[Mpeg2SlowPalType],
        "Softness": NotRequired[int],
        "SpatialAdaptiveQuantization": NotRequired[Mpeg2SpatialAdaptiveQuantizationType],
        "Syntax": NotRequired[Mpeg2SyntaxType],
        "Telecine": NotRequired[Mpeg2TelecineType],
        "TemporalAdaptiveQuantization": NotRequired[Mpeg2TemporalAdaptiveQuantizationType],
    },
)
MsSmoothAdditionalManifestPaginatorTypeDef = TypedDict(
    "MsSmoothAdditionalManifestPaginatorTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[List[str]],
    },
)
MsSmoothAdditionalManifestTypeDef = TypedDict(
    "MsSmoothAdditionalManifestTypeDef",
    {
        "ManifestNameModifier": NotRequired[str],
        "SelectedOutputs": NotRequired[Sequence[str]],
    },
)
MxfXavcProfileSettingsTypeDef = TypedDict(
    "MxfXavcProfileSettingsTypeDef",
    {
        "DurationMode": NotRequired[MxfXavcDurationModeType],
        "MaxAncDataSize": NotRequired[int],
    },
)
NexGuardFileMarkerSettingsTypeDef = TypedDict(
    "NexGuardFileMarkerSettingsTypeDef",
    {
        "License": NotRequired[str],
        "Payload": NotRequired[int],
        "Preset": NotRequired[str],
        "Strength": NotRequired[WatermarkingStrengthType],
    },
)
NoiseReducerFilterSettingsTypeDef = TypedDict(
    "NoiseReducerFilterSettingsTypeDef",
    {
        "Strength": NotRequired[int],
    },
)
NoiseReducerSpatialFilterSettingsTypeDef = TypedDict(
    "NoiseReducerSpatialFilterSettingsTypeDef",
    {
        "PostFilterSharpenStrength": NotRequired[int],
        "Speed": NotRequired[int],
        "Strength": NotRequired[int],
    },
)
NoiseReducerTemporalFilterSettingsTypeDef = TypedDict(
    "NoiseReducerTemporalFilterSettingsTypeDef",
    {
        "AggressiveMode": NotRequired[int],
        "PostTemporalSharpening": NotRequired[NoiseFilterPostTemporalSharpeningType],
        "PostTemporalSharpeningStrength": NotRequired[
            NoiseFilterPostTemporalSharpeningStrengthType
        ],
        "Speed": NotRequired[int],
        "Strength": NotRequired[int],
    },
)
VideoDetailTypeDef = TypedDict(
    "VideoDetailTypeDef",
    {
        "HeightInPx": NotRequired[int],
        "WidthInPx": NotRequired[int],
    },
)
ProresSettingsTypeDef = TypedDict(
    "ProresSettingsTypeDef",
    {
        "ChromaSampling": NotRequired[ProresChromaSamplingType],
        "CodecProfile": NotRequired[ProresCodecProfileType],
        "FramerateControl": NotRequired[ProresFramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[ProresFramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "InterlaceMode": NotRequired[ProresInterlaceModeType],
        "ParControl": NotRequired[ProresParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "ScanTypeConversionMode": NotRequired[ProresScanTypeConversionModeType],
        "SlowPal": NotRequired[ProresSlowPalType],
        "Telecine": NotRequired[ProresTelecineType],
    },
)
ReservationPlanTypeDef = TypedDict(
    "ReservationPlanTypeDef",
    {
        "Commitment": NotRequired[Literal["ONE_YEAR"]],
        "ExpiresAt": NotRequired[datetime],
        "PurchasedAt": NotRequired[datetime],
        "RenewalType": NotRequired[RenewalTypeType],
        "ReservedSlots": NotRequired[int],
        "Status": NotRequired[ReservationPlanStatusType],
    },
)
S3DestinationAccessControlTypeDef = TypedDict(
    "S3DestinationAccessControlTypeDef",
    {
        "CannedAcl": NotRequired[S3ObjectCannedAclType],
    },
)
S3EncryptionSettingsTypeDef = TypedDict(
    "S3EncryptionSettingsTypeDef",
    {
        "EncryptionType": NotRequired[S3ServerSideEncryptionTypeType],
        "KmsEncryptionContext": NotRequired[str],
        "KmsKeyArn": NotRequired[str],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "Arn": str,
        "Tags": Mapping[str, str],
    },
)
TimecodeBurninTypeDef = TypedDict(
    "TimecodeBurninTypeDef",
    {
        "FontSize": NotRequired[int],
        "Position": NotRequired[TimecodeBurninPositionType],
        "Prefix": NotRequired[str],
    },
)
UncompressedSettingsTypeDef = TypedDict(
    "UncompressedSettingsTypeDef",
    {
        "Fourcc": NotRequired[UncompressedFourccType],
        "FramerateControl": NotRequired[UncompressedFramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[UncompressedFramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "InterlaceMode": NotRequired[UncompressedInterlaceModeType],
        "ScanTypeConversionMode": NotRequired[UncompressedScanTypeConversionModeType],
        "SlowPal": NotRequired[UncompressedSlowPalType],
        "Telecine": NotRequired[UncompressedTelecineType],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "Arn": str,
        "TagKeys": NotRequired[Sequence[str]],
    },
)
Vc3SettingsTypeDef = TypedDict(
    "Vc3SettingsTypeDef",
    {
        "FramerateControl": NotRequired[Vc3FramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[Vc3FramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "InterlaceMode": NotRequired[Vc3InterlaceModeType],
        "ScanTypeConversionMode": NotRequired[Vc3ScanTypeConversionModeType],
        "SlowPal": NotRequired[Vc3SlowPalType],
        "Telecine": NotRequired[Vc3TelecineType],
        "Vc3Class": NotRequired[Vc3ClassType],
    },
)
Vp8SettingsTypeDef = TypedDict(
    "Vp8SettingsTypeDef",
    {
        "Bitrate": NotRequired[int],
        "FramerateControl": NotRequired[Vp8FramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[Vp8FramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopSize": NotRequired[float],
        "HrdBufferSize": NotRequired[int],
        "MaxBitrate": NotRequired[int],
        "ParControl": NotRequired[Vp8ParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "QualityTuningLevel": NotRequired[Vp8QualityTuningLevelType],
        "RateControlMode": NotRequired[Literal["VBR"]],
    },
)
Vp9SettingsTypeDef = TypedDict(
    "Vp9SettingsTypeDef",
    {
        "Bitrate": NotRequired[int],
        "FramerateControl": NotRequired[Vp9FramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[Vp9FramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopSize": NotRequired[float],
        "HrdBufferSize": NotRequired[int],
        "MaxBitrate": NotRequired[int],
        "ParControl": NotRequired[Vp9ParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "QualityTuningLevel": NotRequired[Vp9QualityTuningLevelType],
        "RateControlMode": NotRequired[Literal["VBR"]],
    },
)
VideoOverlayInputClippingTypeDef = TypedDict(
    "VideoOverlayInputClippingTypeDef",
    {
        "EndTimecode": NotRequired[str],
        "StartTimecode": NotRequired[str],
    },
)
Xavc4kIntraCbgProfileSettingsTypeDef = TypedDict(
    "Xavc4kIntraCbgProfileSettingsTypeDef",
    {
        "XavcClass": NotRequired[Xavc4kIntraCbgProfileClassType],
    },
)
Xavc4kIntraVbrProfileSettingsTypeDef = TypedDict(
    "Xavc4kIntraVbrProfileSettingsTypeDef",
    {
        "XavcClass": NotRequired[Xavc4kIntraVbrProfileClassType],
    },
)
Xavc4kProfileSettingsTypeDef = TypedDict(
    "Xavc4kProfileSettingsTypeDef",
    {
        "BitrateClass": NotRequired[Xavc4kProfileBitrateClassType],
        "CodecProfile": NotRequired[Xavc4kProfileCodecProfileType],
        "FlickerAdaptiveQuantization": NotRequired[XavcFlickerAdaptiveQuantizationType],
        "GopBReference": NotRequired[XavcGopBReferenceType],
        "GopClosedCadence": NotRequired[int],
        "HrdBufferSize": NotRequired[int],
        "QualityTuningLevel": NotRequired[Xavc4kProfileQualityTuningLevelType],
        "Slices": NotRequired[int],
    },
)
XavcHdIntraCbgProfileSettingsTypeDef = TypedDict(
    "XavcHdIntraCbgProfileSettingsTypeDef",
    {
        "XavcClass": NotRequired[XavcHdIntraCbgProfileClassType],
    },
)
XavcHdProfileSettingsTypeDef = TypedDict(
    "XavcHdProfileSettingsTypeDef",
    {
        "BitrateClass": NotRequired[XavcHdProfileBitrateClassType],
        "FlickerAdaptiveQuantization": NotRequired[XavcFlickerAdaptiveQuantizationType],
        "GopBReference": NotRequired[XavcGopBReferenceType],
        "GopClosedCadence": NotRequired[int],
        "HrdBufferSize": NotRequired[int],
        "InterlaceMode": NotRequired[XavcInterlaceModeType],
        "QualityTuningLevel": NotRequired[XavcHdProfileQualityTuningLevelType],
        "Slices": NotRequired[int],
        "Telecine": NotRequired[XavcHdProfileTelecineType],
    },
)
AudioCodecSettingsTypeDef = TypedDict(
    "AudioCodecSettingsTypeDef",
    {
        "AacSettings": NotRequired[AacSettingsTypeDef],
        "Ac3Settings": NotRequired[Ac3SettingsTypeDef],
        "AiffSettings": NotRequired[AiffSettingsTypeDef],
        "Codec": NotRequired[AudioCodecType],
        "Eac3AtmosSettings": NotRequired[Eac3AtmosSettingsTypeDef],
        "Eac3Settings": NotRequired[Eac3SettingsTypeDef],
        "FlacSettings": NotRequired[FlacSettingsTypeDef],
        "Mp2Settings": NotRequired[Mp2SettingsTypeDef],
        "Mp3Settings": NotRequired[Mp3SettingsTypeDef],
        "OpusSettings": NotRequired[OpusSettingsTypeDef],
        "VorbisSettings": NotRequired[VorbisSettingsTypeDef],
        "WavSettings": NotRequired[WavSettingsTypeDef],
    },
)
AutomatedAbrRulePaginatorTypeDef = TypedDict(
    "AutomatedAbrRulePaginatorTypeDef",
    {
        "AllowedRenditions": NotRequired[List[AllowedRenditionSizeTypeDef]],
        "ForceIncludeRenditions": NotRequired[List[ForceIncludeRenditionSizeTypeDef]],
        "MinBottomRenditionSize": NotRequired[MinBottomRenditionSizeTypeDef],
        "MinTopRenditionSize": NotRequired[MinTopRenditionSizeTypeDef],
        "Type": NotRequired[RuleTypeType],
    },
)
AutomatedAbrRuleTypeDef = TypedDict(
    "AutomatedAbrRuleTypeDef",
    {
        "AllowedRenditions": NotRequired[Sequence[AllowedRenditionSizeTypeDef]],
        "ForceIncludeRenditions": NotRequired[Sequence[ForceIncludeRenditionSizeTypeDef]],
        "MinBottomRenditionSize": NotRequired[MinBottomRenditionSizeTypeDef],
        "MinTopRenditionSize": NotRequired[MinTopRenditionSizeTypeDef],
        "Type": NotRequired[RuleTypeType],
    },
)
Av1SettingsTypeDef = TypedDict(
    "Av1SettingsTypeDef",
    {
        "AdaptiveQuantization": NotRequired[Av1AdaptiveQuantizationType],
        "BitDepth": NotRequired[Av1BitDepthType],
        "FilmGrainSynthesis": NotRequired[Av1FilmGrainSynthesisType],
        "FramerateControl": NotRequired[Av1FramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[Av1FramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopSize": NotRequired[float],
        "MaxBitrate": NotRequired[int],
        "NumberBFramesBetweenReferenceFrames": NotRequired[int],
        "QvbrSettings": NotRequired[Av1QvbrSettingsTypeDef],
        "RateControlMode": NotRequired[Literal["QVBR"]],
        "Slices": NotRequired[int],
        "SpatialAdaptiveQuantization": NotRequired[Av1SpatialAdaptiveQuantizationType],
    },
)
AvcIntraSettingsTypeDef = TypedDict(
    "AvcIntraSettingsTypeDef",
    {
        "AvcIntraClass": NotRequired[AvcIntraClassType],
        "AvcIntraUhdSettings": NotRequired[AvcIntraUhdSettingsTypeDef],
        "FramerateControl": NotRequired[AvcIntraFramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[AvcIntraFramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "InterlaceMode": NotRequired[AvcIntraInterlaceModeType],
        "ScanTypeConversionMode": NotRequired[AvcIntraScanTypeConversionModeType],
        "SlowPal": NotRequired[AvcIntraSlowPalType],
        "Telecine": NotRequired[AvcIntraTelecineType],
    },
)
CaptionDestinationSettingsPaginatorTypeDef = TypedDict(
    "CaptionDestinationSettingsPaginatorTypeDef",
    {
        "BurninDestinationSettings": NotRequired[BurninDestinationSettingsTypeDef],
        "DestinationType": NotRequired[CaptionDestinationTypeType],
        "DvbSubDestinationSettings": NotRequired[DvbSubDestinationSettingsTypeDef],
        "EmbeddedDestinationSettings": NotRequired[EmbeddedDestinationSettingsTypeDef],
        "ImscDestinationSettings": NotRequired[ImscDestinationSettingsTypeDef],
        "SccDestinationSettings": NotRequired[SccDestinationSettingsTypeDef],
        "SrtDestinationSettings": NotRequired[SrtDestinationSettingsTypeDef],
        "TeletextDestinationSettings": NotRequired[TeletextDestinationSettingsPaginatorTypeDef],
        "TtmlDestinationSettings": NotRequired[TtmlDestinationSettingsTypeDef],
        "WebvttDestinationSettings": NotRequired[WebvttDestinationSettingsTypeDef],
    },
)
CaptionDestinationSettingsTypeDef = TypedDict(
    "CaptionDestinationSettingsTypeDef",
    {
        "BurninDestinationSettings": NotRequired[BurninDestinationSettingsTypeDef],
        "DestinationType": NotRequired[CaptionDestinationTypeType],
        "DvbSubDestinationSettings": NotRequired[DvbSubDestinationSettingsTypeDef],
        "EmbeddedDestinationSettings": NotRequired[EmbeddedDestinationSettingsTypeDef],
        "ImscDestinationSettings": NotRequired[ImscDestinationSettingsTypeDef],
        "SccDestinationSettings": NotRequired[SccDestinationSettingsTypeDef],
        "SrtDestinationSettings": NotRequired[SrtDestinationSettingsTypeDef],
        "TeletextDestinationSettings": NotRequired[TeletextDestinationSettingsTypeDef],
        "TtmlDestinationSettings": NotRequired[TtmlDestinationSettingsTypeDef],
        "WebvttDestinationSettings": NotRequired[WebvttDestinationSettingsTypeDef],
    },
)
FileSourceSettingsTypeDef = TypedDict(
    "FileSourceSettingsTypeDef",
    {
        "Convert608To708": NotRequired[FileSourceConvert608To708Type],
        "ConvertPaintToPop": NotRequired[CaptionSourceConvertPaintOnToPopOnType],
        "Framerate": NotRequired[CaptionSourceFramerateTypeDef],
        "SourceFile": NotRequired[str],
        "TimeDelta": NotRequired[int],
        "TimeDeltaUnits": NotRequired[FileSourceTimeDeltaUnitsType],
    },
)
ChannelMappingPaginatorTypeDef = TypedDict(
    "ChannelMappingPaginatorTypeDef",
    {
        "OutputChannels": NotRequired[List[OutputChannelMappingPaginatorTypeDef]],
    },
)
ChannelMappingTypeDef = TypedDict(
    "ChannelMappingTypeDef",
    {
        "OutputChannels": NotRequired[Sequence[OutputChannelMappingTypeDef]],
    },
)
CmafEncryptionSettingsPaginatorTypeDef = TypedDict(
    "CmafEncryptionSettingsPaginatorTypeDef",
    {
        "ConstantInitializationVector": NotRequired[str],
        "EncryptionMethod": NotRequired[CmafEncryptionTypeType],
        "InitializationVectorInManifest": NotRequired[CmafInitializationVectorInManifestType],
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderCmafPaginatorTypeDef],
        "StaticKeyProvider": NotRequired[StaticKeyProviderTypeDef],
        "Type": NotRequired[CmafKeyProviderTypeType],
    },
)
CmafEncryptionSettingsTypeDef = TypedDict(
    "CmafEncryptionSettingsTypeDef",
    {
        "ConstantInitializationVector": NotRequired[str],
        "EncryptionMethod": NotRequired[CmafEncryptionTypeType],
        "InitializationVectorInManifest": NotRequired[CmafInitializationVectorInManifestType],
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderCmafTypeDef],
        "StaticKeyProvider": NotRequired[StaticKeyProviderTypeDef],
        "Type": NotRequired[CmafKeyProviderTypeType],
    },
)
ColorCorrectorTypeDef = TypedDict(
    "ColorCorrectorTypeDef",
    {
        "Brightness": NotRequired[int],
        "ClipLimits": NotRequired[ClipLimitsTypeDef],
        "ColorSpaceConversion": NotRequired[ColorSpaceConversionType],
        "Contrast": NotRequired[int],
        "Hdr10Metadata": NotRequired[Hdr10MetadataTypeDef],
        "HdrToSdrToneMapper": NotRequired[HDRToSDRToneMapperType],
        "Hue": NotRequired[int],
        "MaxLuminance": NotRequired[int],
        "SampleRangeConversion": NotRequired[SampleRangeConversionType],
        "Saturation": NotRequired[int],
        "SdrReferenceWhiteLevel": NotRequired[int],
    },
)
VideoSelectorTypeDef = TypedDict(
    "VideoSelectorTypeDef",
    {
        "AlphaBehavior": NotRequired[AlphaBehaviorType],
        "ColorSpace": NotRequired[ColorSpaceType],
        "ColorSpaceUsage": NotRequired[ColorSpaceUsageType],
        "EmbeddedTimecodeOverride": NotRequired[EmbeddedTimecodeOverrideType],
        "Hdr10Metadata": NotRequired[Hdr10MetadataTypeDef],
        "MaxLuminance": NotRequired[int],
        "PadVideo": NotRequired[PadVideoType],
        "Pid": NotRequired[int],
        "ProgramNumber": NotRequired[int],
        "Rotate": NotRequired[InputRotateType],
        "SampleRange": NotRequired[InputSampleRangeType],
    },
)
CreateQueueRequestRequestTypeDef = TypedDict(
    "CreateQueueRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "PricingPlan": NotRequired[PricingPlanType],
        "ReservationPlanSettings": NotRequired[ReservationPlanSettingsTypeDef],
        "Status": NotRequired[QueueStatusType],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
UpdateQueueRequestRequestTypeDef = TypedDict(
    "UpdateQueueRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "ReservationPlanSettings": NotRequired[ReservationPlanSettingsTypeDef],
        "Status": NotRequired[QueueStatusType],
    },
)
DashIsoEncryptionSettingsPaginatorTypeDef = TypedDict(
    "DashIsoEncryptionSettingsPaginatorTypeDef",
    {
        "PlaybackDeviceCompatibility": NotRequired[DashIsoPlaybackDeviceCompatibilityType],
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderPaginatorTypeDef],
    },
)
HlsEncryptionSettingsPaginatorTypeDef = TypedDict(
    "HlsEncryptionSettingsPaginatorTypeDef",
    {
        "ConstantInitializationVector": NotRequired[str],
        "EncryptionMethod": NotRequired[HlsEncryptionTypeType],
        "InitializationVectorInManifest": NotRequired[HlsInitializationVectorInManifestType],
        "OfflineEncrypted": NotRequired[HlsOfflineEncryptedType],
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderPaginatorTypeDef],
        "StaticKeyProvider": NotRequired[StaticKeyProviderTypeDef],
        "Type": NotRequired[HlsKeyProviderTypeType],
    },
)
MsSmoothEncryptionSettingsPaginatorTypeDef = TypedDict(
    "MsSmoothEncryptionSettingsPaginatorTypeDef",
    {
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderPaginatorTypeDef],
    },
)
DashIsoEncryptionSettingsTypeDef = TypedDict(
    "DashIsoEncryptionSettingsTypeDef",
    {
        "PlaybackDeviceCompatibility": NotRequired[DashIsoPlaybackDeviceCompatibilityType],
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderTypeDef],
    },
)
HlsEncryptionSettingsTypeDef = TypedDict(
    "HlsEncryptionSettingsTypeDef",
    {
        "ConstantInitializationVector": NotRequired[str],
        "EncryptionMethod": NotRequired[HlsEncryptionTypeType],
        "InitializationVectorInManifest": NotRequired[HlsInitializationVectorInManifestType],
        "OfflineEncrypted": NotRequired[HlsOfflineEncryptedType],
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderTypeDef],
        "StaticKeyProvider": NotRequired[StaticKeyProviderTypeDef],
        "Type": NotRequired[HlsKeyProviderTypeType],
    },
)
MsSmoothEncryptionSettingsTypeDef = TypedDict(
    "MsSmoothEncryptionSettingsTypeDef",
    {
        "SpekeKeyProvider": NotRequired[SpekeKeyProviderTypeDef],
    },
)
DescribeEndpointsRequestDescribeEndpointsPaginateTypeDef = TypedDict(
    "DescribeEndpointsRequestDescribeEndpointsPaginateTypeDef",
    {
        "Mode": NotRequired[DescribeEndpointsModeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListJobTemplatesRequestListJobTemplatesPaginateTypeDef = TypedDict(
    "ListJobTemplatesRequestListJobTemplatesPaginateTypeDef",
    {
        "Category": NotRequired[str],
        "ListBy": NotRequired[JobTemplateListByType],
        "Order": NotRequired[OrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListJobsRequestListJobsPaginateTypeDef = TypedDict(
    "ListJobsRequestListJobsPaginateTypeDef",
    {
        "Order": NotRequired[OrderType],
        "Queue": NotRequired[str],
        "Status": NotRequired[JobStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPresetsRequestListPresetsPaginateTypeDef = TypedDict(
    "ListPresetsRequestListPresetsPaginateTypeDef",
    {
        "Category": NotRequired[str],
        "ListBy": NotRequired[PresetListByType],
        "Order": NotRequired[OrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListQueuesRequestListQueuesPaginateTypeDef = TypedDict(
    "ListQueuesRequestListQueuesPaginateTypeDef",
    {
        "ListBy": NotRequired[QueueListByType],
        "Order": NotRequired[OrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeEndpointsResponseTypeDef = TypedDict(
    "DescribeEndpointsResponseTypeDef",
    {
        "Endpoints": List[EndpointTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DolbyVisionTypeDef = TypedDict(
    "DolbyVisionTypeDef",
    {
        "L6Metadata": NotRequired[DolbyVisionLevel6MetadataTypeDef],
        "L6Mode": NotRequired[DolbyVisionLevel6ModeType],
        "Mapping": NotRequired[DolbyVisionMappingType],
        "Profile": NotRequired[DolbyVisionProfileType],
    },
)
EsamSettingsTypeDef = TypedDict(
    "EsamSettingsTypeDef",
    {
        "ManifestConfirmConditionNotification": NotRequired[
            EsamManifestConfirmConditionNotificationTypeDef
        ],
        "ResponseSignalPreroll": NotRequired[int],
        "SignalProcessingNotification": NotRequired[EsamSignalProcessingNotificationTypeDef],
    },
)
GetPolicyResponseTypeDef = TypedDict(
    "GetPolicyResponseTypeDef",
    {
        "Policy": PolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutPolicyRequestRequestTypeDef = TypedDict(
    "PutPolicyRequestRequestTypeDef",
    {
        "Policy": PolicyTypeDef,
    },
)
PutPolicyResponseTypeDef = TypedDict(
    "PutPolicyResponseTypeDef",
    {
        "Policy": PolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
H264SettingsTypeDef = TypedDict(
    "H264SettingsTypeDef",
    {
        "AdaptiveQuantization": NotRequired[H264AdaptiveQuantizationType],
        "BandwidthReductionFilter": NotRequired[BandwidthReductionFilterTypeDef],
        "Bitrate": NotRequired[int],
        "CodecLevel": NotRequired[H264CodecLevelType],
        "CodecProfile": NotRequired[H264CodecProfileType],
        "DynamicSubGop": NotRequired[H264DynamicSubGopType],
        "EndOfStreamMarkers": NotRequired[H264EndOfStreamMarkersType],
        "EntropyEncoding": NotRequired[H264EntropyEncodingType],
        "FieldEncoding": NotRequired[H264FieldEncodingType],
        "FlickerAdaptiveQuantization": NotRequired[H264FlickerAdaptiveQuantizationType],
        "FramerateControl": NotRequired[H264FramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[H264FramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopBReference": NotRequired[H264GopBReferenceType],
        "GopClosedCadence": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[H264GopSizeUnitsType],
        "HrdBufferFinalFillPercentage": NotRequired[int],
        "HrdBufferInitialFillPercentage": NotRequired[int],
        "HrdBufferSize": NotRequired[int],
        "InterlaceMode": NotRequired[H264InterlaceModeType],
        "MaxBitrate": NotRequired[int],
        "MinIInterval": NotRequired[int],
        "NumberBFramesBetweenReferenceFrames": NotRequired[int],
        "NumberReferenceFrames": NotRequired[int],
        "ParControl": NotRequired[H264ParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "QualityTuningLevel": NotRequired[H264QualityTuningLevelType],
        "QvbrSettings": NotRequired[H264QvbrSettingsTypeDef],
        "RateControlMode": NotRequired[H264RateControlModeType],
        "RepeatPps": NotRequired[H264RepeatPpsType],
        "ScanTypeConversionMode": NotRequired[H264ScanTypeConversionModeType],
        "SceneChangeDetect": NotRequired[H264SceneChangeDetectType],
        "Slices": NotRequired[int],
        "SlowPal": NotRequired[H264SlowPalType],
        "Softness": NotRequired[int],
        "SpatialAdaptiveQuantization": NotRequired[H264SpatialAdaptiveQuantizationType],
        "Syntax": NotRequired[H264SyntaxType],
        "Telecine": NotRequired[H264TelecineType],
        "TemporalAdaptiveQuantization": NotRequired[H264TemporalAdaptiveQuantizationType],
        "UnregisteredSeiTimecode": NotRequired[H264UnregisteredSeiTimecodeType],
    },
)
H265SettingsTypeDef = TypedDict(
    "H265SettingsTypeDef",
    {
        "AdaptiveQuantization": NotRequired[H265AdaptiveQuantizationType],
        "AlternateTransferFunctionSei": NotRequired[H265AlternateTransferFunctionSeiType],
        "BandwidthReductionFilter": NotRequired[BandwidthReductionFilterTypeDef],
        "Bitrate": NotRequired[int],
        "CodecLevel": NotRequired[H265CodecLevelType],
        "CodecProfile": NotRequired[H265CodecProfileType],
        "DynamicSubGop": NotRequired[H265DynamicSubGopType],
        "EndOfStreamMarkers": NotRequired[H265EndOfStreamMarkersType],
        "FlickerAdaptiveQuantization": NotRequired[H265FlickerAdaptiveQuantizationType],
        "FramerateControl": NotRequired[H265FramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[H265FramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopBReference": NotRequired[H265GopBReferenceType],
        "GopClosedCadence": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[H265GopSizeUnitsType],
        "HrdBufferFinalFillPercentage": NotRequired[int],
        "HrdBufferInitialFillPercentage": NotRequired[int],
        "HrdBufferSize": NotRequired[int],
        "InterlaceMode": NotRequired[H265InterlaceModeType],
        "MaxBitrate": NotRequired[int],
        "MinIInterval": NotRequired[int],
        "NumberBFramesBetweenReferenceFrames": NotRequired[int],
        "NumberReferenceFrames": NotRequired[int],
        "ParControl": NotRequired[H265ParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "QualityTuningLevel": NotRequired[H265QualityTuningLevelType],
        "QvbrSettings": NotRequired[H265QvbrSettingsTypeDef],
        "RateControlMode": NotRequired[H265RateControlModeType],
        "SampleAdaptiveOffsetFilterMode": NotRequired[H265SampleAdaptiveOffsetFilterModeType],
        "ScanTypeConversionMode": NotRequired[H265ScanTypeConversionModeType],
        "SceneChangeDetect": NotRequired[H265SceneChangeDetectType],
        "Slices": NotRequired[int],
        "SlowPal": NotRequired[H265SlowPalType],
        "SpatialAdaptiveQuantization": NotRequired[H265SpatialAdaptiveQuantizationType],
        "Telecine": NotRequired[H265TelecineType],
        "TemporalAdaptiveQuantization": NotRequired[H265TemporalAdaptiveQuantizationType],
        "TemporalIds": NotRequired[H265TemporalIdsType],
        "Tiles": NotRequired[H265TilesType],
        "UnregisteredSeiTimecode": NotRequired[H265UnregisteredSeiTimecodeType],
        "WriteMp4PackagingType": NotRequired[H265WriteMp4PackagingTypeType],
    },
)
OutputSettingsTypeDef = TypedDict(
    "OutputSettingsTypeDef",
    {
        "HlsSettings": NotRequired[HlsSettingsTypeDef],
    },
)
TimedMetadataInsertionPaginatorTypeDef = TypedDict(
    "TimedMetadataInsertionPaginatorTypeDef",
    {
        "Id3Insertions": NotRequired[List[Id3InsertionTypeDef]],
    },
)
TimedMetadataInsertionTypeDef = TypedDict(
    "TimedMetadataInsertionTypeDef",
    {
        "Id3Insertions": NotRequired[Sequence[Id3InsertionTypeDef]],
    },
)
ImageInserterPaginatorTypeDef = TypedDict(
    "ImageInserterPaginatorTypeDef",
    {
        "InsertableImages": NotRequired[List[InsertableImageTypeDef]],
        "SdrReferenceWhiteLevel": NotRequired[int],
    },
)
ImageInserterTypeDef = TypedDict(
    "ImageInserterTypeDef",
    {
        "InsertableImages": NotRequired[Sequence[InsertableImageTypeDef]],
        "SdrReferenceWhiteLevel": NotRequired[int],
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "ResourceTags": ResourceTagsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
M2tsSettingsPaginatorTypeDef = TypedDict(
    "M2tsSettingsPaginatorTypeDef",
    {
        "AudioBufferModel": NotRequired[M2tsAudioBufferModelType],
        "AudioDuration": NotRequired[M2tsAudioDurationType],
        "AudioFramesPerPes": NotRequired[int],
        "AudioPids": NotRequired[List[int]],
        "Bitrate": NotRequired[int],
        "BufferModel": NotRequired[M2tsBufferModelType],
        "DataPTSControl": NotRequired[M2tsDataPtsControlType],
        "DvbNitSettings": NotRequired[DvbNitSettingsTypeDef],
        "DvbSdtSettings": NotRequired[DvbSdtSettingsTypeDef],
        "DvbSubPids": NotRequired[List[int]],
        "DvbTdtSettings": NotRequired[DvbTdtSettingsTypeDef],
        "DvbTeletextPid": NotRequired[int],
        "EbpAudioInterval": NotRequired[M2tsEbpAudioIntervalType],
        "EbpPlacement": NotRequired[M2tsEbpPlacementType],
        "EsRateInPes": NotRequired[M2tsEsRateInPesType],
        "ForceTsVideoEbpOrder": NotRequired[M2tsForceTsVideoEbpOrderType],
        "FragmentTime": NotRequired[float],
        "KlvMetadata": NotRequired[M2tsKlvMetadataType],
        "MaxPcrInterval": NotRequired[int],
        "MinEbpInterval": NotRequired[int],
        "NielsenId3": NotRequired[M2tsNielsenId3Type],
        "NullPacketBitrate": NotRequired[float],
        "PatInterval": NotRequired[int],
        "PcrControl": NotRequired[M2tsPcrControlType],
        "PcrPid": NotRequired[int],
        "PmtInterval": NotRequired[int],
        "PmtPid": NotRequired[int],
        "PreventBufferUnderflow": NotRequired[M2tsPreventBufferUnderflowType],
        "PrivateMetadataPid": NotRequired[int],
        "ProgramNumber": NotRequired[int],
        "PtsOffset": NotRequired[int],
        "PtsOffsetMode": NotRequired[TsPtsOffsetType],
        "RateMode": NotRequired[M2tsRateModeType],
        "Scte35Esam": NotRequired[M2tsScte35EsamTypeDef],
        "Scte35Pid": NotRequired[int],
        "Scte35Source": NotRequired[M2tsScte35SourceType],
        "SegmentationMarkers": NotRequired[M2tsSegmentationMarkersType],
        "SegmentationStyle": NotRequired[M2tsSegmentationStyleType],
        "SegmentationTime": NotRequired[float],
        "TimedMetadataPid": NotRequired[int],
        "TransportStreamId": NotRequired[int],
        "VideoPid": NotRequired[int],
    },
)
M2tsSettingsTypeDef = TypedDict(
    "M2tsSettingsTypeDef",
    {
        "AudioBufferModel": NotRequired[M2tsAudioBufferModelType],
        "AudioDuration": NotRequired[M2tsAudioDurationType],
        "AudioFramesPerPes": NotRequired[int],
        "AudioPids": NotRequired[Sequence[int]],
        "Bitrate": NotRequired[int],
        "BufferModel": NotRequired[M2tsBufferModelType],
        "DataPTSControl": NotRequired[M2tsDataPtsControlType],
        "DvbNitSettings": NotRequired[DvbNitSettingsTypeDef],
        "DvbSdtSettings": NotRequired[DvbSdtSettingsTypeDef],
        "DvbSubPids": NotRequired[Sequence[int]],
        "DvbTdtSettings": NotRequired[DvbTdtSettingsTypeDef],
        "DvbTeletextPid": NotRequired[int],
        "EbpAudioInterval": NotRequired[M2tsEbpAudioIntervalType],
        "EbpPlacement": NotRequired[M2tsEbpPlacementType],
        "EsRateInPes": NotRequired[M2tsEsRateInPesType],
        "ForceTsVideoEbpOrder": NotRequired[M2tsForceTsVideoEbpOrderType],
        "FragmentTime": NotRequired[float],
        "KlvMetadata": NotRequired[M2tsKlvMetadataType],
        "MaxPcrInterval": NotRequired[int],
        "MinEbpInterval": NotRequired[int],
        "NielsenId3": NotRequired[M2tsNielsenId3Type],
        "NullPacketBitrate": NotRequired[float],
        "PatInterval": NotRequired[int],
        "PcrControl": NotRequired[M2tsPcrControlType],
        "PcrPid": NotRequired[int],
        "PmtInterval": NotRequired[int],
        "PmtPid": NotRequired[int],
        "PreventBufferUnderflow": NotRequired[M2tsPreventBufferUnderflowType],
        "PrivateMetadataPid": NotRequired[int],
        "ProgramNumber": NotRequired[int],
        "PtsOffset": NotRequired[int],
        "PtsOffsetMode": NotRequired[TsPtsOffsetType],
        "RateMode": NotRequired[M2tsRateModeType],
        "Scte35Esam": NotRequired[M2tsScte35EsamTypeDef],
        "Scte35Pid": NotRequired[int],
        "Scte35Source": NotRequired[M2tsScte35SourceType],
        "SegmentationMarkers": NotRequired[M2tsSegmentationMarkersType],
        "SegmentationStyle": NotRequired[M2tsSegmentationStyleType],
        "SegmentationTime": NotRequired[float],
        "TimedMetadataPid": NotRequired[int],
        "TransportStreamId": NotRequired[int],
        "VideoPid": NotRequired[int],
    },
)
MotionImageInserterTypeDef = TypedDict(
    "MotionImageInserterTypeDef",
    {
        "Framerate": NotRequired[MotionImageInsertionFramerateTypeDef],
        "Input": NotRequired[str],
        "InsertionMode": NotRequired[MotionImageInsertionModeType],
        "Offset": NotRequired[MotionImageInsertionOffsetTypeDef],
        "Playback": NotRequired[MotionImagePlaybackType],
        "StartTime": NotRequired[str],
    },
)
MxfSettingsTypeDef = TypedDict(
    "MxfSettingsTypeDef",
    {
        "AfdSignaling": NotRequired[MxfAfdSignalingType],
        "Profile": NotRequired[MxfProfileType],
        "XavcProfileSettings": NotRequired[MxfXavcProfileSettingsTypeDef],
    },
)
PartnerWatermarkingTypeDef = TypedDict(
    "PartnerWatermarkingTypeDef",
    {
        "NexguardFileMarkerSettings": NotRequired[NexGuardFileMarkerSettingsTypeDef],
    },
)
NoiseReducerTypeDef = TypedDict(
    "NoiseReducerTypeDef",
    {
        "Filter": NotRequired[NoiseReducerFilterType],
        "FilterSettings": NotRequired[NoiseReducerFilterSettingsTypeDef],
        "SpatialFilterSettings": NotRequired[NoiseReducerSpatialFilterSettingsTypeDef],
        "TemporalFilterSettings": NotRequired[NoiseReducerTemporalFilterSettingsTypeDef],
    },
)
OutputDetailTypeDef = TypedDict(
    "OutputDetailTypeDef",
    {
        "DurationInMs": NotRequired[int],
        "VideoDetails": NotRequired[VideoDetailTypeDef],
    },
)
QueueTypeDef = TypedDict(
    "QueueTypeDef",
    {
        "Name": str,
        "Arn": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "Description": NotRequired[str],
        "LastUpdated": NotRequired[datetime],
        "PricingPlan": NotRequired[PricingPlanType],
        "ProgressingJobsCount": NotRequired[int],
        "ReservationPlan": NotRequired[ReservationPlanTypeDef],
        "Status": NotRequired[QueueStatusType],
        "SubmittedJobsCount": NotRequired[int],
        "Type": NotRequired[TypeType],
    },
)
S3DestinationSettingsTypeDef = TypedDict(
    "S3DestinationSettingsTypeDef",
    {
        "AccessControl": NotRequired[S3DestinationAccessControlTypeDef],
        "Encryption": NotRequired[S3EncryptionSettingsTypeDef],
        "StorageClass": NotRequired[S3StorageClassType],
    },
)
VideoOverlayInputPaginatorTypeDef = TypedDict(
    "VideoOverlayInputPaginatorTypeDef",
    {
        "FileInput": NotRequired[str],
        "InputClippings": NotRequired[List[VideoOverlayInputClippingTypeDef]],
        "TimecodeSource": NotRequired[InputTimecodeSourceType],
        "TimecodeStart": NotRequired[str],
    },
)
VideoOverlayInputTypeDef = TypedDict(
    "VideoOverlayInputTypeDef",
    {
        "FileInput": NotRequired[str],
        "InputClippings": NotRequired[Sequence[VideoOverlayInputClippingTypeDef]],
        "TimecodeSource": NotRequired[InputTimecodeSourceType],
        "TimecodeStart": NotRequired[str],
    },
)
XavcSettingsTypeDef = TypedDict(
    "XavcSettingsTypeDef",
    {
        "AdaptiveQuantization": NotRequired[XavcAdaptiveQuantizationType],
        "EntropyEncoding": NotRequired[XavcEntropyEncodingType],
        "FramerateControl": NotRequired[XavcFramerateControlType],
        "FramerateConversionAlgorithm": NotRequired[XavcFramerateConversionAlgorithmType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "Profile": NotRequired[XavcProfileType],
        "SlowPal": NotRequired[XavcSlowPalType],
        "Softness": NotRequired[int],
        "SpatialAdaptiveQuantization": NotRequired[XavcSpatialAdaptiveQuantizationType],
        "TemporalAdaptiveQuantization": NotRequired[XavcTemporalAdaptiveQuantizationType],
        "Xavc4kIntraCbgProfileSettings": NotRequired[Xavc4kIntraCbgProfileSettingsTypeDef],
        "Xavc4kIntraVbrProfileSettings": NotRequired[Xavc4kIntraVbrProfileSettingsTypeDef],
        "Xavc4kProfileSettings": NotRequired[Xavc4kProfileSettingsTypeDef],
        "XavcHdIntraCbgProfileSettings": NotRequired[XavcHdIntraCbgProfileSettingsTypeDef],
        "XavcHdProfileSettings": NotRequired[XavcHdProfileSettingsTypeDef],
    },
)
AutomatedAbrSettingsPaginatorTypeDef = TypedDict(
    "AutomatedAbrSettingsPaginatorTypeDef",
    {
        "MaxAbrBitrate": NotRequired[int],
        "MaxRenditions": NotRequired[int],
        "MinAbrBitrate": NotRequired[int],
        "Rules": NotRequired[List[AutomatedAbrRulePaginatorTypeDef]],
    },
)
AutomatedAbrSettingsTypeDef = TypedDict(
    "AutomatedAbrSettingsTypeDef",
    {
        "MaxAbrBitrate": NotRequired[int],
        "MaxRenditions": NotRequired[int],
        "MinAbrBitrate": NotRequired[int],
        "Rules": NotRequired[Sequence[AutomatedAbrRuleTypeDef]],
    },
)
CaptionDescriptionPaginatorTypeDef = TypedDict(
    "CaptionDescriptionPaginatorTypeDef",
    {
        "CaptionSelectorName": NotRequired[str],
        "CustomLanguageCode": NotRequired[str],
        "DestinationSettings": NotRequired[CaptionDestinationSettingsPaginatorTypeDef],
        "LanguageCode": NotRequired[LanguageCodeType],
        "LanguageDescription": NotRequired[str],
    },
)
CaptionDescriptionPresetPaginatorTypeDef = TypedDict(
    "CaptionDescriptionPresetPaginatorTypeDef",
    {
        "CustomLanguageCode": NotRequired[str],
        "DestinationSettings": NotRequired[CaptionDestinationSettingsPaginatorTypeDef],
        "LanguageCode": NotRequired[LanguageCodeType],
        "LanguageDescription": NotRequired[str],
    },
)
CaptionDescriptionPresetTypeDef = TypedDict(
    "CaptionDescriptionPresetTypeDef",
    {
        "CustomLanguageCode": NotRequired[str],
        "DestinationSettings": NotRequired[CaptionDestinationSettingsTypeDef],
        "LanguageCode": NotRequired[LanguageCodeType],
        "LanguageDescription": NotRequired[str],
    },
)
CaptionDescriptionTypeDef = TypedDict(
    "CaptionDescriptionTypeDef",
    {
        "CaptionSelectorName": NotRequired[str],
        "CustomLanguageCode": NotRequired[str],
        "DestinationSettings": NotRequired[CaptionDestinationSettingsTypeDef],
        "LanguageCode": NotRequired[LanguageCodeType],
        "LanguageDescription": NotRequired[str],
    },
)
CaptionSourceSettingsTypeDef = TypedDict(
    "CaptionSourceSettingsTypeDef",
    {
        "AncillarySourceSettings": NotRequired[AncillarySourceSettingsTypeDef],
        "DvbSubSourceSettings": NotRequired[DvbSubSourceSettingsTypeDef],
        "EmbeddedSourceSettings": NotRequired[EmbeddedSourceSettingsTypeDef],
        "FileSourceSettings": NotRequired[FileSourceSettingsTypeDef],
        "SourceType": NotRequired[CaptionSourceTypeType],
        "TeletextSourceSettings": NotRequired[TeletextSourceSettingsTypeDef],
        "TrackSourceSettings": NotRequired[TrackSourceSettingsTypeDef],
        "WebvttHlsSourceSettings": NotRequired[WebvttHlsSourceSettingsTypeDef],
    },
)
RemixSettingsPaginatorTypeDef = TypedDict(
    "RemixSettingsPaginatorTypeDef",
    {
        "AudioDescriptionAudioChannel": NotRequired[int],
        "AudioDescriptionDataChannel": NotRequired[int],
        "ChannelMapping": NotRequired[ChannelMappingPaginatorTypeDef],
        "ChannelsIn": NotRequired[int],
        "ChannelsOut": NotRequired[int],
    },
)
RemixSettingsTypeDef = TypedDict(
    "RemixSettingsTypeDef",
    {
        "AudioDescriptionAudioChannel": NotRequired[int],
        "AudioDescriptionDataChannel": NotRequired[int],
        "ChannelMapping": NotRequired[ChannelMappingTypeDef],
        "ChannelsIn": NotRequired[int],
        "ChannelsOut": NotRequired[int],
    },
)
ContainerSettingsPaginatorTypeDef = TypedDict(
    "ContainerSettingsPaginatorTypeDef",
    {
        "CmfcSettings": NotRequired[CmfcSettingsTypeDef],
        "Container": NotRequired[ContainerTypeType],
        "F4vSettings": NotRequired[F4vSettingsTypeDef],
        "M2tsSettings": NotRequired[M2tsSettingsPaginatorTypeDef],
        "M3u8Settings": NotRequired[M3u8SettingsPaginatorTypeDef],
        "MovSettings": NotRequired[MovSettingsTypeDef],
        "Mp4Settings": NotRequired[Mp4SettingsTypeDef],
        "MpdSettings": NotRequired[MpdSettingsTypeDef],
        "MxfSettings": NotRequired[MxfSettingsTypeDef],
    },
)
ContainerSettingsTypeDef = TypedDict(
    "ContainerSettingsTypeDef",
    {
        "CmfcSettings": NotRequired[CmfcSettingsTypeDef],
        "Container": NotRequired[ContainerTypeType],
        "F4vSettings": NotRequired[F4vSettingsTypeDef],
        "M2tsSettings": NotRequired[M2tsSettingsTypeDef],
        "M3u8Settings": NotRequired[M3u8SettingsTypeDef],
        "MovSettings": NotRequired[MovSettingsTypeDef],
        "Mp4Settings": NotRequired[Mp4SettingsTypeDef],
        "MpdSettings": NotRequired[MpdSettingsTypeDef],
        "MxfSettings": NotRequired[MxfSettingsTypeDef],
    },
)
VideoPreprocessorPaginatorTypeDef = TypedDict(
    "VideoPreprocessorPaginatorTypeDef",
    {
        "ColorCorrector": NotRequired[ColorCorrectorTypeDef],
        "Deinterlacer": NotRequired[DeinterlacerTypeDef],
        "DolbyVision": NotRequired[DolbyVisionTypeDef],
        "Hdr10Plus": NotRequired[Hdr10PlusTypeDef],
        "ImageInserter": NotRequired[ImageInserterPaginatorTypeDef],
        "NoiseReducer": NotRequired[NoiseReducerTypeDef],
        "PartnerWatermarking": NotRequired[PartnerWatermarkingTypeDef],
        "TimecodeBurnin": NotRequired[TimecodeBurninTypeDef],
    },
)
VideoPreprocessorTypeDef = TypedDict(
    "VideoPreprocessorTypeDef",
    {
        "ColorCorrector": NotRequired[ColorCorrectorTypeDef],
        "Deinterlacer": NotRequired[DeinterlacerTypeDef],
        "DolbyVision": NotRequired[DolbyVisionTypeDef],
        "Hdr10Plus": NotRequired[Hdr10PlusTypeDef],
        "ImageInserter": NotRequired[ImageInserterTypeDef],
        "NoiseReducer": NotRequired[NoiseReducerTypeDef],
        "PartnerWatermarking": NotRequired[PartnerWatermarkingTypeDef],
        "TimecodeBurnin": NotRequired[TimecodeBurninTypeDef],
    },
)
OutputGroupDetailTypeDef = TypedDict(
    "OutputGroupDetailTypeDef",
    {
        "OutputDetails": NotRequired[List[OutputDetailTypeDef]],
    },
)
CreateQueueResponseTypeDef = TypedDict(
    "CreateQueueResponseTypeDef",
    {
        "Queue": QueueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetQueueResponseTypeDef = TypedDict(
    "GetQueueResponseTypeDef",
    {
        "Queue": QueueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListQueuesResponseTypeDef = TypedDict(
    "ListQueuesResponseTypeDef",
    {
        "NextToken": str,
        "Queues": List[QueueTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateQueueResponseTypeDef = TypedDict(
    "UpdateQueueResponseTypeDef",
    {
        "Queue": QueueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DestinationSettingsTypeDef = TypedDict(
    "DestinationSettingsTypeDef",
    {
        "S3Settings": NotRequired[S3DestinationSettingsTypeDef],
    },
)
VideoOverlayPaginatorTypeDef = TypedDict(
    "VideoOverlayPaginatorTypeDef",
    {
        "EndTimecode": NotRequired[str],
        "Input": NotRequired[VideoOverlayInputPaginatorTypeDef],
        "StartTimecode": NotRequired[str],
    },
)
VideoOverlayTypeDef = TypedDict(
    "VideoOverlayTypeDef",
    {
        "EndTimecode": NotRequired[str],
        "Input": NotRequired[VideoOverlayInputTypeDef],
        "StartTimecode": NotRequired[str],
    },
)
VideoCodecSettingsTypeDef = TypedDict(
    "VideoCodecSettingsTypeDef",
    {
        "Av1Settings": NotRequired[Av1SettingsTypeDef],
        "AvcIntraSettings": NotRequired[AvcIntraSettingsTypeDef],
        "Codec": NotRequired[VideoCodecType],
        "FrameCaptureSettings": NotRequired[FrameCaptureSettingsTypeDef],
        "H264Settings": NotRequired[H264SettingsTypeDef],
        "H265Settings": NotRequired[H265SettingsTypeDef],
        "Mpeg2Settings": NotRequired[Mpeg2SettingsTypeDef],
        "ProresSettings": NotRequired[ProresSettingsTypeDef],
        "UncompressedSettings": NotRequired[UncompressedSettingsTypeDef],
        "Vc3Settings": NotRequired[Vc3SettingsTypeDef],
        "Vp8Settings": NotRequired[Vp8SettingsTypeDef],
        "Vp9Settings": NotRequired[Vp9SettingsTypeDef],
        "XavcSettings": NotRequired[XavcSettingsTypeDef],
    },
)
AutomatedEncodingSettingsPaginatorTypeDef = TypedDict(
    "AutomatedEncodingSettingsPaginatorTypeDef",
    {
        "AbrSettings": NotRequired[AutomatedAbrSettingsPaginatorTypeDef],
    },
)
AutomatedEncodingSettingsTypeDef = TypedDict(
    "AutomatedEncodingSettingsTypeDef",
    {
        "AbrSettings": NotRequired[AutomatedAbrSettingsTypeDef],
    },
)
CaptionSelectorTypeDef = TypedDict(
    "CaptionSelectorTypeDef",
    {
        "CustomLanguageCode": NotRequired[str],
        "LanguageCode": NotRequired[LanguageCodeType],
        "SourceSettings": NotRequired[CaptionSourceSettingsTypeDef],
    },
)
AudioDescriptionPaginatorTypeDef = TypedDict(
    "AudioDescriptionPaginatorTypeDef",
    {
        "AudioChannelTaggingSettings": NotRequired[AudioChannelTaggingSettingsPaginatorTypeDef],
        "AudioNormalizationSettings": NotRequired[AudioNormalizationSettingsTypeDef],
        "AudioSourceName": NotRequired[str],
        "AudioType": NotRequired[int],
        "AudioTypeControl": NotRequired[AudioTypeControlType],
        "CodecSettings": NotRequired[AudioCodecSettingsTypeDef],
        "CustomLanguageCode": NotRequired[str],
        "LanguageCode": NotRequired[LanguageCodeType],
        "LanguageCodeControl": NotRequired[AudioLanguageCodeControlType],
        "RemixSettings": NotRequired[RemixSettingsPaginatorTypeDef],
        "StreamName": NotRequired[str],
    },
)
AudioSelectorPaginatorTypeDef = TypedDict(
    "AudioSelectorPaginatorTypeDef",
    {
        "AudioDurationCorrection": NotRequired[AudioDurationCorrectionType],
        "CustomLanguageCode": NotRequired[str],
        "DefaultSelection": NotRequired[AudioDefaultSelectionType],
        "ExternalAudioFileInput": NotRequired[str],
        "HlsRenditionGroupSettings": NotRequired[HlsRenditionGroupSettingsTypeDef],
        "LanguageCode": NotRequired[LanguageCodeType],
        "Offset": NotRequired[int],
        "Pids": NotRequired[List[int]],
        "ProgramSelection": NotRequired[int],
        "RemixSettings": NotRequired[RemixSettingsPaginatorTypeDef],
        "SelectorType": NotRequired[AudioSelectorTypeType],
        "Tracks": NotRequired[List[int]],
    },
)
AudioDescriptionTypeDef = TypedDict(
    "AudioDescriptionTypeDef",
    {
        "AudioChannelTaggingSettings": NotRequired[AudioChannelTaggingSettingsTypeDef],
        "AudioNormalizationSettings": NotRequired[AudioNormalizationSettingsTypeDef],
        "AudioSourceName": NotRequired[str],
        "AudioType": NotRequired[int],
        "AudioTypeControl": NotRequired[AudioTypeControlType],
        "CodecSettings": NotRequired[AudioCodecSettingsTypeDef],
        "CustomLanguageCode": NotRequired[str],
        "LanguageCode": NotRequired[LanguageCodeType],
        "LanguageCodeControl": NotRequired[AudioLanguageCodeControlType],
        "RemixSettings": NotRequired[RemixSettingsTypeDef],
        "StreamName": NotRequired[str],
    },
)
AudioSelectorTypeDef = TypedDict(
    "AudioSelectorTypeDef",
    {
        "AudioDurationCorrection": NotRequired[AudioDurationCorrectionType],
        "CustomLanguageCode": NotRequired[str],
        "DefaultSelection": NotRequired[AudioDefaultSelectionType],
        "ExternalAudioFileInput": NotRequired[str],
        "HlsRenditionGroupSettings": NotRequired[HlsRenditionGroupSettingsTypeDef],
        "LanguageCode": NotRequired[LanguageCodeType],
        "Offset": NotRequired[int],
        "Pids": NotRequired[Sequence[int]],
        "ProgramSelection": NotRequired[int],
        "RemixSettings": NotRequired[RemixSettingsTypeDef],
        "SelectorType": NotRequired[AudioSelectorTypeType],
        "Tracks": NotRequired[Sequence[int]],
    },
)
CmafGroupSettingsPaginatorTypeDef = TypedDict(
    "CmafGroupSettingsPaginatorTypeDef",
    {
        "AdditionalManifests": NotRequired[List[CmafAdditionalManifestPaginatorTypeDef]],
        "BaseUrl": NotRequired[str],
        "ClientCache": NotRequired[CmafClientCacheType],
        "CodecSpecification": NotRequired[CmafCodecSpecificationType],
        "DashManifestStyle": NotRequired[DashManifestStyleType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "Encryption": NotRequired[CmafEncryptionSettingsPaginatorTypeDef],
        "FragmentLength": NotRequired[int],
        "ImageBasedTrickPlay": NotRequired[CmafImageBasedTrickPlayType],
        "ImageBasedTrickPlaySettings": NotRequired[CmafImageBasedTrickPlaySettingsTypeDef],
        "ManifestCompression": NotRequired[CmafManifestCompressionType],
        "ManifestDurationFormat": NotRequired[CmafManifestDurationFormatType],
        "MinBufferTime": NotRequired[int],
        "MinFinalSegmentLength": NotRequired[float],
        "MpdManifestBandwidthType": NotRequired[CmafMpdManifestBandwidthTypeType],
        "MpdProfile": NotRequired[CmafMpdProfileType],
        "PtsOffsetHandlingForBFrames": NotRequired[CmafPtsOffsetHandlingForBFramesType],
        "SegmentControl": NotRequired[CmafSegmentControlType],
        "SegmentLength": NotRequired[int],
        "SegmentLengthControl": NotRequired[CmafSegmentLengthControlType],
        "StreamInfResolution": NotRequired[CmafStreamInfResolutionType],
        "TargetDurationCompatibilityMode": NotRequired[CmafTargetDurationCompatibilityModeType],
        "VideoCompositionOffsets": NotRequired[CmafVideoCompositionOffsetsType],
        "WriteDashManifest": NotRequired[CmafWriteDASHManifestType],
        "WriteHlsManifest": NotRequired[CmafWriteHLSManifestType],
        "WriteSegmentTimelineInRepresentation": NotRequired[
            CmafWriteSegmentTimelineInRepresentationType
        ],
    },
)
CmafGroupSettingsTypeDef = TypedDict(
    "CmafGroupSettingsTypeDef",
    {
        "AdditionalManifests": NotRequired[Sequence[CmafAdditionalManifestTypeDef]],
        "BaseUrl": NotRequired[str],
        "ClientCache": NotRequired[CmafClientCacheType],
        "CodecSpecification": NotRequired[CmafCodecSpecificationType],
        "DashManifestStyle": NotRequired[DashManifestStyleType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "Encryption": NotRequired[CmafEncryptionSettingsTypeDef],
        "FragmentLength": NotRequired[int],
        "ImageBasedTrickPlay": NotRequired[CmafImageBasedTrickPlayType],
        "ImageBasedTrickPlaySettings": NotRequired[CmafImageBasedTrickPlaySettingsTypeDef],
        "ManifestCompression": NotRequired[CmafManifestCompressionType],
        "ManifestDurationFormat": NotRequired[CmafManifestDurationFormatType],
        "MinBufferTime": NotRequired[int],
        "MinFinalSegmentLength": NotRequired[float],
        "MpdManifestBandwidthType": NotRequired[CmafMpdManifestBandwidthTypeType],
        "MpdProfile": NotRequired[CmafMpdProfileType],
        "PtsOffsetHandlingForBFrames": NotRequired[CmafPtsOffsetHandlingForBFramesType],
        "SegmentControl": NotRequired[CmafSegmentControlType],
        "SegmentLength": NotRequired[int],
        "SegmentLengthControl": NotRequired[CmafSegmentLengthControlType],
        "StreamInfResolution": NotRequired[CmafStreamInfResolutionType],
        "TargetDurationCompatibilityMode": NotRequired[CmafTargetDurationCompatibilityModeType],
        "VideoCompositionOffsets": NotRequired[CmafVideoCompositionOffsetsType],
        "WriteDashManifest": NotRequired[CmafWriteDASHManifestType],
        "WriteHlsManifest": NotRequired[CmafWriteHLSManifestType],
        "WriteSegmentTimelineInRepresentation": NotRequired[
            CmafWriteSegmentTimelineInRepresentationType
        ],
    },
)
DashIsoGroupSettingsPaginatorTypeDef = TypedDict(
    "DashIsoGroupSettingsPaginatorTypeDef",
    {
        "AdditionalManifests": NotRequired[List[DashAdditionalManifestPaginatorTypeDef]],
        "AudioChannelConfigSchemeIdUri": NotRequired[DashIsoGroupAudioChannelConfigSchemeIdUriType],
        "BaseUrl": NotRequired[str],
        "DashManifestStyle": NotRequired[DashManifestStyleType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "Encryption": NotRequired[DashIsoEncryptionSettingsPaginatorTypeDef],
        "FragmentLength": NotRequired[int],
        "HbbtvCompliance": NotRequired[DashIsoHbbtvComplianceType],
        "ImageBasedTrickPlay": NotRequired[DashIsoImageBasedTrickPlayType],
        "ImageBasedTrickPlaySettings": NotRequired[DashIsoImageBasedTrickPlaySettingsTypeDef],
        "MinBufferTime": NotRequired[int],
        "MinFinalSegmentLength": NotRequired[float],
        "MpdManifestBandwidthType": NotRequired[DashIsoMpdManifestBandwidthTypeType],
        "MpdProfile": NotRequired[DashIsoMpdProfileType],
        "PtsOffsetHandlingForBFrames": NotRequired[DashIsoPtsOffsetHandlingForBFramesType],
        "SegmentControl": NotRequired[DashIsoSegmentControlType],
        "SegmentLength": NotRequired[int],
        "SegmentLengthControl": NotRequired[DashIsoSegmentLengthControlType],
        "VideoCompositionOffsets": NotRequired[DashIsoVideoCompositionOffsetsType],
        "WriteSegmentTimelineInRepresentation": NotRequired[
            DashIsoWriteSegmentTimelineInRepresentationType
        ],
    },
)
DashIsoGroupSettingsTypeDef = TypedDict(
    "DashIsoGroupSettingsTypeDef",
    {
        "AdditionalManifests": NotRequired[Sequence[DashAdditionalManifestTypeDef]],
        "AudioChannelConfigSchemeIdUri": NotRequired[DashIsoGroupAudioChannelConfigSchemeIdUriType],
        "BaseUrl": NotRequired[str],
        "DashManifestStyle": NotRequired[DashManifestStyleType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "Encryption": NotRequired[DashIsoEncryptionSettingsTypeDef],
        "FragmentLength": NotRequired[int],
        "HbbtvCompliance": NotRequired[DashIsoHbbtvComplianceType],
        "ImageBasedTrickPlay": NotRequired[DashIsoImageBasedTrickPlayType],
        "ImageBasedTrickPlaySettings": NotRequired[DashIsoImageBasedTrickPlaySettingsTypeDef],
        "MinBufferTime": NotRequired[int],
        "MinFinalSegmentLength": NotRequired[float],
        "MpdManifestBandwidthType": NotRequired[DashIsoMpdManifestBandwidthTypeType],
        "MpdProfile": NotRequired[DashIsoMpdProfileType],
        "PtsOffsetHandlingForBFrames": NotRequired[DashIsoPtsOffsetHandlingForBFramesType],
        "SegmentControl": NotRequired[DashIsoSegmentControlType],
        "SegmentLength": NotRequired[int],
        "SegmentLengthControl": NotRequired[DashIsoSegmentLengthControlType],
        "VideoCompositionOffsets": NotRequired[DashIsoVideoCompositionOffsetsType],
        "WriteSegmentTimelineInRepresentation": NotRequired[
            DashIsoWriteSegmentTimelineInRepresentationType
        ],
    },
)
FileGroupSettingsTypeDef = TypedDict(
    "FileGroupSettingsTypeDef",
    {
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
    },
)
HlsGroupSettingsPaginatorTypeDef = TypedDict(
    "HlsGroupSettingsPaginatorTypeDef",
    {
        "AdMarkers": NotRequired[List[HlsAdMarkersType]],
        "AdditionalManifests": NotRequired[List[HlsAdditionalManifestPaginatorTypeDef]],
        "AudioOnlyHeader": NotRequired[HlsAudioOnlyHeaderType],
        "BaseUrl": NotRequired[str],
        "CaptionLanguageMappings": NotRequired[List[HlsCaptionLanguageMappingTypeDef]],
        "CaptionLanguageSetting": NotRequired[HlsCaptionLanguageSettingType],
        "CaptionSegmentLengthControl": NotRequired[HlsCaptionSegmentLengthControlType],
        "ClientCache": NotRequired[HlsClientCacheType],
        "CodecSpecification": NotRequired[HlsCodecSpecificationType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "DirectoryStructure": NotRequired[HlsDirectoryStructureType],
        "Encryption": NotRequired[HlsEncryptionSettingsPaginatorTypeDef],
        "ImageBasedTrickPlay": NotRequired[HlsImageBasedTrickPlayType],
        "ImageBasedTrickPlaySettings": NotRequired[HlsImageBasedTrickPlaySettingsTypeDef],
        "ManifestCompression": NotRequired[HlsManifestCompressionType],
        "ManifestDurationFormat": NotRequired[HlsManifestDurationFormatType],
        "MinFinalSegmentLength": NotRequired[float],
        "MinSegmentLength": NotRequired[int],
        "OutputSelection": NotRequired[HlsOutputSelectionType],
        "ProgramDateTime": NotRequired[HlsProgramDateTimeType],
        "ProgramDateTimePeriod": NotRequired[int],
        "ProgressiveWriteHlsManifest": NotRequired[HlsProgressiveWriteHlsManifestType],
        "SegmentControl": NotRequired[HlsSegmentControlType],
        "SegmentLength": NotRequired[int],
        "SegmentLengthControl": NotRequired[HlsSegmentLengthControlType],
        "SegmentsPerSubdirectory": NotRequired[int],
        "StreamInfResolution": NotRequired[HlsStreamInfResolutionType],
        "TargetDurationCompatibilityMode": NotRequired[HlsTargetDurationCompatibilityModeType],
        "TimedMetadataId3Frame": NotRequired[HlsTimedMetadataId3FrameType],
        "TimedMetadataId3Period": NotRequired[int],
        "TimestampDeltaMilliseconds": NotRequired[int],
    },
)
HlsGroupSettingsTypeDef = TypedDict(
    "HlsGroupSettingsTypeDef",
    {
        "AdMarkers": NotRequired[Sequence[HlsAdMarkersType]],
        "AdditionalManifests": NotRequired[Sequence[HlsAdditionalManifestTypeDef]],
        "AudioOnlyHeader": NotRequired[HlsAudioOnlyHeaderType],
        "BaseUrl": NotRequired[str],
        "CaptionLanguageMappings": NotRequired[Sequence[HlsCaptionLanguageMappingTypeDef]],
        "CaptionLanguageSetting": NotRequired[HlsCaptionLanguageSettingType],
        "CaptionSegmentLengthControl": NotRequired[HlsCaptionSegmentLengthControlType],
        "ClientCache": NotRequired[HlsClientCacheType],
        "CodecSpecification": NotRequired[HlsCodecSpecificationType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "DirectoryStructure": NotRequired[HlsDirectoryStructureType],
        "Encryption": NotRequired[HlsEncryptionSettingsTypeDef],
        "ImageBasedTrickPlay": NotRequired[HlsImageBasedTrickPlayType],
        "ImageBasedTrickPlaySettings": NotRequired[HlsImageBasedTrickPlaySettingsTypeDef],
        "ManifestCompression": NotRequired[HlsManifestCompressionType],
        "ManifestDurationFormat": NotRequired[HlsManifestDurationFormatType],
        "MinFinalSegmentLength": NotRequired[float],
        "MinSegmentLength": NotRequired[int],
        "OutputSelection": NotRequired[HlsOutputSelectionType],
        "ProgramDateTime": NotRequired[HlsProgramDateTimeType],
        "ProgramDateTimePeriod": NotRequired[int],
        "ProgressiveWriteHlsManifest": NotRequired[HlsProgressiveWriteHlsManifestType],
        "SegmentControl": NotRequired[HlsSegmentControlType],
        "SegmentLength": NotRequired[int],
        "SegmentLengthControl": NotRequired[HlsSegmentLengthControlType],
        "SegmentsPerSubdirectory": NotRequired[int],
        "StreamInfResolution": NotRequired[HlsStreamInfResolutionType],
        "TargetDurationCompatibilityMode": NotRequired[HlsTargetDurationCompatibilityModeType],
        "TimedMetadataId3Frame": NotRequired[HlsTimedMetadataId3FrameType],
        "TimedMetadataId3Period": NotRequired[int],
        "TimestampDeltaMilliseconds": NotRequired[int],
    },
)
MsSmoothGroupSettingsPaginatorTypeDef = TypedDict(
    "MsSmoothGroupSettingsPaginatorTypeDef",
    {
        "AdditionalManifests": NotRequired[List[MsSmoothAdditionalManifestPaginatorTypeDef]],
        "AudioDeduplication": NotRequired[MsSmoothAudioDeduplicationType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "Encryption": NotRequired[MsSmoothEncryptionSettingsPaginatorTypeDef],
        "FragmentLength": NotRequired[int],
        "FragmentLengthControl": NotRequired[MsSmoothFragmentLengthControlType],
        "ManifestEncoding": NotRequired[MsSmoothManifestEncodingType],
    },
)
MsSmoothGroupSettingsTypeDef = TypedDict(
    "MsSmoothGroupSettingsTypeDef",
    {
        "AdditionalManifests": NotRequired[Sequence[MsSmoothAdditionalManifestTypeDef]],
        "AudioDeduplication": NotRequired[MsSmoothAudioDeduplicationType],
        "Destination": NotRequired[str],
        "DestinationSettings": NotRequired[DestinationSettingsTypeDef],
        "Encryption": NotRequired[MsSmoothEncryptionSettingsTypeDef],
        "FragmentLength": NotRequired[int],
        "FragmentLengthControl": NotRequired[MsSmoothFragmentLengthControlType],
        "ManifestEncoding": NotRequired[MsSmoothManifestEncodingType],
    },
)
VideoDescriptionPaginatorTypeDef = TypedDict(
    "VideoDescriptionPaginatorTypeDef",
    {
        "AfdSignaling": NotRequired[AfdSignalingType],
        "AntiAlias": NotRequired[AntiAliasType],
        "CodecSettings": NotRequired[VideoCodecSettingsTypeDef],
        "ColorMetadata": NotRequired[ColorMetadataType],
        "Crop": NotRequired[RectangleTypeDef],
        "DropFrameTimecode": NotRequired[DropFrameTimecodeType],
        "FixedAfd": NotRequired[int],
        "Height": NotRequired[int],
        "Position": NotRequired[RectangleTypeDef],
        "RespondToAfd": NotRequired[RespondToAfdType],
        "ScalingBehavior": NotRequired[ScalingBehaviorType],
        "Sharpness": NotRequired[int],
        "TimecodeInsertion": NotRequired[VideoTimecodeInsertionType],
        "VideoPreprocessors": NotRequired[VideoPreprocessorPaginatorTypeDef],
        "Width": NotRequired[int],
    },
)
VideoDescriptionTypeDef = TypedDict(
    "VideoDescriptionTypeDef",
    {
        "AfdSignaling": NotRequired[AfdSignalingType],
        "AntiAlias": NotRequired[AntiAliasType],
        "CodecSettings": NotRequired[VideoCodecSettingsTypeDef],
        "ColorMetadata": NotRequired[ColorMetadataType],
        "Crop": NotRequired[RectangleTypeDef],
        "DropFrameTimecode": NotRequired[DropFrameTimecodeType],
        "FixedAfd": NotRequired[int],
        "Height": NotRequired[int],
        "Position": NotRequired[RectangleTypeDef],
        "RespondToAfd": NotRequired[RespondToAfdType],
        "ScalingBehavior": NotRequired[ScalingBehaviorType],
        "Sharpness": NotRequired[int],
        "TimecodeInsertion": NotRequired[VideoTimecodeInsertionType],
        "VideoPreprocessors": NotRequired[VideoPreprocessorTypeDef],
        "Width": NotRequired[int],
    },
)
InputPaginatorTypeDef = TypedDict(
    "InputPaginatorTypeDef",
    {
        "AdvancedInputFilter": NotRequired[AdvancedInputFilterType],
        "AdvancedInputFilterSettings": NotRequired[AdvancedInputFilterSettingsTypeDef],
        "AudioSelectorGroups": NotRequired[Dict[str, AudioSelectorGroupPaginatorTypeDef]],
        "AudioSelectors": NotRequired[Dict[str, AudioSelectorPaginatorTypeDef]],
        "CaptionSelectors": NotRequired[Dict[str, CaptionSelectorTypeDef]],
        "Crop": NotRequired[RectangleTypeDef],
        "DeblockFilter": NotRequired[InputDeblockFilterType],
        "DecryptionSettings": NotRequired[InputDecryptionSettingsTypeDef],
        "DenoiseFilter": NotRequired[InputDenoiseFilterType],
        "DolbyVisionMetadataXml": NotRequired[str],
        "FileInput": NotRequired[str],
        "FilterEnable": NotRequired[InputFilterEnableType],
        "FilterStrength": NotRequired[int],
        "ImageInserter": NotRequired[ImageInserterPaginatorTypeDef],
        "InputClippings": NotRequired[List[InputClippingTypeDef]],
        "InputScanType": NotRequired[InputScanTypeType],
        "Position": NotRequired[RectangleTypeDef],
        "ProgramNumber": NotRequired[int],
        "PsiControl": NotRequired[InputPsiControlType],
        "SupplementalImps": NotRequired[List[str]],
        "TimecodeSource": NotRequired[InputTimecodeSourceType],
        "TimecodeStart": NotRequired[str],
        "VideoGenerator": NotRequired[InputVideoGeneratorTypeDef],
        "VideoOverlays": NotRequired[List[VideoOverlayPaginatorTypeDef]],
        "VideoSelector": NotRequired[VideoSelectorTypeDef],
    },
)
InputTemplatePaginatorTypeDef = TypedDict(
    "InputTemplatePaginatorTypeDef",
    {
        "AdvancedInputFilter": NotRequired[AdvancedInputFilterType],
        "AdvancedInputFilterSettings": NotRequired[AdvancedInputFilterSettingsTypeDef],
        "AudioSelectorGroups": NotRequired[Dict[str, AudioSelectorGroupPaginatorTypeDef]],
        "AudioSelectors": NotRequired[Dict[str, AudioSelectorPaginatorTypeDef]],
        "CaptionSelectors": NotRequired[Dict[str, CaptionSelectorTypeDef]],
        "Crop": NotRequired[RectangleTypeDef],
        "DeblockFilter": NotRequired[InputDeblockFilterType],
        "DenoiseFilter": NotRequired[InputDenoiseFilterType],
        "DolbyVisionMetadataXml": NotRequired[str],
        "FilterEnable": NotRequired[InputFilterEnableType],
        "FilterStrength": NotRequired[int],
        "ImageInserter": NotRequired[ImageInserterPaginatorTypeDef],
        "InputClippings": NotRequired[List[InputClippingTypeDef]],
        "InputScanType": NotRequired[InputScanTypeType],
        "Position": NotRequired[RectangleTypeDef],
        "ProgramNumber": NotRequired[int],
        "PsiControl": NotRequired[InputPsiControlType],
        "TimecodeSource": NotRequired[InputTimecodeSourceType],
        "TimecodeStart": NotRequired[str],
        "VideoOverlays": NotRequired[List[VideoOverlayPaginatorTypeDef]],
        "VideoSelector": NotRequired[VideoSelectorTypeDef],
    },
)
InputTemplateTypeDef = TypedDict(
    "InputTemplateTypeDef",
    {
        "AdvancedInputFilter": NotRequired[AdvancedInputFilterType],
        "AdvancedInputFilterSettings": NotRequired[AdvancedInputFilterSettingsTypeDef],
        "AudioSelectorGroups": NotRequired[Mapping[str, AudioSelectorGroupTypeDef]],
        "AudioSelectors": NotRequired[Mapping[str, AudioSelectorTypeDef]],
        "CaptionSelectors": NotRequired[Mapping[str, CaptionSelectorTypeDef]],
        "Crop": NotRequired[RectangleTypeDef],
        "DeblockFilter": NotRequired[InputDeblockFilterType],
        "DenoiseFilter": NotRequired[InputDenoiseFilterType],
        "DolbyVisionMetadataXml": NotRequired[str],
        "FilterEnable": NotRequired[InputFilterEnableType],
        "FilterStrength": NotRequired[int],
        "ImageInserter": NotRequired[ImageInserterTypeDef],
        "InputClippings": NotRequired[Sequence[InputClippingTypeDef]],
        "InputScanType": NotRequired[InputScanTypeType],
        "Position": NotRequired[RectangleTypeDef],
        "ProgramNumber": NotRequired[int],
        "PsiControl": NotRequired[InputPsiControlType],
        "TimecodeSource": NotRequired[InputTimecodeSourceType],
        "TimecodeStart": NotRequired[str],
        "VideoOverlays": NotRequired[Sequence[VideoOverlayTypeDef]],
        "VideoSelector": NotRequired[VideoSelectorTypeDef],
    },
)
InputTypeDef = TypedDict(
    "InputTypeDef",
    {
        "AdvancedInputFilter": NotRequired[AdvancedInputFilterType],
        "AdvancedInputFilterSettings": NotRequired[AdvancedInputFilterSettingsTypeDef],
        "AudioSelectorGroups": NotRequired[Mapping[str, AudioSelectorGroupTypeDef]],
        "AudioSelectors": NotRequired[Mapping[str, AudioSelectorTypeDef]],
        "CaptionSelectors": NotRequired[Mapping[str, CaptionSelectorTypeDef]],
        "Crop": NotRequired[RectangleTypeDef],
        "DeblockFilter": NotRequired[InputDeblockFilterType],
        "DecryptionSettings": NotRequired[InputDecryptionSettingsTypeDef],
        "DenoiseFilter": NotRequired[InputDenoiseFilterType],
        "DolbyVisionMetadataXml": NotRequired[str],
        "FileInput": NotRequired[str],
        "FilterEnable": NotRequired[InputFilterEnableType],
        "FilterStrength": NotRequired[int],
        "ImageInserter": NotRequired[ImageInserterTypeDef],
        "InputClippings": NotRequired[Sequence[InputClippingTypeDef]],
        "InputScanType": NotRequired[InputScanTypeType],
        "Position": NotRequired[RectangleTypeDef],
        "ProgramNumber": NotRequired[int],
        "PsiControl": NotRequired[InputPsiControlType],
        "SupplementalImps": NotRequired[Sequence[str]],
        "TimecodeSource": NotRequired[InputTimecodeSourceType],
        "TimecodeStart": NotRequired[str],
        "VideoGenerator": NotRequired[InputVideoGeneratorTypeDef],
        "VideoOverlays": NotRequired[Sequence[VideoOverlayTypeDef]],
        "VideoSelector": NotRequired[VideoSelectorTypeDef],
    },
)
OutputGroupSettingsPaginatorTypeDef = TypedDict(
    "OutputGroupSettingsPaginatorTypeDef",
    {
        "CmafGroupSettings": NotRequired[CmafGroupSettingsPaginatorTypeDef],
        "DashIsoGroupSettings": NotRequired[DashIsoGroupSettingsPaginatorTypeDef],
        "FileGroupSettings": NotRequired[FileGroupSettingsTypeDef],
        "HlsGroupSettings": NotRequired[HlsGroupSettingsPaginatorTypeDef],
        "MsSmoothGroupSettings": NotRequired[MsSmoothGroupSettingsPaginatorTypeDef],
        "Type": NotRequired[OutputGroupTypeType],
    },
)
OutputGroupSettingsTypeDef = TypedDict(
    "OutputGroupSettingsTypeDef",
    {
        "CmafGroupSettings": NotRequired[CmafGroupSettingsTypeDef],
        "DashIsoGroupSettings": NotRequired[DashIsoGroupSettingsTypeDef],
        "FileGroupSettings": NotRequired[FileGroupSettingsTypeDef],
        "HlsGroupSettings": NotRequired[HlsGroupSettingsTypeDef],
        "MsSmoothGroupSettings": NotRequired[MsSmoothGroupSettingsTypeDef],
        "Type": NotRequired[OutputGroupTypeType],
    },
)
OutputPaginatorTypeDef = TypedDict(
    "OutputPaginatorTypeDef",
    {
        "AudioDescriptions": NotRequired[List[AudioDescriptionPaginatorTypeDef]],
        "CaptionDescriptions": NotRequired[List[CaptionDescriptionPaginatorTypeDef]],
        "ContainerSettings": NotRequired[ContainerSettingsPaginatorTypeDef],
        "Extension": NotRequired[str],
        "NameModifier": NotRequired[str],
        "OutputSettings": NotRequired[OutputSettingsTypeDef],
        "Preset": NotRequired[str],
        "VideoDescription": NotRequired[VideoDescriptionPaginatorTypeDef],
    },
)
PresetSettingsPaginatorTypeDef = TypedDict(
    "PresetSettingsPaginatorTypeDef",
    {
        "AudioDescriptions": NotRequired[List[AudioDescriptionPaginatorTypeDef]],
        "CaptionDescriptions": NotRequired[List[CaptionDescriptionPresetPaginatorTypeDef]],
        "ContainerSettings": NotRequired[ContainerSettingsPaginatorTypeDef],
        "VideoDescription": NotRequired[VideoDescriptionPaginatorTypeDef],
    },
)
OutputTypeDef = TypedDict(
    "OutputTypeDef",
    {
        "AudioDescriptions": NotRequired[Sequence[AudioDescriptionTypeDef]],
        "CaptionDescriptions": NotRequired[Sequence[CaptionDescriptionTypeDef]],
        "ContainerSettings": NotRequired[ContainerSettingsTypeDef],
        "Extension": NotRequired[str],
        "NameModifier": NotRequired[str],
        "OutputSettings": NotRequired[OutputSettingsTypeDef],
        "Preset": NotRequired[str],
        "VideoDescription": NotRequired[VideoDescriptionTypeDef],
    },
)
PresetSettingsTypeDef = TypedDict(
    "PresetSettingsTypeDef",
    {
        "AudioDescriptions": NotRequired[Sequence[AudioDescriptionTypeDef]],
        "CaptionDescriptions": NotRequired[Sequence[CaptionDescriptionPresetTypeDef]],
        "ContainerSettings": NotRequired[ContainerSettingsTypeDef],
        "VideoDescription": NotRequired[VideoDescriptionTypeDef],
    },
)
OutputGroupPaginatorTypeDef = TypedDict(
    "OutputGroupPaginatorTypeDef",
    {
        "AutomatedEncodingSettings": NotRequired[AutomatedEncodingSettingsPaginatorTypeDef],
        "CustomName": NotRequired[str],
        "Name": NotRequired[str],
        "OutputGroupSettings": NotRequired[OutputGroupSettingsPaginatorTypeDef],
        "Outputs": NotRequired[List[OutputPaginatorTypeDef]],
    },
)
PresetPaginatorTypeDef = TypedDict(
    "PresetPaginatorTypeDef",
    {
        "Name": str,
        "Settings": PresetSettingsPaginatorTypeDef,
        "Arn": NotRequired[str],
        "Category": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "Description": NotRequired[str],
        "LastUpdated": NotRequired[datetime],
        "Type": NotRequired[TypeType],
    },
)
OutputGroupTypeDef = TypedDict(
    "OutputGroupTypeDef",
    {
        "AutomatedEncodingSettings": NotRequired[AutomatedEncodingSettingsTypeDef],
        "CustomName": NotRequired[str],
        "Name": NotRequired[str],
        "OutputGroupSettings": NotRequired[OutputGroupSettingsTypeDef],
        "Outputs": NotRequired[Sequence[OutputTypeDef]],
    },
)
CreatePresetRequestRequestTypeDef = TypedDict(
    "CreatePresetRequestRequestTypeDef",
    {
        "Name": str,
        "Settings": PresetSettingsTypeDef,
        "Category": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
PresetTypeDef = TypedDict(
    "PresetTypeDef",
    {
        "Name": str,
        "Settings": PresetSettingsTypeDef,
        "Arn": NotRequired[str],
        "Category": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "Description": NotRequired[str],
        "LastUpdated": NotRequired[datetime],
        "Type": NotRequired[TypeType],
    },
)
UpdatePresetRequestRequestTypeDef = TypedDict(
    "UpdatePresetRequestRequestTypeDef",
    {
        "Name": str,
        "Category": NotRequired[str],
        "Description": NotRequired[str],
        "Settings": NotRequired[PresetSettingsTypeDef],
    },
)
JobSettingsPaginatorTypeDef = TypedDict(
    "JobSettingsPaginatorTypeDef",
    {
        "AdAvailOffset": NotRequired[int],
        "AvailBlanking": NotRequired[AvailBlankingTypeDef],
        "ColorConversion3DLUTSettings": NotRequired[List[ColorConversion3DLUTSettingTypeDef]],
        "Esam": NotRequired[EsamSettingsTypeDef],
        "ExtendedDataServices": NotRequired[ExtendedDataServicesTypeDef],
        "FollowSource": NotRequired[int],
        "Inputs": NotRequired[List[InputPaginatorTypeDef]],
        "KantarWatermark": NotRequired[KantarWatermarkSettingsTypeDef],
        "MotionImageInserter": NotRequired[MotionImageInserterTypeDef],
        "NielsenConfiguration": NotRequired[NielsenConfigurationTypeDef],
        "NielsenNonLinearWatermark": NotRequired[NielsenNonLinearWatermarkSettingsTypeDef],
        "OutputGroups": NotRequired[List[OutputGroupPaginatorTypeDef]],
        "TimecodeConfig": NotRequired[TimecodeConfigTypeDef],
        "TimedMetadataInsertion": NotRequired[TimedMetadataInsertionPaginatorTypeDef],
    },
)
JobTemplateSettingsPaginatorTypeDef = TypedDict(
    "JobTemplateSettingsPaginatorTypeDef",
    {
        "AdAvailOffset": NotRequired[int],
        "AvailBlanking": NotRequired[AvailBlankingTypeDef],
        "ColorConversion3DLUTSettings": NotRequired[List[ColorConversion3DLUTSettingTypeDef]],
        "Esam": NotRequired[EsamSettingsTypeDef],
        "ExtendedDataServices": NotRequired[ExtendedDataServicesTypeDef],
        "FollowSource": NotRequired[int],
        "Inputs": NotRequired[List[InputTemplatePaginatorTypeDef]],
        "KantarWatermark": NotRequired[KantarWatermarkSettingsTypeDef],
        "MotionImageInserter": NotRequired[MotionImageInserterTypeDef],
        "NielsenConfiguration": NotRequired[NielsenConfigurationTypeDef],
        "NielsenNonLinearWatermark": NotRequired[NielsenNonLinearWatermarkSettingsTypeDef],
        "OutputGroups": NotRequired[List[OutputGroupPaginatorTypeDef]],
        "TimecodeConfig": NotRequired[TimecodeConfigTypeDef],
        "TimedMetadataInsertion": NotRequired[TimedMetadataInsertionPaginatorTypeDef],
    },
)
ListPresetsResponsePaginatorTypeDef = TypedDict(
    "ListPresetsResponsePaginatorTypeDef",
    {
        "NextToken": str,
        "Presets": List[PresetPaginatorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
JobSettingsTypeDef = TypedDict(
    "JobSettingsTypeDef",
    {
        "AdAvailOffset": NotRequired[int],
        "AvailBlanking": NotRequired[AvailBlankingTypeDef],
        "ColorConversion3DLUTSettings": NotRequired[Sequence[ColorConversion3DLUTSettingTypeDef]],
        "Esam": NotRequired[EsamSettingsTypeDef],
        "ExtendedDataServices": NotRequired[ExtendedDataServicesTypeDef],
        "FollowSource": NotRequired[int],
        "Inputs": NotRequired[Sequence[InputTypeDef]],
        "KantarWatermark": NotRequired[KantarWatermarkSettingsTypeDef],
        "MotionImageInserter": NotRequired[MotionImageInserterTypeDef],
        "NielsenConfiguration": NotRequired[NielsenConfigurationTypeDef],
        "NielsenNonLinearWatermark": NotRequired[NielsenNonLinearWatermarkSettingsTypeDef],
        "OutputGroups": NotRequired[Sequence[OutputGroupTypeDef]],
        "TimecodeConfig": NotRequired[TimecodeConfigTypeDef],
        "TimedMetadataInsertion": NotRequired[TimedMetadataInsertionTypeDef],
    },
)
JobTemplateSettingsTypeDef = TypedDict(
    "JobTemplateSettingsTypeDef",
    {
        "AdAvailOffset": NotRequired[int],
        "AvailBlanking": NotRequired[AvailBlankingTypeDef],
        "ColorConversion3DLUTSettings": NotRequired[Sequence[ColorConversion3DLUTSettingTypeDef]],
        "Esam": NotRequired[EsamSettingsTypeDef],
        "ExtendedDataServices": NotRequired[ExtendedDataServicesTypeDef],
        "FollowSource": NotRequired[int],
        "Inputs": NotRequired[Sequence[InputTemplateTypeDef]],
        "KantarWatermark": NotRequired[KantarWatermarkSettingsTypeDef],
        "MotionImageInserter": NotRequired[MotionImageInserterTypeDef],
        "NielsenConfiguration": NotRequired[NielsenConfigurationTypeDef],
        "NielsenNonLinearWatermark": NotRequired[NielsenNonLinearWatermarkSettingsTypeDef],
        "OutputGroups": NotRequired[Sequence[OutputGroupTypeDef]],
        "TimecodeConfig": NotRequired[TimecodeConfigTypeDef],
        "TimedMetadataInsertion": NotRequired[TimedMetadataInsertionTypeDef],
    },
)
CreatePresetResponseTypeDef = TypedDict(
    "CreatePresetResponseTypeDef",
    {
        "Preset": PresetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPresetResponseTypeDef = TypedDict(
    "GetPresetResponseTypeDef",
    {
        "Preset": PresetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPresetsResponseTypeDef = TypedDict(
    "ListPresetsResponseTypeDef",
    {
        "NextToken": str,
        "Presets": List[PresetTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePresetResponseTypeDef = TypedDict(
    "UpdatePresetResponseTypeDef",
    {
        "Preset": PresetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
JobPaginatorTypeDef = TypedDict(
    "JobPaginatorTypeDef",
    {
        "Role": str,
        "Settings": JobSettingsPaginatorTypeDef,
        "AccelerationSettings": NotRequired[AccelerationSettingsTypeDef],
        "AccelerationStatus": NotRequired[AccelerationStatusType],
        "Arn": NotRequired[str],
        "BillingTagsSource": NotRequired[BillingTagsSourceType],
        "ClientRequestToken": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "CurrentPhase": NotRequired[JobPhaseType],
        "ErrorCode": NotRequired[int],
        "ErrorMessage": NotRequired[str],
        "HopDestinations": NotRequired[List[HopDestinationTypeDef]],
        "Id": NotRequired[str],
        "JobPercentComplete": NotRequired[int],
        "JobTemplate": NotRequired[str],
        "Messages": NotRequired[JobMessagesTypeDef],
        "OutputGroupDetails": NotRequired[List[OutputGroupDetailTypeDef]],
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "QueueTransitions": NotRequired[List[QueueTransitionTypeDef]],
        "RetryCount": NotRequired[int],
        "SimulateReservedQueue": NotRequired[SimulateReservedQueueType],
        "Status": NotRequired[JobStatusType],
        "StatusUpdateInterval": NotRequired[StatusUpdateIntervalType],
        "Timing": NotRequired[TimingTypeDef],
        "UserMetadata": NotRequired[Dict[str, str]],
        "Warnings": NotRequired[List[WarningGroupTypeDef]],
    },
)
JobTemplatePaginatorTypeDef = TypedDict(
    "JobTemplatePaginatorTypeDef",
    {
        "Name": str,
        "Settings": JobTemplateSettingsPaginatorTypeDef,
        "AccelerationSettings": NotRequired[AccelerationSettingsTypeDef],
        "Arn": NotRequired[str],
        "Category": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "Description": NotRequired[str],
        "HopDestinations": NotRequired[List[HopDestinationTypeDef]],
        "LastUpdated": NotRequired[datetime],
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "StatusUpdateInterval": NotRequired[StatusUpdateIntervalType],
        "Type": NotRequired[TypeType],
    },
)
CreateJobRequestRequestTypeDef = TypedDict(
    "CreateJobRequestRequestTypeDef",
    {
        "Role": str,
        "Settings": JobSettingsTypeDef,
        "AccelerationSettings": NotRequired[AccelerationSettingsTypeDef],
        "BillingTagsSource": NotRequired[BillingTagsSourceType],
        "ClientRequestToken": NotRequired[str],
        "HopDestinations": NotRequired[Sequence[HopDestinationTypeDef]],
        "JobTemplate": NotRequired[str],
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "SimulateReservedQueue": NotRequired[SimulateReservedQueueType],
        "StatusUpdateInterval": NotRequired[StatusUpdateIntervalType],
        "Tags": NotRequired[Mapping[str, str]],
        "UserMetadata": NotRequired[Mapping[str, str]],
    },
)
JobTypeDef = TypedDict(
    "JobTypeDef",
    {
        "Role": str,
        "Settings": JobSettingsTypeDef,
        "AccelerationSettings": NotRequired[AccelerationSettingsTypeDef],
        "AccelerationStatus": NotRequired[AccelerationStatusType],
        "Arn": NotRequired[str],
        "BillingTagsSource": NotRequired[BillingTagsSourceType],
        "ClientRequestToken": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "CurrentPhase": NotRequired[JobPhaseType],
        "ErrorCode": NotRequired[int],
        "ErrorMessage": NotRequired[str],
        "HopDestinations": NotRequired[List[HopDestinationTypeDef]],
        "Id": NotRequired[str],
        "JobPercentComplete": NotRequired[int],
        "JobTemplate": NotRequired[str],
        "Messages": NotRequired[JobMessagesTypeDef],
        "OutputGroupDetails": NotRequired[List[OutputGroupDetailTypeDef]],
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "QueueTransitions": NotRequired[List[QueueTransitionTypeDef]],
        "RetryCount": NotRequired[int],
        "SimulateReservedQueue": NotRequired[SimulateReservedQueueType],
        "Status": NotRequired[JobStatusType],
        "StatusUpdateInterval": NotRequired[StatusUpdateIntervalType],
        "Timing": NotRequired[TimingTypeDef],
        "UserMetadata": NotRequired[Dict[str, str]],
        "Warnings": NotRequired[List[WarningGroupTypeDef]],
    },
)
CreateJobTemplateRequestRequestTypeDef = TypedDict(
    "CreateJobTemplateRequestRequestTypeDef",
    {
        "Name": str,
        "Settings": JobTemplateSettingsTypeDef,
        "AccelerationSettings": NotRequired[AccelerationSettingsTypeDef],
        "Category": NotRequired[str],
        "Description": NotRequired[str],
        "HopDestinations": NotRequired[Sequence[HopDestinationTypeDef]],
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "StatusUpdateInterval": NotRequired[StatusUpdateIntervalType],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
JobTemplateTypeDef = TypedDict(
    "JobTemplateTypeDef",
    {
        "Name": str,
        "Settings": JobTemplateSettingsTypeDef,
        "AccelerationSettings": NotRequired[AccelerationSettingsTypeDef],
        "Arn": NotRequired[str],
        "Category": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "Description": NotRequired[str],
        "HopDestinations": NotRequired[List[HopDestinationTypeDef]],
        "LastUpdated": NotRequired[datetime],
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "StatusUpdateInterval": NotRequired[StatusUpdateIntervalType],
        "Type": NotRequired[TypeType],
    },
)
UpdateJobTemplateRequestRequestTypeDef = TypedDict(
    "UpdateJobTemplateRequestRequestTypeDef",
    {
        "Name": str,
        "AccelerationSettings": NotRequired[AccelerationSettingsTypeDef],
        "Category": NotRequired[str],
        "Description": NotRequired[str],
        "HopDestinations": NotRequired[Sequence[HopDestinationTypeDef]],
        "Priority": NotRequired[int],
        "Queue": NotRequired[str],
        "Settings": NotRequired[JobTemplateSettingsTypeDef],
        "StatusUpdateInterval": NotRequired[StatusUpdateIntervalType],
    },
)
ListJobsResponsePaginatorTypeDef = TypedDict(
    "ListJobsResponsePaginatorTypeDef",
    {
        "Jobs": List[JobPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListJobTemplatesResponsePaginatorTypeDef = TypedDict(
    "ListJobTemplatesResponsePaginatorTypeDef",
    {
        "JobTemplates": List[JobTemplatePaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateJobResponseTypeDef = TypedDict(
    "CreateJobResponseTypeDef",
    {
        "Job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetJobResponseTypeDef = TypedDict(
    "GetJobResponseTypeDef",
    {
        "Job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListJobsResponseTypeDef = TypedDict(
    "ListJobsResponseTypeDef",
    {
        "Jobs": List[JobTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateJobTemplateResponseTypeDef = TypedDict(
    "CreateJobTemplateResponseTypeDef",
    {
        "JobTemplate": JobTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetJobTemplateResponseTypeDef = TypedDict(
    "GetJobTemplateResponseTypeDef",
    {
        "JobTemplate": JobTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListJobTemplatesResponseTypeDef = TypedDict(
    "ListJobTemplatesResponseTypeDef",
    {
        "JobTemplates": List[JobTemplateTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateJobTemplateResponseTypeDef = TypedDict(
    "UpdateJobTemplateResponseTypeDef",
    {
        "JobTemplate": JobTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

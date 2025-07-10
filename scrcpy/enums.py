# -*- coding: utf-8 -*-
from enum import Enum


class Helper:
    @classmethod
    def from_value(cls, value):
        if value is False:
            return False
        if value is None:
            return cls.DEFAULT  # NOQA
        try:
            return cls[value] # NOQA
        except ValueError:
            return cls.DEFAULT  # NOQA


class VideoCodec(Helper, Enum):
    DEFAULT = "h264"
    H264 = "h264"
    H265 = "h265"
    AV1 = "av1"


class AudioSource(Helper, Enum):
    DEFAULT = "output"  # Forwards whole output, disables playback
    OUTPUT = "output"
    PLAYBACK = "playback"

    MIC = "mic"
    MIC_UNPROCESSED = "mic-unprocessed"
    MIC_CAMCORDER = "mic-camcorder"
    MIC_VOICE_RECOGNITION = "mic-voice-recognition"
    MIC_VOICE_COMMUNICATION = "mic-voice-communication"

    VOICE_CALL = "voice-call"
    VOICE_CALL_UPLINK = "voice-call-uplink"
    VOICE_CALL_DOWNLINK = "voice-call-downlink"
    VOICE_PERFORMANCE = "voice-performance"


class AudioCodec(Helper, Enum):
    DEFAULT = "opus"
    OPUS = "opus"
    AAC = "aac"
    FLAC = "flac"
    RAW = "raw"


class Orientation(Helper, Enum):
    DEFAULT = "0"       # Natural orientation
    DEG_90 = "90"
    DEG_180 = "180"
    DEG_270 = "270"


class FlipOrientation(Helper, Enum):
    DEFAULT = "0"       # Natural orientation
    NORMAL = "0"
    FLIP_0 = "flip0"       # Horizontal flip
    FLIP_90 = "flip90"     # Horizontal flip + 90°
    FLIP_180 = "flip180"   # Vertical flip
    FLIP_270 = "flip270"   # Horizontal flip + 270°


class CameraSize(Helper, Enum):
    DEFAULT = "1920x1080"
    R_4032x3024 = "4032x3024"
    ULTRA_HD = "4032x3024"
    R_4032x2268 = "4032x2268"
    ULTRA_HD_17_9 = "4032x2268"
    R_4032x1816 = "4032x1816"
    ULTRA_HD_WIDE = "4032x1816"
    R_3840x2160 = "3840x2160"
    UHD_4K = "3840x2160"
    R_3648x2736 = "3648x2736"
    HIGH_RES = "3648x2736"
    R_3648x2052 = "3648x2052"
    R_3648x1640 = "3648x1640"
    R_3216x1808 = "3216x1808"
    R_3216x1448 = "3216x1448"
    R_3024x3024 = "3024x3024"
    SQUARE_3K = "3024x3024"
    R_2944x2208 = "2944x2208"
    R_2736x2736 = "2736x2736"
    SQUARE_2K = "2736x2736"
    R_2400x1080 = "2400x1080"
    FHD_PLUS = "2400x1080"
    R_2208x2208 = "2208x2208"
    R_1920x1440 = "1920x1440"
    FULL_HD_TALL = "1920x1440"
    R_1920x1080 = "1920x1080"
    FULL_HD = "1920x1080"
    R_1920x864 = "1920x864"
    FULL_HD_ULTRAWIDE = "1920x864"
    R_1440x1080 = "1440x1080"
    HD_TALL = "1440x1080"
    R_1280x720 = "1280x720"
    HD = "1280x720"
    R_1088x1088 = "1088x1088"
    SQUARE_HD = "1088x1088"
    R_960x720 = "960x720"
    MEDIUM = "960x720"
    R_720x480 = "720x480"
    SD_WIDE = "720x480"
    R_640x480 = "640x480"
    SD = "640x480"
    R_640x360 = "640x360"
    SD_ULTRAWIDE = "640x360"
    R_352x288 = "352x288"
    LOW_1 = "352x288"
    R_320x240 = "320x240"
    LOW_2 = "320x240"
    R_256x144 = "256x144"
    LOW_3 = "256x144"
    R_176x144 = "176x144"
    LOWEST = "176x144"


class Bitrate(Helper, Enum):
    DEFAULT = "8M"
    BR_64M = "64M"
    BR_32M = "32M"
    BR_16M = "16M"
    BR_8M = "8M"
    BR_4M = "4M"
    BR_2M = "2M"
    BR_1M = "1M"
    BR_512K = "512K"
    BR_256K = "256K"
    BR_128K = "128K"
    BR_64K = "64K"
    BR_32K = "32K"
    BR_16K = "16K"
    BR_8K = "8K"
    BR_4K = "4K"
    BR_2K = "2K"
    BR_1K = "1K"


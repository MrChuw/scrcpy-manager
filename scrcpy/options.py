# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from config import ScrcpyConfig


@dataclass
class ScrcpyOptions:
    def __init__(self, config: ScrcpyConfig):
        self.config = config
        self.options = self.generate_args()


    def generate_args(self) -> List[str]:
        args = []

        def append(flag, value=None):
            if value is True:
                args.append(flag)
            elif isinstance(value, Enum):
                args.extend([flag, value.value])
            elif value not in [None, False]:
                args.extend([flag, str(value)])

        # Device
        append("--stay-awake", self.config.Device.stay_awake)
        append("--turn-screen-off", self.config.Device.turn_screen_off)
        append("--show-touches", self.config.Device.show_touches)
        append("--power-off-on-close", self.config.Device.power_off_on_close)
        append("--no-power-on", self.config.Device.power_on_on_start)

        # Window
        append("--window-title", self.config.Window.title)
        append("--window-borderless", self.config.Window.borderless)
        append("--always-on-top", self.config.Window.always_on_top)
        append("--fullscreen", self.config.Window.fullscreen)
        append("--disable-screensaver", self.config.Window.disable_screensaver)
        append("--window-height", self.config.Window.height)
        append("--window-width", self.config.Window.width)

        # Video
        append("--max-size", self.config.Video.max_size)
        append("--video-bit-rate", self.config.Video.bitrate)
        append("--max-fps", self.config.Video.fps)
        append("--print-fps", self.config.Video.print_fps)
        append("--video-codec", self.config.Video.codec)
        append("--video-encoder", self.config.Video.encoder)
        append("--lock-video-orientation", self.config.Video.lock_orientation)
        append("--orientation", self.config.Video.orientation)
        append("--crop", self.config.Video.crop)
        append("--display-id", self.config.Video.display_id)
        append("--display-buffer", self.config.Video.display_buffer)
        append("--v4l2-buffer", self.config.Video.v4l2_buffer)
        append("--no-playback", self.config.Video.no_playback)
        append("--no-video", self.config.Video.no_video)

        # Audio
        if self.config.Audio.no_audio:
            append("--no-audio", self.config.Audio.no_audio)
        if not self.config.Audio.no_audio:
            append("--audio-source", self.config.Audio.source)
            append("--audio-codec", self.config.Audio.codec)
            append("--audio-encoder", self.config.Audio.encoder)
            append("--audio-bit-rate", self.config.Audio.bitrate)
            append("--audio-buffer", self.config.Audio.buffer)
            append("--no-audio-playback", self.config.Audio.no_playback)

        # Camera
        if self.config.Camera.as_video_output:
            append("--video-source", self.config.Camera.video_output)
            append("--camera-size", self.config.Camera.size)
            append("--camera-fps", self.config.Camera.fps)
            append("--v4l2-sink", self.config.Camera.v4l2_sink)

        # Mouse
        append("--no-mouse-hover", self.config.Mouse.no_mouse_hover)

        return args






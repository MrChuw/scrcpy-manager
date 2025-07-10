# -*- coding: utf-8 -*-
from scrcpy.enums import (AudioCodec, AudioSource, Bitrate, CameraSize, Orientation, VideoCodec)
import yaml
from pathlib import Path


class ScrcpyConfig:
    def __init__(self, path: Path = Path(__file__).parent / 'config.yml'):
        data = self.load_config(path)
        self.port = data.get("port", "5555")

        self.Window = self.WindowConfig(data.get("Window", {}))
        self.Device = self.DeviceConfig(data.get("Device", {}))
        self.Video = self.VideoConfig(data.get("Video", {}))
        self.Audio = self.AudioConfig(data.get("Audio", {}))
        self.Camera = self.CameraConfig(data.get("Camera", {}))
        self.Mouse = self.MouseConfig(data.get("Mouse", {}))
        self.App = self.AppConfig(data.get("App", {}))

    def load_config(self, path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data

    class DeviceConfig:
        def __init__(self, data: dict):
            self.stay_awake = data.get("stay_awake", True)
            self.turn_screen_off = data.get("turn_screen_off", False)
            self.show_touches = data.get("show_touches", False)
            self.power_off_on_close = data.get("power_off_on_close", False)
            self.power_on_on_start = data.get("power_on_on_start", False)

    Device: DeviceConfig

    class WindowConfig:
        def __init__(self, data: dict):
            self.title = data.get("title", False)
            self.borderless = data.get("borderless", False)
            self.always_on_top = data.get("always_on_top", False)
            self.fullscreen = data.get("fullscreen", False)
            self.disable_screensaver = data.get("disable_screensaver", False)
            self.width = data.get("width", False)
            self.height = data.get("height", False)

    Window: WindowConfig

    class VideoConfig:
        def __init__(self, data: dict):
            self.max_size = data.get("max_size", False)
            self.bitrate = Bitrate.from_value(data.get("bitrate"))
            self.fps = data.get("fps", False)
            self.print_fps = data.get("print_fps", False)
            self.codec = VideoCodec.from_value(data.get("codec"))
            self.encoder = data.get("encoder", False)
            self.lock_orientation = Orientation.from_value(data.get("lock_orientation"))
            self.orientation = Orientation.from_value(data.get("orientation"))
            self.crop = data.get("crop", False)
            self.display_id = data.get("display_id", False)
            self.display_buffer = data.get("display_buffer", False)
            self.v4l2_buffer = data.get("v4l2_buffer", False)
            self.no_playback = data.get("no_playback", False)
            self.no_video = data.get("no_video", False)

    Video: VideoConfig

    class AudioConfig:
        def __init__(self, data: dict):
            self.no_audio = data.get("no_audio", True)
            self.source = AudioSource.from_value(data.get("source"))
            self.codec = AudioCodec.from_value(data.get("codec"))
            self.encoder = data.get("encoder", False)
            self.bitrate = data.get("bitrate", False)
            self.buffer = data.get("buffer", False)
            self.no_playback = data.get("no_playback", False)

    Audio: AudioConfig

    class CameraConfig:
        def __init__(self, data: dict):
            self.as_video_output = data.get("as_video_output", False)
            self.video_output = data.get("video_output", False)
            self.size = CameraSize.FULL_HD
            self.fps = data.get("fps", False)
            self.v4l2_sink = data.get("v4l2_sink", False)

    Camera: CameraConfig

    class MouseConfig:
        def __init__(self, data: dict):
            self.no_mouse_hover = data.get("no_mouse_hover", False)

    Mouse: MouseConfig

    class AppConfig:
        def __init__(self, data: dict):
            apps_to_open: list[str] = data.get("apps_to_open", [])
            self.apps_to_open: dict[str, str] = {}
            for app in apps_to_open:
                app, alias = app.split(":")
                self.apps_to_open[alias] = app


    App: AppConfig


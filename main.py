# -*- coding: utf-8 -*-
from config import ScrcpyConfig
from scrcpy.options import ScrcpyOptions
from scrcpy.adb_utils import AdbUtils, ADBError
import re
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
import argparse
import re
import signal
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class Scrcpy:
    def __init__(self):
        self.args = None
        self.config = ScrcpyConfig()
        self.options = ScrcpyOptions(self.config)
        self.adb = AdbUtils()
        self.socket = ''
        self.windows: dict[str, subprocess.Popen | None] = {}
        self.running = True
        self.session = PromptSession(history=InMemoryHistory())
        signal.signal(signal.SIGINT, self._handle_exit)

    def _handle_exit(self, signum, frame):
        print("\nInterrupted! Cleaning up...")
        self.running = False
        self._cleanup()
        exit(0)

    def _cleanup(self):
        for name, proc in self.windows.items():
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        if self.adb:
            self.adb.disconnect()
            print("ADB disconnected.")

    def _parse_args(self):
        p = argparse.ArgumentParser(description="ADB over Wi-Fi utility")
        p.add_argument("--port", type=int, default=5555, help="ADB TCP port")
        p.add_argument("--config-dir", type=Path, default=Path(__file__).parent,
                       help="Directory to store last device info")
        return p.parse_args()

    def _connect_device(self, port, config_dir):
        self.adb = AdbUtils(port=port, config_dir=config_dir)
        serial = ''

        try:
            last_socket, _ = self.adb.load_last_device()
            if last_socket:
                print(f"Trying last known device {last_socket}...")
                if self.adb.connect_tcp(last_socket):
                    print("Reconnected to last known device!")
                    serial = last_socket
                else:
                    print("Could not reconnect, falling back to discovery.")

            if not serial:
                print("Discovering attached devices...")
                self.adb.kill_server()
                self.adb.disconnect()
                serial = self.adb.get_device_serial() or ''
                if not serial:
                    print("No Wi-Fi device detected, trying USB...")
                    serial = self.adb.check_usb_connection()
                    self.adb.tcpip()

            # Enable Wi-Fi and fetch IP
            self.adb.shell(serial, "svc wifi enable")
            ip = ''
            while not ip and self.running:
                out = self.adb.shell(serial, "ip -f inet addr show wlan0")
                m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", out)
                if m:
                    ip = m.group(1)
                else:
                    time.sleep(0.5)

            self.socket = f"{ip}:{port}"
            print(f"Connecting to {self.socket}...")
            if not self.adb.connect_tcp(self.socket):
                raise ADBError("Could not connect over TCP")
            print("Connected!")
            return serial

        except ADBError as e:
            print(f"Error during connection: {e}")
            self._handle_exit(None, None)

    def _wait_for_window(self, alias, timeout=5):
        print(f"Waiting up to {timeout}s for window '{alias}' to appear...")
        start = time.time()
        proc = self.windows.get(alias)
        while time.time() - start < timeout:
            if proc is None:
                break
            # if process exited early, no window
            if proc.poll() is not None:
                break
            # assume window is up if still running after half timeout
            if time.time() - start > (timeout / 2):
                break
            time.sleep(0.5)
        if proc is None or proc.poll() is not None:
            print(f"Window '{alias}' did not start within {timeout}s. You can retry manually.")
        else:
            print(f"Window '{alias}' should now be visible.")

    def _start_window(self, alias, target, serial, options):
        try:
            if alias == "Main":
                proc = self.adb.start(serial, options)
            else:
                proc = self.adb.start_app(serial, options, target, alias)
            self.windows[alias] = proc
            self._wait_for_window(alias, timeout=5)
        except Exception as e:
            print(f"Failed to start {alias}: {e}")
            self.windows[alias] = None

    def _launch_all(self, serial):
        apps = {'Main': None, **self.config.App.apps_to_open}
        opts = self.options.options
        with ThreadPoolExecutor() as execute:
            for alias, target in apps.items():
                execute.submit(self._start_window, alias, target, serial, opts)
        time.sleep(1)

    def _interactive_loop(self, serial):
        print("Type 'reload' to refresh config, 'all' to restart all windows, or window alias to restart one.")
        def build_map():
            return {alias.lower(): alias for alias in self.windows}
        connected = True

        while self.running:
            try:
                choice = self.session.prompt("Command: ", refresh_interval=5)
                # choice = input("Command: ")
            except (EOFError, KeyboardInterrupt):
                self._handle_exit(None, None)
            choice = choice.strip()
            lower_map = build_map()
            if choice.lower() == 'all':
                self._cleanup()
                self._launch_all(serial)
            elif choice.lower() == 'reload':
                print("Reloading configuration...")
                self.config = ScrcpyConfig()  # re-read config
                self.options.config = self.config
                self.options.generate_args()
                new_apps = set(self.config.App.apps_to_open)
                existing = set(self.windows)
                to_add = new_apps - existing
                for alias in to_add:
                    target = self.config.App.apps_to_open[alias]
                    self._start_window(alias, target, serial, self.options.options)
                print(f"Spawned new windows: {to_add}" if to_add else "No new apps to add.")
            elif choice.lower() == 'dc':
                connected = False
                print("Disconnecting ADB...")
                self._cleanup()
                self.adb.disconnect()
            elif choice.lower() == 'conn' and connected is False:
                print("Reconnecting and launching all windows...")
                serial = self._connect_device(self.args.port, self.args.config_dir)
                self.adb.save_last_device(self.socket)
                self._launch_all(serial)
            elif choice.lower() == 'conn' and connected is True:
                print("Command only available if adb is disconnected.")
            elif choice.lower() in lower_map:
                alias = lower_map[choice.lower()]
                print(f"Restarting window {choice}..." )
                proc = self.windows[alias]
                if proc:
                    proc.terminate()
                    try:
                        proc.wait(5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                target = None if alias == 'Main' else self.config.App.apps_to_open[alias]
                self._start_window(alias, target, serial, self.options.options)
            else:
                print(f"Unknown command or alias: {choice}" )

    def run(self):
        self.args = self._parse_args()
        serial = self._connect_device(self.args.port, self.args.config_dir)
        self.adb.save_last_device(self.socket)
        print(f"Launch options for all windows: {self.options.options}")

        self._launch_all(serial)
        self._interactive_loop(serial)


if __name__ == "__main__":
    Scrcpy().run()
















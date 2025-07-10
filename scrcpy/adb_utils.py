# -*- coding: utf-8 -*-
import shutil
import subprocess
import time
from pathlib import Path


class ADBHelper:
    def __init__(self):
        self.script_dir = Path(__file__).resolve().parent
        self.last_working_device_file = self.script_dir / "last_working_device.conf"
        self.debug_log_file = self.script_dir / "debug.log"
        self.usb_device_serial = None
        self.rooted = False
        self._check_adb_presence()
        self._init_logs()

    def _check_adb_presence(self):
        if not shutil.which("adb"):
            print(
                "Please install adb and/or add it to system PATH if downloaded as standalone binary"
            )
            exit(1)
        print(f"Running script from {self.script_dir}")

    def _init_logs(self):
        self.last_working_device_file.touch(exist_ok=True)
        self.debug_log_file.write_text("")  # empty the log

    def get_device_serial(self) -> str:
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.splitlines()
            for line in lines:
                if "device" in line and "." not in line:
                    parts = line.strip().split()
                    if parts and parts[1] == "device":
                        return parts[0]  # return serial number
        except subprocess.SubprocessError as e:
            print(f"Error running adb: {e}")
        return ""

    def check_usb_connection(self):
        print("DEBUG> killing adb server...")
        subprocess.run(
            ["adb", "kill-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        while not self.usb_device_serial:
            subprocess.run(
                ["adb", "usb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(2)
            self.usb_device_serial = self.get_device_serial()

            if self.usb_device_serial:
                device_name = self._get_device_name()
                print(f"\ndevice(s) connected via USB cable: {device_name}")
                print(f"usb_device_serial: {self.usb_device_serial}")
                break
            else:
                print(".", end="", flush=True)

    def _get_device_name(self) -> str:
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.splitlines()
            for line in lines:
                if "device" in line and "." not in line:
                    fields = line.strip().split()
                    for field in fields:
                        if field.startswith("model:"):
                            return field.split(":")[1]
        except subprocess.SubprocessError:
            return "Unknown"
        return "Unknown"

    def check_root(self, device_serial: str):
        print("Checking root...")
        try:
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "su", "--command", "id -u"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            elevated_uid = result.stdout.strip().replace("\r", "")
            if elevated_uid:
                print("Device is rooted. Moving on..\n")
                self.rooted = True
            else:
                print(
                    "Your device needs to be rooted for allowing permanent WiFi connectivity through ADB"
                )
                self.rooted = False
        except subprocess.SubprocessError:
            print("Root check failed or device not rooted.")
            self.rooted = False

        with open(self.debug_log_file, "a") as f:
            f.write(f"rooted={int(self.rooted)}\n")

    def start_wifi_connection(self) -> str:
        device_serial = self.get_device_serial()
        if not device_serial:
            raise RuntimeError("No device connected via USB.")

        subprocess.run(
            ["adb", "-s", device_serial, "shell", "svc", "wifi", "enable"],
            stdout=subprocess.DEVNULL,
        )

        wlan0_ip = ""
        while not wlan0_ip:
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "ip -f inet addr show wlan0"],
                capture_output=True,
                text=True,
            )
            lines = result.stdout.splitlines()
            for line in lines:
                if "inet" in line:
                    ip = line.strip().split()[1].split("/")[0]
                    wlan0_ip = ip
                    break
        print(f"WiFi IP: {wlan0_ip}")
        return wlan0_ip

    def set_last_working_device_info(self, device_serial: str):
        lines = [device_serial]

        props = {
            "Manufacturer": "ro.product.manufacturer",
            "Android Version": "ro.build.version.release",
            "SDK Version": "ro.build.version.sdk",
            "Product Name": "ro.product.name",
            "Model": "ro.product.model",
        }

        for label, prop in props.items():
            value = self._get_prop(device_serial, prop)
            lines.append(f"{label}: {value}")

        self.last_working_device_file.write_text("\n".join(lines))

    def _get_prop(self, device_serial: str, prop: str) -> str:
        try:
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "getprop", prop],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return "Unknown"

    def usb_connection(self, port: int = 5555):
        print("\n\n!!! READ CAREFULLY !!!\n")
        print("1. Plug in the USB cable and enable USB debugging.")
        print(
            "2. (Optional) Enable 'Disable adb authorization timeout' in Developer Options."
        )
        print(
            "3. When prompted, allow USB debugging on your device and check 'Always allow'.\n"
        )
        print(
            "Checking if USB cable is connected and USB debugging is enabled...\n......"
        )

        self.check_usb_connection()
        if not self.usb_device_serial:
            raise RuntimeError("No USB device detected.")

        device = self.usb_device_serial
        self.check_root(device)

        if not self.rooted:
            print("Device is not rooted. Using temporary TCP/IP method...")
            subprocess.run(["adb", "tcpip", str(port)])
            time.sleep(5)
        else:
            # Set adb tcp props persistently
            for prop in ["service.adb.tcp.port", "persist.adb.tcp.port"]:
                subprocess.run(
                    [
                        "adb",
                        "-s",
                        device,
                        "shell",
                        "su",
                        "--command",
                        f"setprop {prop} {port}",
                    ],
                    check=False,
                )
                value = subprocess.run(
                    [
                        "adb",
                        "-s",
                        device,
                        "shell",
                        "su",
                        "--command",
                        f"getprop {prop}",
                    ],
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                print(f"Property {prop} set to: {value}")

            print("Restarting adbd...")
            subprocess.run(
                [
                    "adb",
                    "-s",
                    device,
                    "shell",
                    "su",
                    "--command",
                    "stop adbd ; sleep 2 ; start adbd",
                ],
                check=False,
            )
            time.sleep(5)
            print("Restarted adbd")

        print("Attempting to start Wi-Fi on the device...")
        wlan0_ip = self.start_wifi_connection()
        socket = f"{wlan0_ip}:{port}"
        print(f"New socket: {socket}")

        result = subprocess.run(
            ["adb", "connect", socket], capture_output=True, text=True
        )
        status = result.stdout.strip()
        with open(self.debug_log_file, "a") as log:
            log.write(f"ADB connect status: {status}\n")

        if "cannot" in status:
            print("Could not connect via adb to WiFi device.")
            connected = False
        else:
            print("Connecting via WiFi succeeded!")
            subprocess.run(["adb", "connect", socket])
            self.set_last_working_device_info(device_serial=socket)
            print("Device ready!")
            connected = True

        with open(self.debug_log_file, "a") as log:
            log.write(f"connected={str(connected).lower()}\n")

        return connected

    def success_message(self):
        print("######################################")
        print("You may unplug the USB cable if previously inserted.")
        print("Enjoy a smooth wireless experience!")
        print("######################################\n")

    def print_connections(self, port: int = 5555):
        socket = None
        connections = None

        try:
            output = subprocess.run(
                ["adb", "devices", "-l"], capture_output=True, text=True, check=True
            ).stdout

            for line in output.splitlines():
                if "device" in line and str(port) in line:
                    socket = line.split()[0]
                    break

            if not socket:
                print("No active device found using TCP on the given port.")
                return

            while not connections:
                result = subprocess.run(
                    ["adb", "-s", socket, "shell", f"netstat -tupna | grep {port}"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout.strip():
                    connections = result.stdout.strip()
                    print(f"Active connections on port {port}:\n{connections}")
                    break

                time.sleep(1)

        except subprocess.CalledProcessError as e:
            print(f"Error while checking connections: {e}")



class ADBError(Exception):
    pass


class AdbUtils:
    def __init__(self, port: int = 5555, config_dir: Path = Path(__file__).parent.parent):
        self.port = port
        self.config_dir = config_dir
        self.last_device_file = self.config_dir / 'last_working_device.conf'
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _run(self, args, capture_output=True, check=False):
        result = subprocess.run(["adb"] + args,
                                capture_output=capture_output,
                                text=True)
        if check and result.returncode != 0:
            raise ADBError(f"ADB command failed: {' '.join(args)} - {result.stderr}")
        return result.stdout.strip()

    def kill_server(self):
        self._run(["kill-server"], check=False)

    def usb(self):
        self._run(["usb"], check=False)

    def devices(self) -> str:
        return self._run(["devices", "-l"], check=True)

    def get_device_serial(self) -> str:
        output = self.devices()
        for line in output.splitlines():
            if line.endswith("device") and "." not in line:
                return line.split()[0]
        return ""

    def check_usb_connection(self, timeout: int = 60) -> str:
        self.kill_server()
        serial = ""
        start = time.time()
        while not serial and time.time() - start < timeout:
            self.usb()
            time.sleep(2)
            serial = self.get_device_serial()
        if not serial:
            raise ADBError("No USB device found within timeout")
        return serial

    def connect_tcp(self, socket: str) -> bool:
        status = self._run(["connect", socket])
        return "cannot" not in status and "failed" not in status

    def disconnect(self):
        self._run(["disconnect"], check=False)

    def shell(self, serial: str, cmd: str) -> str:
        return self._run(["-s", serial, "shell", cmd], check=True)

    def tcpip(self):
        self._run(["tcpip", str(self.port)], check=True)

    def save_last_device(self, serial: str):
        properties = {
                'Manufacturer': self.shell(serial, "getprop ro.product.manufacturer"),
                'Android Version': self.shell(serial, "getprop ro.build.version.release"),
                'SDK Version': self.shell(serial, "getprop ro.build.version.sdk"),
                'Product Name': self.shell(serial, "getprop ro.product.name"),
                'Model': self.shell(serial, "getprop ro.product.model")
        }
        with open(self.last_device_file, 'w') as f:
            f.write(f"{serial}\n")
            for key, val in properties.items():
                f.write(f"{key}: {val}\n")

    def load_last_device(self) -> (str, dict):
        if not self.last_device_file.exists():
            return '', {}
        with open(self.last_device_file) as f:
            lines = [line.strip() for line in f if line.strip()]
        socket = lines[0]
        props = {}
        for line in lines[1:]:
            if ': ' in line:
                k, v = line.split(': ', 1)
                props[k] = v
        return socket, props

    @staticmethod
    def start(serial: str, options: str):
        cmd = f"scrcpy -s {serial} {' '.join(options)}"
        return subprocess.Popen(cmd, shell=True)

    @staticmethod
    def start_app(serial: str, options: str, app: str, name: str):
        cmd = f"scrcpy -s {serial} {' '.join(options)} --new-display --start-app={app} --window-title={name}"
        return subprocess.Popen(cmd, shell=True)

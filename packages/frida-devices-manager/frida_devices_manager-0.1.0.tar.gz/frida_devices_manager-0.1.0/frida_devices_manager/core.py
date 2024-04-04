import frida.core
import subprocess

from frida_devices_manager.constants import FRIDA_SERVER_PATH, LOCAL_FRIDA_SERVER_PATH


class Core:
    __frida_device: frida.core.Device

    def __init__(self, device: frida.core.Device):
        self.__frida_device = device

    def __eq__(self, other):
        if isinstance(other, str):
            return self.__frida_device.id == other
        elif isinstance(other, frida.core.Device):
            return self.__frida_device.id == other.id
        elif isinstance(other, Core):
            return self.__frida_device.id == other.__frida_device.id
        return NotImplemented

    def __ne__(self, other):
        equality_result = self.__eq__(other)
        if equality_result is NotImplemented:
            return NotImplemented
        return not equality_result

    def is_frida_running(self):
        try:
            frida.get_device(self.__frida_device.id)
            return True
        except frida.ServerNotRunningError:
            return False

    def is_frida_installed(self) -> bool:
        try:
            result = subprocess.check_output(
                ['adb', '-s', self.__frida_device.id, 'shell', 'if', '[', '-f',
                 f'{FRIDA_SERVER_PATH}/frida-server', ']', ';', 'then', 'echo', 'true',
                 ';', 'else', 'echo',
                 'false', ';', 'fi'], text=True
            )
            if 'true' in result:
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False

    def copy_frida_server_to_device(self):
        subprocess.run(
            ['adb', '-s', self.__frida_device.id, 'push',
             LOCAL_FRIDA_SERVER_PATH, FRIDA_SERVER_PATH]
        )

    def run_frida_server(self):
        subprocess.run(
            ['adb', '-s', self.__frida_device.id, 'shell',
             'nohup', f'{FRIDA_SERVER_PATH}/frida-server', '&']
        )

    @staticmethod
    def get_all_connected_devices() -> list['Core']:
        mngr = frida.get_device_manager()
        devices = mngr.enumerate_devices()
        connected_devices = [Core(device) for device in devices if
                             device.type in ["device", "usb"]]
        return connected_devices

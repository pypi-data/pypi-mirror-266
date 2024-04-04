import unittest
import frida
import subprocess
from unittest.mock import Mock
from frida_devices_manager.core import Core


class TestCore(unittest.TestCase):

    def setUp(self):
        self.device = Mock(spec=frida.core.Device)
        self.device.id = "12345"
        self.core = Core(self.device)

    def test_eq(self):
        other = Core(self.device)
        self.assertTrue(self.core.__eq__(other))

        other_str = "12345"
        self.assertTrue(self.core.__eq__(other_str))

        other = "56789"
        self.assertFalse(self.core.__eq__(other))

        other_device = Mock(spec=frida.core.Device)
        other_device.id = "56789"
        other = Core(other_device)
        self.assertFalse(self.core.__eq__(other))
        self.assertFalse(self.core.__eq__(other_device))

    def test_ne(self):
        other = Core(self.device)
        self.assertFalse(self.core.__ne__(other))

        other_str = "12345"
        self.assertFalse(self.core.__ne__(other_str))

        other = "56789"
        self.assertTrue(self.core.__ne__(other))

        other_device = Mock(spec=frida.core.Device)
        other_device.id = "56789"
        other = Core(other_device)
        self.assertTrue(self.core.__ne__(other))
        self.assertTrue(self.core.__ne__(other_device))

    def test_is_frida_running(self):
        frida.get_device = Mock(side_effect=frida.ServerNotRunningError)
        result = self.core.is_frida_running()
        self.assertFalse(result)

    def test_is_frida_installed(self):
        subprocess.check_output = Mock(return_value="true\n")
        result = self.core.is_frida_installed()
        self.assertTrue(result)

        subprocess.check_output = Mock(return_value="false\n")
        result = self.core.is_frida_installed()
        self.assertFalse(result)

        subprocess.check_output = Mock(
            side_effect=subprocess.CalledProcessError(-1, 'bogus')
        )
        result = self.core.is_frida_installed()
        self.assertFalse(result)

    def test_copy_frida_server_to_device(self):
        subprocess.run = Mock()
        self.core.copy_frida_server_to_device()
        subprocess.run.assert_called_once()

    def test_run_frida_server(self):
        subprocess.run = Mock()
        self.core.run_frida_server()
        subprocess.run.assert_called_once()

    def test_get_all_connected_devices(self):
        device1 = Mock(spec=frida.core.Device)
        device1.type = "device"
        device2 = Mock(spec=frida.core.Device)
        device2.type = "usb"
        device_list = [device1, device2]
        frida.get_device_manager = Mock(
            return_value=Mock(enumerate_devices=Mock(return_value=device_list))
        )
        result = Core.get_all_connected_devices()
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()

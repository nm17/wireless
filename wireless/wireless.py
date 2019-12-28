import subprocess
from abc import ABCMeta, abstractmethod

from packaging import version

from wireless.drivers.linux.nmcli_new import Nmcli0990Wireless
from wireless.drivers.linux.nmcli_old import NmcliWireless
from wireless.drivers.linux.wpa_supplicant import WPASupplicantWireless
from wireless.drivers.osx.network_setup import NetworksetupWireless


def cmd(cmd):
    return (
        subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        .stdout.read()
        .decode()
    )


# abstracts away wireless connection
class Wireless:
    _driver_name = None
    _driver = None

    # init
    def __init__(self, interface=None):
        # detect and init appropriate driver
        self._driver_name = self._detectDriver()
        if self._driver_name == "nmcli":
            self._driver = NmcliWireless(interface=interface)
        elif self._driver_name == "nmcli0990":
            self._driver = Nmcli0990Wireless(interface=interface)
        elif self._driver_name == "wpa_supplicant":
            self._driver = WPASupplicantWireless(interface=interface)
        elif self._driver_name == "networksetup":
            self._driver = NetworksetupWireless(interface=interface)

        # attempt to auto detect the interface if none was provided
        if self.interface() is None:
            interfaces = self.interfaces()
            if len(interfaces) > 0:
                self.interface(interfaces[0])

        # raise an error if there is still no interface defined
        if self.interface() is None:
            raise Exception("Unable to auto-detect the network interface.")

    def _detectDriver(self):
        # try nmcli (Ubuntu 14.04)
        response = cmd("which nmcli")
        if len(response) > 0 and "not found" not in response:
            response = cmd("nmcli --version")
            parts = response.split()
            ver = parts[-1]
            if version.parse(ver) > version.parse("0.9.9.0"):
                return "nmcli0990"
            else:
                return "nmcli"

        # try nmcli (Ubuntu w/o network-manager)
        response = cmd("which wpa_supplicant")
        if len(response) > 0 and "not found" not in response:
            return "wpa_supplicant"

        # try networksetup (Mac OS 10.10)
        response = cmd("which networksetup")
        if len(response) > 0 and "not found" not in response:
            return "networksetup"

        raise Exception("Unable to find compatible wireless driver.")

    # connect to a network
    def connect(self, ssid, password):
        return self._driver.connect(ssid, password)

    # return the ssid of the current network
    def current(self):
        return self._driver.current()

    # return a list of wireless adapters
    def interfaces(self):
        return self._driver.interfaces()

    # return the current wireless adapter
    def interface(self, interface=None):
        return self._driver.interface(interface)

    # return the current wireless adapter
    def power(self, power=None):
        return self._driver.power(power)

    # return the driver name
    def driver(self):
        return self._driver_name


# abstract class for all wireless drivers
class WirelessDriver:
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self, ssid, password):
        pass

    @abstractmethod
    def current(self):
        pass

    @abstractmethod
    def interfaces(self):
        pass

    @abstractmethod
    def interface(self, interface=None):
        pass

    @abstractmethod
    def power(self, power=None):
        pass

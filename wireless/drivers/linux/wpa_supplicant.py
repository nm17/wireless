import re
from time import sleep

from wireless.wireless import WirelessDriver, cmd


class WPASupplicantWireless(WirelessDriver):
    _file = "/tmp/wpa_supplicant.conf"
    _interface = None

    # init
    def __init__(self, interface=None):
        self.interface(interface)

    # connect to a network
    def connect(self, ssid, password):
        # attempt to stop any active wpa_supplicant instances
        # ideally we do this just for the interface we care about
        cmd("sudo killall wpa_supplicant")

        # don't do DHCP for GoPros; can cause dropouts with the server
        cmd("sudo ifconfig {} 10.5.5.10/24 up".format(self._interface))

        # create configuration file
        f = open(self._file, "w")
        f.write('network={{\n    ssid="{}"\n    psk="{}"\n}}\n'.format(ssid, password))
        f.close()

        # attempt to connect
        cmd("sudo wpa_supplicant -i{} -c{} -B".format(self._interface, self._file))

        # check that the connection was successful
        # i've never seen it take more than 3 seconds for the link to establish
        sleep(5)
        if self.current() != ssid:
            return False

        # attempt to grab an IP
        # better hope we are connected because the timeout here is really long
        # cmd('sudo dhclient {}'.format(self._interface))

        # parse response
        return True

    # returned the ssid of the current network
    def current(self):
        # get interface status
        response = cmd("iwconfig {}".format(self.interface()))

        # the current network is on the first line.
        # ex: wlan0     IEEE 802.11AC  ESSID:"SSID"  Nickname:"<WIFI@REALTEK>"
        line = response.splitlines()[0]
        match = re.search('ESSID:"(.+?)"', line)
        if match is not None:
            network = match.group(1)
            if network != "off/any":
                return network

        # return none if there was not an active connection
        return None

    # return a list of wireless adapters
    def interfaces(self):
        # grab list of interfaces
        response = cmd("iwconfig")

        # parse response
        interfaces = []
        for line in response.splitlines():
            if len(line) > 0 and not line.startswith(" "):
                # this line contains an interface name!
                if "no wireless extensions" not in line:
                    # this is a wireless interface
                    interfaces.append(line.split()[0])

        # return list
        return interfaces

    # return the current wireless adapter
    def interface(self, interface=None):
        if interface is not None:
            self._interface = interface
        else:
            return self._interface

    # enable/disable wireless networking
    def power(self, power=None):
        # not supported yet
        return None

from wireless.wireless import WirelessDriver, cmd


class NetworksetupWireless(WirelessDriver):
    _interface = None

    # init
    def __init__(self, interface=None):
        self.interface(interface)

    # connect to a network
    def connect(self, ssid, password):
        # attempt to connect
        response = cmd(
            "networksetup -setairportnetwork {} {} {}".format(
                self._interface, ssid, password
            )
        )

        # parse response - assume success when there is no response
        return len(response) == 0

    # returned the ssid of the current network
    def current(self):
        # attempt to get current network
        response = cmd("networksetup -getairportnetwork {}".format(self._interface))

        # parse response
        phrase = "Current Wi-Fi Network: "
        if phrase in response:
            return response.replace("Current Wi-Fi Network: ", "").strip()
        else:
            return None

    # return a list of wireless adapters
    def interfaces(self):
        # grab list of interfaces
        response = cmd("networksetup -listallhardwareports")

        # parse response
        interfaces = []
        detectedWifi = False
        for line in response.splitlines():
            if detectedWifi:
                # this line has our interface name in it
                interfaces.append(line.replace("Device: ", ""))
                detectedWifi = False
            else:
                # search for the line that has 'Wi-Fi' in it
                if "Wi-Fi" in line:
                    detectedWifi = True

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
        if power is True:
            cmd("networksetup -setairportpower {} on".format(self._interface))
        elif power is False:
            cmd("networksetup -setairportpower {} off".format(self._interface))
        else:
            response = cmd("networksetup -getairportpower {}".format(self._interface))
            return "On" in response

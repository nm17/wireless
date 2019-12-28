from wireless.wireless import WirelessDriver, cmd


class NmcliWireless(WirelessDriver):
    _interface = None

    # init
    def __init__(self, interface=None):
        self.interface(interface)

    # clean up connections where partial is part of the connection name
    # this is needed to prevent the following error after extended use:
    # 'maximum number of pending replies per connection has been reached'
    def _clean(self, partial):
        # list matching connections
        response = cmd('nmcli --fields UUID,NAME con list | grep {}'.format(
            partial))

        # delete all of the matching connections
        for line in response.splitlines():
            if len(line) > 0:
                uuid = line.split()[0]
                cmd('nmcli con delete uuid {}'.format(uuid))

    # ignore warnings in nmcli output
    # sometimes there are warnings but we connected just fine
    def _errorInResponse(self, response):
        # no error if no response
        if len(response) == 0:
            return False

        # loop through each line
        for line in response.splitlines():
            # all error lines start with 'Error'
            if line.startswith('Error'):
                return True

        # if we didn't find an error then we are in the clear
        return False

    # connect to a network
    def connect(self, ssid, password):
        # clean up previous connection
        self._clean(self.current())

        # attempt to connect
        response = cmd('nmcli dev wifi connect {} password {} iface {}'.format(
            ssid, password, self._interface))

        # parse response
        return not self._errorInResponse(response)

    # returned the ssid of the current network
    def current(self):
        # list active connections for all interfaces
        response = cmd('nmcli con status | grep {}'.format(
            self.interface()))

        # the current network is in the first column
        for line in response.splitlines():
            if len(line) > 0:
                return line.split()[0]

        # return none if there was not an active connection
        return None

    # return a list of wireless adapters
    def interfaces(self):
        # grab list of interfaces
        response = cmd('nmcli dev')

        # parse response
        interfaces = []
        for line in response.splitlines():
            if 'wireless' in line:
                # this line has our interface name in the first column
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
        if power is True:
            cmd('nmcli nm wifi on')
        elif power is False:
            cmd('nmcli nm wifi off')
        else:
            response = cmd('nmcli nm wifi')
            return 'enabled' in response
# -*- coding: utf-8 -*-
import logging
import platform
import socket

import netifaces
import ping
import requests

from leap.base import constants
from leap.base import exceptions

logger = logging.getLogger(name=__name__)

#EVENTS OF NOTE
EVENT_CONNECT_REFUSED = "[ECONNREFUSED]: Connection refused (code=111)"


class LeapNetworkChecker(object):
    """
    all network related checks
    """
    def __init__(self, *args, **kwargs):
        provider_gw = kwargs.pop('provider_gw', None)
        self.provider_gateway = provider_gw

    def run_all(self, checker=None):
        if not checker:
            checker = self
        #self.error = None  # ?

        # for MVS
        checker.check_tunnel_default_interface()
        checker.check_internet_connection()
        checker.is_internet_up()

        if self.provider_gateway:
            checker.ping_gateway(self.provider_gateway)

        checker.parse_log_and_react([], ())

    def check_internet_connection(self):
        try:
            # XXX remove this hardcoded random ip
            # ping leap.se or eip provider instead...?
            requests.get('http://216.172.161.165')
        except requests.ConnectionError as e:
            error = "Unidentified Connection Error"
            if e.message == "[Errno 113] No route to host":
                if not self.is_internet_up():
                    error = "No valid internet connection found."
                else:
                    error = "Provider server appears to be down."
            logger.error(error)
            raise exceptions.NoInternetConnection(error)
        except (requests.HTTPError, requests.RequestException) as e:
            raise exceptions.NoInternetConnection(e.message)
        logger.debug('Network appears to be up.')

    def is_internet_up(self):
        iface, gateway = self.get_default_interface_gateway()
        try:
            self.ping_gateway(self.provider_gateway)
        except exceptions.NoConnectionToGateway:
            return False
        return True

    def check_tunnel_default_interface(self):
        """
        Raises an TunnelNotDefaultRouteError
        (including when no routes are present)
        """
        if not platform.system() == "Linux":
            raise NotImplementedError

        # XXX GET DARWIN IMPLEMENTATION

        f = open("/proc/net/route")
        route_table = f.readlines()
        f.close()
        #toss out header
        route_table.pop(0)

        if not route_table:
            raise exceptions.TunnelNotDefaultRouteError()

        line = route_table.pop(0)
        iface, destination = line.split('\t')[0:2]
        if not destination == '00000000' or not iface == 'tun0':
            raise exceptions.TunnelNotDefaultRouteError()

    def get_default_interface_gateway(self):
        """only impletemented for linux so far."""
        if not platform.system() == "Linux":
            raise NotImplementedError

        # XXX use psutil
        f = open("/proc/net/route")
        route_table = f.readlines()
        f.close()
        #toss out header
        route_table.pop(0)

        default_iface = None
        gateway = None
        while route_table:
            line = route_table.pop(0)
            iface, destination, gateway = line.split('\t')[0:3]
            if destination == '00000000':
                default_iface = iface
                break

        if not default_iface:
            raise exceptions.NoDefaultInterfaceFoundError

        if default_iface not in netifaces.interfaces():
            raise exceptions.InterfaceNotFoundError

        return default_iface, gateway

    def ping_gateway(self, gateway):
        # TODO: Discuss how much packet loss (%) is acceptable.

        # XXX -- validate gateway
        # -- is it a valid ip? (there's something in util)
        # -- is it a domain?
        # -- can we resolve? -- raise NoDNSError if not.

        # XXX -- needs review!
        # We cannout use this ping implementation; it needs root.
        # We need to look for another, poors-man implementation
        # or wrap around system traceroute (using sh module, fi)
        # -- kali
        packet_loss = ping.quiet_ping(gateway)[0]
        if packet_loss > constants.MAX_ICMP_PACKET_LOSS:
            raise exceptions.NoConnectionToGateway

    def check_name_resolution(self, domain_name):
        try:
            socket.gethostbyname(domain_name)
            return True
        except socket.gaierror:
            raise exceptions.CannotResolveDomainError

    def parse_log_and_react(self, log, error_matrix=None):
        """
        compares the recent openvpn status log to
        strings passed in and executes the callbacks passed in.
        @param log: openvpn log
        @type log: list of strings
        @param error_matrix: tuples of strings and tuples of callbacks
        @type error_matrix: tuples strings and call backs
        """
        for line in log:
            # we could compile a regex here to save some cycles up -- kali
            for each in error_matrix:
                error, callbacks = each
                if error in line:
                    for cb in callbacks:
                        if callable(cb):
                            cb()
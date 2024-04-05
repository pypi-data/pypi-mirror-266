#!/usr/bin/env python3
import grpc

from openobd_protocol import RemoteDiagnosticServices_pb2_grpc as grpcService
from openobd_protocol import ModuleConfiguration_pb2 as grpcModuleConfiguration
from openobd_protocol import BusConfiguration_pb2 as grpcBusConfiguration
from openobd_protocol import Status_pb2 as grpcStatus
from openobd_protocol.CAN import Isotp_pb2 as grpcIsotp
from openobd_protocol.CAN import CanServices_pb2_grpc as grpcCanService
from openobd_protocol.UserInterface import UserInterface_pb2 as grpcUserInterface
from openobd_protocol.UserInterface import UserInterfaceServices_pb2_grpc as grpcUserInterfaceService

from typing import Iterator


class OpenOBDClient(object):

    rest_api = None
    token = None

    """
    Client for gRPC functionality
    """
    def __init__(self, rest_api=None):
        rest_api = rest_api

    def connected(self):
        """Reports back if OpenOBD client is connected

        TODO: Write function
        """
        return True

    def __create_socket__(self):
        """REST API calls to create a socket and retrieve GRPC host and token"""

        # self.__connect_through_grpc__()

    def __connect_through_grpc__(self, grpc_host, grpc_port=443, token=token):
        self.token = token

        ''' Check if local grpc-proxy is running '''
        if grpc_port == 443:
            self.channel = grpc.secure_channel(grpc_host, grpc.ssl_channel_credentials())
        else:
            self.channel = grpc.insecure_channel('{}:{}'.format(grpc_host, grpc_port))

        '''
        Bind the openobd and the server
        '''
        self.rds = grpcService.RemoteDiagnosticServicesStub(self.channel)
        self.can = grpcCanService.CanServicesStub(self.channel)
        self.ui = grpcUserInterfaceService.UserInterfaceServicesStub(self.channel)

    def __metadata__(self):
        metadata = (("authorization", "Bearer {}".format(self.token)),)
        return metadata

    def request_module_configuration(self, module_configuration: grpcModuleConfiguration.ModuleConfiguration):
        """
        Client function to call the rpc for GetServerResponse
        """
        return self.rds.requestModuleConfiguration(request=module_configuration, metadata=self.__metadata__())

    def configure_bus(self, bus_configuration: grpcBusConfiguration.BusConfiguration) -> grpcStatus.Status:
        """
        Client function to call the rpc
        :param bus_configuration:
        :return: Status of the bus configuration request
        """
        return self.rds.configureBus(request=bus_configuration, metadata=self.__metadata__())

    def configure_buses(self, bus_configurations: Iterator[grpcBusConfiguration.BusConfiguration]) -> grpcStatus.Status:
        """
        client function to set up multiple buses
        :param bus_configurations: An iterator containing the buses that are requested to be set
        :return: Status of the bus configuration request
        """
        return self.rds.configureBuses(bus_configurations, metadata=self.__metadata__())

    def send_message(self, isotp_message: grpcIsotp.IsotpMessage) -> grpcIsotp.IsotpMessage:
        """
        client function to send and receive a single ISOTP format message
        :param isotp_message: The ISOTP message that is requested to be sent
        :return: An ISOTP response message
        """
        return self.can.send(isotp_message, metadata=self.__metadata__())

    def open_channel(self, isotp_messages: Iterator[grpcIsotp.IsotpMessage]) -> Iterator[grpcIsotp.IsotpMessage]:
        """
        Client function to send and receive a stream of ISOTP format messages
        :param isotp_messages: An iterator containing the ISOTP messages that are requested to be sent
        :return: A list of ISOTP response messages
        """
        return self.can.openChannel(isotp_messages, metadata=self.__metadata__())

    def attach_form(self, user_interface: grpcUserInterface.UserInterface) -> grpcStatus.Status:
        """
        Client function to initialize the user interface service
        :param user_interface: The user interface which is to be started
        :return: Status of the user interface request
        """
        return self.ui.attachForm(user_interface, metadata=self.__metadata__())

    def detach_form(self, user_interface: grpcUserInterface.UserInterface) -> grpcStatus.Status:
        """
        Client function to stop the user interface service
        :param user_interface: The user interface which is to be stopped
        :return: Status of the user interface request
        """
        return self.ui.detachForm(user_interface, metadata=self.__metadata__())

    def control(self, user_interface_messages: Iterator[grpcUserInterface.UserInterface]) -> grpcUserInterface.UserInterface:
        """
        Client function to control various components of the user interface
        :param user_interface_messages: An iterator containing the user interface message to be controlled
        :return: User interface component with output or answers depending upon the control fields sent
        """
        return self.ui.control(user_interface_messages, metadata=self.__metadata__())


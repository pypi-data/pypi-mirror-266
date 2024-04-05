# Copyright (c) 2024 Jifeline Networks B.V.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""OpenOBD Python Client implementiation"""

try:
    # pylint: disable=ungrouped-imports
    from openobd._metadata import __version__
except ImportError:
    __version__ = "dev0"

'''Import the message definitions from openobd_protocol '''
from openobd_protocol.ModuleConfiguration_pb2 import ModuleConfiguration, HardwareModule, Bitrate
from openobd_protocol.BusConfiguration_pb2 import *
from openobd_protocol.CAN.Isotp_pb2 import *
from openobd_protocol.UserInterface.UserInterface_pb2 import *
from openobd.openobdapi import OpenObdApi, OpenObdApiClientConfiguration

import traceback

AUTHENTICATION_TOKEN = None
GRPC_ENDPOINT = None

def openobd(incognito_api):
    pass


def openobd_rest(connection_uuid, provider_uuid, endpoint_url, api_key):
    global AUTHENTICATION_TOKEN, GRPC_ENDPOINT
    try:
        openobd_api = OpenObdApi(endpoint_url, api_key)
        response = openobd_api.get_openobd_credentials(connection_uuid, provider_uuid)
        body = response.json()
        try:
            AUTHENTICATION_TOKEN = body['session']['authentication_token']
            GRPC_ENDPOINT = body['session']['grpc_endpoint']
        except KeyError as kex:
            print("[!] No authentication token found: {}".format(kex))
            print("[i] Received status code: {}".format(body['status_code']))

        if AUTHENTICATION_TOKEN and GRPC_ENDPOINT:
            # now retrieve client
            return openobd_grpc(GRPC_ENDPOINT, AUTHENTICATION_TOKEN)
    except Exception as e:
        print("[!] [Warning] Unexpected exception occurred: {}".format(e))
        print(traceback.format_exc(e))



def openobd_grpc(grpc_host, token, grpc_port=443):
    """Creates a GRPC channel to a server.

    The returned Channel is thread-safe.

    Args:
      grpc_host: The GRPC server address.
      grpc_port: The GRPC server port (mostly 443).
      token: OpenOBD access token for the use of the service

    Returns:
      An openobd client.
    """
    from grpc import _channel  # pylint: disable=cyclic-import
    from grpc.experimental import _insecure_channel_credentials
    from openobd.openobdclient import OpenOBDClient

    client = OpenOBDClient()
    client.__connect_through_grpc__(grpc_host, grpc_port, token)

    return client

def openobd_on_connector(connector_uuid):
    pass


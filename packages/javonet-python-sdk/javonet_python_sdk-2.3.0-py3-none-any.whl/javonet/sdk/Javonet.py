"""
The Javonet module is a singleton module that serves as the entry point for interacting with Javonet.
It provides functions to activate and initialize the Javonet SDK.
It supports both in-memory and TCP connections.
Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/javonet-static-class>`_ for more information.
"""
from javonet.core.transmitter.PythonTransmitter import PythonTransmitter
from javonet.utils.ConnectionType import ConnectionType
from javonet.sdk.internal.RuntimeFactory import RuntimeFactory

PythonTransmitter.activate_with_licence_file()


def in_memory():
    """
    Initializes Javonet using an in-memory channel on the same machine.
    
    Returns:
        RuntimeFactory: An instance configured for an in-memory connection.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/in-memory-channel>`_ for more information.
    """
    connection_type = ConnectionType.InMemory
    return RuntimeFactory(connection_type)


def tcp(address):
    """
    Initializes Javonet with a TCP connection to a remote machine.
    
    Args:
        address (str): The address of the remote machine.
        
    Returns:
        RuntimeFactory: An instance configured for a TCP connection.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/tcp-channel>`_ for more information.
    """
    connection_type = ConnectionType.Tcp
    return RuntimeFactory(connection_type, address)


def activate(licence_key, proxy_host=None, proxy_user_name=None, proxy_user_password=None):
    """
    Activates Javonet with the provided license key and optional proxy settings.
    
    Args:
        licence_key (str): The license key to activate Javonet.
        proxy_host (str, optional): The host for the proxy server. Defaults to None.
        proxy_user_name (str, optional): The username for the proxy server. Defaults to None.
        proxy_user_password (str, optional): The password for the proxy server. Defaults to None.
        
    Returns:
        int: The activation status code.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/getting-started/activating-javonet>`_ for more information.
    """
    if proxy_host is None:
        return PythonTransmitter.activate_with_credentials(licence_key)
    else:
        if proxy_user_name is None:
            proxy_user_name = ""
        if proxy_user_password is None:
            proxy_user_password = ""

        return PythonTransmitter.activate_with_credentials_and_proxy(licence_key,
                                                                     proxy_user_name, proxy_user_password)

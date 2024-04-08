from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.ConnectionType import ConnectionType
from javonet.sdk.internal.RuntimeContext import RuntimeContext
from javonet.sdk.internal.abstract.AbstractRuntimeFactory import AbstractRuntimeFactory


class RuntimeFactory(AbstractRuntimeFactory):
    """
    The RuntimeFactory class implements the AbstractRuntimeFactory interface and provides methods for creating runtime contexts.
    Each method corresponds to a specific runtime (CLR, JVM, .NET Core, Perl, Ruby, Node.js, Python) and returns a RuntimeContext instance for that runtime.
    """

    def __init__(self, connection_type, tcp_address=None):
        self.connection_type = connection_type
        if connection_type is ConnectionType.Tcp:
            if tcp_address is None:
                raise Exception("Error tcp ip adress is not given!")
        self.tcp_address = tcp_address

    def clr(self):
        """
        Creates RuntimeContext instance to interact with CLR runtime.

        Returns:
            RuntimeContext instance for the CLR runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return RuntimeContext.get_instance(RuntimeName.clr, self.connection_type, self.tcp_address)

    def jvm(self):
        """
        Creates RuntimeContext instance to interact with JVM runtime.

        Returns:
            RuntimeContext instance for the JVM runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return RuntimeContext.get_instance(RuntimeName.jvm, self.connection_type, self.tcp_address)

    def netcore(self):
        """
        Creates RuntimeContext instance to interact with .NET Core runtime.

        Returns:
            RuntimeContext instance for the .NET Core runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return RuntimeContext.get_instance(RuntimeName.netcore, self.connection_type, self.tcp_address)

    def perl(self):
        """
        Creates RuntimeContext instance to interact with Perl runtime.

        Returns:
            RuntimeContext instance for the Perl runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return RuntimeContext.get_instance(RuntimeName.perl, self.connection_type, self.tcp_address)

    def ruby(self):
        """
        Creates RuntimeContext instance to interact with Ruby runtime.

        Returns:
            RuntimeContext instance for the Ruby runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return RuntimeContext.get_instance(RuntimeName.ruby, self.connection_type, self.tcp_address)

    def nodejs(self):
        """
        Creates RuntimeContext instance to interact with Node.js runtime.

        Returns:
            RuntimeContext instance for the Node.js runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return RuntimeContext.get_instance(RuntimeName.nodejs, self.connection_type, self.tcp_address)

    def python(self):
        """
        Creates RuntimeContext instance to interact with Python runtime.
        
        Returns:
            a RuntimeContext instance for the Python runtime
        
        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return RuntimeContext.get_instance(RuntimeName.python, self.connection_type, self.tcp_address)
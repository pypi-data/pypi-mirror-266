from javonet.utils.exception.ExceptionThrower import ExceptionThrower
from javonet.core.interpreter.Interpreter import Interpreter
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType

from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.ConnectionType import ConnectionType
from javonet.sdk.internal.InvocationContext import InvocationContext
from javonet.sdk.internal.abstract.AbstractTypeContext import AbstractTypeContext


class RuntimeContext(AbstractTypeContext):
    """
    Represents a single context which allows interaction with a selected technology.
    Refers to a single instance of the called runtime within a particular target OS process.
    This can be either the local currently running process (inMemory) or a particular remote process identified by the IP Address and PORT of the target Javonet instance.
    Multiple Runtime Contexts can be initialized within one process.
    Calling the same technology on inMemory communication channel will return the existing instance of runtime context.
    Calling the same technology on TCP channel but on different nodes will result in unique Runtime Contexts.
    Within the runtime context, any number of libraries can be loaded and any objects from the target technology can be interacted with, as they are aware of each other due to sharing the same memory space and same runtime instance.
    
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
    """

    __memory_runtime_contexts = dict()
    __network_runtime_contexts = dict()

    @staticmethod
    def get_instance(runtime_name: RuntimeName, connection_type: ConnectionType, tcp_address: str):
        if connection_type == ConnectionType.Tcp and tcp_address is not None:
            if tcp_address in RuntimeContext.__network_runtime_contexts:
                runtime_ctx = RuntimeContext.__network_runtime_contexts.get(tcp_address)
                runtime_ctx.current_command = None
                return runtime_ctx
            else:
                runtime_ctx = RuntimeContext(runtime_name, connection_type, tcp_address)
                RuntimeContext.__network_runtime_contexts[tcp_address] = runtime_ctx
                return runtime_ctx
        else:
            if runtime_name in RuntimeContext.__memory_runtime_contexts:
                runtime_ctx = RuntimeContext.__memory_runtime_contexts.get(runtime_name)
                runtime_ctx.current_command = None
                return runtime_ctx
            else:
                runtime_ctx = RuntimeContext(runtime_name, connection_type, "")
                RuntimeContext.__memory_runtime_contexts[runtime_name] = runtime_ctx
                return runtime_ctx

    def __init__(self, runtime_name: RuntimeName, connection_type: ConnectionType, tcp_address: str):
        self.__isExecuted = False
        self.__runtime_name = runtime_name
        self.__connection_type = connection_type
        self.__tcp_ip_address = tcp_address
        self.__python_interpreter = Interpreter()
        self.__current_command = None
        self.__response_command = None

    def execute(self):
        """
        Executes the current command. The initial state of RuntimeContext is non-materialized, 
        wrapping either a single command or a chain of recursively nested commands.
        Commands become nested through each invocation of methods on RuntimeContext.
        Each invocation triggers the creation of a new RuntimeContext instance wrapping the current command with a new parent command.
        The developer can decide at any moment of the materialization for the context, taking full control of the chunks of the expression being transferred and processed on the target runtime.

        Raises:
            Exception: If the command results in an exception.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/execute-method>`_ for more information.
        """

        self.__response_command = self.__python_interpreter.execute(self.__current_command, self.__connection_type,
                                                                    self.__tcp_ip_address)
        self.__current_command = None
        self.__isExecuted = True
        if self.__response_command.command_type == CommandType.Exception:
            raise ExceptionThrower.throw_exception(self.__response_command)

    def load_library(self, library_path: str):
        """
        Adds a reference to a library. This method allows you to use any library from all supported technologies. 
        The necessary libraries need to be referenced. The argument is a relative or full path to the library. 
        If the library has dependencies on other libraries, the latter needs to be added first.
        After referencing the library, any objects stored in this package can be used. 
        Use static classes, create instances, call methods, use fields and properties, and much more.

        Args:
            library_path (str): The relative or full path to the library.

        Returns:
            RuntimeContext: A RuntimeContext instance with loaded library from called runtime.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/getting-started/adding-references-to-libraries>`_ for more information.
        """
        local_command = Command(self.__runtime_name, CommandType.LoadLibrary, [library_path])
        self.__current_command = self.__build_command(local_command)
        self.execute()
        return self

    def get_type(self, type_name: str, *args):
        """
        Retrieves a reference to a specific type. The type can be a class, interface or enum. 
        The type can be retrieved from any referenced library.
    
        Args:
            type_name (str): The name of the type.
            *args: The optional generic type arguments.
    
        Returns:
            InvocationContext: The InvocationContext instance that wraps the command to get the type.
        """
        local_command = Command(self.__runtime_name, CommandType.GetType, [type_name, *args])
        self.__current_command = None
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def cast(self, *args):
        """
        Casts the provided value to a specific type. This method is used when invoking methods that require specific types of arguments.
        The arguments include the target type and the value to be cast. The target type must be retrieved from the called runtime using the getType method.
        After casting the value, it can be used as an argument when invoking methods.

        Args:
            *args: The target type and the value to be cast.

        Returns:
            InvocationContext: The InvocationContext that wraps the command to cast the value to a specific type.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/casting/casting>`_ for more information.
        """
        local_command = Command(self.__runtime_name, CommandType.Cast, [*args])
        self.__current_command = None
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def get_enum_item(self, *args):
        """
        Retrieves a specific item from an enum type. This method is used when working with enums from the called runtime.
        The arguments include the enum type and the name of the item. The enum type must be retrieved from the called runtime using the getType method.
        After retrieving the item, it can be used as an argument when invoking methods or for other operations.

        Args:
            *args: The enum type and the name of the item.

        Returns:
            InvocationContext: The InvocationContext instance that wraps the command to get the enum item.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/enums/using-enum-type>`_ for more information.
        """
        local_command = Command(self.__runtime_name, CommandType.GetEnumItem, [*args])
        self.__current_command = None
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def as_out(self, *args):
        """
        Creates a reference type argument that can be passed to a method with an out parameter modifier. 
        This method is used when working with methods from the called runtime that require arguments to be passed by reference.
        The arguments include the value and optionally the type of the reference. The type must be retrieved from the called runtime using the getType method.
        After creating the reference, it can be used as an argument when invoking methods.

        Args:
            *args: The value and optionally the type of the out parameter.

        Returns:
            InvocationContext: The InvocationContext instance that wraps the command to create a reference type argument.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/methods-arguments/passing-arguments-by-reference-with-out-keyword>`_ for more information.
        """
        local_command = Command(self.__runtime_name, CommandType.AsOut, [*args])
        self.__current_command = None
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def as_ref(self, *args):
        """
        Creates a reference type argument that can be passed to a method with a ref parameter modifier. 
        This method is used when working with methods from the called runtime that require arguments to be passed by reference.
        The arguments include the value and optionally the type of the reference. The type must be retrieved from the called runtime using the getType method.
        After creating the reference, it can be used as an argument when invoking methods.
    
        Args:
            *args: The value and optionally the type of the ref parameter.
    
        Returns:
            InvocationContext: The InvocationContext instance that wraps the command to create a reference type argument.
    
        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/methods-arguments/passing-arguments-by-reference-with-ref-keyword>`_ for more information.
        """
        local_command = Command(self.__runtime_name, CommandType.AsRef, [*args])
        self.__current_command = None
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def __build_command(self, command):
        for i in range(len(command.payload)):
            command.payload[i] = self.__encapsulate_payload_item(command.payload[i])

        return command.prepend_arg_to_payload(self.__current_command)

    # encapsulate payload item into command
    def __encapsulate_payload_item(self, payload_item):
        if isinstance(payload_item, Command):
            for i in range(len(payload_item.payload)):
                payload_item.payload[i] = self.__encapsulate_payload_item(payload_item.payload[i])
            return payload_item

        elif isinstance(payload_item, InvocationContext):
            return payload_item.get_current_command()

        elif isinstance(payload_item, list):
            for i in range(len(payload_item)):
                payload_item[i] = self.__encapsulate_payload_item(payload_item[i])
            return Command(self.__runtime_name, CommandType.Array, payload_item)

        else:
            return Command(self.__runtime_name, CommandType.Value, [payload_item])

    def __build_command(self, command):
        for i in range(len(command.payload)):
            command.payload[i] = self.__encapsulate_payload_item(command.payload[i])

        return command.prepend_arg_to_payload(self.__current_command)

    # encapsulate payload item into command
    def __encapsulate_payload_item(self, payload_item):
        if isinstance(payload_item, Command):
            for i in range(len(payload_item.payload)):
                payload_item.payload[i] = self.__encapsulate_payload_item(payload_item.payload[i])
            return payload_item

        elif isinstance(payload_item, InvocationContext):
            return payload_item.get_current_command()

        elif isinstance(payload_item, list):
            for i in range(len(payload_item)):
                payload_item[i] = self.__encapsulate_payload_item(payload_item[i])
            return Command(self.__runtime_name, CommandType.Array, payload_item)

        else:
            return Command(self.__runtime_name, CommandType.Value, [payload_item])

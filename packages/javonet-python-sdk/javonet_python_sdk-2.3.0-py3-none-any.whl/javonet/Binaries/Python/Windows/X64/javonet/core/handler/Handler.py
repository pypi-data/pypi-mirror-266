from javonet.core.handler.AbstractHandler import AbstractHandler
from javonet.core.handler.CommandHandler.ValueHandler import ValueHandler
from javonet.core.handler.CommandHandler.LoadLibraryHandler import LoadLibraryHandler
from javonet.core.handler.CommandHandler.InvokeStaticMethodHandler import InvokeStaticMethodHandler
from javonet.core.handler.CommandHandler.SetStaticFieldHandler import SetStaticFieldHandler
from javonet.core.handler.CommandHandler.CreateClassInstanceHandler import CreateClassInstanceHandler
from javonet.core.handler.CommandHandler.GetStaticFieldHandler import GetStaticFieldHandler
from javonet.core.handler.CommandHandler.ResolveInstanceHandler import ResolveInstanceHandler
from javonet.core.handler.CommandHandler.GetTypeHandler import GetTypeHandler
from javonet.core.handler.CommandHandler.InvokeInstanceMethodHandler import InvokeInstanceMethodHandler
from javonet.core.handler.CommandHandler.CastingHandler import CastingHandler
from javonet.core.handler.CommandHandler.GetInstanceFieldHandler import GetInstanceFieldHandler
from javonet.core.handler.CommandHandler.SetInstanceFieldHandler import SetInstanceFieldHandler
from javonet.core.handler.CommandHandler.DestructReferenceHandler import DestructReferenceHandler
from javonet.core.handler.CommandHandler.ArrayGetItemHandler import ArrayGetItemHandler
from javonet.core.handler.CommandHandler.ArrayGetSizeHandler import ArrayGetSizeHandler
from javonet.core.handler.CommandHandler.ArrayGetRankHandler import ArrayGetRankHandler
from javonet.core.handler.CommandHandler.ArraySetItemHandler import ArraySetItemHandler
from javonet.core.handler.CommandHandler.ArrayHandler import ArrayHandler
from javonet.core.handler.CommandHandler.GetEnumItemHandler import GetEnumItemHandler
from javonet.core.handler.CommandHandler.GetEnumNameHandler import GetEnumNameHandler
from javonet.core.handler.CommandHandler.GetEnumValueHandler import GetEnumValueHandler

from javonet.core.handler.HandlerDictionary import handler_dict
from javonet.core.handler.ReferencesCache import ReferencesCache
from javonet.utils.exception.ExceptionSerializer import ExceptionSerializer
from javonet.utils.CommandType import CommandType
from javonet.utils.Command import Command


class Handler(AbstractHandler):

    def __init__(self):

        handler_dict[CommandType.Value] = ValueHandler()
        handler_dict[CommandType.LoadLibrary] = LoadLibraryHandler()
        handler_dict[CommandType.InvokeStaticMethod] = InvokeStaticMethodHandler()
        handler_dict[CommandType.SetStaticField] = SetStaticFieldHandler()
        handler_dict[CommandType.CreateClassInstance] = CreateClassInstanceHandler()
        handler_dict[CommandType.GetStaticField] = GetStaticFieldHandler()
        handler_dict[CommandType.Reference] = ResolveInstanceHandler()
        handler_dict[CommandType.GetType] = GetTypeHandler()
        handler_dict[CommandType.InvokeInstanceMethod] = InvokeInstanceMethodHandler()
        handler_dict[CommandType.Cast] = CastingHandler()
        handler_dict[CommandType.GetInstanceField] = GetInstanceFieldHandler()
        handler_dict[CommandType.SetInstanceField] = SetInstanceFieldHandler()
        handler_dict[CommandType.DestructReference] = DestructReferenceHandler()
        handler_dict[CommandType.ArrayGetItem] = ArrayGetItemHandler()
        handler_dict[CommandType.ArrayGetSize] = ArrayGetSizeHandler()
        handler_dict[CommandType.ArrayGetRank] = ArrayGetRankHandler()
        handler_dict[CommandType.ArraySetItem] = ArraySetItemHandler()
        handler_dict[CommandType.Array] = ArrayHandler()
        handler_dict[CommandType.GetEnumItem] = GetEnumItemHandler()
        handler_dict[CommandType.GetEnumName] = GetEnumNameHandler()
        handler_dict[CommandType.GetEnumValue] = GetEnumValueHandler()


    def handle_command(self, command):
        try:
            if command.command_type == CommandType.RetrieveArray:
                response_array = handler_dict[CommandType.Reference].handle_command(command.payload[0])
                return Command.create_array_response(response_array, command.runtime_name)

            response = handler_dict.get(command.command_type).handle_command(command)
            return self.__parse_response(response, command.runtime_name)
        except Exception as e:
            return ExceptionSerializer.serialize_exception(e, command)

    def __parse_response(self, response, runtime_name):
        if self.__is_response_simple_type(response):
            return Command.create_response(response, runtime_name)
        else:
            reference_cache = ReferencesCache()
            guid = reference_cache.cache_reference(response)
            return Command.create_reference(guid, runtime_name)

    @staticmethod
    def __is_response_simple_type(response):
        return isinstance(response, (int, float, bool, str))

    @staticmethod
    def __is_response_array(response):
        return isinstance(response, list);

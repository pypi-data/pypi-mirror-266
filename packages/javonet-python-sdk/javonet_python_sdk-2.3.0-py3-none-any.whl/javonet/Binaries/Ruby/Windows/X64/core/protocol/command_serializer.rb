require_relative 'type_serializer'
require_relative '../../utils/connection_type'
require_relative '../../utils/runtime_name'

class CommandSerializer

  def initialize
    @byte_buffer = []
  end

  def serialize(root_command, connection_type = ConnectionType::IN_MEMORY, tcp_address = nil, runtime_version = 0)
    queue = []
    queue.unshift(root_command)
    self.insert_into_buffer([root_command.runtime_name, runtime_version])
    if connection_type == ConnectionType::TCP
      self.insert_into_buffer([ConnectionType::TCP])
      self.insert_into_buffer(self.serialize_tcp(tcp_address))
    end
    if connection_type == ConnectionType::IN_MEMORY
      self.insert_into_buffer([ConnectionType::IN_MEMORY])
      self.insert_into_buffer([0, 0, 0, 0, 0, 0])
    end
    self.insert_into_buffer([RuntimeName::RUBY, root_command.command_type])
    self.serialize_recursively(queue)
  end

  def serialize_tcp(tcp_address)
    if tcp_address.kind_of?(Array)
      tcp_address
    else
      tcp_address_array = tcp_address.split(':')
      tcp_address_ip = tcp_address_array[0].split('.')
      tcp_address_port = tcp_address_array[1]
      tcp_address_bytearray = []
      tcp_address_ip.each { |address|
        tcp_address_bytearray.concat([address.to_i])
      }
      port_byte = [tcp_address_port.to_i].pack("s_").bytes
      tcp_address_bytearray.concat(port_byte)
      tcp_address_bytearray
    end

  end

  def serialize_primitive(payload_item)
    if [true, false].include? payload_item
      TypeSerializer.serialize_bool(payload_item)
    elsif payload_item.is_a? Integer
      if (-2 ** 31..2 ** 31).include?(payload_item)
        return TypeSerializer.serialize_int(payload_item)
      elsif (-2 ** 63..2 ** 63).include?(payload_item)
        return TypeSerializer.serialize_longlong(payload_item)
      else
        return TypeSerializer.serialize_ullong(payload_item)
      end
    elsif payload_item.is_a? String
      TypeSerializer.serialize_string(payload_item)
    elsif payload_item.is_a? Float
      TypeSerializer.serialize_double(payload_item)
    elsif payload_item.is_a?
    else
      raise Exception.new("Payload not supported in command serializer")
    end
  end

  def insert_into_buffer(arguments)
    @byte_buffer = @byte_buffer + arguments
  end

  def serialize_recursively(queue)
    if queue.length == 0
      return @byte_buffer
    end
    command = queue.shift
    queue.unshift(command.drop_first_payload_argument)
    if command.payload.length > 0
      if command.payload[0].is_a? Command
        inner_command = command.payload[0]
        self.insert_into_buffer(TypeSerializer.serialize_command(inner_command))
        queue.unshift(inner_command)
      else
        result = self.serialize_primitive(command.payload[0])
        self.insert_into_buffer(result)
        return self.serialize_recursively(queue)
      end
    else
      queue.shift
    end
    self.serialize_recursively(queue)
  end

end
const { Handler } = require('../handler/Handler')
const CommandSerializer = require('../protocol/CommandSerializer')
const CommandDeserializer = require('../protocol/CommandDeserializer')
const Runtime = require("../../utils/RuntimeName");

let Transmitter
let Receiver

class Interpreter {
    handler = new Handler()

    execute(command, connectionType, tcpAddress) {
        let commandSerializer = new CommandSerializer()
        let byteMessage = commandSerializer.serialize(command,connectionType, tcpAddress)
        let responseByteArray

        if (command.runtimeName === Runtime.Nodejs)
        {
            // lazy receiver loading
            if (!Receiver) {
                Receiver = require('../receiver/Receiver')
            }
            responseByteArray = Receiver.sendCommand(byteMessage)

        }
        else {
            // lazy transmitter loading
            if (!Transmitter) {
                Transmitter = require('../transmitter/Transmitter')
            }
            responseByteArray = Transmitter.sendCommand(byteMessage)
        }
        return new CommandDeserializer(responseByteArray).deserialize()
    }

    process(byteArray) {
        let commandDeserializer = new CommandDeserializer(byteArray)
        let receivedCommand = commandDeserializer.deserialize()
        let responseCommand = this.handler.handleCommand(receivedCommand)
        let commandSerializer = new CommandSerializer()
        return commandSerializer.serialize(responseCommand, 0, "0.0.0.0:0")
    }
}

module.exports = Interpreter

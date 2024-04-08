const Interpreter = require('../interpreter/Interpreter')
const interpreter = new Interpreter()

class Receiver {
    static sendCommand(byteArray) {
        return interpreter.process(byteArray)
    }
    static heartBeat(byteArray) {
        return Int8Array.from([49, 48])
    }
}

module.exports = Receiver

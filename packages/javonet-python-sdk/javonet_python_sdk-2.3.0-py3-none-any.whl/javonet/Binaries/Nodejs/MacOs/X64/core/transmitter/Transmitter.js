const wrapper = require('./TransmitterWrapper')

class Transmitter {

   static sendCommand(messageArray) {
        return wrapper.sendCommand(messageArray)
    }

    static #activate = function(licenceKey = "", proxyHost = "", proxyUserName="", proxyUserPassword="") {
        return wrapper.activate(licenceKey, proxyHost, proxyUserName, proxyUserPassword)
    }

    static activateWithLicenceFile() {
        return this.#activate()
    }

    static activateWithCredentials(licenceKey) {
        return this.#activate(licenceKey)
    }

    static activateWithCredentialsAndProxy(licenceKey, proxyHost, proxyUserName, proxyUserPassword) {
        return this.#activate(licenceKey, proxyHost, proxyUserName, proxyUserPassword)
    }
}

module.exports = Transmitter

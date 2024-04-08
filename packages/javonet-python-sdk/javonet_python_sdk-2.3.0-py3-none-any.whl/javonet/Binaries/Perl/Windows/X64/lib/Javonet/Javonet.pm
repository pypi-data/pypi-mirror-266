package Javonet::Javonet;
use strict;
use warnings FATAL => 'all';
use Moose;
use lib 'lib';
use aliased 'Javonet::Sdk::Internal::RuntimeFactory' => 'RuntimeFactory';
use aliased 'Javonet::Core::Transmitter::PerlTransmitter' => 'Transmitter', qw(activate_with_licence_file activate_with_credentials activate_with_credentials_and_proxy);

BEGIN {
    Transmitter->activate_with_licence_file()
}

sub activate {
    if(@_ == 1) {
        return Transmitter->activate_with_licence_file();
    }
    if(@_ == 2) {
        my($self, $licenceKey) = @_;
        return Transmitter->activate_with_credentials($licenceKey);
    } elsif (@_ > 2) {
        my($self, $licenceKey, $proxyHost, $proxyUserName, $proxyPassword) = @_;
        $proxyUserName //="";
        $proxyPassword //="";
        return Transmitter->activate_with_credentials_and_proxy($licenceKey, $proxyHost, $proxyUserName, $proxyPassword);
    }

}

sub in_memory {
    return RuntimeFactory->new(Javonet::Sdk::Internal::ConnectionType::get_connection_type('InMemory'));
}

sub tcp {
    # additional shift is needed to pass second argument
    my $class = shift;
    my $address = shift;
    return RuntimeFactory->new(Javonet::Sdk::Internal::ConnectionType::get_connection_type('Tcp'), $address);
}

1;
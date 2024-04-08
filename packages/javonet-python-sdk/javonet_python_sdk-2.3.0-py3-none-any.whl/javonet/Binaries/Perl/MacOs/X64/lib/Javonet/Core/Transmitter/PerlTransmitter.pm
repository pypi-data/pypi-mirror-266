package Javonet::Core::Transmitter::PerlTransmitter;
use strict;
use warnings;
use Cwd;
use aliased 'Javonet::Core::Transmitter::PerlTransmitterWrapper' => 'PerlTransmitterWrapper' , qw(send_command_ activate_);
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(send_command activate_with_licence_file activate_with_credentials activate_with_credentials_and_proxy);

sub send_command {
    my ($self, $message_ref) = @_;
    my @response = PerlTransmitterWrapper->send_command_($message_ref);
    return @response;
}

sub activate_with_licence_file {
    return __activate();
}

sub activate_with_credentials {
    my($self, $licenceKey) = @_;
    return __activate($licenceKey);
}

sub activate_with_credentials_and_proxy {
    my($self,  $licenceKey, $proxyHost, $proxyUserName, $proxyPassword) = @_;
    return __activate($licenceKey, $proxyHost, $proxyUserName, $proxyPassword);
}

sub __activate {
    my($licenceKey, $proxyHost, $proxyUserName, $proxyPassword) = @_;
    #set default values
    $licenceKey //="";
    $proxyHost //="";
    $proxyUserName //="";
    $proxyPassword //="";
    return PerlTransmitterWrapper->activate_($licenceKey, $proxyHost, $proxyUserName, $proxyPassword);
}

1;

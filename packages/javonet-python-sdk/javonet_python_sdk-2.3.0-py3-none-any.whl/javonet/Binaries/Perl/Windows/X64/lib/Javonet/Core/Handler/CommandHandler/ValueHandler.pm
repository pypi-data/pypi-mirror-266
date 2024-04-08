package Javonet::Core::Handler::CommandHandler::ValueHandler;
use aliased 'Javonet::Core::Handler::PerlHandler' => 'PerlHandler';
use strict;
use warnings FATAL => 'all';
use Moose;
use lib 'lib';
use Nice::Try;
use aliased 'Javonet::Core::Exception::Exception' => 'Exception';
extends 'Javonet::Core::Handler::CommandHandler::AbstractCommandHandler';

sub new {
    my $class = shift;
    my $self = {
        required_parameters_count => 1
    };
    return bless $self, $class;
}

sub process {
    my ($self, $command) = @_;
    try {
        return $command->{payload}[0];
    }
    catch ( $e ) {
        return Exception->new($e);
    }
}

no Moose;
1;

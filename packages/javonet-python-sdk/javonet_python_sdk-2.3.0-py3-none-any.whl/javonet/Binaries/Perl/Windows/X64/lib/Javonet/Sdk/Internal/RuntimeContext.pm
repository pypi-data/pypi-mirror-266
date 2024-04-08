package Javonet::Sdk::Internal::RuntimeContext;
use strict;
use warnings FATAL => 'all';
use Moose;
use aliased 'Javonet::Sdk::Core::PerlCommand' => 'PerlCommand';
use aliased 'Javonet::Sdk::Internal::InvocationContext' => 'InvocationContext';
use aliased 'Javonet::Core::Handler::PerlHandler' => 'PerlHandler';
use aliased 'Javonet::Core::Interpreter::Interpreter' => 'Interpreter', qw(execute_);
use aliased 'Javonet::Core::Exception::ExceptionThrower' => 'ExceptionThrower';

extends 'Javonet::Sdk::Internal::Abstract::AbstractModuleContext',
    'Javonet::Sdk::Internal::Abstract::AbstractTypeContext';

my $perl_handler = Javonet::Core::Handler::PerlHandler->new();
our %memoryRuntimeContexts;
our %networkRuntimeContexts;

#@override
sub new {
    my $class = shift;

    my $self = {
        runtime_lib     => shift,
        connection_type => shift,
        tcp_address     => shift,
        response_command => 0,
    };
    bless $self, $class;
    return $self;
}

sub get_instance {
    my $runtime_lib = shift;
    my $connection_type = shift;
    my $tcp_address = shift;
    if($connection_type eq Javonet::Sdk::Internal::ConnectionType::get_connection_type("Tcp") && $tcp_address ne "") {
        if(exists $networkRuntimeContexts{$tcp_address}) {
            my $runtimeCtx = $networkRuntimeContexts{$tcp_address};
            $runtimeCtx->{current_command} = undef();
            return $runtimeCtx;
        }
        else {
            my $runtimeCtx = Javonet::Sdk::Internal::RuntimeContext->new($runtime_lib, $connection_type, $tcp_address);
            $networkRuntimeContexts{$tcp_address} = $runtimeCtx;
            return($runtimeCtx);
        }
    }
    else {
        if(exists $memoryRuntimeContexts{$runtime_lib}) {
            my $runtimeCtx = $memoryRuntimeContexts{$runtime_lib};
            $runtimeCtx->{current_command} = undef();
            return $runtimeCtx;
        }
        else {
            my $runtimeCtx = Javonet::Sdk::Internal::RuntimeContext->new($runtime_lib, $connection_type, '');
            $memoryRuntimeContexts{$runtime_lib} = $runtimeCtx;
            return($runtimeCtx);
        }
    }
}


sub execute {
    my $self = $_[0];
    my $command = shift;
    my $connection_type = shift;
    my $tcp_address = shift;
    if($command->{runtime} eq Javonet::Sdk::Core::RuntimeLib::get_runtime('Perl')) {
        $self->{response_command} = $perl_handler->handle_command($command);
    } else {
        $self->{response_command} = Interpreter->execute_($command, $connection_type, $tcp_address);
    }
    if ($self->{response_command}->{command_type} == Javonet::Sdk::Core::PerlCommandType::get_command_type('Exception')) {
        ExceptionThrower->throwException($self->{response_command})
    }
}


#@override
sub load_library {
    my $self = shift;
    my @load_library_parameters = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('LoadLibrary'),
        payload => \@load_library_parameters
    );

    execute($command, $self->{connection_type}, $self->{tcp_address});
    return $self;
}

#@override
sub get_type {
    my $self = shift;
    my @arguments = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('GetType'),
        payload => \@arguments
    );

    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub cast {
    my $self = shift;
    my @arguments = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('Cast'),
        payload => \@arguments
    );

    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub get_enum_item {
    my $self = shift;
    my @arguments = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('GetEnumItem'),
        payload => \@arguments
    );

    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

sub as_out {
    my $self = shift;
    my @arguments = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('AsOut'),
        payload => \@arguments
    );

    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

sub as_ref {
    my $self = shift;
    my @arguments = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('AsRef'),
        payload => \@arguments
    );

    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub build_command {
    my ($self, $command) = @_;
    my $command_payload_length = @{$command->{payload}};
    for (my $i = 0; $i < $command_payload_length; $i++) {
        $command->{payload}[$i] = $self->encapsulate_payload_item($command->{payload}[$i]);
    }
    return $command->prepend_arg_to_payload($self->{current_command});
}

sub encapsulate_payload_item {
    my ($self, $payload_item) = @_;
    if ($payload_item->isa('Javonet::Sdk::Internal::InvocationContext')) {
        return $payload_item->get_current_command();
    } else {
        return $payload_item;
    }
}

no Moose;
1;
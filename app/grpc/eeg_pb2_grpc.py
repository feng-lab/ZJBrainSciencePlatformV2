# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from app.grpc import eeg_pb2 as app_dot_generated_dot_eeg__pb2


class EEGServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.displayEEG = channel.unary_unary(
            "/EEGService/displayEEG",
            request_serializer=app_dot_generated_dot_eeg__pb2.DisplayEEGRequest.SerializeToString,
            response_deserializer=app_dot_generated_dot_eeg__pb2.DisplayEEGResponse.FromString,
        )


class EEGServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def displayEEG(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_EEGServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "displayEEG": grpc.unary_unary_rpc_method_handler(
            servicer.displayEEG,
            request_deserializer=app_dot_generated_dot_eeg__pb2.DisplayEEGRequest.FromString,
            response_serializer=app_dot_generated_dot_eeg__pb2.DisplayEEGResponse.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler("EEGService", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class EEGService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def displayEEG(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/EEGService/displayEEG",
            app_dot_generated_dot_eeg__pb2.DisplayEEGRequest.SerializeToString,
            app_dot_generated_dot_eeg__pb2.DisplayEEGResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
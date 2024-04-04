# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from opus_protobuf import common_pb2 as opus__protobuf_dot_common__pb2
from opus_protobuf import payment_pb2 as opus__protobuf_dot_payment__pb2


class PaymentControllerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.HealthCheck = channel.unary_unary(
                '/payment.PaymentController/HealthCheck',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=opus__protobuf_dot_common__pb2.Health.FromString,
                )
        self.CreateStripeCustomer = channel.unary_unary(
                '/payment.PaymentController/CreateStripeCustomer',
                request_serializer=opus__protobuf_dot_payment__pb2.CreateStripeCustomerRequest.SerializeToString,
                response_deserializer=opus__protobuf_dot_common__pb2.Response.FromString,
                )


class PaymentControllerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def HealthCheck(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateStripeCustomer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PaymentControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'HealthCheck': grpc.unary_unary_rpc_method_handler(
                    servicer.HealthCheck,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=opus__protobuf_dot_common__pb2.Health.SerializeToString,
            ),
            'CreateStripeCustomer': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateStripeCustomer,
                    request_deserializer=opus__protobuf_dot_payment__pb2.CreateStripeCustomerRequest.FromString,
                    response_serializer=opus__protobuf_dot_common__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'payment.PaymentController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class PaymentController(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def HealthCheck(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/payment.PaymentController/HealthCheck',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            opus__protobuf_dot_common__pb2.Health.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateStripeCustomer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/payment.PaymentController/CreateStripeCustomer',
            opus__protobuf_dot_payment__pb2.CreateStripeCustomerRequest.SerializeToString,
            opus__protobuf_dot_common__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

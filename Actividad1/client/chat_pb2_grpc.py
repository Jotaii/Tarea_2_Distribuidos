# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import chat_pb2 as chat__pb2


class ChatStub(object):
  """Servicio de Chat para en envío y recepción de mensajes. 
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SendMsg = channel.unary_unary(
        '/grpc.Chat/SendMsg',
        request_serializer=chat__pb2.Msg.SerializeToString,
        response_deserializer=chat__pb2.Empty.FromString,
        )
    self.Channel = channel.unary_stream(
        '/grpc.Chat/Channel',
        request_serializer=chat__pb2.Empty.SerializeToString,
        response_deserializer=chat__pb2.Msg.FromString,
        )


class ChatServicer(object):
  """Servicio de Chat para en envío y recepción de mensajes. 
  """

  def SendMsg(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Channel(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ChatServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SendMsg': grpc.unary_unary_rpc_method_handler(
          servicer.SendMsg,
          request_deserializer=chat__pb2.Msg.FromString,
          response_serializer=chat__pb2.Empty.SerializeToString,
      ),
      'Channel': grpc.unary_stream_rpc_method_handler(
          servicer.Channel,
          request_deserializer=chat__pb2.Empty.FromString,
          response_serializer=chat__pb2.Msg.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'grpc.Chat', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class UsersStub(object):
  """Servicio de Usuarios para el administración de estos. 
  Permite la conexión de clientes al chat, obtención del listado
  de usuarios y la desconexión. 
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Join = channel.unary_unary(
        '/grpc.Users/Join',
        request_serializer=chat__pb2.User.SerializeToString,
        response_deserializer=chat__pb2.Response.FromString,
        )
    self.GetUsers = channel.unary_unary(
        '/grpc.Users/GetUsers',
        request_serializer=chat__pb2.Empty.SerializeToString,
        response_deserializer=chat__pb2.UsersListResponse.FromString,
        )
    self.Disconnect = channel.unary_unary(
        '/grpc.Users/Disconnect',
        request_serializer=chat__pb2.User.SerializeToString,
        response_deserializer=chat__pb2.Empty.FromString,
        )


class UsersServicer(object):
  """Servicio de Usuarios para el administración de estos. 
  Permite la conexión de clientes al chat, obtención del listado
  de usuarios y la desconexión. 
  """

  def Join(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetUsers(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Disconnect(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_UsersServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Join': grpc.unary_unary_rpc_method_handler(
          servicer.Join,
          request_deserializer=chat__pb2.User.FromString,
          response_serializer=chat__pb2.Response.SerializeToString,
      ),
      'GetUsers': grpc.unary_unary_rpc_method_handler(
          servicer.GetUsers,
          request_deserializer=chat__pb2.Empty.FromString,
          response_serializer=chat__pb2.UsersListResponse.SerializeToString,
      ),
      'Disconnect': grpc.unary_unary_rpc_method_handler(
          servicer.Disconnect,
          request_deserializer=chat__pb2.User.FromString,
          response_serializer=chat__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'grpc.Users', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class MessagesServiceStub(object):
  """Servicio de Almacenamiento de mensajes. Permite guardar temporalmente
  los mensajes y entregar una lista de estos al cliente que lo solicite. 
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SaveMessage = channel.unary_unary(
        '/grpc.MessagesService/SaveMessage',
        request_serializer=chat__pb2.Msg.SerializeToString,
        response_deserializer=chat__pb2.Empty.FromString,
        )
    self.GetAllMessages = channel.unary_unary(
        '/grpc.MessagesService/GetAllMessages',
        request_serializer=chat__pb2.User.SerializeToString,
        response_deserializer=chat__pb2.UserMessages.FromString,
        )


class MessagesServiceServicer(object):
  """Servicio de Almacenamiento de mensajes. Permite guardar temporalmente
  los mensajes y entregar una lista de estos al cliente que lo solicite. 
  """

  def SaveMessage(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetAllMessages(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_MessagesServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SaveMessage': grpc.unary_unary_rpc_method_handler(
          servicer.SaveMessage,
          request_deserializer=chat__pb2.Msg.FromString,
          response_serializer=chat__pb2.Empty.SerializeToString,
      ),
      'GetAllMessages': grpc.unary_unary_rpc_method_handler(
          servicer.GetAllMessages,
          request_deserializer=chat__pb2.User.FromString,
          response_serializer=chat__pb2.UserMessages.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'grpc.MessagesService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
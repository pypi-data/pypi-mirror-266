from esdbclient import EventStoreDBClient
from esdbclient.protos.Grpc.shared_pb2 import WrongExpectedVersion

e = EventStoreDBClient()
e.append_events
e.read_stream()
e.get_current_version

e.get_current_version

WrongExpectedVersion

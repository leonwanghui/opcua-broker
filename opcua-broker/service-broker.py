import argparse
import logging
import time

from flask import Flask
from openbrokerapi import api
from openbrokerapi.catalog import (
    ServicePlan,
    Schemas
)
from openbrokerapi.log_util import basic_config
from openbrokerapi.service_broker import (
    ServiceBroker,
    Service,
    ProvisionedServiceSpec,
    UpdateServiceSpec,
    Binding,
    DeprovisionServiceSpec,
    LastOperation,
    UnbindDetails,
    ProvisionDetails,
    UpdateDetails,
    BindDetails,
    DeprovisionDetails
)
from opcua import Client
from opcua import Node
from opcua import ua
from opcua.common.subscription import Subscription


class OpcuaServiceBroker(ServiceBroker):
    def __init__(self, args):
        self.url = args.url

    def catalog(self) -> Service:
        servers = []
        for server_edp in uadiscover(self.url):
            client = Client(server_edp.EndpointUrl)

            client.connect()
            try:
                node = client.get_root_node()
                print("Browsing node {0} at {1}\n".format(node, server_edp.EndpointUrl))

                children_nodes = []
                get_children_nodes(node, children_nodes)
                servers.append(dict(name=server_edp.Server.ApplicationName.to_string(), endpoint=server_edp.EndpointUrl, nodes=children_nodes))
            finally:
                client.disconnect()

        return Service(
            id='00000000-0000-0000-0000-000000000000',
            name='opcua',
            description='opcua transport service',
            bindable=False,
            plans=[
                ServicePlan(
                    id='00000000-0000-0000-0000-000000000000',
                    name='node',
                    description='opcua node service plan',
                    schemas=Schemas({'servers':servers}),
                ),
                ServicePlan(
                    id='00000000-0000-0000-0000-000000000000',
                    name='subscribtion',
                    description='opcua subscribtion service plan',
                    schemas=Schemas({'servers':servers}),
                ),
            ],
            tags=['node', 'subscribtion'],
            plan_updateable=True,
        )

    def provision(self, instance_id: str, service_details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        pass

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
        pass

    def deprovision(self, instance_id: str, details: DeprovisionDetails,
                    async_allowed: bool) -> DeprovisionServiceSpec:
        pass

    def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        pass

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        pass

    def last_operation(self, instance_id: str, operation_data: str) -> LastOperation:
        pass

def parse_args(parser):
    args = parser.parse_args()
    if args.url and '://' not in args.url:
        logging.info("Adding default scheme %s to URL %s", ua.OPC_TCP_SCHEME, args.url)
        args.url = ua.OPC_TCP_SCHEME + '://' + args.url
    return args

def get_children_nodes(node, children_nodes=[], depth=2, timeout:object=4):
    for leaf in node.get_children_descriptions():
        children_nodes.append(dict(NodeId=leaf.NodeId.to_string(), DisplayName=leaf.DisplayName.to_string(), BrowseName=leaf.BrowseName.to_string(), Depth=3-depth))
        if depth:
            get_children_nodes(Node(node.server, leaf.NodeId), children_nodes, depth - 1, timeout)

def uadiscover(url:object, timeout:object=4):
    client = Client(url, timeout=timeout)

    print("Performing discovery at {0}\n".format(url))
    return client.connect_and_get_server_endpoints()

def uasubscribe(url:object, nodeid:ua.NodeId, path:str, eventtype:str="datachange", timeout:object=4):
    client = Client(url, timeout=timeout)
    client.connect()
    try:
        node = client.get_node(nodeid)
        if path:
            path = path.split(",")
            if node.nodeid == ua.NodeId(84, 0) and path[0] == "0:Root":
                # let user specify root if not node given
                path = path[1:]
            node = node.get_child(path)

        handler = SubHandler()
        sub = client.create_subscription(500, handler)
        if eventtype == "datachange":
            sub.subscribe_data_change(node)
        else:
            sub.subscribe_events(node)
        print("Type Ctr-C to exit")
        while True:
            time.sleep(1)
    finally:
        client.disconnect()


class SubHandler(object):

    def datachange_notification(self, node, val, data):
        print("New data change event", node, val, data)

    def event_notification(self, event):
        print("New event", event)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p",
                        "--port",
                        default='http://0.0.0.0:5000',
                        help="Use '--port' option to specify the port for broker to listen on")
    parser.add_argument("-u",
                        "--url",
                        default='opu.tcp://localhost:4840',
                        required=True,
                        help="Use '--url' option to specify the client endpoint for broker to connect the backend")

    args = parse_args(parser)
    # start the server without authentication
    api.serve(OpcuaServiceBroker(args), None)

    app = Flask(__name__)
    app.run(args.api_server)

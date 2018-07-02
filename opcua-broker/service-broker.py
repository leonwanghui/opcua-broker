import argparse
import logging
import time
import handler

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


opcua_service_class_id = "00000000-0000-0000-0000-000000000000"
discovery_service_plan_id = "00000000-0000-0000-0000-000000000001"
node_management_service_plan_id = "00000000-0000-0000-0000-000000000002"


class OpcuaServiceBroker(ServiceBroker):
    def __init__(self, opcua_handler: handler.OpcuaHandler):
        self.opcua_handler = opcua_handler

    def catalog(self) -> Service:
        discovery_instance = {
            'create': {
                "parameters": {
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "properties": {
                        "discovery_url": {
                            "description": "The url of discovery server specified for provisioning discovery service instance.",
                            "type": "string"
                        }
                    }
                }
            }
        }
        node_instance = {
            'create': {
                "parameters": {
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "properties": {
                        "url": {
                            "description": "The url of opcua server specified for provisioning node management service instance.",
                            "type": "string"
                        },
                        "nodesToAdd": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "parentNodeId": {
                                        "description": "The parent node id specified for provisioning node management service instance.",
                                        "type": "number"
                                    },
                                    "referenceTypeId": {
                                        "description": "The reference type id specified for provisioning node management service instance.",
                                        "type": "number"
                                    },
                                    "requestedNewNodeId": {
                                        "description": "The requested new node id specified for provisioning node management service instance.",
                                        "type": "number"
                                    },
                                    "browseName": {
                                        "description": "The reference type id specified for provisioning node management service instance.",
                                        "type": "string"
                                    },
                                    "nodeClass": {
                                        "description": "The reference type id specified for provisioning node management service instance.",
                                        "type": "number"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        reference_instance = {
            'create': {
                "parameters": {
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "properties": {
                        "url": {
                            "description": "The url of opcua server specified for provisioning node management service instance.",
                            "type": "string"
                        },
                        "referencesToAdd": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sourceNodeId": {
                                        "description": "The source node id specified for provisioning node management service.",
                                        "type": "string"
                                    },
                                    "referenceTypeId": {
                                        "description": "The reference type id specified for provisioning node management service.",
                                        "type": "string"
                                    },
                                    "targetNodeId": {
                                        "description": "The target node id specified for provisioning node management service.",
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        return Service(
            id=opcua_service_class_id,
            name='opcua_service',
            description='opcua transport service',
            bindable=False,
            plans=[
                ServicePlan(
                    id=discovery_service_plan_id,
                    name='device_discovery',
                    description='opcua device discovery service plan',
                    bindable=True,
                    schemas=Schemas(service_instance=discovery_instance),
                ),
                ServicePlan(
                    id=node_management_service_plan_id,
                    name='node_management',
                    description='opcua device nodes management service plan',
                    schemas=Schemas(service_instance=node_instance),
                ),
                ServicePlan(
                    id='00000000-0000-0000-0000-000000000003',
                    name='reference_management',
                    description='opcua device node references management service plan',
                    schemas=Schemas(service_instance=reference_instance),
                ),
                ServicePlan(
                    id='00000000-0000-0000-0000-000000000004',
                    name='data_change',
                    description='opcua data change monitoring service plan',
                    bindable=True,
                ),
                ServicePlan(
                    id='00000000-0000-0000-0000-000000000005',
                    name='events',
                    description='opcua events monitoring service plan',
                    bindable=True,
                ),
            ],
            tags=['discovery', 'device_management', 'monitoring'],
            plan_updateable=True,
        )

    def provision(self, instance_id: str, service_details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        if service_details.plan_id == discovery_service_plan_id:
            return self.opcua_handler.provision_discovery_instance(instance_id=instance_id,
                                                                   service_id=service_details.service_id,
                                                                   plan_id=service_details.plan_id,
                                                                   parameters=service_details.parameters)
        elif service_details.plan_id == node_management_service_plan_id:
            return self.opcua_handler.provision_node_instance(instance_id=instance_id,
                                                              service_id=service_details.service_id,
                                                              plan_id=service_details.plan_id,
                                                              parameters=service_details.parameters)
        else:
            return ProvisionedServiceSpec(state="failed")

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
        pass

    def deprovision(self, instance_id: str, details: DeprovisionDetails,
                    async_allowed: bool) -> DeprovisionServiceSpec:
        if details.plan_id == discovery_service_plan_id:
            return self.opcua_handler.deprovision_discovery_instance(instance_id)
        elif details.plan_id == node_management_service_plan_id:
            return self.opcua_handler.deprovision_node_instance(instance_id)
        else:
            return DeprovisionServiceSpec(is_async=False)

    def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        return self.opcua_handler.bind_discovery_instance(instance_id=instance_id,
                                                          binding_id=binding_id,
                                                          service_id=details.service_id,
                                                          plan_id=details.plan_id,
                                                          bind_resource=details.bind_resource,
                                                          parameters=details.parameters)

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        return self.opcua_handler.unbind_discovery_instance(instance_id=instance_id, binding_id=binding_id)

    def last_operation(self, instance_id: str, operation_data: str) -> LastOperation:
        pass


def parse_args(parser):
    args = parser.parse_args()
    if args.url and '://' not in args.url:
        logging.info("Adding default scheme %s to URL %s", ua.OPC_TCP_SCHEME, args.url)
        args.url = ua.OPC_TCP_SCHEME + '://' + args.url
    return args


def get_children_nodes(node, children_nodes=[], depth=2, timeout: object=4):
    for leaf in node.get_children_descriptions():
        children_nodes.append(dict(NodeId=leaf.NodeId.to_string(), DisplayName=leaf.DisplayName.to_string(), BrowseName=leaf.BrowseName.to_string(), Depth=3-depth))
        if depth:
            get_children_nodes(Node(node.server, leaf.NodeId), children_nodes, depth - 1, timeout)


def uasubscribe(url: object, nodeid: ua.NodeId, path: str, eventtype: str="datachange", timeout: object=4):
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
    opcua_handler = handler.OpcuaHandler(url=args.url)
    api.serve(OpcuaServiceBroker(opcua_handler), None)

    app = Flask(__name__)
    app.run(args.port)

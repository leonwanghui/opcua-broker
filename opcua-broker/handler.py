import json

from openbrokerapi.service_broker import (
    ProvisionedServiceSpec,
    UpdateServiceSpec,
    Binding,
    DeprovisionServiceSpec,
    LastOperation,
    UnbindDetails,
    ProvisionState,
    ProvisionDetails,
    UpdateDetails,
    BindResource,
    BindDetails,
    DeprovisionDetails
)

from opcua import Client
from opcua import Node
from opcua import ua


class OpcuaServiceInstance:
    def __init__(self,
                 instance_id: str,
                 service_id: str,
                 plan_id: str,
                 params: dict=None,
                 **kwargs):
        self.id = instance_id
        self.service_id = service_id
        self.plan_id = plan_id
        self.params = params


class OpcuaServiceBinding:
    def __init__(self,
                 binding_id: str,
                 instance_id: str,
                 service_id: str,
                 plan_id: str,
                 bind_resource: BindResource,
                 params: dict=None,
                 **kwargs):
        self.id = binding_id
        self.instance_id = instance_id
        self.service_id = service_id
        self.plan_id = plan_id
        self.bind_resource = bind_resource
        self.params = params


class OpcuaHandler(object):
    def __init__(self,
                 url: str,
                 service_instance_map: dict=None,
                 service_binding_map: dict=None,
                 **kwargs):
        self.url = url
        self.service_instance_map = service_instance_map
        self.service_binding_map = service_binding_map

    def provision_discovery_instance(self, instance_id: str, service_id: str, plan_id: str,
                                     parameters: dict=None) -> ProvisionedServiceSpec:
        url = parameters.get("discovery_url")
        if not url:
            return ProvisionedServiceSpec(state="failed")

        client = Client(url)

        print("Performing discovery at {0}\n".format(url))
        try:
            endpoints = client.connect_and_get_server_endpoints()

            service_instance = OpcuaServiceInstance(instance_id, service_id, plan_id, parameters)
            service_instance.params["endpoints"] = endpoints

            service_instance_map = dict()
            service_instance_map[instance_id] = service_instance
            self.service_instance_map = service_instance_map
        except Exception as e:
            print("Error: {0}\n".format(e))
            return ProvisionedServiceSpec(state="failed")

        print("Discovery service instance {0} is provisioned successfully\n".format(instance_id))
        return ProvisionedServiceSpec()

    def deprovision_discovery_instance(self, instance_id: str) -> DeprovisionServiceSpec:
        if self.service_instance_map is None or instance_id not in self.service_instance_map:
            return DeprovisionServiceSpec(is_async=False)

        self.service_instance_map.pop(instance_id)

        print("Discovery service instance {0} is deprovisioned successfully\n".format(instance_id))
        return DeprovisionServiceSpec(is_async=False)

    def bind_discovery_instance(self, instance_id: str, binding_id: str, service_id: str, plan_id: str,
                                bind_resource: BindResource, parameters: dict=None):
        if instance_id not in self.service_instance_map:
            return Binding(state="failed")

        credentials = dict()
        service_instance = self.service_instance_map[instance_id]
        credentials["endpoints"] = service_instance.params["endpoints"]
        service_binding = OpcuaServiceBinding(binding_id, instance_id, service_id, plan_id, bind_resource, parameters)
        service_binding.params["credentials"] = credentials

        service_binding_map = dict()
        service_binding_map[binding_id] = service_binding
        self.service_binding_map = service_binding_map

        print("Discovery service binding {0} is bound to service instance {1} successfully\n"
              .format(binding_id, instance_id))
        return Binding(credentials=credentials)

    def unbind_discovery_instance(self, instance_id: str, binding_id: str):
        if self.service_binding_map is None or binding_id not in self.service_binding_map:
            return

        service_binding = self.service_binding_map[binding_id]
        if not instance_id == service_binding.instance_id:
            print("Discovery service binding {0} was not bound to service instance {1}\n"
                  .format(binding_id, instance_id))
            return

        self.service_binding_map.pop(binding_id)

        print("Discovery service binding {0} is unbound to service instance {1} successfully\n"
              .format(binding_id, instance_id))
        return

    def provision_node_instance(self, instance_id: str, service_id: str, plan_id: str,
                                parameters: dict=None) -> ProvisionedServiceSpec:
        url = parameters.get("url")
        if not url:
            print("Error: {0}\n".format("url not contained in provision parameters!"))
            return ProvisionedServiceSpec(state="failed")
        nodes_to_add = parameters.get("nodesToAdd")
        if not nodes_to_add:
            print("Error: {0}\n".format("nodes_to_add not contained in provision parameters!"))
            return ProvisionedServiceSpec(state="failed")

        add_nodes_items = []
        for node_to_add in nodes_to_add:
            add_nodes_item = ua.AddNodesItem()

            if "parentNodeId" in node_to_add:
                add_nodes_item.ParentNodeId = ua.ExpandedNodeId(node_to_add.get("parentNodeId"))
            if "referenceTypeId" in node_to_add:
                add_nodes_item.ReferenceTypeId = ua.NodeId(node_to_add.get("referenceTypeId"))
            if "requestedNewNodeId" in node_to_add:
                add_nodes_item.RequestedNewNodeId = ua.ExpandedNodeId(node_to_add.get("requestedNewNodeId"))
            if "browseName" in node_to_add:
                add_nodes_item.BrowseName = ua.QualifiedName(node_to_add.get("browseName"))
            if "nodeClass" in node_to_add:
                add_nodes_item.NodeClass = ua.NodeClass(node_to_add.get("nodeClass"))
            add_nodes_items.append(add_nodes_item)

        print(add_nodes_items)
        client = Client(url)
        try:
            client.connect()
            nodes = []
            for add_nodes_item in add_nodes_items:
                parent_node = client.get_node(add_nodes_item.ParentNodeId)
                if add_nodes_item.NodeClass == 1:
                    obj = parent_node.add_object(add_nodes_item.RequestedNewNodeId, add_nodes_item.BrowseName)
                    nodes.append(obj)
                elif add_nodes_item.NodeClass == 2:
                    var = parent_node.add_variable(add_nodes_item.RequestedNewNodeId, add_nodes_item.BrowseName)
                    nodes.append(var)
                elif add_nodes_item.NodeClass == 4:
                    method = parent_node.add_method()
                    nodes.append(method)
                else:
                    folder = parent_node.add_folder(add_nodes_item.RequestedNewNodeId, add_nodes_item.BrowseName)
                    nodes.append(folder)

            service_instance = OpcuaServiceInstance(instance_id, service_id, plan_id, parameters)
            service_instance.params["nodes"] = nodes

            service_instance_map = dict()
            service_instance_map[instance_id] = service_instance
            self.service_instance_map = service_instance_map
        except Exception as e:
            print("Error: {0}\n".format(e))
            return ProvisionedServiceSpec(state="failed")

        print("Node management service instance {0} is provisioned successfully\n".format(instance_id))
        return ProvisionedServiceSpec()

    def deprovision_node_instance(self, instance_id: str) -> DeprovisionServiceSpec:
        if self.service_instance_map is None or instance_id not in self.service_instance_map:
            return DeprovisionServiceSpec(is_async=False)

        service_instance = self.service_instance_map.get(instance_id)
        url = service_instance.params.get("url")
        nodes = service_instance.params.get("nodes")
        print(nodes)

        client = Client(url)
        try:
            client.connect()
            client.delete_nodes(nodes)
        except Exception as e:
            print("Error: {0}\n".format(e))
            return DeprovisionServiceSpec(is_async=False)

        self.service_instance_map.pop(instance_id)

        print("Node service instance {0} is deprovisioned successfully\n".format(instance_id))
        return DeprovisionServiceSpec(is_async=False)

    def provision_subscription_instance(self, instance_id: str, service_id: str, plan_id: str,
                                        parameters: dict=None) -> ProvisionedServiceSpec:
        return ProvisionedServiceSpec()

    def deprovision_subscription_instance(self, instance_id: str) -> DeprovisionServiceSpec:
        return DeprovisionServiceSpec(is_async=False)
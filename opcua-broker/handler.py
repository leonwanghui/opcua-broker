from openbrokerapi.service_broker import (
    ProvisionedServiceSpec,
    UpdateServiceSpec,
    Binding,
    DeprovisionServiceSpec,
    LastOperation,
    UnbindDetails,
    ProvisionDetails,
    UpdateDetails,
    BindResource,
    BindDetails,
    DeprovisionDetails
)

from opcua import Client
from opcua import Node
from opcua import ua


class OpensdsServiceInstance:
    def __init__(self,
                 id:str,
                 service_id:str,
                 plan_id:str,
                 params=None,
                 **kwargs):
        self.id = id
        self.service_id = service_id
        self.plan_id = plan_id
        self.params = params


class OpensdsServiceBinding:
    def __init__(self,
                 id:str,
                 service_id:str,
                 plan_id:str,
                 bind_resource:BindResource,
                 params=None,
                 **kwargs):
        self.id = id
        self.service_id = service_id
        self.plan_id = plan_id
        self.bind_resource = bind_resource
        self.params = params


class OpcuaHandler(object):
    def __init__(self,
                 url:str,
                 service_instance_map:dict=None,
                 service_binding_map:dict=None,
                 **kwargs):
        self.url = url
        self.service_instance_map = service_instance_map
        self.service_binding_map = service_binding_map

    def provision_servers_discovery_instance(self) -> ProvisionedServiceSpec:
        client = Client(self.url)

        print("Performing discovery at {0}\n".format(self.url))
        servers = client.connect_and_find_servers()
        return ProvisionedServiceSpec()

    def deprovision_servers_discovery_instance(self) -> DeprovisionServiceSpec:
        return

    def provision_endpoints_discovery_instance(self) -> ProvisionedServiceSpec:
        client = Client(self.url)

        print("Performing discovery at {0}\n".format(self.url))
        if self.resource_type == 'server':
            servers = client.connect_and_find_servers()
        elif self.resource_type == 'endpoint':
            endponits = client.connect_and_get_server_endpoints()
        return

    def deprovision_endpoints_discovery_instance(self) -> DeprovisionServiceSpec:
        return

    def provision_node_instance(self) -> ProvisionedServiceSpec:
        return

    def deprovision_node_instance(self) -> DeprovisionServiceSpec:
        return

    def provision_subscription_instance(self) -> ProvisionedServiceSpec:
        return

    def deprovision_subscription_instance(self) -> DeprovisionServiceSpec:
        return
from openbrokerapi.service_broker import (
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


class OpcuaHandler(object):
    def __init__(self, url, resource_type):
        self.url = url
        self.resource_type = resource_type

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
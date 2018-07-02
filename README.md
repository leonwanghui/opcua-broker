# opcua-broker
It a public tool that provides the integration between opc server and service catalog.

## Catalog
curl http://127.0.0.1:5000/v2/catalog -H "X-Broker-APi-Version: 2.13"

## Provision
* Discovery service
```shell
curl http://127.0.0.1:5000/v2/service_instances/abc123?accepts_incomplete=true -d '{
  "service_id": "00000000-0000-0000-0000-000000000000",
  "plan_id": "00000000-0000-0000-0000-000000000001",
  "context": {
    "platform": "cloudfoundry"
  },
  "organization_guid": "org-guid-here",
  "space_guid": "space-guid-here",
  "parameters": {
    "discovery_url": "opc.tcp://localhost:4840"
  }
}' -X PUT -H "X-Broker-API-Version: 2.13" -H "Content-Type: application/json"
```

* Node management service
```shell
curl http://127.0.0.1:5000/v2/service_instances/abc456?accepts_incomplete=true -d '{
  "service_id": "00000000-0000-0000-0000-000000000000",
  "plan_id": "00000000-0000-0000-0000-000000000002",
  "context": {
    "platform": "cloudfoundry"
  },
  "organization_guid": "org-guid-here",
  "space_guid": "space-guid-here",
  "parameters": {
    "url": "opc.tcp://localhost:4840",
    "nodesToAdd": [{"browseName":"Helloworld","nodeClass":1,"parentNodeId":84,"requestedNewNodeId":10080},{"browseName":"Goodbye","nodeClass":1,"parentNodeId":10080,"requestedNewNodeId":10081}]
  }
}' -X PUT -H "X-Broker-API-Version: 2.13" -H "Content-Type: application/json"
```

## Binding
* Discovery service
```shell
curl http://127.0.0.1:5000/v2/service_instances/abc123/service_bindings/xyz123 -d '{
  "context": {
    "platform": "cloudfoundry"
  },
  "service_id": "00000000-0000-0000-0000-000000000000",
  "plan_id": "00000000-0000-0000-0000-000000000001",
  "bind_resource": {
    "app_guid": "app-guid-here"
  },
  "parameters": {}
}' -X PUT -H "X-Broker-API-Version: 2.13" -H "Content-Type: application/json"
```

## Unbinding
* Discovery service
```shell
curl 'http://127.0.0.1:5000/v2/service_instances/abc123/service_bindings/xyz123?service_id=00000000-0000-0000-0000-000000000000&plan_id=00000000-0000-0000-0000-000000000001' -X DELETE -H "X-Broker-API-Version: 2.13"
```

## Deprovision
* Discovery service
```shell
curl 'http://127.0.0.1:5000/v2/service_instances/abc123?accepts_incomplete=true&service_id=00000000-0000-0000-0000-000000000000&plan_id=00000000-0000-0000-0000-000000000001' -X DELETE -H "X-Broker-API-Version: 2.13"
```

* Node management service
```shell
curl 'http://127.0.0.1:5000/v2/service_instances/abc456?accepts_incomplete=true&service_id=00000000-0000-0000-0000-000000000000&plan_id=00000000-0000-0000-0000-000000000002' -X DELETE -H "X-Broker-API-Version: 2.13"
```

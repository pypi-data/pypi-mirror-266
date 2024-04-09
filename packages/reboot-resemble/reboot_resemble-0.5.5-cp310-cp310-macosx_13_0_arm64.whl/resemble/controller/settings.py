# The ports that user containers will be asked to use to expose their Resemble
# servers. We will expose these ports via k8s Deployment/Service as well.
USER_CONTAINER_GRPC_PORT = 50051
USER_CONTAINER_WEBSOCKET_PORT = 50052

# On Kubernetes we use labels to identify which pods are Resemble consensuses,
# and what their consensuses are called. This defines what those label is
# called.
IS_RESEMBLE_CONSENSUS_LABEL_NAME = 'reboot.dev/is-resemble-consensus'
IS_RESEMBLE_CONSENSUS_LABEL_VALUE = 'true'
RESEMBLE_CONSENSUS_ID_LABEL_NAME = 'reboot.dev/resemble-consensus-id'

# On Kubernetes, how can we identify the Istio ingress gateways?
# ISSUE(1529): this should likely be something a cluster operator can configure.
#              The following are the settings that our LocalKubernetes gets when
#              it installs Istio using Istio's `demo` profile.
ISTIO_INGRESSGATEWAY_NAMESPACE = 'istio-system'
ISTIO_INGRESSGATEWAY_NAME = 'istio-ingressgateway'
# By "internal port" we mean the port that traffic already inside the Kubernetes
# cluster should use to access the Istio ingress gateway. This may differ from
# the port that external traffic from outside the Kubernetes cluster uses to
# reach the load balancer.
#
# TODO(rjh): change this to 9990 to be more unique and match the default
#            insecure port?
ISTIO_INGRESSGATEWAY_INTERNAL_PORT = 8080
ISTIO_INGRESSGATEWAY_LABEL_NAME = 'istio'
ISTIO_INGRESSGATEWAY_LABEL_VALUE = 'ingressgateway'

# In an Istio `VirtualService`, how do we address all Istio sidecars?
ISTIO_ALL_SIDECARS_GATEWAY_NAME = 'mesh'

# Labels that need to be set on a namespace in order for Istio to do sidecar
# injection.
ISTIO_NAMESPACE_LABELS = {
    # Required to be set in order for Istio to inject sidecars into a Resemble
    # namespace.
    'istio-injection': 'enabled',
}

# The resemble system requires two Kubernetes namespaces: one for the system
# itself, and one to place `ApplicationDeployment`s. What are these namespaces
# called?
RESEMBLE_SYSTEM_NAMESPACE = 'resemble-system'
# The following must match the hardcoded value in
#   `tests/test_resemble_bank/k8s/deployment/kustomization.yaml`.
RESEMBLE_APPLICATION_DEPLOYMENT_NAMESPACE = 'resemble-application-deployments'

# On Kubernetes, some objects need fixed names.
RESEMBLE_MESH_VIRTUAL_SERVICE_NAME = 'network-managers-mesh-virtual-service'
RESEMBLE_GATEWAY_VIRTUAL_SERVICE_NAME = 'network-managers-gateway-virtual-service'
RESEMBLE_MESH_ROUTING_FILTER_NAME = 'network-managers-mesh-routing-envoy-filter'
RESEMBLE_GATEWAY_ROUTING_FILTER_NAME = 'network-managers-gateway-routing-envoy-filter'
RESEMBLE_GATEWAY_NAME = 'resemble-gateway'

# On Kubernetes, the Resemble system will offer a fixed hostname that clients
# use when they want to talk to any Resemble service.
RESEMBLE_ROUTABLE_HOSTNAME = 'resemble-service'

### Environment variables.
# We use environment variables when we need to communicate information between
# processes. Our naming convention is as follows:
#   `ENVVAR_<SOMETHING>` is the name of an environment variable.
#   `<SOMETHING>_<VALUE-NAME>` is one VALUE the `SOMETHING` environment
#    variable might take.

# Application ID injected via an environment variable.
ENVVAR_RESEMBLE_APPLICATION_ID = 'RESEMBLE_APPLICATION_ID'

# Kubernetes pod metadata injected via environment variables.
ENVVAR_KUBERNETES_POD_UID = 'KUBERNETES_POD_UID'
ENVVAR_KUBERNETES_POD_NAME = 'KUBERNETES_POD_NAME'
ENVVAR_KUBERNETES_POD_NAMESPACE = 'KUBERNETES_POD_NAMESPACE'
ENVVAR_KUBERNETES_SERVICE_ACCOUNT = 'KUBERNETES_SERVICE_ACCOUNT'

# Gives the mode in which a Resemble application is expected to be started.
# Present on any Resemble config pod.
ENVVAR_RESEMBLE_MODE = 'RESEMBLE_MODE'
RESEMBLE_MODE_CONFIG = 'config'  # Start the server as a config server.

# Gives the port on which a config-mode server is expected to start serving.
# Present on any Resemble config pod.
ENVVAR_RESEMBLE_CONFIG_SERVER_PORT = 'RESEMBLE_CONFIG_SERVER_PORT'

# The name of the Kubernetes storage class that Resemble should use for its
# state storage.
RESEMBLE_STORAGE_CLASS_NAME = 'resemble-storage'

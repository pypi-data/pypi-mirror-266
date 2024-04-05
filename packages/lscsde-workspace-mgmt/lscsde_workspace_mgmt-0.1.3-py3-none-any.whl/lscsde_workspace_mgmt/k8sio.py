from logging import Logger
from kubernetes_asyncio import client
from kubernetes_asyncio.client.exceptions import ApiException
from pydantic import TypeAdapter
from .models import AnalyticsWorkspace, AnalyticsWorkspaceBinding
from .exceptions import (
    InvalidParameterException,
    InvalidLabelFormatException
)
from .objects import (
    AnalyticsWorkspace,
    AnalyticsWorkspaceBinding,
    AnalyticsWorkspaceStatus,
    AnalyticsWorkspaceBindingStatus,
    AnalyticsWorkspaceSpec,
    AnalyticsWorkspaceBindingSpec,
    KubernetesHelper
)
from kubernetes_asyncio.client.models import (
    V1ObjectMeta,
    V1Pod,
    V1Volume,
    V1VolumeMount,
    V1PersistentVolumeClaim,
    V1PersistentVolumeClaimSpec,
    V1PersistentVolumeClaimVolumeSource,
    V1PersistentVolumeClaimList
)

class KubernetesNamespacedCustomClient:
    def __init__(self, k8s_api : client.CustomObjectsApi, log : Logger, group : str, version : str, plural : str, kind : str):
        self.group = group
        self.version = version
        self.plural = plural
        self.kind = kind
        self.api = k8s_api
        self.log : Logger = log

    def get_api_version(self):
        return f"{self.group}/{self.version}"

    async def get(self, namespace, name):
        return await self.api.get_namespaced_custom_object(
            group = self.group,
            version = self.version,
            namespace = namespace,
            plural = self.plural,
            name = name
        )
    
    async def list(self, namespace, **kwargs):
        return await self.api.list_namespaced_custom_object(
            group = self.group,
            version = self.version,
            namespace = namespace,
            plural = self.plural,
            **kwargs
        )
    
    async def patch(self, namespace : str, name : str, body : dict):
        return await self.api.patch_namespaced_custom_object(
            group = self.group, 
            version = self.version, 
            namespace = namespace,
            plural = self.plural, 
            name = name, 
            body = body
            )
    
    async def patch_status(self, namespace : str, name : str, body : dict):
        return await self.api.patch_namespaced_custom_object_status(
            group = self.group,
            version = self.version,
            namespace = namespace,
            plural = self.plural,
            name = name,
            body = body
        )
    
    async def replace(self, namespace : str, name : str, body : dict):
        return await self.api.replace_namespaced_custom_object(
            group = self.group,
            version = self.version,
            namespace = namespace,
            plural = self.plural,
            name = name,
            body = body
        )
    
    async def create(self, namespace : str, body : dict):
        return await self.api.create_namespaced_custom_object(
            group = self.group,
            version = self.version,
            namespace = namespace,
            plural = self.plural,
            body = body
        )
    
    async def delete(self, namespace : str, name : str):
        return await self.api.delete_namespaced_custom_object(
            group = self.group,
            version = self.version,
            namespace = namespace,
            plural = self.plural,
            name = name
        )

class AnalyticsWorkspaceBindingClient(KubernetesNamespacedCustomClient):
    adaptor = TypeAdapter(AnalyticsWorkspaceBinding)
    def __init__(self, k8s_api: client.CustomObjectsApi, log: Logger):
        super().__init__(
            k8s_api = k8s_api, 
            log = log, 
            group = "xlscsde.nhs.uk",
            version = "v1",
            plural = "analyticsworkspacebindings",
            kind = "AnalyticsWorkspaceBinding"
        )

    async def get(self, namespace, name):
        result = await super().get(namespace, name)
        print(result)
        return self.adaptor.validate_python(result)
    
    async def list(self, namespace, **kwargs):
        result = await super().list(namespace, **kwargs)
        return [self.adaptor.validate_python(item) for item in result["items"]]

    

    async def list_by_username(self, namespace, username):
        helper = KubernetesHelper() 
        formatted_username = helper.format_as_label(username)
        no_label = await self.list(namespace = namespace, label_selector = f"!xlscsde.nhs.uk/username")
        for item in no_label:
            if item.spec.username:
                try:
                    if not item.metadata.labels:
                        patch_body = [{"op": "add", "path": "/metadata/labels", "value": { "xlscsde.nhs.uk/username" : item.spec.username_as_label() }}]
                    else:
                        patch_body = [{"op": "add", "path": "/metadata/labels/xlscsde.nhs.uk~1username", "value": item.spec.username_as_label() }]

                    patch_response = await self.patch(
                        namespace = item.metadata.namespace, 
                        name = item.metadata.name, 
                        patch_body = patch_body
                        )
                except InvalidLabelFormatException as ex:
                    self.log.error(f"Could not validate {item.metadata.name} due to a label format exception: {ex}")

        return await self.list(namespace = namespace, label_selector = f"xlscsde.nhs.uk/username={formatted_username}")

    async def create(self, body : AnalyticsWorkspaceBinding, append_label : bool = True):
        contents = self.adaptor.dump_python(body, by_alias=True)
        
        if append_label:
            contents["metadata"]["labels"]["xlscsde.nhs.uk/username"] = body.spec.username_as_label()

        result = await super().create(
            namespace = body.metadata.namespace,
            body = contents
        )
        return self.adaptor.validate_python(result)

    async def patch(self, namespace : str = None, name : str = None, patch_body : dict = None, body : AnalyticsWorkspaceBinding = None):
        if not patch_body:
            if not body:
                raise InvalidParameterException("Either namespace, name and patch_body or body must be provided")
            
            spec_adapter = TypeAdapter(AnalyticsWorkspaceBindingSpec)
            status_adapter = TypeAdapter(AnalyticsWorkspaceBindingStatus)
            patch_body = [
                {"op": "replace", "path": "/spec", "value": spec_adapter.dump_python(body.spec, by_alias=True)},
                {"op": "replace", "path": "/status", "value": status_adapter.dump_python(body.status, by_alias=True)}
            ]

        if not namespace:
            if not body:
                raise InvalidParameterException("Either namespace, name and patch_body or body must be provided")
            namespace = body.metadata.namespace

        if not name:
            if not body:
                raise InvalidParameterException("Either namespace, name and patch_body or body must be provided")
            name = body.metadata.name
            
        result = await super().patch(
            namespace = namespace,
            name = name,
            body = patch_body
        )
        return self.adaptor.validate_python(result)

    async def patch_status(self, namespace : str, name : str, status : AnalyticsWorkspaceBindingStatus):
        status_adapter = TypeAdapter(AnalyticsWorkspaceBindingStatus)
        body = [{"op": "replace", "path": "/status", "value": status_adapter.dump_python(status, by_alias=True)}] 
        result = await super().patch_status(
            namespace = namespace,
            name = name,
            body = body
        )
        return self.adaptor.validate_python(result)

    async def replace(self, body : AnalyticsWorkspaceBinding, append_label : bool = True):
        contents = self.adaptor.dump_python(body, by_alias=True)
        if append_label:
            contents["metadata"]["labels"]["xlscsde.nhs.uk/username"] = body.spec.username_as_label()

        result = await super().replace(
            namespace = body.metadata.namespace,
            name = body.metadata.name,
            body = contents
        )
        return self.adaptor.validate_python(result)
    
    async def delete(self, body : AnalyticsWorkspaceBinding = None, namespace : str = None, name : str = None):
        if body:
            if not namespace:
                namespace = body.metadata.namespace
            if not name:
                name = body.metadata.name
        
        patch_body = [{"op": "replace", "path": "/status/statusText", "value": "Deleting"}] 

        current = await super().get(namespace, name)
        if not current.get("status"):
            patch_body = [{"op": "add", "path": "/status", "value": { "statusText" : "Deleting" }}] 
            
        await super().patch_status(
            namespace = body.metadata.namespace,
            name = body.metadata.name,
            body = patch_body
        )
        return await super().delete(
            namespace = body.metadata.namespace,
            name = body.metadata.name
        )

class AnalyticsWorkspaceClient(KubernetesNamespacedCustomClient):
    adaptor = TypeAdapter(AnalyticsWorkspace)

    def __init__(self, k8s_api: client.CustomObjectsApi, log: Logger):
        super().__init__(
            k8s_api = k8s_api, 
            log = log, 
            group = "xlscsde.nhs.uk",
            version = "v1",
            plural = "analyticsworkspaces",
            kind = "AnalyticsWorkspace"
        )
        
    async def get(self, namespace, name):
        result = await super().get(namespace, name)
        return self.adaptor.validate_python(result)
    
    async def list(self, namespace, **kwargs):
        result = await super().list(namespace, **kwargs)
        
        return [self.adaptor.validate_python(item) for item in result["items"]]
    
    async def list_by_username(self, binding_client : AnalyticsWorkspaceBindingClient, namespace : str, username : str):
        bindings = await binding_client.list_by_username(
            namespace = namespace,
            username = username
            )
        bound_workspaces = list(set([x.spec.workspace for x in bindings]))
        workspaces = []
        for bound_workspace in bound_workspaces:
            try:
                workspace = await self.get(namespace = namespace, name = bound_workspace)
                workspaces.append(workspace)
            except ApiException as e:
                if e.status == 404:
                    self.log.error(f"Workspace {bound_workspace} referenced by user {username} on {namespace} does not exist")
                else:
                    raise e    
        
        return workspaces     
            
    async def create(self, body : AnalyticsWorkspace):
        result = await super().create(
            namespace = body.metadata.namespace,
            body = self.adaptor.dump_python(body, by_alias=True)
        )
        return self.adaptor.validate_python(result)

    async def patch(self, namespace : str = None, name : str = None, patch_body : dict = None, body : AnalyticsWorkspace = None):
        if not patch_body:
            if not body:
                raise InvalidParameterException("Either namespace, name and patch_body or body must be provided")
            
            spec_adapter = TypeAdapter(AnalyticsWorkspaceSpec)
            status_adapter = TypeAdapter(AnalyticsWorkspaceStatus)

            patch_body = [
                {"op": "replace", "path": "/spec", "value": spec_adapter.dump_python(body.spec, by_alias=True)},
                {"op": "replace", "path": "/status", "value": status_adapter.dump_python(body.status, by_alias=True)}
            ]

        if not namespace:
            if not body:
                raise InvalidParameterException("Either namespace, name and patch_body or body must be provided")
            namespace = body.metadata.namespace

        if not name:
            if not body:
                raise InvalidParameterException("Either namespace, name and patch_body or body must be provided")
            name = body.metadata.name
            
        result = await super().patch(
            namespace = namespace,
            name = name,
            body = patch_body
        )        
        
        return self.adaptor.validate_python(result)

    async def patch_status(self, namespace : str, name : str, status : AnalyticsWorkspaceStatus):
        status_adapter = TypeAdapter(AnalyticsWorkspaceStatus)
        body = [{"op": "replace", "path": "/status", "value": status_adapter.dump_python(status, by_alias=True)}] 
        result = await super().patch_status(
            namespace = namespace,
            name = name,
            body = body
        )
        return self.adaptor.validate_python(result)


    async def replace(self, body : AnalyticsWorkspace):
        result = await super().replace(
            namespace = body.metadata.namespace,
            name = body.metadata.name,
            body = self.adaptor.dump_python(body, by_alias=True)
        )
        return self.adaptor.validate_python(result)
        
    
    async def delete(self, body : AnalyticsWorkspace = None, namespace : str = None, name : str = None):
        if body:
            if not namespace:
                namespace = body.metadata.namespace
            if not name:
                name = body.metadata.name
        
        
        patch_body = [{"op": "replace", "path": "/status/statusText", "value": "Deleting"}] 

        current = await super().get(namespace, name)
        if not current.get("status"):
            patch_body = [{"op": "add", "path": "/status", "value": { "statusText" : "Deleting" }}] 

        await super().patch_status(
            namespace = body.metadata.namespace,
            name = body.metadata.name,
            body = patch_body
        )
        return await super().delete(
            namespace = body.metadata.namespace,
            name = body.metadata.name
        )
    
class PersistentVolumeClaimClient:
    def __init__(self, api_client : client.ApiClient, log : Logger):
        self.api = client.CoreV1Api(api_client)
        self.log = log
        
    async def get(self, name: str, namespace: str) -> V1PersistentVolumeClaim:
        self.log.info(f"Searching for PVC {name} on {namespace} exists")
        response : V1PersistentVolumeClaimList = await self.api.list_namespaced_persistent_volume_claim(namespace, field_selector = f"metadata.name={name}")
        
        if len(response.items) == 0:
            return None
        
        return response.items[0]

    async def create_if_not_exists(self, name: str, namespace: str, storage_class_name : str, labels: dict[str, str] = {}, access_modes : list[str]=["ReadWriteMany"], storage_requested : str = "10Gi"):
        pvc = await self.get(name, namespace)
        if not pvc:
            self.log.info(f"PVC {name} on {namespace} does not exist.")
            
            pvc = V1PersistentVolumeClaim(
                metadata = V1ObjectMeta(
                    name=name,
                    namespace= namespace,
                    labels = labels
                ),
                spec=V1PersistentVolumeClaimSpec(
                    storage_class_name = storage_class_name,
                    access_modes = access_modes,
                    resources= {
                        "requests": { 
                            "storage": storage_requested
                        }
                    }
                )
            )
            return await self.api.create_namespaced_persistent_volume_claim(namespace, pvc)

        return pvc
    
    async def mount(self, pod: V1Pod, storage_name : str, namespace: str, storage_class_name : str, mount_path : str, read_only : bool = False) -> V1Pod:
        self.log.info(f"Attempting to mount {storage_name} on {namespace}...")
        storage : V1PersistentVolumeClaim = await self.create_if_not_exists(storage_name, namespace, storage_class_name)

        volume = V1Volume(
            name = storage_name,
            persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
                claim_name=storage.metadata.name
            )
        )

        if mount_path == "":
            mount_path= f"/mnt/{storage_name}"

        volume_mount = V1VolumeMount(
            name = storage_name,
            mount_path= mount_path,
            read_only = read_only
        )
        if not pod.spec.volumes:
            pod.spec.volumes = []
        pod.spec.volumes.append(volume)
        if not pod.spec.containers[0].volume_mounts:
            pod.spec.containers[0].volume_mounts = []
        pod.spec.containers[0].volume_mounts.append(volume_mount)

        self.log.info(f"Successfully mounted {storage.metadata.name} to {mount_path}.")

        return pod

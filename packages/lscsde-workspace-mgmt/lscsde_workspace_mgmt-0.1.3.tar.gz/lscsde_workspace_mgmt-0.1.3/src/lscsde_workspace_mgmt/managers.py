from .k8sio import (
    AnalyticsWorkspaceClient,
    AnalyticsWorkspaceBindingClient,
    PersistentVolumeClaimClient,
    V1ObjectMeta,
    V1Pod
)

from .objects import (
    AnalyticsWorkspace,
    AnalyticsWorkspaceBinding,
    AnalyticsWorkspaceConverter
)

from .exceptions import (
    WorkspaceNotFoundException
)

from kubernetes_asyncio.client import (
    CustomObjectsApi,
    ApiClient
)
from logging import Logger

class AnalyticsWorkspaceManager:
    def __init__(self, api_client : ApiClient, log : Logger):
        custom_objects_api = CustomObjectsApi(api_client=api_client)
        self.workspace_client = AnalyticsWorkspaceClient(custom_objects_api, log)
        self.binding_client = AnalyticsWorkspaceBindingClient(custom_objects_api, log)
        self.pvc_client = PersistentVolumeClaimClient(api_client, log)
        self.log = log

    async def get_workspaces_for_user(self, namespace : str, username : str):
        workspaces = await self.workspace_client.list_by_username(self.binding_client, namespace, username)
        permitted_workspaces : dict[str, AnalyticsWorkspace] = {}
        for workspace in workspaces:
            if workspace.metadata.name not in permitted_workspaces:
                permitted_workspaces[workspace.metadata.name] = workspace

        return permitted_workspaces

    async def get_permitted_workspaces(self, namespace : str, username : str):
        permitted_workspaces = await self.get_workspaces_for_user(namespace, username)
        sorted_workspaces = sorted(
            permitted_workspaces.values(), key=lambda x: x.spec.display_name
        )
        converter = AnalyticsWorkspaceConverter()
        return [converter.to_workspace_dict(item) for item in sorted_workspaces]
        
    async def mount_workspace(self, pod : V1Pod, storage_class_name, mount_prefix, storage_prefix : str = "", read_only : bool = False, mount_path = ""):
        metadata : V1ObjectMeta = pod.metadata
        namespace = metadata.namespace
        name = metadata.name
        workspace_name = metadata.labels.get("workspace")

        if not workspace_name:
            raise WorkspaceNotFoundException(namespace, name)
        
        workspace = await self.workspace_client.get(namespace, workspace_name)
        
        storage_name : str = f"{storage_prefix}{workspace_name}"

        if workspace.status.persistent_volume_claim:
            storage_name = workspace.status.persistent_volume_claim 

        if workspace.spec.jupyter_workspace.persistent_volume_claim.name:
            storage_name = workspace.spec.jupyter_workspace.persistent_volume_claim.name

        if workspace.spec.jupyter_workspace.persistent_volume_claim.storage_class_name:
            storage_class_name = workspace.spec.jupyter_workspace.persistent_volume_claim.storage_class_name

        if not mount_path:
            mount_path = f"{mount_prefix}/{workspace_name}"
        
        amended_pod = await self.pvc_client.mount(
            pod = pod, 
            storage_name = storage_name, 
            namespace = namespace,
            mount_path = mount_path,
            storage_class_name = storage_class_name,
            read_only = read_only
            )
        
        update_status : bool = False
        if not workspace.status.persistent_volume_claim:
            workspace.status.persistent_volume_claim = storage_name
            update_status = True

        if workspace.status.status_text != "Provisioned":
            workspace.status.status_text = "Provisioned"
            update_status = True
        
        if update_status == True:
            await self.workspace_client.patch_status(
                namespace = workspace.metadata.namespace,
                name = workspace.metadata.name,
                status = workspace.status
                )
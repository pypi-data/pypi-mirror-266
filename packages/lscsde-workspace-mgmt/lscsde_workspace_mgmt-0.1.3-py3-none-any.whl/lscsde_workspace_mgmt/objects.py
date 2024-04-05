from datetime import datetime, timedelta
from kubernetes_asyncio.client.models import V1ObjectMeta
from .exceptions import InvalidLabelFormatException
import re 
from .models import (
    AnalyticsWorkspaceBindingClaim,
    AnalyticsWorkspaceBinding,
    AnalyticsWorkspaceBindingClaim,
    AnalyticsWorkspaceBindingSpec,
    AnalyticsWorkspaceBindingStatus,
    AnalyticsWorkspace,
    AnalyticsWorkspaceSpec,
    AnalyticsWorkspaceStatus,
    AnalyticsWorkspaceValidity,
    JupyterWorkspacePersistentVolumeClaim,
    JupyterWorkspaceSpec,
    JupyterWorkspaceStorage,
    KubernetesMetadata,
    VirtualMachineWorkspaceSpec,
    KubernetesHelper
)

class AnalyticsWorkspaceConverter:
    def days_until_expiry(self, time_str):
        ws_end_date = datetime.strptime(time_str, "%Y-%m-%d")
        ws_days_left: timedelta = ws_end_date - datetime.today()
        return ws_days_left
    
    def to_workspace_dict(self, workspace : AnalyticsWorkspace):
        contents = {}
        contents["display_name"] = workspace.spec.display_name
        contents["description"] = workspace.spec.description
        
        if workspace.spec.jupyter_workspace:
            contents["kubespawner_override"] = {}
            contents["kubespawner_override"]["image"] = workspace.spec.jupyter_workspace.image
            extra_labels = {}
            if workspace.spec.jupyter_workspace.extra_labels:
                extra_labels = workspace.spec.jupyter_workspace.extra_labels.copy()
            extra_labels["workspace"] = workspace.metadata.name
            contents["kubespawner_override"]["extra_labels"] = extra_labels

            if workspace.spec.jupyter_workspace.resources:
                mem_guarantee = workspace.spec.jupyter_workspace.resources.get("requests").get("memory")
                if mem_guarantee:
                    contents["kubespawner_override"]["mem_guarantee"] = mem_guarantee

                mem_limit = workspace.spec.jupyter_workspace.resources.get("limits").get("memory")
                if mem_limit:
                    contents["kubespawner_override"]["mem_limit"] = mem_limit

                cpu_guarantee = workspace.spec.jupyter_workspace.resources.get("requests").get("cpu")
                if cpu_guarantee:
                    contents["kubespawner_override"]["cpu_guarantee"] = cpu_guarantee

                cpu_limit = workspace.spec.jupyter_workspace.resources.get("limits").get("cpu")
                if cpu_limit:
                    contents["kubespawner_override"]["cpu_limit"] = cpu_limit

            default_url = workspace.spec.jupyter_workspace.default_uri
            if default_url:
                contents["kubespawner_override"]["default_url"] = default_url

            if workspace.spec.jupyter_workspace.node_selector:
                contents["kubespawner_override"]["node_selector"] = workspace.spec.jupyter_workspace.node_selector

            if workspace.spec.jupyter_workspace.tolerations:
                contents["kubespawner_override"]["tolerations"] = workspace.spec.jupyter_workspace.tolerations
            
        contents["slug"] = workspace.metadata.name
        contents["start_date"] = workspace.spec.validity.available_from
        contents["end_date"] = workspace.spec.validity.expires
        contents["ws_days_left"] = self.days_until_expiry(workspace.spec.validity.expires)
        return contents

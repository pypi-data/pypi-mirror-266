from datetime import date,datetime, timedelta
from kubernetes_asyncio.client.models import V1ObjectMeta
from .exceptions import InvalidLabelFormatException
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from typing import Optional
from pydantic.dataclasses import dataclass
import re 
import json

class KubernetesHelper:
    def format_as_label(self, username : str):
        formatted = re.sub('[^0-9a-z.]+', '___', username.casefold())
        validation_expression = '^(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?$'
        if not re.match(pattern = validation_expression, string = formatted):
            raise InvalidLabelFormatException(f"Invalid value: \"{formatted}\": a valid label must be an empty string or consist of alphanumeric characters, '-', '_' or '.', and must start and end with an alphanumeric character (e.g. 'MyValue',  or 'my_value',  or '12345', regex used for validation is '{validation_expression}')")
        return formatted

class KubernetesMetadata(BaseModel):
    name : Optional[str] = Field(default="")
    namespace : Optional[str] = Field(default="default")
    annotations : Optional[dict[str, str]] = Field(default={})
    labels : Optional[dict[str, str]] = Field(default={})
    resource_version : Optional[str] = Field(alias="resourceVersion", default=None)


class AnalyticsWorkspaceValidity(BaseModel):
    available_from : Optional[str] = Field(alias="availableFrom")
    expires : Optional[str] = Field()

class VirtualMachineWorkspaceSpec(BaseModel):
    max_hosts : Optional[int] = Field(alias="maxHosts")
    
class JupyterWorkspaceStorage(BaseModel):
    mount_path : Optional[str] = Field(alias="mountPath", default=None)
    persistent_volume_claim : Optional[str] = Field(alias="persistentVolumeClaim", default=None)
    storage_class_name : Optional[str] = Field(alias="storageClassName", default=None)
    

class JupyterWorkspacePersistentVolumeClaim(BaseModel):
    name : Optional[str] = Field(alias="name", default=None)
    storage_class_name : Optional[str] = Field(alias="storageClassName", default=None)

class JupyterWorkspaceSpec(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image : Optional[str] = Field(default=None)
    extra_labels : Optional[dict[str, str]] = Field(alias="extraLabels", default = None)
    default_uri : Optional[str] = Field(alias="defaultUri", default = None)
    node_selector : Optional[dict[str, any]]  = Field(alias="nodeSelector", default=None)
    tolerations: Optional[dict[str, any]]  = Field(alias="tolerations", default=None)
    resources: Optional[dict[str, any]]  = Field(alias="resources", default=None)
    additional_storage: Optional[list[JupyterWorkspaceStorage]]  = Field(alias="additionalStorage", default=None)
    persistent_volume_claim: Optional[JupyterWorkspacePersistentVolumeClaim] = Field(alias="persistentVolumeClaim", default=JupyterWorkspacePersistentVolumeClaim())

class AnalyticsWorkspaceStatus(BaseModel):
    status_text : Optional[str] = Field(alias="statusText", default="Waiting")
    persistent_volume_claim : Optional[str] = Field(alias="persistentVolumeClaim", default=None)
    additional_storage : Optional[dict[str, str]] = Field(alias="additionalStorage", default=None)
    
class AnalyticsWorkspaceBindingStatus(BaseModel):
    status_text : Optional[str] = Field(alias="statusText", default="Waiting")
    
class AnalyticsWorkspaceSpec(BaseModel):
    display_name : Optional[str] = Field(alias="displayName", default=None)
    description : Optional[str] = Field(alias="description", default=None)
    validity : Optional[AnalyticsWorkspaceValidity] = Field(alias="validity", default=None)
    jupyter_workspace : Optional[JupyterWorkspaceSpec] = Field(alias="jupyterWorkspace", default=JupyterWorkspaceSpec())
    virtual_machine_workspace : Optional[VirtualMachineWorkspaceSpec] = Field(alias="virtualMachineWorkspace", default=None)
    
class AnalyticsWorkspaceBindingClaim(BaseModel):
    name : Optional[str] = Field(alias="name", default=None)
    operator : Optional[str] = Field(alias="operator", default=None)
    value : Optional[str] = Field(alias="value", default=None)

class AnalyticsWorkspaceBindingSpec(BaseModel):
    workspace : Optional[str] = Field(alias="workspace", default=None)
    expires : Optional[str] = Field(alias="expires", default=None)
    username : Optional[str] = Field(alias="username", default=None)
    comments : Optional[str] = Field(alias="comments", default=None)
    claims : Optional[list[AnalyticsWorkspaceBindingClaim]] = Field(alias="claims", default=None)

    def username_as_label(self):
        helper = KubernetesHelper()
        return helper.format_as_label(self.username) 

class AnalyticsWorkspaceBinding(BaseModel):
    api_version : Optional[str] = Field(alias="apiVersion", default="xlscsde.nhs.uk/v1")
    kind : Optional[str] = Field(alias="kind", default="AnalyticsWorkspaceBinding")
    metadata : Optional[KubernetesMetadata] = Field(alias="metadata", default=KubernetesMetadata())
    spec : Optional[AnalyticsWorkspaceBindingSpec] = Field(alias="spec", default=AnalyticsWorkspaceBindingSpec())
    status : Optional[AnalyticsWorkspaceBindingStatus] = Field(alias="status", default=AnalyticsWorkspaceBindingStatus())

    

class AnalyticsWorkspace(BaseModel):
    api_version : Optional[str] = Field(alias="apiVersion", default="xlscsde.nhs.uk/v1")
    kind : Optional[str] = Field(alias="kind", default="AnalyticsWorkspace")
    metadata : Optional[KubernetesMetadata] = Field(alias="metadata", default=KubernetesMetadata())
    spec : Optional[AnalyticsWorkspaceSpec] = Field(alias="spec", default=AnalyticsWorkspaceSpec())
    status : Optional[AnalyticsWorkspaceStatus] = Field(alias="status", default = AnalyticsWorkspaceStatus())
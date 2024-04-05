'''
# `hcp_waypoint_add_on_definition`

Refer to the Terraform Registry for docs: [`hcp_waypoint_add_on_definition`](https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class WaypointAddOnDefinition(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-hcp.waypointAddOnDefinition.WaypointAddOnDefinition",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition hcp_waypoint_add_on_definition}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: builtins.str,
        name: builtins.str,
        summary: builtins.str,
        terraform_cloud_workspace_details: typing.Union["WaypointAddOnDefinitionTerraformCloudWorkspaceDetails", typing.Dict[builtins.str, typing.Any]],
        terraform_no_code_module: typing.Union["WaypointAddOnDefinitionTerraformNoCodeModule", typing.Dict[builtins.str, typing.Any]],
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        project_id: typing.Optional[builtins.str] = None,
        readme_markdown_template: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition hcp_waypoint_add_on_definition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: A longer description of the Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#description WaypointAddOnDefinition#description}
        :param name: The name of the Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#name WaypointAddOnDefinition#name}
        :param summary: A short summary of the Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#summary WaypointAddOnDefinition#summary}
        :param terraform_cloud_workspace_details: Terraform Cloud Workspace details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_cloud_workspace_details WaypointAddOnDefinition#terraform_cloud_workspace_details}
        :param terraform_no_code_module: Terraform Cloud no-code Module details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_no_code_module WaypointAddOnDefinition#terraform_no_code_module}
        :param labels: List of labels attached to this Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#labels WaypointAddOnDefinition#labels}
        :param project_id: The ID of the HCP project where the Waypoint Add-on Definition is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#project_id WaypointAddOnDefinition#project_id}
        :param readme_markdown_template: The markdown template for the Add-on Definition README. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#readme_markdown_template WaypointAddOnDefinition#readme_markdown_template}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__228a48df25a261b668774144693c4eff33450f646342dbb58693c15b2c1aa9b9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WaypointAddOnDefinitionConfig(
            description=description,
            name=name,
            summary=summary,
            terraform_cloud_workspace_details=terraform_cloud_workspace_details,
            terraform_no_code_module=terraform_no_code_module,
            labels=labels,
            project_id=project_id,
            readme_markdown_template=readme_markdown_template,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a WaypointAddOnDefinition resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WaypointAddOnDefinition to import.
        :param import_from_id: The id of the existing WaypointAddOnDefinition that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WaypointAddOnDefinition to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a92ada119c0a532b472e365d34a9a0ffd135ffce66552e97a1b089d14db6e43)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putTerraformCloudWorkspaceDetails")
    def put_terraform_cloud_workspace_details(
        self,
        *,
        name: builtins.str,
        terraform_project_id: builtins.str,
    ) -> None:
        '''
        :param name: Name of the Terraform Cloud Workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#name WaypointAddOnDefinition#name}
        :param terraform_project_id: Tetraform Cloud Project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_project_id WaypointAddOnDefinition#terraform_project_id}
        '''
        value = WaypointAddOnDefinitionTerraformCloudWorkspaceDetails(
            name=name, terraform_project_id=terraform_project_id
        )

        return typing.cast(None, jsii.invoke(self, "putTerraformCloudWorkspaceDetails", [value]))

    @jsii.member(jsii_name="putTerraformNoCodeModule")
    def put_terraform_no_code_module(
        self,
        *,
        source: builtins.str,
        version: builtins.str,
    ) -> None:
        '''
        :param source: Terraform Cloud no-code Module Source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#source WaypointAddOnDefinition#source}
        :param version: Terraform Cloud no-code Module Version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#version WaypointAddOnDefinition#version}
        '''
        value = WaypointAddOnDefinitionTerraformNoCodeModule(
            source=source, version=version
        )

        return typing.cast(None, jsii.invoke(self, "putTerraformNoCodeModule", [value]))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetReadmeMarkdownTemplate")
    def reset_readme_markdown_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadmeMarkdownTemplate", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @builtins.property
    @jsii.member(jsii_name="terraformCloudWorkspaceDetails")
    def terraform_cloud_workspace_details(
        self,
    ) -> "WaypointAddOnDefinitionTerraformCloudWorkspaceDetailsOutputReference":
        return typing.cast("WaypointAddOnDefinitionTerraformCloudWorkspaceDetailsOutputReference", jsii.get(self, "terraformCloudWorkspaceDetails"))

    @builtins.property
    @jsii.member(jsii_name="terraformNoCodeModule")
    def terraform_no_code_module(
        self,
    ) -> "WaypointAddOnDefinitionTerraformNoCodeModuleOutputReference":
        return typing.cast("WaypointAddOnDefinitionTerraformNoCodeModuleOutputReference", jsii.get(self, "terraformNoCodeModule"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="readmeMarkdownTemplateInput")
    def readme_markdown_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readmeMarkdownTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="summaryInput")
    def summary_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "summaryInput"))

    @builtins.property
    @jsii.member(jsii_name="terraformCloudWorkspaceDetailsInput")
    def terraform_cloud_workspace_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointAddOnDefinitionTerraformCloudWorkspaceDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointAddOnDefinitionTerraformCloudWorkspaceDetails"]], jsii.get(self, "terraformCloudWorkspaceDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="terraformNoCodeModuleInput")
    def terraform_no_code_module_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointAddOnDefinitionTerraformNoCodeModule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointAddOnDefinitionTerraformNoCodeModule"]], jsii.get(self, "terraformNoCodeModuleInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__848b9ec45669c16c71902265fa5b2c111e23df57ca3b89561e2299ffd64d2685)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__437dbd9280036805298e97467c3303b62333bf8bb4610e30903dc895ca7b7a33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7eab7b2b83d1fbbfce11dfee65a0e63ba15f6715fb0b6cc7594642b8c804a53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdf644f29b299073cce6f2463c54a924ebd0d80084d04db9dfec8cce10a3ddd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value)

    @builtins.property
    @jsii.member(jsii_name="readmeMarkdownTemplate")
    def readme_markdown_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readmeMarkdownTemplate"))

    @readme_markdown_template.setter
    def readme_markdown_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f722d58a72bba34fdf713aca00de214a7e720ac0700ecaefd86c2417824760bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readmeMarkdownTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="summary")
    def summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "summary"))

    @summary.setter
    def summary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__605b12050a84e5c69b93ec0ff96f6886075d6e7a323a4e0008211b0a4569bdef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "summary", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-hcp.waypointAddOnDefinition.WaypointAddOnDefinitionConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "description": "description",
        "name": "name",
        "summary": "summary",
        "terraform_cloud_workspace_details": "terraformCloudWorkspaceDetails",
        "terraform_no_code_module": "terraformNoCodeModule",
        "labels": "labels",
        "project_id": "projectId",
        "readme_markdown_template": "readmeMarkdownTemplate",
    },
)
class WaypointAddOnDefinitionConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: builtins.str,
        name: builtins.str,
        summary: builtins.str,
        terraform_cloud_workspace_details: typing.Union["WaypointAddOnDefinitionTerraformCloudWorkspaceDetails", typing.Dict[builtins.str, typing.Any]],
        terraform_no_code_module: typing.Union["WaypointAddOnDefinitionTerraformNoCodeModule", typing.Dict[builtins.str, typing.Any]],
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        project_id: typing.Optional[builtins.str] = None,
        readme_markdown_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param description: A longer description of the Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#description WaypointAddOnDefinition#description}
        :param name: The name of the Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#name WaypointAddOnDefinition#name}
        :param summary: A short summary of the Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#summary WaypointAddOnDefinition#summary}
        :param terraform_cloud_workspace_details: Terraform Cloud Workspace details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_cloud_workspace_details WaypointAddOnDefinition#terraform_cloud_workspace_details}
        :param terraform_no_code_module: Terraform Cloud no-code Module details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_no_code_module WaypointAddOnDefinition#terraform_no_code_module}
        :param labels: List of labels attached to this Add-on Definition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#labels WaypointAddOnDefinition#labels}
        :param project_id: The ID of the HCP project where the Waypoint Add-on Definition is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#project_id WaypointAddOnDefinition#project_id}
        :param readme_markdown_template: The markdown template for the Add-on Definition README. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#readme_markdown_template WaypointAddOnDefinition#readme_markdown_template}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(terraform_cloud_workspace_details, dict):
            terraform_cloud_workspace_details = WaypointAddOnDefinitionTerraformCloudWorkspaceDetails(**terraform_cloud_workspace_details)
        if isinstance(terraform_no_code_module, dict):
            terraform_no_code_module = WaypointAddOnDefinitionTerraformNoCodeModule(**terraform_no_code_module)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a40a2cbc7571adb614c8a0532c8a86107dd834e783021898b5df56a91c33947c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument summary", value=summary, expected_type=type_hints["summary"])
            check_type(argname="argument terraform_cloud_workspace_details", value=terraform_cloud_workspace_details, expected_type=type_hints["terraform_cloud_workspace_details"])
            check_type(argname="argument terraform_no_code_module", value=terraform_no_code_module, expected_type=type_hints["terraform_no_code_module"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument readme_markdown_template", value=readme_markdown_template, expected_type=type_hints["readme_markdown_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "name": name,
            "summary": summary,
            "terraform_cloud_workspace_details": terraform_cloud_workspace_details,
            "terraform_no_code_module": terraform_no_code_module,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if labels is not None:
            self._values["labels"] = labels
        if project_id is not None:
            self._values["project_id"] = project_id
        if readme_markdown_template is not None:
            self._values["readme_markdown_template"] = readme_markdown_template

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def description(self) -> builtins.str:
        '''A longer description of the Add-on Definition.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#description WaypointAddOnDefinition#description}
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Add-on Definition.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#name WaypointAddOnDefinition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def summary(self) -> builtins.str:
        '''A short summary of the Add-on Definition.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#summary WaypointAddOnDefinition#summary}
        '''
        result = self._values.get("summary")
        assert result is not None, "Required property 'summary' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def terraform_cloud_workspace_details(
        self,
    ) -> "WaypointAddOnDefinitionTerraformCloudWorkspaceDetails":
        '''Terraform Cloud Workspace details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_cloud_workspace_details WaypointAddOnDefinition#terraform_cloud_workspace_details}
        '''
        result = self._values.get("terraform_cloud_workspace_details")
        assert result is not None, "Required property 'terraform_cloud_workspace_details' is missing"
        return typing.cast("WaypointAddOnDefinitionTerraformCloudWorkspaceDetails", result)

    @builtins.property
    def terraform_no_code_module(
        self,
    ) -> "WaypointAddOnDefinitionTerraformNoCodeModule":
        '''Terraform Cloud no-code Module details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_no_code_module WaypointAddOnDefinition#terraform_no_code_module}
        '''
        result = self._values.get("terraform_no_code_module")
        assert result is not None, "Required property 'terraform_no_code_module' is missing"
        return typing.cast("WaypointAddOnDefinitionTerraformNoCodeModule", result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of labels attached to this Add-on Definition.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#labels WaypointAddOnDefinition#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the HCP project where the Waypoint Add-on Definition is located.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#project_id WaypointAddOnDefinition#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme_markdown_template(self) -> typing.Optional[builtins.str]:
        '''The markdown template for the Add-on Definition README.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#readme_markdown_template WaypointAddOnDefinition#readme_markdown_template}
        '''
        result = self._values.get("readme_markdown_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaypointAddOnDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-hcp.waypointAddOnDefinition.WaypointAddOnDefinitionTerraformCloudWorkspaceDetails",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "terraform_project_id": "terraformProjectId"},
)
class WaypointAddOnDefinitionTerraformCloudWorkspaceDetails:
    def __init__(
        self,
        *,
        name: builtins.str,
        terraform_project_id: builtins.str,
    ) -> None:
        '''
        :param name: Name of the Terraform Cloud Workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#name WaypointAddOnDefinition#name}
        :param terraform_project_id: Tetraform Cloud Project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_project_id WaypointAddOnDefinition#terraform_project_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47af780e6812a10dbd9e57daea3b71738809a49206fca17d31d7a6b3b2315fac)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument terraform_project_id", value=terraform_project_id, expected_type=type_hints["terraform_project_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "terraform_project_id": terraform_project_id,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Terraform Cloud Workspace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#name WaypointAddOnDefinition#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def terraform_project_id(self) -> builtins.str:
        '''Tetraform Cloud Project ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#terraform_project_id WaypointAddOnDefinition#terraform_project_id}
        '''
        result = self._values.get("terraform_project_id")
        assert result is not None, "Required property 'terraform_project_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaypointAddOnDefinitionTerraformCloudWorkspaceDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WaypointAddOnDefinitionTerraformCloudWorkspaceDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-hcp.waypointAddOnDefinition.WaypointAddOnDefinitionTerraformCloudWorkspaceDetailsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46eec1c20996930cb3e69621bd80aff391b9259e1d65b7281201ebcc5c8f7bd9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="terraformProjectIdInput")
    def terraform_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "terraformProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6da2bbe02b80a5b4b00120c0196d7dcbf1dd48fcd0ee500a0f032a7f3de467a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="terraformProjectId")
    def terraform_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "terraformProjectId"))

    @terraform_project_id.setter
    def terraform_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef9d847eb5b9b53c5832551b5df56d2edd77dd25d0b987551d6839fd3a1b2f84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformProjectId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformCloudWorkspaceDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformCloudWorkspaceDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformCloudWorkspaceDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3855be17e5c38327e1dbc815a7d66891eabf9e89c72d00cd00c99afbad885787)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-hcp.waypointAddOnDefinition.WaypointAddOnDefinitionTerraformNoCodeModule",
    jsii_struct_bases=[],
    name_mapping={"source": "source", "version": "version"},
)
class WaypointAddOnDefinitionTerraformNoCodeModule:
    def __init__(self, *, source: builtins.str, version: builtins.str) -> None:
        '''
        :param source: Terraform Cloud no-code Module Source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#source WaypointAddOnDefinition#source}
        :param version: Terraform Cloud no-code Module Version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#version WaypointAddOnDefinition#version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7e5cead345c6408d898f55df7d236b3ceb955fc76dd57df7eee8dad5e9c6da4)
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source": source,
            "version": version,
        }

    @builtins.property
    def source(self) -> builtins.str:
        '''Terraform Cloud no-code Module Source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#source WaypointAddOnDefinition#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Terraform Cloud no-code Module Version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_add_on_definition#version WaypointAddOnDefinition#version}
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaypointAddOnDefinitionTerraformNoCodeModule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WaypointAddOnDefinitionTerraformNoCodeModuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-hcp.waypointAddOnDefinition.WaypointAddOnDefinitionTerraformNoCodeModuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64f33e63f24bd03782065fb0620b6f842e0f380202d9c1f133b2350ae9e48140)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3b35cd3e86cbbfa4ae743c2537d23cd42b6c1f15ee1faf677af3148a1c8554c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__610e657aec6e511e6c297db19eaa2d283b66447abbf6a87603feae04fe1d8d5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformNoCodeModule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformNoCodeModule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformNoCodeModule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d29341b3051fcad7fc026d871230b6961aeb50c58c7142910877b8b8b7ea582)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "WaypointAddOnDefinition",
    "WaypointAddOnDefinitionConfig",
    "WaypointAddOnDefinitionTerraformCloudWorkspaceDetails",
    "WaypointAddOnDefinitionTerraformCloudWorkspaceDetailsOutputReference",
    "WaypointAddOnDefinitionTerraformNoCodeModule",
    "WaypointAddOnDefinitionTerraformNoCodeModuleOutputReference",
]

publication.publish()

def _typecheckingstub__228a48df25a261b668774144693c4eff33450f646342dbb58693c15b2c1aa9b9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: builtins.str,
    name: builtins.str,
    summary: builtins.str,
    terraform_cloud_workspace_details: typing.Union[WaypointAddOnDefinitionTerraformCloudWorkspaceDetails, typing.Dict[builtins.str, typing.Any]],
    terraform_no_code_module: typing.Union[WaypointAddOnDefinitionTerraformNoCodeModule, typing.Dict[builtins.str, typing.Any]],
    labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    project_id: typing.Optional[builtins.str] = None,
    readme_markdown_template: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a92ada119c0a532b472e365d34a9a0ffd135ffce66552e97a1b089d14db6e43(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__848b9ec45669c16c71902265fa5b2c111e23df57ca3b89561e2299ffd64d2685(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__437dbd9280036805298e97467c3303b62333bf8bb4610e30903dc895ca7b7a33(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7eab7b2b83d1fbbfce11dfee65a0e63ba15f6715fb0b6cc7594642b8c804a53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdf644f29b299073cce6f2463c54a924ebd0d80084d04db9dfec8cce10a3ddd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f722d58a72bba34fdf713aca00de214a7e720ac0700ecaefd86c2417824760bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__605b12050a84e5c69b93ec0ff96f6886075d6e7a323a4e0008211b0a4569bdef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a40a2cbc7571adb614c8a0532c8a86107dd834e783021898b5df56a91c33947c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: builtins.str,
    name: builtins.str,
    summary: builtins.str,
    terraform_cloud_workspace_details: typing.Union[WaypointAddOnDefinitionTerraformCloudWorkspaceDetails, typing.Dict[builtins.str, typing.Any]],
    terraform_no_code_module: typing.Union[WaypointAddOnDefinitionTerraformNoCodeModule, typing.Dict[builtins.str, typing.Any]],
    labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    project_id: typing.Optional[builtins.str] = None,
    readme_markdown_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47af780e6812a10dbd9e57daea3b71738809a49206fca17d31d7a6b3b2315fac(
    *,
    name: builtins.str,
    terraform_project_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46eec1c20996930cb3e69621bd80aff391b9259e1d65b7281201ebcc5c8f7bd9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6da2bbe02b80a5b4b00120c0196d7dcbf1dd48fcd0ee500a0f032a7f3de467a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef9d847eb5b9b53c5832551b5df56d2edd77dd25d0b987551d6839fd3a1b2f84(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3855be17e5c38327e1dbc815a7d66891eabf9e89c72d00cd00c99afbad885787(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformCloudWorkspaceDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7e5cead345c6408d898f55df7d236b3ceb955fc76dd57df7eee8dad5e9c6da4(
    *,
    source: builtins.str,
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64f33e63f24bd03782065fb0620b6f842e0f380202d9c1f133b2350ae9e48140(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b35cd3e86cbbfa4ae743c2537d23cd42b6c1f15ee1faf677af3148a1c8554c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__610e657aec6e511e6c297db19eaa2d283b66447abbf6a87603feae04fe1d8d5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d29341b3051fcad7fc026d871230b6961aeb50c58c7142910877b8b8b7ea582(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointAddOnDefinitionTerraformNoCodeModule]],
) -> None:
    """Type checking stubs"""
    pass

'''
# `hcp_waypoint_application_template`

Refer to the Terraform Registry for docs: [`hcp_waypoint_application_template`](https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template).
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


class WaypointApplicationTemplate(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-hcp.waypointApplicationTemplate.WaypointApplicationTemplate",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template hcp_waypoint_application_template}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        summary: builtins.str,
        terraform_cloud_workspace_details: typing.Union["WaypointApplicationTemplateTerraformCloudWorkspaceDetails", typing.Dict[builtins.str, typing.Any]],
        terraform_no_code_module: typing.Union["WaypointApplicationTemplateTerraformNoCodeModule", typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template hcp_waypoint_application_template} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Application Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#name WaypointApplicationTemplate#name}
        :param summary: A brief description of the template, up to 110 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#summary WaypointApplicationTemplate#summary}
        :param terraform_cloud_workspace_details: Terraform Cloud Workspace details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_cloud_workspace_details WaypointApplicationTemplate#terraform_cloud_workspace_details}
        :param terraform_no_code_module: Terraform Cloud No-Code Module details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_no_code_module WaypointApplicationTemplate#terraform_no_code_module}
        :param description: A description of the template, along with when and why it should be used, up to 500 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#description WaypointApplicationTemplate#description}
        :param labels: List of labels attached to this Application Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#labels WaypointApplicationTemplate#labels}
        :param project_id: The ID of the HCP project where the Waypoint Application Template is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#project_id WaypointApplicationTemplate#project_id}
        :param readme_markdown_template: Instructions for using the template (markdown format supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#readme_markdown_template WaypointApplicationTemplate#readme_markdown_template}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88707a0e918bb0f513ce5e331d14349a4276577aba72f2a883f54e030d999648)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WaypointApplicationTemplateConfig(
            name=name,
            summary=summary,
            terraform_cloud_workspace_details=terraform_cloud_workspace_details,
            terraform_no_code_module=terraform_no_code_module,
            description=description,
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
        '''Generates CDKTF code for importing a WaypointApplicationTemplate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WaypointApplicationTemplate to import.
        :param import_from_id: The id of the existing WaypointApplicationTemplate that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WaypointApplicationTemplate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89f3a053652f618fbcfc9cbff36232f736896b17bfbc8d6d8f2836d6361c6aef)
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
        :param name: Name of the Terraform Cloud Workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#name WaypointApplicationTemplate#name}
        :param terraform_project_id: Terraform Cloud Project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_project_id WaypointApplicationTemplate#terraform_project_id}
        '''
        value = WaypointApplicationTemplateTerraformCloudWorkspaceDetails(
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
        :param source: No-Code Module Source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#source WaypointApplicationTemplate#source}
        :param version: No-Code Module Version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#version WaypointApplicationTemplate#version}
        '''
        value = WaypointApplicationTemplateTerraformNoCodeModule(
            source=source, version=version
        )

        return typing.cast(None, jsii.invoke(self, "putTerraformNoCodeModule", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    ) -> "WaypointApplicationTemplateTerraformCloudWorkspaceDetailsOutputReference":
        return typing.cast("WaypointApplicationTemplateTerraformCloudWorkspaceDetailsOutputReference", jsii.get(self, "terraformCloudWorkspaceDetails"))

    @builtins.property
    @jsii.member(jsii_name="terraformNoCodeModule")
    def terraform_no_code_module(
        self,
    ) -> "WaypointApplicationTemplateTerraformNoCodeModuleOutputReference":
        return typing.cast("WaypointApplicationTemplateTerraformNoCodeModuleOutputReference", jsii.get(self, "terraformNoCodeModule"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointApplicationTemplateTerraformCloudWorkspaceDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointApplicationTemplateTerraformCloudWorkspaceDetails"]], jsii.get(self, "terraformCloudWorkspaceDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="terraformNoCodeModuleInput")
    def terraform_no_code_module_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointApplicationTemplateTerraformNoCodeModule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WaypointApplicationTemplateTerraformNoCodeModule"]], jsii.get(self, "terraformNoCodeModuleInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97e680e8778a31cac8f5d031fd3d30c1ca4ccf04192b89a03de9541c276f5c85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d8c5c6bcee01a48af7b3be658ec937c5a09329ada87c9797604eb28417d1b1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad5e079f162c23a874576b9ee086415df8e82cb9a82ac17ea779671f267bd9c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c3b12bba6dce52fe546e83bd66cd47bfd6b840f4fa334159be0e70d65efe9a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value)

    @builtins.property
    @jsii.member(jsii_name="readmeMarkdownTemplate")
    def readme_markdown_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readmeMarkdownTemplate"))

    @readme_markdown_template.setter
    def readme_markdown_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b40da882bc9192ae3f55dbee57cc5f135d268e11fe9a57421f2f729590164498)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readmeMarkdownTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="summary")
    def summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "summary"))

    @summary.setter
    def summary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c4ac3f134814a186bf1570e0b18f965ca3fbdfc4ad5b72b147c54969eea959b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "summary", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-hcp.waypointApplicationTemplate.WaypointApplicationTemplateConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "summary": "summary",
        "terraform_cloud_workspace_details": "terraformCloudWorkspaceDetails",
        "terraform_no_code_module": "terraformNoCodeModule",
        "description": "description",
        "labels": "labels",
        "project_id": "projectId",
        "readme_markdown_template": "readmeMarkdownTemplate",
    },
)
class WaypointApplicationTemplateConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        summary: builtins.str,
        terraform_cloud_workspace_details: typing.Union["WaypointApplicationTemplateTerraformCloudWorkspaceDetails", typing.Dict[builtins.str, typing.Any]],
        terraform_no_code_module: typing.Union["WaypointApplicationTemplateTerraformNoCodeModule", typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
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
        :param name: The name of the Application Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#name WaypointApplicationTemplate#name}
        :param summary: A brief description of the template, up to 110 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#summary WaypointApplicationTemplate#summary}
        :param terraform_cloud_workspace_details: Terraform Cloud Workspace details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_cloud_workspace_details WaypointApplicationTemplate#terraform_cloud_workspace_details}
        :param terraform_no_code_module: Terraform Cloud No-Code Module details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_no_code_module WaypointApplicationTemplate#terraform_no_code_module}
        :param description: A description of the template, along with when and why it should be used, up to 500 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#description WaypointApplicationTemplate#description}
        :param labels: List of labels attached to this Application Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#labels WaypointApplicationTemplate#labels}
        :param project_id: The ID of the HCP project where the Waypoint Application Template is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#project_id WaypointApplicationTemplate#project_id}
        :param readme_markdown_template: Instructions for using the template (markdown format supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#readme_markdown_template WaypointApplicationTemplate#readme_markdown_template}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(terraform_cloud_workspace_details, dict):
            terraform_cloud_workspace_details = WaypointApplicationTemplateTerraformCloudWorkspaceDetails(**terraform_cloud_workspace_details)
        if isinstance(terraform_no_code_module, dict):
            terraform_no_code_module = WaypointApplicationTemplateTerraformNoCodeModule(**terraform_no_code_module)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa0a113fb8f77042be69bd07ebb4e4da31e8e210d39470abf1737ec777cdeaa6)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument summary", value=summary, expected_type=type_hints["summary"])
            check_type(argname="argument terraform_cloud_workspace_details", value=terraform_cloud_workspace_details, expected_type=type_hints["terraform_cloud_workspace_details"])
            check_type(argname="argument terraform_no_code_module", value=terraform_no_code_module, expected_type=type_hints["terraform_no_code_module"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument readme_markdown_template", value=readme_markdown_template, expected_type=type_hints["readme_markdown_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if description is not None:
            self._values["description"] = description
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
    def name(self) -> builtins.str:
        '''The name of the Application Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#name WaypointApplicationTemplate#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def summary(self) -> builtins.str:
        '''A brief description of the template, up to 110 characters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#summary WaypointApplicationTemplate#summary}
        '''
        result = self._values.get("summary")
        assert result is not None, "Required property 'summary' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def terraform_cloud_workspace_details(
        self,
    ) -> "WaypointApplicationTemplateTerraformCloudWorkspaceDetails":
        '''Terraform Cloud Workspace details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_cloud_workspace_details WaypointApplicationTemplate#terraform_cloud_workspace_details}
        '''
        result = self._values.get("terraform_cloud_workspace_details")
        assert result is not None, "Required property 'terraform_cloud_workspace_details' is missing"
        return typing.cast("WaypointApplicationTemplateTerraformCloudWorkspaceDetails", result)

    @builtins.property
    def terraform_no_code_module(
        self,
    ) -> "WaypointApplicationTemplateTerraformNoCodeModule":
        '''Terraform Cloud No-Code Module details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_no_code_module WaypointApplicationTemplate#terraform_no_code_module}
        '''
        result = self._values.get("terraform_no_code_module")
        assert result is not None, "Required property 'terraform_no_code_module' is missing"
        return typing.cast("WaypointApplicationTemplateTerraformNoCodeModule", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the template, along with when and why it should be used, up to 500 characters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#description WaypointApplicationTemplate#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of labels attached to this Application Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#labels WaypointApplicationTemplate#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the HCP project where the Waypoint Application Template is located.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#project_id WaypointApplicationTemplate#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme_markdown_template(self) -> typing.Optional[builtins.str]:
        '''Instructions for using the template (markdown format supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#readme_markdown_template WaypointApplicationTemplate#readme_markdown_template}
        '''
        result = self._values.get("readme_markdown_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaypointApplicationTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-hcp.waypointApplicationTemplate.WaypointApplicationTemplateTerraformCloudWorkspaceDetails",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "terraform_project_id": "terraformProjectId"},
)
class WaypointApplicationTemplateTerraformCloudWorkspaceDetails:
    def __init__(
        self,
        *,
        name: builtins.str,
        terraform_project_id: builtins.str,
    ) -> None:
        '''
        :param name: Name of the Terraform Cloud Workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#name WaypointApplicationTemplate#name}
        :param terraform_project_id: Terraform Cloud Project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_project_id WaypointApplicationTemplate#terraform_project_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e50db9335889d5c3d1f29d26b8927a85e30dc255fef58910ff5477f03bda1a41)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument terraform_project_id", value=terraform_project_id, expected_type=type_hints["terraform_project_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "terraform_project_id": terraform_project_id,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Terraform Cloud Workspace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#name WaypointApplicationTemplate#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def terraform_project_id(self) -> builtins.str:
        '''Terraform Cloud Project ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#terraform_project_id WaypointApplicationTemplate#terraform_project_id}
        '''
        result = self._values.get("terraform_project_id")
        assert result is not None, "Required property 'terraform_project_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaypointApplicationTemplateTerraformCloudWorkspaceDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WaypointApplicationTemplateTerraformCloudWorkspaceDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-hcp.waypointApplicationTemplate.WaypointApplicationTemplateTerraformCloudWorkspaceDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__405ec5458ffc4a06fe36e495a96f72b8eb024a64edf2f49c27c56c4a77e56891)
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
            type_hints = typing.get_type_hints(_typecheckingstub__33f804127aabf5d852c25cda34412e3254c8a3871ff16dc19b42a66d2fbb0af0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="terraformProjectId")
    def terraform_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "terraformProjectId"))

    @terraform_project_id.setter
    def terraform_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e91b28bdee80d1df61334be5dea601f4992ba5bc18cc52567189019316e907f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformProjectId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformCloudWorkspaceDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformCloudWorkspaceDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformCloudWorkspaceDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37a1209f2d1d19bfdd009e2fc10c8ceaf5debf1bfeb3c528f8eb82e4faf6ca99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-hcp.waypointApplicationTemplate.WaypointApplicationTemplateTerraformNoCodeModule",
    jsii_struct_bases=[],
    name_mapping={"source": "source", "version": "version"},
)
class WaypointApplicationTemplateTerraformNoCodeModule:
    def __init__(self, *, source: builtins.str, version: builtins.str) -> None:
        '''
        :param source: No-Code Module Source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#source WaypointApplicationTemplate#source}
        :param version: No-Code Module Version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#version WaypointApplicationTemplate#version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f551c6bbb31a915ce786a326a050cbaa9c547859ed71eb6a1b8879f5c9fd783e)
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source": source,
            "version": version,
        }

    @builtins.property
    def source(self) -> builtins.str:
        '''No-Code Module Source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#source WaypointApplicationTemplate#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''No-Code Module Version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/hcp/0.86.0/docs/resources/waypoint_application_template#version WaypointApplicationTemplate#version}
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaypointApplicationTemplateTerraformNoCodeModule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WaypointApplicationTemplateTerraformNoCodeModuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-hcp.waypointApplicationTemplate.WaypointApplicationTemplateTerraformNoCodeModuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b10a76d33cfd19bba4b5e83854e38105a608440cac158f747bb69dffb749361)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7fd4977245bed39ddb8af380cdec7faf3f99f08514bf8486f3455d6f448c1ab0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0eb5d67f5b0d172143959c395b915c322e3ca5e2aa18a3765c0776c2e593308)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformNoCodeModule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformNoCodeModule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformNoCodeModule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f29e0a8c3cbb57729bf316690fdfe882bdab9255ab6ce0fe0cf9c6ee9b85f02d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "WaypointApplicationTemplate",
    "WaypointApplicationTemplateConfig",
    "WaypointApplicationTemplateTerraformCloudWorkspaceDetails",
    "WaypointApplicationTemplateTerraformCloudWorkspaceDetailsOutputReference",
    "WaypointApplicationTemplateTerraformNoCodeModule",
    "WaypointApplicationTemplateTerraformNoCodeModuleOutputReference",
]

publication.publish()

def _typecheckingstub__88707a0e918bb0f513ce5e331d14349a4276577aba72f2a883f54e030d999648(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    summary: builtins.str,
    terraform_cloud_workspace_details: typing.Union[WaypointApplicationTemplateTerraformCloudWorkspaceDetails, typing.Dict[builtins.str, typing.Any]],
    terraform_no_code_module: typing.Union[WaypointApplicationTemplateTerraformNoCodeModule, typing.Dict[builtins.str, typing.Any]],
    description: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__89f3a053652f618fbcfc9cbff36232f736896b17bfbc8d6d8f2836d6361c6aef(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97e680e8778a31cac8f5d031fd3d30c1ca4ccf04192b89a03de9541c276f5c85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d8c5c6bcee01a48af7b3be658ec937c5a09329ada87c9797604eb28417d1b1d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad5e079f162c23a874576b9ee086415df8e82cb9a82ac17ea779671f267bd9c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c3b12bba6dce52fe546e83bd66cd47bfd6b840f4fa334159be0e70d65efe9a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b40da882bc9192ae3f55dbee57cc5f135d268e11fe9a57421f2f729590164498(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c4ac3f134814a186bf1570e0b18f965ca3fbdfc4ad5b72b147c54969eea959b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa0a113fb8f77042be69bd07ebb4e4da31e8e210d39470abf1737ec777cdeaa6(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    summary: builtins.str,
    terraform_cloud_workspace_details: typing.Union[WaypointApplicationTemplateTerraformCloudWorkspaceDetails, typing.Dict[builtins.str, typing.Any]],
    terraform_no_code_module: typing.Union[WaypointApplicationTemplateTerraformNoCodeModule, typing.Dict[builtins.str, typing.Any]],
    description: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    project_id: typing.Optional[builtins.str] = None,
    readme_markdown_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e50db9335889d5c3d1f29d26b8927a85e30dc255fef58910ff5477f03bda1a41(
    *,
    name: builtins.str,
    terraform_project_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__405ec5458ffc4a06fe36e495a96f72b8eb024a64edf2f49c27c56c4a77e56891(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33f804127aabf5d852c25cda34412e3254c8a3871ff16dc19b42a66d2fbb0af0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e91b28bdee80d1df61334be5dea601f4992ba5bc18cc52567189019316e907f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a1209f2d1d19bfdd009e2fc10c8ceaf5debf1bfeb3c528f8eb82e4faf6ca99(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformCloudWorkspaceDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f551c6bbb31a915ce786a326a050cbaa9c547859ed71eb6a1b8879f5c9fd783e(
    *,
    source: builtins.str,
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b10a76d33cfd19bba4b5e83854e38105a608440cac158f747bb69dffb749361(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fd4977245bed39ddb8af380cdec7faf3f99f08514bf8486f3455d6f448c1ab0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0eb5d67f5b0d172143959c395b915c322e3ca5e2aa18a3765c0776c2e593308(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f29e0a8c3cbb57729bf316690fdfe882bdab9255ab6ce0fe0cf9c6ee9b85f02d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WaypointApplicationTemplateTerraformNoCodeModule]],
) -> None:
    """Type checking stubs"""
    pass

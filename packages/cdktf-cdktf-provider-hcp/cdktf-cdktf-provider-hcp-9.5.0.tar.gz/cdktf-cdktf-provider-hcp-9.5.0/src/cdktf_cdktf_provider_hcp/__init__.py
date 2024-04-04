'''
# CDKTF prebuilt bindings for hashicorp/hcp provider version 0.85.0

This repo builds and publishes the [Terraform hcp provider](https://registry.terraform.io/providers/hashicorp/hcp/0.85.0/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-hcp](https://www.npmjs.com/package/@cdktf/provider-hcp).

`npm install @cdktf/provider-hcp`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-hcp](https://pypi.org/project/cdktf-cdktf-provider-hcp).

`pipenv install cdktf-cdktf-provider-hcp`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Hcp](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Hcp).

`dotnet add package HashiCorp.Cdktf.Providers.Hcp`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-hcp](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-hcp).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-hcp</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-hcp-go`](https://github.com/cdktf/cdktf-provider-hcp-go) package.

`go get github.com/cdktf/cdktf-provider-hcp-go/hcp/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-hcp-go/blob/main/hcp/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-hcp).

## Versioning

This project is explicitly not tracking the Terraform hcp provider version 1:1. In fact, it always tracks `latest` of `~> 0.45` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform hcp provider](https://registry.terraform.io/providers/hashicorp/hcp/0.85.0)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

from ._jsii import *

__all__ = [
    "aws_network_peering",
    "aws_transit_gateway_attachment",
    "azure_peering_connection",
    "boundary_cluster",
    "consul_cluster",
    "consul_cluster_root_token",
    "consul_snapshot",
    "data_hcp_aws_network_peering",
    "data_hcp_aws_transit_gateway_attachment",
    "data_hcp_azure_peering_connection",
    "data_hcp_boundary_cluster",
    "data_hcp_consul_agent_helm_config",
    "data_hcp_consul_agent_kubernetes_secret",
    "data_hcp_consul_cluster",
    "data_hcp_consul_versions",
    "data_hcp_group",
    "data_hcp_hvn",
    "data_hcp_hvn_peering_connection",
    "data_hcp_hvn_route",
    "data_hcp_iam_policy",
    "data_hcp_organization",
    "data_hcp_packer_artifact",
    "data_hcp_packer_bucket_names",
    "data_hcp_packer_run_task",
    "data_hcp_packer_version",
    "data_hcp_project",
    "data_hcp_service_principal",
    "data_hcp_user_principal",
    "data_hcp_vault_cluster",
    "data_hcp_vault_plugin",
    "data_hcp_vault_secrets_app",
    "data_hcp_vault_secrets_secret",
    "data_hcp_waypoint_add_on_definition",
    "data_hcp_waypoint_application",
    "data_hcp_waypoint_application_template",
    "group",
    "group_members",
    "hvn",
    "hvn_peering_connection",
    "hvn_route",
    "iam_workload_identity_provider",
    "log_streaming_destination",
    "notifications_webhook",
    "organization_iam_binding",
    "organization_iam_policy",
    "packer_channel",
    "packer_channel_assignment",
    "packer_run_task",
    "project",
    "project_iam_binding",
    "project_iam_policy",
    "provider",
    "service_principal",
    "service_principal_key",
    "vault_cluster",
    "vault_cluster_admin_token",
    "vault_plugin",
    "vault_secrets_app",
    "vault_secrets_secret",
    "waypoint_add_on_definition",
    "waypoint_application",
    "waypoint_application_template",
    "waypoint_tfc_config",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import aws_network_peering
from . import aws_transit_gateway_attachment
from . import azure_peering_connection
from . import boundary_cluster
from . import consul_cluster
from . import consul_cluster_root_token
from . import consul_snapshot
from . import data_hcp_aws_network_peering
from . import data_hcp_aws_transit_gateway_attachment
from . import data_hcp_azure_peering_connection
from . import data_hcp_boundary_cluster
from . import data_hcp_consul_agent_helm_config
from . import data_hcp_consul_agent_kubernetes_secret
from . import data_hcp_consul_cluster
from . import data_hcp_consul_versions
from . import data_hcp_group
from . import data_hcp_hvn
from . import data_hcp_hvn_peering_connection
from . import data_hcp_hvn_route
from . import data_hcp_iam_policy
from . import data_hcp_organization
from . import data_hcp_packer_artifact
from . import data_hcp_packer_bucket_names
from . import data_hcp_packer_run_task
from . import data_hcp_packer_version
from . import data_hcp_project
from . import data_hcp_service_principal
from . import data_hcp_user_principal
from . import data_hcp_vault_cluster
from . import data_hcp_vault_plugin
from . import data_hcp_vault_secrets_app
from . import data_hcp_vault_secrets_secret
from . import data_hcp_waypoint_add_on_definition
from . import data_hcp_waypoint_application
from . import data_hcp_waypoint_application_template
from . import group
from . import group_members
from . import hvn
from . import hvn_peering_connection
from . import hvn_route
from . import iam_workload_identity_provider
from . import log_streaming_destination
from . import notifications_webhook
from . import organization_iam_binding
from . import organization_iam_policy
from . import packer_channel
from . import packer_channel_assignment
from . import packer_run_task
from . import project
from . import project_iam_binding
from . import project_iam_policy
from . import provider
from . import service_principal
from . import service_principal_key
from . import vault_cluster
from . import vault_cluster_admin_token
from . import vault_plugin
from . import vault_secrets_app
from . import vault_secrets_secret
from . import waypoint_add_on_definition
from . import waypoint_application
from . import waypoint_application_template
from . import waypoint_tfc_config

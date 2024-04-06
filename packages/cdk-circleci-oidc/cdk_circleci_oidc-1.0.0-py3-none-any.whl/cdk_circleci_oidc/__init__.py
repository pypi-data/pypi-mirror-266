'''
# CircleCI OIDC

This repository contains constructs to communicate between CircleCI and AWS via an Open ID Connect (OIDC) provider. The
process is described in [this CircleCI blog post](https://circleci.com/blog/openid-connect-identity-tokens/).

## Security Benefits

By using the OpenID Connect provider, you can communicate with AWS from CircleCI without saving static credentials
(e.g., `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) in your CircleCI project settings or a context. Removing static
credentials, especially in light of the early 2023 [breach](https://circleci.com/blog/jan-4-2023-incident-report/), is a
best practice for security.

## Quick Start

Install the package:

```bash
npm install @blimmer/cdk-circleci-oidc

or

yarn add @blimmer/cdk-circleci-oidc
```

Then, create the provider and role(s).

```python
import { Stack, StackProps } from "aws-cdk-lib";
import { CircleCiOidcProvider, CircleCiOidcRole } from "@blimmer/cdk-circleci-oidc";
import { Construct } from "constructs";
import { ManagedPolicy, PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Bucket } from "aws-cdk-lib/aws-s3";

export class CircleCiStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // The provider is only created _once per AWS account_. It might make sense to define this in a separate stack
    // that defines more global resources. See below for how to use import the provider in stacks that don't define it.
    const provider = new CircleCiOidcProvider(this, "OidcProvider", {
      // Find your organization ID in the CircleCI dashboard under "Organization Settings"
      organizationId: "11111111-2222-3333-4444-555555555555",
    });

    const myCircleCiRole = new CircleCiOidcRole(this, "MyCircleCiRole", {
      provider,
      roleName: "MyCircleCiRole",

      // Pass some managed policies to the role
      managedPolicies: [ManagedPolicy.fromAwsManagedPolicyName("AmazonS3ReadOnlyAccess")],
    });

    // You can work with the CircleCI role like any other role
    myCircleCiRole.addToPolicy(
      new PolicyStatement({
        actions: ["s3:ListAllMyBuckets"],
        resources: ["*"],
      }),
    );

    // Including using `.grant` convenience methods
    const bucket = new Bucket(this, "MyBucket");
    bucket.grantRead(myCircleCiRole);
  }
}
```

Now, in your `.circleci/config.yml` file, you can use the
[AWS CLI Orb](https://circleci.com/developer/orbs/orb/circleci/aws-cli) to assume your new role.

```yaml
version: 2.1

orbs:
  aws-cli: circleci/aws-cli@4.1.0 # https://circleci.com/developer/orbs/orb/circleci/aws-cli

workflows:
  version: 2
  build:
    jobs:
      - oidc-job:
          context: oidc-assumption # You _must_ use a context, even if it doesn't contain any secrets (see https://circleci.com/docs/openid-connect-tokens/#openid-connect-id-token-availability)

jobs:
  oidc-job:
    docker:
      - image: cimg/base:stable
    steps:
      - checkout
      # https://circleci.com/developer/orbs/orb/circleci/aws-cli#commands-setup
      - aws-cli/setup:
          role_arn: "arn:aws:iam::123456789101:role/MyCircleCiRole"
      - run:
          name: List S3 Buckets
          command: aws s3 ls
```

## Usage in Stacks that Don't Define the Provider

The `CircleCiOidcProvider` is only created **once per account**. You can use the
`CircleCiOidcProvider.fromOrganizationId` method to import a previously created provider into any stack.

```python
import { Stack, StackProps } from "aws-cdk-lib";
import { CircleCiOidcRole, CircleCiOidcProvider } from "@blimmer/cdk-circleci-oidc";
import { Construct } from "constructs";

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const myCircleCiRole = new CircleCiOidcRole(this, "MyCircleCiRole", {
      provider: CircleCiOidcProvider.fromOrganizationId(this, "11111111-2222-3333-4444-555555555555"),
      roleName: "MyCircleCiRole",
    });
  }
}
```

## Usage

For detailed API docs, see [API.md](/API.md).

## Python

This package is available for Python as `cdk-circleci-oidc`.

```bash
pip install cdk-circleci-oidc
```

## Upgrading Between Major Versions

The API can be expected to change between major versions. Please consult the [UPGRADING docs](/UPGRADING.md.md) for for
information.

## Contributing

Contributions, issues, and feedback are welcome!
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiConfiguration",
    jsii_struct_bases=[],
    name_mapping={"provider": "provider", "project_ids": "projectIds"},
)
class CircleCiConfiguration:
    def __init__(
        self,
        *,
        provider: "ICircleCiOidcProvider",
        project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param provider: Reference to CircleCI OpenID Connect Provider configured in AWS IAM. Either pass an construct defined by ``new CircleCiOidcProvider`` or a retrieved reference from ``CircleCiOidcProvider.fromOrganizationId``. There can be only one (per AWS Account).
        :param project_ids: Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role. If you don't provide this value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format. Default: - All CircleCI projects in the provider's organization
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eab586ff05607d35fc5f8efd5281b65977e0f3fb2d81f3f891844470cefb35ea)
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument project_ids", value=project_ids, expected_type=type_hints["project_ids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "provider": provider,
        }
        if project_ids is not None:
            self._values["project_ids"] = project_ids

    @builtins.property
    def provider(self) -> "ICircleCiOidcProvider":
        '''Reference to CircleCI OpenID Connect Provider configured in AWS IAM.

        Either pass an construct defined by ``new CircleCiOidcProvider``
        or a retrieved reference from ``CircleCiOidcProvider.fromOrganizationId``.
        There can be only one (per AWS Account).
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast("ICircleCiOidcProvider", result)

    @builtins.property
    def project_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role.

        If you don't provide this
        value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a
        project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format.

        :default: - All CircleCI projects in the provider's organization
        '''
        result = self._values.get("project_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CircleCiConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcProviderProps",
    jsii_struct_bases=[],
    name_mapping={"organization_id": "organizationId", "thumbprints": "thumbprints"},
)
class CircleCiOidcProviderProps:
    def __init__(
        self,
        *,
        organization_id: builtins.str,
        thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param organization_id: The ID of your CircleCI organization. This is typically in a UUID format. You can find this ID in the CircleCI dashboard UI under the "Organization Settings" tab.
        :param thumbprints: The OIDC thumbprints used by the provider. You should not need to provide this value unless CircleCI suddenly rotates their OIDC thumbprints (e.g., in response to a security incident). If you do need to generate this thumbprint, you can follow the instructions here: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1393e64f485bb45467827f50708b32ad642b6fb53664b1862c1828b4be061413)
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument thumbprints", value=thumbprints, expected_type=type_hints["thumbprints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "organization_id": organization_id,
        }
        if thumbprints is not None:
            self._values["thumbprints"] = thumbprints

    @builtins.property
    def organization_id(self) -> builtins.str:
        '''The ID of your CircleCI organization.

        This is typically in a UUID format. You can find this ID in the CircleCI
        dashboard UI under the "Organization Settings" tab.
        '''
        result = self._values.get("organization_id")
        assert result is not None, "Required property 'organization_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def thumbprints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The OIDC thumbprints used by the provider.

        You should not need to provide this value unless CircleCI suddenly
        rotates their OIDC thumbprints (e.g., in response to a security incident).

        If you do need to generate this thumbprint, you can follow the instructions here:
        https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
        '''
        result = self._values.get("thumbprints")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CircleCiOidcProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CircleCiOidcRole(
    _aws_cdk_aws_iam_ceddda9d.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcRole",
):
    '''Define an IAM Role that can be assumed by a CircleCI Job via the CircleCI OpenID Connect Identity Provider.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        provider: "ICircleCiOidcProvider",
        project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param provider: Reference to CircleCI OpenID Connect Provider configured in AWS IAM. Either pass an construct defined by ``new CircleCiOidcProvider`` or a retrieved reference from ``CircleCiOidcProvider.fromOrganizationId``. There can be only one (per AWS Account).
        :param project_ids: Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role. If you don't provide this value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format. Default: - All CircleCI projects in the provider's organization
        :param description: A description of the role. It can be up to 1000 characters long. Default: - No description.
        :param external_ids: List of IDs that the role assumer needs to provide one of when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param managed_policies: A list of managed policies associated with this role. You can add managed policies later using ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``. Default: - No managed policies.
        :param max_session_duration: The maximum session duration that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: Duration.hours(1)
        :param path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
        :param permissions_boundary: AWS supports permissions boundaries for IAM entities (users or roles). A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. An entity's permissions boundary allows it to perform only the actions that are allowed by both its identity-based policies and its permissions boundaries. Default: - No permissions boundary.
        :param role_name: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the role name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a1d9304663f45d61bd197cf48bd3145a25be4318f85ebeec9bb3b566e0f0ba9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CircleCiOidcRoleProps(
            provider=provider,
            project_ids=project_ids,
            description=description,
            external_ids=external_ids,
            inline_policies=inline_policies,
            managed_policies=managed_policies,
            max_session_duration=max_session_duration,
            path=path,
            permissions_boundary=permissions_boundary,
            role_name=role_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.interface(jsii_type="@blimmer/cdk-circleci-oidc.ICircleCiOidcProvider")
class ICircleCiOidcProvider(typing_extensions.Protocol):
    '''Describes a CircleCI OpenID Connect Identity Provider for AWS IAM.'''

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        ...


class _ICircleCiOidcProviderProxy:
    '''Describes a CircleCI OpenID Connect Identity Provider for AWS IAM.'''

    __jsii_type__: typing.ClassVar[str] = "@blimmer/cdk-circleci-oidc.ICircleCiOidcProvider"

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICircleCiOidcProvider).__jsii_proxy_class__ = lambda : _ICircleCiOidcProviderProxy


@jsii.data_type(
    jsii_type="@blimmer/cdk-circleci-oidc.RoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "external_ids": "externalIds",
        "inline_policies": "inlinePolicies",
        "managed_policies": "managedPolicies",
        "max_session_duration": "maxSessionDuration",
        "path": "path",
        "permissions_boundary": "permissionsBoundary",
        "role_name": "roleName",
    },
)
class RoleProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''RoleProps.

        :param description: A description of the role. It can be up to 1000 characters long. Default: - No description.
        :param external_ids: List of IDs that the role assumer needs to provide one of when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param managed_policies: A list of managed policies associated with this role. You can add managed policies later using ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``. Default: - No managed policies.
        :param max_session_duration: The maximum session duration that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: Duration.hours(1)
        :param path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
        :param permissions_boundary: AWS supports permissions boundaries for IAM entities (users or roles). A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. An entity's permissions boundary allows it to perform only the actions that are allowed by both its identity-based policies and its permissions boundaries. Default: - No permissions boundary.
        :param role_name: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the role name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30f6776c1ccf1de8fc7c032c787078de37f3f66d205ead67cae11deb84fbb41a)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument external_ids", value=external_ids, expected_type=type_hints["external_ids"])
            check_type(argname="argument inline_policies", value=inline_policies, expected_type=type_hints["inline_policies"])
            check_type(argname="argument managed_policies", value=managed_policies, expected_type=type_hints["managed_policies"])
            check_type(argname="argument max_session_duration", value=max_session_duration, expected_type=type_hints["max_session_duration"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if external_ids is not None:
            self._values["external_ids"] = external_ids
        if inline_policies is not None:
            self._values["inline_policies"] = inline_policies
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if max_session_duration is not None:
            self._values["max_session_duration"] = max_session_duration
        if path is not None:
            self._values["path"] = path
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the role.

        It can be up to 1000 characters long.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IDs that the role assumer needs to provide one of when assuming this role.

        If the configured and provided external IDs do not match, the
        AssumeRole operation will fail.

        :default: No external ID required
        '''
        result = self._values.get("external_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def inline_policies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]]:
        '''A list of named policies to inline into this role.

        These policies will be
        created with the role, whereas those added by ``addToPolicy`` are added
        using a separate CloudFormation resource (allowing a way around circular
        dependencies that could otherwise be introduced).

        :default: - No policy is inlined in the Role resource.
        '''
        result = self._values.get("inline_policies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]]:
        '''A list of managed policies associated with this role.

        You can add managed policies later using
        ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``.

        :default: - No managed policies.
        '''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]], result)

    @builtins.property
    def max_session_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum session duration that you want to set for the specified role.

        This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours.

        Anyone who assumes the role from the AWS CLI or API can use the
        DurationSeconds API parameter or the duration-seconds CLI parameter to
        request a longer session. The MaxSessionDuration setting determines the
        maximum duration that can be requested using the DurationSeconds
        parameter.

        If users don't specify a value for the DurationSeconds parameter, their
        security credentials are valid for one hour by default. This applies when
        you use the AssumeRole* API operations or the assume-role* CLI operations
        but does not apply when you use those operations to create a console URL.

        :default: Duration.hours(1)

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html
        '''
        result = self._values.get("max_session_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path associated with this role.

        For information about IAM paths, see
        Friendly Names and Paths in IAM User Guide.

        :default: /
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]:
        '''AWS supports permissions boundaries for IAM entities (users or roles).

        A permissions boundary is an advanced feature for using a managed policy
        to set the maximum permissions that an identity-based policy can grant to
        an IAM entity. An entity's permissions boundary allows it to perform only
        the actions that are allowed by both its identity-based policies and its
        permissions boundaries.

        :default: - No permissions boundary.

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''A name for the IAM role.

        For valid values, see the RoleName parameter for
        the CreateRole action in the IAM API Reference.

        IMPORTANT: If you specify a name, you cannot perform updates that require
        replacement of this resource. You can perform updates that require no or
        some interruption. If you must replace the resource, specify a new name.

        If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to
        acknowledge your template's capabilities. For more information, see
        Acknowledging IAM Resources in AWS CloudFormation Templates.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the role name.
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ICircleCiOidcProvider)
class CircleCiOidcProvider(
    _aws_cdk_aws_iam_ceddda9d.CfnOIDCProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcProvider",
):
    '''This construct creates a CircleCI ODIC provider to allow AWS access from CircleCI jobs.

    You'll need to instantiate
    this construct once per AWS account you want to use CircleCI OIDC with.

    You can import a existing provider using ``CircleCiOidcProvider.fromOrganizationId``.

    To create a role that can be assumed by CircleCI jobs, use the ``CircleCiOidcRole`` construct.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        organization_id: builtins.str,
        thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param organization_id: The ID of your CircleCI organization. This is typically in a UUID format. You can find this ID in the CircleCI dashboard UI under the "Organization Settings" tab.
        :param thumbprints: The OIDC thumbprints used by the provider. You should not need to provide this value unless CircleCI suddenly rotates their OIDC thumbprints (e.g., in response to a security incident). If you do need to generate this thumbprint, you can follow the instructions here: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1633f8e2586bf0d50337d86af80f18850686241366bdb00da0c6d2e30c2f1b28)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CircleCiOidcProviderProps(
            organization_id=organization_id, thumbprints=thumbprints
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromOrganizationId")
    @builtins.classmethod
    def from_organization_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        organization_id: builtins.str,
    ) -> ICircleCiOidcProvider:
        '''
        :param scope: -
        :param organization_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fee2eb6189dca866c9ff6a10072625f160fb3e3e4386a0cc23c419d3f4ea1113)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
        return typing.cast(ICircleCiOidcProvider, jsii.sinvoke(cls, "fromOrganizationId", [scope, organization_id]))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))


@jsii.data_type(
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcRoleProps",
    jsii_struct_bases=[CircleCiConfiguration, RoleProps],
    name_mapping={
        "provider": "provider",
        "project_ids": "projectIds",
        "description": "description",
        "external_ids": "externalIds",
        "inline_policies": "inlinePolicies",
        "managed_policies": "managedPolicies",
        "max_session_duration": "maxSessionDuration",
        "path": "path",
        "permissions_boundary": "permissionsBoundary",
        "role_name": "roleName",
    },
)
class CircleCiOidcRoleProps(CircleCiConfiguration, RoleProps):
    def __init__(
        self,
        *,
        provider: ICircleCiOidcProvider,
        project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props that define the IAM Role that can be assumed by a CircleCI job via the CircleCI OpenID Connect Identity Provider.

        Besides {@link CircleCiConfiguration}, you may pass in any {@link RoleProps} except ``assumedBy``
        which will be defined by this construct.

        :param provider: Reference to CircleCI OpenID Connect Provider configured in AWS IAM. Either pass an construct defined by ``new CircleCiOidcProvider`` or a retrieved reference from ``CircleCiOidcProvider.fromOrganizationId``. There can be only one (per AWS Account).
        :param project_ids: Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role. If you don't provide this value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format. Default: - All CircleCI projects in the provider's organization
        :param description: A description of the role. It can be up to 1000 characters long. Default: - No description.
        :param external_ids: List of IDs that the role assumer needs to provide one of when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param managed_policies: A list of managed policies associated with this role. You can add managed policies later using ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``. Default: - No managed policies.
        :param max_session_duration: The maximum session duration that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: Duration.hours(1)
        :param path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
        :param permissions_boundary: AWS supports permissions boundaries for IAM entities (users or roles). A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. An entity's permissions boundary allows it to perform only the actions that are allowed by both its identity-based policies and its permissions boundaries. Default: - No permissions boundary.
        :param role_name: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the role name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28caf46e7e0d75fcdc4c1a3dec9aa2e5dff8efcf72c3adb43eab258081ffcf9)
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument project_ids", value=project_ids, expected_type=type_hints["project_ids"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument external_ids", value=external_ids, expected_type=type_hints["external_ids"])
            check_type(argname="argument inline_policies", value=inline_policies, expected_type=type_hints["inline_policies"])
            check_type(argname="argument managed_policies", value=managed_policies, expected_type=type_hints["managed_policies"])
            check_type(argname="argument max_session_duration", value=max_session_duration, expected_type=type_hints["max_session_duration"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "provider": provider,
        }
        if project_ids is not None:
            self._values["project_ids"] = project_ids
        if description is not None:
            self._values["description"] = description
        if external_ids is not None:
            self._values["external_ids"] = external_ids
        if inline_policies is not None:
            self._values["inline_policies"] = inline_policies
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if max_session_duration is not None:
            self._values["max_session_duration"] = max_session_duration
        if path is not None:
            self._values["path"] = path
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def provider(self) -> ICircleCiOidcProvider:
        '''Reference to CircleCI OpenID Connect Provider configured in AWS IAM.

        Either pass an construct defined by ``new CircleCiOidcProvider``
        or a retrieved reference from ``CircleCiOidcProvider.fromOrganizationId``.
        There can be only one (per AWS Account).
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(ICircleCiOidcProvider, result)

    @builtins.property
    def project_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role.

        If you don't provide this
        value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a
        project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format.

        :default: - All CircleCI projects in the provider's organization
        '''
        result = self._values.get("project_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the role.

        It can be up to 1000 characters long.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IDs that the role assumer needs to provide one of when assuming this role.

        If the configured and provided external IDs do not match, the
        AssumeRole operation will fail.

        :default: No external ID required
        '''
        result = self._values.get("external_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def inline_policies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]]:
        '''A list of named policies to inline into this role.

        These policies will be
        created with the role, whereas those added by ``addToPolicy`` are added
        using a separate CloudFormation resource (allowing a way around circular
        dependencies that could otherwise be introduced).

        :default: - No policy is inlined in the Role resource.
        '''
        result = self._values.get("inline_policies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]]:
        '''A list of managed policies associated with this role.

        You can add managed policies later using
        ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``.

        :default: - No managed policies.
        '''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]], result)

    @builtins.property
    def max_session_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum session duration that you want to set for the specified role.

        This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours.

        Anyone who assumes the role from the AWS CLI or API can use the
        DurationSeconds API parameter or the duration-seconds CLI parameter to
        request a longer session. The MaxSessionDuration setting determines the
        maximum duration that can be requested using the DurationSeconds
        parameter.

        If users don't specify a value for the DurationSeconds parameter, their
        security credentials are valid for one hour by default. This applies when
        you use the AssumeRole* API operations or the assume-role* CLI operations
        but does not apply when you use those operations to create a console URL.

        :default: Duration.hours(1)

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html
        '''
        result = self._values.get("max_session_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path associated with this role.

        For information about IAM paths, see
        Friendly Names and Paths in IAM User Guide.

        :default: /
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]:
        '''AWS supports permissions boundaries for IAM entities (users or roles).

        A permissions boundary is an advanced feature for using a managed policy
        to set the maximum permissions that an identity-based policy can grant to
        an IAM entity. An entity's permissions boundary allows it to perform only
        the actions that are allowed by both its identity-based policies and its
        permissions boundaries.

        :default: - No permissions boundary.

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''A name for the IAM role.

        For valid values, see the RoleName parameter for
        the CreateRole action in the IAM API Reference.

        IMPORTANT: If you specify a name, you cannot perform updates that require
        replacement of this resource. You can perform updates that require no or
        some interruption. If you must replace the resource, specify a new name.

        If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to
        acknowledge your template's capabilities. For more information, see
        Acknowledging IAM Resources in AWS CloudFormation Templates.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the role name.
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CircleCiOidcRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CircleCiConfiguration",
    "CircleCiOidcProvider",
    "CircleCiOidcProviderProps",
    "CircleCiOidcRole",
    "CircleCiOidcRoleProps",
    "ICircleCiOidcProvider",
    "RoleProps",
]

publication.publish()

def _typecheckingstub__eab586ff05607d35fc5f8efd5281b65977e0f3fb2d81f3f891844470cefb35ea(
    *,
    provider: ICircleCiOidcProvider,
    project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1393e64f485bb45467827f50708b32ad642b6fb53664b1862c1828b4be061413(
    *,
    organization_id: builtins.str,
    thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a1d9304663f45d61bd197cf48bd3145a25be4318f85ebeec9bb3b566e0f0ba9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    provider: ICircleCiOidcProvider,
    project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    path: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30f6776c1ccf1de8fc7c032c787078de37f3f66d205ead67cae11deb84fbb41a(
    *,
    description: typing.Optional[builtins.str] = None,
    external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    path: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1633f8e2586bf0d50337d86af80f18850686241366bdb00da0c6d2e30c2f1b28(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    organization_id: builtins.str,
    thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fee2eb6189dca866c9ff6a10072625f160fb3e3e4386a0cc23c419d3f4ea1113(
    scope: _constructs_77d1e7e8.Construct,
    organization_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28caf46e7e0d75fcdc4c1a3dec9aa2e5dff8efcf72c3adb43eab258081ffcf9(
    *,
    provider: ICircleCiOidcProvider,
    project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    path: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

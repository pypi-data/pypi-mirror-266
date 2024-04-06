'''
# CircleCI OIDC

This repository contains constructs to communicate between CircleCI and AWS via an Open ID Connect (OIDC) provider.
The process is described in [this CircleCI blog post](https://circleci.com/blog/openid-connect-identity-tokens/).

## Security Benefits

By using the OpenID Connect provider, you can communicate with AWS from CircleCI without saving static credentials
(e.g., `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) in your CircleCI project settings or a context. Removing
static credentials, especially in light of the early 2023 [breach](https://circleci.com/blog/jan-4-2023-incident-report/),
is a best practice for security.

## Quick Start

Install the package:

```bash
npm install @blimmer/cdk-circleci-oidc

or

yarn add @blimmer/cdk-circleci-oidc
```

Then, create the provider and role(s).

```python
import { Stack, StackProps } from 'aws-cdk-lib';
import { CircleCiOidcProvider, CircleCiOidcRole } from '@blimmer/cdk-circleci-oidc';
import { Construct } from 'constructs';
import { ManagedPolicy, PolicyStatement } from 'aws-cdk-lib/aws-iam';
import { Bucket } from 'aws-cdk-lib/aws-s3';

export class CircleCiStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const provider = new CircleCiOidcProvider(this, 'OidcProvider', {
      // Find your organization ID in the CircleCI dashboard under "Organization Settings"
      organizationId: '11111111-2222-3333-4444-555555555555',
    });

    const myCircleCiRole = new CircleCiOidcRole(this, 'MyCircleCiRole', {
      circleCiOidcProvider: provider,
      roleName: "MyCircleCiRole",

      // Pass some managed policies to the role
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'),
      ],
    })

    // You can also access the role from the construct. This allows adding roles and using `grant` methods after the
    // construct has been created.
    myCircleCiRole.role.addToPolicy(new PolicyStatement({
      actions: ['s3:ListAllMyBuckets'],
      resources: ['*'],
    }));

    const bucket = new Bucket(this, 'MyBucket');
    bucket.grantRead(myCircleCiRole.role);
  }
}
```

Now, in your `.circleci/config.yml` file, you can use the [AWS CLI Orb](https://circleci.com/developer/orbs/orb/circleci/aws-cli)
to assume your new role.

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
          role_arn: 'arn:aws:iam::123456789101:role/MyCircleCiRole'
      - run:
          name: List S3 Buckets
          command: aws s3 ls
```

## Cross Stack Usage

If you want to use the OIDC provider in another stack, you can use the `getProviderForExport` method.

```python
import { Stack, StackProps } from 'aws-cdk-lib';
import { CircleCiOidcProvider } from '@blimmer/cdk-circleci-oidc';
import { Construct } from 'constructs';

export class CircleCiStack extends Stack {
  readonly circleCiOidcProvider: ManualCircleCiOidcProviderProps; // export for use in other stacks

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const provider = new CircleCiOidcProvider(this, 'OidcProvider', {
      // Find your organization ID in the CircleCI dashboard under "Organization Settings"
      organizationId: '11111111-2222-3333-4444-555555555555',
    });

    this.circleCiOidcProvider = provider.getProviderForExport(this.account);
  }
}
```

```python
import { Stack, StackProps } from 'aws-cdk-lib';
import { CircleCiOidcRole } from '@blimmer/cdk-circleci-oidc';
import { Construct } from 'constructs';
import type { CircleCiStack } from './CircleCiStack';

interface ConsumingStackProps {
  circleci: CircleCi;
}

export class ConsumingStack extends Stack {
  constructor(scope: Construct, id: string, props: ConsumingStackProps) {
    super(scope, id, props);
    const { circleCiOidcProvider } = props.circleci;

    const myCircleCiRole = new CircleCiOidcRole(this, 'MyCircleCiRole', {
      circleCiOidcProvider,
      roleName: "MyCircleCiRole",
    })
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

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


class CircleCiOidcProvider(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcProvider",
):
    '''This construct creates a CircleCI ODIC provider to allow AWS access from CircleCI jobs.

    You'll need to instantiate
    this construct once per AWS account you want to use CircleCI OIDC with.

    To create a role that can be assumed by CircleCI jobs, use the ``CircleCiOidcRole`` construct.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        organization_id: builtins.str,
        circle_ci_oidc_thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param organization_id: The ID of your CircleCI organization. This is typically in a UUID format. You can find this ID in the CircleCI dashboard UI under the "Organization Settings" tab.
        :param circle_ci_oidc_thumbprints: The OIDC thumbprints used by the provider. You should not need to provide this value unless CircleCI suddenly rotates their OIDC thumbprints (e.g., in response to a security incident). If you do need to generate this thumbprint, you can follow the instructions here: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1633f8e2586bf0d50337d86af80f18850686241366bdb00da0c6d2e30c2f1b28)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CircleCiOidcProviderProps(
            organization_id=organization_id,
            circle_ci_oidc_thumbprints=circle_ci_oidc_thumbprints,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getProviderForExport")
    def get_provider_for_export(
        self,
        account_id: builtins.str,
        import_name: typing.Optional[builtins.str] = None,
    ) -> "ManualCircleCiOidcProviderProps":
        '''
        :param account_id: -
        :param import_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93743c7aa8bdd0562b9935e6f9582d915c2988d42f8996ca90588c7a737a966c)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument import_name", value=import_name, expected_type=type_hints["import_name"])
        return typing.cast("ManualCircleCiOidcProviderProps", jsii.invoke(self, "getProviderForExport", [account_id, import_name]))

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> _aws_cdk_aws_iam_ceddda9d.CfnOIDCProvider:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.CfnOIDCProvider, jsii.get(self, "provider"))


@jsii.data_type(
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcProviderProps",
    jsii_struct_bases=[],
    name_mapping={
        "organization_id": "organizationId",
        "circle_ci_oidc_thumbprints": "circleCiOidcThumbprints",
    },
)
class CircleCiOidcProviderProps:
    def __init__(
        self,
        *,
        organization_id: builtins.str,
        circle_ci_oidc_thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param organization_id: The ID of your CircleCI organization. This is typically in a UUID format. You can find this ID in the CircleCI dashboard UI under the "Organization Settings" tab.
        :param circle_ci_oidc_thumbprints: The OIDC thumbprints used by the provider. You should not need to provide this value unless CircleCI suddenly rotates their OIDC thumbprints (e.g., in response to a security incident). If you do need to generate this thumbprint, you can follow the instructions here: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1393e64f485bb45467827f50708b32ad642b6fb53664b1862c1828b4be061413)
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument circle_ci_oidc_thumbprints", value=circle_ci_oidc_thumbprints, expected_type=type_hints["circle_ci_oidc_thumbprints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "organization_id": organization_id,
        }
        if circle_ci_oidc_thumbprints is not None:
            self._values["circle_ci_oidc_thumbprints"] = circle_ci_oidc_thumbprints

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
    def circle_ci_oidc_thumbprints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The OIDC thumbprints used by the provider.

        You should not need to provide this value unless CircleCI suddenly
        rotates their OIDC thumbprints (e.g., in response to a security incident).

        If you do need to generate this thumbprint, you can follow the instructions here:
        https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
        '''
        result = self._values.get("circle_ci_oidc_thumbprints")
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
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcRole",
):
    '''This construct creates a CircleCI ODIC provider to allow AWS access from CircleCI jobs.

    You'll need to instantiate
    this construct once per AWS account you want to use CircleCI OIDC with.

    To create a role that can be assumed by CircleCI jobs, use the ``CircleCiOidcRole`` construct.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        circle_ci_oidc_provider: typing.Union[typing.Union["ManualCircleCiOidcProviderProps", typing.Dict[builtins.str, typing.Any]], CircleCiOidcProvider],
        circle_ci_project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param circle_ci_oidc_provider: 
        :param circle_ci_project_ids: Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role. If you don't provide this value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format. Default: - All CircleCI projects in the provider's organization
        :param description: 
        :param inline_policies: 
        :param managed_policies: 
        :param role_name: You can pass an explicit role name if you'd like, since you need to reference the Role ARN within your CircleCI configuration. Default: - CloudFormation will auto-generate you a role name
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a1d9304663f45d61bd197cf48bd3145a25be4318f85ebeec9bb3b566e0f0ba9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CircleCiOidcRoleProps(
            circle_ci_oidc_provider=circle_ci_oidc_provider,
            circle_ci_project_ids=circle_ci_project_ids,
            description=description,
            inline_policies=inline_policies,
            managed_policies=managed_policies,
            role_name=role_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@blimmer/cdk-circleci-oidc.CircleCiOidcRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "circle_ci_oidc_provider": "circleCiOidcProvider",
        "circle_ci_project_ids": "circleCiProjectIds",
        "description": "description",
        "inline_policies": "inlinePolicies",
        "managed_policies": "managedPolicies",
        "role_name": "roleName",
    },
)
class CircleCiOidcRoleProps:
    def __init__(
        self,
        *,
        circle_ci_oidc_provider: typing.Union[typing.Union["ManualCircleCiOidcProviderProps", typing.Dict[builtins.str, typing.Any]], CircleCiOidcProvider],
        circle_ci_project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param circle_ci_oidc_provider: 
        :param circle_ci_project_ids: Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role. If you don't provide this value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format. Default: - All CircleCI projects in the provider's organization
        :param description: 
        :param inline_policies: 
        :param managed_policies: 
        :param role_name: You can pass an explicit role name if you'd like, since you need to reference the Role ARN within your CircleCI configuration. Default: - CloudFormation will auto-generate you a role name
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28caf46e7e0d75fcdc4c1a3dec9aa2e5dff8efcf72c3adb43eab258081ffcf9)
            check_type(argname="argument circle_ci_oidc_provider", value=circle_ci_oidc_provider, expected_type=type_hints["circle_ci_oidc_provider"])
            check_type(argname="argument circle_ci_project_ids", value=circle_ci_project_ids, expected_type=type_hints["circle_ci_project_ids"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument inline_policies", value=inline_policies, expected_type=type_hints["inline_policies"])
            check_type(argname="argument managed_policies", value=managed_policies, expected_type=type_hints["managed_policies"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "circle_ci_oidc_provider": circle_ci_oidc_provider,
        }
        if circle_ci_project_ids is not None:
            self._values["circle_ci_project_ids"] = circle_ci_project_ids
        if description is not None:
            self._values["description"] = description
        if inline_policies is not None:
            self._values["inline_policies"] = inline_policies
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def circle_ci_oidc_provider(
        self,
    ) -> typing.Union["ManualCircleCiOidcProviderProps", CircleCiOidcProvider]:
        result = self._values.get("circle_ci_oidc_provider")
        assert result is not None, "Required property 'circle_ci_oidc_provider' is missing"
        return typing.cast(typing.Union["ManualCircleCiOidcProviderProps", CircleCiOidcProvider], result)

    @builtins.property
    def circle_ci_project_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Provide the UUID(s) of the CircleCI project(s) you want to be allowed to use this role.

        If you don't provide this
        value, the role will be allowed to be assumed by any CircleCI project in your organization. You can find a
        project's ID in the CircleCI dashboard UI under the "Project Settings" tab. It's usually in a UUID format.

        :default: - All CircleCI projects in the provider's organization
        '''
        result = self._values.get("circle_ci_project_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inline_policies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]]:
        result = self._values.get("inline_policies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]]:
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''You can pass an explicit role name if you'd like, since you need to reference the Role ARN within your CircleCI configuration.

        :default: - CloudFormation will auto-generate you a role name
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


@jsii.data_type(
    jsii_type="@blimmer/cdk-circleci-oidc.ManualCircleCiOidcProviderProps",
    jsii_struct_bases=[],
    name_mapping={"organization_id": "organizationId", "provider": "provider"},
)
class ManualCircleCiOidcProviderProps:
    def __init__(
        self,
        *,
        organization_id: builtins.str,
        provider: _aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider,
    ) -> None:
        '''If you're using the {@link CircleCiOidcProvider} construct, pass it instead of these manually-defined props.

        :param organization_id: The ID of your CircleCI organization. This is typically in a UUID format. You can find this ID in the CircleCI dashboard UI under the "Organization Settings" tab.
        :param provider: The CircleCI OIDC provider. You can either manually create it or import it.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c04311493906b53cf6208c540dc321548c4b1ae90f3eb70fd4fd420775796493)
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "organization_id": organization_id,
            "provider": provider,
        }

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
    def provider(self) -> _aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider:
        '''The CircleCI OIDC provider.

        You can either manually create it or import it.
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManualCircleCiOidcProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CircleCiOidcProvider",
    "CircleCiOidcProviderProps",
    "CircleCiOidcRole",
    "CircleCiOidcRoleProps",
    "ManualCircleCiOidcProviderProps",
]

publication.publish()

def _typecheckingstub__1633f8e2586bf0d50337d86af80f18850686241366bdb00da0c6d2e30c2f1b28(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    organization_id: builtins.str,
    circle_ci_oidc_thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93743c7aa8bdd0562b9935e6f9582d915c2988d42f8996ca90588c7a737a966c(
    account_id: builtins.str,
    import_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1393e64f485bb45467827f50708b32ad642b6fb53664b1862c1828b4be061413(
    *,
    organization_id: builtins.str,
    circle_ci_oidc_thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a1d9304663f45d61bd197cf48bd3145a25be4318f85ebeec9bb3b566e0f0ba9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    circle_ci_oidc_provider: typing.Union[typing.Union[ManualCircleCiOidcProviderProps, typing.Dict[builtins.str, typing.Any]], CircleCiOidcProvider],
    circle_ci_project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28caf46e7e0d75fcdc4c1a3dec9aa2e5dff8efcf72c3adb43eab258081ffcf9(
    *,
    circle_ci_oidc_provider: typing.Union[typing.Union[ManualCircleCiOidcProviderProps, typing.Dict[builtins.str, typing.Any]], CircleCiOidcProvider],
    circle_ci_project_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c04311493906b53cf6208c540dc321548c4b1ae90f3eb70fd4fd420775796493(
    *,
    organization_id: builtins.str,
    provider: _aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider,
) -> None:
    """Type checking stubs"""
    pass

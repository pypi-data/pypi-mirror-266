'''
# Custom Resources Library for Amazon OpenSearch Service

An AWS CDK construct library to manage OpenSearch resources via CloudFormation custom resource. This is especially useful if you use fine-grained access control feature on OpenSearch, where you have to create resources such as role or role mapping via OpenSearch REST API.

![architecture](./imgs/architecture.png)

## Currently supported resources

* [Role](https://opensearch.org/docs/latest/security/access-control/api/#create-role)
* [RoleMapping](https://opensearch.org/docs/latest/security/access-control/api/#create-role-mapping)
* [User](https://opensearch.org/docs/latest/security/access-control/api/#create-role-mapping)

You can manage any other REST resources via our low level API (`ResourceBase` class).

## Usage

Instal it via npm:

```sh
npm install opensearch-rest-resources
```

Then you can create OpenSearch resources using [`Domain`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_opensearchservice.Domain.html) construct.

```python
import { IVpc } from 'aws-cdk-lib/aws-ec2';
import { IRole } from 'aws-cdk-lib/aws-iam';
import { Domain } from 'aws-cdk-lib/aws-opensearchservice';
import { OpenSearchRole, OpenSearchRoleMapping } from 'opensearch-rest-resources';

declare const vpc: IVpc;
declare const backendRole: IRole;
declare const domain: Domain;

const role = new OpenSearchRole(this, 'Role1', {
    vpc,
    domain,
    roleName: 'Role1',
    payload: {
        clusterPermissions: ['indices:data/write/bulk'],
        indexPermissions: [
            {
                indexPatterns: ['*'],
                allowedActions: ['read', 'write', 'index', 'create_index'],
            },
        ],
    }
});

const roleMapping = new OpenSearchRoleMapping(this, 'RoleMapping1', {
    vpc,
    domain,
    roleName: 'Role1',
    payload: {
        backendRoles: [backendRole.roleArn],
    },
    removalPolicy: RemovalPolicy.RETAIN,
});
roleMapping.node.addDependency(role);
```

## Limitation

Currently this library assumes your OpenSearch domain is configured such that:

* [Fine-grained access control](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html) is enabled
* Use the [`Domain`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_opensearchservice.Domain.html) L2 construct
* The master is authenticated with username and password, and the credential is stored in Secret Manager
* [Domain access policy](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html#fgac-recommendations) is configured to allow access from the master user

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:ESHttp*",
      "Resource": "domain-arn/*"
    }
  ]
}
```

Most of the above follow the current [operational best practices](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html) of Amazon OpenSearch Service. If you want other configuration supported, please submit [an issue](https://github.com/tmokmss/opensearch-rest-resources/issues).
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
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="opensearch-rest-resources.IndexPermissions",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_actions": "allowedActions",
        "dls": "dls",
        "fls": "fls",
        "index_patterns": "indexPatterns",
        "masked_fields": "maskedFields",
    },
)
class IndexPermissions:
    def __init__(
        self,
        *,
        allowed_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        dls: typing.Optional[builtins.str] = None,
        fls: typing.Optional[typing.Sequence[builtins.str]] = None,
        index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        masked_fields: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allowed_actions: https://opensearch.org/docs/latest/security/access-control/default-action-groups/.
        :param dls: 
        :param fls: 
        :param index_patterns: 
        :param masked_fields: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3034364b6d6379b6c3b2510c168b8972c1dcf9b07eb40fc7bbdc58010608ac00)
            check_type(argname="argument allowed_actions", value=allowed_actions, expected_type=type_hints["allowed_actions"])
            check_type(argname="argument dls", value=dls, expected_type=type_hints["dls"])
            check_type(argname="argument fls", value=fls, expected_type=type_hints["fls"])
            check_type(argname="argument index_patterns", value=index_patterns, expected_type=type_hints["index_patterns"])
            check_type(argname="argument masked_fields", value=masked_fields, expected_type=type_hints["masked_fields"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_actions is not None:
            self._values["allowed_actions"] = allowed_actions
        if dls is not None:
            self._values["dls"] = dls
        if fls is not None:
            self._values["fls"] = fls
        if index_patterns is not None:
            self._values["index_patterns"] = index_patterns
        if masked_fields is not None:
            self._values["masked_fields"] = masked_fields

    @builtins.property
    def allowed_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''https://opensearch.org/docs/latest/security/access-control/default-action-groups/.'''
        result = self._values.get("allowed_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dls(self) -> typing.Optional[builtins.str]:
        result = self._values.get("dls")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fls(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("fls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def index_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("index_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def masked_fields(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("masked_fields")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IndexPermissions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenSearchCustomResource(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="opensearch-rest-resources.OpenSearchCustomResource",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        payload_json: builtins.str,
        rest_endpoint: builtins.str,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain: The OpenSearch domain you want to create a resource in.
        :param payload_json: A payload in JSON string to send with a request on create/update event.
        :param rest_endpoint: A REST endpoint to call from the custom resource handler. It sends PUT request on a create/update event and DELETE request on a delete event.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88b7de23b7128611fcf29d3404857d67dca8a603b41add8856c8e8e50273d72f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchCustomResourceProps(
            domain=domain,
            payload_json=payload_json,
            rest_endpoint=rest_endpoint,
            removal_policy=removal_policy,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="opensearch-rest-resources.OpenSearchCustomResourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "payload_json": "payloadJson",
        "rest_endpoint": "restEndpoint",
        "removal_policy": "removalPolicy",
        "vpc": "vpc",
    },
)
class OpenSearchCustomResourceProps:
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        payload_json: builtins.str,
        rest_endpoint: builtins.str,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param domain: The OpenSearch domain you want to create a resource in.
        :param payload_json: A payload in JSON string to send with a request on create/update event.
        :param rest_endpoint: A REST endpoint to call from the custom resource handler. It sends PUT request on a create/update event and DELETE request on a delete event.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdfb6ebf47fc374b01c571ea7c22a6ef12e6a8ba43b993c7a76b892ec0afda3a)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument payload_json", value=payload_json, expected_type=type_hints["payload_json"])
            check_type(argname="argument rest_endpoint", value=rest_endpoint, expected_type=type_hints["rest_endpoint"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "payload_json": payload_json,
            "rest_endpoint": rest_endpoint,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.Domain:
        '''The OpenSearch domain you want to create a resource in.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.Domain, result)

    @builtins.property
    def payload_json(self) -> builtins.str:
        '''A payload in JSON string to send with a request on create/update event.'''
        result = self._values.get("payload_json")
        assert result is not None, "Required property 'payload_json' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rest_endpoint(self) -> builtins.str:
        '''A REST endpoint to call from the custom resource handler.

        It sends PUT request on a create/update event and DELETE request on a delete event.

        Example::

            _plugins/_security/api/roles/roleName
        '''
        result = self._values.get("rest_endpoint")
        assert result is not None, "Required property 'rest_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the resource is removed from the stack.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC your OpenSearch domain is in.

        :default: Assumes your Domain is not deployed within a VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchCustomResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenSearchRole(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="opensearch-rest-resources.OpenSearchRole",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        payload: typing.Union["RolePayload", typing.Dict[builtins.str, typing.Any]],
        role_name: builtins.str,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param payload: See https://opensearch.org/docs/latest/security/access-control/api/#create-role for the details.
        :param role_name: The name of this role.
        :param domain: The OpenSearch domain you want to create a resource in.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11b3dbdadf9ad4e9eb287cd1fb49920a34f29982e1c81061e7655c436c58310e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchRoleProps(
            payload=payload,
            role_name=role_name,
            domain=domain,
            removal_policy=removal_policy,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class OpenSearchRoleMapping(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="opensearch-rest-resources.OpenSearchRoleMapping",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        payload: typing.Union["RoleMappingPayload", typing.Dict[builtins.str, typing.Any]],
        role_name: builtins.str,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param payload: See https://opensearch.org/docs/latest/security/access-control/api/#create-role-mapping for the details.
        :param role_name: The role you create a role mapping for. Create a role by {@link OpenSearchRole} class, or use `a predefined role <https://opensearch.org/docs/latest/security/access-control/users-roles/#predefined-roles>`_.
        :param domain: The OpenSearch domain you want to create a resource in.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a648bd6553d5af4908ea24e1f83ff607db47eb845ef54b6dc7d9a6e22a0d8c36)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchRoleMappingProps(
            payload=payload,
            role_name=role_name,
            domain=domain,
            removal_policy=removal_policy,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class OpenSearchUser(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="opensearch-rest-resources.OpenSearchUser",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        payload: typing.Union["UserPayload", typing.Dict[builtins.str, typing.Any]],
        user_name: builtins.str,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param payload: See https://opensearch.org/docs/latest/security/access-control/api/#create-user for the details.
        :param user_name: The name of this user.
        :param domain: The OpenSearch domain you want to create a resource in.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__020b51bbd8211c5405011c19762bef3c8303e05f610a6b7e6f2b64bcf9151850)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchUserProps(
            payload=payload,
            user_name=user_name,
            domain=domain,
            removal_policy=removal_policy,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="opensearch-rest-resources.ResourcePropsBase",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain", "removal_policy": "removalPolicy", "vpc": "vpc"},
)
class ResourcePropsBase:
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param domain: The OpenSearch domain you want to create a resource in.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__925237d929be76edf0f5d1670f8f84caac9877c0ca124747b7db826a1ad69fbc)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.Domain:
        '''The OpenSearch domain you want to create a resource in.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.Domain, result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the resource is removed from the stack.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC your OpenSearch domain is in.

        :default: Assumes your Domain is not deployed within a VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourcePropsBase(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opensearch-rest-resources.RoleMappingPayload",
    jsii_struct_bases=[],
    name_mapping={"backend_roles": "backendRoles", "hosts": "hosts", "users": "users"},
)
class RoleMappingPayload:
    def __init__(
        self,
        *,
        backend_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        users: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param backend_roles: 
        :param hosts: 
        :param users: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f1cf8f23f1d4b6ee0af1c6ca2f78d22a4dd0c97fca39b46d40e032a11fd6eee)
            check_type(argname="argument backend_roles", value=backend_roles, expected_type=type_hints["backend_roles"])
            check_type(argname="argument hosts", value=hosts, expected_type=type_hints["hosts"])
            check_type(argname="argument users", value=users, expected_type=type_hints["users"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if backend_roles is not None:
            self._values["backend_roles"] = backend_roles
        if hosts is not None:
            self._values["hosts"] = hosts
        if users is not None:
            self._values["users"] = users

    @builtins.property
    def backend_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("backend_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def hosts(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("hosts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def users(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("users")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleMappingPayload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opensearch-rest-resources.RolePayload",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_permissions": "clusterPermissions",
        "index_permissions": "indexPermissions",
        "tenant_permissions": "tenantPermissions",
    },
)
class RolePayload:
    def __init__(
        self,
        *,
        cluster_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        index_permissions: typing.Optional[typing.Sequence[typing.Union[IndexPermissions, typing.Dict[builtins.str, typing.Any]]]] = None,
        tenant_permissions: typing.Optional[typing.Sequence[typing.Union["TenantPermissions", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param cluster_permissions: 
        :param index_permissions: 
        :param tenant_permissions: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abe17fdca3ba675f147ce8e13bf7f4a91a4618b9b7118ffcefe4f165609a5d61)
            check_type(argname="argument cluster_permissions", value=cluster_permissions, expected_type=type_hints["cluster_permissions"])
            check_type(argname="argument index_permissions", value=index_permissions, expected_type=type_hints["index_permissions"])
            check_type(argname="argument tenant_permissions", value=tenant_permissions, expected_type=type_hints["tenant_permissions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cluster_permissions is not None:
            self._values["cluster_permissions"] = cluster_permissions
        if index_permissions is not None:
            self._values["index_permissions"] = index_permissions
        if tenant_permissions is not None:
            self._values["tenant_permissions"] = tenant_permissions

    @builtins.property
    def cluster_permissions(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("cluster_permissions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def index_permissions(self) -> typing.Optional[typing.List[IndexPermissions]]:
        result = self._values.get("index_permissions")
        return typing.cast(typing.Optional[typing.List[IndexPermissions]], result)

    @builtins.property
    def tenant_permissions(self) -> typing.Optional[typing.List["TenantPermissions"]]:
        result = self._values.get("tenant_permissions")
        return typing.cast(typing.Optional[typing.List["TenantPermissions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RolePayload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opensearch-rest-resources.TenantPermissions",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_actions": "allowedActions",
        "tenant_patterns": "tenantPatterns",
    },
)
class TenantPermissions:
    def __init__(
        self,
        *,
        allowed_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tenant_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allowed_actions: 
        :param tenant_patterns: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6911f04ee8768447dce085b0d4537e5b75bad831650de29bb55c811a29e1784)
            check_type(argname="argument allowed_actions", value=allowed_actions, expected_type=type_hints["allowed_actions"])
            check_type(argname="argument tenant_patterns", value=tenant_patterns, expected_type=type_hints["tenant_patterns"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_actions is not None:
            self._values["allowed_actions"] = allowed_actions
        if tenant_patterns is not None:
            self._values["tenant_patterns"] = tenant_patterns

    @builtins.property
    def allowed_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("allowed_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tenant_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("tenant_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TenantPermissions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opensearch-rest-resources.UserPayload",
    jsii_struct_bases=[],
    name_mapping={
        "attributes": "attributes",
        "backend_roles": "backendRoles",
        "hash": "hash",
        "opendistro_security_roles": "opendistroSecurityRoles",
        "password": "password",
    },
)
class UserPayload:
    def __init__(
        self,
        *,
        attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        backend_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        hash: typing.Optional[builtins.str] = None,
        opendistro_security_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param attributes: 
        :param backend_roles: 
        :param hash: 
        :param opendistro_security_roles: 
        :param password: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35005ff68161381ae27d501788706281dc7d84e1d106676b23210cf89aa52eb7)
            check_type(argname="argument attributes", value=attributes, expected_type=type_hints["attributes"])
            check_type(argname="argument backend_roles", value=backend_roles, expected_type=type_hints["backend_roles"])
            check_type(argname="argument hash", value=hash, expected_type=type_hints["hash"])
            check_type(argname="argument opendistro_security_roles", value=opendistro_security_roles, expected_type=type_hints["opendistro_security_roles"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if attributes is not None:
            self._values["attributes"] = attributes
        if backend_roles is not None:
            self._values["backend_roles"] = backend_roles
        if hash is not None:
            self._values["hash"] = hash
        if opendistro_security_roles is not None:
            self._values["opendistro_security_roles"] = opendistro_security_roles
        if password is not None:
            self._values["password"] = password

    @builtins.property
    def attributes(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def backend_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("backend_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def hash(self) -> typing.Optional[builtins.str]:
        result = self._values.get("hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def opendistro_security_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("opendistro_security_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPayload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opensearch-rest-resources.OpenSearchRoleMappingProps",
    jsii_struct_bases=[ResourcePropsBase],
    name_mapping={
        "domain": "domain",
        "removal_policy": "removalPolicy",
        "vpc": "vpc",
        "payload": "payload",
        "role_name": "roleName",
    },
)
class OpenSearchRoleMappingProps(ResourcePropsBase):
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        payload: typing.Union[RoleMappingPayload, typing.Dict[builtins.str, typing.Any]],
        role_name: builtins.str,
    ) -> None:
        '''
        :param domain: The OpenSearch domain you want to create a resource in.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        :param payload: See https://opensearch.org/docs/latest/security/access-control/api/#create-role-mapping for the details.
        :param role_name: The role you create a role mapping for. Create a role by {@link OpenSearchRole} class, or use `a predefined role <https://opensearch.org/docs/latest/security/access-control/users-roles/#predefined-roles>`_.
        '''
        if isinstance(payload, dict):
            payload = RoleMappingPayload(**payload)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af952f6c3707964cd4342b6a769c893ee65a7acf2a698f5c20d050a2a4e678b)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "payload": payload,
            "role_name": role_name,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.Domain:
        '''The OpenSearch domain you want to create a resource in.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.Domain, result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the resource is removed from the stack.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC your OpenSearch domain is in.

        :default: Assumes your Domain is not deployed within a VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def payload(self) -> RoleMappingPayload:
        '''See https://opensearch.org/docs/latest/security/access-control/api/#create-role-mapping for the details.'''
        result = self._values.get("payload")
        assert result is not None, "Required property 'payload' is missing"
        return typing.cast(RoleMappingPayload, result)

    @builtins.property
    def role_name(self) -> builtins.str:
        '''The role you create a role mapping for.

        Create a role by {@link OpenSearchRole} class, or use `a predefined role <https://opensearch.org/docs/latest/security/access-control/users-roles/#predefined-roles>`_.
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchRoleMappingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opensearch-rest-resources.OpenSearchRoleProps",
    jsii_struct_bases=[ResourcePropsBase],
    name_mapping={
        "domain": "domain",
        "removal_policy": "removalPolicy",
        "vpc": "vpc",
        "payload": "payload",
        "role_name": "roleName",
    },
)
class OpenSearchRoleProps(ResourcePropsBase):
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        payload: typing.Union[RolePayload, typing.Dict[builtins.str, typing.Any]],
        role_name: builtins.str,
    ) -> None:
        '''
        :param domain: The OpenSearch domain you want to create a resource in.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        :param payload: See https://opensearch.org/docs/latest/security/access-control/api/#create-role for the details.
        :param role_name: The name of this role.
        '''
        if isinstance(payload, dict):
            payload = RolePayload(**payload)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b004c82f4d985ce97c47e706a94cf07027b40eefaffe2857093b1b9a2966f74)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "payload": payload,
            "role_name": role_name,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.Domain:
        '''The OpenSearch domain you want to create a resource in.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.Domain, result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the resource is removed from the stack.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC your OpenSearch domain is in.

        :default: Assumes your Domain is not deployed within a VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def payload(self) -> RolePayload:
        '''See https://opensearch.org/docs/latest/security/access-control/api/#create-role for the details.'''
        result = self._values.get("payload")
        assert result is not None, "Required property 'payload' is missing"
        return typing.cast(RolePayload, result)

    @builtins.property
    def role_name(self) -> builtins.str:
        '''The name of this role.'''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opensearch-rest-resources.OpenSearchUserProps",
    jsii_struct_bases=[ResourcePropsBase],
    name_mapping={
        "domain": "domain",
        "removal_policy": "removalPolicy",
        "vpc": "vpc",
        "payload": "payload",
        "user_name": "userName",
    },
)
class OpenSearchUserProps(ResourcePropsBase):
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        payload: typing.Union[UserPayload, typing.Dict[builtins.str, typing.Any]],
        user_name: builtins.str,
    ) -> None:
        '''
        :param domain: The OpenSearch domain you want to create a resource in.
        :param removal_policy: Policy to apply when the resource is removed from the stack. Default: RemovalPolicy.DESTROY
        :param vpc: The VPC your OpenSearch domain is in. Default: Assumes your Domain is not deployed within a VPC
        :param payload: See https://opensearch.org/docs/latest/security/access-control/api/#create-user for the details.
        :param user_name: The name of this user.
        '''
        if isinstance(payload, dict):
            payload = UserPayload(**payload)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e62d78568436419f29a2ab3ef0f6237e2b48cfd8f32a81c9cc98f1ebd718146)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "payload": payload,
            "user_name": user_name,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.Domain:
        '''The OpenSearch domain you want to create a resource in.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.Domain, result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the resource is removed from the stack.

        :default: RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC your OpenSearch domain is in.

        :default: Assumes your Domain is not deployed within a VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def payload(self) -> UserPayload:
        '''See https://opensearch.org/docs/latest/security/access-control/api/#create-user for the details.'''
        result = self._values.get("payload")
        assert result is not None, "Required property 'payload' is missing"
        return typing.cast(UserPayload, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''The name of this user.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IndexPermissions",
    "OpenSearchCustomResource",
    "OpenSearchCustomResourceProps",
    "OpenSearchRole",
    "OpenSearchRoleMapping",
    "OpenSearchRoleMappingProps",
    "OpenSearchRoleProps",
    "OpenSearchUser",
    "OpenSearchUserProps",
    "ResourcePropsBase",
    "RoleMappingPayload",
    "RolePayload",
    "TenantPermissions",
    "UserPayload",
]

publication.publish()

def _typecheckingstub__3034364b6d6379b6c3b2510c168b8972c1dcf9b07eb40fc7bbdc58010608ac00(
    *,
    allowed_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    dls: typing.Optional[builtins.str] = None,
    fls: typing.Optional[typing.Sequence[builtins.str]] = None,
    index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    masked_fields: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88b7de23b7128611fcf29d3404857d67dca8a603b41add8856c8e8e50273d72f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    payload_json: builtins.str,
    rest_endpoint: builtins.str,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdfb6ebf47fc374b01c571ea7c22a6ef12e6a8ba43b993c7a76b892ec0afda3a(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    payload_json: builtins.str,
    rest_endpoint: builtins.str,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11b3dbdadf9ad4e9eb287cd1fb49920a34f29982e1c81061e7655c436c58310e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    payload: typing.Union[RolePayload, typing.Dict[builtins.str, typing.Any]],
    role_name: builtins.str,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a648bd6553d5af4908ea24e1f83ff607db47eb845ef54b6dc7d9a6e22a0d8c36(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    payload: typing.Union[RoleMappingPayload, typing.Dict[builtins.str, typing.Any]],
    role_name: builtins.str,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020b51bbd8211c5405011c19762bef3c8303e05f610a6b7e6f2b64bcf9151850(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    payload: typing.Union[UserPayload, typing.Dict[builtins.str, typing.Any]],
    user_name: builtins.str,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__925237d929be76edf0f5d1670f8f84caac9877c0ca124747b7db826a1ad69fbc(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f1cf8f23f1d4b6ee0af1c6ca2f78d22a4dd0c97fca39b46d40e032a11fd6eee(
    *,
    backend_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
    users: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abe17fdca3ba675f147ce8e13bf7f4a91a4618b9b7118ffcefe4f165609a5d61(
    *,
    cluster_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
    index_permissions: typing.Optional[typing.Sequence[typing.Union[IndexPermissions, typing.Dict[builtins.str, typing.Any]]]] = None,
    tenant_permissions: typing.Optional[typing.Sequence[typing.Union[TenantPermissions, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6911f04ee8768447dce085b0d4537e5b75bad831650de29bb55c811a29e1784(
    *,
    allowed_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    tenant_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35005ff68161381ae27d501788706281dc7d84e1d106676b23210cf89aa52eb7(
    *,
    attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    backend_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    hash: typing.Optional[builtins.str] = None,
    opendistro_security_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    password: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af952f6c3707964cd4342b6a769c893ee65a7acf2a698f5c20d050a2a4e678b(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    payload: typing.Union[RoleMappingPayload, typing.Dict[builtins.str, typing.Any]],
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b004c82f4d985ce97c47e706a94cf07027b40eefaffe2857093b1b9a2966f74(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    payload: typing.Union[RolePayload, typing.Dict[builtins.str, typing.Any]],
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e62d78568436419f29a2ab3ef0f6237e2b48cfd8f32a81c9cc98f1ebd718146(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.Domain,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    payload: typing.Union[UserPayload, typing.Dict[builtins.str, typing.Any]],
    user_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

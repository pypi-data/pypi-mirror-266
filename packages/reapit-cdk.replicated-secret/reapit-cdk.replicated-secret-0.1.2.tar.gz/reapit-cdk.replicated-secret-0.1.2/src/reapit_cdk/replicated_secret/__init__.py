'''
# @reapit-cdk/replicated-secret

![npm version](https://img.shields.io/npm/v/@reapit-cdk/replicated-secret)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/replicated-secret)
![coverage: 97.06%25](https://img.shields.io/badge/coverage-97.06%25-green)
![Integ Tests: ✔](https://img.shields.io/badge/Integ%20Tests-%E2%9C%94-green)

Creates a Secret and replicates it across the given regions. Requires a [ReplicatedKey](../replicated-key/readme.md) be passed in.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/replicated-secret
# or
npm install @reapit-cdk/replicated-secret --save-dev
```

## Usage

```python
import { Stack, App } from 'aws-cdk-lib'
import { Function, Runtime, Code } from 'aws-cdk-lib/aws-lambda'
import { ReplicatedKey } from '@reapit-cdk/replicated-key'
import { ReplicatedSecret } from '@reapit-cdk/replicated-secret'

const app = new App()
const stack = new Stack(app, 'stack-name', {
  env: {
    region: 'us-east-1', // region must be specified
  },
})
const replicatedKey = new ReplicatedKey(stack, 'key', {
  replicaRegions: ['af-south-1', 'cn-north-1'],
})
const replicatedSecret = new ReplicatedSecret(stack, 'secret', {
  replicaRegions: ['af-south-1', 'cn-north-1'],
  replicatedKey,
})
const lambda = new Function(stack, 'lambda', {
  runtime: Runtime.NODEJS_18_X,
  handler: 'lambda.handler',
  code: Code.fromInline('export const handler = () => {}'),
  environment: {
    usSecretArn: replicatedSecret.getRegionalSecret('us-east-1').secretArn,
    afSecretArn: replicatedSecret.getRegionalSecret('af-south-1').secretArn,
    cnSecretArn: replicatedSecret.getRegionalSecret('cn-north-1').secretArn,
  },
})
replicatedSecret.grantWrite(lambda)
```
'''
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
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8
import reapit_cdk.replicated_key as _reapit_cdk_replicated_key_c62599cb


@jsii.data_type(
    jsii_type="@reapit-cdk/replicated-secret.MultiRegionSecretProps",
    jsii_struct_bases=[],
    name_mapping={
        "replica_regions": "replicaRegions",
        "replicated_key": "replicatedKey",
        "secret_object_value": "secretObjectValue",
        "secret_string_value": "secretStringValue",
    },
)
class MultiRegionSecretProps:
    def __init__(
        self,
        *,
        replica_regions: typing.Sequence[builtins.str],
        replicated_key: _reapit_cdk_replicated_key_c62599cb.ReplicatedKey,
        secret_object_value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]] = None,
        secret_string_value: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param replica_regions: 
        :param replicated_key: 
        :param secret_object_value: 
        :param secret_string_value: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee5e96b97eaad70869666ad6c127ed8d91f6a913ab0ce0d9c7ca50f2a46ef04)
            check_type(argname="argument replica_regions", value=replica_regions, expected_type=type_hints["replica_regions"])
            check_type(argname="argument replicated_key", value=replicated_key, expected_type=type_hints["replicated_key"])
            check_type(argname="argument secret_object_value", value=secret_object_value, expected_type=type_hints["secret_object_value"])
            check_type(argname="argument secret_string_value", value=secret_string_value, expected_type=type_hints["secret_string_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "replica_regions": replica_regions,
            "replicated_key": replicated_key,
        }
        if secret_object_value is not None:
            self._values["secret_object_value"] = secret_object_value
        if secret_string_value is not None:
            self._values["secret_string_value"] = secret_string_value

    @builtins.property
    def replica_regions(self) -> typing.List[builtins.str]:
        result = self._values.get("replica_regions")
        assert result is not None, "Required property 'replica_regions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def replicated_key(self) -> _reapit_cdk_replicated_key_c62599cb.ReplicatedKey:
        result = self._values.get("replicated_key")
        assert result is not None, "Required property 'replicated_key' is missing"
        return typing.cast(_reapit_cdk_replicated_key_c62599cb.ReplicatedKey, result)

    @builtins.property
    def secret_object_value(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]]:
        result = self._values.get("secret_object_value")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]], result)

    @builtins.property
    def secret_string_value(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        result = self._values.get("secret_string_value")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MultiRegionSecretProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReplicatedSecret(
    _aws_cdk_aws_secretsmanager_ceddda9d.Secret,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/replicated-secret.ReplicatedSecret",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        replica_regions: typing.Sequence[builtins.str],
        replicated_key: _reapit_cdk_replicated_key_c62599cb.ReplicatedKey,
        secret_object_value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]] = None,
        secret_string_value: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param replica_regions: 
        :param replicated_key: 
        :param secret_object_value: 
        :param secret_string_value: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d086e5fa905aeb9b61cb98680b7543bf282d1453d52fb16a657e8bf2845e99e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MultiRegionSecretProps(
            replica_regions=replica_regions,
            replicated_key=replicated_key,
            secret_object_value=secret_object_value,
            secret_string_value=secret_string_value,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getRegionalSecret")
    def get_regional_secret(
        self,
        region: builtins.str,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''
        :param region: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c00f128bf1999ccab53e485c5a99c497bf3e0a7fda0d5877fd307333508e463)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.invoke(self, "getRegionalSecret", [region]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        version_stages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants reading the secret value to some role.

        :param grantee: -
        :param version_stages: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae3ff0506fa540442df0b12d4490cfa796b57afcd4cc058ceae84a3dd1474e58)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument version_stages", value=version_stages, expected_type=type_hints["version_stages"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee, version_stages]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants writing and updating the secret value to some role.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4487a11668ef96ac08440418fc891ffc120bd341110ad146ae1ac06bfb33f5ee)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantWrite", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="dependable")
    def dependable(self) -> _constructs_77d1e7e8.IDependable:
        return typing.cast(_constructs_77d1e7e8.IDependable, jsii.get(self, "dependable"))

    @dependable.setter
    def dependable(self, value: _constructs_77d1e7e8.IDependable) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60149def3fef9fa6edd3d05cd996af8ef928df95a30d903586a7452182f09a04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependable", value)

    @builtins.property
    @jsii.member(jsii_name="masterRegion")
    def master_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterRegion"))

    @master_region.setter
    def master_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95eb742fa42f39c4165f5913595dc787da35b92c0361417a4016c79bff12041f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterRegion", value)


__all__ = [
    "MultiRegionSecretProps",
    "ReplicatedSecret",
]

publication.publish()

def _typecheckingstub__7ee5e96b97eaad70869666ad6c127ed8d91f6a913ab0ce0d9c7ca50f2a46ef04(
    *,
    replica_regions: typing.Sequence[builtins.str],
    replicated_key: _reapit_cdk_replicated_key_c62599cb.ReplicatedKey,
    secret_object_value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]] = None,
    secret_string_value: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d086e5fa905aeb9b61cb98680b7543bf282d1453d52fb16a657e8bf2845e99e5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    replica_regions: typing.Sequence[builtins.str],
    replicated_key: _reapit_cdk_replicated_key_c62599cb.ReplicatedKey,
    secret_object_value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]] = None,
    secret_string_value: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c00f128bf1999ccab53e485c5a99c497bf3e0a7fda0d5877fd307333508e463(
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae3ff0506fa540442df0b12d4490cfa796b57afcd4cc058ceae84a3dd1474e58(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    version_stages: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4487a11668ef96ac08440418fc891ffc120bd341110ad146ae1ac06bfb33f5ee(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60149def3fef9fa6edd3d05cd996af8ef928df95a30d903586a7452182f09a04(
    value: _constructs_77d1e7e8.IDependable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95eb742fa42f39c4165f5913595dc787da35b92c0361417a4016c79bff12041f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

'''
# @reapit-cdk/replicated-key

![npm version](https://img.shields.io/npm/v/@reapit-cdk/replicated-key)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/replicated-key)
![coverage: 99.02%25](https://img.shields.io/badge/coverage-99.02%25-green)
![Integ Tests: ✔](https://img.shields.io/badge/Integ%20Tests-%E2%9C%94-green)

Creates a KMS key and replicates it to the desired regions. Useful when replicating secrets across regions.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/replicated-key
# or
npm install @reapit-cdk/replicated-key --save-dev
```

## Usage

```python
import { Stack, App } from 'aws-cdk-lib'
import { ReplicatedKey } from '@reapit-cdk/replicated-key'
import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda'

const app = new App()
const stack = new Stack(app, 'stack-name', {
  env: {
    region: 'us-east-1', // region must be specified
  },
})
const key = new ReplicatedKey(stack, 'key', {
  replicaRegions: ['af-south-1', 'cn-north-1'],
})

const lambda = new Function(stack, 'lambda', {
  runtime: Runtime.NODEJS_18_X,
  handler: 'lambda.handler',
  code: Code.fromInline('export const handler = () => {}'),
  environment: {
    usKeyArn: key.getRegionalKey('us-east-1').keyArn,
    afKeyArn: key.getRegionalKey('af-south-1').keyArn,
    cnKeyArn: key.getRegionalKey('cn-north-1').keyArn,
  },
})

key.grantEncryptDecrypt(lambda)
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

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import constructs as _constructs_77d1e7e8


class ReplicatedKey(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/replicated-key.ReplicatedKey",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        replica_regions: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param replica_regions: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b207719880dc1e62e3b7a3c6cf4226c86e52f321de7f86f886ba995223f0528)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ReplicatedKeyProps(replica_regions=replica_regions)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getRegionalKey")
    def get_regional_key(self, region: builtins.str) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''
        :param region: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdca62b1379f3c35431bd9e431b682b0dbc7fa7574246d1c9ed1bc3e1f4b8c4c)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.invoke(self, "getRegionalKey", [region]))

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__523ff68d772f5e0e5828b96d87eddafa91e94c728cd366f405eb10984b2e1b3c)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDecrypt", [grantee]))

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28552da25850abb6b4cd23379564565100c74800640d522215ee7f321df2d16b)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantEncrypt", [grantee]))

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c261cba811060660ae6882d60264bceb3d7ee19caae5b138dd7c53b68f9abac5)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantEncryptDecrypt", [grantee]))

    @jsii.member(jsii_name="tryGetRegionalKey")
    def try_get_regional_key(
        self,
        region: builtins.str,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''
        :param region: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02cd09ef3c8d6e01c8a9aaa10bc1c651a0265cdf409d44b7d5c44e2433c6bc26)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.invoke(self, "tryGetRegionalKey", [region]))

    @builtins.property
    @jsii.member(jsii_name="dependable")
    def dependable(self) -> _constructs_77d1e7e8.IDependable:
        return typing.cast(_constructs_77d1e7e8.IDependable, jsii.get(self, "dependable"))

    @dependable.setter
    def dependable(self, value: _constructs_77d1e7e8.IDependable) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1ecc92a802c1a7fd78d3e7e156eae8c2b871605659d7c471ff69b1f269aa1f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependable", value)


@jsii.data_type(
    jsii_type="@reapit-cdk/replicated-key.ReplicatedKeyProps",
    jsii_struct_bases=[],
    name_mapping={"replica_regions": "replicaRegions"},
)
class ReplicatedKeyProps:
    def __init__(self, *, replica_regions: typing.Sequence[builtins.str]) -> None:
        '''
        :param replica_regions: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79bf9d9968da945c0407b975edb7a22aa7946f5081ef36c56419a0a6ceb61313)
            check_type(argname="argument replica_regions", value=replica_regions, expected_type=type_hints["replica_regions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "replica_regions": replica_regions,
        }

    @builtins.property
    def replica_regions(self) -> typing.List[builtins.str]:
        result = self._values.get("replica_regions")
        assert result is not None, "Required property 'replica_regions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReplicatedKeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ReplicatedKey",
    "ReplicatedKeyProps",
]

publication.publish()

def _typecheckingstub__8b207719880dc1e62e3b7a3c6cf4226c86e52f321de7f86f886ba995223f0528(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    replica_regions: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdca62b1379f3c35431bd9e431b682b0dbc7fa7574246d1c9ed1bc3e1f4b8c4c(
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__523ff68d772f5e0e5828b96d87eddafa91e94c728cd366f405eb10984b2e1b3c(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28552da25850abb6b4cd23379564565100c74800640d522215ee7f321df2d16b(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c261cba811060660ae6882d60264bceb3d7ee19caae5b138dd7c53b68f9abac5(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02cd09ef3c8d6e01c8a9aaa10bc1c651a0265cdf409d44b7d5c44e2433c6bc26(
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1ecc92a802c1a7fd78d3e7e156eae8c2b871605659d7c471ff69b1f269aa1f0(
    value: _constructs_77d1e7e8.IDependable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79bf9d9968da945c0407b975edb7a22aa7946f5081ef36c56419a0a6ceb61313(
    *,
    replica_regions: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

'''
# @reapit-cdk/userpool-domain

![npm version](https://img.shields.io/npm/v/@reapit-cdk/userpool-domain)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/userpool-domain)
![coverage: 99.02%25](https://img.shields.io/badge/coverage-99.02%25-green)
![Integ Tests: ✔](https://img.shields.io/badge/Integ%20Tests-%E2%9C%94-green)

This construct returns the given Cognito UserPool's UserPoolDomain, or creates one. This resolves an issue with [AWS::Cognito::UserPoolDomain](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooldomain.html), since that will fail if one already exists.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/userpool-domain
# or
npm install @reapit-cdk/userpool-domain --save-dev
```

## Usage

```python
import { CfnOutput, Stack, App } from 'aws-cdk-lib'
import { UserPool } from 'aws-cdk-lib/aws-cognito'
import { UserPoolDomain } from '@reapit-cdk/userpool-domain'

const app = new App()
const stack = new Stack(app, 'stack-name')
const userPool = UserPool.fromUserPoolId(stack, 'userpool', 'USERPOOL_ID')
const userPoolDomain = new UserPoolDomain(stack, 'domain', { userPool })
new CfnOutput(stack, 'userPoolDomain', {
  value: userPoolDomain.domain,
})
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

import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8


class UserPoolDomain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/userpool-domain.UserPoolDomain",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user_pool: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__957337c902609422d45487176d6f7701eebb3fef85328a108ba1ae5789a3d84a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        __2 = UserPoolDomainProps(user_pool=user_pool)

        jsii.create(self.__class__, self, [scope, id, __2])

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a02812ef006abb7065e248c444cbb5bf91ba35dd704f01705f43a2d48c2ae0a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value)

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: _aws_cdk_custom_resources_ceddda9d.Provider) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc5d3e9504e846e0a24f237a3c25abad90b0f12463a11fcc762a2d2e27728830)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value)


@jsii.data_type(
    jsii_type="@reapit-cdk/userpool-domain.UserPoolDomainProps",
    jsii_struct_bases=[],
    name_mapping={"user_pool": "userPool"},
)
class UserPoolDomainProps:
    def __init__(self, *, user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool) -> None:
        '''
        :param user_pool: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76be66576f55527286c61680318aa9ae4631af0256ee3583e08ad74ab398b97a)
            check_type(argname="argument user_pool", value=user_pool, expected_type=type_hints["user_pool"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "user_pool": user_pool,
        }

    @builtins.property
    def user_pool(self) -> _aws_cdk_aws_cognito_ceddda9d.IUserPool:
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.IUserPool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "UserPoolDomain",
    "UserPoolDomainProps",
]

publication.publish()

def _typecheckingstub__957337c902609422d45487176d6f7701eebb3fef85328a108ba1ae5789a3d84a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a02812ef006abb7065e248c444cbb5bf91ba35dd704f01705f43a2d48c2ae0a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc5d3e9504e846e0a24f237a3c25abad90b0f12463a11fcc762a2d2e27728830(
    value: _aws_cdk_custom_resources_ceddda9d.Provider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76be66576f55527286c61680318aa9ae4631af0256ee3583e08ad74ab398b97a(
    *,
    user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
) -> None:
    """Type checking stubs"""
    pass

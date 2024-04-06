'''
# @reapit-cdk/cloudfront-invalidation

![npm version](https://img.shields.io/npm/v/@reapit-cdk/cloudfront-invalidation)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/cloudfront-invalidation)
![coverage: 99.02%25](https://img.shields.io/badge/coverage-99.02%25-green)
![Integ Tests: ✔](https://img.shields.io/badge/Integ%20Tests-%E2%9C%94-green)

CloudFront invalidations are [very error prone](https://github.com/aws/aws-cdk/issues/15891#issuecomment-966456154), making it hard to invalidate distributions reliably. This construct aims to solve this problem by using a step function which is triggered on stack update, and uses exponential backoff to retry the invalidation. Inspired by https://github.com/aws/aws-cdk/issues/15891#issuecomment-1362163142.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/cloudfront-invalidation
# or
npm install @reapit-cdk/cloudfront-invalidation --save-dev
```

## Usage

```python
import { Stack, App } from 'aws-cdk-lib'
import { Distribution } from 'aws-cdk-lib/aws-cloudfront'
import { HttpOrigin } from 'aws-cdk-lib/aws-cloudfront-origins'

import { CloudfrontInvalidation } from '@reapit-cdk/cloudfront-invalidation'

const app = new App()
const stack = new Stack(app, 'stack-name', {
  env: {
    region: 'us-east-1', // region must be specified
  },
})
const distribution = new Distribution(stack, 'distribution', {
  defaultBehavior: {
    origin: new HttpOrigin('example.org'),
  },
})
new CloudfrontInvalidation(stack, 'invalidation', {
  distribution,
  items: ['/index.html', '/config.js'], // path patterns you want invalidated
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

import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import constructs as _constructs_77d1e7e8


class CloudfrontInvalidation(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/cloudfront-invalidation.CloudfrontInvalidation",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        distribution: _aws_cdk_aws_cloudfront_ceddda9d.IDistribution,
        invalidate_on_creation: typing.Optional[builtins.bool] = None,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param distribution: 
        :param invalidate_on_creation: 
        :param items: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc17db6997777c04190ffd367ed66dfd92171cef35290d229e7e7c28dc345231)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        __2 = CloudfrontInvalidationProps(
            distribution=distribution,
            invalidate_on_creation=invalidate_on_creation,
            items=items,
        )

        jsii.create(self.__class__, self, [scope, id, __2])


@jsii.data_type(
    jsii_type="@reapit-cdk/cloudfront-invalidation.CloudfrontInvalidationProps",
    jsii_struct_bases=[],
    name_mapping={
        "distribution": "distribution",
        "invalidate_on_creation": "invalidateOnCreation",
        "items": "items",
    },
)
class CloudfrontInvalidationProps:
    def __init__(
        self,
        *,
        distribution: _aws_cdk_aws_cloudfront_ceddda9d.IDistribution,
        invalidate_on_creation: typing.Optional[builtins.bool] = None,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param distribution: 
        :param invalidate_on_creation: 
        :param items: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d51ac1c969be096f5ad9377bea6919dd08c41d356e20bbfaa33182eb9bd2ca44)
            check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
            check_type(argname="argument invalidate_on_creation", value=invalidate_on_creation, expected_type=type_hints["invalidate_on_creation"])
            check_type(argname="argument items", value=items, expected_type=type_hints["items"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "distribution": distribution,
        }
        if invalidate_on_creation is not None:
            self._values["invalidate_on_creation"] = invalidate_on_creation
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.IDistribution:
        result = self._values.get("distribution")
        assert result is not None, "Required property 'distribution' is missing"
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.IDistribution, result)

    @builtins.property
    def invalidate_on_creation(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("invalidate_on_creation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontInvalidationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudfrontInvalidation",
    "CloudfrontInvalidationProps",
]

publication.publish()

def _typecheckingstub__cc17db6997777c04190ffd367ed66dfd92171cef35290d229e7e7c28dc345231(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    distribution: _aws_cdk_aws_cloudfront_ceddda9d.IDistribution,
    invalidate_on_creation: typing.Optional[builtins.bool] = None,
    items: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d51ac1c969be096f5ad9377bea6919dd08c41d356e20bbfaa33182eb9bd2ca44(
    *,
    distribution: _aws_cdk_aws_cloudfront_ceddda9d.IDistribution,
    invalidate_on_creation: typing.Optional[builtins.bool] = None,
    items: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

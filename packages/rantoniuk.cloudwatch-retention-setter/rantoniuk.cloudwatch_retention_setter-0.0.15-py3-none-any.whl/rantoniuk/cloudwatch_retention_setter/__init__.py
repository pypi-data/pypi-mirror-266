'''
# Cloudwatch Retention Setter

![release](https://github.com/rantoniuk/cloudwatch-retention-setter/actions/workflows/release.yml/badge.svg)[![npm version](https://badge.fury.io/js/cloudwatch-retention-setter.svg)](https://badge.fury.io/js/cloudwatch-retention-setter)[![PyPI version](https://badge.fury.io/py/cloudwatch-retention-setter.svg)](https://badge.fury.io/py/cloudwatch-retention-setter)

Cloudwatch Retention Setter is an AWS CDK construct library that reacts on AWS CloudWatch events. AWS CloudWatch does not offer the ability to set a "default retention policy" that would be set to all newly created Log Groups (e.g. by Lambda Function runs).

This construct addresses this by monitoring AWS CloudWatch Events via EventBridge, when a new LogGroup is created a Lambda function is invoked automatically that sets the retention policy to the specified value.

![](https://raw.githubusercontent.com/rantoniuk/cloudwatch-retention-setter/main/img/arch.png)

## Getting started

### TypeScript

#### Installation

npm:

```
npm install --save cloudwatch-retention-setter
```

yarn:

```
yarn add cloudwatch-retention-setter
```

#### Usage

```python
import * as cdk from 'aws-cdk-lib';
import { CloudwatchRetentionSetter } from 'cloudwatch-retention-setter';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import { Schedule } from 'aws-cdk-lib/aws-events';

const app = new cdk.App();
const stack = new cdk.Stack(app, '<stack-name>');

// use default retention of 6 months
new CloudwatchRetentionSetter(stack, 'cloudwatch-retention-setter');

// use custom retention
new CloudwatchRetentionSetter(stack, 'cloudwatch-retention-setter', {
  retentionDays: RetentionDays.ONE_MONTH,
});
```

### Python

#### Installation

```bash
$ pip install cloudwatch-retention-setter
```

#### Usage

```python
import aws_cdk.core as cdk
from cdk_cloudwatch_retention_setter import CloudwatchRetentionSetter

app = cdk.App()
stack = cdk.Stack(app, "<stack-name>")

CloudwatchRetentionSetter(stack, "cloudwatch-retention-setter")
```
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

import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import constructs as _constructs_77d1e7e8


class CloudwatchRetentionSetter(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudwatch-retention-setter.CloudwatchRetentionSetter",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param retention_days: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe809a2e34bc15a3744e0bdf9b59a9ce0d6475002b1604f1353ba447113ffcd6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CloudwatchRetentionSetterProps(retention_days=retention_days)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudwatch-retention-setter.CloudwatchRetentionSetterProps",
    jsii_struct_bases=[],
    name_mapping={"retention_days": "retentionDays"},
)
class CloudwatchRetentionSetterProps:
    def __init__(
        self,
        *,
        retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param retention_days: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b38f5d0ed3854d5159ac86ed7864b724bf52432ddc1ea5941e761b31d9d46a6c)
            check_type(argname="argument retention_days", value=retention_days, expected_type=type_hints["retention_days"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if retention_days is not None:
            self._values["retention_days"] = retention_days

    @builtins.property
    def retention_days(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        result = self._values.get("retention_days")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudwatchRetentionSetterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudwatchRetentionSetter",
    "CloudwatchRetentionSetterProps",
]

publication.publish()

def _typecheckingstub__fe809a2e34bc15a3744e0bdf9b59a9ce0d6475002b1604f1353ba447113ffcd6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b38f5d0ed3854d5159ac86ed7864b724bf52432ddc1ea5941e761b31d9d46a6c(
    *,
    retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

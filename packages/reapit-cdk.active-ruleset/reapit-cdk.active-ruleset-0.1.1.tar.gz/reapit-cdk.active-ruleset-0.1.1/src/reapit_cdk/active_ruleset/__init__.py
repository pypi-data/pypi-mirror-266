'''
# @reapit-cdk/active-ruleset

![npm version](https://img.shields.io/npm/v/@reapit-cdk/active-ruleset)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/active-ruleset)
![coverage: 99.02%25](https://img.shields.io/badge/coverage-99.02%25-green)
![Integ Tests: ✔](https://img.shields.io/badge/Integ%20Tests-%E2%9C%94-green)

This construct returns the currently active SES receipt RuleSet, or creates one. This enables you to add rules to it.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/active-ruleset
# or
npm install @reapit-cdk/active-ruleset --save-dev
```

## Usage

```python
import { CfnOutput, Stack, App } from 'aws-cdk-lib'
import { ActiveRuleset } from '@reapit-cdk/active-ruleset'

const app = new App()
const stack = new Stack(app, 'stack-name')
const activeRuleset = new ActiveRuleset(stack, 'active-ruleset')
new CfnOutput(stack, 'activeRulesetName', {
  value: activeRuleset.receiptRuleSet.receiptRuleSetName,
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

import aws_cdk.aws_ses as _aws_cdk_aws_ses_ceddda9d
import constructs as _constructs_77d1e7e8


class ActiveRuleset(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/active-ruleset.ActiveRuleset",
):
    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd310576d1978d6e738fdcbbbca630f557f4bc3a1c97ff4c24d3e19f4deac193)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="receiptRuleSet")
    def receipt_rule_set(self) -> _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet:
        return typing.cast(_aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet, jsii.get(self, "receiptRuleSet"))

    @receipt_rule_set.setter
    def receipt_rule_set(
        self,
        value: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd6c12d39ae0828c1166fb70c9f16c606a53b9453f3a01d93429955f738111b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "receiptRuleSet", value)


__all__ = [
    "ActiveRuleset",
]

publication.publish()

def _typecheckingstub__fd310576d1978d6e738fdcbbbca630f557f4bc3a1c97ff4c24d3e19f4deac193(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd6c12d39ae0828c1166fb70c9f16c606a53b9453f3a01d93429955f738111b6(
    value: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
) -> None:
    """Type checking stubs"""
    pass

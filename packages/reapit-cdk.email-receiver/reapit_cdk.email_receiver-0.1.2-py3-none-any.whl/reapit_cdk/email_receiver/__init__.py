'''
# @reapit-cdk/email-receiver

![npm version](https://img.shields.io/npm/v/@reapit-cdk/email-receiver)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/email-receiver)
![coverage: 99.02%25](https://img.shields.io/badge/coverage-99.02%25-green)
![Integ Tests: ✔](https://img.shields.io/badge/Integ%20Tests-%E2%9C%94-green)

This construct sets up everything necessary to receive email. The emails get stored in a dynamodb table, queryable by recipient. This is designed to be used in end-to-end tests, with the [@reapit-cdk/email-receiver-client](../../libs/email-receiver-client) helper library.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/email-receiver
# or
npm install @reapit-cdk/email-receiver --save-dev
```

## Usage

```python
import { CfnOutput, Stack, App } from 'aws-cdk-lib'
import { HostedZone } from 'aws-cdk-lib/aws-route53'
import { EmailReceiver } from '@reapit-cdk/email-receiver'

const app = new App()
const stack = new Stack(app, 'stack-name', {
  env: {
    region: 'us-east-1', // region must be specified
  },
})

const hostedZone = new HostedZone(stack, 'hostedZone', {
  zoneName: 'example.org',
})

const emailReceiver = new EmailReceiver(stack, 'domain', {
  hostedZone,
  // you can optionally override the parent domain
  // (e.g. your hosted zone is example.org but you want to use dev.example.org)
  // parentDomain: '',
  // you can optionally override the subdomain
  // this defaults to 'email' so the resulting domain will be email.example.org
  // subdomain: '',
})

new CfnOutput(stack, 'emailReceiverDomainName', {
  value: emailReceiver.domainName,
})
new CfnOutput(stack, 'emailReceiverTableArn', {
  value: emailReceiver.table.tableArn,
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

import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8


class EmailReceiver(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/email-receiver.EmailReceiver",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        parent_domain: typing.Optional[builtins.str] = None,
        subdomain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: 
        :param parent_domain: 
        :param subdomain: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d26066fddd6ccd4d500526925c25c444d5886e57a524ca2d9759f07e624ba4de)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EmailReceiverProps(
            hosted_zone=hosted_zone, parent_domain=parent_domain, subdomain=subdomain
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__978baf7b72bdc6e6b575908253f86a58a2e67460b391426a0a1ee73f9c8c7069)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainName", value)

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.Table:
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.Table, jsii.get(self, "table"))

    @table.setter
    def table(self, value: _aws_cdk_aws_dynamodb_ceddda9d.Table) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6facea8f3b2f2b924f472f5e803fde6979d1d3bae5ae8f95a7efff5606d32938)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "table", value)


@jsii.data_type(
    jsii_type="@reapit-cdk/email-receiver.EmailReceiverProps",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "parent_domain": "parentDomain",
        "subdomain": "subdomain",
    },
)
class EmailReceiverProps:
    def __init__(
        self,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        parent_domain: typing.Optional[builtins.str] = None,
        subdomain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosted_zone: 
        :param parent_domain: 
        :param subdomain: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad9246b1b7f3a3b8be9164afa99baf2db1f034b664099080ceba141377990f1d)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument parent_domain", value=parent_domain, expected_type=type_hints["parent_domain"])
            check_type(argname="argument subdomain", value=subdomain, expected_type=type_hints["subdomain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone": hosted_zone,
        }
        if parent_domain is not None:
            self._values["parent_domain"] = parent_domain
        if subdomain is not None:
            self._values["subdomain"] = subdomain

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    @builtins.property
    def parent_domain(self) -> typing.Optional[builtins.str]:
        result = self._values.get("parent_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subdomain(self) -> typing.Optional[builtins.str]:
        result = self._values.get("subdomain")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmailReceiverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EmailReceiver",
    "EmailReceiverProps",
]

publication.publish()

def _typecheckingstub__d26066fddd6ccd4d500526925c25c444d5886e57a524ca2d9759f07e624ba4de(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    parent_domain: typing.Optional[builtins.str] = None,
    subdomain: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__978baf7b72bdc6e6b575908253f86a58a2e67460b391426a0a1ee73f9c8c7069(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6facea8f3b2f2b924f472f5e803fde6979d1d3bae5ae8f95a7efff5606d32938(
    value: _aws_cdk_aws_dynamodb_ceddda9d.Table,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad9246b1b7f3a3b8be9164afa99baf2db1f034b664099080ceba141377990f1d(
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    parent_domain: typing.Optional[builtins.str] = None,
    subdomain: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

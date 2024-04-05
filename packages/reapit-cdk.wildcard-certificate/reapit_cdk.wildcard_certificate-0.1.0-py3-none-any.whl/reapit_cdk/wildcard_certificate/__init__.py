'''
# @reapit-cdk/wildcard-certificate

![npm version](https://img.shields.io/npm/v/@reapit-cdk/wildcard-certificate)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/wildcard-certificate)
![coverage: 96.75%25](https://img.shields.io/badge/coverage-96.75%25-green)
![Integ Tests: ✔](https://img.shields.io/badge/Integ%20Tests-%E2%9C%94-green)

This construct returns a wildcard certificate valid for subdomains of the given domain names, creating and validating on if it doesn't exist. It supports cross-account DNS validation, you can pass in arns of roles from other accounts and it'll assume them whilst doing the Route53 updates.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/wildcard-certificate
# or
npm install @reapit-cdk/wildcard-certificate --save-dev
```

## Usage

```python
import { CfnOutput, Stack, App } from 'aws-cdk-lib'
import { WildcardCertificate } from '@reapit-cdk/wildcard-certificate'

const app = new App()
const stack = new Stack(app, 'stack-name', {
  // stack env is required if hostedZoneArn isn't specified
  env: {
    region: 'us-east-1',
    account: '000000',
  },
})

// simple example
const wildcardCertificate = new WildcardCertificate(stack, 'cert', {
  domains: [
    {
      domainName: 'example.org',
    },
    {
      domainName: 'example.com',
    },
  ],
})
new CfnOutput(stack, 'wildcardCertificateArn', {
  value: wildcardCertificate.certificate.certificateArn,
})

// cross-account example
const xAccountWildcardCertificate = new WildcardCertificate(stack, 'x-account-cert', {
  domains: [
    {
      domainName: 'example.org',
    },
    {
      domainName: 'example.com',
      hostedZoneArn: 'arn:partition:route53::account:hostedzone/Id',
      roleArn: 'arn:aws:iam::account:role/role-name-with-path',
    },
  ],
})
new CfnOutput(stack, 'xAccountWildcardCertificateArn', {
  value: xAccountWildcardCertificate.certificate.certificateArn,
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

import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@reapit-cdk/wildcard-certificate.Domain",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "account": "account",
        "hosted_zone_arn": "hostedZoneArn",
        "include_parent": "includeParent",
        "role_arn": "roleArn",
    },
)
class Domain:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        hosted_zone_arn: typing.Optional[builtins.str] = None,
        include_parent: typing.Optional[builtins.bool] = None,
        role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain_name: 
        :param account: 
        :param hosted_zone_arn: 
        :param include_parent: 
        :param role_arn: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79946d8f3ca49b8a620b62e2e3a499a0f49c14c3aaf75300362bd33b61947a0a)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument hosted_zone_arn", value=hosted_zone_arn, expected_type=type_hints["hosted_zone_arn"])
            check_type(argname="argument include_parent", value=include_parent, expected_type=type_hints["include_parent"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
        }
        if account is not None:
            self._values["account"] = account
        if hosted_zone_arn is not None:
            self._values["hosted_zone_arn"] = hosted_zone_arn
        if include_parent is not None:
            self._values["include_parent"] = include_parent
        if role_arn is not None:
            self._values["role_arn"] = role_arn

    @builtins.property
    def domain_name(self) -> builtins.str:
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosted_zone_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("hosted_zone_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_parent(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("include_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Domain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WildcardCertificate(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/wildcard-certificate.WildcardCertificate",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domains: typing.Sequence[typing.Union[Domain, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domains: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69ca235bdd3da6f114ab38ff9deee1c5bf9b70fdac18d3a378e7275e523a7b46)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WildcardCertificateProps(domains=domains)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(
        self,
        value: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cc5ede8b789593fe492ea48962ae456e1aa3a649260428315c527cdfd812ff9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value)


@jsii.data_type(
    jsii_type="@reapit-cdk/wildcard-certificate.WildcardCertificateProps",
    jsii_struct_bases=[],
    name_mapping={"domains": "domains"},
)
class WildcardCertificateProps:
    def __init__(
        self,
        *,
        domains: typing.Sequence[typing.Union[Domain, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param domains: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a83d49bf69d3a7d99e81ab3652311ec41b6ecce8ba1523fd0e292078ff86bacd)
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domains": domains,
        }

    @builtins.property
    def domains(self) -> typing.List[Domain]:
        result = self._values.get("domains")
        assert result is not None, "Required property 'domains' is missing"
        return typing.cast(typing.List[Domain], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WildcardCertificateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Domain",
    "WildcardCertificate",
    "WildcardCertificateProps",
]

publication.publish()

def _typecheckingstub__79946d8f3ca49b8a620b62e2e3a499a0f49c14c3aaf75300362bd33b61947a0a(
    *,
    domain_name: builtins.str,
    account: typing.Optional[builtins.str] = None,
    hosted_zone_arn: typing.Optional[builtins.str] = None,
    include_parent: typing.Optional[builtins.bool] = None,
    role_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69ca235bdd3da6f114ab38ff9deee1c5bf9b70fdac18d3a378e7275e523a7b46(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domains: typing.Sequence[typing.Union[Domain, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cc5ede8b789593fe492ea48962ae456e1aa3a649260428315c527cdfd812ff9(
    value: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a83d49bf69d3a7d99e81ab3652311ec41b6ecce8ba1523fd0e292078ff86bacd(
    *,
    domains: typing.Sequence[typing.Union[Domain, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

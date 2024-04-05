'''
[![GitHub](https://img.shields.io/github/license/yicr/aws-ecs-fargate-task-termination-detection-event-rule?style=flat-square)](https://github.com/yicr/aws-ecs-fargate-task-termination-detection-event-rule/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarer/aws-ecs-fargate-task-termination-detection-event-rule?style=flat-square)](https://www.npmjs.com/package/@gammarer/aws-ecs-fargate-task-termination-detection-event-rule)
[![PyPI](https://img.shields.io/pypi/v/gammarer.aws-ecs-fargate-task-termination-detection-event-rule?style=flat-square)](https://pypi.org/project/gammarer.aws-ecs-fargate-task-termination-detection-event-rule/)

<!-- [![Nuget](https://img.shields.io/nuget/v/Gammarer.CDK.AWS.SecureFrontendWebAppCloudFrontDistribution?style=flat-square)](https://www.nuget.org/packages/Gammarer.CDK.AWS.SecureFrontendWebAppCloudFrontDistribution/)  -->

[![Sonatype Nexus (Releases)](https://img.shields.io/nexus/r/com.gammarer/aws-ecs-fargate-task-termination-detection-event-rule?server=https%3A%2F%2Fs01.oss.sonatype.org%2F&style=flat-square)](https://s01.oss.sonatype.org/content/repositories/releases/com/gammarer/aws-ecs-fargate-task-termination-detection-event-rule/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/yicr/aws-ecs-fargate-task-termination-detection-event-rule/release.yml?branch=main&label=release&style=flat-square)](https://github.com/yicr/aws-ecs-fargate-task-termination-detection-event-rule/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/yicr/aws-ecs-fargate-task-termination-detection-event-rule?sort=semver&style=flat-square)](https://github.com/yicr/aws-ecs-fargate-task-termination-detection-event-rule/releases)

# AWS ECS Fargate task termination detection notification event rule

This an AWS ECS Fargate task termination detection Event Rule.

## Install

### TypeScript

```shell
npm install @gammarer/aws-ecs-fargate-task-termination-detection-event-rule
# or
yarn add @gammarer/aws-ecs-fargate-task-termination-detection-event-rule
```

### Python

```shell
pip install gammarer.aws-ecs-fargate-task-termination-detection-event-rule
```

### Java

Add the following to pom.xml:

```xml
<dependency>
  <groupId>com.gammarer</groupId>
  <artifactId>aws-ecs-fargate-task-termination-detection-event-rule</artifactId>
</dependency>
```

## Example

```python
import { EcsFargateTaskTerminationDetectionEventRule } from '@gammarer/aws-ecs-fargate-task-termination-detection-event-rule';

const clusterArn = 'arn:aws:ecs:us-east-1:123456789012:cluster/example-app-cluster';

const rule = new EcsFargateTaskTerminationDetectionEventRule(stack, 'EcsFargateTaskTerminationDetectionEventRule', {
  ruleName: 'example-event-rule',
  description: 'example event rule.',
  clusterArn,
});
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

import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import constructs as _constructs_77d1e7e8


class EcsFargateTaskTerminationDetectionEventRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarer/aws-ecs-fargate-task-termination-detection-event-rule.EcsFargateTaskTerminationDetectionEventRule",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster_arn: builtins.str,
        description: typing.Optional[builtins.str] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_arn: 
        :param description: 
        :param rule_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13af9043267117a0e0612e26875f65aa7cd63a155140b4a5166841f9b96a0205)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EcsFargateTaskTerminationDetectionEventRuleProps(
            cluster_arn=cluster_arn, description=description, rule_name=rule_name
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@gammarer/aws-ecs-fargate-task-termination-detection-event-rule.EcsFargateTaskTerminationDetectionEventRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_arn": "clusterArn",
        "description": "description",
        "rule_name": "ruleName",
    },
)
class EcsFargateTaskTerminationDetectionEventRuleProps:
    def __init__(
        self,
        *,
        cluster_arn: builtins.str,
        description: typing.Optional[builtins.str] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cluster_arn: 
        :param description: 
        :param rule_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb13c043c5d46c1697779ee91ec0a7b9a30de83720b87d3bfcbf1cfb7da8b2ac)
            check_type(argname="argument cluster_arn", value=cluster_arn, expected_type=type_hints["cluster_arn"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_arn": cluster_arn,
        }
        if description is not None:
            self._values["description"] = description
        if rule_name is not None:
            self._values["rule_name"] = rule_name

    @builtins.property
    def cluster_arn(self) -> builtins.str:
        result = self._values.get("cluster_arn")
        assert result is not None, "Required property 'cluster_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsFargateTaskTerminationDetectionEventRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EcsFargateTaskTerminationDetectionEventRule",
    "EcsFargateTaskTerminationDetectionEventRuleProps",
]

publication.publish()

def _typecheckingstub__13af9043267117a0e0612e26875f65aa7cd63a155140b4a5166841f9b96a0205(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster_arn: builtins.str,
    description: typing.Optional[builtins.str] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb13c043c5d46c1697779ee91ec0a7b9a30de83720b87d3bfcbf1cfb7da8b2ac(
    *,
    cluster_arn: builtins.str,
    description: typing.Optional[builtins.str] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

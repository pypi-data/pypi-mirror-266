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

'''
# custom-cloud9-ssm

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|[`cdk_use_cases.custom_cloud9_ssm`](https://pypi.org/project/cdk-use-cases.custom-cloud9-ssm/)|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|[`@cdk-use-cases/custom-cloud9-ssm`](https://www.npmjs.com/package/@cdk-use-cases/custom-cloud9-ssm)|

This pattern implements a Cloud9 EC2 environment, applying an initial configuration to the EC2 instance using an SSM Document. It includes helper methods to add steps and parameters to the SSM Document and to resize the EBS volume of the EC2 instance to a given size.

Here is a minimal deployable pattern definition in Typescript:

```python
new CustomCloud9Ssm(stack, 'CustomCloud9Ssm');
```

You can view [other usage examples](#other-usage-examples).

## Initializer

```python
new CustomCloud9Ssm(scope: Construct, id: string, props: CustomCloud9SsmProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`CustomCloud9SsmProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| ssmDocumentProps? | [ssm.CfnDocumentProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ssm.CfnDocumentProps.html) | Optional configuration for the SSM Document. |
| cloud9Ec2Props? | [cloud9.CfnEnvironmentEC2Props](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloud9.CfnEnvironmentEC2Props.html) | Optional configuration for the Cloud9 EC2 environment. |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| ec2Role | [iam.Role](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html) | The IAM Role that is attached to the EC2 instance launched with the Cloud9 environment to grant it permissions to execute the statements in the SSM Document. |

## Pattern Methods

```python
public addDocumentSteps(steps: string): void
```

*Description*

Adds one or more steps to the content of the SSM Document.

*Parameters*

* steps `string`: YAML formatted string containing one or more steps to be added to the `mainSteps` section of the SSM Document.

```python
public addDocumentParameters(parameters: string): void
```

*Description*

Adds one or more parameters to the content of the SSM Document.

*Parameters*

* parameters `string`: YAML formatted string containing one or more parameters to be added to the `parameters` section of the SSM Document.

```python
public resizeEBSTo(size: number): void
```

*Description*

Adds a step to the SSM Document content that resizes the EBS volume of the EC2 instance. Attaches the required policies to `ec2Role`.

*Parameters*

* size `number`: size in GiB to resize the EBS volume to.

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Cloud9 EC2 environment

* Creates a Cloud9 EC2 environment with:

  * T3.large instance type.

### SSM Document

* Creates an SSM Document with:

  * A step that installs jq.
  * A step that resizes the EBS volume of the EC2 instance to 100 GiB.

## Architecture

![Architecture Diagram](architecture.png)

## Other usage examples

*Using default configuration and adding steps*

```python
import {CustomCloud9Ssm} from '@cdk-use-cases/custom-cloud9-ssm';

// Define a step that installs boto3
const boto3Step = `
- name: InstallBoto3
  action: aws:runShellScript
  inputs:
    runCommand:
    - "#!/bin/bash"
    - sudo pip install boto3
`

// Create the custom environment
let customCloud9 = new CustomCloud9Ssm(this, 'CustomCloud9Ssm')

// Add your step to the default document configuration
customCloud9.addDocumentSteps(boto3Step)
```

*Providing props for the SSM Document and resizing the EBS volume*

```python
import {CustomCloud9Ssm, CustomCloud9SsmProps} from '@cdk-use-cases/custom-cloud9-ssm';
const yaml = require('yaml')

// Define the content of the document
const content = `
schemaVersion: '2.2'
description: Bootstrap Cloud9 EC2 instance
mainSteps:
- name: InstallBoto3
  action: aws:runShellScript
  inputs:
    runCommand:
    - "#!/bin/bash"
    - sudo pip install boto3
`

// Specify the configuration for the SSM Document
const cloud9Props: CustomCloud9SsmProps = {
    ssmDocumentProps: {
        documentType: 'Command',
        content: yaml.parse(content),
        name: 'MyDocument'
    }
}

// Create the custom environment
let customCloud9 = new CustomCloud9Ssm(this, 'CustomCloud9Ssm', cloud9Props)

// Add a step to resize the EBS volume to 50GB
customCloud9.resizeEBSTo(50)
```

---


© Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk.aws_cloud9 as _aws_cdk_aws_cloud9_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_ssm as _aws_cdk_aws_ssm_ceddda9d
import constructs as _constructs_77d1e7e8


class CustomCloud9Ssm(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-use-cases/custom-cloud9-ssm.CustomCloud9Ssm",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cloud9_ec2_props: typing.Optional[typing.Union[_aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2Props, typing.Dict[builtins.str, typing.Any]]] = None,
        ssm_document_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.CfnDocumentProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cloud9_ec2_props: (experimental) Optional configuration for the Cloud9 EC2 environment. Default: : none
        :param ssm_document_props: (experimental) Optional configuration for the SSM Document. Default: : none

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9331dc95faf0e493016ac3a0982aaa83cefaaccd48d693be757169708d3581c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CustomCloud9SsmProps(
            cloud9_ec2_props=cloud9_ec2_props, ssm_document_props=ssm_document_props
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addDocumentParameters")
    def add_document_parameters(self, parameters: builtins.str) -> None:
        '''(experimental) Adds one or more parameters to the content of the SSM Document.

        :param parameters: YAML formatted string containing one or more parameters to be added to the parameters section of the SSM Document.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcb54d511e5e5d5e6230c31ceb0565e1fdc0fd1eb25c19bc2847f64e4f4f54bb)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        return typing.cast(None, jsii.invoke(self, "addDocumentParameters", [parameters]))

    @jsii.member(jsii_name="addDocumentSteps")
    def add_document_steps(self, steps: builtins.str) -> None:
        '''(experimental) Adds one or more steps to the content of the SSM Document.

        :param steps: YAML formatted string containing one or more steps to be added to the mainSteps section of the SSM Document.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f65e24a0b3f838e5cc13a77ae47fdb74efac64f4f101d19732cdd9f146ed4c7)
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
        return typing.cast(None, jsii.invoke(self, "addDocumentSteps", [steps]))

    @jsii.member(jsii_name="deployCDKProject")
    def deploy_cdk_project(self, url: builtins.str) -> None:
        '''(experimental) Adds a step to the SSM Document content that deploys a CDK project from its compressed version.

        :param url: from where to download the file using the wget command.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a3fb410590672b4abade9ba4a825a4c40ab6b12910dff2df7e9165adfcea34e)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        return typing.cast(None, jsii.invoke(self, "deployCDKProject", [url]))

    @jsii.member(jsii_name="resizeEBSTo")
    def resize_ebs_to(self, size: jsii.Number) -> None:
        '''(experimental) Adds a step to the SSM Document content that resizes the EBS volume of the EC2 instance.

        Attaches the required policies to ec2Role.

        :param size: in GiB to resize the EBS volume to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56ddfa2b8a6c41e3fd5100c991019ee37f14df788c7b63e1ef9a4ac192f29f29)
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
        return typing.cast(None, jsii.invoke(self, "resizeEBSTo", [size]))

    @builtins.property
    @jsii.member(jsii_name="ec2Role")
    def ec2_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''(experimental) The IAM Role that is attached to the EC2 instance launched with the Cloud9 environment to grant it permissions to execute the statements in the SSM Document.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "ec2Role"))


@jsii.data_type(
    jsii_type="@cdk-use-cases/custom-cloud9-ssm.CustomCloud9SsmProps",
    jsii_struct_bases=[],
    name_mapping={
        "cloud9_ec2_props": "cloud9Ec2Props",
        "ssm_document_props": "ssmDocumentProps",
    },
)
class CustomCloud9SsmProps:
    def __init__(
        self,
        *,
        cloud9_ec2_props: typing.Optional[typing.Union[_aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2Props, typing.Dict[builtins.str, typing.Any]]] = None,
        ssm_document_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.CfnDocumentProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cloud9_ec2_props: (experimental) Optional configuration for the Cloud9 EC2 environment. Default: : none
        :param ssm_document_props: (experimental) Optional configuration for the SSM Document. Default: : none

        :stability: experimental
        '''
        if isinstance(cloud9_ec2_props, dict):
            cloud9_ec2_props = _aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2Props(**cloud9_ec2_props)
        if isinstance(ssm_document_props, dict):
            ssm_document_props = _aws_cdk_aws_ssm_ceddda9d.CfnDocumentProps(**ssm_document_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__039fbf3a0e07870378db7192288c961d9677ae0f7343c84767d57be4a8ae9634)
            check_type(argname="argument cloud9_ec2_props", value=cloud9_ec2_props, expected_type=type_hints["cloud9_ec2_props"])
            check_type(argname="argument ssm_document_props", value=ssm_document_props, expected_type=type_hints["ssm_document_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud9_ec2_props is not None:
            self._values["cloud9_ec2_props"] = cloud9_ec2_props
        if ssm_document_props is not None:
            self._values["ssm_document_props"] = ssm_document_props

    @builtins.property
    def cloud9_ec2_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2Props]:
        '''(experimental) Optional configuration for the Cloud9 EC2 environment.

        :default: : none

        :stability: experimental
        '''
        result = self._values.get("cloud9_ec2_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2Props], result)

    @builtins.property
    def ssm_document_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ssm_ceddda9d.CfnDocumentProps]:
        '''(experimental) Optional configuration for the SSM Document.

        :default: : none

        :stability: experimental
        '''
        result = self._values.get("ssm_document_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ssm_ceddda9d.CfnDocumentProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomCloud9SsmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CustomCloud9Ssm",
    "CustomCloud9SsmProps",
]

publication.publish()

def _typecheckingstub__9331dc95faf0e493016ac3a0982aaa83cefaaccd48d693be757169708d3581c3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cloud9_ec2_props: typing.Optional[typing.Union[_aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2Props, typing.Dict[builtins.str, typing.Any]]] = None,
    ssm_document_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.CfnDocumentProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb54d511e5e5d5e6230c31ceb0565e1fdc0fd1eb25c19bc2847f64e4f4f54bb(
    parameters: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f65e24a0b3f838e5cc13a77ae47fdb74efac64f4f101d19732cdd9f146ed4c7(
    steps: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a3fb410590672b4abade9ba4a825a4c40ab6b12910dff2df7e9165adfcea34e(
    url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ddfa2b8a6c41e3fd5100c991019ee37f14df788c7b63e1ef9a4ac192f29f29(
    size: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__039fbf3a0e07870378db7192288c961d9677ae0f7343c84767d57be4a8ae9634(
    *,
    cloud9_ec2_props: typing.Optional[typing.Union[_aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2Props, typing.Dict[builtins.str, typing.Any]]] = None,
    ssm_document_props: typing.Optional[typing.Union[_aws_cdk_aws_ssm_ceddda9d.CfnDocumentProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

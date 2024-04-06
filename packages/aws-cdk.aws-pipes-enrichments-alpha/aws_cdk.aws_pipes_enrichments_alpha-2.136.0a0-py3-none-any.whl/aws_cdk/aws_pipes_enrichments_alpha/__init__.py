'''
# Amazon EventBridge Pipes Enrichments Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

EventBridge Pipes Enrichments let you create enrichments for an EventBridge Pipe.

For more details see the service documentation:

[Documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/pipes-enrichment.html)

## Pipe sources

Pipe enrichments are invoked prior to sending the events to a target of a EventBridge Pipe.

### Lambda function

A Lambda function can be used to enrich events of a pipe.

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue

# enrichment_function: lambda.Function


enrichment = enrichments.LambdaEnrichment(enrichment_function)

pipe = pipes.Pipe(self, "Pipe",
    source=SomeSource(source_queue),
    enrichment=enrichment,
    target=SomeTarget(target_queue)
)
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

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_pipes_alpha as _aws_cdk_aws_pipes_alpha_c8863edb


@jsii.implements(_aws_cdk_aws_pipes_alpha_c8863edb.IEnrichment)
class LambdaEnrichment(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.LambdaEnrichment",
):
    '''(experimental) A Lambda enrichment for a pipe.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # source_queue: sqs.Queue
        # target_queue: sqs.Queue
        
        # enrichment_function: lambda.Function
        
        
        enrichment = enrichments.LambdaEnrichment(enrichment_function)
        
        pipe = pipes.Pipe(self, "Pipe",
            source=SomeSource(source_queue),
            enrichment=enrichment,
            target=SomeTarget(target_queue)
        )
    '''

    def __init__(
        self,
        lambda_: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        *,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    ) -> None:
        '''
        :param lambda_: -
        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c2328454e32118c406277a3396e86d7e20c1075eafcd353a83b1b8a42f43a27)
            check_type(argname="argument lambda_", value=lambda_, expected_type=type_hints["lambda_"])
        props = LambdaEnrichmentProps(input_transformation=input_transformation)

        jsii.create(self.__class__, self, [lambda_, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
    ) -> _aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig:
        '''(experimental) Bind this enrichment to a pipe.

        :param pipe: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59a728fcc4d8aca29008023d9b63f1c246d2a8e4ef68377f172c94a926580caf)
            check_type(argname="argument pipe", value=pipe, expected_type=type_hints["pipe"])
        return typing.cast(_aws_cdk_aws_pipes_alpha_c8863edb.EnrichmentParametersConfig, jsii.invoke(self, "bind", [pipe]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''(experimental) Grant the pipes role to invoke the enrichment.

        :param pipe_role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d57f0a30006838ea06d202d63caf797ab47ca4c8aea6da9133fcb5c7e7ce1d72)
            check_type(argname="argument pipe_role", value=pipe_role, expected_type=type_hints["pipe_role"])
        return typing.cast(None, jsii.invoke(self, "grantInvoke", [pipe_role]))

    @builtins.property
    @jsii.member(jsii_name="enrichmentArn")
    def enrichment_arn(self) -> builtins.str:
        '''(experimental) The ARN of the enrichment resource.

        Length Constraints: Minimum length of 0. Maximum length of 1600.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "enrichmentArn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-pipes-enrichments-alpha.LambdaEnrichmentProps",
    jsii_struct_bases=[],
    name_mapping={"input_transformation": "inputTransformation"},
)
class LambdaEnrichmentProps:
    def __init__(
        self,
        *,
        input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
    ) -> None:
        '''(experimental) Properties for a LambdaEnrichment.

        :param input_transformation: (experimental) The input transformation for the enrichment. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_pipes_alpha as pipes_alpha
            import aws_cdk.aws_pipes_enrichments_alpha as pipes_enrichments_alpha
            
            # input_transformation: pipes_alpha.InputTransformation
            
            lambda_enrichment_props = pipes_enrichments_alpha.LambdaEnrichmentProps(
                input_transformation=input_transformation
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45d24844f53d2bf42f2facaf64d0c1ac127817605aaf6017892ba404b8d6d437)
            check_type(argname="argument input_transformation", value=input_transformation, expected_type=type_hints["input_transformation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if input_transformation is not None:
            self._values["input_transformation"] = input_transformation

    @builtins.property
    def input_transformation(
        self,
    ) -> typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation]:
        '''(experimental) The input transformation for the enrichment.

        :default: - None

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-input-transformation.html
        :stability: experimental
        '''
        result = self._values.get("input_transformation")
        return typing.cast(typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEnrichmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaEnrichment",
    "LambdaEnrichmentProps",
]

publication.publish()

def _typecheckingstub__2c2328454e32118c406277a3396e86d7e20c1075eafcd353a83b1b8a42f43a27(
    lambda_: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    *,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59a728fcc4d8aca29008023d9b63f1c246d2a8e4ef68377f172c94a926580caf(
    pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d57f0a30006838ea06d202d63caf797ab47ca4c8aea6da9133fcb5c7e7ce1d72(
    pipe_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45d24844f53d2bf42f2facaf64d0c1ac127817605aaf6017892ba404b8d6d437(
    *,
    input_transformation: typing.Optional[_aws_cdk_aws_pipes_alpha_c8863edb.InputTransformation] = None,
) -> None:
    """Type checking stubs"""
    pass

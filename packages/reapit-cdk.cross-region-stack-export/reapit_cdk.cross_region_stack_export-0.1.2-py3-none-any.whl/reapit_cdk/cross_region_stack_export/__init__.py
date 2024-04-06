'''
# @reapit-cdk/cross-region-stack-export

![npm version](https://img.shields.io/npm/v/@reapit-cdk/cross-region-stack-export)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/cross-region-stack-export)
![coverage: 71.85%25](https://img.shields.io/badge/coverage-71.85%25-orange)
![Integ Tests: X](https://img.shields.io/badge/Integ%20Tests-X-red)

Allows you to share values between stack across regions and accounts.

## Package Installation:

```sh
yarn add --dev @reapit-cdk/cross-region-stack-export
# or
npm install @reapit-cdk/cross-region-stack-export --save-dev
```

## Usage

```python
import { CfnOutput, Stack, App } from 'aws-cdk-lib'
import { CrossRegionStackExport } from '@reapit-cdk/cross-region-stack-export'
import { Bucket } from 'aws-cdk-lib/aws-s3'

const app = new App()
const euStack = new Stack(app, 'stack-eu', {
  env: {
    account: '11111111',
    region: 'eu-west-1',
  },
})

const exporter = new CrossRegionStackExport(euStack, 'exporter')
exporter.setValue('thing', 'avalue')

const bucket = new Bucket(euStack, 'bucket')
exporter.setValue('bucketArn', bucket.bucketArn)

const usStack = new Stack(app, 'stack-us', {
  env: {
    account: '2222222222',
    region: 'us-east-1',
  },
})

const importer = exporter.getImporter(usStack, 'eu-importer')

const euThing = importer.getValue('thing')
const euBucket = Bucket.fromBucketArn(usStack, 'eu-bucket', importer.getValue('bucketArn'))

new CfnOutput(usStack, 'euThing', {
  value: euThing,
})

new CfnOutput(usStack, 'euBucketName', {
  value: euBucket.bucketName,
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


class CrossRegionStackExport(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/cross-region-stack-export.CrossRegionStackExport",
):
    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56e37646d711d995bec182260bdadd3faa61245fe392879f982bf8ced351d82b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="getImporter")
    def get_importer(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        always_update: typing.Optional[builtins.bool] = None,
    ) -> "CrossRegionStackImport":
        '''
        :param scope: -
        :param id: -
        :param always_update: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47e62c610729b359efa5e3504f1cb6f02906809bf0ec2c91f9ce1b77fd90d9ce)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument always_update", value=always_update, expected_type=type_hints["always_update"])
        return typing.cast("CrossRegionStackImport", jsii.invoke(self, "getImporter", [scope, id, always_update]))

    @jsii.member(jsii_name="getParameterName")
    def get_parameter_name(self, stack_export: builtins.str) -> builtins.str:
        '''
        :param stack_export: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d06c4cbf772f5a4447b133dbfb4188b1707e9d56cfe83ea607eb713932c63579)
            check_type(argname="argument stack_export", value=stack_export, expected_type=type_hints["stack_export"])
        return typing.cast(builtins.str, jsii.invoke(self, "getParameterName", [stack_export]))

    @jsii.member(jsii_name="getReadOnlyRole")
    def get_read_only_role(
        self,
        account: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :param account: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb06335cdd14bc27a7d2f1cb10f630ca606224738cc23bc2e6d77fee0aea8b27)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.invoke(self, "getReadOnlyRole", [account]))

    @jsii.member(jsii_name="setValue")
    def set_value(self, id: builtins.str, value: builtins.str) -> None:
        '''
        :param id: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dce52544dd2f47af36bcc66f9273bfaf8e00cd446663fa3c71218fc3f05a5dd)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "setValue", [id, value]))

    @builtins.property
    @jsii.member(jsii_name="parameterPath")
    def parameter_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterPath"))

    @parameter_path.setter
    def parameter_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cc66d6fd99aaf58753a843b96e82270be7f70fd8d664fde14252e292a9f0d28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterPath", value)

    @builtins.property
    @jsii.member(jsii_name="sourceStack")
    def source_stack(self) -> _aws_cdk_ceddda9d.Stack:
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.get(self, "sourceStack"))

    @source_stack.setter
    def source_stack(self, value: _aws_cdk_ceddda9d.Stack) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5f3c7e8e00b8dac00a56b24f6812f23019fff964415e6c0d4ebc404f18f9866)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceStack", value)


class CrossRegionStackImport(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/cross-region-stack-export.CrossRegionStackImport",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        from_exporter: CrossRegionStackExport,
        role_arn: builtins.str,
        always_update: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param from_exporter: -
        :param role_arn: -
        :param always_update: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ec453dc46844020d7a37aad722abfac27a0baddc5cf9b7916605c142caa5d10)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument from_exporter", value=from_exporter, expected_type=type_hints["from_exporter"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument always_update", value=always_update, expected_type=type_hints["always_update"])
        jsii.create(self.__class__, self, [scope, id, from_exporter, role_arn, always_update])

    @jsii.member(jsii_name="getValue")
    def get_value(self, stack_export: builtins.str) -> builtins.str:
        '''
        :param stack_export: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__643f74d3da7a62610f51de3b3c00815cf52739099cabf4afe458c3ec482b8ba2)
            check_type(argname="argument stack_export", value=stack_export, expected_type=type_hints["stack_export"])
        return typing.cast(builtins.str, jsii.invoke(self, "getValue", [stack_export]))

    @builtins.property
    @jsii.member(jsii_name="exporter")
    def exporter(self) -> CrossRegionStackExport:
        return typing.cast(CrossRegionStackExport, jsii.get(self, "exporter"))

    @exporter.setter
    def exporter(self, value: CrossRegionStackExport) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98428e3fbe3c5f2e8ef7d954317bb9caafbe01f148d06579e871795ecbe3f1f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exporter", value)

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "RemoteParameters":
        return typing.cast("RemoteParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "RemoteParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d66f22ebf546e2015aac2e9d633b96ee2bee29442491c049cd275633c0e33d0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value)


class RemoteParameters(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/cross-region-stack-export.RemoteParameters",
):
    '''Represents the RemoteParameters of the remote CDK stack.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        path: builtins.str,
        region: builtins.str,
        always_update: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param path: The parameter path.
        :param region: The region code of the remote stack.
        :param always_update: Indicate whether always update the custom resource to get the new stack output. Default: true
        :param role: The assumed role used to get remote parameters.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9964e61e7ae65959d724814dbdeece319e79c797ce213c78581c66597a78f11d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RemoteParametersProps(
            path=path, region=region, always_update=always_update, role=role
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="get")
    def get(self, key: builtins.str) -> builtins.str:
        '''Get the parameter.

        :param key: output key.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3c458d715f06957562776eab376d192affdbb025cea5ead5dc98f4000109ba7)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast(builtins.str, jsii.invoke(self, "get", [key]))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''The parameters in the SSM parameter store for the remote stack.'''
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.get(self, "parameters"))


@jsii.data_type(
    jsii_type="@reapit-cdk/cross-region-stack-export.RemoteParametersProps",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "region": "region",
        "always_update": "alwaysUpdate",
        "role": "role",
    },
)
class RemoteParametersProps:
    def __init__(
        self,
        *,
        path: builtins.str,
        region: builtins.str,
        always_update: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''Properties of the RemoteParameters.

        :param path: The parameter path.
        :param region: The region code of the remote stack.
        :param always_update: Indicate whether always update the custom resource to get the new stack output. Default: true
        :param role: The assumed role used to get remote parameters.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae146030780e945eead6b2ebbec5237d5548199cd6398544e17ee661157d3412)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument always_update", value=always_update, expected_type=type_hints["always_update"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
            "region": region,
        }
        if always_update is not None:
            self._values["always_update"] = always_update
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def path(self) -> builtins.str:
        '''The parameter path.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''The region code of the remote stack.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def always_update(self) -> typing.Optional[builtins.bool]:
        '''Indicate whether always update the custom resource to get the new stack output.

        :default: true
        '''
        result = self._values.get("always_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The assumed role used to get remote parameters.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RemoteParametersProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CrossRegionStackExport",
    "CrossRegionStackImport",
    "RemoteParameters",
    "RemoteParametersProps",
]

publication.publish()

def _typecheckingstub__56e37646d711d995bec182260bdadd3faa61245fe392879f982bf8ced351d82b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47e62c610729b359efa5e3504f1cb6f02906809bf0ec2c91f9ce1b77fd90d9ce(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    always_update: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d06c4cbf772f5a4447b133dbfb4188b1707e9d56cfe83ea607eb713932c63579(
    stack_export: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb06335cdd14bc27a7d2f1cb10f630ca606224738cc23bc2e6d77fee0aea8b27(
    account: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dce52544dd2f47af36bcc66f9273bfaf8e00cd446663fa3c71218fc3f05a5dd(
    id: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc66d6fd99aaf58753a843b96e82270be7f70fd8d664fde14252e292a9f0d28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5f3c7e8e00b8dac00a56b24f6812f23019fff964415e6c0d4ebc404f18f9866(
    value: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec453dc46844020d7a37aad722abfac27a0baddc5cf9b7916605c142caa5d10(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    from_exporter: CrossRegionStackExport,
    role_arn: builtins.str,
    always_update: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__643f74d3da7a62610f51de3b3c00815cf52739099cabf4afe458c3ec482b8ba2(
    stack_export: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98428e3fbe3c5f2e8ef7d954317bb9caafbe01f148d06579e871795ecbe3f1f2(
    value: CrossRegionStackExport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d66f22ebf546e2015aac2e9d633b96ee2bee29442491c049cd275633c0e33d0b(
    value: RemoteParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9964e61e7ae65959d724814dbdeece319e79c797ce213c78581c66597a78f11d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    path: builtins.str,
    region: builtins.str,
    always_update: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3c458d715f06957562776eab376d192affdbb025cea5ead5dc98f4000109ba7(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae146030780e945eead6b2ebbec5237d5548199cd6398544e17ee661157d3412(
    *,
    path: builtins.str,
    region: builtins.str,
    always_update: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

'''
# AWS Secure CloudFront Origin Bucket (for CDK v2)

[![GitHub](https://img.shields.io/github/license/gammarer/aws-secure-cloudfront-origin-bucket?style=flat-square)](https://github.com/gammarer/aws-secure-cloudfront-origin-bucket/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarer/aws-secure-cloudfront-origin-bucket?style=flat-square)](https://www.npmjs.com/package/@gammarer/aws-secure-cloudfront-origin-bucket)
[![PyPI](https://img.shields.io/pypi/v/gammarer.aws-secure-cloudfront-origin-bucket?style=flat-square)](https://pypi.org/project/gammarer.aws-secure-cloudfront-origin-bucket/)
[![Nuget](https://img.shields.io/nuget/v/Gammarer.CDK.AWS.SecureCloudFrontOriginBucket?style=flat-square)](https://www.nuget.org/packages/Gammarer.CDK.AWS.ScureCloudFrontOriginBucket/)
[![Sonatype Nexus (Releases)](https://img.shields.io/nexus/r/com.gammarer/aws-secure-cloudfront-origin-bucket?server=https%3A%2F%2Fs01.oss.sonatype.org%2F&style=flat-square)](https://s01.oss.sonatype.org/content/repositories/releases/com/gammarer/aws-secure-cloudfront-origin-bucket/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarer/aws-secure-cloudfront-origin-bucket/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarer/aws-secure-cloudfront-origin-bucket/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarer/aws-secure-cloudfront-origin-bucket?sort=semver&style=flat-square)](https://github.com/gammarer/aws-secure-cloudfront-origin-bucket/releases)

[![View on Construct Hub](https://constructs.dev/badge?package=@gammarer/aws-secure-cloudfront-origin-bucket)](https://constructs.dev/packages/@gammarer/aws-secure-cloudfront-origin-bucket)

An AWS CDK construct library to create secure S3 buckets for CloudFront origin.

## Install

### TypeScript

```shell
npm install @gammarer/aws-secure-cloudfront-origin-bucket
# or
yarn add @gammarer/aws-secure-cloudfront-origin-bucket
# or
pnpm add @gammarer/aws-secure-cloudfront-origin-bucket
# or
bun add @gammarer/aws-secure-cloudfront-origin-bucket
```

### Python

```shell
pip install gammarer.aws-secure-cloudfront-origin-bucket
```

### C# / .NET

```shell
dotnet add package Gammarer.CDK.AWS.SecureCloudFrontOriginBucket
```

### Java

Add the following to pom.xml:

```xml
<dependency>
  <groupId>com.gammarer</groupId>
  <artifactId>aws-secure-cloudfront-origin-bucket</artifactId>
</dependency>
```

## Example

### for OAI(Origin Access Identity)

```python
import { SecureCloudFrontOriginBucket, SecureCloudFrontOriginType } from '@gammarer/aws-secure-cloudfront-origin-bucket';

const oai = new cloudfront.OriginAccessIdentity(stack, 'OriginAccessIdentity');

new SecureCloudFrontOriginBucket(stack, 'SecureCloudFrontOriginBucket', {
  bucketName: 'example-origin-bucket',
  cloudFrontOriginType: SecureCloudFrontOriginType.ORIGIN_ACCESS_IDENTITY,
  cloudFrontOriginAccessIdentityS3CanonicalUserId: oai.cloudFrontOriginAccessIdentityS3CanonicalUserId,
});
```

### for OAC(Origin Access Control)

```python
import { SecureCloudFrontOriginBucket, SecureCloudFrontOriginType } from '@gammarer/aws-secure-cloudfront-origin-bucket';

declare const s3Bucket: cloudfront.Distribution;

new SecureCloudFrontOriginBucket(stack, 'SecureCloudFrontOriginBucket', {
  bucketName: 'example-origin-bucket',
  cloudFrontOriginType: SecureCloudFrontOriginType.ORIGIN_ACCESS_CONTROL,
  cloudFrontArn: 'arn:aws:cloudfront::123456789:distribution/DISTRIBUTIONID',
});
```

## License

This project is licensed under the Apache-2.0 License.
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

import constructs as _constructs_77d1e7e8
import gammarer.aws_secure_bucket as _gammarer_aws_secure_bucket_909c3804


@jsii.data_type(
    jsii_type="@gammarer/aws-secure-cloudfront-origin-bucket.SecureCloudFrontOriginAccessControlBucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_front_arn": "cloudFrontArn",
        "cloud_front_origin_type": "cloudFrontOriginType",
        "bucket_name": "bucketName",
    },
)
class SecureCloudFrontOriginAccessControlBucketProps:
    def __init__(
        self,
        *,
        cloud_front_arn: builtins.str,
        cloud_front_origin_type: "SecureCloudFrontOriginType",
        bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_front_arn: 
        :param cloud_front_origin_type: 
        :param bucket_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6887e02de81d8694734031f4784a3b6950148b1810ef7a8ad571f7bc59915be)
            check_type(argname="argument cloud_front_arn", value=cloud_front_arn, expected_type=type_hints["cloud_front_arn"])
            check_type(argname="argument cloud_front_origin_type", value=cloud_front_origin_type, expected_type=type_hints["cloud_front_origin_type"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cloud_front_arn": cloud_front_arn,
            "cloud_front_origin_type": cloud_front_origin_type,
        }
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name

    @builtins.property
    def cloud_front_arn(self) -> builtins.str:
        result = self._values.get("cloud_front_arn")
        assert result is not None, "Required property 'cloud_front_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloud_front_origin_type(self) -> "SecureCloudFrontOriginType":
        result = self._values.get("cloud_front_origin_type")
        assert result is not None, "Required property 'cloud_front_origin_type' is missing"
        return typing.cast("SecureCloudFrontOriginType", result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureCloudFrontOriginAccessControlBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gammarer/aws-secure-cloudfront-origin-bucket.SecureCloudFrontOriginAccessIdentityBucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_front_origin_access_identity_s3_canonical_user_id": "cloudFrontOriginAccessIdentityS3CanonicalUserId",
        "cloud_front_origin_type": "cloudFrontOriginType",
        "bucket_name": "bucketName",
    },
)
class SecureCloudFrontOriginAccessIdentityBucketProps:
    def __init__(
        self,
        *,
        cloud_front_origin_access_identity_s3_canonical_user_id: builtins.str,
        cloud_front_origin_type: "SecureCloudFrontOriginType",
        bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_front_origin_access_identity_s3_canonical_user_id: 
        :param cloud_front_origin_type: 
        :param bucket_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7988acdcb7891a51fff9ae14a3b6690a65d528fae41910fdaf2354ece737fbd)
            check_type(argname="argument cloud_front_origin_access_identity_s3_canonical_user_id", value=cloud_front_origin_access_identity_s3_canonical_user_id, expected_type=type_hints["cloud_front_origin_access_identity_s3_canonical_user_id"])
            check_type(argname="argument cloud_front_origin_type", value=cloud_front_origin_type, expected_type=type_hints["cloud_front_origin_type"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cloud_front_origin_access_identity_s3_canonical_user_id": cloud_front_origin_access_identity_s3_canonical_user_id,
            "cloud_front_origin_type": cloud_front_origin_type,
        }
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name

    @builtins.property
    def cloud_front_origin_access_identity_s3_canonical_user_id(self) -> builtins.str:
        result = self._values.get("cloud_front_origin_access_identity_s3_canonical_user_id")
        assert result is not None, "Required property 'cloud_front_origin_access_identity_s3_canonical_user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloud_front_origin_type(self) -> "SecureCloudFrontOriginType":
        result = self._values.get("cloud_front_origin_type")
        assert result is not None, "Required property 'cloud_front_origin_type' is missing"
        return typing.cast("SecureCloudFrontOriginType", result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureCloudFrontOriginAccessIdentityBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecureCloudFrontOriginBucket(
    _gammarer_aws_secure_bucket_909c3804.SecureBucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarer/aws-secure-cloudfront-origin-bucket.SecureCloudFrontOriginBucket",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Union[typing.Union[SecureCloudFrontOriginAccessControlBucketProps, typing.Dict[builtins.str, typing.Any]], typing.Union[SecureCloudFrontOriginAccessIdentityBucketProps, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c004eda6f2e178cfac2a2d0f96c77d7f739a5eb764d44067c2b96280e19cb8f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])


@jsii.enum(
    jsii_type="@gammarer/aws-secure-cloudfront-origin-bucket.SecureCloudFrontOriginType"
)
class SecureCloudFrontOriginType(enum.Enum):
    ORIGIN_ACCESS_IDENTITY = "ORIGIN_ACCESS_IDENTITY"
    '''OriginAccessIdentity.'''
    ORIGIN_ACCESS_CONTROL = "ORIGIN_ACCESS_CONTROL"
    '''OriginAccessControl.'''


__all__ = [
    "SecureCloudFrontOriginAccessControlBucketProps",
    "SecureCloudFrontOriginAccessIdentityBucketProps",
    "SecureCloudFrontOriginBucket",
    "SecureCloudFrontOriginType",
]

publication.publish()

def _typecheckingstub__b6887e02de81d8694734031f4784a3b6950148b1810ef7a8ad571f7bc59915be(
    *,
    cloud_front_arn: builtins.str,
    cloud_front_origin_type: SecureCloudFrontOriginType,
    bucket_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7988acdcb7891a51fff9ae14a3b6690a65d528fae41910fdaf2354ece737fbd(
    *,
    cloud_front_origin_access_identity_s3_canonical_user_id: builtins.str,
    cloud_front_origin_type: SecureCloudFrontOriginType,
    bucket_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c004eda6f2e178cfac2a2d0f96c77d7f739a5eb764d44067c2b96280e19cb8f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Union[typing.Union[SecureCloudFrontOriginAccessControlBucketProps, typing.Dict[builtins.str, typing.Any]], typing.Union[SecureCloudFrontOriginAccessIdentityBucketProps, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

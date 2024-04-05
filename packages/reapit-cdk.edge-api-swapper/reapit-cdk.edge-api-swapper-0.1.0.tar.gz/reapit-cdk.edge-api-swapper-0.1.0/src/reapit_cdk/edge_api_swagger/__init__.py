'''
# @reapit-cdk/edge-api-swagger

![npm version](https://img.shields.io/npm/v/@reapit-cdk/edge-api-swagger)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/edge-api-swagger)
![coverage: 0%25](https://img.shields.io/badge/coverage-0%25-red)
![Integ Tests: X](https://img.shields.io/badge/Integ%20Tests-X-red)

Add a swagger endpoint to your EdgeAPI

## Package Installation:

```sh
yarn add --dev @reapit-cdk/edge-api-swagger
# or
npm install @reapit-cdk/edge-api-swagger --save-dev
```

## Usage

```python
import { Stack, App } from 'aws-cdk-lib'
import { EdgeAPI, EdgeAPILambda, LambdaEndpoint, ProxyEndpoint } from '@reapit-cdk/edge-api'
import { Code, Runtime } from 'aws-cdk-lib/aws-lambda'
import { EdgeAPISwaggerEndpoint } from '@reapit-cdk/edge-api-swagger'
import { Certificate } from 'aws-cdk-lib/aws-certificatemanager'
import * as path from 'path'

const app = new App()
const stack = new Stack(app, 'stack-name')

const certificate = new Certificate(stack, 'certificate', {
  domainName: 'example.org',
})
const api = new EdgeAPI(stack, 'api', {
  certificate,
  domains: ['example.org', 'example.com'],
  devMode: false,
  defaultEndpoint: new ProxyEndpoint({
    destination: 'example.com',
    pathPattern: '/*',
  }),
})

const lambdaFunction = new EdgeAPILambda(stack, 'lambda', {
  code: Code.fromAsset(path.resolve('../lambda/dist')),
  codePath: path.resolve('../lambda/src/index.ts'), // gets added to the docs
  handler: 'index.handler',
  runtime: Runtime.NODEJS_18_X,
  environment: {
    aVariable: 'contents',
  },
})

api.addEndpoint(
  new LambdaEndpoint({
    pathPattern: '/api/lambda',
    lambdaFunction,
  }),
)

api.addEndpoint(
  new EdgeAPISwaggerEndpoint(stack, 'docs', {
    api,
    url: 'https://example.org',

    pathPattern: '/swagger', // optional, defaults to /swagger

    // optional
    info: {
      title: '', // defaults to Edge API
      version: '', // defaults to 1.0.0
    },
  }),
)
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

import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8
import reapit_cdk.edge_api as _reapit_cdk_edge_api_55b0061f


@jsii.implements(_reapit_cdk_edge_api_55b0061f.IFrontendEndpoint)
class EdgeAPISwaggerEndpoint(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/edge-api-swagger.EdgeAPISwaggerEndpoint",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api: _reapit_cdk_edge_api_55b0061f.EdgeAPI,
        url: builtins.str,
        path_pattern: typing.Optional[builtins.str] = None,
        repo_root: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api: 
        :param url: 
        :param path_pattern: 
        :param repo_root: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc74e0ca2a2221b8ca8aa5d06fad179f348fbae387543a55d1b2601d3651a40)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EdgeAPISwaggerEndpointProps(
            api=api, url=url, path_pattern=path_pattern, repo_root=repo_root
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: _aws_cdk_aws_s3_ceddda9d.Bucket) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca2c5d89bf780de34bcff213eae9d770bd427083ce291cf6ab5adf892950faf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value)

    @builtins.property
    @jsii.member(jsii_name="pathPattern")
    def path_pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPattern"))

    @path_pattern.setter
    def path_pattern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9b111b12a1634b66934135f81244d45ac0e4e58a1811155daebd92d9bc2101e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathPattern", value)

    @builtins.property
    @jsii.member(jsii_name="invalidationItems")
    def invalidation_items(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidationItems"))

    @invalidation_items.setter
    def invalidation_items(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9e3c44b8199e68c8d720b0d018bab53aa2d7f76ebb0728d65a97e5dc5ae5de9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invalidationItems", value)


@jsii.data_type(
    jsii_type="@reapit-cdk/edge-api-swagger.EdgeAPISwaggerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "api": "api",
        "url": "url",
        "path_pattern": "pathPattern",
        "repo_root": "repoRoot",
    },
)
class EdgeAPISwaggerEndpointProps:
    def __init__(
        self,
        *,
        api: _reapit_cdk_edge_api_55b0061f.EdgeAPI,
        url: builtins.str,
        path_pattern: typing.Optional[builtins.str] = None,
        repo_root: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param api: 
        :param url: 
        :param path_pattern: 
        :param repo_root: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11fe5cca0131e31848de0f82f2af7b96443bfa133f962de5205131d520e8f8f3)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument path_pattern", value=path_pattern, expected_type=type_hints["path_pattern"])
            check_type(argname="argument repo_root", value=repo_root, expected_type=type_hints["repo_root"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api": api,
            "url": url,
        }
        if path_pattern is not None:
            self._values["path_pattern"] = path_pattern
        if repo_root is not None:
            self._values["repo_root"] = repo_root

    @builtins.property
    def api(self) -> _reapit_cdk_edge_api_55b0061f.EdgeAPI:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(_reapit_cdk_edge_api_55b0061f.EdgeAPI, result)

    @builtins.property
    def url(self) -> builtins.str:
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path_pattern(self) -> typing.Optional[builtins.str]:
        result = self._values.get("path_pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repo_root(self) -> typing.Optional[builtins.str]:
        result = self._values.get("repo_root")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EdgeAPISwaggerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@reapit-cdk/edge-api-swagger.IFrontendEndpoint")
class IFrontendEndpoint(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        ...

    @bucket.setter
    def bucket(self, value: _aws_cdk_aws_s3_ceddda9d.Bucket) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pathPattern")
    def path_pattern(self) -> builtins.str:
        ...

    @path_pattern.setter
    def path_pattern(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="invalidationItems")
    def invalidation_items(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @invalidation_items.setter
    def invalidation_items(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="responseHeaderOverrides")
    def response_header_overrides(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps]:
        ...

    @response_header_overrides.setter
    def response_header_overrides(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps],
    ) -> None:
        ...


class _IFrontendEndpointProxy:
    __jsii_type__: typing.ClassVar[str] = "@reapit-cdk/edge-api-swagger.IFrontendEndpoint"

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: _aws_cdk_aws_s3_ceddda9d.Bucket) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__005ab6bb566912d4a622c17ae06a17c9ebb2e56efb1564995d7667aa455532c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value)

    @builtins.property
    @jsii.member(jsii_name="pathPattern")
    def path_pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPattern"))

    @path_pattern.setter
    def path_pattern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f314d7d684d50ed1bc898a73bc0d3175407bcdee6c25e7a0a5ba4dd3449a9e00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathPattern", value)

    @builtins.property
    @jsii.member(jsii_name="invalidationItems")
    def invalidation_items(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidationItems"))

    @invalidation_items.setter
    def invalidation_items(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93e1dfeab459fe760b3baf82b26cbc6ab6b939607b4a8a4748f3e8cbef9917cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invalidationItems", value)

    @builtins.property
    @jsii.member(jsii_name="responseHeaderOverrides")
    def response_header_overrides(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps], jsii.get(self, "responseHeaderOverrides"))

    @response_header_overrides.setter
    def response_header_overrides(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77f963d5325c428c03673f77b3d64e73a83f78ab723338b3c8459b83f0517ff7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseHeaderOverrides", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFrontendEndpoint).__jsii_proxy_class__ = lambda : _IFrontendEndpointProxy


__all__ = [
    "EdgeAPISwaggerEndpoint",
    "EdgeAPISwaggerEndpointProps",
    "IFrontendEndpoint",
]

publication.publish()

def _typecheckingstub__fdc74e0ca2a2221b8ca8aa5d06fad179f348fbae387543a55d1b2601d3651a40(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api: _reapit_cdk_edge_api_55b0061f.EdgeAPI,
    url: builtins.str,
    path_pattern: typing.Optional[builtins.str] = None,
    repo_root: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca2c5d89bf780de34bcff213eae9d770bd427083ce291cf6ab5adf892950faf1(
    value: _aws_cdk_aws_s3_ceddda9d.Bucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b111b12a1634b66934135f81244d45ac0e4e58a1811155daebd92d9bc2101e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9e3c44b8199e68c8d720b0d018bab53aa2d7f76ebb0728d65a97e5dc5ae5de9(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11fe5cca0131e31848de0f82f2af7b96443bfa133f962de5205131d520e8f8f3(
    *,
    api: _reapit_cdk_edge_api_55b0061f.EdgeAPI,
    url: builtins.str,
    path_pattern: typing.Optional[builtins.str] = None,
    repo_root: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__005ab6bb566912d4a622c17ae06a17c9ebb2e56efb1564995d7667aa455532c6(
    value: _aws_cdk_aws_s3_ceddda9d.Bucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f314d7d684d50ed1bc898a73bc0d3175407bcdee6c25e7a0a5ba4dd3449a9e00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93e1dfeab459fe760b3baf82b26cbc6ab6b939607b4a8a4748f3e8cbef9917cc(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77f963d5325c428c03673f77b3d64e73a83f78ab723338b3c8459b83f0517ff7(
    value: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps],
) -> None:
    """Type checking stubs"""
    pass

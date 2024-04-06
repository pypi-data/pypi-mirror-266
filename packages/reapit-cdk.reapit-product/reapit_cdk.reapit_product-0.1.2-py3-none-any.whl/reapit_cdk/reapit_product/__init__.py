'''
# @reapit-cdk/reapit-product

![npm version](https://img.shields.io/npm/v/@reapit-cdk/reapit-product)
![npm downloads](https://img.shields.io/npm/dm/@reapit-cdk/reapit-product)
![coverage: 0%25](https://img.shields.io/badge/coverage-0%25-red)
![Integ Tests: X](https://img.shields.io/badge/Integ%20Tests-X-red)

Creates a product in the organisations service

## Package Installation:

```sh
yarn add --dev @reapit-cdk/reapit-product
# or
npm install @reapit-cdk/reapit-product --save-dev
```

## Usage

```python
import { CfnOutput, Stack, App } from 'aws-cdk-lib'
import { ReapitProductProvider } from '@reapit-cdk/reapit-product'
import { RestApi } from 'aws-cdk-lib/aws-apigateway'

const app = new App()
const stack = new Stack(app, 'stack-name')

const orgsApiGwId = '' // imported from somewhere or hard coded

const organisationsServiceApiGateway = RestApi.fromRestApiId(stack, 'orgs-api-gw', orgsApiGwId)

const productProvider = new ReapitProductProvider(stack, 'product-provider', {
  organisationsServiceApiGateway,
  stageName: 'api',
})

const product = productProvider.createProduct(stack, 'product', {
  name: 'a product name',
  callbackUrls: [],
  grant: 'authorizationCode',
  isInternalApp: true,
  requiresUserAdmin: false,
  scopes: [],
  signoutUrls: [],
})

new CfnOutput(stack, 'client-id', {
  value: product.externalId,
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

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@reapit-cdk/reapit-product.ProductModel",
    jsii_struct_bases=[],
    name_mapping={
        "auth_flow": "authFlow",
        "created": "created",
        "external_id": "externalId",
        "id": "id",
        "is_internal_app": "isInternalApp",
        "name": "name",
        "scopes": "scopes",
        "usage_key_id": "usageKeyId",
    },
)
class ProductModel:
    def __init__(
        self,
        *,
        auth_flow: builtins.str,
        created: builtins.str,
        external_id: builtins.str,
        id: builtins.str,
        is_internal_app: builtins.bool,
        name: builtins.str,
        scopes: typing.Sequence[builtins.str],
        usage_key_id: builtins.str,
    ) -> None:
        '''Representation of a product.

        :param auth_flow: The auth flow of the product (authorisationCode/clientCredentials).
        :param created: The date and time when the product was created example: 2019-08-14T12:30:02.0000000Z.
        :param external_id: The identifier of the product within the IDP.
        :param id: The unique identifier of the product.
        :param is_internal_app: A flag to determine if the products app is for internal use only.
        :param name: The name of the product.
        :param scopes: The scopes the product has.
        :param usage_key_id: The gateway usage keys identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60e70e4fa6d588982fbc2571bbb7eeec9cd77ed450f5745b5c25d85e1af73d9d)
            check_type(argname="argument auth_flow", value=auth_flow, expected_type=type_hints["auth_flow"])
            check_type(argname="argument created", value=created, expected_type=type_hints["created"])
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument is_internal_app", value=is_internal_app, expected_type=type_hints["is_internal_app"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument scopes", value=scopes, expected_type=type_hints["scopes"])
            check_type(argname="argument usage_key_id", value=usage_key_id, expected_type=type_hints["usage_key_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_flow": auth_flow,
            "created": created,
            "external_id": external_id,
            "id": id,
            "is_internal_app": is_internal_app,
            "name": name,
            "scopes": scopes,
            "usage_key_id": usage_key_id,
        }

    @builtins.property
    def auth_flow(self) -> builtins.str:
        '''The auth flow of the product (authorisationCode/clientCredentials).'''
        result = self._values.get("auth_flow")
        assert result is not None, "Required property 'auth_flow' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created(self) -> builtins.str:
        '''The date and time when the product was created example: 2019-08-14T12:30:02.0000000Z.'''
        result = self._values.get("created")
        assert result is not None, "Required property 'created' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def external_id(self) -> builtins.str:
        '''The identifier of the product within the IDP.'''
        result = self._values.get("external_id")
        assert result is not None, "Required property 'external_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The unique identifier of the product.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_internal_app(self) -> builtins.bool:
        '''A flag to determine if the products app is for internal use only.'''
        result = self._values.get("is_internal_app")
        assert result is not None, "Required property 'is_internal_app' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the product.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scopes(self) -> typing.List[builtins.str]:
        '''The scopes the product has.'''
        result = self._values.get("scopes")
        assert result is not None, "Required property 'scopes' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def usage_key_id(self) -> builtins.str:
        '''The gateway usage keys identifier.'''
        result = self._values.get("usage_key_id")
        assert result is not None, "Required property 'usage_key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProductModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@reapit-cdk/reapit-product.ReapitProduct",
    jsii_struct_bases=[],
    name_mapping={
        "callback_urls": "callbackUrls",
        "grant": "grant",
        "is_internal_app": "isInternalApp",
        "name": "name",
        "requires_user_admin": "requiresUserAdmin",
        "scopes": "scopes",
        "signout_urls": "signoutUrls",
    },
)
class ReapitProduct:
    def __init__(
        self,
        *,
        callback_urls: typing.Sequence[builtins.str],
        grant: builtins.str,
        is_internal_app: builtins.bool,
        name: builtins.str,
        requires_user_admin: builtins.bool,
        scopes: typing.Sequence[builtins.str],
        signout_urls: typing.Sequence[builtins.str],
    ) -> None:
        '''Model to create a new product.

        :param callback_urls: A list of callback urls.
        :param grant: The grant type associated to the product (authorizationCode/clientCredentials).
        :param is_internal_app: A flag to determine if the app is for internal use only.
        :param name: The name of this group.
        :param requires_user_admin: Flag indicating whether or not the product has user admin capabilities that require an additional scope to be set on the OAuth client.
        :param scopes: A list of scopes to assign to the app.
        :param signout_urls: A list of signout urls.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80c19234487bb011fbb752501d004974115f329c3712d389888f39cd7896bbb7)
            check_type(argname="argument callback_urls", value=callback_urls, expected_type=type_hints["callback_urls"])
            check_type(argname="argument grant", value=grant, expected_type=type_hints["grant"])
            check_type(argname="argument is_internal_app", value=is_internal_app, expected_type=type_hints["is_internal_app"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument requires_user_admin", value=requires_user_admin, expected_type=type_hints["requires_user_admin"])
            check_type(argname="argument scopes", value=scopes, expected_type=type_hints["scopes"])
            check_type(argname="argument signout_urls", value=signout_urls, expected_type=type_hints["signout_urls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "callback_urls": callback_urls,
            "grant": grant,
            "is_internal_app": is_internal_app,
            "name": name,
            "requires_user_admin": requires_user_admin,
            "scopes": scopes,
            "signout_urls": signout_urls,
        }

    @builtins.property
    def callback_urls(self) -> typing.List[builtins.str]:
        '''A list of callback urls.'''
        result = self._values.get("callback_urls")
        assert result is not None, "Required property 'callback_urls' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def grant(self) -> builtins.str:
        '''The grant type associated to the product (authorizationCode/clientCredentials).'''
        result = self._values.get("grant")
        assert result is not None, "Required property 'grant' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_internal_app(self) -> builtins.bool:
        '''A flag to determine if the app is for internal use only.'''
        result = self._values.get("is_internal_app")
        assert result is not None, "Required property 'is_internal_app' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of this group.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def requires_user_admin(self) -> builtins.bool:
        '''Flag indicating whether or not the product has user admin capabilities that require an additional scope to be set on the OAuth client.'''
        result = self._values.get("requires_user_admin")
        assert result is not None, "Required property 'requires_user_admin' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def scopes(self) -> typing.List[builtins.str]:
        '''A list of scopes to assign to the app.'''
        result = self._values.get("scopes")
        assert result is not None, "Required property 'scopes' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def signout_urls(self) -> typing.List[builtins.str]:
        '''A list of signout urls.'''
        result = self._values.get("signout_urls")
        assert result is not None, "Required property 'signout_urls' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReapitProduct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReapitProductProvider(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@reapit-cdk/reapit-product.ReapitProductProvider",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        organisations_service_api_gateway: _aws_cdk_aws_apigateway_ceddda9d.IRestApi,
        stage_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param organisations_service_api_gateway: 
        :param stage_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9f52fce75fa6a50d297d58481d4e806b7931c2eff41b9ce0362cf7f39276fe9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ReapitProductProviderProps(
            organisations_service_api_gateway=organisations_service_api_gateway,
            stage_name=stage_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createProduct")
    def create_product(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        callback_urls: typing.Sequence[builtins.str],
        grant: builtins.str,
        is_internal_app: builtins.bool,
        name: builtins.str,
        requires_user_admin: builtins.bool,
        scopes: typing.Sequence[builtins.str],
        signout_urls: typing.Sequence[builtins.str],
    ) -> ProductModel:
        '''
        :param scope: -
        :param id: -
        :param callback_urls: A list of callback urls.
        :param grant: The grant type associated to the product (authorizationCode/clientCredentials).
        :param is_internal_app: A flag to determine if the app is for internal use only.
        :param name: The name of this group.
        :param requires_user_admin: Flag indicating whether or not the product has user admin capabilities that require an additional scope to be set on the OAuth client.
        :param scopes: A list of scopes to assign to the app.
        :param signout_urls: A list of signout urls.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77b85b8720ff262f3b45147c6196d745108378bebc3716576ffbd1fe65274fa2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        product = ReapitProduct(
            callback_urls=callback_urls,
            grant=grant,
            is_internal_app=is_internal_app,
            name=name,
            requires_user_admin=requires_user_admin,
            scopes=scopes,
            signout_urls=signout_urls,
        )

        return typing.cast(ProductModel, jsii.invoke(self, "createProduct", [scope, id, product]))

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: _aws_cdk_custom_resources_ceddda9d.Provider) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8809712e2e43aab01bc2a61bf32819033f55164712ee28c68cd2a43f709407de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value)


@jsii.data_type(
    jsii_type="@reapit-cdk/reapit-product.ReapitProductProviderProps",
    jsii_struct_bases=[],
    name_mapping={
        "organisations_service_api_gateway": "organisationsServiceApiGateway",
        "stage_name": "stageName",
    },
)
class ReapitProductProviderProps:
    def __init__(
        self,
        *,
        organisations_service_api_gateway: _aws_cdk_aws_apigateway_ceddda9d.IRestApi,
        stage_name: builtins.str,
    ) -> None:
        '''
        :param organisations_service_api_gateway: 
        :param stage_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__614e8299fd4e290e1cbcea7dbe8ebf1489d89dad9f09f9dfab1d465a28cf2d45)
            check_type(argname="argument organisations_service_api_gateway", value=organisations_service_api_gateway, expected_type=type_hints["organisations_service_api_gateway"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "organisations_service_api_gateway": organisations_service_api_gateway,
            "stage_name": stage_name,
        }

    @builtins.property
    def organisations_service_api_gateway(
        self,
    ) -> _aws_cdk_aws_apigateway_ceddda9d.IRestApi:
        result = self._values.get("organisations_service_api_gateway")
        assert result is not None, "Required property 'organisations_service_api_gateway' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.IRestApi, result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReapitProductProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProductModel",
    "ReapitProduct",
    "ReapitProductProvider",
    "ReapitProductProviderProps",
]

publication.publish()

def _typecheckingstub__60e70e4fa6d588982fbc2571bbb7eeec9cd77ed450f5745b5c25d85e1af73d9d(
    *,
    auth_flow: builtins.str,
    created: builtins.str,
    external_id: builtins.str,
    id: builtins.str,
    is_internal_app: builtins.bool,
    name: builtins.str,
    scopes: typing.Sequence[builtins.str],
    usage_key_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80c19234487bb011fbb752501d004974115f329c3712d389888f39cd7896bbb7(
    *,
    callback_urls: typing.Sequence[builtins.str],
    grant: builtins.str,
    is_internal_app: builtins.bool,
    name: builtins.str,
    requires_user_admin: builtins.bool,
    scopes: typing.Sequence[builtins.str],
    signout_urls: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9f52fce75fa6a50d297d58481d4e806b7931c2eff41b9ce0362cf7f39276fe9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    organisations_service_api_gateway: _aws_cdk_aws_apigateway_ceddda9d.IRestApi,
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77b85b8720ff262f3b45147c6196d745108378bebc3716576ffbd1fe65274fa2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    callback_urls: typing.Sequence[builtins.str],
    grant: builtins.str,
    is_internal_app: builtins.bool,
    name: builtins.str,
    requires_user_admin: builtins.bool,
    scopes: typing.Sequence[builtins.str],
    signout_urls: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8809712e2e43aab01bc2a61bf32819033f55164712ee28c68cd2a43f709407de(
    value: _aws_cdk_custom_resources_ceddda9d.Provider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__614e8299fd4e290e1cbcea7dbe8ebf1489d89dad9f09f9dfab1d465a28cf2d45(
    *,
    organisations_service_api_gateway: _aws_cdk_aws_apigateway_ceddda9d.IRestApi,
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

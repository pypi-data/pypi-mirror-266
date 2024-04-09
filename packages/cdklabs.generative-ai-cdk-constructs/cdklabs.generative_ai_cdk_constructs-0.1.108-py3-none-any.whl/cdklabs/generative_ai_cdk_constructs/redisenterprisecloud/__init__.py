'''
# Redis Enterprise Cloud Vector Store Construct Library

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) TypeScript|`@cdklabs/generative-ai-cdk-constructs`|

This construct library provides a class that defines an existing Redis Enterprise Cloud database to be used for a vector store for a Knowledge Base.

## Table of contents

* [API](#api)
* [Redis Enterprise Cloud Vector Store](#redis-enterprise-cloud-vector-store)

## API

See the [API documentation](../../../apidocs/modules/redisenterprisecloud.md).

## Redis Enterprise Cloud Vector Store

```python
import { redisenterprisecloud } from '@cdklabs/generative-ai-cdk-constructs';

new redisenterprisecloud.PineconVectorStore({
  endpoint: 'redis-endpoint',
  vectorIndexName: 'your-index-name',
  credentialsSecretArn: 'arn:aws:secretsmanager:your-region:123456789876:secret:your-key-name'
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

from .._jsii import *


class RedisEnterpriseVectorStore(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/generative-ai-cdk-constructs.redisenterprisecloud.RedisEnterpriseVectorStore",
):
    '''(experimental) Class to define a RedisEnterpriseCloudVectorStore.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        credentials_secret_arn: builtins.str,
        endpoint: builtins.str,
        vector_index_name: builtins.str,
    ) -> None:
        '''
        :param credentials_secret_arn: (experimental) ARN of the secret defining the username, password, serverCertificate, clientCertificate and clientPrivateKey to use when connecting to the Redis Enterprise Cloud database. Learn more in the link below.
        :param endpoint: (experimental) The endpoint URL for your Redis Enterprise Cloud database.
        :param vector_index_name: (experimental) Vector index name of your Redis Enterprise Cloud.

        :stability: experimental
        '''
        props = RedisEnterpriseVectorStoreProps(
            credentials_secret_arn=credentials_secret_arn,
            endpoint=endpoint,
            vector_index_name=vector_index_name,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="credentialsSecretArn")
    def credentials_secret_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "credentialsSecretArn"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="vectorIndexName")
    def vector_index_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "vectorIndexName"))


@jsii.data_type(
    jsii_type="@cdklabs/generative-ai-cdk-constructs.redisenterprisecloud.RedisEnterpriseVectorStoreProps",
    jsii_struct_bases=[],
    name_mapping={
        "credentials_secret_arn": "credentialsSecretArn",
        "endpoint": "endpoint",
        "vector_index_name": "vectorIndexName",
    },
)
class RedisEnterpriseVectorStoreProps:
    def __init__(
        self,
        *,
        credentials_secret_arn: builtins.str,
        endpoint: builtins.str,
        vector_index_name: builtins.str,
    ) -> None:
        '''(experimental) Properties for a RedisEnterpriseCloudVectorStore.

        :param credentials_secret_arn: (experimental) ARN of the secret defining the username, password, serverCertificate, clientCertificate and clientPrivateKey to use when connecting to the Redis Enterprise Cloud database. Learn more in the link below.
        :param endpoint: (experimental) The endpoint URL for your Redis Enterprise Cloud database.
        :param vector_index_name: (experimental) Vector index name of your Redis Enterprise Cloud.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cfb9ae3b9b44e8458cc41a112a0b40e19551879ba0591c788cdd91ff071e2fc)
            check_type(argname="argument credentials_secret_arn", value=credentials_secret_arn, expected_type=type_hints["credentials_secret_arn"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument vector_index_name", value=vector_index_name, expected_type=type_hints["vector_index_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "credentials_secret_arn": credentials_secret_arn,
            "endpoint": endpoint,
            "vector_index_name": vector_index_name,
        }

    @builtins.property
    def credentials_secret_arn(self) -> builtins.str:
        '''(experimental) ARN of the secret defining the username, password, serverCertificate, clientCertificate and clientPrivateKey to use when connecting to the Redis Enterprise Cloud database.

        Learn more in the link below.

        :see: https://docs.redis.com/latest/rc/cloud-integrations/aws-marketplace/aws-bedrock/set-up-redis/
        :stability: experimental
        '''
        result = self._values.get("credentials_secret_arn")
        assert result is not None, "Required property 'credentials_secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''(experimental) The endpoint URL for your Redis Enterprise Cloud database.

        :stability: experimental
        '''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vector_index_name(self) -> builtins.str:
        '''(experimental) Vector index name of your Redis Enterprise Cloud.

        :stability: experimental
        '''
        result = self._values.get("vector_index_name")
        assert result is not None, "Required property 'vector_index_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedisEnterpriseVectorStoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RedisEnterpriseVectorStore",
    "RedisEnterpriseVectorStoreProps",
]

publication.publish()

def _typecheckingstub__5cfb9ae3b9b44e8458cc41a112a0b40e19551879ba0591c788cdd91ff071e2fc(
    *,
    credentials_secret_arn: builtins.str,
    endpoint: builtins.str,
    vector_index_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

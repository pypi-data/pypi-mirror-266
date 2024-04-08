'''
# cdk-rds-dump

cdk-rds-dump is a Constructs library for AWS CDK that provides the functionality to dump the contents of Amazon RDS, generate it as an SQL file, and store it in Amazon S3.

![Architecture](./image/architecture.png)

[![View on Construct Hub](https://constructs.dev/badge?package=cdk-rds-dump)](https://constructs.dev/packages/cdk-rds-dump)
[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/badmintoncryer/cdk-rds-dump)
[![npm version](https://badge.fury.io/js/cdk-rds-dump.svg)](https://badge.fury.io/js/cdk-rds-dump)
[![Build Status](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/build.yml/badge.svg)](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/build.yml)
[![Release Status](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/release.yml/badge.svg)](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![npm downloads](https://img.shields.io/npm/dm/cdk-rds-dump.svg?style=flat)](https://www.npmjs.com/package/cdk-rds-dump)

## Usage

Install from npm:

```sh
npm i cdk-rds-dump
```

Then write CDK code as below:

```python
import { RdsDump, DbEngine } from 'cdk-rds-dump';

declare const rdsCluster: rds.DatabaseCluster;
new RdsDump(this, "RdsDump", {
  dbEngine: DbEngine.MYSQL,
  rdsCluster: cluster,
  databaseName: "testDatabase",
  schedule: events.Schedule.cron({ minute: "0", hour: "0" }),
  lambdaEnv: {
    ENV_VAR: "value",
  },
  createSecretsManagerVPCEndpoint: true,
  createS3GatewayEndpoint: true,
  // DB secret is obtained from rdsCluster.secret as default.
  // If you want to use a different secret, you can specify it as follows.
  // secretId: 'secretsmanager-secret-id',
});
```

## How does it work?

This code creates a new RDS cluster and uses the RdsDump Construct to dump the data from that RDS cluster. The dumped data is generated as an SQL file and stored in Amazon S3.

For detailed usage and details of the parameters, refer to the [API documentation](./API.md).

## Why do we need this construct?

AWS RDS is a very useful managed RDB service and includes, by default, the ability to create snapshots.
However, in some cases, such as for development reasons, it is easier to handle SQL files dumped from the DB.
Therefore, cdk-rds-dump was created as a construct to easily create SQL files on a regular basis.

## Contribution

Contributions to the project are welcome. Submit improvement proposals via pull requests or propose new features.

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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="cdk-rds-dump.DbEngine")
class DbEngine(enum.Enum):
    MYSQL = "MYSQL"


class RdsDump(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-rds-dump.RdsDump",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        database_name: builtins.str,
        db_engine: DbEngine,
        rds_cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
        schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
        create_s3_gateway_endpoint: typing.Optional[builtins.bool] = None,
        create_secrets_manager_vpc_endpoint: typing.Optional[builtins.bool] = None,
        id_suffix: typing.Optional[builtins.str] = None,
        lambda_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        lambda_nsg: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        secret_id: typing.Optional[builtins.str] = None,
        secrets_manager_vpc_endpoint_nsg_id: typing.Optional[builtins.str] = None,
        unsecure_password: typing.Optional[builtins.str] = None,
        unsecure_user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param database_name: Database name to dump.
        :param db_engine: Select DB engine type. Currently only mysql can be selected.
        :param rds_cluster: RDS Cluster to dump.
        :param schedule: Schedule to dump. See aws-cdk-lib/aws-events.Schedule. ex. import * as events from 'aws-cdk-lib/aws-events' // It is executed daily at 00:00 UTC. events.Schedule.cron({ minute: "0", hour: "0" })
        :param create_s3_gateway_endpoint: Whether to create an S3 Gateway Endpoint for the VPC where the RDS is located. Default: false
        :param create_secrets_manager_vpc_endpoint: Whether to create an Interface Endpoint for the Secrets Manager. It is recommended to use a secret stored in the Secrets Manager, but in that case, the lambda doing the dump needs a route to access the Secrets Manager. If createSecretsManagerVPCEndpoint is true, an Interface Endpoint is created to allow access to the Secrets Manager. Default: false
        :param id_suffix: Suffix to add to the resource ID. Default: - no suffix
        :param lambda_env: Environment variables to set in the lambda function. ex. { "ENV_VAR": "value" } Default: - no environment variables
        :param lambda_nsg: Security group to allow access to the lambda function. Default: - use auto generated security group
        :param memory_size: The amount of memory in MB allocated to the Lambda function. Default: 1024
        :param secret_id: Secret id for database connection information stored in the Secrets Manager. We recommend using the secret stored in the Secrets Manager as the connection information to the DB, but it is also possible to specify the user name and password directly. If secretId is set, the corresponding secret on SecretsManager is retrieved to access the DB. Default: - use database cluster's secret
        :param secrets_manager_vpc_endpoint_nsg_id: List of IDs of security groups to attach to the Interface Endpoint for Secrets Manager. Only used if createSecretsManagerVPCEndpoint is true. Default: - use auto generated security group
        :param unsecure_password: Database Password. We recommend using the secret stored in the Secrets Manager as the connection information to the DB, but it is also possible to specify the user name and password directly. unsecurePassword is a parameter to pass the password when the ``unsecureUsername`` is used. Default: - do not use unsecurePassword
        :param unsecure_user_name: Database username. We recommend using the secret stored in the Secrets Manager as the connection information to the DB, but it is also possible to specify the user name and password directly. unsecureUserName is a parameter to pass the user name when the ``unsecurePassword`` is used. Default: - do not use unsecureUserName
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a38fc7ecfd277f87fd8e580c47c6b6b6ef0f7559271578ac203a7ce2e09649b7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        __2 = RdsDumpProps(
            database_name=database_name,
            db_engine=db_engine,
            rds_cluster=rds_cluster,
            schedule=schedule,
            create_s3_gateway_endpoint=create_s3_gateway_endpoint,
            create_secrets_manager_vpc_endpoint=create_secrets_manager_vpc_endpoint,
            id_suffix=id_suffix,
            lambda_env=lambda_env,
            lambda_nsg=lambda_nsg,
            memory_size=memory_size,
            secret_id=secret_id,
            secrets_manager_vpc_endpoint_nsg_id=secrets_manager_vpc_endpoint_nsg_id,
            unsecure_password=unsecure_password,
            unsecure_user_name=unsecure_user_name,
        )

        jsii.create(self.__class__, self, [scope, id, __2])


@jsii.data_type(
    jsii_type="cdk-rds-dump.RdsDumpProps",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "db_engine": "dbEngine",
        "rds_cluster": "rdsCluster",
        "schedule": "schedule",
        "create_s3_gateway_endpoint": "createS3GatewayEndpoint",
        "create_secrets_manager_vpc_endpoint": "createSecretsManagerVPCEndpoint",
        "id_suffix": "idSuffix",
        "lambda_env": "lambdaEnv",
        "lambda_nsg": "lambdaNsg",
        "memory_size": "memorySize",
        "secret_id": "secretId",
        "secrets_manager_vpc_endpoint_nsg_id": "secretsManagerVPCEndpointNsgId",
        "unsecure_password": "unsecurePassword",
        "unsecure_user_name": "unsecureUserName",
    },
)
class RdsDumpProps:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        db_engine: DbEngine,
        rds_cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
        schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
        create_s3_gateway_endpoint: typing.Optional[builtins.bool] = None,
        create_secrets_manager_vpc_endpoint: typing.Optional[builtins.bool] = None,
        id_suffix: typing.Optional[builtins.str] = None,
        lambda_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        lambda_nsg: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        secret_id: typing.Optional[builtins.str] = None,
        secrets_manager_vpc_endpoint_nsg_id: typing.Optional[builtins.str] = None,
        unsecure_password: typing.Optional[builtins.str] = None,
        unsecure_user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param database_name: Database name to dump.
        :param db_engine: Select DB engine type. Currently only mysql can be selected.
        :param rds_cluster: RDS Cluster to dump.
        :param schedule: Schedule to dump. See aws-cdk-lib/aws-events.Schedule. ex. import * as events from 'aws-cdk-lib/aws-events' // It is executed daily at 00:00 UTC. events.Schedule.cron({ minute: "0", hour: "0" })
        :param create_s3_gateway_endpoint: Whether to create an S3 Gateway Endpoint for the VPC where the RDS is located. Default: false
        :param create_secrets_manager_vpc_endpoint: Whether to create an Interface Endpoint for the Secrets Manager. It is recommended to use a secret stored in the Secrets Manager, but in that case, the lambda doing the dump needs a route to access the Secrets Manager. If createSecretsManagerVPCEndpoint is true, an Interface Endpoint is created to allow access to the Secrets Manager. Default: false
        :param id_suffix: Suffix to add to the resource ID. Default: - no suffix
        :param lambda_env: Environment variables to set in the lambda function. ex. { "ENV_VAR": "value" } Default: - no environment variables
        :param lambda_nsg: Security group to allow access to the lambda function. Default: - use auto generated security group
        :param memory_size: The amount of memory in MB allocated to the Lambda function. Default: 1024
        :param secret_id: Secret id for database connection information stored in the Secrets Manager. We recommend using the secret stored in the Secrets Manager as the connection information to the DB, but it is also possible to specify the user name and password directly. If secretId is set, the corresponding secret on SecretsManager is retrieved to access the DB. Default: - use database cluster's secret
        :param secrets_manager_vpc_endpoint_nsg_id: List of IDs of security groups to attach to the Interface Endpoint for Secrets Manager. Only used if createSecretsManagerVPCEndpoint is true. Default: - use auto generated security group
        :param unsecure_password: Database Password. We recommend using the secret stored in the Secrets Manager as the connection information to the DB, but it is also possible to specify the user name and password directly. unsecurePassword is a parameter to pass the password when the ``unsecureUsername`` is used. Default: - do not use unsecurePassword
        :param unsecure_user_name: Database username. We recommend using the secret stored in the Secrets Manager as the connection information to the DB, but it is also possible to specify the user name and password directly. unsecureUserName is a parameter to pass the user name when the ``unsecurePassword`` is used. Default: - do not use unsecureUserName
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e5f91888e54819ce8e66b2c7e425c251eafd75500758ab8d657b3e1e91f875)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument db_engine", value=db_engine, expected_type=type_hints["db_engine"])
            check_type(argname="argument rds_cluster", value=rds_cluster, expected_type=type_hints["rds_cluster"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument create_s3_gateway_endpoint", value=create_s3_gateway_endpoint, expected_type=type_hints["create_s3_gateway_endpoint"])
            check_type(argname="argument create_secrets_manager_vpc_endpoint", value=create_secrets_manager_vpc_endpoint, expected_type=type_hints["create_secrets_manager_vpc_endpoint"])
            check_type(argname="argument id_suffix", value=id_suffix, expected_type=type_hints["id_suffix"])
            check_type(argname="argument lambda_env", value=lambda_env, expected_type=type_hints["lambda_env"])
            check_type(argname="argument lambda_nsg", value=lambda_nsg, expected_type=type_hints["lambda_nsg"])
            check_type(argname="argument memory_size", value=memory_size, expected_type=type_hints["memory_size"])
            check_type(argname="argument secret_id", value=secret_id, expected_type=type_hints["secret_id"])
            check_type(argname="argument secrets_manager_vpc_endpoint_nsg_id", value=secrets_manager_vpc_endpoint_nsg_id, expected_type=type_hints["secrets_manager_vpc_endpoint_nsg_id"])
            check_type(argname="argument unsecure_password", value=unsecure_password, expected_type=type_hints["unsecure_password"])
            check_type(argname="argument unsecure_user_name", value=unsecure_user_name, expected_type=type_hints["unsecure_user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "db_engine": db_engine,
            "rds_cluster": rds_cluster,
            "schedule": schedule,
        }
        if create_s3_gateway_endpoint is not None:
            self._values["create_s3_gateway_endpoint"] = create_s3_gateway_endpoint
        if create_secrets_manager_vpc_endpoint is not None:
            self._values["create_secrets_manager_vpc_endpoint"] = create_secrets_manager_vpc_endpoint
        if id_suffix is not None:
            self._values["id_suffix"] = id_suffix
        if lambda_env is not None:
            self._values["lambda_env"] = lambda_env
        if lambda_nsg is not None:
            self._values["lambda_nsg"] = lambda_nsg
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if secret_id is not None:
            self._values["secret_id"] = secret_id
        if secrets_manager_vpc_endpoint_nsg_id is not None:
            self._values["secrets_manager_vpc_endpoint_nsg_id"] = secrets_manager_vpc_endpoint_nsg_id
        if unsecure_password is not None:
            self._values["unsecure_password"] = unsecure_password
        if unsecure_user_name is not None:
            self._values["unsecure_user_name"] = unsecure_user_name

    @builtins.property
    def database_name(self) -> builtins.str:
        '''Database name to dump.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_engine(self) -> DbEngine:
        '''Select DB engine type.

        Currently only mysql can be selected.
        '''
        result = self._values.get("db_engine")
        assert result is not None, "Required property 'db_engine' is missing"
        return typing.cast(DbEngine, result)

    @builtins.property
    def rds_cluster(self) -> _aws_cdk_aws_rds_ceddda9d.DatabaseCluster:
        '''RDS Cluster to dump.'''
        result = self._values.get("rds_cluster")
        assert result is not None, "Required property 'rds_cluster' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.DatabaseCluster, result)

    @builtins.property
    def schedule(self) -> _aws_cdk_aws_events_ceddda9d.Schedule:
        '''Schedule to dump.

        See aws-cdk-lib/aws-events.Schedule.
        ex.
        import * as events from 'aws-cdk-lib/aws-events'
        // It is executed daily at 00:00 UTC.
        events.Schedule.cron({ minute: "0", hour: "0" })
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Schedule, result)

    @builtins.property
    def create_s3_gateway_endpoint(self) -> typing.Optional[builtins.bool]:
        '''Whether to create an S3 Gateway Endpoint for the VPC where the RDS is located.

        :default: false
        '''
        result = self._values.get("create_s3_gateway_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def create_secrets_manager_vpc_endpoint(self) -> typing.Optional[builtins.bool]:
        '''Whether to create an Interface Endpoint for the Secrets Manager.

        It is recommended to use a secret stored in the Secrets Manager,
        but in that case, the lambda doing the dump needs a route to access the Secrets Manager.
        If createSecretsManagerVPCEndpoint is true, an Interface Endpoint is created to allow access to the Secrets Manager.

        :default: false
        '''
        result = self._values.get("create_secrets_manager_vpc_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def id_suffix(self) -> typing.Optional[builtins.str]:
        '''Suffix to add to the resource ID.

        :default: - no suffix
        '''
        result = self._values.get("id_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables to set in the lambda function.

        ex. { "ENV_VAR": "value" }

        :default: - no environment variables
        '''
        result = self._values.get("lambda_env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def lambda_nsg(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security group to allow access to the lambda function.

        :default: - use auto generated security group
        '''
        result = self._values.get("lambda_nsg")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory in MB allocated to the Lambda function.

        :default: 1024
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def secret_id(self) -> typing.Optional[builtins.str]:
        '''Secret id for database connection information stored in the Secrets Manager.

        We recommend using the secret stored in the Secrets Manager as the connection information to the DB,
        but it is also possible to specify the user name and password directly.
        If secretId is set, the corresponding secret on SecretsManager is retrieved to access the DB.

        :default: - use database cluster's secret
        '''
        result = self._values.get("secret_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secrets_manager_vpc_endpoint_nsg_id(self) -> typing.Optional[builtins.str]:
        '''List of IDs of security groups to attach to the Interface Endpoint for Secrets Manager.

        Only used if createSecretsManagerVPCEndpoint is true.

        :default: - use auto generated security group
        '''
        result = self._values.get("secrets_manager_vpc_endpoint_nsg_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unsecure_password(self) -> typing.Optional[builtins.str]:
        '''Database Password.

        We recommend using the secret stored in the Secrets Manager as the connection information to the DB,
        but it is also possible to specify the user name and password directly.
        unsecurePassword is a parameter to pass the password when the ``unsecureUsername`` is used.

        :default: - do not use unsecurePassword
        '''
        result = self._values.get("unsecure_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unsecure_user_name(self) -> typing.Optional[builtins.str]:
        '''Database username.

        We recommend using the secret stored in the Secrets Manager as the connection information to the DB,
        but it is also possible to specify the user name and password directly.
        unsecureUserName is a parameter to pass the user name when the ``unsecurePassword`` is used.

        :default: - do not use unsecureUserName
        '''
        result = self._values.get("unsecure_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsDumpProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DbEngine",
    "RdsDump",
    "RdsDumpProps",
]

publication.publish()

def _typecheckingstub__a38fc7ecfd277f87fd8e580c47c6b6b6ef0f7559271578ac203a7ce2e09649b7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    database_name: builtins.str,
    db_engine: DbEngine,
    rds_cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
    create_s3_gateway_endpoint: typing.Optional[builtins.bool] = None,
    create_secrets_manager_vpc_endpoint: typing.Optional[builtins.bool] = None,
    id_suffix: typing.Optional[builtins.str] = None,
    lambda_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    lambda_nsg: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    memory_size: typing.Optional[jsii.Number] = None,
    secret_id: typing.Optional[builtins.str] = None,
    secrets_manager_vpc_endpoint_nsg_id: typing.Optional[builtins.str] = None,
    unsecure_password: typing.Optional[builtins.str] = None,
    unsecure_user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e5f91888e54819ce8e66b2c7e425c251eafd75500758ab8d657b3e1e91f875(
    *,
    database_name: builtins.str,
    db_engine: DbEngine,
    rds_cluster: _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
    create_s3_gateway_endpoint: typing.Optional[builtins.bool] = None,
    create_secrets_manager_vpc_endpoint: typing.Optional[builtins.bool] = None,
    id_suffix: typing.Optional[builtins.str] = None,
    lambda_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    lambda_nsg: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    memory_size: typing.Optional[jsii.Number] = None,
    secret_id: typing.Optional[builtins.str] = None,
    secrets_manager_vpc_endpoint_nsg_id: typing.Optional[builtins.str] = None,
    unsecure_password: typing.Optional[builtins.str] = None,
    unsecure_user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

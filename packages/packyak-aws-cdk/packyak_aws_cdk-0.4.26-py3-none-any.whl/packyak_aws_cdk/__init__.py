'''
# PackYak ![image](https://github.com/sam-goodwin/packyak/assets/38672686/249af136-45fb-4d13-82bb-5818e803eeb0)

[![PyPI version](https://badge.fury.io/py/packyak.svg)](https://badge.fury.io/py/packyak)

# Packyak AWS CDK

PackYak is a next-generation framework for building and deploying Data Lakehouses in AWS with a Git-like versioned developer workflow that simplifies how Data Scientists and Data Engineers collaborate.

It enables you to deploy your entire Data Lakehouse, ETL and Machine Learning platforms on AWS with no external dependencies, maintain your Data Tables with Git-like versioning semantics and scale data production with Dagster-like Software-defined Asset Graphs.

It combines 5 key technologies into one framework that makes scaling Data Lakehouses and Data Science teams dead simple:

1. Git-like versioning of Data Tables with [Project Nessie](https://projectnessie.org/) - no more worrying about the version of data, simply use branches, tags and commits to freeze data or roll back mistakes.
2. Software-defined Assets (as seen in Dagster) - think of your data pipelines in terms of the data it produces. Greatly simplify how data is produced, modified over time and backfilled in the event of errors.
3. Infrastructure-as-Code (AWS CDK and Pulumi) - deploy in minutes and manage it all yourself with minimal effort.
4. Apache Spark - write your ETL as simple python processes that are then scaled automatically over a managed AWS EMR Spark Cluster.
5. Streamlit - build Streamlit applications that integrate the Data Lakehouse and Apache Spark to provide interactive reports and exploratory tools over the versioned data lake.

# Get Started

## Install Docker

If you haven't already, install [Docker](https://docs.docker.com/get-docker/).

## Install Python Poetry & Plugins

```sh
# Install the Python Poetry CLI
curl -sSL https://install.python-poetry.org | python3 -

# Add the export plugin to generate narrow requirements.txt
poetry self add poetry-plugin-export
```

## Install the `packyak` CLI:

```sh
pip install packyak
```

## Create a new Project

```sh
packyak new my-project
cd ./my-project
```

## Deploy to AWS

```sh
poetry run cdk deploy
```

## Git-like Data Catalog (Project Nessie)

PackYak comes with a Construct for hosting a [Project Nessie](https://projectnessie.org/) catalog that supports Git-like versioning of the tables in a Data Lakehouse.

It deploys with an AWS DynamoDB Versioned store and an API hosted in AWS Lambda or AWS ECS. The Nessie Server is stateless and can be scaled easily with minimal-to-zero operational overhead.

### Create a `NessieDynamoDBVersionStore`

```py
from packyak.aws_cdk import DynamoDBNessieVersionStore

versionStore = DynamoDBNessieVersionStore(
  scope=stack,
  id="VersionStore",
  versionStoreName="my-version-store",
)
```

### Create a Bucket to store Data Tables (e.g. Parquet files). This will store the "Repository"'s data.

```py
myRepoBucket = Bucket(
  scope=stack,
  id="MyCatalogBucket",
)
```

### Create the Nessie Catalog Service

```py
# hosted on AWS ECS
myCatalog = NessieECSCatalog(
  scope=stack,
  id="MyCatalog",
  vpc=vpc,
  warehouseBucket=myRepoBucket,
  catalogName=lakeHouseName,
  versionStore=versionStore,
)
```

### Create a Branch

Branch off the `main` branch of data into a `dev` branch to "freeze" the data as of a particular commit

```sql
CREATE BRANCH dev FROM main
```

## Deploy a Spark Cluster

Create an EMR Cluster for processing data

```py
spark = Cluster(
  scope=stack,
  id="Spark",
  clusterName="my-cluster",
  vpc=vpc,
  catalogs={
    # use the Nessie Catalog as the default data catalog for Spark SQL queries
    "spark_catalog": myCatalog,
  },
  installSSMAgent=true,
)
```

## Configure SparkSQL to be served over JDBC

```py
sparkSQL = spark.jdbc(port=10001)
```

## Deploy Streamlit Site

Stand up a Streamlit Site to serve interactive reports and applications over your data.

```py
site = StreamlitSite(
  scope=stack,
  # Point it at the Streamlit site entrypoint
  home="app/home.py",
  # Where the Streamlit pages/tabs are, defaults to `dirname(home)/pages/*.py`
  # pages="app/pages"
)
```

## Deploy to AWS

```sh
packyak deploy
```

Or via the AWS CDK CLI:

```sh
poetry run cdk deploy
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
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecr_assets as _aws_cdk_aws_ecr_assets_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_ecs_patterns as _aws_cdk_aws_ecs_patterns_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_emr as _aws_cdk_aws_emr_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import aws_cdk.aws_sagemaker as _aws_cdk_aws_sagemaker_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.AddHomeRequest",
    jsii_struct_bases=[],
    name_mapping={
        "uid": "uid",
        "username": "username",
        "gid": "gid",
        "secondary_groups": "secondaryGroups",
    },
)
class AddHomeRequest:
    def __init__(
        self,
        *,
        uid: builtins.str,
        username: builtins.str,
        gid: typing.Optional[builtins.str] = None,
        secondary_groups: typing.Optional[typing.Sequence[typing.Union["PosixGroup", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param uid: (experimental) The POSIX user ID for the user. This should be a unique identifier.
        :param username: (experimental) The username for the user. This should be unique across all users.
        :param gid: (experimental) The POSIX group ID for the user. This is used for file system permissions. Default: - same as the uid
        :param secondary_groups: (experimental) Secondary groups to assign to files written to this home directory.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d365811008c01281a2353f15bcdb3dba02ab02c8a5dd9ac10d125333165a89d6)
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
            check_type(argname="argument secondary_groups", value=secondary_groups, expected_type=type_hints["secondary_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "uid": uid,
            "username": username,
        }
        if gid is not None:
            self._values["gid"] = gid
        if secondary_groups is not None:
            self._values["secondary_groups"] = secondary_groups

    @builtins.property
    def uid(self) -> builtins.str:
        '''(experimental) The POSIX user ID for the user.

        This should be a unique identifier.

        :stability: experimental
        '''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) The username for the user.

        This should be unique across all users.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gid(self) -> typing.Optional[builtins.str]:
        '''(experimental) The POSIX group ID for the user.

        This is used for file system permissions.

        :default: - same as the uid

        :stability: experimental
        '''
        result = self._values.get("gid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_groups(self) -> typing.Optional[typing.List["PosixGroup"]]:
        '''(experimental) Secondary groups to assign to files written to this home directory.

        :stability: experimental
        '''
        result = self._values.get("secondary_groups")
        return typing.cast(typing.Optional[typing.List["PosixGroup"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddHomeRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.AddUserProfileProps",
    jsii_struct_bases=[],
    name_mapping={"execution_role": "executionRole"},
)
class AddUserProfileProps:
    def __init__(
        self,
        *,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param execution_role: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd296c2e747fd9b7a4bd1509b8a55934c797d3968875d41e011bf0fbbb27429a)
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if execution_role is not None:
            self._values["execution_role"] = execution_role

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''
        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddUserProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@packyak/aws-cdk.AdjustmentType")
class AdjustmentType(enum.Enum):
    '''
    :stability: experimental
    '''

    CHANGE_IN_CAPACITY = "CHANGE_IN_CAPACITY"
    '''(experimental) The number of Amazon EC2 instances to add or remove each time the scaling activity is triggered.

    :stability: experimental
    '''
    PERCENT_CHANGE_IN_CAPACITY = "PERCENT_CHANGE_IN_CAPACITY"
    '''(experimental) The percentage of the current instance group size to add or remove each time the scaling activity is triggered.

    :stability: experimental
    '''
    EXACT_CAPACITY = "EXACT_CAPACITY"
    '''(experimental) The exact number of Amazon EC2 instances to add or remove each time the scaling activity is triggered.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@packyak/aws-cdk.AllocationStrategy")
class AllocationStrategy(enum.Enum):
    '''
    :see: https://docs.aws.amazon.com/emr/latest/ManagementGuide/managed-scaling-allocation-strategy.html
    :stability: experimental
    '''

    CAPACITY_OPTIMIZED = "CAPACITY_OPTIMIZED"
    '''
    :stability: experimental
    '''
    PRICE_CAPACITY_OPTIMIZED = "PRICE_CAPACITY_OPTIMIZED"
    '''
    :stability: experimental
    '''
    DIVERSIFIED = "DIVERSIFIED"
    '''
    :stability: experimental
    '''
    LOWEST_PRICE = "LOWEST_PRICE"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@packyak/aws-cdk.AppNetworkAccessType")
class AppNetworkAccessType(enum.Enum):
    '''
    :stability: experimental
    '''

    VPC_ONLY = "VPC_ONLY"
    '''
    :stability: experimental
    '''
    PUBLIC_INTERNET_ONLY = "PUBLIC_INTERNET_ONLY"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@packyak/aws-cdk.AuthMode")
class AuthMode(enum.Enum):
    '''
    :stability: experimental
    '''

    SSO = "SSO"
    '''
    :stability: experimental
    '''
    IAM = "IAM"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.AutoScalingPolicy",
    jsii_struct_bases=[],
    name_mapping={"constraints": "constraints", "rules": "rules"},
)
class AutoScalingPolicy:
    def __init__(
        self,
        *,
        constraints: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union["ScalingConstraints", typing.Dict[builtins.str, typing.Any]]],
        rules: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union["ScalingRule", typing.Dict[builtins.str, typing.Any]]]]],
    ) -> None:
        '''
        :param constraints: (experimental) The upper and lower Amazon EC2 instance limits for an automatic scaling policy. Automatic scaling activity will not cause an instance group to grow above or below these limits.
        :param rules: (experimental) The scale-in and scale-out rules that comprise the automatic scaling policy.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb0021309ff9d8938fdc28d02da5f6f2384cf42812b659fba780b9d43fdc9512)
            check_type(argname="argument constraints", value=constraints, expected_type=type_hints["constraints"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "constraints": constraints,
            "rules": rules,
        }

    @builtins.property
    def constraints(
        self,
    ) -> typing.Union[_aws_cdk_ceddda9d.IResolvable, "ScalingConstraints"]:
        '''(experimental) The upper and lower Amazon EC2 instance limits for an automatic scaling policy.

        Automatic scaling activity will not cause an instance group to grow above or below these limits.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-autoscalingpolicy.html#cfn-emr-cluster-autoscalingpolicy-constraints
        :stability: experimental
        '''
        result = self._values.get("constraints")
        assert result is not None, "Required property 'constraints' is missing"
        return typing.cast(typing.Union[_aws_cdk_ceddda9d.IResolvable, "ScalingConstraints"], result)

    @builtins.property
    def rules(
        self,
    ) -> typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, "ScalingRule"]]]:
        '''(experimental) The scale-in and scale-out rules that comprise the automatic scaling policy.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-autoscalingpolicy.html#cfn-emr-cluster-autoscalingpolicy-rules
        :stability: experimental
        '''
        result = self._values.get("rules")
        assert result is not None, "Required property 'rules' is missing"
        return typing.cast(typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, "ScalingRule"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScalingPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.BaseClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "catalogs": "catalogs",
        "cluster_name": "clusterName",
        "vpc": "vpc",
        "additional_privileged_registries": "additionalPrivilegedRegistries",
        "additional_trusted_registries": "additionalTrustedRegistries",
        "bootstrap_actions": "bootstrapActions",
        "configurations": "configurations",
        "enable_docker": "enableDocker",
        "enable_spark_rapids": "enableSparkRapids",
        "enable_ssm_agent": "enableSSMAgent",
        "enable_xg_boost": "enableXGBoost",
        "environment": "environment",
        "extra_java_options": "extraJavaOptions",
        "home": "home",
        "idle_timeout": "idleTimeout",
        "install_git_hub_cli": "installGitHubCLI",
        "managed_scaling_policy": "managedScalingPolicy",
        "release_label": "releaseLabel",
        "removal_policy": "removalPolicy",
        "scale_down_behavior": "scaleDownBehavior",
        "step_concurrency_level": "stepConcurrencyLevel",
        "steps": "steps",
    },
)
class BaseClusterProps:
    def __init__(
        self,
        *,
        catalogs: typing.Mapping[builtins.str, "ICatalog"],
        cluster_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions: typing.Optional[typing.Sequence[typing.Union["BootstrapAction", typing.Dict[builtins.str, typing.Any]]]] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_docker: typing.Optional[builtins.bool] = None,
        enable_spark_rapids: typing.Optional[builtins.bool] = None,
        enable_ssm_agent: typing.Optional[builtins.bool] = None,
        enable_xg_boost: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        home: typing.Optional["Workspace"] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        install_git_hub_cli: typing.Optional[builtins.bool] = None,
        managed_scaling_policy: typing.Optional[typing.Union["ManagedScalingPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        release_label: typing.Optional["ReleaseLabel"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        scale_down_behavior: typing.Optional["ScaleDownBehavior"] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        steps: typing.Optional[typing.Sequence[typing.Union["Step", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param catalogs: (experimental) The catalogs to use for the EMR cluster.
        :param cluster_name: (experimental) Name of the EMR Cluster.
        :param vpc: (experimental) The VPC to deploy the EMR cluster into.
        :param additional_privileged_registries: (experimental) Additional registries to allow privileged containers from. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param additional_trusted_registries: (experimental) Additional registries to trust for Docker containers. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param bootstrap_actions: Default: - No bootstrap actions
        :param configurations: (experimental) Override EMR Configurations. Default: - the {@link catalog }'s configurations + .venv for the user code.
        :param enable_docker: (experimental) Enable Docker support on the cluster. Default: true
        :param enable_spark_rapids: (experimental) Enable the Spark Rapids plugin. Default: false
        :param enable_ssm_agent: (experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes. Default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``
        :param enable_xg_boost: (experimental) Enable the XGBoost spark library. Default: false
        :param environment: (experimental) Environment variables to make available to the EMR cluster. Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there. Default: - no environment variables
        :param extra_java_options: (experimental) Extra java options to include in the Spark context by default.
        :param home: (experimental) Mount a shared filesystem to the EMR cluster.
        :param idle_timeout: Default: None
        :param install_git_hub_cli: (experimental) Install the GitHub CLI on the EMR cluster. Default: false
        :param managed_scaling_policy: Default: - No managed scaling policy
        :param release_label: Default: - {@link ReleaseLabel.LATEST }
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param scale_down_behavior: Default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }
        :param step_concurrency_level: (experimental) The concurrency level of the cluster. Default: 1
        :param steps: (experimental) The EMR Steps to submit to the cluster.

        :stability: experimental
        '''
        if isinstance(managed_scaling_policy, dict):
            managed_scaling_policy = ManagedScalingPolicy(**managed_scaling_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__170eb3a40128ce3c532930d58e1541d8d16a82652e5d2bb9d601b8207bd708c6)
            check_type(argname="argument catalogs", value=catalogs, expected_type=type_hints["catalogs"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument additional_privileged_registries", value=additional_privileged_registries, expected_type=type_hints["additional_privileged_registries"])
            check_type(argname="argument additional_trusted_registries", value=additional_trusted_registries, expected_type=type_hints["additional_trusted_registries"])
            check_type(argname="argument bootstrap_actions", value=bootstrap_actions, expected_type=type_hints["bootstrap_actions"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
            check_type(argname="argument enable_docker", value=enable_docker, expected_type=type_hints["enable_docker"])
            check_type(argname="argument enable_spark_rapids", value=enable_spark_rapids, expected_type=type_hints["enable_spark_rapids"])
            check_type(argname="argument enable_ssm_agent", value=enable_ssm_agent, expected_type=type_hints["enable_ssm_agent"])
            check_type(argname="argument enable_xg_boost", value=enable_xg_boost, expected_type=type_hints["enable_xg_boost"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument extra_java_options", value=extra_java_options, expected_type=type_hints["extra_java_options"])
            check_type(argname="argument home", value=home, expected_type=type_hints["home"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument install_git_hub_cli", value=install_git_hub_cli, expected_type=type_hints["install_git_hub_cli"])
            check_type(argname="argument managed_scaling_policy", value=managed_scaling_policy, expected_type=type_hints["managed_scaling_policy"])
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument scale_down_behavior", value=scale_down_behavior, expected_type=type_hints["scale_down_behavior"])
            check_type(argname="argument step_concurrency_level", value=step_concurrency_level, expected_type=type_hints["step_concurrency_level"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "catalogs": catalogs,
            "cluster_name": cluster_name,
            "vpc": vpc,
        }
        if additional_privileged_registries is not None:
            self._values["additional_privileged_registries"] = additional_privileged_registries
        if additional_trusted_registries is not None:
            self._values["additional_trusted_registries"] = additional_trusted_registries
        if bootstrap_actions is not None:
            self._values["bootstrap_actions"] = bootstrap_actions
        if configurations is not None:
            self._values["configurations"] = configurations
        if enable_docker is not None:
            self._values["enable_docker"] = enable_docker
        if enable_spark_rapids is not None:
            self._values["enable_spark_rapids"] = enable_spark_rapids
        if enable_ssm_agent is not None:
            self._values["enable_ssm_agent"] = enable_ssm_agent
        if enable_xg_boost is not None:
            self._values["enable_xg_boost"] = enable_xg_boost
        if environment is not None:
            self._values["environment"] = environment
        if extra_java_options is not None:
            self._values["extra_java_options"] = extra_java_options
        if home is not None:
            self._values["home"] = home
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if install_git_hub_cli is not None:
            self._values["install_git_hub_cli"] = install_git_hub_cli
        if managed_scaling_policy is not None:
            self._values["managed_scaling_policy"] = managed_scaling_policy
        if release_label is not None:
            self._values["release_label"] = release_label
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if scale_down_behavior is not None:
            self._values["scale_down_behavior"] = scale_down_behavior
        if step_concurrency_level is not None:
            self._values["step_concurrency_level"] = step_concurrency_level
        if steps is not None:
            self._values["steps"] = steps

    @builtins.property
    def catalogs(self) -> typing.Mapping[builtins.str, "ICatalog"]:
        '''(experimental) The catalogs to use for the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("catalogs")
        assert result is not None, "Required property 'catalogs' is missing"
        return typing.cast(typing.Mapping[builtins.str, "ICatalog"], result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''(experimental) Name of the EMR Cluster.

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to deploy the EMR cluster into.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def additional_privileged_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to allow privileged containers from.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_privileged_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_trusted_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to trust for Docker containers.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_trusted_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bootstrap_actions(self) -> typing.Optional[typing.List["BootstrapAction"]]:
        '''
        :default: - No bootstrap actions

        :stability: experimental
        '''
        result = self._values.get("bootstrap_actions")
        return typing.cast(typing.Optional[typing.List["BootstrapAction"]], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List["Configuration"]]:
        '''(experimental) Override EMR Configurations.

        :default: - the {@link catalog }'s configurations + .venv for the user code.

        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List["Configuration"]], result)

    @builtins.property
    def enable_docker(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Docker support on the cluster.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enable_docker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_spark_rapids(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the Spark Rapids plugin.

        :default: false

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-rapids.html
        :stability: experimental
        '''
        result = self._values.get("enable_spark_rapids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ssm_agent(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes.

        :default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``

        :stability: experimental
        '''
        result = self._values.get("enable_ssm_agent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_xg_boost(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the XGBoost spark library.

        :default: false

        :see: https://docs.nvidia.com/spark-rapids/user-guide/latest/getting-started/aws-emr.html
        :stability: experimental
        '''
        result = self._values.get("enable_xg_boost")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables to make available to the EMR cluster.

        Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there.

        :default: - no environment variables

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def extra_java_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Extra java options to include in the Spark context by default.

        :stability: experimental
        '''
        result = self._values.get("extra_java_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def home(self) -> typing.Optional["Workspace"]:
        '''(experimental) Mount a shared filesystem to the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("home")
        return typing.cast(typing.Optional["Workspace"], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''
        :default: None

        :stability: experimental
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def install_git_hub_cli(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install the GitHub CLI on the EMR cluster.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("install_git_hub_cli")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_scaling_policy(self) -> typing.Optional["ManagedScalingPolicy"]:
        '''
        :default: - No managed scaling policy

        :stability: experimental
        '''
        result = self._values.get("managed_scaling_policy")
        return typing.cast(typing.Optional["ManagedScalingPolicy"], result)

    @builtins.property
    def release_label(self) -> typing.Optional["ReleaseLabel"]:
        '''
        :default: - {@link ReleaseLabel.LATEST }

        :stability: experimental
        '''
        result = self._values.get("release_label")
        return typing.cast(typing.Optional["ReleaseLabel"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :default: {@link RemovalPolicy.DESTROY }

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def scale_down_behavior(self) -> typing.Optional["ScaleDownBehavior"]:
        '''
        :default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }

        :stability: experimental
        '''
        result = self._values.get("scale_down_behavior")
        return typing.cast(typing.Optional["ScaleDownBehavior"], result)

    @builtins.property
    def step_concurrency_level(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The concurrency level of the cluster.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("step_concurrency_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def steps(self) -> typing.Optional[typing.List["Step"]]:
        '''(experimental) The EMR Steps to submit to the cluster.

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-submit-step.html
        :stability: experimental
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.List["Step"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.BaseNessieRepoProps",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_name": "catalogName",
        "default_main_branch": "defaultMainBranch",
        "log_group": "logGroup",
        "removal_policy": "removalPolicy",
        "version_store": "versionStore",
        "warehouse_bucket": "warehouseBucket",
        "warehouse_prefix": "warehousePrefix",
    },
)
class BaseNessieRepoProps:
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        default_main_branch: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store: typing.Optional["DynamoDBNessieVersionStore"] = None,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: (experimental) The name of this catalog in the Spark Context. Default: spark_catalog - i.e. the default catalog
        :param default_main_branch: (experimental) The default main branch of a Nessie repository. Default: main
        :param log_group: (experimental) The log group to use for the Nessie service. Default: - a new log group is created for you
        :param removal_policy: (experimental) The removal policy to apply to the Nessie service. Default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.
        :param version_store: (experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.
        :param warehouse_bucket: Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix to use for the warehouse path. Default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb1113f4b23cb04ea5bb029de40f2c712e0a43e86df2d0cdff19138f0252493e)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument default_main_branch", value=default_main_branch, expected_type=type_hints["default_main_branch"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument version_store", value=version_store, expected_type=type_hints["version_store"])
            check_type(argname="argument warehouse_bucket", value=warehouse_bucket, expected_type=type_hints["warehouse_bucket"])
            check_type(argname="argument warehouse_prefix", value=warehouse_prefix, expected_type=type_hints["warehouse_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if default_main_branch is not None:
            self._values["default_main_branch"] = default_main_branch
        if log_group is not None:
            self._values["log_group"] = log_group
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if version_store is not None:
            self._values["version_store"] = version_store
        if warehouse_bucket is not None:
            self._values["warehouse_bucket"] = warehouse_bucket
        if warehouse_prefix is not None:
            self._values["warehouse_prefix"] = warehouse_prefix

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of this catalog in the Spark Context.

        :default: spark_catalog - i.e. the default catalog

        :stability: experimental
        '''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_main_branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The default main branch of a Nessie repository.

        :default: main

        :stability: experimental
        '''
        result = self._values.get("default_main_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) The log group to use for the Nessie service.

        :default: - a new log group is created for you

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply to the Nessie service.

        :default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def version_store(self) -> typing.Optional["DynamoDBNessieVersionStore"]:
        '''(experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.

        :stability: experimental
        '''
        result = self._values.get("version_store")
        return typing.cast(typing.Optional["DynamoDBNessieVersionStore"], result)

    @builtins.property
    def warehouse_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''
        :default: - one is created for you

        :stability: experimental
        '''
        result = self._values.get("warehouse_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def warehouse_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The prefix to use for the warehouse path.

        :default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        result = self._values.get("warehouse_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseNessieRepoProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.BootstrapAction",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "script": "script", "args": "args"},
)
class BootstrapAction:
    def __init__(
        self,
        *,
        name: builtins.str,
        script: _aws_cdk_aws_s3_assets_ceddda9d.Asset,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: 
        :param script: 
        :param args: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17ee3e3194d801bb8f4751d17f0543d30fc618c893f3829dbd99fce2aa368326)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument script", value=script, expected_type=type_hints["script"])
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "script": script,
        }
        if args is not None:
            self._values["args"] = args

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def script(self) -> _aws_cdk_aws_s3_assets_ceddda9d.Asset:
        '''
        :stability: experimental
        '''
        result = self._values.get("script")
        assert result is not None, "Required property 'script' is missing"
        return typing.cast(_aws_cdk_aws_s3_assets_ceddda9d.Asset, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BootstrapAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.CloudWatchAlarmDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "comparison_operator": "comparisonOperator",
        "metric_name": "metricName",
        "period": "period",
        "threshold": "threshold",
        "dimensions": "dimensions",
        "evaluation_periods": "evaluationPeriods",
        "namespace": "namespace",
        "statistic": "statistic",
        "unit": "unit",
    },
)
class CloudWatchAlarmDefinition:
    def __init__(
        self,
        *,
        comparison_operator: builtins.str,
        metric_name: builtins.str,
        period: jsii.Number,
        threshold: jsii.Number,
        dimensions: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union["MetricDimension", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''``CloudWatchAlarmDefinition`` is a subproperty of the ``ScalingTrigger`` property, which determines when to trigger an automatic scaling activity.

        Scaling activity begins when you satisfy the defined alarm conditions.

        :param comparison_operator: Determines how the metric specified by ``MetricName`` is compared to the value specified by ``Threshold`` .
        :param metric_name: The name of the CloudWatch metric that is watched to determine an alarm condition.
        :param period: The period, in seconds, over which the statistic is applied. CloudWatch metrics for Amazon EMR are emitted every five minutes (300 seconds), so if you specify a CloudWatch metric, specify ``300`` .
        :param threshold: The value against which the specified statistic is compared.
        :param dimensions: A CloudWatch metric dimension.
        :param evaluation_periods: The number of periods, in five-minute increments, during which the alarm condition must exist before the alarm triggers automatic scaling activity. The default value is ``1`` .
        :param namespace: The namespace for the CloudWatch metric. The default is ``AWS/ElasticMapReduce`` .
        :param statistic: The statistic to apply to the metric associated with the alarm. The default is ``AVERAGE`` .
        :param unit: The unit of measure associated with the CloudWatch metric being watched. The value specified for ``Unit`` must correspond to the units specified in the CloudWatch metric.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42c7d99699b235e40f3519ebdbc280f257a91f1adc441108f8353377f4061b3c)
            check_type(argname="argument comparison_operator", value=comparison_operator, expected_type=type_hints["comparison_operator"])
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "comparison_operator": comparison_operator,
            "metric_name": metric_name,
            "period": period,
            "threshold": threshold,
        }
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if namespace is not None:
            self._values["namespace"] = namespace
        if statistic is not None:
            self._values["statistic"] = statistic
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def comparison_operator(self) -> builtins.str:
        '''Determines how the metric specified by ``MetricName`` is compared to the value specified by ``Threshold`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-comparisonoperator
        '''
        result = self._values.get("comparison_operator")
        assert result is not None, "Required property 'comparison_operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''The name of the CloudWatch metric that is watched to determine an alarm condition.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-metricname
        '''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> jsii.Number:
        '''The period, in seconds, over which the statistic is applied.

        CloudWatch metrics for Amazon EMR are emitted every five minutes (300 seconds), so if you specify a CloudWatch metric, specify ``300`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-period
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''The value against which the specified statistic is compared.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-threshold
        '''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, "MetricDimension"]]]]:
        '''A CloudWatch metric dimension.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-dimensions
        '''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, "MetricDimension"]]]], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''The number of periods, in five-minute increments, during which the alarm condition must exist before the alarm triggers automatic scaling activity.

        The default value is ``1`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-evaluationperiods
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The namespace for the CloudWatch metric.

        The default is ``AWS/ElasticMapReduce`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-namespace
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''The statistic to apply to the metric associated with the alarm.

        The default is ``AVERAGE`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-statistic
        '''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''The unit of measure associated with the CloudWatch metric being watched.

        The value specified for ``Unit`` must correspond to the units specified in the CloudWatch metric.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-cloudwatchalarmdefinition.html#cfn-emr-cluster-cloudwatchalarmdefinition-unit
        '''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudWatchAlarmDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_iam_ceddda9d.IGrantable, _aws_cdk_aws_ec2_ceddda9d.IConnectable)
class Cluster(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.Cluster",
):
    '''(experimental) An EMR Cluster.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        core_instance_fleet: typing.Optional[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]] = None,
        core_instance_group: typing.Optional[typing.Union["InstanceGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_instance_fleet: typing.Optional[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_instance_group: typing.Optional[typing.Union["PrimaryInstanceGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        task_instance_fleets: typing.Optional[typing.Sequence[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]]] = None,
        task_instance_groups: typing.Optional[typing.Sequence[typing.Union["InstanceGroup", typing.Dict[builtins.str, typing.Any]]]] = None,
        catalogs: typing.Mapping[builtins.str, "ICatalog"],
        cluster_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_docker: typing.Optional[builtins.bool] = None,
        enable_spark_rapids: typing.Optional[builtins.bool] = None,
        enable_ssm_agent: typing.Optional[builtins.bool] = None,
        enable_xg_boost: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        home: typing.Optional["Workspace"] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        install_git_hub_cli: typing.Optional[builtins.bool] = None,
        managed_scaling_policy: typing.Optional[typing.Union["ManagedScalingPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        release_label: typing.Optional["ReleaseLabel"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        scale_down_behavior: typing.Optional["ScaleDownBehavior"] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        steps: typing.Optional[typing.Sequence[typing.Union["Step", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param core_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the core {@link InstanceFleet} when using {@link FleetCluster}s.
        :param core_instance_group: (experimental) Describes the EC2 instances and instance configurations for core {@link InstanceGroup}s when using {@link UniformCluster}s.
        :param primary_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the master {@link InstanceFleet} when using {@link FleetCluster}s.
        :param primary_instance_group: (experimental) Describes the EC2 instances and instance configurations for the master {@link InstanceGroup} when using {@link UniformCluster}s.
        :param task_instance_fleets: (experimental) Describes the EC2 instances and instance configurations for the task {@link InstanceFleet}s when using {@link FleetCluster}s. These task {@link InstanceFleet}s are added to the cluster as part of the cluster launch. Each task {@link InstanceFleet} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceFleet}s. .. epigraph:: You can currently specify only one task instance fleet for a cluster. After creating the cluster, you can only modify the mutable properties of ``InstanceFleetConfig`` , which are ``TargetOnDemandCapacity`` and ``TargetSpotCapacity`` . Modifying any other property results in cluster replacement. > To allow a maximum of 30 Amazon EC2 instance types per fleet, include ``TaskInstanceFleets`` when you create your cluster. If you create your cluster without ``TaskInstanceFleets`` , Amazon EMR uses its default allocation strategy, which allows for a maximum of five Amazon EC2 instance types.
        :param task_instance_groups: (experimental) Describes the EC2 instances and instance configurations for task {@link InstanceGroup}s when using {@link UniformCluster}s. These task {@link InstanceGroup}s are added to the cluster as part of the cluster launch. Each task {@link InstanceGroup} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceGroup}s. .. epigraph:: After creating the cluster, you can only modify the mutable properties of ``InstanceGroupConfig`` , which are ``AutoScalingPolicy`` and ``InstanceCount`` . Modifying any other property results in cluster replacement.
        :param catalogs: (experimental) The catalogs to use for the EMR cluster.
        :param cluster_name: (experimental) Name of the EMR Cluster.
        :param vpc: (experimental) The VPC to deploy the EMR cluster into.
        :param additional_privileged_registries: (experimental) Additional registries to allow privileged containers from. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param additional_trusted_registries: (experimental) Additional registries to trust for Docker containers. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param bootstrap_actions: Default: - No bootstrap actions
        :param configurations: (experimental) Override EMR Configurations. Default: - the {@link catalog }'s configurations + .venv for the user code.
        :param enable_docker: (experimental) Enable Docker support on the cluster. Default: true
        :param enable_spark_rapids: (experimental) Enable the Spark Rapids plugin. Default: false
        :param enable_ssm_agent: (experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes. Default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``
        :param enable_xg_boost: (experimental) Enable the XGBoost spark library. Default: false
        :param environment: (experimental) Environment variables to make available to the EMR cluster. Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there. Default: - no environment variables
        :param extra_java_options: (experimental) Extra java options to include in the Spark context by default.
        :param home: (experimental) Mount a shared filesystem to the EMR cluster.
        :param idle_timeout: Default: None
        :param install_git_hub_cli: (experimental) Install the GitHub CLI on the EMR cluster. Default: false
        :param managed_scaling_policy: Default: - No managed scaling policy
        :param release_label: Default: - {@link ReleaseLabel.LATEST }
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param scale_down_behavior: Default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }
        :param step_concurrency_level: (experimental) The concurrency level of the cluster. Default: 1
        :param steps: (experimental) The EMR Steps to submit to the cluster.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__326dd028735c17e7178d84ab14e8c6beb9f3765f8638e57a971fb58271219792)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ClusterProps(
            core_instance_fleet=core_instance_fleet,
            core_instance_group=core_instance_group,
            primary_instance_fleet=primary_instance_fleet,
            primary_instance_group=primary_instance_group,
            task_instance_fleets=task_instance_fleets,
            task_instance_groups=task_instance_groups,
            catalogs=catalogs,
            cluster_name=cluster_name,
            vpc=vpc,
            additional_privileged_registries=additional_privileged_registries,
            additional_trusted_registries=additional_trusted_registries,
            bootstrap_actions=bootstrap_actions,
            configurations=configurations,
            enable_docker=enable_docker,
            enable_spark_rapids=enable_spark_rapids,
            enable_ssm_agent=enable_ssm_agent,
            enable_xg_boost=enable_xg_boost,
            environment=environment,
            extra_java_options=extra_java_options,
            home=home,
            idle_timeout=idle_timeout,
            install_git_hub_cli=install_git_hub_cli,
            managed_scaling_policy=managed_scaling_policy,
            release_label=release_label,
            removal_policy=removal_policy,
            scale_down_behavior=scale_down_behavior,
            step_concurrency_level=step_concurrency_level,
            steps=steps,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addBootstrapAction")
    def add_bootstrap_action(
        self,
        *,
        name: builtins.str,
        script: _aws_cdk_aws_s3_assets_ceddda9d.Asset,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Add a Bootstrap Action to the cluster.

        Bootstrap actions are scripts that run on the cluster before Hadoop starts.

        :param name: 
        :param script: 
        :param args: 

        :see: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-bootstrap.html
        :stability: experimental
        '''
        action = BootstrapAction(name=name, script=script, args=args)

        return typing.cast(None, jsii.invoke(self, "addBootstrapAction", [action]))

    @jsii.member(jsii_name="addConfig")
    def add_config(self, *configurations: "Configuration") -> None:
        '''(experimental) Add EMR Configurations to the cluster.

        E.g. spark or hive configurations.

        :param configurations: additional configurations to add.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcb74dd3ad16954dfc52d59289b7aa9ccd07b7dd4fbd7fa75c253348f2932832)
            check_type(argname="argument configurations", value=configurations, expected_type=typing.Tuple[type_hints["configurations"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addConfig", [*configurations]))

    @jsii.member(jsii_name="addStep")
    def add_step(
        self,
        *,
        hadoop_jar_step: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emr_ceddda9d.CfnCluster.HadoopJarStepConfigProperty, typing.Dict[builtins.str, typing.Any]]],
        name: builtins.str,
        action_on_failure: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add an EMR Step to the cluster.

        This step will run when the cluster is started.

        :param hadoop_jar_step: The JAR file used for the step.
        :param name: The name of the step.
        :param action_on_failure: The action to take when the cluster step fails. Possible values are ``CANCEL_AND_WAIT`` and ``CONTINUE`` .

        :stability: experimental
        '''
        step = Step(
            hadoop_jar_step=hadoop_jar_step,
            name=name,
            action_on_failure=action_on_failure,
        )

        return typing.cast(None, jsii.invoke(self, "addStep", [step]))

    @jsii.member(jsii_name="allowLivyFrom")
    def allow_livy_from(self, other: _aws_cdk_aws_ec2_ceddda9d.IConnectable) -> None:
        '''(experimental) Allows connections to the Livy server on port 8998 from the specified {@link other} security group.

        :param other: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc9b2f0743c1e90f3938a277ebc0eb6024ab132d898a5290097146f15891b622)
            check_type(argname="argument other", value=other, expected_type=type_hints["other"])
        return typing.cast(None, jsii.invoke(self, "allowLivyFrom", [other]))

    @jsii.member(jsii_name="enableSSMAgent")
    def enable_ssm_agent(self) -> None:
        '''(experimental) Installs the SSM Agent on Primary, Core, and Task nodes.

        Authorizes the EC2 instances to communicate with the SSM service.

        :see: https://aws.amazon.com/blogs/big-data/securing-access-to-emr-clusters-using-aws-systems-manager/
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "enableSSMAgent", []))

    @jsii.member(jsii_name="grantStartSSMSession")
    def grant_start_ssm_session(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''(experimental) Grant an permission to start an SSM Session on the EMR cluster.

        :param grantee: the principal to grant the permission to. // TODO: figure out how to use SSM Session Documents to: // 1. customize where state is store and encrypt it // 2. customize other session properties // 3. constrain access with IAM Condition: ssm:SessionDocumentAccessCheck

        :see: https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-specify-session-document.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a5bb4ccf54350bc9166401e5fd426d8d9608356ea47b38b22d8cfe924c69419)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantStartSSMSession", [grantee]))

    @jsii.member(jsii_name="installGitHubCLI")
    def install_git_hub_cli(self) -> None:
        '''(experimental) Install the GitHub CLI on the EMR cluster.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "installGitHubCLI", []))

    @jsii.member(jsii_name="installNvidiaContainerToolkit")
    def install_nvidia_container_toolkit(self) -> None:
        '''(experimental) Install the NVidia drivers on the EMR cluster.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "installNvidiaContainerToolkit", []))

    @jsii.member(jsii_name="installNvidiaDrivers")
    def install_nvidia_drivers(self) -> None:
        '''(experimental) Install the NVidia drivers on the EMR cluster.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "installNvidiaDrivers", []))

    @jsii.member(jsii_name="jdbc")
    def jdbc(
        self,
        *,
        port: jsii.Number,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hive_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        include_extensions: typing.Optional[builtins.bool] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> "Jdbc":
        '''(experimental) Configure the EMR cluster start the Thrift Server and serve JDBC requests on the specified port.

        :param port: 
        :param extra_java_options: 
        :param hive_conf: 
        :param include_extensions: (experimental) Include tje .ivy2/jars directory so that the server will pick up extra extensions. Default: true
        :param spark_conf: 

        :return: a reference to the JDBC server

        :stability: experimental

        Example::

            const sparkSQL = cluster.jdbc({
             port: 10000,
            });
            sparkSQL.allowFrom(sageMakerDomain);
        '''
        options = JdbcProps(
            port=port,
            extra_java_options=extra_java_options,
            hive_conf=hive_conf,
            include_extensions=include_extensions,
            spark_conf=spark_conf,
        )

        return typing.cast("Jdbc", jsii.invoke(self, "jdbc", [options]))

    @jsii.member(jsii_name="mount")
    def mount(self, home: "Home") -> None:
        '''(experimental) Mount a {@link Home} directory onto the File System.

        :param home: the home directory to mount.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa1e982fa3c2429881ad2232928af4534f82f46a6edd9c77529f3e60b1f292b7)
            check_type(argname="argument home", value=home, expected_type=type_hints["home"])
        return typing.cast(None, jsii.invoke(self, "mount", [home]))

    @jsii.member(jsii_name="mountAccessPoint")
    def mount_access_point(
        self,
        access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
        *,
        gid: jsii.Number,
        mount_point: builtins.str,
        uid: jsii.Number,
        username: builtins.str,
    ) -> None:
        '''(experimental) Mount an EFS Access Point on the EMR cluster.

        :param access_point: the EFS Access Point to mount.
        :param gid: 
        :param mount_point: 
        :param uid: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf2b2f138734f7c01c625c41cc6dbe8d545ea0347ef4dfc43d9d6dabbd0c7ce1)
            check_type(argname="argument access_point", value=access_point, expected_type=type_hints["access_point"])
        options = MountFileSystemOptions(
            gid=gid, mount_point=mount_point, uid=uid, username=username
        )

        return typing.cast(None, jsii.invoke(self, "mountAccessPoint", [access_point, options]))

    @jsii.member(jsii_name="mountFileSystem")
    def mount_file_system(
        self,
        file_system: _aws_cdk_aws_efs_ceddda9d.IFileSystem,
        *,
        gid: jsii.Number,
        mount_point: builtins.str,
        uid: jsii.Number,
        username: builtins.str,
    ) -> None:
        '''(experimental) Mount an EFS File System on the EMR cluster.

        :param file_system: the EFS File System to mount.
        :param gid: 
        :param mount_point: 
        :param uid: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ed7bdb70f76a68cd9abec9d8ea3a1d9869cb673dd864bc41ba4fadbe8e27e19)
            check_type(argname="argument file_system", value=file_system, expected_type=type_hints["file_system"])
        options = MountFileSystemOptions(
            gid=gid, mount_point=mount_point, uid=uid, username=username
        )

        return typing.cast(None, jsii.invoke(self, "mountFileSystem", [file_system, options]))

    @jsii.member(jsii_name="mountYarnCGroups")
    def mount_yarn_c_groups(self) -> None:
        '''(experimental) Mounts YARN cgroups if not already mounted.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "mountYarnCGroups", []))

    @jsii.member(jsii_name="setupHadoopUsers")
    def setup_hadoop_users(self) -> None:
        '''(experimental) Setup Hadoop Users on the EMR cluster.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "setupHadoopUsers", []))

    @jsii.member(jsii_name="writeEnvironmentVariables")
    def _write_environment_variables(
        self,
        variables: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''(experimental) Write environment variables to the EMR cluster.

        Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there.

        :param variables: the environment variables to write.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d87af115c92712f3e3fbf2f42cdf8628fccc2ffafa0ca1ad4221ce3685635cf6)
            check_type(argname="argument variables", value=variables, expected_type=type_hints["variables"])
        return typing.cast(None, jsii.invoke(self, "writeEnvironmentVariables", [variables]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="coreSg")
    def core_sg(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "coreSg"))

    @builtins.property
    @jsii.member(jsii_name="extraJavaOptions")
    def extra_java_options(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "extraJavaOptions"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> _aws_cdk_aws_iam_ceddda9d.InstanceProfile:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.InstanceProfile, jsii.get(self, "instanceProfile"))

    @builtins.property
    @jsii.member(jsii_name="jobFlowRole")
    def job_flow_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "jobFlowRole"))

    @builtins.property
    @jsii.member(jsii_name="primarySg")
    def primary_sg(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "primarySg"))

    @builtins.property
    @jsii.member(jsii_name="release")
    def release(self) -> "ReleaseLabel":
        '''
        :stability: experimental
        '''
        return typing.cast("ReleaseLabel", jsii.get(self, "release"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def _resource(self) -> _aws_cdk_aws_emr_ceddda9d.CfnCluster:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_emr_ceddda9d.CfnCluster, jsii.get(self, "resource"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccessSg")
    def service_access_sg(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "serviceAccessSg"))

    @builtins.property
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "serviceRole"))

    @builtins.property
    @jsii.member(jsii_name="taskInstanceFleets")
    def _task_instance_fleets(self) -> typing.List["InstanceFleet"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["InstanceFleet"], jsii.get(self, "taskInstanceFleets"))

    @builtins.property
    @jsii.member(jsii_name="taskInstanceGroups")
    def _task_instance_groups(self) -> typing.List["InstanceGroup"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["InstanceGroup"], jsii.get(self, "taskInstanceGroups"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.ClusterProps",
    jsii_struct_bases=[BaseClusterProps],
    name_mapping={
        "catalogs": "catalogs",
        "cluster_name": "clusterName",
        "vpc": "vpc",
        "additional_privileged_registries": "additionalPrivilegedRegistries",
        "additional_trusted_registries": "additionalTrustedRegistries",
        "bootstrap_actions": "bootstrapActions",
        "configurations": "configurations",
        "enable_docker": "enableDocker",
        "enable_spark_rapids": "enableSparkRapids",
        "enable_ssm_agent": "enableSSMAgent",
        "enable_xg_boost": "enableXGBoost",
        "environment": "environment",
        "extra_java_options": "extraJavaOptions",
        "home": "home",
        "idle_timeout": "idleTimeout",
        "install_git_hub_cli": "installGitHubCLI",
        "managed_scaling_policy": "managedScalingPolicy",
        "release_label": "releaseLabel",
        "removal_policy": "removalPolicy",
        "scale_down_behavior": "scaleDownBehavior",
        "step_concurrency_level": "stepConcurrencyLevel",
        "steps": "steps",
        "core_instance_fleet": "coreInstanceFleet",
        "core_instance_group": "coreInstanceGroup",
        "primary_instance_fleet": "primaryInstanceFleet",
        "primary_instance_group": "primaryInstanceGroup",
        "task_instance_fleets": "taskInstanceFleets",
        "task_instance_groups": "taskInstanceGroups",
    },
)
class ClusterProps(BaseClusterProps):
    def __init__(
        self,
        *,
        catalogs: typing.Mapping[builtins.str, "ICatalog"],
        cluster_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_docker: typing.Optional[builtins.bool] = None,
        enable_spark_rapids: typing.Optional[builtins.bool] = None,
        enable_ssm_agent: typing.Optional[builtins.bool] = None,
        enable_xg_boost: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        home: typing.Optional["Workspace"] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        install_git_hub_cli: typing.Optional[builtins.bool] = None,
        managed_scaling_policy: typing.Optional[typing.Union["ManagedScalingPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        release_label: typing.Optional["ReleaseLabel"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        scale_down_behavior: typing.Optional["ScaleDownBehavior"] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        steps: typing.Optional[typing.Sequence[typing.Union["Step", typing.Dict[builtins.str, typing.Any]]]] = None,
        core_instance_fleet: typing.Optional[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]] = None,
        core_instance_group: typing.Optional[typing.Union["InstanceGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_instance_fleet: typing.Optional[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_instance_group: typing.Optional[typing.Union["PrimaryInstanceGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        task_instance_fleets: typing.Optional[typing.Sequence[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]]] = None,
        task_instance_groups: typing.Optional[typing.Sequence[typing.Union["InstanceGroup", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param catalogs: (experimental) The catalogs to use for the EMR cluster.
        :param cluster_name: (experimental) Name of the EMR Cluster.
        :param vpc: (experimental) The VPC to deploy the EMR cluster into.
        :param additional_privileged_registries: (experimental) Additional registries to allow privileged containers from. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param additional_trusted_registries: (experimental) Additional registries to trust for Docker containers. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param bootstrap_actions: Default: - No bootstrap actions
        :param configurations: (experimental) Override EMR Configurations. Default: - the {@link catalog }'s configurations + .venv for the user code.
        :param enable_docker: (experimental) Enable Docker support on the cluster. Default: true
        :param enable_spark_rapids: (experimental) Enable the Spark Rapids plugin. Default: false
        :param enable_ssm_agent: (experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes. Default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``
        :param enable_xg_boost: (experimental) Enable the XGBoost spark library. Default: false
        :param environment: (experimental) Environment variables to make available to the EMR cluster. Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there. Default: - no environment variables
        :param extra_java_options: (experimental) Extra java options to include in the Spark context by default.
        :param home: (experimental) Mount a shared filesystem to the EMR cluster.
        :param idle_timeout: Default: None
        :param install_git_hub_cli: (experimental) Install the GitHub CLI on the EMR cluster. Default: false
        :param managed_scaling_policy: Default: - No managed scaling policy
        :param release_label: Default: - {@link ReleaseLabel.LATEST }
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param scale_down_behavior: Default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }
        :param step_concurrency_level: (experimental) The concurrency level of the cluster. Default: 1
        :param steps: (experimental) The EMR Steps to submit to the cluster.
        :param core_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the core {@link InstanceFleet} when using {@link FleetCluster}s.
        :param core_instance_group: (experimental) Describes the EC2 instances and instance configurations for core {@link InstanceGroup}s when using {@link UniformCluster}s.
        :param primary_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the master {@link InstanceFleet} when using {@link FleetCluster}s.
        :param primary_instance_group: (experimental) Describes the EC2 instances and instance configurations for the master {@link InstanceGroup} when using {@link UniformCluster}s.
        :param task_instance_fleets: (experimental) Describes the EC2 instances and instance configurations for the task {@link InstanceFleet}s when using {@link FleetCluster}s. These task {@link InstanceFleet}s are added to the cluster as part of the cluster launch. Each task {@link InstanceFleet} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceFleet}s. .. epigraph:: You can currently specify only one task instance fleet for a cluster. After creating the cluster, you can only modify the mutable properties of ``InstanceFleetConfig`` , which are ``TargetOnDemandCapacity`` and ``TargetSpotCapacity`` . Modifying any other property results in cluster replacement. > To allow a maximum of 30 Amazon EC2 instance types per fleet, include ``TaskInstanceFleets`` when you create your cluster. If you create your cluster without ``TaskInstanceFleets`` , Amazon EMR uses its default allocation strategy, which allows for a maximum of five Amazon EC2 instance types.
        :param task_instance_groups: (experimental) Describes the EC2 instances and instance configurations for task {@link InstanceGroup}s when using {@link UniformCluster}s. These task {@link InstanceGroup}s are added to the cluster as part of the cluster launch. Each task {@link InstanceGroup} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceGroup}s. .. epigraph:: After creating the cluster, you can only modify the mutable properties of ``InstanceGroupConfig`` , which are ``AutoScalingPolicy`` and ``InstanceCount`` . Modifying any other property results in cluster replacement.

        :stability: experimental
        '''
        if isinstance(managed_scaling_policy, dict):
            managed_scaling_policy = ManagedScalingPolicy(**managed_scaling_policy)
        if isinstance(core_instance_fleet, dict):
            core_instance_fleet = InstanceFleet(**core_instance_fleet)
        if isinstance(core_instance_group, dict):
            core_instance_group = InstanceGroup(**core_instance_group)
        if isinstance(primary_instance_fleet, dict):
            primary_instance_fleet = InstanceFleet(**primary_instance_fleet)
        if isinstance(primary_instance_group, dict):
            primary_instance_group = PrimaryInstanceGroup(**primary_instance_group)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d1e25f38a23ff0e943bb86ed7b3aa4ba92982ab80e75489897d731cb1747ab2)
            check_type(argname="argument catalogs", value=catalogs, expected_type=type_hints["catalogs"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument additional_privileged_registries", value=additional_privileged_registries, expected_type=type_hints["additional_privileged_registries"])
            check_type(argname="argument additional_trusted_registries", value=additional_trusted_registries, expected_type=type_hints["additional_trusted_registries"])
            check_type(argname="argument bootstrap_actions", value=bootstrap_actions, expected_type=type_hints["bootstrap_actions"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
            check_type(argname="argument enable_docker", value=enable_docker, expected_type=type_hints["enable_docker"])
            check_type(argname="argument enable_spark_rapids", value=enable_spark_rapids, expected_type=type_hints["enable_spark_rapids"])
            check_type(argname="argument enable_ssm_agent", value=enable_ssm_agent, expected_type=type_hints["enable_ssm_agent"])
            check_type(argname="argument enable_xg_boost", value=enable_xg_boost, expected_type=type_hints["enable_xg_boost"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument extra_java_options", value=extra_java_options, expected_type=type_hints["extra_java_options"])
            check_type(argname="argument home", value=home, expected_type=type_hints["home"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument install_git_hub_cli", value=install_git_hub_cli, expected_type=type_hints["install_git_hub_cli"])
            check_type(argname="argument managed_scaling_policy", value=managed_scaling_policy, expected_type=type_hints["managed_scaling_policy"])
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument scale_down_behavior", value=scale_down_behavior, expected_type=type_hints["scale_down_behavior"])
            check_type(argname="argument step_concurrency_level", value=step_concurrency_level, expected_type=type_hints["step_concurrency_level"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
            check_type(argname="argument core_instance_fleet", value=core_instance_fleet, expected_type=type_hints["core_instance_fleet"])
            check_type(argname="argument core_instance_group", value=core_instance_group, expected_type=type_hints["core_instance_group"])
            check_type(argname="argument primary_instance_fleet", value=primary_instance_fleet, expected_type=type_hints["primary_instance_fleet"])
            check_type(argname="argument primary_instance_group", value=primary_instance_group, expected_type=type_hints["primary_instance_group"])
            check_type(argname="argument task_instance_fleets", value=task_instance_fleets, expected_type=type_hints["task_instance_fleets"])
            check_type(argname="argument task_instance_groups", value=task_instance_groups, expected_type=type_hints["task_instance_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "catalogs": catalogs,
            "cluster_name": cluster_name,
            "vpc": vpc,
        }
        if additional_privileged_registries is not None:
            self._values["additional_privileged_registries"] = additional_privileged_registries
        if additional_trusted_registries is not None:
            self._values["additional_trusted_registries"] = additional_trusted_registries
        if bootstrap_actions is not None:
            self._values["bootstrap_actions"] = bootstrap_actions
        if configurations is not None:
            self._values["configurations"] = configurations
        if enable_docker is not None:
            self._values["enable_docker"] = enable_docker
        if enable_spark_rapids is not None:
            self._values["enable_spark_rapids"] = enable_spark_rapids
        if enable_ssm_agent is not None:
            self._values["enable_ssm_agent"] = enable_ssm_agent
        if enable_xg_boost is not None:
            self._values["enable_xg_boost"] = enable_xg_boost
        if environment is not None:
            self._values["environment"] = environment
        if extra_java_options is not None:
            self._values["extra_java_options"] = extra_java_options
        if home is not None:
            self._values["home"] = home
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if install_git_hub_cli is not None:
            self._values["install_git_hub_cli"] = install_git_hub_cli
        if managed_scaling_policy is not None:
            self._values["managed_scaling_policy"] = managed_scaling_policy
        if release_label is not None:
            self._values["release_label"] = release_label
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if scale_down_behavior is not None:
            self._values["scale_down_behavior"] = scale_down_behavior
        if step_concurrency_level is not None:
            self._values["step_concurrency_level"] = step_concurrency_level
        if steps is not None:
            self._values["steps"] = steps
        if core_instance_fleet is not None:
            self._values["core_instance_fleet"] = core_instance_fleet
        if core_instance_group is not None:
            self._values["core_instance_group"] = core_instance_group
        if primary_instance_fleet is not None:
            self._values["primary_instance_fleet"] = primary_instance_fleet
        if primary_instance_group is not None:
            self._values["primary_instance_group"] = primary_instance_group
        if task_instance_fleets is not None:
            self._values["task_instance_fleets"] = task_instance_fleets
        if task_instance_groups is not None:
            self._values["task_instance_groups"] = task_instance_groups

    @builtins.property
    def catalogs(self) -> typing.Mapping[builtins.str, "ICatalog"]:
        '''(experimental) The catalogs to use for the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("catalogs")
        assert result is not None, "Required property 'catalogs' is missing"
        return typing.cast(typing.Mapping[builtins.str, "ICatalog"], result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''(experimental) Name of the EMR Cluster.

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to deploy the EMR cluster into.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def additional_privileged_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to allow privileged containers from.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_privileged_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_trusted_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to trust for Docker containers.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_trusted_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bootstrap_actions(self) -> typing.Optional[typing.List[BootstrapAction]]:
        '''
        :default: - No bootstrap actions

        :stability: experimental
        '''
        result = self._values.get("bootstrap_actions")
        return typing.cast(typing.Optional[typing.List[BootstrapAction]], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List["Configuration"]]:
        '''(experimental) Override EMR Configurations.

        :default: - the {@link catalog }'s configurations + .venv for the user code.

        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List["Configuration"]], result)

    @builtins.property
    def enable_docker(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Docker support on the cluster.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enable_docker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_spark_rapids(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the Spark Rapids plugin.

        :default: false

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-rapids.html
        :stability: experimental
        '''
        result = self._values.get("enable_spark_rapids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ssm_agent(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes.

        :default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``

        :stability: experimental
        '''
        result = self._values.get("enable_ssm_agent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_xg_boost(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the XGBoost spark library.

        :default: false

        :see: https://docs.nvidia.com/spark-rapids/user-guide/latest/getting-started/aws-emr.html
        :stability: experimental
        '''
        result = self._values.get("enable_xg_boost")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables to make available to the EMR cluster.

        Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there.

        :default: - no environment variables

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def extra_java_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Extra java options to include in the Spark context by default.

        :stability: experimental
        '''
        result = self._values.get("extra_java_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def home(self) -> typing.Optional["Workspace"]:
        '''(experimental) Mount a shared filesystem to the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("home")
        return typing.cast(typing.Optional["Workspace"], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''
        :default: None

        :stability: experimental
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def install_git_hub_cli(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install the GitHub CLI on the EMR cluster.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("install_git_hub_cli")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_scaling_policy(self) -> typing.Optional["ManagedScalingPolicy"]:
        '''
        :default: - No managed scaling policy

        :stability: experimental
        '''
        result = self._values.get("managed_scaling_policy")
        return typing.cast(typing.Optional["ManagedScalingPolicy"], result)

    @builtins.property
    def release_label(self) -> typing.Optional["ReleaseLabel"]:
        '''
        :default: - {@link ReleaseLabel.LATEST }

        :stability: experimental
        '''
        result = self._values.get("release_label")
        return typing.cast(typing.Optional["ReleaseLabel"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :default: {@link RemovalPolicy.DESTROY }

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def scale_down_behavior(self) -> typing.Optional["ScaleDownBehavior"]:
        '''
        :default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }

        :stability: experimental
        '''
        result = self._values.get("scale_down_behavior")
        return typing.cast(typing.Optional["ScaleDownBehavior"], result)

    @builtins.property
    def step_concurrency_level(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The concurrency level of the cluster.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("step_concurrency_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def steps(self) -> typing.Optional[typing.List["Step"]]:
        '''(experimental) The EMR Steps to submit to the cluster.

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-submit-step.html
        :stability: experimental
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.List["Step"]], result)

    @builtins.property
    def core_instance_fleet(self) -> typing.Optional["InstanceFleet"]:
        '''(experimental) Describes the EC2 instances and instance configurations for the core {@link InstanceFleet} when using {@link FleetCluster}s.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-coreinstancefleet
        :stability: experimental
        '''
        result = self._values.get("core_instance_fleet")
        return typing.cast(typing.Optional["InstanceFleet"], result)

    @builtins.property
    def core_instance_group(self) -> typing.Optional["InstanceGroup"]:
        '''(experimental) Describes the EC2 instances and instance configurations for core {@link InstanceGroup}s when using {@link UniformCluster}s.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-coreinstancegroup
        :stability: experimental
        '''
        result = self._values.get("core_instance_group")
        return typing.cast(typing.Optional["InstanceGroup"], result)

    @builtins.property
    def primary_instance_fleet(self) -> typing.Optional["InstanceFleet"]:
        '''(experimental) Describes the EC2 instances and instance configurations for the master {@link InstanceFleet} when using {@link FleetCluster}s.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-masterinstancefleet
        :stability: experimental
        '''
        result = self._values.get("primary_instance_fleet")
        return typing.cast(typing.Optional["InstanceFleet"], result)

    @builtins.property
    def primary_instance_group(self) -> typing.Optional["PrimaryInstanceGroup"]:
        '''(experimental) Describes the EC2 instances and instance configurations for the master {@link InstanceGroup} when using {@link UniformCluster}s.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-masterinstancegroup
        :stability: experimental
        '''
        result = self._values.get("primary_instance_group")
        return typing.cast(typing.Optional["PrimaryInstanceGroup"], result)

    @builtins.property
    def task_instance_fleets(self) -> typing.Optional[typing.List["InstanceFleet"]]:
        '''(experimental) Describes the EC2 instances and instance configurations for the task {@link InstanceFleet}s when using {@link FleetCluster}s.

        These task {@link InstanceFleet}s are added to the cluster as part of the cluster launch.
        Each task {@link InstanceFleet} must have a unique name specified so that CloudFormation
        can differentiate between the task {@link InstanceFleet}s.
        .. epigraph::

           You can currently specify only one task instance fleet for a cluster. After creating the cluster, you can only modify the mutable properties of ``InstanceFleetConfig`` , which are ``TargetOnDemandCapacity`` and ``TargetSpotCapacity`` . Modifying any other property results in cluster replacement. > To allow a maximum of 30 Amazon EC2 instance types per fleet, include ``TaskInstanceFleets`` when you create your cluster. If you create your cluster without ``TaskInstanceFleets`` , Amazon EMR uses its default allocation strategy, which allows for a maximum of five Amazon EC2 instance types.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-taskinstancefleets
        :stability: experimental
        '''
        result = self._values.get("task_instance_fleets")
        return typing.cast(typing.Optional[typing.List["InstanceFleet"]], result)

    @builtins.property
    def task_instance_groups(self) -> typing.Optional[typing.List["InstanceGroup"]]:
        '''(experimental) Describes the EC2 instances and instance configurations for task {@link InstanceGroup}s when using {@link UniformCluster}s.

        These task {@link InstanceGroup}s are added to the cluster as part of the cluster launch.
        Each task {@link InstanceGroup} must have a unique name specified so that CloudFormation
        can differentiate between the task {@link InstanceGroup}s.
        .. epigraph::

           After creating the cluster, you can only modify the mutable properties of ``InstanceGroupConfig`` , which are ``AutoScalingPolicy`` and ``InstanceCount`` . Modifying any other property results in cluster replacement.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-taskinstancegroups
        :stability: experimental
        '''
        result = self._values.get("task_instance_groups")
        return typing.cast(typing.Optional[typing.List["InstanceGroup"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.ComputeLimits",
    jsii_struct_bases=[],
    name_mapping={
        "maximum_capacity_units": "maximumCapacityUnits",
        "minimum_capacity_units": "minimumCapacityUnits",
        "unit_type": "unitType",
        "maximum_core_capacity_units": "maximumCoreCapacityUnits",
        "maximum_on_demand_capacity_units": "maximumOnDemandCapacityUnits",
    },
)
class ComputeLimits:
    def __init__(
        self,
        *,
        maximum_capacity_units: jsii.Number,
        minimum_capacity_units: jsii.Number,
        unit_type: "ComputeUnit",
        maximum_core_capacity_units: typing.Optional[jsii.Number] = None,
        maximum_on_demand_capacity_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param maximum_capacity_units: (experimental) The upper boundary of Amazon EC2 units. It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. Managed scaling activities are not allowed beyond this boundary. The limit only applies to the core and task nodes. The master node cannot be scaled after initial configuration.
        :param minimum_capacity_units: (experimental) The lower boundary of Amazon EC2 units. It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. Managed scaling activities are not allowed beyond this boundary. The limit only applies to the core and task nodes. The master node cannot be scaled after initial configuration.
        :param unit_type: (experimental) The unit type used for specifying a managed scaling policy.
        :param maximum_core_capacity_units: (experimental) The upper boundary of Amazon EC2 units for core node type in a cluster. It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. The core units are not allowed to scale beyond this boundary. The parameter is used to split capacity allocation between core and task nodes.
        :param maximum_on_demand_capacity_units: (experimental) The upper boundary of On-Demand Amazon EC2 units. It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. The On-Demand units are not allowed to scale beyond this boundary. The parameter is used to split capacity allocation between On-Demand and Spot Instances.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3faadce00754b829619a7e305620ab7fc2d60cc3b5402c905c8eb3ee16b5f397)
            check_type(argname="argument maximum_capacity_units", value=maximum_capacity_units, expected_type=type_hints["maximum_capacity_units"])
            check_type(argname="argument minimum_capacity_units", value=minimum_capacity_units, expected_type=type_hints["minimum_capacity_units"])
            check_type(argname="argument unit_type", value=unit_type, expected_type=type_hints["unit_type"])
            check_type(argname="argument maximum_core_capacity_units", value=maximum_core_capacity_units, expected_type=type_hints["maximum_core_capacity_units"])
            check_type(argname="argument maximum_on_demand_capacity_units", value=maximum_on_demand_capacity_units, expected_type=type_hints["maximum_on_demand_capacity_units"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "maximum_capacity_units": maximum_capacity_units,
            "minimum_capacity_units": minimum_capacity_units,
            "unit_type": unit_type,
        }
        if maximum_core_capacity_units is not None:
            self._values["maximum_core_capacity_units"] = maximum_core_capacity_units
        if maximum_on_demand_capacity_units is not None:
            self._values["maximum_on_demand_capacity_units"] = maximum_on_demand_capacity_units

    @builtins.property
    def maximum_capacity_units(self) -> jsii.Number:
        '''(experimental) The upper boundary of Amazon EC2 units.

        It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. Managed scaling activities are not allowed beyond this boundary. The limit only applies to the core and task nodes. The master node cannot be scaled after initial configuration.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-computelimits.html#cfn-emr-cluster-computelimits-maximumcapacityunits
        :stability: experimental
        '''
        result = self._values.get("maximum_capacity_units")
        assert result is not None, "Required property 'maximum_capacity_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def minimum_capacity_units(self) -> jsii.Number:
        '''(experimental) The lower boundary of Amazon EC2 units.

        It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. Managed scaling activities are not allowed beyond this boundary. The limit only applies to the core and task nodes. The master node cannot be scaled after initial configuration.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-computelimits.html#cfn-emr-cluster-computelimits-minimumcapacityunits
        :stability: experimental
        '''
        result = self._values.get("minimum_capacity_units")
        assert result is not None, "Required property 'minimum_capacity_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit_type(self) -> "ComputeUnit":
        '''(experimental) The unit type used for specifying a managed scaling policy.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-computelimits.html#cfn-emr-cluster-computelimits-unittype
        :stability: experimental
        '''
        result = self._values.get("unit_type")
        assert result is not None, "Required property 'unit_type' is missing"
        return typing.cast("ComputeUnit", result)

    @builtins.property
    def maximum_core_capacity_units(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The upper boundary of Amazon EC2 units for core node type in a cluster.

        It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. The core units are not allowed to scale beyond this boundary. The parameter is used to split capacity allocation between core and task nodes.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-computelimits.html#cfn-emr-cluster-computelimits-maximumcorecapacityunits
        :stability: experimental
        '''
        result = self._values.get("maximum_core_capacity_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum_on_demand_capacity_units(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The upper boundary of On-Demand Amazon EC2 units.

        It is measured through vCPU cores or instances for instance groups and measured through units for instance fleets. The On-Demand units are not allowed to scale beyond this boundary. The parameter is used to split capacity allocation between On-Demand and Spot Instances.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-computelimits.html#cfn-emr-cluster-computelimits-maximumondemandcapacityunits
        :stability: experimental
        '''
        result = self._values.get("maximum_on_demand_capacity_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@packyak/aws-cdk.ComputeUnit")
class ComputeUnit(enum.Enum):
    '''
    :stability: experimental
    '''

    INSTANCES = "INSTANCES"
    '''
    :stability: experimental
    '''
    INSTANCE_FLEET_UNITS = "INSTANCE_FLEET_UNITS"
    '''
    :stability: experimental
    '''
    VCPU = "VCPU"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.Configuration",
    jsii_struct_bases=[],
    name_mapping={
        "classification": "classification",
        "configuration_properties": "configurationProperties",
        "configurations": "configurations",
    },
)
class Configuration:
    def __init__(
        self,
        *,
        classification: builtins.str,
        configuration_properties: typing.Mapping[builtins.str, builtins.str],
        configurations: typing.Optional[typing.Sequence[typing.Union["Configuration", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param classification: 
        :param configuration_properties: 
        :param configurations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9faeef4120b59640960ae462acb70087060336971435d887fda52f15396d8441)
            check_type(argname="argument classification", value=classification, expected_type=type_hints["classification"])
            check_type(argname="argument configuration_properties", value=configuration_properties, expected_type=type_hints["configuration_properties"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "classification": classification,
            "configuration_properties": configuration_properties,
        }
        if configurations is not None:
            self._values["configurations"] = configurations

    @builtins.property
    def classification(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("classification")
        assert result is not None, "Required property 'classification' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configuration_properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("configuration_properties")
        assert result is not None, "Required property 'configuration_properties' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List["Configuration"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List["Configuration"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.DNSConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "domain_name": "domainName",
        "hosted_zone": "hostedZone",
    },
)
class DNSConfiguration:
    def __init__(
        self,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        domain_name: builtins.str,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    ) -> None:
        '''
        :param certificate: 
        :param domain_name: 
        :param hosted_zone: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81b9b42796b2032f822078ff7b8bd89a58e3e49dcd51db45579d47e54a39eeee)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
            "domain_name": domain_name,
            "hosted_zone": hosted_zone,
        }

    @builtins.property
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''
        :stability: experimental
        '''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''
        :stability: experimental
        '''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DNSConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.DagsterDatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_identifier": "clusterIdentifier",
        "credentials": "credentials",
        "port": "port",
        "readers": "readers",
        "writer": "writer",
    },
)
class DagsterDatabaseProps:
    def __init__(
        self,
        *,
        cluster_identifier: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
        port: typing.Optional[jsii.Number] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    ) -> None:
        '''
        :param cluster_identifier: (experimental) An optional identifier for the cluster. Default: - A name is automatically generated.
        :param credentials: (experimental) Credentials for the administrative user. Default: - A username of 'admin' and SecretsManager-generated password
        :param port: (experimental) The port to connect to the database on. Default: - 5432
        :param readers: (experimental) The readers instances to use for the database. Default: - No readers are created.
        :param writer: (experimental) The writer instance to use for the database. Default: - A serverless instance is created.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98fe0909f89f176d0141b4b3345c67021ea1a24e405067b84665729e4dc9d842)
            check_type(argname="argument cluster_identifier", value=cluster_identifier, expected_type=type_hints["cluster_identifier"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument readers", value=readers, expected_type=type_hints["readers"])
            check_type(argname="argument writer", value=writer, expected_type=type_hints["writer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if credentials is not None:
            self._values["credentials"] = credentials
        if port is not None:
            self._values["port"] = port
        if readers is not None:
            self._values["readers"] = readers
        if writer is not None:
            self._values["writer"] = writer

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional identifier for the cluster.

        :default: - A name is automatically generated.

        :stability: experimental
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials]:
        '''(experimental) Credentials for the administrative user.

        :default: - A username of 'admin' and SecretsManager-generated password

        :stability: experimental
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port to connect to the database on.

        :default: - 5432

        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def readers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]]:
        '''(experimental) The readers instances to use for the database.

        :default: - No readers are created.

        :stability: experimental
        '''
        result = self._values.get("readers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]], result)

    @builtins.property
    def writer(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]:
        '''(experimental) The writer instance to use for the database.

        :default: - A serverless instance is created.

        :stability: experimental
        '''
        result = self._values.get("writer")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DagsterDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DagsterService(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.DagsterService",
):
    '''(experimental) Represents a Dagster service deployment in AWS, encapsulating the necessary AWS resources.

    This class allows for the easy setup of a Dagster service with a connected Aurora Postgres database
    within an ECS cluster. It abstracts away the complexity of directly dealing with AWS CDK constructs
    for creating and configuring the ECS service, database, and necessary permissions.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Cluster] = None,
        database: typing.Optional[typing.Union[DagsterDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The ECS cluster to deploy the service to. You must specify either {@link vpc} or {@link cluster}.
        :param database: (experimental) The database to deploy to.
        :param removal_policy: (experimental) The removal policy to use for the database and service. Default: - The database is not removed automatically.
        :param vpc: (experimental) The VPC to deploy the service to. You must specify either {@link vpc} or {@link cluster}.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4b0eb15936f6f6cf218041d3b956080f80797638288b505c722dac10d425c8c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DagsterServiceProps(
            cluster=cluster, database=database, removal_policy=removal_policy, vpc=vpc
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allowDBAccessFrom")
    def allow_db_access_from(
        self,
        connectable: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    ) -> None:
        '''(experimental) Allow a connectable to access the database.

        :param connectable: The connectable to allow access from.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5fe68778add2bd477819d11ac1d3d7fde3e6a002284cb787b2cefc33b68da6a)
            check_type(argname="argument connectable", value=connectable, expected_type=type_hints["connectable"])
        return typing.cast(None, jsii.invoke(self, "allowDBAccessFrom", [connectable]))

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> _aws_cdk_aws_rds_ceddda9d.DatabaseCluster:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.DatabaseCluster, jsii.get(self, "database"))

    @builtins.property
    @jsii.member(jsii_name="databaseSecret")
    def database_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "databaseSecret"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.DagsterServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "database": "database",
        "removal_policy": "removalPolicy",
        "vpc": "vpc",
    },
)
class DagsterServiceProps:
    def __init__(
        self,
        *,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Cluster] = None,
        database: typing.Optional[typing.Union[DagsterDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param cluster: (experimental) The ECS cluster to deploy the service to. You must specify either {@link vpc} or {@link cluster}.
        :param database: (experimental) The database to deploy to.
        :param removal_policy: (experimental) The removal policy to use for the database and service. Default: - The database is not removed automatically.
        :param vpc: (experimental) The VPC to deploy the service to. You must specify either {@link vpc} or {@link cluster}.

        :stability: experimental
        '''
        if isinstance(database, dict):
            database = DagsterDatabaseProps(**database)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__441a2f78284f95b372c2942261709062f139a99540404ac4eca640163ce5c780)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cluster is not None:
            self._values["cluster"] = cluster
        if database is not None:
            self._values["database"] = database
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Cluster]:
        '''(experimental) The ECS cluster to deploy the service to.

        You must specify either {@link vpc} or {@link cluster}.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Cluster], result)

    @builtins.property
    def database(self) -> typing.Optional[DagsterDatabaseProps]:
        '''(experimental) The database to deploy to.

        :stability: experimental
        '''
        result = self._values.get("database")
        return typing.cast(typing.Optional[DagsterDatabaseProps], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to use for the database and service.

        :default: - The database is not removed automatically.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC to deploy the service to.

        You must specify either {@link vpc} or {@link cluster}.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DagsterServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.DefaultUserSettings",
    jsii_struct_bases=[],
    name_mapping={
        "execution_role": "executionRole",
        "studio_web_portal": "studioWebPortal",
    },
)
class DefaultUserSettings:
    def __init__(
        self,
        *,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        studio_web_portal: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param execution_role: (experimental) The execution role for the user.
        :param studio_web_portal: (experimental) Whether users can access the Studio by default. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0873f2525085ef388fe5b1c7f480099a454fa6950f1cb093fb40de3662d2d4e)
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument studio_web_portal", value=studio_web_portal, expected_type=type_hints["studio_web_portal"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if studio_web_portal is not None:
            self._values["studio_web_portal"] = studio_web_portal

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The execution role for the user.

        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def studio_web_portal(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether users can access the Studio by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("studio_web_portal")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefaultUserSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IConnectable, _aws_cdk_aws_iam_ceddda9d.IGrantable)
class Domain(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.Domain",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        app_network_access_type: typing.Optional[AppNetworkAccessType] = None,
        auth_mode: typing.Optional[AuthMode] = None,
        default_image: typing.Optional["SageMakerImage"] = None,
        default_user_settings: typing.Optional[typing.Union[DefaultUserSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        sage_maker_sg: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: (experimental) The name of the domain to create.
        :param vpc: (experimental) The VPC where the Domain (and its resources) will be deployed to.
        :param app_network_access_type: (experimental) Specifies the VPC used for non-EFS traffic. Default: AppNetworkAccessType.VpcOnly
        :param auth_mode: (experimental) The authentication mode for the domain. Default: AuthMode.SSO
        :param default_image: (experimental) The default image for user profiles in the domain. Default: {@link SageMakerImage.CPU_V1 }
        :param default_user_settings: (experimental) The default settings for user profiles in the domain.
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param sage_maker_sg: (experimental) The security group for SageMaker to use.
        :param subnet_selection: (experimental) The subnets to deploy the Domain to. Default: SubnetSelection.PrimaryContainer

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b39317c6769151217f56205904c51cd118463003e1c82a917782ef88011fed14)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DomainProps(
            domain_name=domain_name,
            vpc=vpc,
            app_network_access_type=app_network_access_type,
            auth_mode=auth_mode,
            default_image=default_image,
            default_user_settings=default_user_settings,
            removal_policy=removal_policy,
            sage_maker_sg=sage_maker_sg,
            subnet_selection=subnet_selection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addUserProfile")
    def add_user_profile(
        self,
        username: builtins.str,
        *,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> "UserProfile":
        '''
        :param username: -
        :param execution_role: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e405c8f3997826f91b7f4298f025d4e5bb50f7fd62a432b81be85cb84bf6bf09)
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        props = AddUserProfileProps(execution_role=execution_role)

        return typing.cast("UserProfile", jsii.invoke(self, "addUserProfile", [username, props]))

    @jsii.member(jsii_name="enableCleanup")
    def enable_cleanup(self, removal_policy: _aws_cdk_ceddda9d.RemovalPolicy) -> None:
        '''(experimental) Creates a CustomResource that will clean up the domain prior to it being destroyed: 1.

        Delete any running Apps (i.e. instances of a Space)
        2. Delete the Domain's spaces.
        2. Delete the Domain's EFS file system (first, by deleting any mounted access points, then the FS).

        :param removal_policy: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a3d16fced81f471914f455d31101b08c9111eabf0413986dcb2bf5bc93f4a46)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        return typing.cast(None, jsii.invoke(self, "enableCleanup", [removal_policy]))

    @jsii.member(jsii_name="grantCreateApp")
    def grant_create_app(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a329618998e617d0011f9fc5cbc37ddfb4a1d734188d7a0530611804deec9cd8)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantCreateApp", [grantee]))

    @jsii.member(jsii_name="grantCreatePresignedDomainUrl")
    def grant_create_presigned_domain_url(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22a5adfc31d5acdf532137425862afa23f6c4de17c0ef170cf937e8bd5406d99)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantCreatePresignedDomainUrl", [grantee]))

    @jsii.member(jsii_name="grantCreateSpace")
    def grant_create_space(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28944ea6eb4d6bf5fbaf9efdc289e0339e6114d345826ec21a090d7752b82f11)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantCreateSpace", [grantee]))

    @jsii.member(jsii_name="grantDeleteApp")
    def grant_delete_app(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0746c9ef321d8e5e9c13f51fbb97143347eeb003e0dbb277e9312d08b920945a)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDeleteApp", [grantee]))

    @jsii.member(jsii_name="grantDeleteSpace")
    def grant_delete_space(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eac904d1e1a43e8ac5faba9775659dc9fa04e093790d62619b9d9d9aaf3fc10)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDeleteSpace", [grantee]))

    @jsii.member(jsii_name="grantDescribeApp")
    def grant_describe_app(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea691bc547ce6aa2168f2661375ba18ac984f4f4debbaa2f54f9a75b07d0fa62)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDescribeApp", [grantee]))

    @jsii.member(jsii_name="grantDescribeDomain")
    def grant_describe_domain(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ccf37c0fd390833cefc7819e95388c6e738d283a7812d5734b51e6bb389a4cf)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDescribeDomain", [grantee]))

    @jsii.member(jsii_name="grantDescribeSpace")
    def grant_describe_space(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fda286e86ee044e41b0a9adea0091e74c6d5839aa1c07ba4866056b8b7a90318)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDescribeSpace", [grantee]))

    @jsii.member(jsii_name="grantDescribeUserProfile")
    def grant_describe_user_profile(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3659dc8ef782a84d25438d733254b5d663850a083c78f465c98ab1ea4b906574)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantDescribeUserProfile", [grantee]))

    @jsii.member(jsii_name="grantEMRClusterAccess")
    def grant_emr_cluster_access(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''(experimental) Grants access to list and describe clusters in the JupyterNotebook.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__548ad34790588b478390e8e012a53fa696f0dbb3f8742341e2c8cce4c7608c71)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantEMRClusterAccess", [grantee]))

    @jsii.member(jsii_name="grantGlueInteractiveSession")
    def grant_glue_interactive_session(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ab2dd3a7a4ddf1a651e030aaf22f6caed7004b94b4cfd0b3326b424033cb1e7)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantGlueInteractiveSession", [grantee]))

    @jsii.member(jsii_name="grantListApps")
    def grant_list_apps(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d11c67e524851f75bc2242aea8e3f3b81bab190fd7383194f07fd11f7ab54041)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantListApps", [grantee]))

    @jsii.member(jsii_name="grantListSessions")
    def grant_list_sessions(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__839adbef507a2164f2932b6c92d67abc8c3eefa1943959ea40db5ad3d459df55)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantListSessions", [grantee]))

    @jsii.member(jsii_name="grantListSpaces")
    def grant_list_spaces(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fa6904f7781e447da5f82f620f04151c7cba6256ba3149edfbca791ae1477d9)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantListSpaces", [grantee]))

    @jsii.member(jsii_name="grantListTags")
    def grant_list_tags(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0672a62edb2af17901b06dcd1dad71d788e57f4bbed2706ec5eb67ac56e7ba5e)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantListTags", [grantee]))

    @jsii.member(jsii_name="grantSageMakerSearch")
    def grant_sage_maker_search(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__defd0b829457596f659bfadd8478ae76cc16a0a8e45c6c1091b03533a1ce031d)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantSageMakerSearch", [grantee]))

    @jsii.member(jsii_name="grantSearchServiceCatalogProducts")
    def grant_search_service_catalog_products(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9690f9bdf3023560fca8be548eee521c34ce68a771f5e7eba8c1027fc96a012d)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantSearchServiceCatalogProducts", [grantee]))

    @jsii.member(jsii_name="grantStudioAccess")
    def grant_studio_access(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfd71e1bd7996d9607def6160eb444a42c549562b2934d29762c328f146debe2)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantStudioAccess", [grantee]))

    @jsii.member(jsii_name="grantUpdateSpace")
    def grant_update_space(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37497f96410e127045d256634518d73e5f09782f33b9148bffc56b44e4699e9a)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantUpdateSpace", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="domainArn")
    def domain_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainArn"))

    @builtins.property
    @jsii.member(jsii_name="domainId")
    def domain_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainId"))

    @builtins.property
    @jsii.member(jsii_name="domainUrl")
    def domain_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainUrl"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="homeEfsFileSystemArn")
    def home_efs_file_system_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "homeEfsFileSystemArn"))

    @builtins.property
    @jsii.member(jsii_name="homeEfsFileSystemId")
    def home_efs_file_system_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "homeEfsFileSystemId"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def _resource(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnDomain:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnDomain, jsii.get(self, "resource"))

    @builtins.property
    @jsii.member(jsii_name="sageMakerSg")
    def sage_maker_sg(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "sageMakerSg"))

    @builtins.property
    @jsii.member(jsii_name="singleSignOnApplicationArn")
    def single_sign_on_application_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "singleSignOnApplicationArn"))

    @builtins.property
    @jsii.member(jsii_name="singleSignOnManagedApplicationInstanceId")
    def single_sign_on_managed_application_instance_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "singleSignOnManagedApplicationInstanceId"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.DomainProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "vpc": "vpc",
        "app_network_access_type": "appNetworkAccessType",
        "auth_mode": "authMode",
        "default_image": "defaultImage",
        "default_user_settings": "defaultUserSettings",
        "removal_policy": "removalPolicy",
        "sage_maker_sg": "sageMakerSg",
        "subnet_selection": "subnetSelection",
    },
)
class DomainProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        app_network_access_type: typing.Optional[AppNetworkAccessType] = None,
        auth_mode: typing.Optional[AuthMode] = None,
        default_image: typing.Optional["SageMakerImage"] = None,
        default_user_settings: typing.Optional[typing.Union[DefaultUserSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        sage_maker_sg: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param domain_name: (experimental) The name of the domain to create.
        :param vpc: (experimental) The VPC where the Domain (and its resources) will be deployed to.
        :param app_network_access_type: (experimental) Specifies the VPC used for non-EFS traffic. Default: AppNetworkAccessType.VpcOnly
        :param auth_mode: (experimental) The authentication mode for the domain. Default: AuthMode.SSO
        :param default_image: (experimental) The default image for user profiles in the domain. Default: {@link SageMakerImage.CPU_V1 }
        :param default_user_settings: (experimental) The default settings for user profiles in the domain.
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param sage_maker_sg: (experimental) The security group for SageMaker to use.
        :param subnet_selection: (experimental) The subnets to deploy the Domain to. Default: SubnetSelection.PrimaryContainer

        :stability: experimental
        '''
        if isinstance(default_user_settings, dict):
            default_user_settings = DefaultUserSettings(**default_user_settings)
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4ab655c7b1031ca9fc7ade8ae044ce6762df8c9a01da3c16f289342ef98bd8b)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument app_network_access_type", value=app_network_access_type, expected_type=type_hints["app_network_access_type"])
            check_type(argname="argument auth_mode", value=auth_mode, expected_type=type_hints["auth_mode"])
            check_type(argname="argument default_image", value=default_image, expected_type=type_hints["default_image"])
            check_type(argname="argument default_user_settings", value=default_user_settings, expected_type=type_hints["default_user_settings"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument sage_maker_sg", value=sage_maker_sg, expected_type=type_hints["sage_maker_sg"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
            "vpc": vpc,
        }
        if app_network_access_type is not None:
            self._values["app_network_access_type"] = app_network_access_type
        if auth_mode is not None:
            self._values["auth_mode"] = auth_mode
        if default_image is not None:
            self._values["default_image"] = default_image
        if default_user_settings is not None:
            self._values["default_user_settings"] = default_user_settings
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if sage_maker_sg is not None:
            self._values["sage_maker_sg"] = sage_maker_sg
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''(experimental) The name of the domain to create.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-domain.html#cfn-sagemaker-domain-domainname
        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC where the Domain (and its resources) will be deployed to.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def app_network_access_type(self) -> typing.Optional[AppNetworkAccessType]:
        '''(experimental) Specifies the VPC used for non-EFS traffic.

        :default: AppNetworkAccessType.VpcOnly

        :stability: experimental
        '''
        result = self._values.get("app_network_access_type")
        return typing.cast(typing.Optional[AppNetworkAccessType], result)

    @builtins.property
    def auth_mode(self) -> typing.Optional[AuthMode]:
        '''(experimental) The authentication mode for the domain.

        :default: AuthMode.SSO

        :stability: experimental
        '''
        result = self._values.get("auth_mode")
        return typing.cast(typing.Optional[AuthMode], result)

    @builtins.property
    def default_image(self) -> typing.Optional["SageMakerImage"]:
        '''(experimental) The default image for user profiles in the domain.

        :default: {@link SageMakerImage.CPU_V1 }

        :stability: experimental
        '''
        result = self._values.get("default_image")
        return typing.cast(typing.Optional["SageMakerImage"], result)

    @builtins.property
    def default_user_settings(self) -> typing.Optional[DefaultUserSettings]:
        '''(experimental) The default settings for user profiles in the domain.

        :stability: experimental
        '''
        result = self._values.get("default_user_settings")
        return typing.cast(typing.Optional[DefaultUserSettings], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :default: {@link RemovalPolicy.DESTROY }

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def sage_maker_sg(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]:
        '''(experimental) The security group for SageMaker to use.

        :stability: experimental
        '''
        result = self._values.get("sage_maker_sg")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) The subnets to deploy the Domain to.

        :default: SubnetSelection.PrimaryContainer

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamoDBNessieVersionStore(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.DynamoDBNessieVersionStore",
):
    '''
    :see: https://projectnessie.org/try/configuration/#dynamodb-version-store-settings
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param removal_policy: Default: - RemovalPolicy.DESTROY
        :param version_store_name: (experimental) Nessie has two tables, ``objs`` and ``refs``. Nessie supports configuring a "prefix" that will be used to determine the names of these tables. Default: - "nessie"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38444b6f6d1ec4add548f3ae004c63748ea34266d1bf2c2d69305eb47c80507c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NessieVersionStoreProps(
            removal_policy=removal_policy, version_store_name=version_store_name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantReadData")
    def grant_read_data(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b95a70a93f69ccc7a9b492766b86bc6c93f3c322975743e20b240c292f35ae8)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantReadData", [grantee]))

    @jsii.member(jsii_name="grantReadWriteData")
    def grant_read_write_data(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbe43b619325570536138d75d8328854ea580a8678df2dbd84c0e758b9cefd8c)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantReadWriteData", [grantee]))

    @jsii.member(jsii_name="grantWriteData")
    def grant_write_data(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c5149b787ca472bf31a4ab23acc710d8a2285accc319e0fb4c7721b7cf323f1)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantWriteData", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="objs")
    def objs(self) -> _aws_cdk_aws_dynamodb_ceddda9d.Table:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.Table, jsii.get(self, "objs"))

    @builtins.property
    @jsii.member(jsii_name="refs")
    def refs(self) -> _aws_cdk_aws_dynamodb_ceddda9d.Table:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.Table, jsii.get(self, "refs"))

    @builtins.property
    @jsii.member(jsii_name="tablePrefix")
    def table_prefix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "tablePrefix"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.EbsBlockDevice",
    jsii_struct_bases=[],
    name_mapping={
        "size_in_gb": "sizeInGb",
        "volume_type": "volumeType",
        "iops": "iops",
        "throughput": "throughput",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class EbsBlockDevice:
    def __init__(
        self,
        *,
        size_in_gb: jsii.Number,
        volume_type: _aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType,
        iops: typing.Optional[jsii.Number] = None,
        throughput: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size_in_gb: (experimental) The volume size, in gibibytes (GiB). This can be a number from 1 - 1024. If the volume type is EBS-optimized, the minimum value is 10.
        :param volume_type: (experimental) The volume type. Volume types supported are: - gp3 ({@link EbsDeviceVolumeType.GENERAL_PURPOSE_SSD_GP3}) - gp2 ({@link EbsDeviceVolumeType.GENERAL_PURPOSE_SSD}) - io1 ({@link EbsDeviceVolumeType.PROVISIONED_IOPS_SSD}) - st1 ({@link EbsDeviceVolumeType.THROUGHPUT_OPTIMIZED_HDD}) - sc1 ({@link EbsDeviceVolumeType.COLD_HDD}) - standard ({@link EbsDeviceVolumeType.STANDARD}) Default: standard
        :param iops: (experimental) The number of I/O operations per second (IOPS) that the volume supports.
        :param throughput: (experimental) The throughput, in mebibyte per second (MiB/s). This optional parameter can be a number from ``125`` - ``1000`` and is valid only for {@link EbsDeviceVolumeType.GENERAL_PURPOSE_SSD_GP3} volumes.
        :param volumes_per_instance: (experimental) The number of EBS volumes with a specific volume configuration to attach to each instance. Default: 1

        :see: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-storage.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1896aeef4fcde328bc873304caf61e83a6fa969eb9f8a59924b62aa9a7a936ee)
            check_type(argname="argument size_in_gb", value=size_in_gb, expected_type=type_hints["size_in_gb"])
            check_type(argname="argument volume_type", value=volume_type, expected_type=type_hints["volume_type"])
            check_type(argname="argument iops", value=iops, expected_type=type_hints["iops"])
            check_type(argname="argument throughput", value=throughput, expected_type=type_hints["throughput"])
            check_type(argname="argument volumes_per_instance", value=volumes_per_instance, expected_type=type_hints["volumes_per_instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "size_in_gb": size_in_gb,
            "volume_type": volume_type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if throughput is not None:
            self._values["throughput"] = throughput
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size_in_gb(self) -> jsii.Number:
        '''(experimental) The volume size, in gibibytes (GiB).

        This can be a number from 1 - 1024. If the volume type is EBS-optimized, the minimum value is 10.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-volumespecification.html#cfn-emr-cluster-volumespecification-sizeingb
        :stability: experimental
        '''
        result = self._values.get("size_in_gb")
        assert result is not None, "Required property 'size_in_gb' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def volume_type(self) -> _aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType:
        '''(experimental) The volume type.

        Volume types supported are:

        - gp3 ({@link EbsDeviceVolumeType.GENERAL_PURPOSE_SSD_GP3})
        - gp2 ({@link EbsDeviceVolumeType.GENERAL_PURPOSE_SSD})
        - io1 ({@link EbsDeviceVolumeType.PROVISIONED_IOPS_SSD})
        - st1 ({@link EbsDeviceVolumeType.THROUGHPUT_OPTIMIZED_HDD})
        - sc1 ({@link EbsDeviceVolumeType.COLD_HDD})
        - standard ({@link EbsDeviceVolumeType.STANDARD})

        :default: standard

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-volumespecification.html#cfn-emr-cluster-volumespecification-volumetype
        :stability: experimental
        '''
        result = self._values.get("volume_type")
        assert result is not None, "Required property 'volume_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of I/O operations per second (IOPS) that the volume supports.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-volumespecification.html#cfn-emr-cluster-volumespecification-iops
        :stability: experimental
        '''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def throughput(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The throughput, in mebibyte per second (MiB/s).

        This optional parameter can be a number from ``125`` - ``1000`` and is valid
        only for {@link EbsDeviceVolumeType.GENERAL_PURPOSE_SSD_GP3} volumes.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-volumespecification.html#cfn-emr-cluster-volumespecification-throughput
        :stability: experimental
        '''
        result = self._values.get("throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of EBS volumes with a specific volume configuration to attach to each instance.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EbsBlockDevice(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FleetCluster(
    Cluster,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.FleetCluster",
):
    '''(experimental) An EMR Cluster that is comprised of {@link InstanceFleet}s.

    :see: https://docs.aws.amazon.com/emr/latest/ManagementGuide/on-demand-capacity-reservations.html
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        core_instance_fleet: typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]],
        primary_instance_fleet: typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]],
        task_instance_fleets: typing.Optional[typing.Sequence[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]]] = None,
        catalogs: typing.Mapping[builtins.str, "ICatalog"],
        cluster_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_docker: typing.Optional[builtins.bool] = None,
        enable_spark_rapids: typing.Optional[builtins.bool] = None,
        enable_ssm_agent: typing.Optional[builtins.bool] = None,
        enable_xg_boost: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        home: typing.Optional["Workspace"] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        install_git_hub_cli: typing.Optional[builtins.bool] = None,
        managed_scaling_policy: typing.Optional[typing.Union["ManagedScalingPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        release_label: typing.Optional["ReleaseLabel"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        scale_down_behavior: typing.Optional["ScaleDownBehavior"] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        steps: typing.Optional[typing.Sequence[typing.Union["Step", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param core_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the core {@link InstanceFleet}.
        :param primary_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the primary {@link InstanceFleet} when using {@link FleetCluster}s.
        :param task_instance_fleets: (experimental) Describes the EC2 instances and instance configurations for the task {@link InstanceFleet}s. These task {@link InstanceFleet}s are added to the cluster as part of the cluster launch. Each task {@link InstanceFleet} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceFleet}s. .. epigraph:: You can currently specify only one task instance fleet for a cluster. After creating the cluster, you can only modify the mutable properties of ``InstanceFleetConfig`` , which are ``TargetOnDemandCapacity`` and ``TargetSpotCapacity`` . Modifying any other property results in cluster replacement. > To allow a maximum of 30 Amazon EC2 instance types per fleet, include ``TaskInstanceFleets`` when you create your cluster. If you create your cluster without ``TaskInstanceFleets`` , Amazon EMR uses its default allocation strategy, which allows for a maximum of five Amazon EC2 instance types.
        :param catalogs: (experimental) The catalogs to use for the EMR cluster.
        :param cluster_name: (experimental) Name of the EMR Cluster.
        :param vpc: (experimental) The VPC to deploy the EMR cluster into.
        :param additional_privileged_registries: (experimental) Additional registries to allow privileged containers from. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param additional_trusted_registries: (experimental) Additional registries to trust for Docker containers. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param bootstrap_actions: Default: - No bootstrap actions
        :param configurations: (experimental) Override EMR Configurations. Default: - the {@link catalog }'s configurations + .venv for the user code.
        :param enable_docker: (experimental) Enable Docker support on the cluster. Default: true
        :param enable_spark_rapids: (experimental) Enable the Spark Rapids plugin. Default: false
        :param enable_ssm_agent: (experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes. Default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``
        :param enable_xg_boost: (experimental) Enable the XGBoost spark library. Default: false
        :param environment: (experimental) Environment variables to make available to the EMR cluster. Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there. Default: - no environment variables
        :param extra_java_options: (experimental) Extra java options to include in the Spark context by default.
        :param home: (experimental) Mount a shared filesystem to the EMR cluster.
        :param idle_timeout: Default: None
        :param install_git_hub_cli: (experimental) Install the GitHub CLI on the EMR cluster. Default: false
        :param managed_scaling_policy: Default: - No managed scaling policy
        :param release_label: Default: - {@link ReleaseLabel.LATEST }
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param scale_down_behavior: Default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }
        :param step_concurrency_level: (experimental) The concurrency level of the cluster. Default: 1
        :param steps: (experimental) The EMR Steps to submit to the cluster.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fe26ebd4797e22c94256285ebde7f20739db1573a73fd948758ad3ae94295fa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FleetClusterProps(
            core_instance_fleet=core_instance_fleet,
            primary_instance_fleet=primary_instance_fleet,
            task_instance_fleets=task_instance_fleets,
            catalogs=catalogs,
            cluster_name=cluster_name,
            vpc=vpc,
            additional_privileged_registries=additional_privileged_registries,
            additional_trusted_registries=additional_trusted_registries,
            bootstrap_actions=bootstrap_actions,
            configurations=configurations,
            enable_docker=enable_docker,
            enable_spark_rapids=enable_spark_rapids,
            enable_ssm_agent=enable_ssm_agent,
            enable_xg_boost=enable_xg_boost,
            environment=environment,
            extra_java_options=extra_java_options,
            home=home,
            idle_timeout=idle_timeout,
            install_git_hub_cli=install_git_hub_cli,
            managed_scaling_policy=managed_scaling_policy,
            release_label=release_label,
            removal_policy=removal_policy,
            scale_down_behavior=scale_down_behavior,
            step_concurrency_level=step_concurrency_level,
            steps=steps,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.FleetClusterProps",
    jsii_struct_bases=[BaseClusterProps],
    name_mapping={
        "catalogs": "catalogs",
        "cluster_name": "clusterName",
        "vpc": "vpc",
        "additional_privileged_registries": "additionalPrivilegedRegistries",
        "additional_trusted_registries": "additionalTrustedRegistries",
        "bootstrap_actions": "bootstrapActions",
        "configurations": "configurations",
        "enable_docker": "enableDocker",
        "enable_spark_rapids": "enableSparkRapids",
        "enable_ssm_agent": "enableSSMAgent",
        "enable_xg_boost": "enableXGBoost",
        "environment": "environment",
        "extra_java_options": "extraJavaOptions",
        "home": "home",
        "idle_timeout": "idleTimeout",
        "install_git_hub_cli": "installGitHubCLI",
        "managed_scaling_policy": "managedScalingPolicy",
        "release_label": "releaseLabel",
        "removal_policy": "removalPolicy",
        "scale_down_behavior": "scaleDownBehavior",
        "step_concurrency_level": "stepConcurrencyLevel",
        "steps": "steps",
        "core_instance_fleet": "coreInstanceFleet",
        "primary_instance_fleet": "primaryInstanceFleet",
        "task_instance_fleets": "taskInstanceFleets",
    },
)
class FleetClusterProps(BaseClusterProps):
    def __init__(
        self,
        *,
        catalogs: typing.Mapping[builtins.str, "ICatalog"],
        cluster_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_docker: typing.Optional[builtins.bool] = None,
        enable_spark_rapids: typing.Optional[builtins.bool] = None,
        enable_ssm_agent: typing.Optional[builtins.bool] = None,
        enable_xg_boost: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        home: typing.Optional["Workspace"] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        install_git_hub_cli: typing.Optional[builtins.bool] = None,
        managed_scaling_policy: typing.Optional[typing.Union["ManagedScalingPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        release_label: typing.Optional["ReleaseLabel"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        scale_down_behavior: typing.Optional["ScaleDownBehavior"] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        steps: typing.Optional[typing.Sequence[typing.Union["Step", typing.Dict[builtins.str, typing.Any]]]] = None,
        core_instance_fleet: typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]],
        primary_instance_fleet: typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]],
        task_instance_fleets: typing.Optional[typing.Sequence[typing.Union["InstanceFleet", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param catalogs: (experimental) The catalogs to use for the EMR cluster.
        :param cluster_name: (experimental) Name of the EMR Cluster.
        :param vpc: (experimental) The VPC to deploy the EMR cluster into.
        :param additional_privileged_registries: (experimental) Additional registries to allow privileged containers from. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param additional_trusted_registries: (experimental) Additional registries to trust for Docker containers. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param bootstrap_actions: Default: - No bootstrap actions
        :param configurations: (experimental) Override EMR Configurations. Default: - the {@link catalog }'s configurations + .venv for the user code.
        :param enable_docker: (experimental) Enable Docker support on the cluster. Default: true
        :param enable_spark_rapids: (experimental) Enable the Spark Rapids plugin. Default: false
        :param enable_ssm_agent: (experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes. Default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``
        :param enable_xg_boost: (experimental) Enable the XGBoost spark library. Default: false
        :param environment: (experimental) Environment variables to make available to the EMR cluster. Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there. Default: - no environment variables
        :param extra_java_options: (experimental) Extra java options to include in the Spark context by default.
        :param home: (experimental) Mount a shared filesystem to the EMR cluster.
        :param idle_timeout: Default: None
        :param install_git_hub_cli: (experimental) Install the GitHub CLI on the EMR cluster. Default: false
        :param managed_scaling_policy: Default: - No managed scaling policy
        :param release_label: Default: - {@link ReleaseLabel.LATEST }
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param scale_down_behavior: Default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }
        :param step_concurrency_level: (experimental) The concurrency level of the cluster. Default: 1
        :param steps: (experimental) The EMR Steps to submit to the cluster.
        :param core_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the core {@link InstanceFleet}.
        :param primary_instance_fleet: (experimental) Describes the EC2 instances and instance configurations for the primary {@link InstanceFleet} when using {@link FleetCluster}s.
        :param task_instance_fleets: (experimental) Describes the EC2 instances and instance configurations for the task {@link InstanceFleet}s. These task {@link InstanceFleet}s are added to the cluster as part of the cluster launch. Each task {@link InstanceFleet} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceFleet}s. .. epigraph:: You can currently specify only one task instance fleet for a cluster. After creating the cluster, you can only modify the mutable properties of ``InstanceFleetConfig`` , which are ``TargetOnDemandCapacity`` and ``TargetSpotCapacity`` . Modifying any other property results in cluster replacement. > To allow a maximum of 30 Amazon EC2 instance types per fleet, include ``TaskInstanceFleets`` when you create your cluster. If you create your cluster without ``TaskInstanceFleets`` , Amazon EMR uses its default allocation strategy, which allows for a maximum of five Amazon EC2 instance types.

        :stability: experimental
        '''
        if isinstance(managed_scaling_policy, dict):
            managed_scaling_policy = ManagedScalingPolicy(**managed_scaling_policy)
        if isinstance(core_instance_fleet, dict):
            core_instance_fleet = InstanceFleet(**core_instance_fleet)
        if isinstance(primary_instance_fleet, dict):
            primary_instance_fleet = InstanceFleet(**primary_instance_fleet)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7b880bc0da0f93f23bfa396fe9c59e3746d2b0092ea0fc82abaa18d17075a1b)
            check_type(argname="argument catalogs", value=catalogs, expected_type=type_hints["catalogs"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument additional_privileged_registries", value=additional_privileged_registries, expected_type=type_hints["additional_privileged_registries"])
            check_type(argname="argument additional_trusted_registries", value=additional_trusted_registries, expected_type=type_hints["additional_trusted_registries"])
            check_type(argname="argument bootstrap_actions", value=bootstrap_actions, expected_type=type_hints["bootstrap_actions"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
            check_type(argname="argument enable_docker", value=enable_docker, expected_type=type_hints["enable_docker"])
            check_type(argname="argument enable_spark_rapids", value=enable_spark_rapids, expected_type=type_hints["enable_spark_rapids"])
            check_type(argname="argument enable_ssm_agent", value=enable_ssm_agent, expected_type=type_hints["enable_ssm_agent"])
            check_type(argname="argument enable_xg_boost", value=enable_xg_boost, expected_type=type_hints["enable_xg_boost"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument extra_java_options", value=extra_java_options, expected_type=type_hints["extra_java_options"])
            check_type(argname="argument home", value=home, expected_type=type_hints["home"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument install_git_hub_cli", value=install_git_hub_cli, expected_type=type_hints["install_git_hub_cli"])
            check_type(argname="argument managed_scaling_policy", value=managed_scaling_policy, expected_type=type_hints["managed_scaling_policy"])
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument scale_down_behavior", value=scale_down_behavior, expected_type=type_hints["scale_down_behavior"])
            check_type(argname="argument step_concurrency_level", value=step_concurrency_level, expected_type=type_hints["step_concurrency_level"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
            check_type(argname="argument core_instance_fleet", value=core_instance_fleet, expected_type=type_hints["core_instance_fleet"])
            check_type(argname="argument primary_instance_fleet", value=primary_instance_fleet, expected_type=type_hints["primary_instance_fleet"])
            check_type(argname="argument task_instance_fleets", value=task_instance_fleets, expected_type=type_hints["task_instance_fleets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "catalogs": catalogs,
            "cluster_name": cluster_name,
            "vpc": vpc,
            "core_instance_fleet": core_instance_fleet,
            "primary_instance_fleet": primary_instance_fleet,
        }
        if additional_privileged_registries is not None:
            self._values["additional_privileged_registries"] = additional_privileged_registries
        if additional_trusted_registries is not None:
            self._values["additional_trusted_registries"] = additional_trusted_registries
        if bootstrap_actions is not None:
            self._values["bootstrap_actions"] = bootstrap_actions
        if configurations is not None:
            self._values["configurations"] = configurations
        if enable_docker is not None:
            self._values["enable_docker"] = enable_docker
        if enable_spark_rapids is not None:
            self._values["enable_spark_rapids"] = enable_spark_rapids
        if enable_ssm_agent is not None:
            self._values["enable_ssm_agent"] = enable_ssm_agent
        if enable_xg_boost is not None:
            self._values["enable_xg_boost"] = enable_xg_boost
        if environment is not None:
            self._values["environment"] = environment
        if extra_java_options is not None:
            self._values["extra_java_options"] = extra_java_options
        if home is not None:
            self._values["home"] = home
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if install_git_hub_cli is not None:
            self._values["install_git_hub_cli"] = install_git_hub_cli
        if managed_scaling_policy is not None:
            self._values["managed_scaling_policy"] = managed_scaling_policy
        if release_label is not None:
            self._values["release_label"] = release_label
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if scale_down_behavior is not None:
            self._values["scale_down_behavior"] = scale_down_behavior
        if step_concurrency_level is not None:
            self._values["step_concurrency_level"] = step_concurrency_level
        if steps is not None:
            self._values["steps"] = steps
        if task_instance_fleets is not None:
            self._values["task_instance_fleets"] = task_instance_fleets

    @builtins.property
    def catalogs(self) -> typing.Mapping[builtins.str, "ICatalog"]:
        '''(experimental) The catalogs to use for the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("catalogs")
        assert result is not None, "Required property 'catalogs' is missing"
        return typing.cast(typing.Mapping[builtins.str, "ICatalog"], result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''(experimental) Name of the EMR Cluster.

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to deploy the EMR cluster into.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def additional_privileged_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to allow privileged containers from.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_privileged_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_trusted_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to trust for Docker containers.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_trusted_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bootstrap_actions(self) -> typing.Optional[typing.List[BootstrapAction]]:
        '''
        :default: - No bootstrap actions

        :stability: experimental
        '''
        result = self._values.get("bootstrap_actions")
        return typing.cast(typing.Optional[typing.List[BootstrapAction]], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List[Configuration]]:
        '''(experimental) Override EMR Configurations.

        :default: - the {@link catalog }'s configurations + .venv for the user code.

        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List[Configuration]], result)

    @builtins.property
    def enable_docker(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Docker support on the cluster.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enable_docker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_spark_rapids(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the Spark Rapids plugin.

        :default: false

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-rapids.html
        :stability: experimental
        '''
        result = self._values.get("enable_spark_rapids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ssm_agent(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes.

        :default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``

        :stability: experimental
        '''
        result = self._values.get("enable_ssm_agent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_xg_boost(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the XGBoost spark library.

        :default: false

        :see: https://docs.nvidia.com/spark-rapids/user-guide/latest/getting-started/aws-emr.html
        :stability: experimental
        '''
        result = self._values.get("enable_xg_boost")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables to make available to the EMR cluster.

        Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there.

        :default: - no environment variables

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def extra_java_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Extra java options to include in the Spark context by default.

        :stability: experimental
        '''
        result = self._values.get("extra_java_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def home(self) -> typing.Optional["Workspace"]:
        '''(experimental) Mount a shared filesystem to the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("home")
        return typing.cast(typing.Optional["Workspace"], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''
        :default: None

        :stability: experimental
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def install_git_hub_cli(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install the GitHub CLI on the EMR cluster.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("install_git_hub_cli")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_scaling_policy(self) -> typing.Optional["ManagedScalingPolicy"]:
        '''
        :default: - No managed scaling policy

        :stability: experimental
        '''
        result = self._values.get("managed_scaling_policy")
        return typing.cast(typing.Optional["ManagedScalingPolicy"], result)

    @builtins.property
    def release_label(self) -> typing.Optional["ReleaseLabel"]:
        '''
        :default: - {@link ReleaseLabel.LATEST }

        :stability: experimental
        '''
        result = self._values.get("release_label")
        return typing.cast(typing.Optional["ReleaseLabel"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :default: {@link RemovalPolicy.DESTROY }

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def scale_down_behavior(self) -> typing.Optional["ScaleDownBehavior"]:
        '''
        :default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }

        :stability: experimental
        '''
        result = self._values.get("scale_down_behavior")
        return typing.cast(typing.Optional["ScaleDownBehavior"], result)

    @builtins.property
    def step_concurrency_level(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The concurrency level of the cluster.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("step_concurrency_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def steps(self) -> typing.Optional[typing.List["Step"]]:
        '''(experimental) The EMR Steps to submit to the cluster.

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-submit-step.html
        :stability: experimental
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.List["Step"]], result)

    @builtins.property
    def core_instance_fleet(self) -> "InstanceFleet":
        '''(experimental) Describes the EC2 instances and instance configurations for the core {@link InstanceFleet}.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-coreinstancefleet
        :stability: experimental
        '''
        result = self._values.get("core_instance_fleet")
        assert result is not None, "Required property 'core_instance_fleet' is missing"
        return typing.cast("InstanceFleet", result)

    @builtins.property
    def primary_instance_fleet(self) -> "InstanceFleet":
        '''(experimental) Describes the EC2 instances and instance configurations for the primary {@link InstanceFleet} when using {@link FleetCluster}s.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-masterinstancefleet
        :stability: experimental
        '''
        result = self._values.get("primary_instance_fleet")
        assert result is not None, "Required property 'primary_instance_fleet' is missing"
        return typing.cast("InstanceFleet", result)

    @builtins.property
    def task_instance_fleets(self) -> typing.Optional[typing.List["InstanceFleet"]]:
        '''(experimental) Describes the EC2 instances and instance configurations for the task {@link InstanceFleet}s.

        These task {@link InstanceFleet}s are added to the cluster as part of the cluster launch.
        Each task {@link InstanceFleet} must have a unique name specified so that CloudFormation
        can differentiate between the task {@link InstanceFleet}s.
        .. epigraph::

           You can currently specify only one task instance fleet for a cluster. After creating the cluster, you can only modify the mutable properties of ``InstanceFleetConfig`` , which are ``TargetOnDemandCapacity`` and ``TargetSpotCapacity`` . Modifying any other property results in cluster replacement. > To allow a maximum of 30 Amazon EC2 instance types per fleet, include ``TaskInstanceFleets`` when you create your cluster. If you create your cluster without ``TaskInstanceFleets`` , Amazon EMR uses its default allocation strategy, which allows for a maximum of five Amazon EC2 instance types.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-taskinstancefleets
        :stability: experimental
        '''
        result = self._values.get("task_instance_fleets")
        return typing.cast(typing.Optional[typing.List["InstanceFleet"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FleetClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.FromBucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "warehouse_bucket_name": "warehouseBucketName",
        "warehouse_prefix": "warehousePrefix",
    },
)
class FromBucketProps:
    def __init__(
        self,
        *,
        warehouse_bucket_name: builtins.str,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param warehouse_bucket_name: 
        :param warehouse_prefix: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64c71c6a195e64fcc7766185b4e1593d178b1bf46a3fd25f066e29cd8724c1a3)
            check_type(argname="argument warehouse_bucket_name", value=warehouse_bucket_name, expected_type=type_hints["warehouse_bucket_name"])
            check_type(argname="argument warehouse_prefix", value=warehouse_prefix, expected_type=type_hints["warehouse_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "warehouse_bucket_name": warehouse_bucket_name,
        }
        if warehouse_prefix is not None:
            self._values["warehouse_prefix"] = warehouse_prefix

    @builtins.property
    def warehouse_bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("warehouse_bucket_name")
        assert result is not None, "Required property 'warehouse_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def warehouse_prefix(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("warehouse_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FromBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IConnectable)
class Home(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.Home",
):
    '''(experimental) A Home directory is a secure directory in a {@link Workspace} only accessible by the User who owns it.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        file_system: _aws_cdk_aws_efs_ceddda9d.FileSystem,
        uid: builtins.str,
        username: builtins.str,
        gid: typing.Optional[builtins.str] = None,
        secondary_groups: typing.Optional[typing.Sequence[typing.Union["PosixGroup", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param file_system: (experimental) The file system associated with the user.
        :param uid: (experimental) The POSIX user ID for the user. This should be a unique identifier.
        :param username: (experimental) The username for the user. This should be unique across all users.
        :param gid: (experimental) The POSIX group ID for the user. This is used for file system permissions. Default: - same as the uid
        :param secondary_groups: (experimental) Secondary groups to assign to files written to this home directory.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__565212a4b85e23ae7e75f9af714ae0d6c58b278abee4604b6e959e86a3d3ca98)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HomeProps(
            file_system=file_system,
            uid=uid,
            username=username,
            gid=gid,
            secondary_groups=secondary_groups,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allowFrom")
    def allow_from(self, connectable: _aws_cdk_aws_ec2_ceddda9d.IConnectable) -> None:
        '''
        :param connectable: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e37cb5626890e66da3571373688915fca87b6cf18d6c0dbddbafe8d3f3326f7)
            check_type(argname="argument connectable", value=connectable, expected_type=type_hints["connectable"])
        return typing.cast(None, jsii.invoke(self, "allowFrom", [connectable]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        __0: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        actions: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param __0: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92a47ab18dc2d229886601567cbd4520f5d3447db1909eae7af40a537284a288)
            check_type(argname="argument __0", value=__0, expected_type=type_hints["__0"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        return typing.cast(None, jsii.invoke(self, "grant", [__0, actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, __0: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param __0: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f499ee8828f3f2cb8680f4189798e08ad6b5205c936440fa5bb4919e298a7835)
            check_type(argname="argument __0", value=__0, expected_type=type_hints["__0"])
        return typing.cast(None, jsii.invoke(self, "grantRead", [__0]))

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(self, __0: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param __0: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85410aca4b22598ee59d643583833f47a41d83dc8563194e0cd73bce957cb7b4)
            check_type(argname="argument __0", value=__0, expected_type=type_hints["__0"])
        return typing.cast(None, jsii.invoke(self, "grantReadWrite", [__0]))

    @jsii.member(jsii_name="grantRootAccess")
    def grant_root_access(self, __0: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''
        :param __0: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7aec28287cccd97087f2cb06dcc02199690033ca6da8e3311b09c6636a1ea120)
            check_type(argname="argument __0", value=__0, expected_type=type_hints["__0"])
        return typing.cast(None, jsii.invoke(self, "grantRootAccess", [__0]))

    @builtins.property
    @jsii.member(jsii_name="accessPoint")
    def access_point(self) -> _aws_cdk_aws_efs_ceddda9d.AccessPoint:
        '''(experimental) An {@link AccessPoint} to the user's home directory.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.AccessPoint, jsii.get(self, "accessPoint"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) The connections for the EFS file system.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="gid")
    def gid(self) -> builtins.str:
        '''(experimental) The POSIX group ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gid"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''(experimental) Absolute path to the home directory.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        '''(experimental) The POSIX user ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        '''(experimental) The username of the user.

        Should match the AWS SSO username.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "username"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.HomeProps",
    jsii_struct_bases=[],
    name_mapping={
        "file_system": "fileSystem",
        "uid": "uid",
        "username": "username",
        "gid": "gid",
        "secondary_groups": "secondaryGroups",
    },
)
class HomeProps:
    def __init__(
        self,
        *,
        file_system: _aws_cdk_aws_efs_ceddda9d.FileSystem,
        uid: builtins.str,
        username: builtins.str,
        gid: typing.Optional[builtins.str] = None,
        secondary_groups: typing.Optional[typing.Sequence[typing.Union["PosixGroup", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param file_system: (experimental) The file system associated with the user.
        :param uid: (experimental) The POSIX user ID for the user. This should be a unique identifier.
        :param username: (experimental) The username for the user. This should be unique across all users.
        :param gid: (experimental) The POSIX group ID for the user. This is used for file system permissions. Default: - same as the uid
        :param secondary_groups: (experimental) Secondary groups to assign to files written to this home directory.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2016038cc3fc8f8a8e6c9dc814e5b4561ac849f85a87b90b9264b3c90356995)
            check_type(argname="argument file_system", value=file_system, expected_type=type_hints["file_system"])
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
            check_type(argname="argument secondary_groups", value=secondary_groups, expected_type=type_hints["secondary_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "file_system": file_system,
            "uid": uid,
            "username": username,
        }
        if gid is not None:
            self._values["gid"] = gid
        if secondary_groups is not None:
            self._values["secondary_groups"] = secondary_groups

    @builtins.property
    def file_system(self) -> _aws_cdk_aws_efs_ceddda9d.FileSystem:
        '''(experimental) The file system associated with the user.

        :stability: experimental
        '''
        result = self._values.get("file_system")
        assert result is not None, "Required property 'file_system' is missing"
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.FileSystem, result)

    @builtins.property
    def uid(self) -> builtins.str:
        '''(experimental) The POSIX user ID for the user.

        This should be a unique identifier.

        :stability: experimental
        '''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) The username for the user.

        This should be unique across all users.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gid(self) -> typing.Optional[builtins.str]:
        '''(experimental) The POSIX group ID for the user.

        This is used for file system permissions.

        :default: - same as the uid

        :stability: experimental
        '''
        result = self._values.get("gid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_groups(self) -> typing.Optional[typing.List["PosixGroup"]]:
        '''(experimental) Secondary groups to assign to files written to this home directory.

        :stability: experimental
        '''
        result = self._values.get("secondary_groups")
        return typing.cast(typing.Optional[typing.List["PosixGroup"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HomeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@packyak/aws-cdk.IBindable")
class IBindable(_aws_cdk_aws_iam_ceddda9d.IGrantable, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(self, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: -
        :param value: -

        :stability: experimental
        '''
        ...


class _IBindableProxy(
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@packyak/aws-cdk.IBindable"

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(self, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: -
        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62123fceb85b330c2443ea9e4844b198ca4e0f45eca5af15d990eff38617e338)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "addEnvironment", [key, value]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBindable).__jsii_proxy_class__ = lambda : _IBindableProxy


@jsii.interface(jsii_type="@packyak/aws-cdk.ICatalog")
class ICatalog(typing_extensions.Protocol):
    '''(experimental) A Table Catalog implementation provides.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(self, cluster: Cluster, catalog_name: builtins.str) -> None:
        '''(experimental) Bind this Catalog to a {@link Cluster} by granting any required IAM Policies and adding any required configurations to the Cluster.

        :param cluster: the cluster to bind this catalog to.
        :param catalog_name: the name to bind the catalog under.

        :stability: experimental
        '''
        ...


class _ICatalogProxy:
    '''(experimental) A Table Catalog implementation provides.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@packyak/aws-cdk.ICatalog"

    @jsii.member(jsii_name="bind")
    def bind(self, cluster: Cluster, catalog_name: builtins.str) -> None:
        '''(experimental) Bind this Catalog to a {@link Cluster} by granting any required IAM Policies and adding any required configurations to the Cluster.

        :param cluster: the cluster to bind this catalog to.
        :param catalog_name: the name to bind the catalog under.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ba13ad981cd127d54e85d1a4b2c4f77032428b6b6e23ead782555b8b4617031)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
        return typing.cast(None, jsii.invoke(self, "bind", [cluster, catalog_name]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICatalog).__jsii_proxy_class__ = lambda : _ICatalogProxy


@jsii.interface(jsii_type="@packyak/aws-cdk.INessieCatalog")
class INessieCatalog(ICatalog, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="apiV1Url")
    def api_v1_url(self) -> builtins.str:
        '''(deprecated) Endpoint for the Nessie API v1.

        This endpoint provides access to the version 1 of the Nessie API. It is recommended to use the v2 endpoint for the latest features and improvements.

        :deprecated: This version of the API is deprecated and will be removed in future releases. Use {@link apiV2Url } instead.

        :stability: deprecated
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="apiV2Url")
    def api_v2_url(self) -> builtins.str:
        '''(experimental) Endpoint for the Nessie API v2.

        This endpoint provides access to the version 2 of the Nessie API. It is the recommended endpoint to use for all interactions with the Nessie service.

        Note: The Nessie CLI is compatible only with this version of the API. For CLI interactions, ensure to use this endpoint.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultMainBranch")
    def default_main_branch(self) -> builtins.str:
        '''(experimental) The default main branch of the Nessie repository.

        This property specifies the main branch that will be used by default for all operations within the Nessie service.

        :default: main

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        '''(experimental) The Nessie service endpoint.

        :stability: experimental
        '''
        ...


class _INessieCatalogProxy(
    jsii.proxy_for(ICatalog), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@packyak/aws-cdk.INessieCatalog"

    @builtins.property
    @jsii.member(jsii_name="apiV1Url")
    def api_v1_url(self) -> builtins.str:
        '''(deprecated) Endpoint for the Nessie API v1.

        This endpoint provides access to the version 1 of the Nessie API. It is recommended to use the v2 endpoint for the latest features and improvements.

        :deprecated: This version of the API is deprecated and will be removed in future releases. Use {@link apiV2Url } instead.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiV1Url"))

    @builtins.property
    @jsii.member(jsii_name="apiV2Url")
    def api_v2_url(self) -> builtins.str:
        '''(experimental) Endpoint for the Nessie API v2.

        This endpoint provides access to the version 2 of the Nessie API. It is the recommended endpoint to use for all interactions with the Nessie service.

        Note: The Nessie CLI is compatible only with this version of the API. For CLI interactions, ensure to use this endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiV2Url"))

    @builtins.property
    @jsii.member(jsii_name="defaultMainBranch")
    def default_main_branch(self) -> builtins.str:
        '''(experimental) The default main branch of the Nessie repository.

        This property specifies the main branch that will be used by default for all operations within the Nessie service.

        :default: main

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "defaultMainBranch"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        '''(experimental) The Nessie service endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INessieCatalog).__jsii_proxy_class__ = lambda : _INessieCatalogProxy


@jsii.implements(ICatalog)
class IcebergGlueCatalog(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.IcebergGlueCatalog",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param warehouse_bucket: (experimental) The S3 bucket where the Iceberg table data is stored. Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix for the Iceberg table data in the S3 bucket. Default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcf3c0364f4d160fe9034f175d8eb6cc3d6d3fb23381b927b0d52a823dbb6a77)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IcebergGlueCatalogProps(
            warehouse_bucket=warehouse_bucket, warehouse_prefix=warehouse_prefix
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromBucketName")
    @builtins.classmethod
    def from_bucket_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        warehouse_bucket_name: builtins.str,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> "IcebergGlueCatalog":
        '''
        :param scope: -
        :param id: -
        :param warehouse_bucket_name: 
        :param warehouse_prefix: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c8134ca0fa427857fe6c762437e22f941b749792f5a0705a5beb13b6f80468d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FromBucketProps(
            warehouse_bucket_name=warehouse_bucket_name,
            warehouse_prefix=warehouse_prefix,
        )

        return typing.cast("IcebergGlueCatalog", jsii.sinvoke(cls, "fromBucketName", [scope, id, props]))

    @jsii.member(jsii_name="bind")
    def bind(self, cluster: Cluster, catalog_name: builtins.str) -> None:
        '''(experimental) Bind this Catalog to a {@link Cluster} by granting any required IAM Policies and adding any required configurations to the Cluster.

        :param cluster: -
        :param catalog_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c7dc1276a04dbc750cc24c39a7c676937f09de7bb3266691c1ac2e95c8c309a)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
        return typing.cast(None, jsii.invoke(self, "bind", [cluster, catalog_name]))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.IcebergGlueCatalogProps",
    jsii_struct_bases=[],
    name_mapping={
        "warehouse_bucket": "warehouseBucket",
        "warehouse_prefix": "warehousePrefix",
    },
)
class IcebergGlueCatalogProps:
    def __init__(
        self,
        *,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param warehouse_bucket: (experimental) The S3 bucket where the Iceberg table data is stored. Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix for the Iceberg table data in the S3 bucket. Default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be36b3a23075d957cc97f13224bf1742ba67fd459d9b772c66e22d3edc9dac37)
            check_type(argname="argument warehouse_bucket", value=warehouse_bucket, expected_type=type_hints["warehouse_bucket"])
            check_type(argname="argument warehouse_prefix", value=warehouse_prefix, expected_type=type_hints["warehouse_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if warehouse_bucket is not None:
            self._values["warehouse_bucket"] = warehouse_bucket
        if warehouse_prefix is not None:
            self._values["warehouse_prefix"] = warehouse_prefix

    @builtins.property
    def warehouse_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) The S3 bucket where the Iceberg table data is stored.

        :default: - one is created for you

        :stability: experimental
        '''
        result = self._values.get("warehouse_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def warehouse_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The prefix for the Iceberg table data in the S3 bucket.

        :default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        result = self._values.get("warehouse_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IcebergGlueCatalogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.InstanceFleet",
    jsii_struct_bases=[],
    name_mapping={
        "instance_types": "instanceTypes",
        "name": "name",
        "allocation_strategy": "allocationStrategy",
        "target_on_demand_capacity": "targetOnDemandCapacity",
        "target_spot_capacity": "targetSpotCapacity",
        "timeout_action": "timeoutAction",
        "timeout_duration": "timeoutDuration",
    },
)
class InstanceFleet:
    def __init__(
        self,
        *,
        instance_types: typing.Sequence[typing.Union["InstanceTypeConfig", typing.Dict[builtins.str, typing.Any]]],
        name: builtins.str,
        allocation_strategy: typing.Optional[AllocationStrategy] = None,
        target_on_demand_capacity: typing.Optional[jsii.Number] = None,
        target_spot_capacity: typing.Optional[jsii.Number] = None,
        timeout_action: typing.Optional["TimeoutAction"] = None,
        timeout_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param instance_types: (experimental) The instance types and their weights to use for the InstanceFleet.
        :param name: (experimental) The name of the InstanceFleet.
        :param allocation_strategy: (experimental) The allocation strategy to use when provisioning Spot Instances. Default: AllocationStrategy.LOWEST_PRICE
        :param target_on_demand_capacity: (experimental) The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision. When the instance fleet launches, Amazon EMR tries to provision On-Demand instances as specified by {@link instanceTypes}. Each {@link InstanceTypeConfig} has a specified {@link InstanceTypeConfig.weightedCapacity}. When an On-Demand instance is provisioned, the {@link InstanceTypeConfig.weightedCapacity} units count toward the target capacity. Amazon EMR provisions instances until the target capacity is totally fulfilled, even if this results in an overage. For example, if there are 2 units remaining to fulfill capacity, and Amazon EMR can only provision an instance with a ``WeightedCapacity`` of 5 units, the instance is provisioned, and the target capacity is exceeded by 3 units. .. epigraph:: If not specified or set to 0, only Spot instances are provisioned for the instance fleet using ``TargetSpotCapacity`` . At least one of ``TargetSpotCapacity`` and ``TargetOnDemandCapacity`` should be greater than 0. For a master instance fleet, only one of ``TargetSpotCapacity`` and ``TargetOnDemandCapacity`` can be specified, and its value must be 1.
        :param target_spot_capacity: (experimental) The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision. When the instance fleet launches, Amazon EMR tries to provision Spot instances as specified by {@link InstanceTypeConfig}. Each instance configuration has a specified ``WeightedCapacity``. When a Spot instance is provisioned, the ``WeightedCapacity`` units count toward the target capacity. Amazon EMR provisions instances until the target capacity is totally fulfilled, even if this results in an overage. For example, if there are 2 units remaining to fulfill capacity, and Amazon EMR can only provision an instance with a ``WeightedCapacity`` of 5 units, the instance is provisioned, and the target capacity is exceeded by 3 units. .. epigraph:: If not specified or set to 0, only On-Demand instances are provisioned for the instance fleet. At least one of ``TargetSpotCapacity`` and ``TargetOnDemandCapacity`` should be greater than 0. For a master instance fleet, only one of ``TargetSpotCapacity`` and ``TargetOnDemandCapacity`` can be specified, and its value must be 1.
        :param timeout_action: (experimental) The action to take when provisioning a Cluster and Spot Instances are not available. Default: SWITCH_TO_ON_DEMAND
        :param timeout_duration: (experimental) The action to take when TargetSpotCapacity has not been fulfilled when the TimeoutDurationMinutes has expired; that is, when all Spot Instances could not be provisioned within the Spot provisioning timeout. Valid values are {@link TimeoutAction.TERMINATE_CLUSTER} and {@link TimeoutAction.SWITCH_TO_ON_DEMAND}. {@link TimeoutAction.SWITCH_TO_ON_DEMAND} specifies that if no Spot Instances are available, On-Demand Instances should be provisioned to fulfill any remaining Spot capacity. The minimum is ``5`` minutes and the maximum is ``24`` hours. Default: - 1 hour

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a8e830f7bfa4a9fb090af90b9a9af86ec643a49d1d904685ce6d895915c13ae)
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allocation_strategy", value=allocation_strategy, expected_type=type_hints["allocation_strategy"])
            check_type(argname="argument target_on_demand_capacity", value=target_on_demand_capacity, expected_type=type_hints["target_on_demand_capacity"])
            check_type(argname="argument target_spot_capacity", value=target_spot_capacity, expected_type=type_hints["target_spot_capacity"])
            check_type(argname="argument timeout_action", value=timeout_action, expected_type=type_hints["timeout_action"])
            check_type(argname="argument timeout_duration", value=timeout_duration, expected_type=type_hints["timeout_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_types": instance_types,
            "name": name,
        }
        if allocation_strategy is not None:
            self._values["allocation_strategy"] = allocation_strategy
        if target_on_demand_capacity is not None:
            self._values["target_on_demand_capacity"] = target_on_demand_capacity
        if target_spot_capacity is not None:
            self._values["target_spot_capacity"] = target_spot_capacity
        if timeout_action is not None:
            self._values["timeout_action"] = timeout_action
        if timeout_duration is not None:
            self._values["timeout_duration"] = timeout_duration

    @builtins.property
    def instance_types(self) -> typing.List["InstanceTypeConfig"]:
        '''(experimental) The instance types and their weights to use for the InstanceFleet.

        :stability: experimental
        '''
        result = self._values.get("instance_types")
        assert result is not None, "Required property 'instance_types' is missing"
        return typing.cast(typing.List["InstanceTypeConfig"], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the InstanceFleet.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocation_strategy(self) -> typing.Optional[AllocationStrategy]:
        '''(experimental) The allocation strategy to use when provisioning Spot Instances.

        :default: AllocationStrategy.LOWEST_PRICE

        :stability: experimental
        '''
        result = self._values.get("allocation_strategy")
        return typing.cast(typing.Optional[AllocationStrategy], result)

    @builtins.property
    def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.

        When the instance fleet launches, Amazon EMR
        tries to provision On-Demand instances as specified by {@link instanceTypes}.

        Each {@link InstanceTypeConfig} has a specified {@link InstanceTypeConfig.weightedCapacity}.
        When an On-Demand instance is provisioned, the {@link InstanceTypeConfig.weightedCapacity}
        units count toward the target capacity.

        Amazon EMR provisions instances until the target capacity is totally fulfilled, even
        if this results in an overage. For example, if there are 2 units remaining to fulfill
        capacity, and Amazon EMR can only provision an instance with a ``WeightedCapacity`` of 5
        units, the instance is provisioned, and the target capacity is exceeded by 3 units.
        .. epigraph::

           If not specified or set to 0, only Spot instances are provisioned for the instance fleet
           using ``TargetSpotCapacity`` . At least one of ``TargetSpotCapacity`` and ``TargetOnDemandCapacity``
           should be greater than 0. For a master instance fleet, only one of ``TargetSpotCapacity`` and
           ``TargetOnDemandCapacity`` can be specified, and its value must be 1.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancefleetconfig.html#cfn-emr-cluster-instancefleetconfig-targetondemandcapacity
        :stability: experimental
        '''
        result = self._values.get("target_on_demand_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.

        When the instance fleet launches, Amazon EMR tries to provision Spot instances as specified by
        {@link InstanceTypeConfig}. Each instance configuration has a specified ``WeightedCapacity``. When a Spot instance is provisioned, the ``WeightedCapacity`` units count toward the target capacity. Amazon EMR provisions instances until the target capacity is totally fulfilled, even if this results in an overage. For example, if there are 2 units remaining to fulfill capacity, and Amazon EMR can only provision an instance with a ``WeightedCapacity`` of 5 units, the instance is provisioned, and the target capacity is exceeded by 3 units.
        .. epigraph::

           If not specified or set to 0, only On-Demand instances are provisioned for the instance fleet. At least one of ``TargetSpotCapacity`` and ``TargetOnDemandCapacity`` should be greater than 0. For a master instance fleet, only one of ``TargetSpotCapacity`` and ``TargetOnDemandCapacity`` can be specified, and its value must be 1.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancefleetconfig.html#cfn-emr-cluster-instancefleetconfig-targetspotcapacity
        :stability: experimental
        '''
        result = self._values.get("target_spot_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout_action(self) -> typing.Optional["TimeoutAction"]:
        '''(experimental) The action to take when provisioning a Cluster and Spot Instances are not available.

        :default: SWITCH_TO_ON_DEMAND

        :see: https://docs.aws.amazon.com/emr/latest/APIReference/API_SpotProvisioningSpecification.html
        :stability: experimental
        '''
        result = self._values.get("timeout_action")
        return typing.cast(typing.Optional["TimeoutAction"], result)

    @builtins.property
    def timeout_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The action to take when TargetSpotCapacity has not been fulfilled when the TimeoutDurationMinutes has expired;

        that is, when all Spot Instances
        could not be provisioned within the Spot provisioning timeout. Valid
        values are {@link TimeoutAction.TERMINATE_CLUSTER} and {@link TimeoutAction.SWITCH_TO_ON_DEMAND}.

        {@link TimeoutAction.SWITCH_TO_ON_DEMAND} specifies that if no Spot Instances
        are available, On-Demand Instances should be provisioned to fulfill any
        remaining Spot capacity.

        The minimum is ``5`` minutes and the maximum is ``24`` hours.

        :default: - 1 hour

        :see: {@link http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-spotprovisioningspecification.html#cfn-emr-cluster-spotprovisioningspecification-timeoutaction}
        :stability: experimental
        '''
        result = self._values.get("timeout_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceFleet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.InstanceGroup",
    jsii_struct_bases=[],
    name_mapping={
        "instance_count": "instanceCount",
        "instance_type": "instanceType",
        "name": "name",
        "auto_scaling_policy": "autoScalingPolicy",
        "bid_price": "bidPrice",
        "configurations": "configurations",
        "custom_ami": "customAmi",
        "ebs_block_devices": "ebsBlockDevices",
        "ebs_optimized": "ebsOptimized",
        "market": "market",
    },
)
class InstanceGroup:
    def __init__(
        self,
        *,
        instance_count: jsii.Number,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        name: builtins.str,
        auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        bid_price: typing.Optional[builtins.str] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
        custom_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        ebs_block_devices: typing.Optional[typing.Sequence[typing.Union[EbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        market: typing.Optional["InstanceMarket"] = None,
    ) -> None:
        '''
        :param instance_count: (experimental) Target number of instances for the instance group.
        :param instance_type: (experimental) The Amazon EC2 instance type for all instances in the instance group.
        :param name: (experimental) Friendly name given to the instance group.
        :param auto_scaling_policy: (experimental) ``AutoScalingPolicy`` is a subproperty of the `InstanceGroupConfig <https://docs.aws.amazon.com//AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig-instancegroupconfig.html>`_ property type that specifies the constraints and rules of an automatic scaling policy in Amazon EMR . The automatic scaling policy defines how an instance group dynamically adds and terminates EC2 instances in response to the value of a CloudWatch metric. Only core and task instance groups can use automatic scaling policies. For more information, see `Using Automatic Scaling in Amazon EMR <https://docs.aws.amazon.com//emr/latest/ManagementGuide/emr-automatic-scaling.html>`_ .
        :param bid_price: (experimental) If specified, indicates that the instance group uses Spot Instances. This is the maximum price you are willing to pay for Spot Instances. Specify ``OnDemandPrice`` to set the amount equal to the On-Demand price, or specify an amount in USD.
        :param configurations: (experimental) > Amazon EMR releases 4.x or later. The list of configurations supplied for an Amazon EMR cluster instance group. You can specify a separate configuration for each instance group (master, core, and task).
        :param custom_ami: (experimental) The custom AMI ID to use for the provisioned instance group.
        :param ebs_block_devices: (experimental) EBS {@link EbsBlockDevice}s to attach to an instance in an {@link InstanceFleet }. Default: - No EBS block devices
        :param ebs_optimized: (experimental) An Amazon EBS–optimized instance uses an optimized configuration stack and provides additional, dedicated capacity for Amazon EBS I/O. This optimization provides the best performance for your EBS volumes by minimizing contention between Amazon EBS I/O and other traffic from your instance. **Note**: .. epigraph:: For Current Generation Instance types, EBS-optimization is enabled by default at no additional cost. For Previous Generation Instances types, EBS-optimization prices are on the Previous Generation Pricing Page. Default: true
        :param market: (experimental) Market type of the Amazon EC2 instances used to create a cluster node.

        :stability: experimental
        '''
        if isinstance(auto_scaling_policy, dict):
            auto_scaling_policy = AutoScalingPolicy(**auto_scaling_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d789f501f696ccecc6fe3a5c6c3e8e1ef13012d686e91ffd2a154f89069279fc)
            check_type(argname="argument instance_count", value=instance_count, expected_type=type_hints["instance_count"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument auto_scaling_policy", value=auto_scaling_policy, expected_type=type_hints["auto_scaling_policy"])
            check_type(argname="argument bid_price", value=bid_price, expected_type=type_hints["bid_price"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
            check_type(argname="argument custom_ami", value=custom_ami, expected_type=type_hints["custom_ami"])
            check_type(argname="argument ebs_block_devices", value=ebs_block_devices, expected_type=type_hints["ebs_block_devices"])
            check_type(argname="argument ebs_optimized", value=ebs_optimized, expected_type=type_hints["ebs_optimized"])
            check_type(argname="argument market", value=market, expected_type=type_hints["market"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_count": instance_count,
            "instance_type": instance_type,
            "name": name,
        }
        if auto_scaling_policy is not None:
            self._values["auto_scaling_policy"] = auto_scaling_policy
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if configurations is not None:
            self._values["configurations"] = configurations
        if custom_ami is not None:
            self._values["custom_ami"] = custom_ami
        if ebs_block_devices is not None:
            self._values["ebs_block_devices"] = ebs_block_devices
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if market is not None:
            self._values["market"] = market

    @builtins.property
    def instance_count(self) -> jsii.Number:
        '''(experimental) Target number of instances for the instance group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-instancecount
        :stability: experimental
        '''
        result = self._values.get("instance_count")
        assert result is not None, "Required property 'instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''(experimental) The Amazon EC2 instance type for all instances in the instance group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-instancetype
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Friendly name given to the instance group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-name
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_scaling_policy(self) -> typing.Optional[AutoScalingPolicy]:
        '''(experimental) ``AutoScalingPolicy`` is a subproperty of the `InstanceGroupConfig <https://docs.aws.amazon.com//AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig-instancegroupconfig.html>`_ property type that specifies the constraints and rules of an automatic scaling policy in Amazon EMR . The automatic scaling policy defines how an instance group dynamically adds and terminates EC2 instances in response to the value of a CloudWatch metric. Only core and task instance groups can use automatic scaling policies. For more information, see `Using Automatic Scaling in Amazon EMR <https://docs.aws.amazon.com//emr/latest/ManagementGuide/emr-automatic-scaling.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-autoscalingpolicy
        :stability: experimental
        '''
        result = self._values.get("auto_scaling_policy")
        return typing.cast(typing.Optional[AutoScalingPolicy], result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''(experimental) If specified, indicates that the instance group uses Spot Instances.

        This is the maximum price you are willing to pay for Spot Instances. Specify ``OnDemandPrice`` to set the amount equal to the On-Demand price, or specify an amount in USD.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-bidprice
        :stability: experimental
        '''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List[Configuration]]:
        '''(experimental) > Amazon EMR releases 4.x or later.

        The list of configurations supplied for an Amazon EMR cluster instance group. You can specify a separate configuration for each instance group (master, core, and task).

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-configurations
        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List[Configuration]], result)

    @builtins.property
    def custom_ami(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage]:
        '''(experimental) The custom AMI ID to use for the provisioned instance group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-customamiid
        :stability: experimental
        '''
        result = self._values.get("custom_ami")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage], result)

    @builtins.property
    def ebs_block_devices(self) -> typing.Optional[typing.List[EbsBlockDevice]]:
        '''(experimental) EBS {@link EbsBlockDevice}s to attach to an instance in an {@link InstanceFleet }.

        :default: - No EBS block devices

        :stability: experimental
        '''
        result = self._values.get("ebs_block_devices")
        return typing.cast(typing.Optional[typing.List[EbsBlockDevice]], result)

    @builtins.property
    def ebs_optimized(self) -> typing.Optional[builtins.bool]:
        '''(experimental) An Amazon EBS–optimized instance uses an optimized configuration stack and provides additional, dedicated capacity for Amazon EBS I/O.

        This
        optimization provides the best performance for your EBS volumes by minimizing
        contention between Amazon EBS I/O and other traffic from your instance.

        **Note**:
        .. epigraph::

           For Current Generation Instance types, EBS-optimization is enabled by default at no additional cost. For Previous Generation Instances types, EBS-optimization prices are on the Previous Generation Pricing Page.

        :default: true

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-optimized.html
        :stability: experimental
        '''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def market(self) -> typing.Optional["InstanceMarket"]:
        '''(experimental) Market type of the Amazon EC2 instances used to create a cluster node.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-market
        :stability: experimental
        '''
        result = self._values.get("market")
        return typing.cast(typing.Optional["InstanceMarket"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@packyak/aws-cdk.InstanceMarket")
class InstanceMarket(enum.Enum):
    '''
    :stability: experimental
    '''

    ON_DEMAND = "ON_DEMAND"
    '''
    :stability: experimental
    '''
    SPOT = "SPOT"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.InstanceTypeConfig",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "bid_price": "bidPrice",
        "bid_price_as_percentage_of_on_demand_price": "bidPriceAsPercentageOfOnDemandPrice",
        "configurations": "configurations",
        "custom_ami": "customAmi",
        "ebs_block_devices": "ebsBlockDevices",
        "ebs_optimized": "ebsOptimized",
        "weighted_capacity": "weightedCapacity",
    },
)
class InstanceTypeConfig:
    def __init__(
        self,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        bid_price: typing.Optional[builtins.str] = None,
        bid_price_as_percentage_of_on_demand_price: typing.Optional[jsii.Number] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
        custom_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        ebs_block_devices: typing.Optional[typing.Sequence[typing.Union[EbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        weighted_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type: 
        :param bid_price: (experimental) The bid price for each Amazon EC2 Spot Instance type as defined by {@link InstanceType} .
        :param bid_price_as_percentage_of_on_demand_price: (experimental) The bid price, as a percentage of On-Demand price, for each Amazon EC2 Spot Instance as defined by {@link InstanceType}.
        :param configurations: (experimental) Optional extra configurations to apply to the instances in the fleet.
        :param custom_ami: (experimental) The custom AMI to use for the InstanceFleet. Default: - The default Amazon EMR AMI for the specified release label.
        :param ebs_block_devices: (experimental) EBS {@link EbsBlockDevice}s to attach to an instance in an {@link InstanceFleet}. Default: - No EBS block devices
        :param ebs_optimized: (experimental) An Amazon EBS–optimized instance uses an optimized configuration stack and provides additional, dedicated capacity for Amazon EBS I/O. This optimization provides the best performance for your EBS volumes by minimizing contention between Amazon EBS I/O and other traffic from your instance. **Note**: .. epigraph:: For Current Generation Instance types, EBS-optimization is enabled by default at no additional cost. For Previous Generation Instances types, EBS-optimization prices are on the Previous Generation Pricing Page. Default: true
        :param weighted_capacity: (experimental) The number of units that a provisioned instance of this type provides toward fulfilling the target capacities defined in ``InstanceFleetConfig``. This value is ``1`` for a master instance fleet, and must be 1 or greater for core and task instance fleets. Defaults to 1 if not specified. Default: 1

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__029012672ed7c72ba6a26d55172513021665b3fb45d1f49093ffa04920bcb8d9)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument bid_price", value=bid_price, expected_type=type_hints["bid_price"])
            check_type(argname="argument bid_price_as_percentage_of_on_demand_price", value=bid_price_as_percentage_of_on_demand_price, expected_type=type_hints["bid_price_as_percentage_of_on_demand_price"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
            check_type(argname="argument custom_ami", value=custom_ami, expected_type=type_hints["custom_ami"])
            check_type(argname="argument ebs_block_devices", value=ebs_block_devices, expected_type=type_hints["ebs_block_devices"])
            check_type(argname="argument ebs_optimized", value=ebs_optimized, expected_type=type_hints["ebs_optimized"])
            check_type(argname="argument weighted_capacity", value=weighted_capacity, expected_type=type_hints["weighted_capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
        }
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if bid_price_as_percentage_of_on_demand_price is not None:
            self._values["bid_price_as_percentage_of_on_demand_price"] = bid_price_as_percentage_of_on_demand_price
        if configurations is not None:
            self._values["configurations"] = configurations
        if custom_ami is not None:
            self._values["custom_ami"] = custom_ami
        if ebs_block_devices is not None:
            self._values["ebs_block_devices"] = ebs_block_devices
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if weighted_capacity is not None:
            self._values["weighted_capacity"] = weighted_capacity

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''(experimental) The bid price for each Amazon EC2 Spot Instance type as defined by {@link InstanceType} .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancetypeconfig.html#cfn-emr-cluster-instancetypeconfig-bidprice
        :stability: experimental
        '''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_price_as_percentage_of_on_demand_price(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''(experimental) The bid price, as a percentage of On-Demand price, for each Amazon EC2 Spot Instance as defined by {@link InstanceType}.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancetypeconfig.html#cfn-emr-cluster-instancetypeconfig-bidpriceaspercentageofondemandprice
        :stability: experimental
        '''
        result = self._values.get("bid_price_as_percentage_of_on_demand_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List[Configuration]]:
        '''(experimental) Optional extra configurations to apply to the instances in the fleet.

        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List[Configuration]], result)

    @builtins.property
    def custom_ami(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage]:
        '''(experimental) The custom AMI to use for the InstanceFleet.

        :default: - The default Amazon EMR AMI for the specified release label.

        :stability: experimental
        '''
        result = self._values.get("custom_ami")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage], result)

    @builtins.property
    def ebs_block_devices(self) -> typing.Optional[typing.List[EbsBlockDevice]]:
        '''(experimental) EBS {@link EbsBlockDevice}s to attach to an instance in an {@link InstanceFleet}.

        :default: - No EBS block devices

        :stability: experimental
        '''
        result = self._values.get("ebs_block_devices")
        return typing.cast(typing.Optional[typing.List[EbsBlockDevice]], result)

    @builtins.property
    def ebs_optimized(self) -> typing.Optional[builtins.bool]:
        '''(experimental) An Amazon EBS–optimized instance uses an optimized configuration stack and provides additional, dedicated capacity for Amazon EBS I/O.

        This
        optimization provides the best performance for your EBS volumes by minimizing
        contention between Amazon EBS I/O and other traffic from your instance.

        **Note**:
        .. epigraph::

           For Current Generation Instance types, EBS-optimization is enabled by default at no additional cost. For Previous Generation Instances types, EBS-optimization prices are on the Previous Generation Pricing Page.

        :default: true

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-optimized.html
        :stability: experimental
        '''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def weighted_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of units that a provisioned instance of this type provides toward fulfilling the target capacities defined in ``InstanceFleetConfig``.

        This value is ``1`` for a master instance fleet, and must be 1 or greater for
        core and task instance fleets. Defaults to 1 if not specified.

        :default: 1

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancetypeconfig.html#cfn-emr-cluster-instancetypeconfig-weightedcapacity
        :stability: experimental
        '''
        result = self._values.get("weighted_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceTypeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Jdbc(metaclass=jsii.JSIIMeta, jsii_type="@packyak/aws-cdk.Jdbc"):
    '''(experimental) Configures an EMR Cluster to start a Thrift Server daemon.

    :stability: experimental
    '''

    def __init__(
        self,
        cluster: Cluster,
        *,
        port: jsii.Number,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hive_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        include_extensions: typing.Optional[builtins.bool] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param cluster: -
        :param port: 
        :param extra_java_options: 
        :param hive_conf: 
        :param include_extensions: (experimental) Include tje .ivy2/jars directory so that the server will pick up extra extensions. Default: true
        :param spark_conf: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784d34b0dce3fbe462c26bf3f7f6264ebbac5607bf8202541d0a1b2a53a7717b)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = JdbcProps(
            port=port,
            extra_java_options=extra_java_options,
            hive_conf=hive_conf,
            include_extensions=include_extensions,
            spark_conf=spark_conf,
        )

        jsii.create(self.__class__, self, [cluster, options])

    @jsii.member(jsii_name="allowFrom")
    def allow_from(self, *connectables: _aws_cdk_aws_ec2_ceddda9d.IConnectable) -> None:
        '''
        :param connectables: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62d169371e3a5aa421799f066dfb490ae95c50dd1910709b0637e97948f7a1c4)
            check_type(argname="argument connectables", value=connectables, expected_type=typing.Tuple[type_hints["connectables"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "allowFrom", [*connectables]))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.JdbcProps",
    jsii_struct_bases=[],
    name_mapping={
        "port": "port",
        "extra_java_options": "extraJavaOptions",
        "hive_conf": "hiveConf",
        "include_extensions": "includeExtensions",
        "spark_conf": "sparkConf",
    },
)
class JdbcProps:
    def __init__(
        self,
        *,
        port: jsii.Number,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hive_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        include_extensions: typing.Optional[builtins.bool] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param port: 
        :param extra_java_options: 
        :param hive_conf: 
        :param include_extensions: (experimental) Include tje .ivy2/jars directory so that the server will pick up extra extensions. Default: true
        :param spark_conf: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fac0fe1d0685f09839aec156e0fdb8fbed92f4a617d1f8d59883ff5eea99d1a3)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument extra_java_options", value=extra_java_options, expected_type=type_hints["extra_java_options"])
            check_type(argname="argument hive_conf", value=hive_conf, expected_type=type_hints["hive_conf"])
            check_type(argname="argument include_extensions", value=include_extensions, expected_type=type_hints["include_extensions"])
            check_type(argname="argument spark_conf", value=spark_conf, expected_type=type_hints["spark_conf"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "port": port,
        }
        if extra_java_options is not None:
            self._values["extra_java_options"] = extra_java_options
        if hive_conf is not None:
            self._values["hive_conf"] = hive_conf
        if include_extensions is not None:
            self._values["include_extensions"] = include_extensions
        if spark_conf is not None:
            self._values["spark_conf"] = spark_conf

    @builtins.property
    def port(self) -> jsii.Number:
        '''
        :see: https://spark.apache.org/docs/latest/sql-distributed-sql-engine.html
        :stability: experimental
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def extra_java_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("extra_java_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def hive_conf(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hive_conf")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def include_extensions(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include tje .ivy2/jars directory so that the server will pick up extra extensions.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("include_extensions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def spark_conf(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("spark_conf")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JdbcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.ManagedScalingPolicy",
    jsii_struct_bases=[],
    name_mapping={"compute_limits": "computeLimits"},
)
class ManagedScalingPolicy:
    def __init__(
        self,
        *,
        compute_limits: typing.Union[ComputeLimits, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param compute_limits: 

        :stability: experimental
        '''
        if isinstance(compute_limits, dict):
            compute_limits = ComputeLimits(**compute_limits)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4affd6995a6e5d5458d74deb9a00af0e126912b1c17740abfd29ffa5a438ff4)
            check_type(argname="argument compute_limits", value=compute_limits, expected_type=type_hints["compute_limits"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "compute_limits": compute_limits,
        }

    @builtins.property
    def compute_limits(self) -> ComputeLimits:
        '''
        :stability: experimental
        '''
        result = self._values.get("compute_limits")
        assert result is not None, "Required property 'compute_limits' is missing"
        return typing.cast(ComputeLimits, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedScalingPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.MetricDimension",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class MetricDimension:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''``MetricDimension`` is a subproperty of the ``CloudWatchAlarmDefinition`` property type.

        ``MetricDimension`` specifies a CloudWatch dimension, which is specified with a ``Key`` ``Value`` pair. The key is known as a ``Name`` in CloudWatch. By default, Amazon EMR uses one dimension whose ``Key`` is ``JobFlowID`` and ``Value`` is a variable representing the cluster ID, which is ``${emr.clusterId}`` . This enables the automatic scaling rule for EMR to bootstrap when the cluster ID becomes available during cluster creation.

        :param key: The dimension name.
        :param value: The dimension value.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-metricdimension.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8077db17f6c7fad8dba95e72ee1e14128f1a9109ee88f2df5a1d94ba8fa2e4a8)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''The dimension name.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-metricdimension.html#cfn-emr-cluster-metricdimension-key
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The dimension value.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-metricdimension.html#cfn-emr-cluster-metricdimension-value
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetricDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.MountFileSystemOptions",
    jsii_struct_bases=[],
    name_mapping={
        "gid": "gid",
        "mount_point": "mountPoint",
        "uid": "uid",
        "username": "username",
    },
)
class MountFileSystemOptions:
    def __init__(
        self,
        *,
        gid: jsii.Number,
        mount_point: builtins.str,
        uid: jsii.Number,
        username: builtins.str,
    ) -> None:
        '''
        :param gid: 
        :param mount_point: 
        :param uid: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f15c666d729817bc139a1898a277a4ba44218aad78c9b75cd0ca318c7f82876)
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
            check_type(argname="argument mount_point", value=mount_point, expected_type=type_hints["mount_point"])
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gid": gid,
            "mount_point": mount_point,
            "uid": uid,
            "username": username,
        }

    @builtins.property
    def gid(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uid(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MountFileSystemOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.NessieECSCatalogProps",
    jsii_struct_bases=[
        BaseNessieRepoProps,
        _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps,
    ],
    name_mapping={
        "catalog_name": "catalogName",
        "default_main_branch": "defaultMainBranch",
        "log_group": "logGroup",
        "removal_policy": "removalPolicy",
        "version_store": "versionStore",
        "warehouse_bucket": "warehouseBucket",
        "warehouse_prefix": "warehousePrefix",
        "capacity_provider_strategies": "capacityProviderStrategies",
        "certificate": "certificate",
        "circuit_breaker": "circuitBreaker",
        "cloud_map_options": "cloudMapOptions",
        "cluster": "cluster",
        "deployment_controller": "deploymentController",
        "desired_count": "desiredCount",
        "domain_name": "domainName",
        "domain_zone": "domainZone",
        "enable_ecs_managed_tags": "enableECSManagedTags",
        "enable_execute_command": "enableExecuteCommand",
        "health_check_grace_period": "healthCheckGracePeriod",
        "idle_timeout": "idleTimeout",
        "listener_port": "listenerPort",
        "load_balancer": "loadBalancer",
        "load_balancer_name": "loadBalancerName",
        "max_healthy_percent": "maxHealthyPercent",
        "min_healthy_percent": "minHealthyPercent",
        "open_listener": "openListener",
        "propagate_tags": "propagateTags",
        "protocol": "protocol",
        "protocol_version": "protocolVersion",
        "public_load_balancer": "publicLoadBalancer",
        "record_type": "recordType",
        "redirect_http": "redirectHTTP",
        "service_name": "serviceName",
        "ssl_policy": "sslPolicy",
        "target_protocol": "targetProtocol",
        "task_image_options": "taskImageOptions",
        "vpc": "vpc",
        "cpu": "cpu",
        "ephemeral_storage_gib": "ephemeralStorageGiB",
        "memory_limit_mib": "memoryLimitMiB",
        "platform_version": "platformVersion",
        "runtime_platform": "runtimePlatform",
        "task_definition": "taskDefinition",
        "assign_public_ip": "assignPublicIp",
        "health_check": "healthCheck",
        "security_groups": "securityGroups",
        "task_subnets": "taskSubnets",
        "dns": "dns",
        "platform": "platform",
    },
)
class NessieECSCatalogProps(
    BaseNessieRepoProps,
    _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps,
):
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        default_main_branch: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        dns: typing.Optional[typing.Union[DNSConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
    ) -> None:
        '''
        :param catalog_name: (experimental) The name of this catalog in the Spark Context. Default: spark_catalog - i.e. the default catalog
        :param default_main_branch: (experimental) The default main branch of a Nessie repository. Default: main
        :param log_group: (experimental) The log group to use for the Nessie service. Default: - a new log group is created for you
        :param removal_policy: (experimental) The removal policy to apply to the Nessie service. Default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.
        :param version_store: (experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.
        :param warehouse_bucket: Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix to use for the warehouse path. Default: - no prefix (e.g. use the root: ``s3://bucket/``)
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param dns: 
        :param platform: 

        :stability: experimental
        '''
        if isinstance(circuit_breaker, dict):
            circuit_breaker = _aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker(**circuit_breaker)
        if isinstance(cloud_map_options, dict):
            cloud_map_options = _aws_cdk_aws_ecs_ceddda9d.CloudMapOptions(**cloud_map_options)
        if isinstance(deployment_controller, dict):
            deployment_controller = _aws_cdk_aws_ecs_ceddda9d.DeploymentController(**deployment_controller)
        if isinstance(task_image_options, dict):
            task_image_options = _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions(**task_image_options)
        if isinstance(runtime_platform, dict):
            runtime_platform = _aws_cdk_aws_ecs_ceddda9d.RuntimePlatform(**runtime_platform)
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_ecs_ceddda9d.HealthCheck(**health_check)
        if isinstance(task_subnets, dict):
            task_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**task_subnets)
        if isinstance(dns, dict):
            dns = DNSConfiguration(**dns)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98c31d2f2930fd529bf754148ceeb46b3270756e8314cb386d0891cfea6439eb)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument default_main_branch", value=default_main_branch, expected_type=type_hints["default_main_branch"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument version_store", value=version_store, expected_type=type_hints["version_store"])
            check_type(argname="argument warehouse_bucket", value=warehouse_bucket, expected_type=type_hints["warehouse_bucket"])
            check_type(argname="argument warehouse_prefix", value=warehouse_prefix, expected_type=type_hints["warehouse_prefix"])
            check_type(argname="argument capacity_provider_strategies", value=capacity_provider_strategies, expected_type=type_hints["capacity_provider_strategies"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument circuit_breaker", value=circuit_breaker, expected_type=type_hints["circuit_breaker"])
            check_type(argname="argument cloud_map_options", value=cloud_map_options, expected_type=type_hints["cloud_map_options"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument deployment_controller", value=deployment_controller, expected_type=type_hints["deployment_controller"])
            check_type(argname="argument desired_count", value=desired_count, expected_type=type_hints["desired_count"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument domain_zone", value=domain_zone, expected_type=type_hints["domain_zone"])
            check_type(argname="argument enable_ecs_managed_tags", value=enable_ecs_managed_tags, expected_type=type_hints["enable_ecs_managed_tags"])
            check_type(argname="argument enable_execute_command", value=enable_execute_command, expected_type=type_hints["enable_execute_command"])
            check_type(argname="argument health_check_grace_period", value=health_check_grace_period, expected_type=type_hints["health_check_grace_period"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument listener_port", value=listener_port, expected_type=type_hints["listener_port"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument load_balancer_name", value=load_balancer_name, expected_type=type_hints["load_balancer_name"])
            check_type(argname="argument max_healthy_percent", value=max_healthy_percent, expected_type=type_hints["max_healthy_percent"])
            check_type(argname="argument min_healthy_percent", value=min_healthy_percent, expected_type=type_hints["min_healthy_percent"])
            check_type(argname="argument open_listener", value=open_listener, expected_type=type_hints["open_listener"])
            check_type(argname="argument propagate_tags", value=propagate_tags, expected_type=type_hints["propagate_tags"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument protocol_version", value=protocol_version, expected_type=type_hints["protocol_version"])
            check_type(argname="argument public_load_balancer", value=public_load_balancer, expected_type=type_hints["public_load_balancer"])
            check_type(argname="argument record_type", value=record_type, expected_type=type_hints["record_type"])
            check_type(argname="argument redirect_http", value=redirect_http, expected_type=type_hints["redirect_http"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument ssl_policy", value=ssl_policy, expected_type=type_hints["ssl_policy"])
            check_type(argname="argument target_protocol", value=target_protocol, expected_type=type_hints["target_protocol"])
            check_type(argname="argument task_image_options", value=task_image_options, expected_type=type_hints["task_image_options"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument ephemeral_storage_gib", value=ephemeral_storage_gib, expected_type=type_hints["ephemeral_storage_gib"])
            check_type(argname="argument memory_limit_mib", value=memory_limit_mib, expected_type=type_hints["memory_limit_mib"])
            check_type(argname="argument platform_version", value=platform_version, expected_type=type_hints["platform_version"])
            check_type(argname="argument runtime_platform", value=runtime_platform, expected_type=type_hints["runtime_platform"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument task_subnets", value=task_subnets, expected_type=type_hints["task_subnets"])
            check_type(argname="argument dns", value=dns, expected_type=type_hints["dns"])
            check_type(argname="argument platform", value=platform, expected_type=type_hints["platform"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if default_main_branch is not None:
            self._values["default_main_branch"] = default_main_branch
        if log_group is not None:
            self._values["log_group"] = log_group
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if version_store is not None:
            self._values["version_store"] = version_store
        if warehouse_bucket is not None:
            self._values["warehouse_bucket"] = warehouse_bucket
        if warehouse_prefix is not None:
            self._values["warehouse_prefix"] = warehouse_prefix
        if capacity_provider_strategies is not None:
            self._values["capacity_provider_strategies"] = capacity_provider_strategies
        if certificate is not None:
            self._values["certificate"] = certificate
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cloud_map_options is not None:
            self._values["cloud_map_options"] = cloud_map_options
        if cluster is not None:
            self._values["cluster"] = cluster
        if deployment_controller is not None:
            self._values["deployment_controller"] = deployment_controller
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if domain_zone is not None:
            self._values["domain_zone"] = domain_zone
        if enable_ecs_managed_tags is not None:
            self._values["enable_ecs_managed_tags"] = enable_ecs_managed_tags
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if health_check_grace_period is not None:
            self._values["health_check_grace_period"] = health_check_grace_period
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if listener_port is not None:
            self._values["listener_port"] = listener_port
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if load_balancer_name is not None:
            self._values["load_balancer_name"] = load_balancer_name
        if max_healthy_percent is not None:
            self._values["max_healthy_percent"] = max_healthy_percent
        if min_healthy_percent is not None:
            self._values["min_healthy_percent"] = min_healthy_percent
        if open_listener is not None:
            self._values["open_listener"] = open_listener
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if protocol is not None:
            self._values["protocol"] = protocol
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if public_load_balancer is not None:
            self._values["public_load_balancer"] = public_load_balancer
        if record_type is not None:
            self._values["record_type"] = record_type
        if redirect_http is not None:
            self._values["redirect_http"] = redirect_http
        if service_name is not None:
            self._values["service_name"] = service_name
        if ssl_policy is not None:
            self._values["ssl_policy"] = ssl_policy
        if target_protocol is not None:
            self._values["target_protocol"] = target_protocol
        if task_image_options is not None:
            self._values["task_image_options"] = task_image_options
        if vpc is not None:
            self._values["vpc"] = vpc
        if cpu is not None:
            self._values["cpu"] = cpu
        if ephemeral_storage_gib is not None:
            self._values["ephemeral_storage_gib"] = ephemeral_storage_gib
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if runtime_platform is not None:
            self._values["runtime_platform"] = runtime_platform
        if task_definition is not None:
            self._values["task_definition"] = task_definition
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if health_check is not None:
            self._values["health_check"] = health_check
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if task_subnets is not None:
            self._values["task_subnets"] = task_subnets
        if dns is not None:
            self._values["dns"] = dns
        if platform is not None:
            self._values["platform"] = platform

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of this catalog in the Spark Context.

        :default: spark_catalog - i.e. the default catalog

        :stability: experimental
        '''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_main_branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The default main branch of a Nessie repository.

        :default: main

        :stability: experimental
        '''
        result = self._values.get("default_main_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) The log group to use for the Nessie service.

        :default: - a new log group is created for you

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply to the Nessie service.

        :default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def version_store(self) -> typing.Optional[DynamoDBNessieVersionStore]:
        '''(experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.

        :stability: experimental
        '''
        result = self._values.get("version_store")
        return typing.cast(typing.Optional[DynamoDBNessieVersionStore], result)

    @builtins.property
    def warehouse_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''
        :default: - one is created for you

        :stability: experimental
        '''
        result = self._values.get("warehouse_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def warehouse_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The prefix to use for the warehouse path.

        :default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        result = self._values.get("warehouse_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capacity_provider_strategies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]]:
        '''A list of Capacity Provider strategies used to place a service.

        :default: - undefined
        '''
        result = self._values.get("capacity_provider_strategies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]], result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''Certificate Manager certificate to associate with the load balancer.

        Setting this option will set the load balancer protocol to HTTPS.

        :default:

        - No certificate associated with the load balancer, if using
        the HTTP protocol. For HTTPS, a DNS-validated certificate will be
        created for the load balancer's specified domain name if a domain name
        and domain zone are specified.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def circuit_breaker(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker]:
        '''Whether to enable the deployment circuit breaker.

        If this property is defined, circuit breaker will be implicitly
        enabled.

        :default: - disabled
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker], result)

    @builtins.property
    def cloud_map_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions]:
        '''The options for configuring an Amazon ECS service to use service discovery.

        :default: - AWS Cloud Map service discovery is not enabled.
        '''
        result = self._values.get("cloud_map_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions], result)

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster]:
        '''The name of the cluster that hosts the service.

        If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc.

        :default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster], result)

    @builtins.property
    def deployment_controller(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController]:
        '''Specifies which deployment controller to use for the service.

        For more information, see
        `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_

        :default: - Rolling update (ECS)
        '''
        result = self._values.get("deployment_controller")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        '''The desired number of instantiations of the task definition to keep running on the service.

        The minimum value is 1

        :default:

        - The default is 1 for all new services and uses the existing service's desired count
        when updating an existing service.
        '''
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''The domain name for the service, e.g. "api.example.com.".

        :default: - No domain name.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''The Route53 hosted zone for the domain, e.g. "example.com.".

        :default: - No Route53 hosted domain zone.
        '''
        result = self._values.get("domain_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def enable_ecs_managed_tags(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether to enable Amazon ECS managed tags for the tasks within the service.

        For more information, see
        `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_

        :default: false
        '''
        result = self._values.get("enable_ecs_managed_tags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether ECS Exec should be enabled.

        :default: - false
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check_grace_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started.

        :default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        '''
        result = self._values.get("health_check_grace_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The load balancer idle timeout, in seconds.

        Can be between 1 and 4000 seconds

        :default: - CloudFormation sets idle timeout to 60 seconds
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def listener_port(self) -> typing.Optional[jsii.Number]:
        '''Listener port of the application load balancer that will serve traffic to the service.

        :default:

        - The default listener port is determined from the protocol (port 80 for HTTP,
        port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        '''
        result = self._values.get("listener_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]:
        '''The application load balancer that will serve traffic to the service.

        The VPC attribute of a load balancer must be specified for it to be used
        to create a new service with this pattern.

        [disable-awslint:ref-via-interface]

        :default: - a new load balancer will be created.
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer], result)

    @builtins.property
    def load_balancer_name(self) -> typing.Optional[builtins.str]:
        '''Name of the load balancer.

        :default: - Automatically generated name.
        '''
        result = self._values.get("load_balancer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

        :default: - 100 if daemon, otherwise 200
        '''
        result = self._values.get("max_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

        :default: - 0 if daemon, otherwise 50
        '''
        result = self._values.get("min_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def open_listener(self) -> typing.Optional[builtins.bool]:
        '''Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default.

        :default: true -- The security group allows ingress from all IP addresses.
        '''
        result = self._values.get("open_listener")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource]:
        '''Specifies whether to propagate the tags from the task definition or the service to the tasks in the service.

        Tags can only be propagated to the tasks within the service during service creation.

        :default: - none
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource], result)

    @builtins.property
    def protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from clients to the load balancer.

        The load balancer port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).  If HTTPS, either a certificate or domain
        name and domain zone must also be specified.

        :default:

        HTTP. If a certificate is specified, the protocol will be
        set by default to HTTPS.
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def protocol_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion]:
        '''The protocol version to use.

        :default: ApplicationProtocolVersion.HTTP1
        '''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion], result)

    @builtins.property
    def public_load_balancer(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the Load Balancer will be internet-facing.

        :default: true
        '''
        result = self._values.get("public_load_balancer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def record_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType]:
        '''Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all.

        This is useful if you need to work with DNS systems that do not support alias records.

        :default: ApplicationLoadBalancedServiceRecordType.ALIAS
        '''
        result = self._values.get("record_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType], result)

    @builtins.property
    def redirect_http(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS.

        :default: false
        '''
        result = self._values.get("redirect_http")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''The name of the service.

        :default: - CloudFormation-generated name.
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy]:
        '''The security policy that defines which ciphers and protocols are supported by the ALB Listener.

        :default: - The recommended elastic load balancing security policy
        '''
        result = self._values.get("ssl_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy], result)

    @builtins.property
    def target_protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from the load balancer to the ECS tasks.

        The default target port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).

        :default: HTTP.
        '''
        result = self._values.get("target_protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def task_image_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions]:
        '''The properties required to create a new task definition.

        TaskDefinition or TaskImageOptions must be specified, but not both.

        :default: none
        '''
        result = self._values.get("task_image_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed.

        If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster.

        :default: - uses the VPC defined in the cluster or creates a new VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''The number of cpu units used by the task.

        Valid values, which determines your range of valid values for the memory parameter:

        256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB

        512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB

        1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB

        2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments

        4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments

        8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments

        16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 256
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ephemeral_storage_gib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in GiB) of ephemeral storage to be allocated to the task.

        The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB.

        Only supported in Fargate platform version 1.4.0 or later.

        :default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        '''
        result = self._values.get("ephemeral_storage_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in MiB) of memory used by the task.

        This field is required and you must use one of the following values, which determines your range of valid values
        for the cpu parameter:

        512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU)

        1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU)

        2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU)

        Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU)

        Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU)

        Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU)

        Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU)

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 512
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion]:
        '''The platform version on which to run your service.

        If one is not specified, the LATEST platform version is used by default. For more information, see
        `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_
        in the Amazon Elastic Container Service Developer Guide.

        :default: Latest
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion], result)

    @builtins.property
    def runtime_platform(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform]:
        '''The runtime platform of the task definition.

        :default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        '''
        result = self._values.get("runtime_platform")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform], result)

    @builtins.property
    def task_definition(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition]:
        '''The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both.

        [disable-awslint:ref-via-interface]

        :default: - none
        '''
        result = self._values.get("task_definition")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition], result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the service will be assigned a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck]:
        '''The health check command and associated configuration parameters for the container.

        :default: - Health check configuration from container.
        '''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the service.

        If you do not specify a security group, a new security group is created.

        :default: - A new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def task_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the service.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("task_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def dns(self) -> typing.Optional[DNSConfiguration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("dns")
        return typing.cast(typing.Optional[DNSConfiguration], result)

    @builtins.property
    def platform(self) -> typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform]:
        '''
        :stability: experimental
        '''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NessieECSCatalogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.NessieLambdaCatalogProps",
    jsii_struct_bases=[BaseNessieRepoProps],
    name_mapping={
        "catalog_name": "catalogName",
        "default_main_branch": "defaultMainBranch",
        "log_group": "logGroup",
        "removal_policy": "removalPolicy",
        "version_store": "versionStore",
        "warehouse_bucket": "warehouseBucket",
        "warehouse_prefix": "warehousePrefix",
    },
)
class NessieLambdaCatalogProps(BaseNessieRepoProps):
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        default_main_branch: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: (experimental) The name of this catalog in the Spark Context. Default: spark_catalog - i.e. the default catalog
        :param default_main_branch: (experimental) The default main branch of a Nessie repository. Default: main
        :param log_group: (experimental) The log group to use for the Nessie service. Default: - a new log group is created for you
        :param removal_policy: (experimental) The removal policy to apply to the Nessie service. Default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.
        :param version_store: (experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.
        :param warehouse_bucket: Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix to use for the warehouse path. Default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6c71cb603e6e9655d9f397972634d1db947ba48130957573e80f35e065776d0)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument default_main_branch", value=default_main_branch, expected_type=type_hints["default_main_branch"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument version_store", value=version_store, expected_type=type_hints["version_store"])
            check_type(argname="argument warehouse_bucket", value=warehouse_bucket, expected_type=type_hints["warehouse_bucket"])
            check_type(argname="argument warehouse_prefix", value=warehouse_prefix, expected_type=type_hints["warehouse_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if default_main_branch is not None:
            self._values["default_main_branch"] = default_main_branch
        if log_group is not None:
            self._values["log_group"] = log_group
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if version_store is not None:
            self._values["version_store"] = version_store
        if warehouse_bucket is not None:
            self._values["warehouse_bucket"] = warehouse_bucket
        if warehouse_prefix is not None:
            self._values["warehouse_prefix"] = warehouse_prefix

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of this catalog in the Spark Context.

        :default: spark_catalog - i.e. the default catalog

        :stability: experimental
        '''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_main_branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The default main branch of a Nessie repository.

        :default: main

        :stability: experimental
        '''
        result = self._values.get("default_main_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) The log group to use for the Nessie service.

        :default: - a new log group is created for you

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) The removal policy to apply to the Nessie service.

        :default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def version_store(self) -> typing.Optional[DynamoDBNessieVersionStore]:
        '''(experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.

        :stability: experimental
        '''
        result = self._values.get("version_store")
        return typing.cast(typing.Optional[DynamoDBNessieVersionStore], result)

    @builtins.property
    def warehouse_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''
        :default: - one is created for you

        :stability: experimental
        '''
        result = self._values.get("warehouse_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def warehouse_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The prefix to use for the warehouse path.

        :default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        result = self._values.get("warehouse_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NessieLambdaCatalogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.NessieVersionStoreProps",
    jsii_struct_bases=[],
    name_mapping={
        "removal_policy": "removalPolicy",
        "version_store_name": "versionStoreName",
    },
)
class NessieVersionStoreProps:
    def __init__(
        self,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param removal_policy: Default: - RemovalPolicy.DESTROY
        :param version_store_name: (experimental) Nessie has two tables, ``objs`` and ``refs``. Nessie supports configuring a "prefix" that will be used to determine the names of these tables. Default: - "nessie"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c90f21257ff6c373cd9b8bed683c0af254fb7c1339068d939b967ab65560880)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument version_store_name", value=version_store_name, expected_type=type_hints["version_store_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if version_store_name is not None:
            self._values["version_store_name"] = version_store_name

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :default: - RemovalPolicy.DESTROY

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def version_store_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Nessie has two tables, ``objs`` and ``refs``.

        Nessie supports configuring a "prefix" that will be used to determine the names of these tables.

        :default: - "nessie"

        :see: https://project-nessie.zulipchat.com/#narrow/stream/371187-general/topic/AWS.20Lambda.20with.20SnapStart/near/420329834
        :stability: experimental
        '''
        result = self._values.get("version_store_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NessieVersionStoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.PosixGroup",
    jsii_struct_bases=[],
    name_mapping={"gid": "gid", "name": "name"},
)
class PosixGroup:
    def __init__(self, *, gid: jsii.Number, name: builtins.str) -> None:
        '''(experimental) A statically defined POSIX Group.

        :param gid: (experimental) Unique ID of the POSIX group.
        :param name: (experimental) Unique name of the POSIX group.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4dd8a0c8155f1e29163bfa4e608e4468e4b804af5e46a20deccff38cbc24cc7)
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gid": gid,
            "name": name,
        }

    @builtins.property
    def gid(self) -> jsii.Number:
        '''(experimental) Unique ID of the POSIX group.

        :stability: experimental
        '''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Unique name of the POSIX group.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PosixGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.PrimaryInstanceGroup",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "name": "name",
        "auto_scaling_policy": "autoScalingPolicy",
        "bid_price": "bidPrice",
        "configurations": "configurations",
        "custom_ami": "customAmi",
        "ebs_block_devices": "ebsBlockDevices",
        "ebs_optimized": "ebsOptimized",
        "instance_count": "instanceCount",
        "market": "market",
    },
)
class PrimaryInstanceGroup:
    def __init__(
        self,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        name: builtins.str,
        auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        bid_price: typing.Optional[builtins.str] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
        custom_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
        ebs_block_devices: typing.Optional[typing.Sequence[typing.Union[EbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        market: typing.Optional[InstanceMarket] = None,
    ) -> None:
        '''
        :param instance_type: (experimental) The Amazon EC2 instance type for all instances in the instance group.
        :param name: (experimental) Friendly name given to the instance group.
        :param auto_scaling_policy: (experimental) ``AutoScalingPolicy`` is a subproperty of the `InstanceGroupConfig <https://docs.aws.amazon.com//AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig-instancegroupconfig.html>`_ property type that specifies the constraints and rules of an automatic scaling policy in Amazon EMR . The automatic scaling policy defines how an instance group dynamically adds and terminates EC2 instances in response to the value of a CloudWatch metric. Only core and task instance groups can use automatic scaling policies. For more information, see `Using Automatic Scaling in Amazon EMR <https://docs.aws.amazon.com//emr/latest/ManagementGuide/emr-automatic-scaling.html>`_ .
        :param bid_price: (experimental) If specified, indicates that the instance group uses Spot Instances. This is the maximum price you are willing to pay for Spot Instances. Specify ``OnDemandPrice`` to set the amount equal to the On-Demand price, or specify an amount in USD.
        :param configurations: (experimental) > Amazon EMR releases 4.x or later. The list of configurations supplied for an Amazon EMR cluster instance group. You can specify a separate configuration for each instance group (master, core, and task).
        :param custom_ami: (experimental) The custom AMI ID to use for the provisioned instance group.
        :param ebs_block_devices: (experimental) EBS {@link EbsBlockDevice}s to attach to an instance in an {@link InstanceFleet }. Default: - No EBS block devices
        :param ebs_optimized: (experimental) An Amazon EBS–optimized instance uses an optimized configuration stack and provides additional, dedicated capacity for Amazon EBS I/O. This optimization provides the best performance for your EBS volumes by minimizing contention between Amazon EBS I/O and other traffic from your instance. **Note**: .. epigraph:: For Current Generation Instance types, EBS-optimization is enabled by default at no additional cost. For Previous Generation Instances types, EBS-optimization prices are on the Previous Generation Pricing Page. Default: true
        :param instance_count: (experimental) Number of instances in the Primary {@link InstanceGroup}. TODO: I need to validate if there can be more than 1 primary instance group. Default: 1
        :param market: (experimental) Market type of the Amazon EC2 instances used to create a cluster node.

        :stability: experimental
        '''
        if isinstance(auto_scaling_policy, dict):
            auto_scaling_policy = AutoScalingPolicy(**auto_scaling_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__383e1ad4836b4415ffda8afef3eaf4b449d1c46d873c9c7157bbbb2775717e14)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument auto_scaling_policy", value=auto_scaling_policy, expected_type=type_hints["auto_scaling_policy"])
            check_type(argname="argument bid_price", value=bid_price, expected_type=type_hints["bid_price"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
            check_type(argname="argument custom_ami", value=custom_ami, expected_type=type_hints["custom_ami"])
            check_type(argname="argument ebs_block_devices", value=ebs_block_devices, expected_type=type_hints["ebs_block_devices"])
            check_type(argname="argument ebs_optimized", value=ebs_optimized, expected_type=type_hints["ebs_optimized"])
            check_type(argname="argument instance_count", value=instance_count, expected_type=type_hints["instance_count"])
            check_type(argname="argument market", value=market, expected_type=type_hints["market"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
            "name": name,
        }
        if auto_scaling_policy is not None:
            self._values["auto_scaling_policy"] = auto_scaling_policy
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if configurations is not None:
            self._values["configurations"] = configurations
        if custom_ami is not None:
            self._values["custom_ami"] = custom_ami
        if ebs_block_devices is not None:
            self._values["ebs_block_devices"] = ebs_block_devices
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if instance_count is not None:
            self._values["instance_count"] = instance_count
        if market is not None:
            self._values["market"] = market

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''(experimental) The Amazon EC2 instance type for all instances in the instance group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-instancetype
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Friendly name given to the instance group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-name
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_scaling_policy(self) -> typing.Optional[AutoScalingPolicy]:
        '''(experimental) ``AutoScalingPolicy`` is a subproperty of the `InstanceGroupConfig <https://docs.aws.amazon.com//AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig-instancegroupconfig.html>`_ property type that specifies the constraints and rules of an automatic scaling policy in Amazon EMR . The automatic scaling policy defines how an instance group dynamically adds and terminates EC2 instances in response to the value of a CloudWatch metric. Only core and task instance groups can use automatic scaling policies. For more information, see `Using Automatic Scaling in Amazon EMR <https://docs.aws.amazon.com//emr/latest/ManagementGuide/emr-automatic-scaling.html>`_ .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-autoscalingpolicy
        :stability: experimental
        '''
        result = self._values.get("auto_scaling_policy")
        return typing.cast(typing.Optional[AutoScalingPolicy], result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''(experimental) If specified, indicates that the instance group uses Spot Instances.

        This is the maximum price you are willing to pay for Spot Instances. Specify ``OnDemandPrice`` to set the amount equal to the On-Demand price, or specify an amount in USD.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-bidprice
        :stability: experimental
        '''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List[Configuration]]:
        '''(experimental) > Amazon EMR releases 4.x or later.

        The list of configurations supplied for an Amazon EMR cluster instance group. You can specify a separate configuration for each instance group (master, core, and task).

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-configurations
        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List[Configuration]], result)

    @builtins.property
    def custom_ami(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage]:
        '''(experimental) The custom AMI ID to use for the provisioned instance group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-customamiid
        :stability: experimental
        '''
        result = self._values.get("custom_ami")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage], result)

    @builtins.property
    def ebs_block_devices(self) -> typing.Optional[typing.List[EbsBlockDevice]]:
        '''(experimental) EBS {@link EbsBlockDevice}s to attach to an instance in an {@link InstanceFleet }.

        :default: - No EBS block devices

        :stability: experimental
        '''
        result = self._values.get("ebs_block_devices")
        return typing.cast(typing.Optional[typing.List[EbsBlockDevice]], result)

    @builtins.property
    def ebs_optimized(self) -> typing.Optional[builtins.bool]:
        '''(experimental) An Amazon EBS–optimized instance uses an optimized configuration stack and provides additional, dedicated capacity for Amazon EBS I/O.

        This
        optimization provides the best performance for your EBS volumes by minimizing
        contention between Amazon EBS I/O and other traffic from your instance.

        **Note**:
        .. epigraph::

           For Current Generation Instance types, EBS-optimization is enabled by default at no additional cost. For Previous Generation Instances types, EBS-optimization prices are on the Previous Generation Pricing Page.

        :default: true

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-optimized.html
        :stability: experimental
        '''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of instances in the Primary {@link InstanceGroup}.

        TODO: I need to validate if there can be more than 1 primary instance group.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def market(self) -> typing.Optional[InstanceMarket]:
        '''(experimental) Market type of the Amazon EC2 instances used to create a cluster node.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-instancegroupconfig.html#cfn-emr-cluster-instancegroupconfig-market
        :stability: experimental
        '''
        result = self._values.get("market")
        return typing.cast(typing.Optional[InstanceMarket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrimaryInstanceGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.PythonPoetryArgs",
    jsii_struct_bases=[],
    name_mapping={
        "all_extras": "allExtras",
        "dev": "dev",
        "exclude": "exclude",
        "include": "include",
        "without_hashes": "withoutHashes",
        "without_urls": "withoutUrls",
    },
)
class PythonPoetryArgs:
    def __init__(
        self,
        *,
        all_extras: typing.Optional[builtins.bool] = None,
        dev: typing.Optional[builtins.bool] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
        without_hashes: typing.Optional[builtins.bool] = None,
        without_urls: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param all_extras: 
        :param dev: 
        :param exclude: 
        :param include: 
        :param without_hashes: 
        :param without_urls: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbe524884870ca65c48adab2502dfd388d957f47d677bd55844748044805aec3)
            check_type(argname="argument all_extras", value=all_extras, expected_type=type_hints["all_extras"])
            check_type(argname="argument dev", value=dev, expected_type=type_hints["dev"])
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
            check_type(argname="argument without_hashes", value=without_hashes, expected_type=type_hints["without_hashes"])
            check_type(argname="argument without_urls", value=without_urls, expected_type=type_hints["without_urls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if all_extras is not None:
            self._values["all_extras"] = all_extras
        if dev is not None:
            self._values["dev"] = dev
        if exclude is not None:
            self._values["exclude"] = exclude
        if include is not None:
            self._values["include"] = include
        if without_hashes is not None:
            self._values["without_hashes"] = without_hashes
        if without_urls is not None:
            self._values["without_urls"] = without_urls

    @builtins.property
    def all_extras(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("all_extras")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("dev")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def without_hashes(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("without_hashes")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def without_urls(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("without_urls")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonPoetryArgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReleaseLabel(metaclass=jsii.JSIIMeta, jsii_type="@packyak/aws-cdk.ReleaseLabel"):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        label: builtins.str,
        spark_version: "SparkVersion",
        python_version: "PythonVersion",
        scala_version: "ScalaVersion",
    ) -> None:
        '''
        :param label: -
        :param spark_version: -
        :param python_version: -
        :param scala_version: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64fd11a40a56ac99a11e46ec1b209f77e1d100ce52c646b4bd35654c477f5707)
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument spark_version", value=spark_version, expected_type=type_hints["spark_version"])
            check_type(argname="argument python_version", value=python_version, expected_type=type_hints["python_version"])
            check_type(argname="argument scala_version", value=scala_version, expected_type=type_hints["scala_version"])
        jsii.create(self.__class__, self, [label, spark_version, python_version, scala_version])

    @jsii.python.classproperty
    @jsii.member(jsii_name="EMR_6")
    def EMR_6(cls) -> "ReleaseLabel":
        '''
        :stability: experimental
        '''
        return typing.cast("ReleaseLabel", jsii.sget(cls, "EMR_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EMR_6_15_0")
    def EMR_6_15_0(cls) -> "ReleaseLabel":
        '''
        :stability: experimental
        '''
        return typing.cast("ReleaseLabel", jsii.sget(cls, "EMR_6_15_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EMR_7_0_0")
    def EMR_7_0_0(cls) -> "ReleaseLabel":
        '''
        :stability: experimental
        '''
        return typing.cast("ReleaseLabel", jsii.sget(cls, "EMR_7_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="LATEST")
    def LATEST(cls) -> "ReleaseLabel":
        '''
        :stability: experimental
        '''
        return typing.cast("ReleaseLabel", jsii.sget(cls, "LATEST"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @builtins.property
    @jsii.member(jsii_name="majorVersion")
    def major_version(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "majorVersion"))

    @builtins.property
    @jsii.member(jsii_name="pythonVersion")
    def python_version(self) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.get(self, "pythonVersion"))

    @builtins.property
    @jsii.member(jsii_name="scalaVersion")
    def scala_version(self) -> "ScalaVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("ScalaVersion", jsii.get(self, "scalaVersion"))

    @builtins.property
    @jsii.member(jsii_name="sparkVersion")
    def spark_version(self) -> "SparkVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("SparkVersion", jsii.get(self, "sparkVersion"))


class SageMakerImage(
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.SageMakerImage",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        resource_id: builtins.str,
        image_type: "SageMakerImageType",
    ) -> None:
        '''
        :param resource_id: -
        :param image_type: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e1ed4f69faebd9388d4951836ce7bd7c02d994160af437df9300fdeeef90643)
            check_type(argname="argument resource_id", value=resource_id, expected_type=type_hints["resource_id"])
            check_type(argname="argument image_type", value=image_type, expected_type=type_hints["image_type"])
        jsii.create(self.__class__, self, [resource_id, image_type])

    @jsii.member(jsii_name="getArnForStack")
    def get_arn_for_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> builtins.str:
        '''
        :param stack: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24947d6fc0a5dc9cc009b6d476f771725b3ffce98fd89e63f88d9e93a459b240)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(builtins.str, jsii.invoke(self, "getArnForStack", [stack]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CPU_V0")
    def CPU_V0(cls) -> "SageMakerImage":
        '''
        :stability: experimental
        '''
        return typing.cast("SageMakerImage", jsii.sget(cls, "CPU_V0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CPU_V1")
    def CPU_V1(cls) -> "SageMakerImage":
        '''
        :stability: experimental
        '''
        return typing.cast("SageMakerImage", jsii.sget(cls, "CPU_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GPU_V0")
    def GPU_V0(cls) -> "SageMakerImage":
        '''
        :stability: experimental
        '''
        return typing.cast("SageMakerImage", jsii.sget(cls, "GPU_V0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GPU_V1")
    def GPU_V1(cls) -> "SageMakerImage":
        '''
        :stability: experimental
        '''
        return typing.cast("SageMakerImage", jsii.sget(cls, "GPU_V1"))


@jsii.enum(jsii_type="@packyak/aws-cdk.SageMakerImageType")
class SageMakerImageType(enum.Enum):
    '''
    :stability: experimental
    '''

    DISTRIBUTION = "DISTRIBUTION"
    '''
    :stability: experimental
    '''
    IMAGE = "IMAGE"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@packyak/aws-cdk.ScaleDownBehavior")
class ScaleDownBehavior(enum.Enum):
    '''
    :stability: experimental
    '''

    TERMINATE_AT_INSTANCE_HOUR = "TERMINATE_AT_INSTANCE_HOUR"
    '''
    :stability: experimental
    '''
    TERMINATE_AT_TASK_COMPLETION = "TERMINATE_AT_TASK_COMPLETION"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.ScalingAction",
    jsii_struct_bases=[],
    name_mapping={
        "simple_scaling_policy_configuration": "simpleScalingPolicyConfiguration",
        "market": "market",
    },
)
class ScalingAction:
    def __init__(
        self,
        *,
        simple_scaling_policy_configuration: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union["SimpleScalingPolicy", typing.Dict[builtins.str, typing.Any]]],
        market: typing.Optional[InstanceMarket] = None,
    ) -> None:
        '''``ScalingAction`` determines the type of adjustment the automatic scaling activity makes when triggered, and the periodicity of the adjustment.

        :param simple_scaling_policy_configuration: The type of adjustment the automatic scaling activity makes when triggered, and the periodicity of the adjustment.
        :param market: Not available for instance groups. Instance groups use the market type specified for the group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingaction.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82c40f0441842fc84af2f238149188b8b8ec95a2db22879d82ae48e66675562b)
            check_type(argname="argument simple_scaling_policy_configuration", value=simple_scaling_policy_configuration, expected_type=type_hints["simple_scaling_policy_configuration"])
            check_type(argname="argument market", value=market, expected_type=type_hints["market"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "simple_scaling_policy_configuration": simple_scaling_policy_configuration,
        }
        if market is not None:
            self._values["market"] = market

    @builtins.property
    def simple_scaling_policy_configuration(
        self,
    ) -> typing.Union[_aws_cdk_ceddda9d.IResolvable, "SimpleScalingPolicy"]:
        '''The type of adjustment the automatic scaling activity makes when triggered, and the periodicity of the adjustment.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingaction.html#cfn-emr-cluster-scalingaction-simplescalingpolicyconfiguration
        '''
        result = self._values.get("simple_scaling_policy_configuration")
        assert result is not None, "Required property 'simple_scaling_policy_configuration' is missing"
        return typing.cast(typing.Union[_aws_cdk_ceddda9d.IResolvable, "SimpleScalingPolicy"], result)

    @builtins.property
    def market(self) -> typing.Optional[InstanceMarket]:
        '''Not available for instance groups.

        Instance groups use the market type specified for the group.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingaction.html#cfn-emr-cluster-scalingaction-market
        '''
        result = self._values.get("market")
        return typing.cast(typing.Optional[InstanceMarket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScalingAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.ScalingConstraints",
    jsii_struct_bases=[],
    name_mapping={"max_capacity": "maxCapacity", "min_capacity": "minCapacity"},
)
class ScalingConstraints:
    def __init__(self, *, max_capacity: jsii.Number, min_capacity: jsii.Number) -> None:
        '''``ScalingConstraints`` is a subproperty of the ``AutoScalingPolicy`` property type.

        ``ScalingConstraints`` defines the upper and lower EC2 instance limits for an automatic scaling policy. Automatic scaling activities triggered by automatic scaling rules will not cause an instance group to grow above or shrink below these limits.

        :param max_capacity: The upper boundary of Amazon EC2 instances in an instance group beyond which scaling activities are not allowed to grow. Scale-out activities will not add instances beyond this boundary.
        :param min_capacity: The lower boundary of Amazon EC2 instances in an instance group below which scaling activities are not allowed to shrink. Scale-in activities will not terminate instances below this boundary.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingconstraints.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0493b6264f42490efa4439290de4d281d9b44190041d5e565eaaabfdd57a5d0)
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_capacity", value=min_capacity, expected_type=type_hints["min_capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_capacity": max_capacity,
            "min_capacity": min_capacity,
        }

    @builtins.property
    def max_capacity(self) -> jsii.Number:
        '''The upper boundary of Amazon EC2 instances in an instance group beyond which scaling activities are not allowed to grow.

        Scale-out activities will not add instances beyond this boundary.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingconstraints.html#cfn-emr-cluster-scalingconstraints-maxcapacity
        '''
        result = self._values.get("max_capacity")
        assert result is not None, "Required property 'max_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_capacity(self) -> jsii.Number:
        '''The lower boundary of Amazon EC2 instances in an instance group below which scaling activities are not allowed to shrink.

        Scale-in activities will not terminate instances below this boundary.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingconstraints.html#cfn-emr-cluster-scalingconstraints-mincapacity
        '''
        result = self._values.get("min_capacity")
        assert result is not None, "Required property 'min_capacity' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScalingConstraints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.ScalingRule",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "name": "name",
        "trigger": "trigger",
        "description": "description",
    },
)
class ScalingRule:
    def __init__(
        self,
        *,
        action: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[ScalingAction, typing.Dict[builtins.str, typing.Any]]],
        name: builtins.str,
        trigger: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union["ScalingTrigger", typing.Dict[builtins.str, typing.Any]]],
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''``ScalingRule`` is a subproperty of the ``AutoScalingPolicy`` property type.

        ``ScalingRule`` defines the scale-in or scale-out rules for scaling activity, including the CloudWatch metric alarm that triggers activity, how EC2 instances are added or removed, and the periodicity of adjustments. The automatic scaling policy for an instance group can comprise one or more automatic scaling rules.

        :param action: The conditions that trigger an automatic scaling activity.
        :param name: The name used to identify an automatic scaling rule. Rule names must be unique within a scaling policy.
        :param trigger: The CloudWatch alarm definition that determines when automatic scaling activity is triggered.
        :param description: A friendly, more verbose description of the automatic scaling rule.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingrule.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b782ace7defba201794dcced4fc8267ec88fcdb67ea24dc5c4eb961d7c82136)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument trigger", value=trigger, expected_type=type_hints["trigger"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "name": name,
            "trigger": trigger,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def action(self) -> typing.Union[_aws_cdk_ceddda9d.IResolvable, ScalingAction]:
        '''The conditions that trigger an automatic scaling activity.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingrule.html#cfn-emr-cluster-scalingrule-action
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(typing.Union[_aws_cdk_ceddda9d.IResolvable, ScalingAction], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name used to identify an automatic scaling rule.

        Rule names must be unique within a scaling policy.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingrule.html#cfn-emr-cluster-scalingrule-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def trigger(self) -> typing.Union[_aws_cdk_ceddda9d.IResolvable, "ScalingTrigger"]:
        '''The CloudWatch alarm definition that determines when automatic scaling activity is triggered.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingrule.html#cfn-emr-cluster-scalingrule-trigger
        '''
        result = self._values.get("trigger")
        assert result is not None, "Required property 'trigger' is missing"
        return typing.cast(typing.Union[_aws_cdk_ceddda9d.IResolvable, "ScalingTrigger"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A friendly, more verbose description of the automatic scaling rule.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingrule.html#cfn-emr-cluster-scalingrule-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScalingRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.ScalingTrigger",
    jsii_struct_bases=[],
    name_mapping={"cloud_watch_alarm_definition": "cloudWatchAlarmDefinition"},
)
class ScalingTrigger:
    def __init__(
        self,
        *,
        cloud_watch_alarm_definition: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CloudWatchAlarmDefinition, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''``ScalingTrigger`` is a subproperty of the ``ScalingRule`` property type.

        ``ScalingTrigger`` determines the conditions that trigger an automatic scaling activity.

        :param cloud_watch_alarm_definition: The definition of a CloudWatch metric alarm. When the defined alarm conditions are met along with other trigger parameters, scaling activity begins.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingtrigger.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67beae64caa09b21144afee8e7168cb51a0c6adb9c532d1ebd8372af22e65571)
            check_type(argname="argument cloud_watch_alarm_definition", value=cloud_watch_alarm_definition, expected_type=type_hints["cloud_watch_alarm_definition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cloud_watch_alarm_definition": cloud_watch_alarm_definition,
        }

    @builtins.property
    def cloud_watch_alarm_definition(
        self,
    ) -> typing.Union[_aws_cdk_ceddda9d.IResolvable, CloudWatchAlarmDefinition]:
        '''The definition of a CloudWatch metric alarm.

        When the defined alarm conditions are met along with other trigger parameters, scaling activity begins.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-scalingtrigger.html#cfn-emr-cluster-scalingtrigger-cloudwatchalarmdefinition
        '''
        result = self._values.get("cloud_watch_alarm_definition")
        assert result is not None, "Required property 'cloud_watch_alarm_definition' is missing"
        return typing.cast(typing.Union[_aws_cdk_ceddda9d.IResolvable, CloudWatchAlarmDefinition], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScalingTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.SimpleScalingPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "scaling_adjustment": "scalingAdjustment",
        "adjustment_type": "adjustmentType",
        "cool_down": "coolDown",
    },
)
class SimpleScalingPolicy:
    def __init__(
        self,
        *,
        scaling_adjustment: jsii.Number,
        adjustment_type: typing.Optional[AdjustmentType] = None,
        cool_down: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''``SimpleScalingPolicyConfiguration`` is a subproperty of the ``ScalingAction`` property type.

        ``SimpleScalingPolicyConfiguration`` determines how an automatic scaling action adds or removes instances, the cooldown period, and the number of EC2 instances that are added each time the CloudWatch metric alarm condition is satisfied.

        :param scaling_adjustment: The amount by which to scale in or scale out, based on the specified ``AdjustmentType`` . A positive value adds to the instance group's Amazon EC2 instance count while a negative number removes instances. If ``AdjustmentType`` is set to ``EXACT_CAPACITY`` , the number should only be a positive integer. If ``AdjustmentType`` is set to ``PERCENT_CHANGE_IN_CAPACITY`` , the value should express the percentage as an integer. For example, -20 indicates a decrease in 20% increments of cluster capacity.
        :param adjustment_type: The way in which Amazon EC2 instances are added (if ``ScalingAdjustment`` is a positive number) or terminated (if ``ScalingAdjustment`` is a negative number) each time the scaling activity is triggered. ``CHANGE_IN_CAPACITY`` indicates that the Amazon EC2 instance count increments or decrements by ``ScalingAdjustment`` , which should be expressed as an integer. ``PERCENT_CHANGE_IN_CAPACITY`` indicates the instance count increments or decrements by the percentage specified by ``ScalingAdjustment`` , which should be expressed as an integer. For example, 20 indicates an increase in 20% increments of cluster capacity. ``EXACT_CAPACITY`` indicates the scaling activity results in an instance group with the number of Amazon EC2 instances specified by ``ScalingAdjustment`` , which should be expressed as a positive integer. Default: AdjustmentType.CHANGE_IN_CAPACITY
        :param cool_down: The amount of time, in seconds, after a scaling activity completes before any further trigger-related scaling activities can start.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-simplescalingpolicyconfiguration.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54ddc62c0cddb203ed5c1373cc8509449a60b05b0f5d6c12436ebee720305446)
            check_type(argname="argument scaling_adjustment", value=scaling_adjustment, expected_type=type_hints["scaling_adjustment"])
            check_type(argname="argument adjustment_type", value=adjustment_type, expected_type=type_hints["adjustment_type"])
            check_type(argname="argument cool_down", value=cool_down, expected_type=type_hints["cool_down"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "scaling_adjustment": scaling_adjustment,
        }
        if adjustment_type is not None:
            self._values["adjustment_type"] = adjustment_type
        if cool_down is not None:
            self._values["cool_down"] = cool_down

    @builtins.property
    def scaling_adjustment(self) -> jsii.Number:
        '''The amount by which to scale in or scale out, based on the specified ``AdjustmentType`` .

        A positive value adds to the instance group's Amazon EC2 instance count while a negative number removes instances. If ``AdjustmentType`` is set to ``EXACT_CAPACITY`` , the number should only be a positive integer. If ``AdjustmentType`` is set to ``PERCENT_CHANGE_IN_CAPACITY`` , the value should express the percentage as an integer. For example, -20 indicates a decrease in 20% increments of cluster capacity.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-simplescalingpolicyconfiguration.html#cfn-emr-cluster-simplescalingpolicyconfiguration-scalingadjustment
        '''
        result = self._values.get("scaling_adjustment")
        assert result is not None, "Required property 'scaling_adjustment' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def adjustment_type(self) -> typing.Optional[AdjustmentType]:
        '''The way in which Amazon EC2 instances are added (if ``ScalingAdjustment`` is a positive number) or terminated (if ``ScalingAdjustment`` is a negative number) each time the scaling activity is triggered.

        ``CHANGE_IN_CAPACITY`` indicates that the Amazon EC2 instance count increments or decrements by ``ScalingAdjustment`` , which should be expressed as an integer. ``PERCENT_CHANGE_IN_CAPACITY`` indicates the instance count increments or decrements by the percentage specified by ``ScalingAdjustment`` , which should be expressed as an integer. For example, 20 indicates an increase in 20% increments of cluster capacity. ``EXACT_CAPACITY`` indicates the scaling activity results in an instance group with the number of Amazon EC2 instances specified by ``ScalingAdjustment`` , which should be expressed as a positive integer.

        :default: AdjustmentType.CHANGE_IN_CAPACITY

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-simplescalingpolicyconfiguration.html#cfn-emr-cluster-simplescalingpolicyconfiguration-adjustmenttype
        '''
        result = self._values.get("adjustment_type")
        return typing.cast(typing.Optional[AdjustmentType], result)

    @builtins.property
    def cool_down(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in seconds, after a scaling activity completes before any further trigger-related scaling activities can start.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-simplescalingpolicyconfiguration.html#cfn-emr-cluster-simplescalingpolicyconfiguration-cooldown
        '''
        result = self._values.get("cool_down")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SimpleScalingPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.Step",
    jsii_struct_bases=[_aws_cdk_aws_emr_ceddda9d.CfnCluster.StepConfigProperty],
    name_mapping={
        "hadoop_jar_step": "hadoopJarStep",
        "name": "name",
        "action_on_failure": "actionOnFailure",
    },
)
class Step(_aws_cdk_aws_emr_ceddda9d.CfnCluster.StepConfigProperty):
    def __init__(
        self,
        *,
        hadoop_jar_step: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emr_ceddda9d.CfnCluster.HadoopJarStepConfigProperty, typing.Dict[builtins.str, typing.Any]]],
        name: builtins.str,
        action_on_failure: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hadoop_jar_step: The JAR file used for the step.
        :param name: The name of the step.
        :param action_on_failure: The action to take when the cluster step fails. Possible values are ``CANCEL_AND_WAIT`` and ``CONTINUE`` .

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1ce8be45455ac9eb169db10448fccf280b2b4bc8ccaae864952c43b4a254c34)
            check_type(argname="argument hadoop_jar_step", value=hadoop_jar_step, expected_type=type_hints["hadoop_jar_step"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument action_on_failure", value=action_on_failure, expected_type=type_hints["action_on_failure"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hadoop_jar_step": hadoop_jar_step,
            "name": name,
        }
        if action_on_failure is not None:
            self._values["action_on_failure"] = action_on_failure

    @builtins.property
    def hadoop_jar_step(
        self,
    ) -> typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emr_ceddda9d.CfnCluster.HadoopJarStepConfigProperty]:
        '''The JAR file used for the step.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-stepconfig.html#cfn-emr-cluster-stepconfig-hadoopjarstep
        '''
        result = self._values.get("hadoop_jar_step")
        assert result is not None, "Required property 'hadoop_jar_step' is missing"
        return typing.cast(typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emr_ceddda9d.CfnCluster.HadoopJarStepConfigProperty], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the step.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-stepconfig.html#cfn-emr-cluster-stepconfig-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_on_failure(self) -> typing.Optional[builtins.str]:
        '''The action to take when the cluster step fails.

        Possible values are ``CANCEL_AND_WAIT`` and ``CONTINUE`` .

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-stepconfig.html#cfn-emr-cluster-stepconfig-actiononfailure
        '''
        result = self._values.get("action_on_failure")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Step(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamlitSite(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.StreamlitSite",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        home: builtins.str,
        dockerfile: typing.Optional[builtins.str] = None,
        platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
        python_poetry_args: typing.Optional[typing.Union[PythonPoetryArgs, typing.Dict[builtins.str, typing.Any]]] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param home: (experimental) Entrypoint to the streamlit application.
        :param dockerfile: (experimental) The name of the Dockerfile to use to build this Streamlit site. Default: "Dockerfile"
        :param platform: (experimental) The platform to use to build this Streamlit site. Default: {@link Platform.LINUX_AMD64 }
        :param python_poetry_args: (experimental) Override how the ``requirements.txt`` file is generated with Python Poetry. Default: - see {@link exportRequirementsSync }
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080175f818a8350c34bed3f38ee75e2eb119e92ec7de4456fb5d9c13b4ba04ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StreamlitSiteProps(
            home=home,
            dockerfile=dockerfile,
            platform=platform,
            python_poetry_args=python_poetry_args,
            assign_public_ip=assign_public_ip,
            health_check=health_check,
            security_groups=security_groups,
            task_subnets=task_subnets,
            capacity_provider_strategies=capacity_provider_strategies,
            certificate=certificate,
            circuit_breaker=circuit_breaker,
            cloud_map_options=cloud_map_options,
            cluster=cluster,
            deployment_controller=deployment_controller,
            desired_count=desired_count,
            domain_name=domain_name,
            domain_zone=domain_zone,
            enable_ecs_managed_tags=enable_ecs_managed_tags,
            enable_execute_command=enable_execute_command,
            health_check_grace_period=health_check_grace_period,
            idle_timeout=idle_timeout,
            listener_port=listener_port,
            load_balancer=load_balancer,
            load_balancer_name=load_balancer_name,
            max_healthy_percent=max_healthy_percent,
            min_healthy_percent=min_healthy_percent,
            open_listener=open_listener,
            propagate_tags=propagate_tags,
            protocol=protocol,
            protocol_version=protocol_version,
            public_load_balancer=public_load_balancer,
            record_type=record_type,
            redirect_http=redirect_http,
            service_name=service_name,
            ssl_policy=ssl_policy,
            target_protocol=target_protocol,
            task_image_options=task_image_options,
            vpc=vpc,
            cpu=cpu,
            ephemeral_storage_gib=ephemeral_storage_gib,
            memory_limit_mib=memory_limit_mib,
            platform_version=platform_version,
            runtime_platform=runtime_platform,
            task_definition=task_definition,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(
        self,
    ) -> _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateService:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateService, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.StreamlitSiteProps",
    jsii_struct_bases=[
        _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps
    ],
    name_mapping={
        "capacity_provider_strategies": "capacityProviderStrategies",
        "certificate": "certificate",
        "circuit_breaker": "circuitBreaker",
        "cloud_map_options": "cloudMapOptions",
        "cluster": "cluster",
        "deployment_controller": "deploymentController",
        "desired_count": "desiredCount",
        "domain_name": "domainName",
        "domain_zone": "domainZone",
        "enable_ecs_managed_tags": "enableECSManagedTags",
        "enable_execute_command": "enableExecuteCommand",
        "health_check_grace_period": "healthCheckGracePeriod",
        "idle_timeout": "idleTimeout",
        "listener_port": "listenerPort",
        "load_balancer": "loadBalancer",
        "load_balancer_name": "loadBalancerName",
        "max_healthy_percent": "maxHealthyPercent",
        "min_healthy_percent": "minHealthyPercent",
        "open_listener": "openListener",
        "propagate_tags": "propagateTags",
        "protocol": "protocol",
        "protocol_version": "protocolVersion",
        "public_load_balancer": "publicLoadBalancer",
        "record_type": "recordType",
        "redirect_http": "redirectHTTP",
        "service_name": "serviceName",
        "ssl_policy": "sslPolicy",
        "target_protocol": "targetProtocol",
        "task_image_options": "taskImageOptions",
        "vpc": "vpc",
        "cpu": "cpu",
        "ephemeral_storage_gib": "ephemeralStorageGiB",
        "memory_limit_mib": "memoryLimitMiB",
        "platform_version": "platformVersion",
        "runtime_platform": "runtimePlatform",
        "task_definition": "taskDefinition",
        "assign_public_ip": "assignPublicIp",
        "health_check": "healthCheck",
        "security_groups": "securityGroups",
        "task_subnets": "taskSubnets",
        "home": "home",
        "dockerfile": "dockerfile",
        "platform": "platform",
        "python_poetry_args": "pythonPoetryArgs",
    },
)
class StreamlitSiteProps(
    _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps,
):
    def __init__(
        self,
        *,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        home: builtins.str,
        dockerfile: typing.Optional[builtins.str] = None,
        platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
        python_poetry_args: typing.Optional[typing.Union[PythonPoetryArgs, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param home: (experimental) Entrypoint to the streamlit application.
        :param dockerfile: (experimental) The name of the Dockerfile to use to build this Streamlit site. Default: "Dockerfile"
        :param platform: (experimental) The platform to use to build this Streamlit site. Default: {@link Platform.LINUX_AMD64 }
        :param python_poetry_args: (experimental) Override how the ``requirements.txt`` file is generated with Python Poetry. Default: - see {@link exportRequirementsSync }

        :stability: experimental
        '''
        if isinstance(circuit_breaker, dict):
            circuit_breaker = _aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker(**circuit_breaker)
        if isinstance(cloud_map_options, dict):
            cloud_map_options = _aws_cdk_aws_ecs_ceddda9d.CloudMapOptions(**cloud_map_options)
        if isinstance(deployment_controller, dict):
            deployment_controller = _aws_cdk_aws_ecs_ceddda9d.DeploymentController(**deployment_controller)
        if isinstance(task_image_options, dict):
            task_image_options = _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions(**task_image_options)
        if isinstance(runtime_platform, dict):
            runtime_platform = _aws_cdk_aws_ecs_ceddda9d.RuntimePlatform(**runtime_platform)
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_ecs_ceddda9d.HealthCheck(**health_check)
        if isinstance(task_subnets, dict):
            task_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**task_subnets)
        if isinstance(python_poetry_args, dict):
            python_poetry_args = PythonPoetryArgs(**python_poetry_args)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e43c9b421aebd058e3dfc4b1d85272f845a8abe30e44d6987a5185b3e8db8c8)
            check_type(argname="argument capacity_provider_strategies", value=capacity_provider_strategies, expected_type=type_hints["capacity_provider_strategies"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument circuit_breaker", value=circuit_breaker, expected_type=type_hints["circuit_breaker"])
            check_type(argname="argument cloud_map_options", value=cloud_map_options, expected_type=type_hints["cloud_map_options"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument deployment_controller", value=deployment_controller, expected_type=type_hints["deployment_controller"])
            check_type(argname="argument desired_count", value=desired_count, expected_type=type_hints["desired_count"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument domain_zone", value=domain_zone, expected_type=type_hints["domain_zone"])
            check_type(argname="argument enable_ecs_managed_tags", value=enable_ecs_managed_tags, expected_type=type_hints["enable_ecs_managed_tags"])
            check_type(argname="argument enable_execute_command", value=enable_execute_command, expected_type=type_hints["enable_execute_command"])
            check_type(argname="argument health_check_grace_period", value=health_check_grace_period, expected_type=type_hints["health_check_grace_period"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument listener_port", value=listener_port, expected_type=type_hints["listener_port"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument load_balancer_name", value=load_balancer_name, expected_type=type_hints["load_balancer_name"])
            check_type(argname="argument max_healthy_percent", value=max_healthy_percent, expected_type=type_hints["max_healthy_percent"])
            check_type(argname="argument min_healthy_percent", value=min_healthy_percent, expected_type=type_hints["min_healthy_percent"])
            check_type(argname="argument open_listener", value=open_listener, expected_type=type_hints["open_listener"])
            check_type(argname="argument propagate_tags", value=propagate_tags, expected_type=type_hints["propagate_tags"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument protocol_version", value=protocol_version, expected_type=type_hints["protocol_version"])
            check_type(argname="argument public_load_balancer", value=public_load_balancer, expected_type=type_hints["public_load_balancer"])
            check_type(argname="argument record_type", value=record_type, expected_type=type_hints["record_type"])
            check_type(argname="argument redirect_http", value=redirect_http, expected_type=type_hints["redirect_http"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument ssl_policy", value=ssl_policy, expected_type=type_hints["ssl_policy"])
            check_type(argname="argument target_protocol", value=target_protocol, expected_type=type_hints["target_protocol"])
            check_type(argname="argument task_image_options", value=task_image_options, expected_type=type_hints["task_image_options"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument ephemeral_storage_gib", value=ephemeral_storage_gib, expected_type=type_hints["ephemeral_storage_gib"])
            check_type(argname="argument memory_limit_mib", value=memory_limit_mib, expected_type=type_hints["memory_limit_mib"])
            check_type(argname="argument platform_version", value=platform_version, expected_type=type_hints["platform_version"])
            check_type(argname="argument runtime_platform", value=runtime_platform, expected_type=type_hints["runtime_platform"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument task_subnets", value=task_subnets, expected_type=type_hints["task_subnets"])
            check_type(argname="argument home", value=home, expected_type=type_hints["home"])
            check_type(argname="argument dockerfile", value=dockerfile, expected_type=type_hints["dockerfile"])
            check_type(argname="argument platform", value=platform, expected_type=type_hints["platform"])
            check_type(argname="argument python_poetry_args", value=python_poetry_args, expected_type=type_hints["python_poetry_args"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "home": home,
        }
        if capacity_provider_strategies is not None:
            self._values["capacity_provider_strategies"] = capacity_provider_strategies
        if certificate is not None:
            self._values["certificate"] = certificate
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cloud_map_options is not None:
            self._values["cloud_map_options"] = cloud_map_options
        if cluster is not None:
            self._values["cluster"] = cluster
        if deployment_controller is not None:
            self._values["deployment_controller"] = deployment_controller
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if domain_zone is not None:
            self._values["domain_zone"] = domain_zone
        if enable_ecs_managed_tags is not None:
            self._values["enable_ecs_managed_tags"] = enable_ecs_managed_tags
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if health_check_grace_period is not None:
            self._values["health_check_grace_period"] = health_check_grace_period
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if listener_port is not None:
            self._values["listener_port"] = listener_port
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if load_balancer_name is not None:
            self._values["load_balancer_name"] = load_balancer_name
        if max_healthy_percent is not None:
            self._values["max_healthy_percent"] = max_healthy_percent
        if min_healthy_percent is not None:
            self._values["min_healthy_percent"] = min_healthy_percent
        if open_listener is not None:
            self._values["open_listener"] = open_listener
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if protocol is not None:
            self._values["protocol"] = protocol
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if public_load_balancer is not None:
            self._values["public_load_balancer"] = public_load_balancer
        if record_type is not None:
            self._values["record_type"] = record_type
        if redirect_http is not None:
            self._values["redirect_http"] = redirect_http
        if service_name is not None:
            self._values["service_name"] = service_name
        if ssl_policy is not None:
            self._values["ssl_policy"] = ssl_policy
        if target_protocol is not None:
            self._values["target_protocol"] = target_protocol
        if task_image_options is not None:
            self._values["task_image_options"] = task_image_options
        if vpc is not None:
            self._values["vpc"] = vpc
        if cpu is not None:
            self._values["cpu"] = cpu
        if ephemeral_storage_gib is not None:
            self._values["ephemeral_storage_gib"] = ephemeral_storage_gib
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if runtime_platform is not None:
            self._values["runtime_platform"] = runtime_platform
        if task_definition is not None:
            self._values["task_definition"] = task_definition
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if health_check is not None:
            self._values["health_check"] = health_check
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if task_subnets is not None:
            self._values["task_subnets"] = task_subnets
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if platform is not None:
            self._values["platform"] = platform
        if python_poetry_args is not None:
            self._values["python_poetry_args"] = python_poetry_args

    @builtins.property
    def capacity_provider_strategies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]]:
        '''A list of Capacity Provider strategies used to place a service.

        :default: - undefined
        '''
        result = self._values.get("capacity_provider_strategies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]], result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''Certificate Manager certificate to associate with the load balancer.

        Setting this option will set the load balancer protocol to HTTPS.

        :default:

        - No certificate associated with the load balancer, if using
        the HTTP protocol. For HTTPS, a DNS-validated certificate will be
        created for the load balancer's specified domain name if a domain name
        and domain zone are specified.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def circuit_breaker(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker]:
        '''Whether to enable the deployment circuit breaker.

        If this property is defined, circuit breaker will be implicitly
        enabled.

        :default: - disabled
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker], result)

    @builtins.property
    def cloud_map_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions]:
        '''The options for configuring an Amazon ECS service to use service discovery.

        :default: - AWS Cloud Map service discovery is not enabled.
        '''
        result = self._values.get("cloud_map_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions], result)

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster]:
        '''The name of the cluster that hosts the service.

        If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc.

        :default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster], result)

    @builtins.property
    def deployment_controller(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController]:
        '''Specifies which deployment controller to use for the service.

        For more information, see
        `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_

        :default: - Rolling update (ECS)
        '''
        result = self._values.get("deployment_controller")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        '''The desired number of instantiations of the task definition to keep running on the service.

        The minimum value is 1

        :default:

        - The default is 1 for all new services and uses the existing service's desired count
        when updating an existing service.
        '''
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''The domain name for the service, e.g. "api.example.com.".

        :default: - No domain name.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''The Route53 hosted zone for the domain, e.g. "example.com.".

        :default: - No Route53 hosted domain zone.
        '''
        result = self._values.get("domain_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def enable_ecs_managed_tags(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether to enable Amazon ECS managed tags for the tasks within the service.

        For more information, see
        `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_

        :default: false
        '''
        result = self._values.get("enable_ecs_managed_tags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether ECS Exec should be enabled.

        :default: - false
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check_grace_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started.

        :default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        '''
        result = self._values.get("health_check_grace_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The load balancer idle timeout, in seconds.

        Can be between 1 and 4000 seconds

        :default: - CloudFormation sets idle timeout to 60 seconds
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def listener_port(self) -> typing.Optional[jsii.Number]:
        '''Listener port of the application load balancer that will serve traffic to the service.

        :default:

        - The default listener port is determined from the protocol (port 80 for HTTP,
        port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        '''
        result = self._values.get("listener_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]:
        '''The application load balancer that will serve traffic to the service.

        The VPC attribute of a load balancer must be specified for it to be used
        to create a new service with this pattern.

        [disable-awslint:ref-via-interface]

        :default: - a new load balancer will be created.
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer], result)

    @builtins.property
    def load_balancer_name(self) -> typing.Optional[builtins.str]:
        '''Name of the load balancer.

        :default: - Automatically generated name.
        '''
        result = self._values.get("load_balancer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

        :default: - 100 if daemon, otherwise 200
        '''
        result = self._values.get("max_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

        :default: - 0 if daemon, otherwise 50
        '''
        result = self._values.get("min_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def open_listener(self) -> typing.Optional[builtins.bool]:
        '''Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default.

        :default: true -- The security group allows ingress from all IP addresses.
        '''
        result = self._values.get("open_listener")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource]:
        '''Specifies whether to propagate the tags from the task definition or the service to the tasks in the service.

        Tags can only be propagated to the tasks within the service during service creation.

        :default: - none
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource], result)

    @builtins.property
    def protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from clients to the load balancer.

        The load balancer port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).  If HTTPS, either a certificate or domain
        name and domain zone must also be specified.

        :default:

        HTTP. If a certificate is specified, the protocol will be
        set by default to HTTPS.
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def protocol_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion]:
        '''The protocol version to use.

        :default: ApplicationProtocolVersion.HTTP1
        '''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion], result)

    @builtins.property
    def public_load_balancer(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the Load Balancer will be internet-facing.

        :default: true
        '''
        result = self._values.get("public_load_balancer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def record_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType]:
        '''Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all.

        This is useful if you need to work with DNS systems that do not support alias records.

        :default: ApplicationLoadBalancedServiceRecordType.ALIAS
        '''
        result = self._values.get("record_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType], result)

    @builtins.property
    def redirect_http(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS.

        :default: false
        '''
        result = self._values.get("redirect_http")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''The name of the service.

        :default: - CloudFormation-generated name.
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy]:
        '''The security policy that defines which ciphers and protocols are supported by the ALB Listener.

        :default: - The recommended elastic load balancing security policy
        '''
        result = self._values.get("ssl_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy], result)

    @builtins.property
    def target_protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from the load balancer to the ECS tasks.

        The default target port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).

        :default: HTTP.
        '''
        result = self._values.get("target_protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def task_image_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions]:
        '''The properties required to create a new task definition.

        TaskDefinition or TaskImageOptions must be specified, but not both.

        :default: none
        '''
        result = self._values.get("task_image_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed.

        If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster.

        :default: - uses the VPC defined in the cluster or creates a new VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''The number of cpu units used by the task.

        Valid values, which determines your range of valid values for the memory parameter:

        256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB

        512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB

        1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB

        2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments

        4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments

        8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments

        16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 256
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ephemeral_storage_gib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in GiB) of ephemeral storage to be allocated to the task.

        The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB.

        Only supported in Fargate platform version 1.4.0 or later.

        :default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        '''
        result = self._values.get("ephemeral_storage_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in MiB) of memory used by the task.

        This field is required and you must use one of the following values, which determines your range of valid values
        for the cpu parameter:

        512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU)

        1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU)

        2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU)

        Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU)

        Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU)

        Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU)

        Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU)

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 512
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion]:
        '''The platform version on which to run your service.

        If one is not specified, the LATEST platform version is used by default. For more information, see
        `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_
        in the Amazon Elastic Container Service Developer Guide.

        :default: Latest
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion], result)

    @builtins.property
    def runtime_platform(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform]:
        '''The runtime platform of the task definition.

        :default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        '''
        result = self._values.get("runtime_platform")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform], result)

    @builtins.property
    def task_definition(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition]:
        '''The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both.

        [disable-awslint:ref-via-interface]

        :default: - none
        '''
        result = self._values.get("task_definition")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition], result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the service will be assigned a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck]:
        '''The health check command and associated configuration parameters for the container.

        :default: - Health check configuration from container.
        '''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the service.

        If you do not specify a security group, a new security group is created.

        :default: - A new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def task_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the service.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("task_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def home(self) -> builtins.str:
        '''(experimental) Entrypoint to the streamlit application.

        :stability: experimental

        Example::

            "my/app.py"
        '''
        result = self._values.get("home")
        assert result is not None, "Required property 'home' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Dockerfile to use to build this Streamlit site.

        :default: "Dockerfile"

        :stability: experimental
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform(self) -> typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform]:
        '''(experimental) The platform to use to build this Streamlit site.

        :default: {@link Platform.LINUX_AMD64 }

        :stability: experimental
        '''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform], result)

    @builtins.property
    def python_poetry_args(self) -> typing.Optional[PythonPoetryArgs]:
        '''(experimental) Override how the ``requirements.txt`` file is generated with Python Poetry.

        :default: - see {@link exportRequirementsSync }

        :stability: experimental
        '''
        result = self._values.get("python_poetry_args")
        return typing.cast(typing.Optional[PythonPoetryArgs], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamlitSiteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@packyak/aws-cdk.TimeoutAction")
class TimeoutAction(enum.Enum):
    '''(experimental) Action to take when provisioning a Cluster and Spot Instances are not available.

    :see: https://docs.aws.amazon.com/emr/latest/APIReference/API_SpotProvisioningSpecification.html
    :stability: experimental
    '''

    SWITCH_TO_ON_DEMAND = "SWITCH_TO_ON_DEMAND"
    '''(experimental) Specifies that if no Spot Instances are available, On-Demand Instances should be provisioned to fulfill any remaining Spot capacity.

    :stability: experimental
    '''
    TERMINATE_CLUSTER = "TERMINATE_CLUSTER"
    '''(experimental) Terminates the Cluster if Spot Instances are not available.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@packyak/aws-cdk.TransportMode")
class TransportMode(enum.Enum):
    '''(experimental) https://mr3docs.datamonad.com/docs/k8s/advanced/transport/.

    :stability: experimental
    '''

    BINARY = "BINARY"
    '''
    :stability: experimental
    '''
    HTTP = "HTTP"
    '''
    :stability: experimental
    '''
    ALL = "ALL"
    '''
    :stability: experimental
    '''


class UniformCluster(
    Cluster,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.UniformCluster",
):
    '''(experimental) Creates an EMR Cluster that is comprised of {@link InstanceGroup}s.

    :see: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-instances-guidelines.html
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        core_instance_group: typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]],
        primary_instance_group: typing.Union[PrimaryInstanceGroup, typing.Dict[builtins.str, typing.Any]],
        task_instance_groups: typing.Optional[typing.Sequence[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
        catalogs: typing.Mapping[builtins.str, ICatalog],
        cluster_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_docker: typing.Optional[builtins.bool] = None,
        enable_spark_rapids: typing.Optional[builtins.bool] = None,
        enable_ssm_agent: typing.Optional[builtins.bool] = None,
        enable_xg_boost: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        home: typing.Optional["Workspace"] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        install_git_hub_cli: typing.Optional[builtins.bool] = None,
        managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        release_label: typing.Optional[ReleaseLabel] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param core_instance_group: (experimental) Describes the EC2 instances and instance configurations for core {@link InstanceGroup}s.
        :param primary_instance_group: (experimental) Describes the EC2 instances and instance configurations for the primary {@link InstanceGroup}.
        :param task_instance_groups: (experimental) Describes the EC2 instances and instance configurations for task {@link InstanceGroup}s. These task {@link InstanceGroup}s are added to the cluster as part of the cluster launch. Each task {@link InstanceGroup} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceGroup}s. .. epigraph:: After creating the cluster, you can only modify the mutable properties of ``InstanceGroupConfig`` , which are ``AutoScalingPolicy`` and ``InstanceCount`` . Modifying any other property results in cluster replacement.
        :param catalogs: (experimental) The catalogs to use for the EMR cluster.
        :param cluster_name: (experimental) Name of the EMR Cluster.
        :param vpc: (experimental) The VPC to deploy the EMR cluster into.
        :param additional_privileged_registries: (experimental) Additional registries to allow privileged containers from. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param additional_trusted_registries: (experimental) Additional registries to trust for Docker containers. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param bootstrap_actions: Default: - No bootstrap actions
        :param configurations: (experimental) Override EMR Configurations. Default: - the {@link catalog }'s configurations + .venv for the user code.
        :param enable_docker: (experimental) Enable Docker support on the cluster. Default: true
        :param enable_spark_rapids: (experimental) Enable the Spark Rapids plugin. Default: false
        :param enable_ssm_agent: (experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes. Default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``
        :param enable_xg_boost: (experimental) Enable the XGBoost spark library. Default: false
        :param environment: (experimental) Environment variables to make available to the EMR cluster. Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there. Default: - no environment variables
        :param extra_java_options: (experimental) Extra java options to include in the Spark context by default.
        :param home: (experimental) Mount a shared filesystem to the EMR cluster.
        :param idle_timeout: Default: None
        :param install_git_hub_cli: (experimental) Install the GitHub CLI on the EMR cluster. Default: false
        :param managed_scaling_policy: Default: - No managed scaling policy
        :param release_label: Default: - {@link ReleaseLabel.LATEST }
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param scale_down_behavior: Default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }
        :param step_concurrency_level: (experimental) The concurrency level of the cluster. Default: 1
        :param steps: (experimental) The EMR Steps to submit to the cluster.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6156fa160d392b0a55ee97154d43d075481d9e85ab19e2f9db0fb9bb44f89a15)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UniformClusterProps(
            core_instance_group=core_instance_group,
            primary_instance_group=primary_instance_group,
            task_instance_groups=task_instance_groups,
            catalogs=catalogs,
            cluster_name=cluster_name,
            vpc=vpc,
            additional_privileged_registries=additional_privileged_registries,
            additional_trusted_registries=additional_trusted_registries,
            bootstrap_actions=bootstrap_actions,
            configurations=configurations,
            enable_docker=enable_docker,
            enable_spark_rapids=enable_spark_rapids,
            enable_ssm_agent=enable_ssm_agent,
            enable_xg_boost=enable_xg_boost,
            environment=environment,
            extra_java_options=extra_java_options,
            home=home,
            idle_timeout=idle_timeout,
            install_git_hub_cli=install_git_hub_cli,
            managed_scaling_policy=managed_scaling_policy,
            release_label=release_label,
            removal_policy=removal_policy,
            scale_down_behavior=scale_down_behavior,
            step_concurrency_level=step_concurrency_level,
            steps=steps,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.UniformClusterProps",
    jsii_struct_bases=[BaseClusterProps],
    name_mapping={
        "catalogs": "catalogs",
        "cluster_name": "clusterName",
        "vpc": "vpc",
        "additional_privileged_registries": "additionalPrivilegedRegistries",
        "additional_trusted_registries": "additionalTrustedRegistries",
        "bootstrap_actions": "bootstrapActions",
        "configurations": "configurations",
        "enable_docker": "enableDocker",
        "enable_spark_rapids": "enableSparkRapids",
        "enable_ssm_agent": "enableSSMAgent",
        "enable_xg_boost": "enableXGBoost",
        "environment": "environment",
        "extra_java_options": "extraJavaOptions",
        "home": "home",
        "idle_timeout": "idleTimeout",
        "install_git_hub_cli": "installGitHubCLI",
        "managed_scaling_policy": "managedScalingPolicy",
        "release_label": "releaseLabel",
        "removal_policy": "removalPolicy",
        "scale_down_behavior": "scaleDownBehavior",
        "step_concurrency_level": "stepConcurrencyLevel",
        "steps": "steps",
        "core_instance_group": "coreInstanceGroup",
        "primary_instance_group": "primaryInstanceGroup",
        "task_instance_groups": "taskInstanceGroups",
    },
)
class UniformClusterProps(BaseClusterProps):
    def __init__(
        self,
        *,
        catalogs: typing.Mapping[builtins.str, ICatalog],
        cluster_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
        configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_docker: typing.Optional[builtins.bool] = None,
        enable_spark_rapids: typing.Optional[builtins.bool] = None,
        enable_ssm_agent: typing.Optional[builtins.bool] = None,
        enable_xg_boost: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        home: typing.Optional["Workspace"] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        install_git_hub_cli: typing.Optional[builtins.bool] = None,
        managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        release_label: typing.Optional[ReleaseLabel] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
        core_instance_group: typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]],
        primary_instance_group: typing.Union[PrimaryInstanceGroup, typing.Dict[builtins.str, typing.Any]],
        task_instance_groups: typing.Optional[typing.Sequence[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param catalogs: (experimental) The catalogs to use for the EMR cluster.
        :param cluster_name: (experimental) Name of the EMR Cluster.
        :param vpc: (experimental) The VPC to deploy the EMR cluster into.
        :param additional_privileged_registries: (experimental) Additional registries to allow privileged containers from. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param additional_trusted_registries: (experimental) Additional registries to trust for Docker containers. Default: - trust the ``local`` registry and all container registries in the account/region pair
        :param bootstrap_actions: Default: - No bootstrap actions
        :param configurations: (experimental) Override EMR Configurations. Default: - the {@link catalog }'s configurations + .venv for the user code.
        :param enable_docker: (experimental) Enable Docker support on the cluster. Default: true
        :param enable_spark_rapids: (experimental) Enable the Spark Rapids plugin. Default: false
        :param enable_ssm_agent: (experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes. Default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``
        :param enable_xg_boost: (experimental) Enable the XGBoost spark library. Default: false
        :param environment: (experimental) Environment variables to make available to the EMR cluster. Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there. Default: - no environment variables
        :param extra_java_options: (experimental) Extra java options to include in the Spark context by default.
        :param home: (experimental) Mount a shared filesystem to the EMR cluster.
        :param idle_timeout: Default: None
        :param install_git_hub_cli: (experimental) Install the GitHub CLI on the EMR cluster. Default: false
        :param managed_scaling_policy: Default: - No managed scaling policy
        :param release_label: Default: - {@link ReleaseLabel.LATEST }
        :param removal_policy: Default: {@link RemovalPolicy.DESTROY }
        :param scale_down_behavior: Default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }
        :param step_concurrency_level: (experimental) The concurrency level of the cluster. Default: 1
        :param steps: (experimental) The EMR Steps to submit to the cluster.
        :param core_instance_group: (experimental) Describes the EC2 instances and instance configurations for core {@link InstanceGroup}s.
        :param primary_instance_group: (experimental) Describes the EC2 instances and instance configurations for the primary {@link InstanceGroup}.
        :param task_instance_groups: (experimental) Describes the EC2 instances and instance configurations for task {@link InstanceGroup}s. These task {@link InstanceGroup}s are added to the cluster as part of the cluster launch. Each task {@link InstanceGroup} must have a unique name specified so that CloudFormation can differentiate between the task {@link InstanceGroup}s. .. epigraph:: After creating the cluster, you can only modify the mutable properties of ``InstanceGroupConfig`` , which are ``AutoScalingPolicy`` and ``InstanceCount`` . Modifying any other property results in cluster replacement.

        :stability: experimental
        '''
        if isinstance(managed_scaling_policy, dict):
            managed_scaling_policy = ManagedScalingPolicy(**managed_scaling_policy)
        if isinstance(core_instance_group, dict):
            core_instance_group = InstanceGroup(**core_instance_group)
        if isinstance(primary_instance_group, dict):
            primary_instance_group = PrimaryInstanceGroup(**primary_instance_group)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8de5a971e9d6c043dccc145931c4535f0429ab5fa70e980fdaa56c30235404f0)
            check_type(argname="argument catalogs", value=catalogs, expected_type=type_hints["catalogs"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument additional_privileged_registries", value=additional_privileged_registries, expected_type=type_hints["additional_privileged_registries"])
            check_type(argname="argument additional_trusted_registries", value=additional_trusted_registries, expected_type=type_hints["additional_trusted_registries"])
            check_type(argname="argument bootstrap_actions", value=bootstrap_actions, expected_type=type_hints["bootstrap_actions"])
            check_type(argname="argument configurations", value=configurations, expected_type=type_hints["configurations"])
            check_type(argname="argument enable_docker", value=enable_docker, expected_type=type_hints["enable_docker"])
            check_type(argname="argument enable_spark_rapids", value=enable_spark_rapids, expected_type=type_hints["enable_spark_rapids"])
            check_type(argname="argument enable_ssm_agent", value=enable_ssm_agent, expected_type=type_hints["enable_ssm_agent"])
            check_type(argname="argument enable_xg_boost", value=enable_xg_boost, expected_type=type_hints["enable_xg_boost"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument extra_java_options", value=extra_java_options, expected_type=type_hints["extra_java_options"])
            check_type(argname="argument home", value=home, expected_type=type_hints["home"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument install_git_hub_cli", value=install_git_hub_cli, expected_type=type_hints["install_git_hub_cli"])
            check_type(argname="argument managed_scaling_policy", value=managed_scaling_policy, expected_type=type_hints["managed_scaling_policy"])
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument scale_down_behavior", value=scale_down_behavior, expected_type=type_hints["scale_down_behavior"])
            check_type(argname="argument step_concurrency_level", value=step_concurrency_level, expected_type=type_hints["step_concurrency_level"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
            check_type(argname="argument core_instance_group", value=core_instance_group, expected_type=type_hints["core_instance_group"])
            check_type(argname="argument primary_instance_group", value=primary_instance_group, expected_type=type_hints["primary_instance_group"])
            check_type(argname="argument task_instance_groups", value=task_instance_groups, expected_type=type_hints["task_instance_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "catalogs": catalogs,
            "cluster_name": cluster_name,
            "vpc": vpc,
            "core_instance_group": core_instance_group,
            "primary_instance_group": primary_instance_group,
        }
        if additional_privileged_registries is not None:
            self._values["additional_privileged_registries"] = additional_privileged_registries
        if additional_trusted_registries is not None:
            self._values["additional_trusted_registries"] = additional_trusted_registries
        if bootstrap_actions is not None:
            self._values["bootstrap_actions"] = bootstrap_actions
        if configurations is not None:
            self._values["configurations"] = configurations
        if enable_docker is not None:
            self._values["enable_docker"] = enable_docker
        if enable_spark_rapids is not None:
            self._values["enable_spark_rapids"] = enable_spark_rapids
        if enable_ssm_agent is not None:
            self._values["enable_ssm_agent"] = enable_ssm_agent
        if enable_xg_boost is not None:
            self._values["enable_xg_boost"] = enable_xg_boost
        if environment is not None:
            self._values["environment"] = environment
        if extra_java_options is not None:
            self._values["extra_java_options"] = extra_java_options
        if home is not None:
            self._values["home"] = home
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if install_git_hub_cli is not None:
            self._values["install_git_hub_cli"] = install_git_hub_cli
        if managed_scaling_policy is not None:
            self._values["managed_scaling_policy"] = managed_scaling_policy
        if release_label is not None:
            self._values["release_label"] = release_label
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if scale_down_behavior is not None:
            self._values["scale_down_behavior"] = scale_down_behavior
        if step_concurrency_level is not None:
            self._values["step_concurrency_level"] = step_concurrency_level
        if steps is not None:
            self._values["steps"] = steps
        if task_instance_groups is not None:
            self._values["task_instance_groups"] = task_instance_groups

    @builtins.property
    def catalogs(self) -> typing.Mapping[builtins.str, ICatalog]:
        '''(experimental) The catalogs to use for the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("catalogs")
        assert result is not None, "Required property 'catalogs' is missing"
        return typing.cast(typing.Mapping[builtins.str, ICatalog], result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''(experimental) Name of the EMR Cluster.

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to deploy the EMR cluster into.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def additional_privileged_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to allow privileged containers from.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_privileged_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_trusted_registries(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional registries to trust for Docker containers.

        :default: - trust the ``local`` registry and all container registries in the account/region pair

        :stability: experimental
        '''
        result = self._values.get("additional_trusted_registries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bootstrap_actions(self) -> typing.Optional[typing.List[BootstrapAction]]:
        '''
        :default: - No bootstrap actions

        :stability: experimental
        '''
        result = self._values.get("bootstrap_actions")
        return typing.cast(typing.Optional[typing.List[BootstrapAction]], result)

    @builtins.property
    def configurations(self) -> typing.Optional[typing.List[Configuration]]:
        '''(experimental) Override EMR Configurations.

        :default: - the {@link catalog }'s configurations + .venv for the user code.

        :stability: experimental
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List[Configuration]], result)

    @builtins.property
    def enable_docker(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Docker support on the cluster.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enable_docker")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_spark_rapids(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the Spark Rapids plugin.

        :default: false

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-rapids.html
        :stability: experimental
        '''
        result = self._values.get("enable_spark_rapids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ssm_agent(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Installs and configures the SSM agent to run on all Primary, Core and Task nodes.

        :default: - ``true`` if {@link enableSSMTunnelOverSSH } is also ``true``, otherwise ``false``

        :stability: experimental
        '''
        result = self._values.get("enable_ssm_agent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_xg_boost(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the XGBoost spark library.

        :default: false

        :see: https://docs.nvidia.com/spark-rapids/user-guide/latest/getting-started/aws-emr.html
        :stability: experimental
        '''
        result = self._values.get("enable_xg_boost")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables to make available to the EMR cluster.

        Environment variables are written to ``/mnt/packyak/.bashrc`` and need to be sourced from there.

        :default: - no environment variables

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def extra_java_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Extra java options to include in the Spark context by default.

        :stability: experimental
        '''
        result = self._values.get("extra_java_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def home(self) -> typing.Optional["Workspace"]:
        '''(experimental) Mount a shared filesystem to the EMR cluster.

        :stability: experimental
        '''
        result = self._values.get("home")
        return typing.cast(typing.Optional["Workspace"], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''
        :default: None

        :stability: experimental
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def install_git_hub_cli(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install the GitHub CLI on the EMR cluster.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("install_git_hub_cli")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_scaling_policy(self) -> typing.Optional[ManagedScalingPolicy]:
        '''
        :default: - No managed scaling policy

        :stability: experimental
        '''
        result = self._values.get("managed_scaling_policy")
        return typing.cast(typing.Optional[ManagedScalingPolicy], result)

    @builtins.property
    def release_label(self) -> typing.Optional[ReleaseLabel]:
        '''
        :default: - {@link ReleaseLabel.LATEST }

        :stability: experimental
        '''
        result = self._values.get("release_label")
        return typing.cast(typing.Optional[ReleaseLabel], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :default: {@link RemovalPolicy.DESTROY }

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def scale_down_behavior(self) -> typing.Optional[ScaleDownBehavior]:
        '''
        :default: - {@link ScaleDownBehavior.TERMINATE_AT_TASK_COMPLETION }

        :stability: experimental
        '''
        result = self._values.get("scale_down_behavior")
        return typing.cast(typing.Optional[ScaleDownBehavior], result)

    @builtins.property
    def step_concurrency_level(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The concurrency level of the cluster.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("step_concurrency_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def steps(self) -> typing.Optional[typing.List[Step]]:
        '''(experimental) The EMR Steps to submit to the cluster.

        :see: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-submit-step.html
        :stability: experimental
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.List[Step]], result)

    @builtins.property
    def core_instance_group(self) -> InstanceGroup:
        '''(experimental) Describes the EC2 instances and instance configurations for core {@link InstanceGroup}s.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-coreinstancegroup
        :stability: experimental
        '''
        result = self._values.get("core_instance_group")
        assert result is not None, "Required property 'core_instance_group' is missing"
        return typing.cast(InstanceGroup, result)

    @builtins.property
    def primary_instance_group(self) -> PrimaryInstanceGroup:
        '''(experimental) Describes the EC2 instances and instance configurations for the primary {@link InstanceGroup}.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-masterinstancegroup
        :stability: experimental
        '''
        result = self._values.get("primary_instance_group")
        assert result is not None, "Required property 'primary_instance_group' is missing"
        return typing.cast(PrimaryInstanceGroup, result)

    @builtins.property
    def task_instance_groups(self) -> typing.Optional[typing.List[InstanceGroup]]:
        '''(experimental) Describes the EC2 instances and instance configurations for task {@link InstanceGroup}s.

        These task {@link InstanceGroup}s are added to the cluster as part of the cluster launch.
        Each task {@link InstanceGroup} must have a unique name specified so that CloudFormation
        can differentiate between the task {@link InstanceGroup}s.
        .. epigraph::

           After creating the cluster, you can only modify the mutable properties of ``InstanceGroupConfig`` , which are ``AutoScalingPolicy`` and ``InstanceCount`` . Modifying any other property results in cluster replacement.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-jobflowinstancesconfig.html#cfn-emr-cluster-jobflowinstancesconfig-taskinstancegroups
        :stability: experimental
        '''
        result = self._values.get("task_instance_groups")
        return typing.cast(typing.Optional[typing.List[InstanceGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UniformClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UserProfile(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.UserProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: Domain,
        user_profile_name: builtins.str,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain: 
        :param user_profile_name: 
        :param execution_role: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b595bca79d019bcd878e4c0258c02d22af8092c227aab0e9a98a15b80bcb93d3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UserProfileProps(
            domain=domain,
            user_profile_name=user_profile_name,
            execution_role=execution_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="resource")
    def _resource(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnUserProfile:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnUserProfile, jsii.get(self, "resource"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.UserProfileProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "user_profile_name": "userProfileName",
        "execution_role": "executionRole",
    },
)
class UserProfileProps:
    def __init__(
        self,
        *,
        domain: Domain,
        user_profile_name: builtins.str,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param domain: 
        :param user_profile_name: 
        :param execution_role: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7c1e04981abad6e5d9fc1bc464b4fc58f03ab0184376bf423aa36df3f3a836d)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument user_profile_name", value=user_profile_name, expected_type=type_hints["user_profile_name"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "user_profile_name": user_profile_name,
        }
        if execution_role is not None:
            self._values["execution_role"] = execution_role

    @builtins.property
    def domain(self) -> Domain:
        '''
        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(Domain, result)

    @builtins.property
    def user_profile_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("user_profile_name")
        assert result is not None, "Required property 'user_profile_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''
        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Version(metaclass=jsii.JSIIMeta, jsii_type="@packyak/aws-cdk.Version"):
    '''
    :stability: experimental
    '''

    def __init__(self, semver_string: builtins.str) -> None:
        '''
        :param semver_string: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b734d37cb05cb3daaa66b89ad864f6009a69762906700cfab2f0c6c9bf37e7fc)
            check_type(argname="argument semver_string", value=semver_string, expected_type=type_hints["semver_string"])
        jsii.create(self.__class__, self, [semver_string])

    @builtins.property
    @jsii.member(jsii_name="majorMinorVersion")
    def major_minor_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "majorMinorVersion"))

    @builtins.property
    @jsii.member(jsii_name="semverString")
    def semver_string(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "semverString"))


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IConnectable)
class Workspace(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.Workspace",
):
    '''(experimental) A Workspace is a shared environment for a team of developers to work on a project together.

    A Workspace contains a shared EFS {@link FileSystem} with {@link AccessPoint }s
    for each {@link User } granted access to the system.

    A Workspace can be mounted to EC2 machines, SageMaker Domains and AWS EMR Clusters.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_anonymous_access: typing.Optional[builtins.bool] = None,
        enable_automatic_backups: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        file_system_name: typing.Optional[builtins.str] = None,
        file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        one_zone: typing.Optional[builtins.bool] = None,
        out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
        performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
        provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
        transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: VPC to launch the file system in.
        :param allow_anonymous_access: Allow access from anonymous client that doesn't use IAM authentication. Default: false when using ``grantRead``, ``grantWrite``, ``grantRootAccess`` or set ``@aws-cdk/aws-efs:denyAnonymousAccess`` feature flag, otherwise true
        :param enable_automatic_backups: Whether to enable automatic backups for the file system. Default: false
        :param encrypted: Defines if the data at rest in the file system is encrypted or not. Default: - If your application has the '@aws-cdk/aws-efs:defaultEncryptionAtRest' feature flag set, the default is true, otherwise, the default is false.
        :param file_system_name: The file system's name. Default: - CDK generated name
        :param file_system_policy: File system policy is an IAM resource policy used to control NFS access to an EFS file system. Default: none
        :param kms_key: The KMS key used for encryption. This is required to encrypt the data at rest if Default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used
        :param lifecycle_policy: A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class. Default: - None. EFS will not transition files to the IA storage class.
        :param one_zone: Whether this is a One Zone file system. If enabled, ``performanceMode`` must be set to ``GENERAL_PURPOSE`` and ``vpcSubnets`` cannot be set. Default: false
        :param out_of_infrequent_access_policy: A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class. Default: - None. EFS will not transition files from IA storage to primary storage.
        :param performance_mode: The performance mode that the file system will operate under. An Amazon EFS file system's performance mode can't be changed after the file system has been created. Updating this property will replace the file system. Default: PerformanceMode.GENERAL_PURPOSE
        :param provisioned_throughput_per_second: Provisioned throughput for the file system. This is a required property if the throughput mode is set to PROVISIONED. Must be at least 1MiB/s. Default: - none, errors out
        :param removal_policy: The removal policy to apply to the file system. Default: RemovalPolicy.RETAIN
        :param replication_overwrite_protection: Whether to enable the filesystem's replication overwrite protection or not. Set false if you want to create a read-only filesystem for use as a replication destination. Default: ReplicationOverwriteProtection.ENABLED
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic
        :param throughput_mode: Enum to mention the throughput mode of the file system. Default: ThroughputMode.BURSTING
        :param transition_to_archive_policy: The number of days after files were last accessed in primary storage (the Standard storage class) at which to move them to Archive storage. Metadata operations such as listing the contents of a directory don't count as file access events. Default: - None. EFS will not transition files to Archive storage class.
        :param vpc_subnets: Which subnets to place the mount target in the VPC. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fd4fbbdb542acd368100f6f00153e82aba103a15b06b40791e454b2bbd45a6f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WorkspaceProps(
            vpc=vpc,
            allow_anonymous_access=allow_anonymous_access,
            enable_automatic_backups=enable_automatic_backups,
            encrypted=encrypted,
            file_system_name=file_system_name,
            file_system_policy=file_system_policy,
            kms_key=kms_key,
            lifecycle_policy=lifecycle_policy,
            one_zone=one_zone,
            out_of_infrequent_access_policy=out_of_infrequent_access_policy,
            performance_mode=performance_mode,
            provisioned_throughput_per_second=provisioned_throughput_per_second,
            removal_policy=removal_policy,
            replication_overwrite_protection=replication_overwrite_protection,
            security_group=security_group,
            throughput_mode=throughput_mode,
            transition_to_archive_policy=transition_to_archive_policy,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addHome")
    def add_home(
        self,
        *,
        uid: builtins.str,
        username: builtins.str,
        gid: typing.Optional[builtins.str] = None,
        secondary_groups: typing.Optional[typing.Sequence[typing.Union[PosixGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> Home:
        '''(experimental) Add a home directory to the workspace.

        :param uid: (experimental) The POSIX user ID for the user. This should be a unique identifier.
        :param username: (experimental) The username for the user. This should be unique across all users.
        :param gid: (experimental) The POSIX group ID for the user. This is used for file system permissions. Default: - same as the uid
        :param secondary_groups: (experimental) Secondary groups to assign to files written to this home directory.

        :stability: experimental
        '''
        props = AddHomeRequest(
            uid=uid, username=username, gid=gid, secondary_groups=secondary_groups
        )

        return typing.cast(Home, jsii.invoke(self, "addHome", [props]))

    @jsii.member(jsii_name="allowFrom")
    def allow_from(self, connectable: _aws_cdk_aws_ec2_ceddda9d.IConnectable) -> None:
        '''(experimental) Allow access to the EFS file system from a connectable, e.g. SecurityGroup.

        :param connectable: the connectable to allow access to the shared EFS file system.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fc2111abe8fd216720469c84ca6dba277189690c6bbb40cce1e7bf076f1c8cf)
            check_type(argname="argument connectable", value=connectable, expected_type=type_hints["connectable"])
        return typing.cast(None, jsii.invoke(self, "allowFrom", [connectable]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) Connections for the EFS file system.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> _aws_cdk_aws_efs_ceddda9d.FileSystem:
        '''(experimental) EFS File System shared by all users of the Workspace.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.FileSystem, jsii.get(self, "fileSystem"))

    @builtins.property
    @jsii.member(jsii_name="ssm")
    def ssm(self) -> Home:
        '''(experimental) Home directory of the ``ssm-user`` POSIX user.

        This is the default user assigned when logging into a machine via SSM.

        :stability: experimental
        '''
        return typing.cast(Home, jsii.get(self, "ssm"))


@jsii.data_type(
    jsii_type="@packyak/aws-cdk.WorkspaceProps",
    jsii_struct_bases=[_aws_cdk_aws_efs_ceddda9d.FileSystemProps],
    name_mapping={
        "vpc": "vpc",
        "allow_anonymous_access": "allowAnonymousAccess",
        "enable_automatic_backups": "enableAutomaticBackups",
        "encrypted": "encrypted",
        "file_system_name": "fileSystemName",
        "file_system_policy": "fileSystemPolicy",
        "kms_key": "kmsKey",
        "lifecycle_policy": "lifecyclePolicy",
        "one_zone": "oneZone",
        "out_of_infrequent_access_policy": "outOfInfrequentAccessPolicy",
        "performance_mode": "performanceMode",
        "provisioned_throughput_per_second": "provisionedThroughputPerSecond",
        "removal_policy": "removalPolicy",
        "replication_overwrite_protection": "replicationOverwriteProtection",
        "security_group": "securityGroup",
        "throughput_mode": "throughputMode",
        "transition_to_archive_policy": "transitionToArchivePolicy",
        "vpc_subnets": "vpcSubnets",
    },
)
class WorkspaceProps(_aws_cdk_aws_efs_ceddda9d.FileSystemProps):
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_anonymous_access: typing.Optional[builtins.bool] = None,
        enable_automatic_backups: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        file_system_name: typing.Optional[builtins.str] = None,
        file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        one_zone: typing.Optional[builtins.bool] = None,
        out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
        performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
        provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
        transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param vpc: VPC to launch the file system in.
        :param allow_anonymous_access: Allow access from anonymous client that doesn't use IAM authentication. Default: false when using ``grantRead``, ``grantWrite``, ``grantRootAccess`` or set ``@aws-cdk/aws-efs:denyAnonymousAccess`` feature flag, otherwise true
        :param enable_automatic_backups: Whether to enable automatic backups for the file system. Default: false
        :param encrypted: Defines if the data at rest in the file system is encrypted or not. Default: - If your application has the '@aws-cdk/aws-efs:defaultEncryptionAtRest' feature flag set, the default is true, otherwise, the default is false.
        :param file_system_name: The file system's name. Default: - CDK generated name
        :param file_system_policy: File system policy is an IAM resource policy used to control NFS access to an EFS file system. Default: none
        :param kms_key: The KMS key used for encryption. This is required to encrypt the data at rest if Default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used
        :param lifecycle_policy: A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class. Default: - None. EFS will not transition files to the IA storage class.
        :param one_zone: Whether this is a One Zone file system. If enabled, ``performanceMode`` must be set to ``GENERAL_PURPOSE`` and ``vpcSubnets`` cannot be set. Default: false
        :param out_of_infrequent_access_policy: A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class. Default: - None. EFS will not transition files from IA storage to primary storage.
        :param performance_mode: The performance mode that the file system will operate under. An Amazon EFS file system's performance mode can't be changed after the file system has been created. Updating this property will replace the file system. Default: PerformanceMode.GENERAL_PURPOSE
        :param provisioned_throughput_per_second: Provisioned throughput for the file system. This is a required property if the throughput mode is set to PROVISIONED. Must be at least 1MiB/s. Default: - none, errors out
        :param removal_policy: The removal policy to apply to the file system. Default: RemovalPolicy.RETAIN
        :param replication_overwrite_protection: Whether to enable the filesystem's replication overwrite protection or not. Set false if you want to create a read-only filesystem for use as a replication destination. Default: ReplicationOverwriteProtection.ENABLED
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic
        :param throughput_mode: Enum to mention the throughput mode of the file system. Default: ThroughputMode.BURSTING
        :param transition_to_archive_policy: The number of days after files were last accessed in primary storage (the Standard storage class) at which to move them to Archive storage. Metadata operations such as listing the contents of a directory don't count as file access events. Default: - None. EFS will not transition files to Archive storage class.
        :param vpc_subnets: Which subnets to place the mount target in the VPC. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed2735c17c77a540d104ba71c241cc505c9512e9373dd603709adf89252dd0a)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument allow_anonymous_access", value=allow_anonymous_access, expected_type=type_hints["allow_anonymous_access"])
            check_type(argname="argument enable_automatic_backups", value=enable_automatic_backups, expected_type=type_hints["enable_automatic_backups"])
            check_type(argname="argument encrypted", value=encrypted, expected_type=type_hints["encrypted"])
            check_type(argname="argument file_system_name", value=file_system_name, expected_type=type_hints["file_system_name"])
            check_type(argname="argument file_system_policy", value=file_system_policy, expected_type=type_hints["file_system_policy"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument lifecycle_policy", value=lifecycle_policy, expected_type=type_hints["lifecycle_policy"])
            check_type(argname="argument one_zone", value=one_zone, expected_type=type_hints["one_zone"])
            check_type(argname="argument out_of_infrequent_access_policy", value=out_of_infrequent_access_policy, expected_type=type_hints["out_of_infrequent_access_policy"])
            check_type(argname="argument performance_mode", value=performance_mode, expected_type=type_hints["performance_mode"])
            check_type(argname="argument provisioned_throughput_per_second", value=provisioned_throughput_per_second, expected_type=type_hints["provisioned_throughput_per_second"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument replication_overwrite_protection", value=replication_overwrite_protection, expected_type=type_hints["replication_overwrite_protection"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument throughput_mode", value=throughput_mode, expected_type=type_hints["throughput_mode"])
            check_type(argname="argument transition_to_archive_policy", value=transition_to_archive_policy, expected_type=type_hints["transition_to_archive_policy"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if allow_anonymous_access is not None:
            self._values["allow_anonymous_access"] = allow_anonymous_access
        if enable_automatic_backups is not None:
            self._values["enable_automatic_backups"] = enable_automatic_backups
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if file_system_name is not None:
            self._values["file_system_name"] = file_system_name
        if file_system_policy is not None:
            self._values["file_system_policy"] = file_system_policy
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if lifecycle_policy is not None:
            self._values["lifecycle_policy"] = lifecycle_policy
        if one_zone is not None:
            self._values["one_zone"] = one_zone
        if out_of_infrequent_access_policy is not None:
            self._values["out_of_infrequent_access_policy"] = out_of_infrequent_access_policy
        if performance_mode is not None:
            self._values["performance_mode"] = performance_mode
        if provisioned_throughput_per_second is not None:
            self._values["provisioned_throughput_per_second"] = provisioned_throughput_per_second
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replication_overwrite_protection is not None:
            self._values["replication_overwrite_protection"] = replication_overwrite_protection
        if security_group is not None:
            self._values["security_group"] = security_group
        if throughput_mode is not None:
            self._values["throughput_mode"] = throughput_mode
        if transition_to_archive_policy is not None:
            self._values["transition_to_archive_policy"] = transition_to_archive_policy
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''VPC to launch the file system in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def allow_anonymous_access(self) -> typing.Optional[builtins.bool]:
        '''Allow access from anonymous client that doesn't use IAM authentication.

        :default:

        false when using ``grantRead``, ``grantWrite``, ``grantRootAccess``
        or set ``@aws-cdk/aws-efs:denyAnonymousAccess`` feature flag, otherwise true
        '''
        result = self._values.get("allow_anonymous_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_automatic_backups(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable automatic backups for the file system.

        :default: false
        '''
        result = self._values.get("enable_automatic_backups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encrypted(self) -> typing.Optional[builtins.bool]:
        '''Defines if the data at rest in the file system is encrypted or not.

        :default: - If your application has the '@aws-cdk/aws-efs:defaultEncryptionAtRest' feature flag set, the default is true, otherwise, the default is false.

        :link: https://docs.aws.amazon.com/cdk/latest/guide/featureflags.html
        '''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def file_system_name(self) -> typing.Optional[builtins.str]:
        '''The file system's name.

        :default: - CDK generated name
        '''
        result = self._values.get("file_system_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''File system policy is an IAM resource policy used to control NFS access to an EFS file system.

        :default: none
        '''
        result = self._values.get("file_system_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used for encryption.

        This is required to encrypt the data at rest if

        :default: - if 'encrypted' is true, the default key for EFS (/aws/elasticfilesystem) is used

        :encrypted: is set to true.
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def lifecycle_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy]:
        '''A policy used by EFS lifecycle management to transition files to the Infrequent Access (IA) storage class.

        :default: - None. EFS will not transition files to the IA storage class.
        '''
        result = self._values.get("lifecycle_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy], result)

    @builtins.property
    def one_zone(self) -> typing.Optional[builtins.bool]:
        '''Whether this is a One Zone file system.

        If enabled, ``performanceMode`` must be set to ``GENERAL_PURPOSE`` and ``vpcSubnets`` cannot be set.

        :default: false

        :link: https://docs.aws.amazon.com/efs/latest/ug/availability-durability.html#file-system-type
        '''
        result = self._values.get("one_zone")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def out_of_infrequent_access_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy]:
        '''A policy used by EFS lifecycle management to transition files from Infrequent Access (IA) storage class to primary storage class.

        :default: - None. EFS will not transition files from IA storage to primary storage.
        '''
        result = self._values.get("out_of_infrequent_access_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy], result)

    @builtins.property
    def performance_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode]:
        '''The performance mode that the file system will operate under.

        An Amazon EFS file system's performance mode can't be changed after the file system has been created.
        Updating this property will replace the file system.

        :default: PerformanceMode.GENERAL_PURPOSE
        '''
        result = self._values.get("performance_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode], result)

    @builtins.property
    def provisioned_throughput_per_second(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''Provisioned throughput for the file system.

        This is a required property if the throughput mode is set to PROVISIONED.
        Must be at least 1MiB/s.

        :default: - none, errors out
        '''
        result = self._values.get("provisioned_throughput_per_second")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply to the file system.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def replication_overwrite_protection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection]:
        '''Whether to enable the filesystem's replication overwrite protection or not.

        Set false if you want to create a read-only filesystem for use as a replication destination.

        :default: ReplicationOverwriteProtection.ENABLED

        :see: https://docs.aws.amazon.com/efs/latest/ug/replication-use-cases.html#replicate-existing-destination
        '''
        result = self._values.get("replication_overwrite_protection")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security Group to assign to this file system.

        :default: - creates new security group which allows all outbound traffic
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def throughput_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode]:
        '''Enum to mention the throughput mode of the file system.

        :default: ThroughputMode.BURSTING
        '''
        result = self._values.get("throughput_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode], result)

    @builtins.property
    def transition_to_archive_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy]:
        '''The number of days after files were last accessed in primary storage (the Standard storage class) at which to move them to Archive storage.

        Metadata operations such as listing the contents of a directory don't count as file access events.

        :default: - None. EFS will not transition files to Archive storage class.
        '''
        result = self._values.get("transition_to_archive_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Which subnets to place the mount target in the VPC.

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INessieCatalog)
class BaseNessieCatalog(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@packyak/aws-cdk.BaseNessieCatalog",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        default_main_branch: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param catalog_name: (experimental) The name of this catalog in the Spark Context. Default: spark_catalog - i.e. the default catalog
        :param default_main_branch: (experimental) The default main branch of a Nessie repository. Default: main
        :param log_group: (experimental) The log group to use for the Nessie service. Default: - a new log group is created for you
        :param removal_policy: (experimental) The removal policy to apply to the Nessie service. Default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.
        :param version_store: (experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.
        :param warehouse_bucket: Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix to use for the warehouse path. Default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1686a5614d12f525217b1a641cd74b8d5c60867f7e7583dfe79f6e75f684557a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseNessieRepoProps(
            catalog_name=catalog_name,
            default_main_branch=default_main_branch,
            log_group=log_group,
            removal_policy=removal_policy,
            version_store=version_store,
            warehouse_bucket=warehouse_bucket,
            warehouse_prefix=warehouse_prefix,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="bind")
    def bind(self, cluster: Cluster, catalog_name: builtins.str) -> None:
        '''(experimental) Bind this Catalog to a {@link Cluster} by granting any required IAM Policies and adding any required configurations to the Cluster.

        :param cluster: -
        :param catalog_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c9322de607c1a4ed0d4f8feeb3508076cce7b69112e1f645c51088b7675f538)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
        return typing.cast(None, jsii.invoke(self, "bind", [cluster, catalog_name]))

    @jsii.member(jsii_name="configAsEnvVars")
    def _config_as_env_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "configAsEnvVars", []))

    @builtins.property
    @jsii.member(jsii_name="apiV1Url")
    def api_v1_url(self) -> builtins.str:
        '''(deprecated) Endpoint for the Nessie API v1.

        :deprecated: use {@link apiV2Url } instead

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiV1Url"))

    @builtins.property
    @jsii.member(jsii_name="apiV2Url")
    def api_v2_url(self) -> builtins.str:
        '''(experimental) Endpoint for the Nessie API v2.

        Note: Nessie CLI is not compatible with V1. For CLI use {@link apiV2Url}

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiV2Url"))

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def _config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) The {@link NessieConfig} for this service.

        This will translate to environment variables set at runtime.

        :see: https://projectnessie.org/try/configuration/#configuration
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="defaultMainBranch")
    def default_main_branch(self) -> builtins.str:
        '''(experimental) The default main branch of a Nessie repository created in this service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "defaultMainBranch"))

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    @abc.abstractmethod
    def endpoint(self) -> builtins.str:
        '''(experimental) The URL to this Nessie service.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="versionStore")
    def version_store(self) -> DynamoDBNessieVersionStore:
        '''(experimental) The DynamoDB Table storing all.

        :see: https://projectnessie.org/develop/kernel/#high-level-abstract
        :stability: experimental
        '''
        return typing.cast(DynamoDBNessieVersionStore, jsii.get(self, "versionStore"))

    @builtins.property
    @jsii.member(jsii_name="warehouseBucket")
    def warehouse_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) The S3 bucket used as the warehouse for Nessie.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "warehouseBucket"))

    @builtins.property
    @jsii.member(jsii_name="warehousePrefix")
    def warehouse_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The prefix to use for the warehouse path.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehousePrefix"))


class _BaseNessieCatalogProxy(BaseNessieCatalog):
    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        '''(experimental) The URL to this Nessie service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseNessieCatalog).__jsii_proxy_class__ = lambda : _BaseNessieCatalogProxy


@jsii.implements(_aws_cdk_aws_iam_ceddda9d.IGrantable)
class NessieECSCatalog(
    BaseNessieCatalog,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.NessieECSCatalog",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        dns: typing.Optional[typing.Union[DNSConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
        catalog_name: typing.Optional[builtins.str] = None,
        default_main_branch: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param dns: 
        :param platform: 
        :param catalog_name: (experimental) The name of this catalog in the Spark Context. Default: spark_catalog - i.e. the default catalog
        :param default_main_branch: (experimental) The default main branch of a Nessie repository. Default: main
        :param log_group: (experimental) The log group to use for the Nessie service. Default: - a new log group is created for you
        :param removal_policy: (experimental) The removal policy to apply to the Nessie service. Default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.
        :param version_store: (experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.
        :param warehouse_bucket: Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix to use for the warehouse path. Default: - no prefix (e.g. use the root: ``s3://bucket/``)
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e60010bceadcd8f2e18b262ced5c3a24ec99d45aed202a23a6b5692df3adf0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NessieECSCatalogProps(
            dns=dns,
            platform=platform,
            catalog_name=catalog_name,
            default_main_branch=default_main_branch,
            log_group=log_group,
            removal_policy=removal_policy,
            version_store=version_store,
            warehouse_bucket=warehouse_bucket,
            warehouse_prefix=warehouse_prefix,
            assign_public_ip=assign_public_ip,
            health_check=health_check,
            security_groups=security_groups,
            task_subnets=task_subnets,
            capacity_provider_strategies=capacity_provider_strategies,
            certificate=certificate,
            circuit_breaker=circuit_breaker,
            cloud_map_options=cloud_map_options,
            cluster=cluster,
            deployment_controller=deployment_controller,
            desired_count=desired_count,
            domain_name=domain_name,
            domain_zone=domain_zone,
            enable_ecs_managed_tags=enable_ecs_managed_tags,
            enable_execute_command=enable_execute_command,
            health_check_grace_period=health_check_grace_period,
            idle_timeout=idle_timeout,
            listener_port=listener_port,
            load_balancer=load_balancer,
            load_balancer_name=load_balancer_name,
            max_healthy_percent=max_healthy_percent,
            min_healthy_percent=min_healthy_percent,
            open_listener=open_listener,
            propagate_tags=propagate_tags,
            protocol=protocol,
            protocol_version=protocol_version,
            public_load_balancer=public_load_balancer,
            record_type=record_type,
            redirect_http=redirect_http,
            service_name=service_name,
            ssl_policy=ssl_policy,
            target_protocol=target_protocol,
            task_image_options=task_image_options,
            vpc=vpc,
            cpu=cpu,
            ephemeral_storage_gib=ephemeral_storage_gib,
            memory_limit_mib=memory_limit_mib,
            platform_version=platform_version,
            runtime_platform=runtime_platform,
            task_definition=task_definition,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        '''(experimental) The URL to this Nessie service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "logGroup"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(
        self,
    ) -> _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateService:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateService, jsii.get(self, "service"))


class NessieLambdaCatalog(
    BaseNessieCatalog,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.NessieLambdaCatalog",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        default_main_branch: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
        warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        warehouse_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param catalog_name: (experimental) The name of this catalog in the Spark Context. Default: spark_catalog - i.e. the default catalog
        :param default_main_branch: (experimental) The default main branch of a Nessie repository. Default: main
        :param log_group: (experimental) The log group to use for the Nessie service. Default: - a new log group is created for you
        :param removal_policy: (experimental) The removal policy to apply to the Nessie service. Default: RemovalPolicy.DESTROY - dynamodb tables will be destroyed.
        :param version_store: (experimental) Properties for configuring the {@link DynamoDBNessieVersionStore}.
        :param warehouse_bucket: Default: - one is created for you
        :param warehouse_prefix: (experimental) The prefix to use for the warehouse path. Default: - no prefix (e.g. use the root: ``s3://bucket/``)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a19c127b98d689699b84972338bfba68356572c72adfccbcd00803c8f3f8a98)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NessieLambdaCatalogProps(
            catalog_name=catalog_name,
            default_main_branch=default_main_branch,
            log_group=log_group,
            removal_policy=removal_policy,
            version_store=version_store,
            warehouse_bucket=warehouse_bucket,
            warehouse_prefix=warehouse_prefix,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        '''(experimental) The URL to this Nessie service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="functionUrl")
    def function_url(self) -> _aws_cdk_aws_lambda_ceddda9d.FunctionUrl:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.FunctionUrl, jsii.get(self, "functionUrl"))


class PythonVersion(
    Version,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.PythonVersion",
):
    '''
    :stability: experimental
    '''

    def __init__(self, semver_string: builtins.str) -> None:
        '''
        :param semver_string: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7f93be30416764679474172c0765c91a3b49d1482ae608cbcafd33778c7536a)
            check_type(argname="argument semver_string", value=semver_string, expected_type=type_hints["semver_string"])
        jsii.create(self.__class__, self, [semver_string])

    @jsii.python.classproperty
    @jsii.member(jsii_name="LATEST")
    def LATEST(cls) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.sget(cls, "LATEST"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_10")
    def V3_10(cls) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.sget(cls, "V3_10"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_11")
    def V3_11(cls) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.sget(cls, "V3_11"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_12")
    def V3_12(cls) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.sget(cls, "V3_12"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_7")
    def V3_7(cls) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.sget(cls, "V3_7"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_8")
    def V3_8(cls) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.sget(cls, "V3_8"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_9")
    def V3_9(cls) -> "PythonVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("PythonVersion", jsii.sget(cls, "V3_9"))


class ScalaVersion(
    Version,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.ScalaVersion",
):
    '''
    :stability: experimental
    '''

    def __init__(self, semver_string: builtins.str) -> None:
        '''
        :param semver_string: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78c55116a9366d4d5d47190cdecbe5f7ceeec7c309ac03c809332df15a10f1c9)
            check_type(argname="argument semver_string", value=semver_string, expected_type=type_hints["semver_string"])
        jsii.create(self.__class__, self, [semver_string])


class SparkVersion(
    Version,
    metaclass=jsii.JSIIMeta,
    jsii_type="@packyak/aws-cdk.SparkVersion",
):
    '''
    :stability: experimental
    '''

    def __init__(self, semver_string: builtins.str) -> None:
        '''
        :param semver_string: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29915039c3bf1b4ce6ac548b7de6468139c4b965eb7349e701b0a4c89d254146)
            check_type(argname="argument semver_string", value=semver_string, expected_type=type_hints["semver_string"])
        jsii.create(self.__class__, self, [semver_string])


__all__ = [
    "AddHomeRequest",
    "AddUserProfileProps",
    "AdjustmentType",
    "AllocationStrategy",
    "AppNetworkAccessType",
    "AuthMode",
    "AutoScalingPolicy",
    "BaseClusterProps",
    "BaseNessieCatalog",
    "BaseNessieRepoProps",
    "BootstrapAction",
    "CloudWatchAlarmDefinition",
    "Cluster",
    "ClusterProps",
    "ComputeLimits",
    "ComputeUnit",
    "Configuration",
    "DNSConfiguration",
    "DagsterDatabaseProps",
    "DagsterService",
    "DagsterServiceProps",
    "DefaultUserSettings",
    "Domain",
    "DomainProps",
    "DynamoDBNessieVersionStore",
    "EbsBlockDevice",
    "FleetCluster",
    "FleetClusterProps",
    "FromBucketProps",
    "Home",
    "HomeProps",
    "IBindable",
    "ICatalog",
    "INessieCatalog",
    "IcebergGlueCatalog",
    "IcebergGlueCatalogProps",
    "InstanceFleet",
    "InstanceGroup",
    "InstanceMarket",
    "InstanceTypeConfig",
    "Jdbc",
    "JdbcProps",
    "ManagedScalingPolicy",
    "MetricDimension",
    "MountFileSystemOptions",
    "NessieECSCatalog",
    "NessieECSCatalogProps",
    "NessieLambdaCatalog",
    "NessieLambdaCatalogProps",
    "NessieVersionStoreProps",
    "PosixGroup",
    "PrimaryInstanceGroup",
    "PythonPoetryArgs",
    "PythonVersion",
    "ReleaseLabel",
    "SageMakerImage",
    "SageMakerImageType",
    "ScalaVersion",
    "ScaleDownBehavior",
    "ScalingAction",
    "ScalingConstraints",
    "ScalingRule",
    "ScalingTrigger",
    "SimpleScalingPolicy",
    "SparkVersion",
    "Step",
    "StreamlitSite",
    "StreamlitSiteProps",
    "TimeoutAction",
    "TransportMode",
    "UniformCluster",
    "UniformClusterProps",
    "UserProfile",
    "UserProfileProps",
    "Version",
    "Workspace",
    "WorkspaceProps",
]

publication.publish()

def _typecheckingstub__d365811008c01281a2353f15bcdb3dba02ab02c8a5dd9ac10d125333165a89d6(
    *,
    uid: builtins.str,
    username: builtins.str,
    gid: typing.Optional[builtins.str] = None,
    secondary_groups: typing.Optional[typing.Sequence[typing.Union[PosixGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd296c2e747fd9b7a4bd1509b8a55934c797d3968875d41e011bf0fbbb27429a(
    *,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb0021309ff9d8938fdc28d02da5f6f2384cf42812b659fba780b9d43fdc9512(
    *,
    constraints: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[ScalingConstraints, typing.Dict[builtins.str, typing.Any]]],
    rules: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[ScalingRule, typing.Dict[builtins.str, typing.Any]]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__170eb3a40128ce3c532930d58e1541d8d16a82652e5d2bb9d601b8207bd708c6(
    *,
    catalogs: typing.Mapping[builtins.str, ICatalog],
    cluster_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_docker: typing.Optional[builtins.bool] = None,
    enable_spark_rapids: typing.Optional[builtins.bool] = None,
    enable_ssm_agent: typing.Optional[builtins.bool] = None,
    enable_xg_boost: typing.Optional[builtins.bool] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    home: typing.Optional[Workspace] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    install_git_hub_cli: typing.Optional[builtins.bool] = None,
    managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    release_label: typing.Optional[ReleaseLabel] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
    step_concurrency_level: typing.Optional[jsii.Number] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb1113f4b23cb04ea5bb029de40f2c712e0a43e86df2d0cdff19138f0252493e(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    default_main_branch: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17ee3e3194d801bb8f4751d17f0543d30fc618c893f3829dbd99fce2aa368326(
    *,
    name: builtins.str,
    script: _aws_cdk_aws_s3_assets_ceddda9d.Asset,
    args: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42c7d99699b235e40f3519ebdbc280f257a91f1adc441108f8353377f4061b3c(
    *,
    comparison_operator: builtins.str,
    metric_name: builtins.str,
    period: jsii.Number,
    threshold: jsii.Number,
    dimensions: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[MetricDimension, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__326dd028735c17e7178d84ab14e8c6beb9f3765f8638e57a971fb58271219792(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    core_instance_fleet: typing.Optional[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]] = None,
    core_instance_group: typing.Optional[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_instance_fleet: typing.Optional[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_instance_group: typing.Optional[typing.Union[PrimaryInstanceGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    task_instance_fleets: typing.Optional[typing.Sequence[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]]] = None,
    task_instance_groups: typing.Optional[typing.Sequence[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
    catalogs: typing.Mapping[builtins.str, ICatalog],
    cluster_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_docker: typing.Optional[builtins.bool] = None,
    enable_spark_rapids: typing.Optional[builtins.bool] = None,
    enable_ssm_agent: typing.Optional[builtins.bool] = None,
    enable_xg_boost: typing.Optional[builtins.bool] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    home: typing.Optional[Workspace] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    install_git_hub_cli: typing.Optional[builtins.bool] = None,
    managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    release_label: typing.Optional[ReleaseLabel] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
    step_concurrency_level: typing.Optional[jsii.Number] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb74dd3ad16954dfc52d59289b7aa9ccd07b7dd4fbd7fa75c253348f2932832(
    *configurations: Configuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc9b2f0743c1e90f3938a277ebc0eb6024ab132d898a5290097146f15891b622(
    other: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a5bb4ccf54350bc9166401e5fd426d8d9608356ea47b38b22d8cfe924c69419(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1e982fa3c2429881ad2232928af4534f82f46a6edd9c77529f3e60b1f292b7(
    home: Home,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf2b2f138734f7c01c625c41cc6dbe8d545ea0347ef4dfc43d9d6dabbd0c7ce1(
    access_point: _aws_cdk_aws_efs_ceddda9d.IAccessPoint,
    *,
    gid: jsii.Number,
    mount_point: builtins.str,
    uid: jsii.Number,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ed7bdb70f76a68cd9abec9d8ea3a1d9869cb673dd864bc41ba4fadbe8e27e19(
    file_system: _aws_cdk_aws_efs_ceddda9d.IFileSystem,
    *,
    gid: jsii.Number,
    mount_point: builtins.str,
    uid: jsii.Number,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d87af115c92712f3e3fbf2f42cdf8628fccc2ffafa0ca1ad4221ce3685635cf6(
    variables: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d1e25f38a23ff0e943bb86ed7b3aa4ba92982ab80e75489897d731cb1747ab2(
    *,
    catalogs: typing.Mapping[builtins.str, ICatalog],
    cluster_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_docker: typing.Optional[builtins.bool] = None,
    enable_spark_rapids: typing.Optional[builtins.bool] = None,
    enable_ssm_agent: typing.Optional[builtins.bool] = None,
    enable_xg_boost: typing.Optional[builtins.bool] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    home: typing.Optional[Workspace] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    install_git_hub_cli: typing.Optional[builtins.bool] = None,
    managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    release_label: typing.Optional[ReleaseLabel] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
    step_concurrency_level: typing.Optional[jsii.Number] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
    core_instance_fleet: typing.Optional[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]] = None,
    core_instance_group: typing.Optional[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_instance_fleet: typing.Optional[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_instance_group: typing.Optional[typing.Union[PrimaryInstanceGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    task_instance_fleets: typing.Optional[typing.Sequence[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]]] = None,
    task_instance_groups: typing.Optional[typing.Sequence[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3faadce00754b829619a7e305620ab7fc2d60cc3b5402c905c8eb3ee16b5f397(
    *,
    maximum_capacity_units: jsii.Number,
    minimum_capacity_units: jsii.Number,
    unit_type: ComputeUnit,
    maximum_core_capacity_units: typing.Optional[jsii.Number] = None,
    maximum_on_demand_capacity_units: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9faeef4120b59640960ae462acb70087060336971435d887fda52f15396d8441(
    *,
    classification: builtins.str,
    configuration_properties: typing.Mapping[builtins.str, builtins.str],
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81b9b42796b2032f822078ff7b8bd89a58e3e49dcd51db45579d47e54a39eeee(
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    domain_name: builtins.str,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98fe0909f89f176d0141b4b3345c67021ea1a24e405067b84665729e4dc9d842(
    *,
    cluster_identifier: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
    port: typing.Optional[jsii.Number] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4b0eb15936f6f6cf218041d3b956080f80797638288b505c722dac10d425c8c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Cluster] = None,
    database: typing.Optional[typing.Union[DagsterDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5fe68778add2bd477819d11ac1d3d7fde3e6a002284cb787b2cefc33b68da6a(
    connectable: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__441a2f78284f95b372c2942261709062f139a99540404ac4eca640163ce5c780(
    *,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Cluster] = None,
    database: typing.Optional[typing.Union[DagsterDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0873f2525085ef388fe5b1c7f480099a454fa6950f1cb093fb40de3662d2d4e(
    *,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    studio_web_portal: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b39317c6769151217f56205904c51cd118463003e1c82a917782ef88011fed14(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    app_network_access_type: typing.Optional[AppNetworkAccessType] = None,
    auth_mode: typing.Optional[AuthMode] = None,
    default_image: typing.Optional[SageMakerImage] = None,
    default_user_settings: typing.Optional[typing.Union[DefaultUserSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    sage_maker_sg: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e405c8f3997826f91b7f4298f025d4e5bb50f7fd62a432b81be85cb84bf6bf09(
    username: builtins.str,
    *,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a3d16fced81f471914f455d31101b08c9111eabf0413986dcb2bf5bc93f4a46(
    removal_policy: _aws_cdk_ceddda9d.RemovalPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a329618998e617d0011f9fc5cbc37ddfb4a1d734188d7a0530611804deec9cd8(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22a5adfc31d5acdf532137425862afa23f6c4de17c0ef170cf937e8bd5406d99(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28944ea6eb4d6bf5fbaf9efdc289e0339e6114d345826ec21a090d7752b82f11(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0746c9ef321d8e5e9c13f51fbb97143347eeb003e0dbb277e9312d08b920945a(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eac904d1e1a43e8ac5faba9775659dc9fa04e093790d62619b9d9d9aaf3fc10(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea691bc547ce6aa2168f2661375ba18ac984f4f4debbaa2f54f9a75b07d0fa62(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ccf37c0fd390833cefc7819e95388c6e738d283a7812d5734b51e6bb389a4cf(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fda286e86ee044e41b0a9adea0091e74c6d5839aa1c07ba4866056b8b7a90318(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3659dc8ef782a84d25438d733254b5d663850a083c78f465c98ab1ea4b906574(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__548ad34790588b478390e8e012a53fa696f0dbb3f8742341e2c8cce4c7608c71(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ab2dd3a7a4ddf1a651e030aaf22f6caed7004b94b4cfd0b3326b424033cb1e7(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d11c67e524851f75bc2242aea8e3f3b81bab190fd7383194f07fd11f7ab54041(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__839adbef507a2164f2932b6c92d67abc8c3eefa1943959ea40db5ad3d459df55(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fa6904f7781e447da5f82f620f04151c7cba6256ba3149edfbca791ae1477d9(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0672a62edb2af17901b06dcd1dad71d788e57f4bbed2706ec5eb67ac56e7ba5e(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__defd0b829457596f659bfadd8478ae76cc16a0a8e45c6c1091b03533a1ce031d(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9690f9bdf3023560fca8be548eee521c34ce68a771f5e7eba8c1027fc96a012d(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfd71e1bd7996d9607def6160eb444a42c549562b2934d29762c328f146debe2(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37497f96410e127045d256634518d73e5f09782f33b9148bffc56b44e4699e9a(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4ab655c7b1031ca9fc7ade8ae044ce6762df8c9a01da3c16f289342ef98bd8b(
    *,
    domain_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    app_network_access_type: typing.Optional[AppNetworkAccessType] = None,
    auth_mode: typing.Optional[AuthMode] = None,
    default_image: typing.Optional[SageMakerImage] = None,
    default_user_settings: typing.Optional[typing.Union[DefaultUserSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    sage_maker_sg: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38444b6f6d1ec4add548f3ae004c63748ea34266d1bf2c2d69305eb47c80507c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b95a70a93f69ccc7a9b492766b86bc6c93f3c322975743e20b240c292f35ae8(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbe43b619325570536138d75d8328854ea580a8678df2dbd84c0e758b9cefd8c(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c5149b787ca472bf31a4ab23acc710d8a2285accc319e0fb4c7721b7cf323f1(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1896aeef4fcde328bc873304caf61e83a6fa969eb9f8a59924b62aa9a7a936ee(
    *,
    size_in_gb: jsii.Number,
    volume_type: _aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType,
    iops: typing.Optional[jsii.Number] = None,
    throughput: typing.Optional[jsii.Number] = None,
    volumes_per_instance: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fe26ebd4797e22c94256285ebde7f20739db1573a73fd948758ad3ae94295fa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    core_instance_fleet: typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]],
    primary_instance_fleet: typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]],
    task_instance_fleets: typing.Optional[typing.Sequence[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]]] = None,
    catalogs: typing.Mapping[builtins.str, ICatalog],
    cluster_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_docker: typing.Optional[builtins.bool] = None,
    enable_spark_rapids: typing.Optional[builtins.bool] = None,
    enable_ssm_agent: typing.Optional[builtins.bool] = None,
    enable_xg_boost: typing.Optional[builtins.bool] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    home: typing.Optional[Workspace] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    install_git_hub_cli: typing.Optional[builtins.bool] = None,
    managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    release_label: typing.Optional[ReleaseLabel] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
    step_concurrency_level: typing.Optional[jsii.Number] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7b880bc0da0f93f23bfa396fe9c59e3746d2b0092ea0fc82abaa18d17075a1b(
    *,
    catalogs: typing.Mapping[builtins.str, ICatalog],
    cluster_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_docker: typing.Optional[builtins.bool] = None,
    enable_spark_rapids: typing.Optional[builtins.bool] = None,
    enable_ssm_agent: typing.Optional[builtins.bool] = None,
    enable_xg_boost: typing.Optional[builtins.bool] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    home: typing.Optional[Workspace] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    install_git_hub_cli: typing.Optional[builtins.bool] = None,
    managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    release_label: typing.Optional[ReleaseLabel] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
    step_concurrency_level: typing.Optional[jsii.Number] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
    core_instance_fleet: typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]],
    primary_instance_fleet: typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]],
    task_instance_fleets: typing.Optional[typing.Sequence[typing.Union[InstanceFleet, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64c71c6a195e64fcc7766185b4e1593d178b1bf46a3fd25f066e29cd8724c1a3(
    *,
    warehouse_bucket_name: builtins.str,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__565212a4b85e23ae7e75f9af714ae0d6c58b278abee4604b6e959e86a3d3ca98(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    file_system: _aws_cdk_aws_efs_ceddda9d.FileSystem,
    uid: builtins.str,
    username: builtins.str,
    gid: typing.Optional[builtins.str] = None,
    secondary_groups: typing.Optional[typing.Sequence[typing.Union[PosixGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e37cb5626890e66da3571373688915fca87b6cf18d6c0dbddbafe8d3f3326f7(
    connectable: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92a47ab18dc2d229886601567cbd4520f5d3447db1909eae7af40a537284a288(
    __0: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    actions: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f499ee8828f3f2cb8680f4189798e08ad6b5205c936440fa5bb4919e298a7835(
    __0: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85410aca4b22598ee59d643583833f47a41d83dc8563194e0cd73bce957cb7b4(
    __0: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aec28287cccd97087f2cb06dcc02199690033ca6da8e3311b09c6636a1ea120(
    __0: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2016038cc3fc8f8a8e6c9dc814e5b4561ac849f85a87b90b9264b3c90356995(
    *,
    file_system: _aws_cdk_aws_efs_ceddda9d.FileSystem,
    uid: builtins.str,
    username: builtins.str,
    gid: typing.Optional[builtins.str] = None,
    secondary_groups: typing.Optional[typing.Sequence[typing.Union[PosixGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62123fceb85b330c2443ea9e4844b198ca4e0f45eca5af15d990eff38617e338(
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ba13ad981cd127d54e85d1a4b2c4f77032428b6b6e23ead782555b8b4617031(
    cluster: Cluster,
    catalog_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcf3c0364f4d160fe9034f175d8eb6cc3d6d3fb23381b927b0d52a823dbb6a77(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c8134ca0fa427857fe6c762437e22f941b749792f5a0705a5beb13b6f80468d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    warehouse_bucket_name: builtins.str,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c7dc1276a04dbc750cc24c39a7c676937f09de7bb3266691c1ac2e95c8c309a(
    cluster: Cluster,
    catalog_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be36b3a23075d957cc97f13224bf1742ba67fd459d9b772c66e22d3edc9dac37(
    *,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a8e830f7bfa4a9fb090af90b9a9af86ec643a49d1d904685ce6d895915c13ae(
    *,
    instance_types: typing.Sequence[typing.Union[InstanceTypeConfig, typing.Dict[builtins.str, typing.Any]]],
    name: builtins.str,
    allocation_strategy: typing.Optional[AllocationStrategy] = None,
    target_on_demand_capacity: typing.Optional[jsii.Number] = None,
    target_spot_capacity: typing.Optional[jsii.Number] = None,
    timeout_action: typing.Optional[TimeoutAction] = None,
    timeout_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d789f501f696ccecc6fe3a5c6c3e8e1ef13012d686e91ffd2a154f89069279fc(
    *,
    instance_count: jsii.Number,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    name: builtins.str,
    auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    bid_price: typing.Optional[builtins.str] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    custom_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    ebs_block_devices: typing.Optional[typing.Sequence[typing.Union[EbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    market: typing.Optional[InstanceMarket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__029012672ed7c72ba6a26d55172513021665b3fb45d1f49093ffa04920bcb8d9(
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    bid_price: typing.Optional[builtins.str] = None,
    bid_price_as_percentage_of_on_demand_price: typing.Optional[jsii.Number] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    custom_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    ebs_block_devices: typing.Optional[typing.Sequence[typing.Union[EbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    weighted_capacity: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784d34b0dce3fbe462c26bf3f7f6264ebbac5607bf8202541d0a1b2a53a7717b(
    cluster: Cluster,
    *,
    port: jsii.Number,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hive_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    include_extensions: typing.Optional[builtins.bool] = None,
    spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62d169371e3a5aa421799f066dfb490ae95c50dd1910709b0637e97948f7a1c4(
    *connectables: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fac0fe1d0685f09839aec156e0fdb8fbed92f4a617d1f8d59883ff5eea99d1a3(
    *,
    port: jsii.Number,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hive_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    include_extensions: typing.Optional[builtins.bool] = None,
    spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4affd6995a6e5d5458d74deb9a00af0e126912b1c17740abfd29ffa5a438ff4(
    *,
    compute_limits: typing.Union[ComputeLimits, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8077db17f6c7fad8dba95e72ee1e14128f1a9109ee88f2df5a1d94ba8fa2e4a8(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f15c666d729817bc139a1898a277a4ba44218aad78c9b75cd0ca318c7f82876(
    *,
    gid: jsii.Number,
    mount_point: builtins.str,
    uid: jsii.Number,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98c31d2f2930fd529bf754148ceeb46b3270756e8314cb386d0891cfea6439eb(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    default_main_branch: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    dns: typing.Optional[typing.Union[DNSConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6c71cb603e6e9655d9f397972634d1db947ba48130957573e80f35e065776d0(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    default_main_branch: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c90f21257ff6c373cd9b8bed683c0af254fb7c1339068d939b967ab65560880(
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4dd8a0c8155f1e29163bfa4e608e4468e4b804af5e46a20deccff38cbc24cc7(
    *,
    gid: jsii.Number,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__383e1ad4836b4415ffda8afef3eaf4b449d1c46d873c9c7157bbbb2775717e14(
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    name: builtins.str,
    auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    bid_price: typing.Optional[builtins.str] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    custom_ami: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IMachineImage] = None,
    ebs_block_devices: typing.Optional[typing.Sequence[typing.Union[EbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    instance_count: typing.Optional[jsii.Number] = None,
    market: typing.Optional[InstanceMarket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbe524884870ca65c48adab2502dfd388d957f47d677bd55844748044805aec3(
    *,
    all_extras: typing.Optional[builtins.bool] = None,
    dev: typing.Optional[builtins.bool] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    include: typing.Optional[typing.Sequence[builtins.str]] = None,
    without_hashes: typing.Optional[builtins.bool] = None,
    without_urls: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64fd11a40a56ac99a11e46ec1b209f77e1d100ce52c646b4bd35654c477f5707(
    label: builtins.str,
    spark_version: SparkVersion,
    python_version: PythonVersion,
    scala_version: ScalaVersion,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e1ed4f69faebd9388d4951836ce7bd7c02d994160af437df9300fdeeef90643(
    resource_id: builtins.str,
    image_type: SageMakerImageType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24947d6fc0a5dc9cc009b6d476f771725b3ffce98fd89e63f88d9e93a459b240(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82c40f0441842fc84af2f238149188b8b8ec95a2db22879d82ae48e66675562b(
    *,
    simple_scaling_policy_configuration: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[SimpleScalingPolicy, typing.Dict[builtins.str, typing.Any]]],
    market: typing.Optional[InstanceMarket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0493b6264f42490efa4439290de4d281d9b44190041d5e565eaaabfdd57a5d0(
    *,
    max_capacity: jsii.Number,
    min_capacity: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b782ace7defba201794dcced4fc8267ec88fcdb67ea24dc5c4eb961d7c82136(
    *,
    action: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[ScalingAction, typing.Dict[builtins.str, typing.Any]]],
    name: builtins.str,
    trigger: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[ScalingTrigger, typing.Dict[builtins.str, typing.Any]]],
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67beae64caa09b21144afee8e7168cb51a0c6adb9c532d1ebd8372af22e65571(
    *,
    cloud_watch_alarm_definition: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CloudWatchAlarmDefinition, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54ddc62c0cddb203ed5c1373cc8509449a60b05b0f5d6c12436ebee720305446(
    *,
    scaling_adjustment: jsii.Number,
    adjustment_type: typing.Optional[AdjustmentType] = None,
    cool_down: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1ce8be45455ac9eb169db10448fccf280b2b4bc8ccaae864952c43b4a254c34(
    *,
    hadoop_jar_step: typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emr_ceddda9d.CfnCluster.HadoopJarStepConfigProperty, typing.Dict[builtins.str, typing.Any]]],
    name: builtins.str,
    action_on_failure: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080175f818a8350c34bed3f38ee75e2eb119e92ec7de4456fb5d9c13b4ba04ab(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    home: builtins.str,
    dockerfile: typing.Optional[builtins.str] = None,
    platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
    python_poetry_args: typing.Optional[typing.Union[PythonPoetryArgs, typing.Dict[builtins.str, typing.Any]]] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e43c9b421aebd058e3dfc4b1d85272f845a8abe30e44d6987a5185b3e8db8c8(
    *,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    home: builtins.str,
    dockerfile: typing.Optional[builtins.str] = None,
    platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
    python_poetry_args: typing.Optional[typing.Union[PythonPoetryArgs, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6156fa160d392b0a55ee97154d43d075481d9e85ab19e2f9db0fb9bb44f89a15(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    core_instance_group: typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]],
    primary_instance_group: typing.Union[PrimaryInstanceGroup, typing.Dict[builtins.str, typing.Any]],
    task_instance_groups: typing.Optional[typing.Sequence[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
    catalogs: typing.Mapping[builtins.str, ICatalog],
    cluster_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_docker: typing.Optional[builtins.bool] = None,
    enable_spark_rapids: typing.Optional[builtins.bool] = None,
    enable_ssm_agent: typing.Optional[builtins.bool] = None,
    enable_xg_boost: typing.Optional[builtins.bool] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    home: typing.Optional[Workspace] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    install_git_hub_cli: typing.Optional[builtins.bool] = None,
    managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    release_label: typing.Optional[ReleaseLabel] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
    step_concurrency_level: typing.Optional[jsii.Number] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8de5a971e9d6c043dccc145931c4535f0429ab5fa70e980fdaa56c30235404f0(
    *,
    catalogs: typing.Mapping[builtins.str, ICatalog],
    cluster_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    additional_privileged_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_trusted_registries: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions: typing.Optional[typing.Sequence[typing.Union[BootstrapAction, typing.Dict[builtins.str, typing.Any]]]] = None,
    configurations: typing.Optional[typing.Sequence[typing.Union[Configuration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_docker: typing.Optional[builtins.bool] = None,
    enable_spark_rapids: typing.Optional[builtins.bool] = None,
    enable_ssm_agent: typing.Optional[builtins.bool] = None,
    enable_xg_boost: typing.Optional[builtins.bool] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_java_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    home: typing.Optional[Workspace] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    install_git_hub_cli: typing.Optional[builtins.bool] = None,
    managed_scaling_policy: typing.Optional[typing.Union[ManagedScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    release_label: typing.Optional[ReleaseLabel] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    scale_down_behavior: typing.Optional[ScaleDownBehavior] = None,
    step_concurrency_level: typing.Optional[jsii.Number] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[Step, typing.Dict[builtins.str, typing.Any]]]] = None,
    core_instance_group: typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]],
    primary_instance_group: typing.Union[PrimaryInstanceGroup, typing.Dict[builtins.str, typing.Any]],
    task_instance_groups: typing.Optional[typing.Sequence[typing.Union[InstanceGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b595bca79d019bcd878e4c0258c02d22af8092c227aab0e9a98a15b80bcb93d3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: Domain,
    user_profile_name: builtins.str,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7c1e04981abad6e5d9fc1bc464b4fc58f03ab0184376bf423aa36df3f3a836d(
    *,
    domain: Domain,
    user_profile_name: builtins.str,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b734d37cb05cb3daaa66b89ad864f6009a69762906700cfab2f0c6c9bf37e7fc(
    semver_string: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd4fbbdb542acd368100f6f00153e82aba103a15b06b40791e454b2bbd45a6f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_anonymous_access: typing.Optional[builtins.bool] = None,
    enable_automatic_backups: typing.Optional[builtins.bool] = None,
    encrypted: typing.Optional[builtins.bool] = None,
    file_system_name: typing.Optional[builtins.str] = None,
    file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    one_zone: typing.Optional[builtins.bool] = None,
    out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
    performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
    provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
    transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fc2111abe8fd216720469c84ca6dba277189690c6bbb40cce1e7bf076f1c8cf(
    connectable: _aws_cdk_aws_ec2_ceddda9d.IConnectable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed2735c17c77a540d104ba71c241cc505c9512e9373dd603709adf89252dd0a(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_anonymous_access: typing.Optional[builtins.bool] = None,
    enable_automatic_backups: typing.Optional[builtins.bool] = None,
    encrypted: typing.Optional[builtins.bool] = None,
    file_system_name: typing.Optional[builtins.str] = None,
    file_system_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lifecycle_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    one_zone: typing.Optional[builtins.bool] = None,
    out_of_infrequent_access_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.OutOfInfrequentAccessPolicy] = None,
    performance_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.PerformanceMode] = None,
    provisioned_throughput_per_second: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_overwrite_protection: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ReplicationOverwriteProtection] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    throughput_mode: typing.Optional[_aws_cdk_aws_efs_ceddda9d.ThroughputMode] = None,
    transition_to_archive_policy: typing.Optional[_aws_cdk_aws_efs_ceddda9d.LifecyclePolicy] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1686a5614d12f525217b1a641cd74b8d5c60867f7e7583dfe79f6e75f684557a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    default_main_branch: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9322de607c1a4ed0d4f8feeb3508076cce7b69112e1f645c51088b7675f538(
    cluster: Cluster,
    catalog_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e60010bceadcd8f2e18b262ced5c3a24ec99d45aed202a23a6b5692df3adf0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    dns: typing.Optional[typing.Union[DNSConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
    catalog_name: typing.Optional[builtins.str] = None,
    default_main_branch: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a19c127b98d689699b84972338bfba68356572c72adfccbcd00803c8f3f8a98(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    default_main_branch: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    version_store: typing.Optional[DynamoDBNessieVersionStore] = None,
    warehouse_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    warehouse_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7f93be30416764679474172c0765c91a3b49d1482ae608cbcafd33778c7536a(
    semver_string: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78c55116a9366d4d5d47190cdecbe5f7ceeec7c309ac03c809332df15a10f1c9(
    semver_string: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29915039c3bf1b4ce6ac548b7de6468139c4b965eb7349e701b0a4c89d254146(
    semver_string: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

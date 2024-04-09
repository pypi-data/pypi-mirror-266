'''
# Cloudparing AWS CDK Construct Library

CDK constructs focused on monitoring and reducing cloud infrastructure costs.

## Installation

<details><summary><strong>TypeScript</strong></summary>

> https://www.npmjs.com/package/@cloudparing/aws-cdk-lib

In your `package.json`:

```json
{
  "dependencies": {
    "@cloudparing/aws-cdk-lib": "^0.0.0",

    // peer dependencies
    "aws-cdk-lib": "^2.65.0",
    "constructs": "^10.0.5"

    // ...your other dependencies...
  }
}
```

</details>

## Features

### Cost and Usage Report (CUR) v2 Report

```python

    const curBucket =
      props.bucket ||
      new cdk.aws_s3.Bucket(this, `Cur2Bucket`, {
        bucketName: `cur2-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
      });

    new Cur2ExportDefinition(this, `Cur2ExportDefinition`, {
      name: 'cur2-daily-csv',
      description: props.exportDescription,
      bucket: curBucket,
    });
```

### Legacy Cost and Usage Report (CUR)

An L2 construct and CDK stack for configuring the AWS Cost and Usage Report.

**NOTE: The CUR report must be deployed to us-east-1**

**Example using the ReportDefinition construct:**

```
    new ReportDefinition(this, `ReportDefinitionId`, {
      reportName: "CUR Report",
      s3Bucket: yourS3Bucket,
    });
```

**Example using the provided Stacks:**

```
import { CurStack, Cur2Stack } from '@cloudparing/aws-cdk-lib';
import * as cdk from 'aws-cdk-lib';

// for development, use account/region from cdk cli
const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new cdk.App();

new CurStack(app, 'curStack-dev', {
  env: devEnv,
  stackName: 'CurStack',
  reportName: 'cur-daily-csv',
});

new Cur2Stack(app, 'cur2Stack-dev', {
  env: devEnv,
  stackName: 'Cur2Stack',
  name: 'cur2-daily-csv',
});

app.synth();

```

Both the L2 construct and the stack provide sensible defaults which can be customized by setting props.

```
    new ReportDefinition(this, `ReportDefinitionId`, {
      reportName: "CUR Report",
      s3Bucket: yourS3Bucket,
      format: 'Parquet'
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.Cur2ContentOptions",
    jsii_struct_bases=[],
    name_mapping={
        "columns": "columns",
        "include_resource_ids": "includeResourceIds",
        "split_cost_allocation_data": "splitCostAllocationData",
        "time_unit": "timeUnit",
    },
)
class Cur2ContentOptions:
    def __init__(
        self,
        *,
        columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_resource_ids: typing.Optional[builtins.bool] = None,
        split_cost_allocation_data: typing.Optional[builtins.bool] = None,
        time_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param columns: The columns that you want to include in your data query. This allows you to create exports with consistent schemas, remove sensitive cost data, and reduce the file size of the export. By default, all columns are selected Default: false
        :param include_resource_ids: Include a column containing the unique AWS resource ID for applicable line items. Including individual resource IDs in your export might increase the file size Default: false
        :param split_cost_allocation_data: Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS). Including these resources introduces new rows and columns in the Cost and Usage Report and might increase the file size Default: false
        :param time_unit: The time granularity for how you want the line items in the export to be aggregated. Default: HOURLY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e2a338ef04831d2164d86bffca9489db99c797dd275a9f3743f8c3dd95b8654)
            check_type(argname="argument columns", value=columns, expected_type=type_hints["columns"])
            check_type(argname="argument include_resource_ids", value=include_resource_ids, expected_type=type_hints["include_resource_ids"])
            check_type(argname="argument split_cost_allocation_data", value=split_cost_allocation_data, expected_type=type_hints["split_cost_allocation_data"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if columns is not None:
            self._values["columns"] = columns
        if include_resource_ids is not None:
            self._values["include_resource_ids"] = include_resource_ids
        if split_cost_allocation_data is not None:
            self._values["split_cost_allocation_data"] = split_cost_allocation_data
        if time_unit is not None:
            self._values["time_unit"] = time_unit

    @builtins.property
    def columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The columns that you want to include in your data query.

        This allows
        you to create exports with consistent schemas, remove sensitive cost data,
        and reduce the file size of the export. By default, all columns are selected

        :default: false
        '''
        result = self._values.get("columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_resource_ids(self) -> typing.Optional[builtins.bool]:
        '''Include a column containing the unique AWS resource ID for applicable line items.

        Including individual resource IDs in your export might
        increase the file size

        :default: false
        '''
        result = self._values.get("include_resource_ids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def split_cost_allocation_data(self) -> typing.Optional[builtins.bool]:
        '''Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS).

        Including these resources introduces new
        rows and columns in the Cost and Usage Report and might increase the file size

        :default: false
        '''
        result = self._values.get("split_cost_allocation_data")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def time_unit(self) -> typing.Optional[builtins.str]:
        '''The time granularity for how you want the line items in the export to be aggregated.

        :default: HOURLY
        '''
        result = self._values.get("time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Cur2ContentOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.Cur2DeliveryOptions",
    jsii_struct_bases=[],
    name_mapping={
        "compression_format": "compressionFormat",
        "export_versioning": "exportVersioning",
    },
)
class Cur2DeliveryOptions:
    def __init__(
        self,
        *,
        compression_format: typing.Optional[builtins.str] = None,
        export_versioning: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param compression_format: The compression type and file format for your export. Default: GZIP_CSV
        :param export_versioning: Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions. Default: OVERWRITE_EXPORT
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5df5cf45e952be8b9ea5c4eb0f3746721eccdf2c40006c21537904a2f6c34a87)
            check_type(argname="argument compression_format", value=compression_format, expected_type=type_hints["compression_format"])
            check_type(argname="argument export_versioning", value=export_versioning, expected_type=type_hints["export_versioning"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if compression_format is not None:
            self._values["compression_format"] = compression_format
        if export_versioning is not None:
            self._values["export_versioning"] = export_versioning

    @builtins.property
    def compression_format(self) -> typing.Optional[builtins.str]:
        '''The compression type and file format for your export.

        :default: GZIP_CSV
        '''
        result = self._values.get("compression_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def export_versioning(self) -> typing.Optional[builtins.str]:
        '''Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions.

        :default: OVERWRITE_EXPORT
        '''
        result = self._values.get("export_versioning")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Cur2DeliveryOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.Cur2ExportOptions",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "name": "name"},
)
class Cur2ExportOptions:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: The description for this specific data export.
        :param name: The name of this specific data export.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b76fcc0045a89bb77697c53f8d8fec29c424076778c2137c572a3c17416090c)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description for this specific data export.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this specific data export.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Cur2ExportOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Cur2Stack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudparing/aws-cdk-lib.Cur2Stack",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        export_description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_resource_ids: typing.Optional[builtins.bool] = None,
        split_cost_allocation_data: typing.Optional[builtins.bool] = None,
        time_unit: typing.Optional[builtins.str] = None,
        compression_format: typing.Optional[builtins.str] = None,
        export_versioning: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket: The S3 bucket where your data export will be stored. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param export_description: The description for this specific data export.
        :param name: The name of this specific data export.
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param columns: The columns that you want to include in your data query. This allows you to create exports with consistent schemas, remove sensitive cost data, and reduce the file size of the export. By default, all columns are selected Default: false
        :param include_resource_ids: Include a column containing the unique AWS resource ID for applicable line items. Including individual resource IDs in your export might increase the file size Default: false
        :param split_cost_allocation_data: Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS). Including these resources introduces new rows and columns in the Cost and Usage Report and might increase the file size Default: false
        :param time_unit: The time granularity for how you want the line items in the export to be aggregated. Default: HOURLY
        :param compression_format: The compression type and file format for your export. Default: GZIP_CSV
        :param export_versioning: Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions. Default: OVERWRITE_EXPORT
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15b55aca791c854ee759a2958cc99ed6e481f48ad477d30e60b445ae7924c2cb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Cur2StackProps(
            bucket=bucket,
            export_description=export_description,
            name=name,
            s3_prefix=s3_prefix,
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
            columns=columns,
            include_resource_ids=include_resource_ids,
            split_cost_allocation_data=split_cost_allocation_data,
            time_unit=time_unit,
            compression_format=compression_format,
            export_versioning=export_versioning,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.Cur2StackProps",
    jsii_struct_bases=[
        _aws_cdk_ceddda9d.StackProps, Cur2ContentOptions, Cur2DeliveryOptions
    ],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "description": "description",
        "env": "env",
        "stack_name": "stackName",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "columns": "columns",
        "include_resource_ids": "includeResourceIds",
        "split_cost_allocation_data": "splitCostAllocationData",
        "time_unit": "timeUnit",
        "compression_format": "compressionFormat",
        "export_versioning": "exportVersioning",
        "bucket": "bucket",
        "export_description": "exportDescription",
        "name": "name",
        "s3_prefix": "s3Prefix",
    },
)
class Cur2StackProps(
    _aws_cdk_ceddda9d.StackProps,
    Cur2ContentOptions,
    Cur2DeliveryOptions,
):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_resource_ids: typing.Optional[builtins.bool] = None,
        split_cost_allocation_data: typing.Optional[builtins.bool] = None,
        time_unit: typing.Optional[builtins.str] = None,
        compression_format: typing.Optional[builtins.str] = None,
        export_versioning: typing.Optional[builtins.str] = None,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        export_description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param columns: The columns that you want to include in your data query. This allows you to create exports with consistent schemas, remove sensitive cost data, and reduce the file size of the export. By default, all columns are selected Default: false
        :param include_resource_ids: Include a column containing the unique AWS resource ID for applicable line items. Including individual resource IDs in your export might increase the file size Default: false
        :param split_cost_allocation_data: Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS). Including these resources introduces new rows and columns in the Cost and Usage Report and might increase the file size Default: false
        :param time_unit: The time granularity for how you want the line items in the export to be aggregated. Default: HOURLY
        :param compression_format: The compression type and file format for your export. Default: GZIP_CSV
        :param export_versioning: Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions. Default: OVERWRITE_EXPORT
        :param bucket: The S3 bucket where your data export will be stored. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param export_description: The description for this specific data export.
        :param name: The name of this specific data export.
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9874515288fcc079414e2aa1ce5051c44b895dbb3b2284094d12f07a49b841d9)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument columns", value=columns, expected_type=type_hints["columns"])
            check_type(argname="argument include_resource_ids", value=include_resource_ids, expected_type=type_hints["include_resource_ids"])
            check_type(argname="argument split_cost_allocation_data", value=split_cost_allocation_data, expected_type=type_hints["split_cost_allocation_data"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
            check_type(argname="argument compression_format", value=compression_format, expected_type=type_hints["compression_format"])
            check_type(argname="argument export_versioning", value=export_versioning, expected_type=type_hints["export_versioning"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument export_description", value=export_description, expected_type=type_hints["export_description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if columns is not None:
            self._values["columns"] = columns
        if include_resource_ids is not None:
            self._values["include_resource_ids"] = include_resource_ids
        if split_cost_allocation_data is not None:
            self._values["split_cost_allocation_data"] = split_cost_allocation_data
        if time_unit is not None:
            self._values["time_unit"] = time_unit
        if compression_format is not None:
            self._values["compression_format"] = compression_format
        if export_versioning is not None:
            self._values["export_versioning"] = export_versioning
        if bucket is not None:
            self._values["bucket"] = bucket
        if export_description is not None:
            self._values["export_description"] = export_description
        if name is not None:
            self._values["name"] = name
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        :default:

        - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag
        is set, ``LegacyStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The columns that you want to include in your data query.

        This allows
        you to create exports with consistent schemas, remove sensitive cost data,
        and reduce the file size of the export. By default, all columns are selected

        :default: false
        '''
        result = self._values.get("columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_resource_ids(self) -> typing.Optional[builtins.bool]:
        '''Include a column containing the unique AWS resource ID for applicable line items.

        Including individual resource IDs in your export might
        increase the file size

        :default: false
        '''
        result = self._values.get("include_resource_ids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def split_cost_allocation_data(self) -> typing.Optional[builtins.bool]:
        '''Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS).

        Including these resources introduces new
        rows and columns in the Cost and Usage Report and might increase the file size

        :default: false
        '''
        result = self._values.get("split_cost_allocation_data")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def time_unit(self) -> typing.Optional[builtins.str]:
        '''The time granularity for how you want the line items in the export to be aggregated.

        :default: HOURLY
        '''
        result = self._values.get("time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compression_format(self) -> typing.Optional[builtins.str]:
        '''The compression type and file format for your export.

        :default: GZIP_CSV
        '''
        result = self._values.get("compression_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def export_versioning(self) -> typing.Optional[builtins.str]:
        '''Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions.

        :default: OVERWRITE_EXPORT
        '''
        result = self._values.get("export_versioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The S3 bucket where your data export will be stored.

        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]+
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def export_description(self) -> typing.Optional[builtins.str]:
        '''The description for this specific data export.'''
        result = self._values.get("export_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this specific data export.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix that AWS adds to the report name when AWS delivers the report.

        Your prefix can't include spaces.
        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]*

        :default: ""
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Cur2StackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CurStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudparing/aws-cdk-lib.CurStack",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        report_name: builtins.str,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
        billing_view_arn: typing.Optional[builtins.str] = None,
        compression: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        report_versioning: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param report_name: The name of the report that you want to create. The name must be unique, is case sensitive, and can't include spaces.
        :param s3_bucket: The S3 bucket where AWS delivers the report - defaults to a new bucket named ``cur-${ACCOUNT_ID}-${REGION}`` Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param additional_artifacts: A list of manifests that you want Amazon Web Services to create for this report. Default: - no additional artifacts
        :param additional_schema_elements: A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs. Default: - no additional schema elements
        :param billing_view_arn: The Amazon Resource Name (ARN) of the billing view. Default: - no billing view ARN
        :param compression: The compression format that Amazon Web Services uses for the report. Default: GZIP
        :param format: The format that AWS saves the report in. Default: textORcsv
        :param refresh_closed_reports: Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months. These charges can include refunds, credits, or support fees. Default: true
        :param report_versioning: Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions. Default: OVERWRITE_REPORT
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        :param time_unit: The length of time covered by the report. Default: DAILY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__573d1ff330d3ed3c251fedf90c1a7878146801f68fdf329f23fc0d9796101f0b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CurStackProps(
            report_name=report_name,
            s3_bucket=s3_bucket,
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
            additional_artifacts=additional_artifacts,
            additional_schema_elements=additional_schema_elements,
            billing_view_arn=billing_view_arn,
            compression=compression,
            format=format,
            refresh_closed_reports=refresh_closed_reports,
            report_versioning=report_versioning,
            s3_prefix=s3_prefix,
            time_unit=time_unit,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class DataExportDefinition(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudparing/aws-cdk-lib.DataExportDefinition",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        properties: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        s3_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param properties: Properties to pass to the Lambda. Default: - No properties.
        :param description: The description for this specific data export.
        :param name: The name of this specific data export.
        :param bucket: The S3 bucket where your data export will be stored. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9a6493ee5c736083edaaf5437f004dc2dcc511c832d276d48ea11f4db41bc67)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataExportDefinitionProps(
            properties=properties,
            description=description,
            name=name,
            bucket=bucket,
            s3_prefix=s3_prefix,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.DataExportStorageOptions",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "s3_prefix": "s3Prefix"},
)
class DataExportStorageOptions:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        s3_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: The S3 bucket where your data export will be stored. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f40f9df5109bca471cae37e4d5a8d3aa734a6a1b3a6e32ec86a25c2abaa501db)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 bucket where your data export will be stored.

        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]+
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix that AWS adds to the report name when AWS delivers the report.

        Your prefix can't include spaces.
        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]*

        :default: ""
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataExportStorageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReportDefinition(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudparing/aws-cdk-lib.ReportDefinition",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        report_name: builtins.str,
        s3_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
        billing_view_arn: typing.Optional[builtins.str] = None,
        compression: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        report_versioning: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param report_name: The name of the report that you want to create. The name must be unique, is case sensitive, and can't include spaces.
        :param s3_bucket: The S3 bucket where AWS delivers the report. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param additional_artifacts: A list of manifests that you want Amazon Web Services to create for this report. Default: - no additional artifacts
        :param additional_schema_elements: A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs. Default: - no additional schema elements
        :param billing_view_arn: The Amazon Resource Name (ARN) of the billing view. Default: - no billing view ARN
        :param compression: The compression format that Amazon Web Services uses for the report. Default: GZIP
        :param format: The format that AWS saves the report in. Default: textORcsv
        :param refresh_closed_reports: Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months. These charges can include refunds, credits, or support fees. Default: true
        :param report_versioning: Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions. Default: OVERWRITE_REPORT
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        :param time_unit: The length of time covered by the report. Default: DAILY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b570e99bc2a2968e266aa82abd2ac1ff951c1a2762076a016e5f268622c5afe)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ReportDefinitionProps(
            report_name=report_name,
            s3_bucket=s3_bucket,
            additional_artifacts=additional_artifacts,
            additional_schema_elements=additional_schema_elements,
            billing_view_arn=billing_view_arn,
            compression=compression,
            format=format,
            refresh_closed_reports=refresh_closed_reports,
            report_versioning=report_versioning,
            s3_prefix=s3_prefix,
            time_unit=time_unit,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.ReportDefinitionOptions",
    jsii_struct_bases=[],
    name_mapping={
        "additional_artifacts": "additionalArtifacts",
        "additional_schema_elements": "additionalSchemaElements",
        "billing_view_arn": "billingViewArn",
        "compression": "compression",
        "format": "format",
        "refresh_closed_reports": "refreshClosedReports",
        "report_versioning": "reportVersioning",
        "s3_prefix": "s3Prefix",
        "time_unit": "timeUnit",
    },
)
class ReportDefinitionOptions:
    def __init__(
        self,
        *,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
        billing_view_arn: typing.Optional[builtins.str] = None,
        compression: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        report_versioning: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param additional_artifacts: A list of manifests that you want Amazon Web Services to create for this report. Default: - no additional artifacts
        :param additional_schema_elements: A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs. Default: - no additional schema elements
        :param billing_view_arn: The Amazon Resource Name (ARN) of the billing view. Default: - no billing view ARN
        :param compression: The compression format that Amazon Web Services uses for the report. Default: GZIP
        :param format: The format that AWS saves the report in. Default: textORcsv
        :param refresh_closed_reports: Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months. These charges can include refunds, credits, or support fees. Default: true
        :param report_versioning: Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions. Default: OVERWRITE_REPORT
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        :param time_unit: The length of time covered by the report. Default: DAILY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692120cf234d49339bf50ec4ae9bc6ef5ad18eb0a77e887a390e7e901efddabe)
            check_type(argname="argument additional_artifacts", value=additional_artifacts, expected_type=type_hints["additional_artifacts"])
            check_type(argname="argument additional_schema_elements", value=additional_schema_elements, expected_type=type_hints["additional_schema_elements"])
            check_type(argname="argument billing_view_arn", value=billing_view_arn, expected_type=type_hints["billing_view_arn"])
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument refresh_closed_reports", value=refresh_closed_reports, expected_type=type_hints["refresh_closed_reports"])
            check_type(argname="argument report_versioning", value=report_versioning, expected_type=type_hints["report_versioning"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_artifacts is not None:
            self._values["additional_artifacts"] = additional_artifacts
        if additional_schema_elements is not None:
            self._values["additional_schema_elements"] = additional_schema_elements
        if billing_view_arn is not None:
            self._values["billing_view_arn"] = billing_view_arn
        if compression is not None:
            self._values["compression"] = compression
        if format is not None:
            self._values["format"] = format
        if refresh_closed_reports is not None:
            self._values["refresh_closed_reports"] = refresh_closed_reports
        if report_versioning is not None:
            self._values["report_versioning"] = report_versioning
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if time_unit is not None:
            self._values["time_unit"] = time_unit

    @builtins.property
    def additional_artifacts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of manifests that you want Amazon Web Services to create for this report.

        :default: - no additional artifacts
        '''
        result = self._values.get("additional_artifacts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_schema_elements(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs.

        :default: - no additional schema elements
        '''
        result = self._values.get("additional_schema_elements")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def billing_view_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the billing view.

        :default: - no billing view ARN
        '''
        result = self._values.get("billing_view_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compression(self) -> typing.Optional[builtins.str]:
        '''The compression format that Amazon Web Services uses for the report.

        :default: GZIP
        '''
        result = self._values.get("compression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format that AWS saves the report in.

        :default: textORcsv
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_closed_reports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]]:
        '''Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months.

        These charges can include refunds,
        credits, or support fees.

        :default: true
        '''
        result = self._values.get("refresh_closed_reports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]], result)

    @builtins.property
    def report_versioning(self) -> typing.Optional[builtins.str]:
        '''Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions.

        :default: OVERWRITE_REPORT
        '''
        result = self._values.get("report_versioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix that AWS adds to the report name when AWS delivers the report.

        Your prefix can't include spaces.
        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]*

        :default: ""
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_unit(self) -> typing.Optional[builtins.str]:
        '''The length of time covered by the report.

        :default: DAILY
        '''
        result = self._values.get("time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReportDefinitionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.ReportDefinitionProps",
    jsii_struct_bases=[ReportDefinitionOptions],
    name_mapping={
        "additional_artifacts": "additionalArtifacts",
        "additional_schema_elements": "additionalSchemaElements",
        "billing_view_arn": "billingViewArn",
        "compression": "compression",
        "format": "format",
        "refresh_closed_reports": "refreshClosedReports",
        "report_versioning": "reportVersioning",
        "s3_prefix": "s3Prefix",
        "time_unit": "timeUnit",
        "report_name": "reportName",
        "s3_bucket": "s3Bucket",
    },
)
class ReportDefinitionProps(ReportDefinitionOptions):
    def __init__(
        self,
        *,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
        billing_view_arn: typing.Optional[builtins.str] = None,
        compression: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        report_versioning: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional[builtins.str] = None,
        report_name: builtins.str,
        s3_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    ) -> None:
        '''
        :param additional_artifacts: A list of manifests that you want Amazon Web Services to create for this report. Default: - no additional artifacts
        :param additional_schema_elements: A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs. Default: - no additional schema elements
        :param billing_view_arn: The Amazon Resource Name (ARN) of the billing view. Default: - no billing view ARN
        :param compression: The compression format that Amazon Web Services uses for the report. Default: GZIP
        :param format: The format that AWS saves the report in. Default: textORcsv
        :param refresh_closed_reports: Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months. These charges can include refunds, credits, or support fees. Default: true
        :param report_versioning: Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions. Default: OVERWRITE_REPORT
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        :param time_unit: The length of time covered by the report. Default: DAILY
        :param report_name: The name of the report that you want to create. The name must be unique, is case sensitive, and can't include spaces.
        :param s3_bucket: The S3 bucket where AWS delivers the report. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fce275d6865901db0c7067757724b474ce4884af474902cbee6c64874642260)
            check_type(argname="argument additional_artifacts", value=additional_artifacts, expected_type=type_hints["additional_artifacts"])
            check_type(argname="argument additional_schema_elements", value=additional_schema_elements, expected_type=type_hints["additional_schema_elements"])
            check_type(argname="argument billing_view_arn", value=billing_view_arn, expected_type=type_hints["billing_view_arn"])
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument refresh_closed_reports", value=refresh_closed_reports, expected_type=type_hints["refresh_closed_reports"])
            check_type(argname="argument report_versioning", value=report_versioning, expected_type=type_hints["report_versioning"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
            check_type(argname="argument report_name", value=report_name, expected_type=type_hints["report_name"])
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "report_name": report_name,
            "s3_bucket": s3_bucket,
        }
        if additional_artifacts is not None:
            self._values["additional_artifacts"] = additional_artifacts
        if additional_schema_elements is not None:
            self._values["additional_schema_elements"] = additional_schema_elements
        if billing_view_arn is not None:
            self._values["billing_view_arn"] = billing_view_arn
        if compression is not None:
            self._values["compression"] = compression
        if format is not None:
            self._values["format"] = format
        if refresh_closed_reports is not None:
            self._values["refresh_closed_reports"] = refresh_closed_reports
        if report_versioning is not None:
            self._values["report_versioning"] = report_versioning
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if time_unit is not None:
            self._values["time_unit"] = time_unit

    @builtins.property
    def additional_artifacts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of manifests that you want Amazon Web Services to create for this report.

        :default: - no additional artifacts
        '''
        result = self._values.get("additional_artifacts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_schema_elements(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs.

        :default: - no additional schema elements
        '''
        result = self._values.get("additional_schema_elements")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def billing_view_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the billing view.

        :default: - no billing view ARN
        '''
        result = self._values.get("billing_view_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compression(self) -> typing.Optional[builtins.str]:
        '''The compression format that Amazon Web Services uses for the report.

        :default: GZIP
        '''
        result = self._values.get("compression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format that AWS saves the report in.

        :default: textORcsv
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_closed_reports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]]:
        '''Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months.

        These charges can include refunds,
        credits, or support fees.

        :default: true
        '''
        result = self._values.get("refresh_closed_reports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]], result)

    @builtins.property
    def report_versioning(self) -> typing.Optional[builtins.str]:
        '''Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions.

        :default: OVERWRITE_REPORT
        '''
        result = self._values.get("report_versioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix that AWS adds to the report name when AWS delivers the report.

        Your prefix can't include spaces.
        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]*

        :default: ""
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_unit(self) -> typing.Optional[builtins.str]:
        '''The length of time covered by the report.

        :default: DAILY
        '''
        result = self._values.get("time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def report_name(self) -> builtins.str:
        '''The name of the report that you want to create.

        The name must be unique, is case sensitive, and can't include spaces.
        '''
        result = self._values.get("report_name")
        assert result is not None, "Required property 'report_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 bucket where AWS delivers the report.

        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]+
        '''
        result = self._values.get("s3_bucket")
        assert result is not None, "Required property 's3_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReportDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Cur2ExportDefinition(
    DataExportDefinition,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudparing/aws-cdk-lib.Cur2ExportDefinition",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_resource_ids: typing.Optional[builtins.bool] = None,
        split_cost_allocation_data: typing.Optional[builtins.bool] = None,
        time_unit: typing.Optional[builtins.str] = None,
        compression_format: typing.Optional[builtins.str] = None,
        export_versioning: typing.Optional[builtins.str] = None,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        s3_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: The description for this specific data export.
        :param name: The name of this specific data export.
        :param columns: The columns that you want to include in your data query. This allows you to create exports with consistent schemas, remove sensitive cost data, and reduce the file size of the export. By default, all columns are selected Default: false
        :param include_resource_ids: Include a column containing the unique AWS resource ID for applicable line items. Including individual resource IDs in your export might increase the file size Default: false
        :param split_cost_allocation_data: Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS). Including these resources introduces new rows and columns in the Cost and Usage Report and might increase the file size Default: false
        :param time_unit: The time granularity for how you want the line items in the export to be aggregated. Default: HOURLY
        :param compression_format: The compression type and file format for your export. Default: GZIP_CSV
        :param export_versioning: Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions. Default: OVERWRITE_EXPORT
        :param bucket: The S3 bucket where your data export will be stored. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d43b9f979783bea0e9dade5be0d65bfa007437a2d38a5d5d2f02183acc94d063)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Cur2ExportProps(
            description=description,
            name=name,
            columns=columns,
            include_resource_ids=include_resource_ids,
            split_cost_allocation_data=split_cost_allocation_data,
            time_unit=time_unit,
            compression_format=compression_format,
            export_versioning=export_versioning,
            bucket=bucket,
            s3_prefix=s3_prefix,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.Cur2ExportProps",
    jsii_struct_bases=[
        Cur2ExportOptions,
        Cur2ContentOptions,
        Cur2DeliveryOptions,
        DataExportStorageOptions,
    ],
    name_mapping={
        "description": "description",
        "name": "name",
        "columns": "columns",
        "include_resource_ids": "includeResourceIds",
        "split_cost_allocation_data": "splitCostAllocationData",
        "time_unit": "timeUnit",
        "compression_format": "compressionFormat",
        "export_versioning": "exportVersioning",
        "bucket": "bucket",
        "s3_prefix": "s3Prefix",
    },
)
class Cur2ExportProps(
    Cur2ExportOptions,
    Cur2ContentOptions,
    Cur2DeliveryOptions,
    DataExportStorageOptions,
):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_resource_ids: typing.Optional[builtins.bool] = None,
        split_cost_allocation_data: typing.Optional[builtins.bool] = None,
        time_unit: typing.Optional[builtins.str] = None,
        compression_format: typing.Optional[builtins.str] = None,
        export_versioning: typing.Optional[builtins.str] = None,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        s3_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: The description for this specific data export.
        :param name: The name of this specific data export.
        :param columns: The columns that you want to include in your data query. This allows you to create exports with consistent schemas, remove sensitive cost data, and reduce the file size of the export. By default, all columns are selected Default: false
        :param include_resource_ids: Include a column containing the unique AWS resource ID for applicable line items. Including individual resource IDs in your export might increase the file size Default: false
        :param split_cost_allocation_data: Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS). Including these resources introduces new rows and columns in the Cost and Usage Report and might increase the file size Default: false
        :param time_unit: The time granularity for how you want the line items in the export to be aggregated. Default: HOURLY
        :param compression_format: The compression type and file format for your export. Default: GZIP_CSV
        :param export_versioning: Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions. Default: OVERWRITE_EXPORT
        :param bucket: The S3 bucket where your data export will be stored. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf2505f2c226f5b088573d14b4e2d8835374c9f491c0f5b16fcc181b9e8b3f5f)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument columns", value=columns, expected_type=type_hints["columns"])
            check_type(argname="argument include_resource_ids", value=include_resource_ids, expected_type=type_hints["include_resource_ids"])
            check_type(argname="argument split_cost_allocation_data", value=split_cost_allocation_data, expected_type=type_hints["split_cost_allocation_data"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
            check_type(argname="argument compression_format", value=compression_format, expected_type=type_hints["compression_format"])
            check_type(argname="argument export_versioning", value=export_versioning, expected_type=type_hints["export_versioning"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if columns is not None:
            self._values["columns"] = columns
        if include_resource_ids is not None:
            self._values["include_resource_ids"] = include_resource_ids
        if split_cost_allocation_data is not None:
            self._values["split_cost_allocation_data"] = split_cost_allocation_data
        if time_unit is not None:
            self._values["time_unit"] = time_unit
        if compression_format is not None:
            self._values["compression_format"] = compression_format
        if export_versioning is not None:
            self._values["export_versioning"] = export_versioning
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description for this specific data export.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this specific data export.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The columns that you want to include in your data query.

        This allows
        you to create exports with consistent schemas, remove sensitive cost data,
        and reduce the file size of the export. By default, all columns are selected

        :default: false
        '''
        result = self._values.get("columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_resource_ids(self) -> typing.Optional[builtins.bool]:
        '''Include a column containing the unique AWS resource ID for applicable line items.

        Including individual resource IDs in your export might
        increase the file size

        :default: false
        '''
        result = self._values.get("include_resource_ids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def split_cost_allocation_data(self) -> typing.Optional[builtins.bool]:
        '''Include detailed cost and usage for shared resources for cost allocation (only available for Amazon ECS).

        Including these resources introduces new
        rows and columns in the Cost and Usage Report and might increase the file size

        :default: false
        '''
        result = self._values.get("split_cost_allocation_data")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def time_unit(self) -> typing.Optional[builtins.str]:
        '''The time granularity for how you want the line items in the export to be aggregated.

        :default: HOURLY
        '''
        result = self._values.get("time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compression_format(self) -> typing.Optional[builtins.str]:
        '''The compression type and file format for your export.

        :default: GZIP_CSV
        '''
        result = self._values.get("compression_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def export_versioning(self) -> typing.Optional[builtins.str]:
        '''Whether you want each version of the data export file to overwrite the previous version or to be delivered in addition to the previous versions.

        :default: OVERWRITE_EXPORT
        '''
        result = self._values.get("export_versioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 bucket where your data export will be stored.

        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]+
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix that AWS adds to the report name when AWS delivers the report.

        Your prefix can't include spaces.
        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]*

        :default: ""
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Cur2ExportProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.CurStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps, ReportDefinitionOptions],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "description": "description",
        "env": "env",
        "stack_name": "stackName",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "additional_artifacts": "additionalArtifacts",
        "additional_schema_elements": "additionalSchemaElements",
        "billing_view_arn": "billingViewArn",
        "compression": "compression",
        "format": "format",
        "refresh_closed_reports": "refreshClosedReports",
        "report_versioning": "reportVersioning",
        "s3_prefix": "s3Prefix",
        "time_unit": "timeUnit",
        "report_name": "reportName",
        "s3_bucket": "s3Bucket",
    },
)
class CurStackProps(_aws_cdk_ceddda9d.StackProps, ReportDefinitionOptions):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
        billing_view_arn: typing.Optional[builtins.str] = None,
        compression: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        report_versioning: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional[builtins.str] = None,
        report_name: builtins.str,
        s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param additional_artifacts: A list of manifests that you want Amazon Web Services to create for this report. Default: - no additional artifacts
        :param additional_schema_elements: A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs. Default: - no additional schema elements
        :param billing_view_arn: The Amazon Resource Name (ARN) of the billing view. Default: - no billing view ARN
        :param compression: The compression format that Amazon Web Services uses for the report. Default: GZIP
        :param format: The format that AWS saves the report in. Default: textORcsv
        :param refresh_closed_reports: Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months. These charges can include refunds, credits, or support fees. Default: true
        :param report_versioning: Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions. Default: OVERWRITE_REPORT
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        :param time_unit: The length of time covered by the report. Default: DAILY
        :param report_name: The name of the report that you want to create. The name must be unique, is case sensitive, and can't include spaces.
        :param s3_bucket: The S3 bucket where AWS delivers the report - defaults to a new bucket named ``cur-${ACCOUNT_ID}-${REGION}`` Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e565341e7abc2f9d9178c2e6dbeb24bfcd225ed6279c8b43e3a485d708bb84c9)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument additional_artifacts", value=additional_artifacts, expected_type=type_hints["additional_artifacts"])
            check_type(argname="argument additional_schema_elements", value=additional_schema_elements, expected_type=type_hints["additional_schema_elements"])
            check_type(argname="argument billing_view_arn", value=billing_view_arn, expected_type=type_hints["billing_view_arn"])
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument refresh_closed_reports", value=refresh_closed_reports, expected_type=type_hints["refresh_closed_reports"])
            check_type(argname="argument report_versioning", value=report_versioning, expected_type=type_hints["report_versioning"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
            check_type(argname="argument report_name", value=report_name, expected_type=type_hints["report_name"])
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "report_name": report_name,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if additional_artifacts is not None:
            self._values["additional_artifacts"] = additional_artifacts
        if additional_schema_elements is not None:
            self._values["additional_schema_elements"] = additional_schema_elements
        if billing_view_arn is not None:
            self._values["billing_view_arn"] = billing_view_arn
        if compression is not None:
            self._values["compression"] = compression
        if format is not None:
            self._values["format"] = format
        if refresh_closed_reports is not None:
            self._values["refresh_closed_reports"] = refresh_closed_reports
        if report_versioning is not None:
            self._values["report_versioning"] = report_versioning
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if time_unit is not None:
            self._values["time_unit"] = time_unit
        if s3_bucket is not None:
            self._values["s3_bucket"] = s3_bucket

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        :default:

        - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag
        is set, ``LegacyStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def additional_artifacts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of manifests that you want Amazon Web Services to create for this report.

        :default: - no additional artifacts
        '''
        result = self._values.get("additional_artifacts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_schema_elements(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of strings that indicate additional content that Amazon Web Services includes in the report, such as individual resource IDs.

        :default: - no additional schema elements
        '''
        result = self._values.get("additional_schema_elements")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def billing_view_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the billing view.

        :default: - no billing view ARN
        '''
        result = self._values.get("billing_view_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compression(self) -> typing.Optional[builtins.str]:
        '''The compression format that Amazon Web Services uses for the report.

        :default: GZIP
        '''
        result = self._values.get("compression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format that AWS saves the report in.

        :default: textORcsv
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_closed_reports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]]:
        '''Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months.

        These charges can include refunds,
        credits, or support fees.

        :default: true
        '''
        result = self._values.get("refresh_closed_reports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]], result)

    @builtins.property
    def report_versioning(self) -> typing.Optional[builtins.str]:
        '''Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions.

        :default: OVERWRITE_REPORT
        '''
        result = self._values.get("report_versioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix that AWS adds to the report name when AWS delivers the report.

        Your prefix can't include spaces.
        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]*

        :default: ""
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_unit(self) -> typing.Optional[builtins.str]:
        '''The length of time covered by the report.

        :default: DAILY
        '''
        result = self._values.get("time_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def report_name(self) -> builtins.str:
        '''The name of the report that you want to create.

        The name must be unique, is case sensitive, and can't include spaces.
        '''
        result = self._values.get("report_name")
        assert result is not None, "Required property 'report_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The S3 bucket where AWS delivers the report - defaults to a new bucket named ``cur-${ACCOUNT_ID}-${REGION}``    Length Constraints: Maximum length of 256.

        Pattern: [A-Za-z0-9_.-]+
        '''
        result = self._values.get("s3_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CurStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudparing/aws-cdk-lib.DataExportDefinitionProps",
    jsii_struct_bases=[Cur2ExportOptions, DataExportStorageOptions],
    name_mapping={
        "description": "description",
        "name": "name",
        "bucket": "bucket",
        "s3_prefix": "s3Prefix",
        "properties": "properties",
    },
)
class DataExportDefinitionProps(Cur2ExportOptions, DataExportStorageOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        s3_prefix: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param description: The description for this specific data export.
        :param name: The name of this specific data export.
        :param bucket: The S3 bucket where your data export will be stored. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]+
        :param s3_prefix: The prefix that AWS adds to the report name when AWS delivers the report. Your prefix can't include spaces. Length Constraints: Maximum length of 256. Pattern: [A-Za-z0-9_.-]* Default: ""
        :param properties: Properties to pass to the Lambda. Default: - No properties.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d237edc50681ac32ffd089b38ec0cd1703035ed93e5cbdd73fbcc0b13337bc9)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description for this specific data export.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this specific data export.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 bucket where your data export will be stored.

        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]+
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix that AWS adds to the report name when AWS delivers the report.

        Your prefix can't include spaces.
        Length Constraints: Maximum length of 256.
        Pattern: [A-Za-z0-9_.-]*

        :default: ""
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Properties to pass to the Lambda.

        :default: - No properties.
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataExportDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Cur2ContentOptions",
    "Cur2DeliveryOptions",
    "Cur2ExportDefinition",
    "Cur2ExportOptions",
    "Cur2ExportProps",
    "Cur2Stack",
    "Cur2StackProps",
    "CurStack",
    "CurStackProps",
    "DataExportDefinition",
    "DataExportDefinitionProps",
    "DataExportStorageOptions",
    "ReportDefinition",
    "ReportDefinitionOptions",
    "ReportDefinitionProps",
]

publication.publish()

def _typecheckingstub__4e2a338ef04831d2164d86bffca9489db99c797dd275a9f3743f8c3dd95b8654(
    *,
    columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_resource_ids: typing.Optional[builtins.bool] = None,
    split_cost_allocation_data: typing.Optional[builtins.bool] = None,
    time_unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5df5cf45e952be8b9ea5c4eb0f3746721eccdf2c40006c21537904a2f6c34a87(
    *,
    compression_format: typing.Optional[builtins.str] = None,
    export_versioning: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b76fcc0045a89bb77697c53f8d8fec29c424076778c2137c572a3c17416090c(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15b55aca791c854ee759a2958cc99ed6e481f48ad477d30e60b445ae7924c2cb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    export_description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_resource_ids: typing.Optional[builtins.bool] = None,
    split_cost_allocation_data: typing.Optional[builtins.bool] = None,
    time_unit: typing.Optional[builtins.str] = None,
    compression_format: typing.Optional[builtins.str] = None,
    export_versioning: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9874515288fcc079414e2aa1ce5051c44b895dbb3b2284094d12f07a49b841d9(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_resource_ids: typing.Optional[builtins.bool] = None,
    split_cost_allocation_data: typing.Optional[builtins.bool] = None,
    time_unit: typing.Optional[builtins.str] = None,
    compression_format: typing.Optional[builtins.str] = None,
    export_versioning: typing.Optional[builtins.str] = None,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    export_description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__573d1ff330d3ed3c251fedf90c1a7878146801f68fdf329f23fc0d9796101f0b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    report_name: builtins.str,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
    billing_view_arn: typing.Optional[builtins.str] = None,
    compression: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    report_versioning: typing.Optional[builtins.str] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    time_unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9a6493ee5c736083edaaf5437f004dc2dcc511c832d276d48ea11f4db41bc67(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    properties: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    s3_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f40f9df5109bca471cae37e4d5a8d3aa734a6a1b3a6e32ec86a25c2abaa501db(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    s3_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b570e99bc2a2968e266aa82abd2ac1ff951c1a2762076a016e5f268622c5afe(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    report_name: builtins.str,
    s3_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
    billing_view_arn: typing.Optional[builtins.str] = None,
    compression: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    report_versioning: typing.Optional[builtins.str] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    time_unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692120cf234d49339bf50ec4ae9bc6ef5ad18eb0a77e887a390e7e901efddabe(
    *,
    additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
    billing_view_arn: typing.Optional[builtins.str] = None,
    compression: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    report_versioning: typing.Optional[builtins.str] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    time_unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fce275d6865901db0c7067757724b474ce4884af474902cbee6c64874642260(
    *,
    additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
    billing_view_arn: typing.Optional[builtins.str] = None,
    compression: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    report_versioning: typing.Optional[builtins.str] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    time_unit: typing.Optional[builtins.str] = None,
    report_name: builtins.str,
    s3_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d43b9f979783bea0e9dade5be0d65bfa007437a2d38a5d5d2f02183acc94d063(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_resource_ids: typing.Optional[builtins.bool] = None,
    split_cost_allocation_data: typing.Optional[builtins.bool] = None,
    time_unit: typing.Optional[builtins.str] = None,
    compression_format: typing.Optional[builtins.str] = None,
    export_versioning: typing.Optional[builtins.str] = None,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    s3_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2505f2c226f5b088573d14b4e2d8835374c9f491c0f5b16fcc181b9e8b3f5f(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_resource_ids: typing.Optional[builtins.bool] = None,
    split_cost_allocation_data: typing.Optional[builtins.bool] = None,
    time_unit: typing.Optional[builtins.str] = None,
    compression_format: typing.Optional[builtins.str] = None,
    export_versioning: typing.Optional[builtins.str] = None,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    s3_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e565341e7abc2f9d9178c2e6dbeb24bfcd225ed6279c8b43e3a485d708bb84c9(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
    billing_view_arn: typing.Optional[builtins.str] = None,
    compression: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    report_versioning: typing.Optional[builtins.str] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    time_unit: typing.Optional[builtins.str] = None,
    report_name: builtins.str,
    s3_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d237edc50681ac32ffd089b38ec0cd1703035ed93e5cbdd73fbcc0b13337bc9(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    s3_prefix: typing.Optional[builtins.str] = None,
    properties: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

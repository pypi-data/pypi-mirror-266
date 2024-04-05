'''
# core module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

The core library includes the basic building blocks of the AWS Solutions Constructs Library. It defines the core classes that are used in the rest of the AWS Solutions Constructs Library.

## Default Properties for AWS CDK Constructs

Core library sets the default properties for the AWS CDK Constructs used by the AWS Solutions Constructs Library constructs.

For example, the following is the snippet of default properties for S3 Bucket construct created by AWS Solutions Constructs. By default, it will turn on the server-side encryption, bucket versioning, block all public access and setup the S3 access logging.

```
{
  encryption: s3.BucketEncryption.S3_MANAGED,
  versioned: true,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  removalPolicy: RemovalPolicy.RETAIN,
  serverAccessLogsBucket: loggingBucket
}
```

## Override the default properties

The default properties set by the Core library can be overridden by user provided properties. For example, the user can override the Amazon S3 Block Public Access property to meet specific requirements.

```
  const stack = new cdk.Stack();

  const props: CloudFrontToS3Props = {
    bucketProps: {
      blockPublicAccess: {
        blockPublicAcls: false,
        blockPublicPolicy: true,
        ignorePublicAcls: false,
        restrictPublicBuckets: true
      }
    }
  };

  new CloudFrontToS3(stack, 'test-cloudfront-s3', props);

  expect(stack).toHaveResource("AWS::S3::Bucket", {
    PublicAccessBlockConfiguration: {
      BlockPublicAcls: false,
      BlockPublicPolicy: true,
      IgnorePublicAcls: false,
      RestrictPublicBuckets: true
    },
  });
```

## Property override warnings

When a default property from the Core library is overridden by a user-provided property, Constructs will emit one or more warning messages to the console highlighting the change(s). These messages are intended to provide situational awareness to the user and prevent unintentional overrides that could create security risks. These messages will appear whenever deployment/build-related commands are executed, including `cdk deploy`, `cdk synth`, `npm test`, etc.

Example message:
`AWS_CONSTRUCTS_WARNING: An override has been provided for the property: BillingMode. Default value: 'PAY_PER_REQUEST'. You provided: 'PROVISIONED'.`

#### Toggling override warnings

Override warning messages are enabled by default, but can be explicitly turned on/off using the `overrideWarningsEnabled` shell variable.

* To explicitly <u>turn off</u> override warnings, run `export overrideWarningsEnabled=false`.
* To explicitly <u>turn on</u> override warnings, run `export overrideWarningsEnabled=true`.
* To revert to the default, run `unset overrideWarningsEnabled`.
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
import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_elasticache as _aws_cdk_aws_elasticache_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_elasticsearch as _aws_cdk_aws_elasticsearch_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_glue as _aws_cdk_aws_glue_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kendra as _aws_cdk_aws_kendra_ceddda9d
import aws_cdk.aws_kinesis as _aws_cdk_aws_kinesis_ceddda9d
import aws_cdk.aws_kinesisfirehose as _aws_cdk_aws_kinesisfirehose_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_lambda_event_sources as _aws_cdk_aws_lambda_event_sources_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_mediastore as _aws_cdk_aws_mediastore_ceddda9d
import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import aws_cdk.aws_sagemaker as _aws_cdk_aws_sagemaker_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.AddProxyMethodToApiResourceInputParams",
    jsii_struct_bases=[],
    name_mapping={
        "api_gateway_role": "apiGatewayRole",
        "api_method": "apiMethod",
        "api_resource": "apiResource",
        "request_template": "requestTemplate",
        "service": "service",
        "action": "action",
        "additional_request_templates": "additionalRequestTemplates",
        "aws_integration_props": "awsIntegrationProps",
        "content_type": "contentType",
        "integration_responses": "integrationResponses",
        "method_options": "methodOptions",
        "path": "path",
        "request_model": "requestModel",
        "request_validator": "requestValidator",
    },
)
class AddProxyMethodToApiResourceInputParams:
    def __init__(
        self,
        *,
        api_gateway_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        api_method: builtins.str,
        api_resource: _aws_cdk_aws_apigateway_ceddda9d.IResource,
        request_template: builtins.str,
        service: builtins.str,
        action: typing.Optional[builtins.str] = None,
        additional_request_templates: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        aws_integration_props: typing.Any = None,
        content_type: typing.Optional[builtins.str] = None,
        integration_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.IntegrationResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
        method_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        path: typing.Optional[builtins.str] = None,
        request_model: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_apigateway_ceddda9d.IModel]] = None,
        request_validator: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IRequestValidator] = None,
    ) -> None:
        '''
        :param api_gateway_role: -
        :param api_method: -
        :param api_resource: -
        :param request_template: -
        :param service: -
        :param action: -
        :param additional_request_templates: -
        :param aws_integration_props: -
        :param content_type: -
        :param integration_responses: -
        :param method_options: -
        :param path: -
        :param request_model: -
        :param request_validator: -
        '''
        if isinstance(method_options, dict):
            method_options = _aws_cdk_aws_apigateway_ceddda9d.MethodOptions(**method_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4b1ec9338820a6eda8ebc288883f36b3164955512161b7cc4267de31aceffb1)
            check_type(argname="argument api_gateway_role", value=api_gateway_role, expected_type=type_hints["api_gateway_role"])
            check_type(argname="argument api_method", value=api_method, expected_type=type_hints["api_method"])
            check_type(argname="argument api_resource", value=api_resource, expected_type=type_hints["api_resource"])
            check_type(argname="argument request_template", value=request_template, expected_type=type_hints["request_template"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument additional_request_templates", value=additional_request_templates, expected_type=type_hints["additional_request_templates"])
            check_type(argname="argument aws_integration_props", value=aws_integration_props, expected_type=type_hints["aws_integration_props"])
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
            check_type(argname="argument integration_responses", value=integration_responses, expected_type=type_hints["integration_responses"])
            check_type(argname="argument method_options", value=method_options, expected_type=type_hints["method_options"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument request_model", value=request_model, expected_type=type_hints["request_model"])
            check_type(argname="argument request_validator", value=request_validator, expected_type=type_hints["request_validator"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_gateway_role": api_gateway_role,
            "api_method": api_method,
            "api_resource": api_resource,
            "request_template": request_template,
            "service": service,
        }
        if action is not None:
            self._values["action"] = action
        if additional_request_templates is not None:
            self._values["additional_request_templates"] = additional_request_templates
        if aws_integration_props is not None:
            self._values["aws_integration_props"] = aws_integration_props
        if content_type is not None:
            self._values["content_type"] = content_type
        if integration_responses is not None:
            self._values["integration_responses"] = integration_responses
        if method_options is not None:
            self._values["method_options"] = method_options
        if path is not None:
            self._values["path"] = path
        if request_model is not None:
            self._values["request_model"] = request_model
        if request_validator is not None:
            self._values["request_validator"] = request_validator

    @builtins.property
    def api_gateway_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        result = self._values.get("api_gateway_role")
        assert result is not None, "Required property 'api_gateway_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def api_method(self) -> builtins.str:
        result = self._values.get("api_method")
        assert result is not None, "Required property 'api_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_resource(self) -> _aws_cdk_aws_apigateway_ceddda9d.IResource:
        result = self._values.get("api_resource")
        assert result is not None, "Required property 'api_resource' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.IResource, result)

    @builtins.property
    def request_template(self) -> builtins.str:
        result = self._values.get("request_template")
        assert result is not None, "Required property 'request_template' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service(self) -> builtins.str:
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action(self) -> typing.Optional[builtins.str]:
        result = self._values.get("action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_request_templates(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("additional_request_templates")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def aws_integration_props(self) -> typing.Any:
        result = self._values.get("aws_integration_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_responses(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_apigateway_ceddda9d.IntegrationResponse]]:
        result = self._values.get("integration_responses")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_apigateway_ceddda9d.IntegrationResponse]], result)

    @builtins.property
    def method_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions]:
        result = self._values.get("method_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_model(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_apigateway_ceddda9d.IModel]]:
        result = self._values.get("request_model")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_apigateway_ceddda9d.IModel]], result)

    @builtins.property
    def request_validator(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IRequestValidator]:
        result = self._values.get("request_validator")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IRequestValidator], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddProxyMethodToApiResourceInputParams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildDeadLetterQueueProps",
    jsii_struct_bases=[],
    name_mapping={
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "existing_queue_obj": "existingQueueObj",
        "max_receive_count": "maxReceiveCount",
    },
)
class BuildDeadLetterQueueProps:
    def __init__(
        self,
        *,
        dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - required field.
        :param existing_queue_obj: Existing instance of SQS queue object, providing both this and queueProps will cause an error. Default: - None.
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Default: - Default props are used
        '''
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**dead_letter_queue_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f79386b6162082a3848170974aab68319c4d3739960a82001b687d0237a8dddb)
            check_type(argname="argument dead_letter_queue_props", value=dead_letter_queue_props, expected_type=type_hints["dead_letter_queue_props"])
            check_type(argname="argument deploy_dead_letter_queue", value=deploy_dead_letter_queue, expected_type=type_hints["deploy_dead_letter_queue"])
            check_type(argname="argument existing_queue_obj", value=existing_queue_obj, expected_type=type_hints["existing_queue_obj"])
            check_type(argname="argument max_receive_count", value=max_receive_count, expected_type=type_hints["max_receive_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count

    @builtins.property
    def dead_letter_queue_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        '''Optional user provided properties for the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a secondary queue to be used as a dead letter queue.

        :default: - required field.
        '''
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        '''Existing instance of SQS queue object, providing both this and queueProps will cause an error.

        :default: - None.
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildDeadLetterQueueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildDynamoDBTableProps",
    jsii_struct_bases=[],
    name_mapping={
        "dynamo_table_props": "dynamoTableProps",
        "existing_table_interface": "existingTableInterface",
        "existing_table_obj": "existingTableObj",
    },
)
class BuildDynamoDBTableProps:
    def __init__(
        self,
        *,
        dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_table_interface: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    ) -> None:
        '''
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_table_interface: Existing instance of dynamodb interface. Providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        :param existing_table_obj: Existing instance of dynamodb table object. Providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        '''
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = _aws_cdk_aws_dynamodb_ceddda9d.TableProps(**dynamo_table_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e74904f1e6e5dba9531be9c242835b8575d1414c52bbe2797073d8398ac6d7f1)
            check_type(argname="argument dynamo_table_props", value=dynamo_table_props, expected_type=type_hints["dynamo_table_props"])
            check_type(argname="argument existing_table_interface", value=existing_table_interface, expected_type=type_hints["existing_table_interface"])
            check_type(argname="argument existing_table_obj", value=existing_table_obj, expected_type=type_hints["existing_table_obj"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if existing_table_interface is not None:
            self._values["existing_table_interface"] = existing_table_interface
        if existing_table_obj is not None:
            self._values["existing_table_obj"] = existing_table_obj

    @builtins.property
    def dynamo_table_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_table_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps], result)

    @builtins.property
    def existing_table_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        '''Existing instance of dynamodb interface.

        Providing both this and ``dynamoTableProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_table_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], result)

    @builtins.property
    def existing_table_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        '''Existing instance of dynamodb table object.

        Providing both this and ``dynamoTableProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_table_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildDynamoDBTableProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildDynamoDBTableResponse",
    jsii_struct_bases=[],
    name_mapping={"table_interface": "tableInterface", "table_object": "tableObject"},
)
class BuildDynamoDBTableResponse:
    def __init__(
        self,
        *,
        table_interface: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
        table_object: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    ) -> None:
        '''
        :param table_interface: -
        :param table_object: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d34caa67dda9b88eb51123471b0d296b6cb3b7f0c31ae08fa986cd195fa0acb)
            check_type(argname="argument table_interface", value=table_interface, expected_type=type_hints["table_interface"])
            check_type(argname="argument table_object", value=table_object, expected_type=type_hints["table_object"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table_interface": table_interface,
        }
        if table_object is not None:
            self._values["table_object"] = table_object

    @builtins.property
    def table_interface(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
        result = self._values.get("table_interface")
        assert result is not None, "Required property 'table_interface' is missing"
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, result)

    @builtins.property
    def table_object(self) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        result = self._values.get("table_object")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildDynamoDBTableResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildDynamoDBTableWithStreamProps",
    jsii_struct_bases=[],
    name_mapping={
        "dynamo_table_props": "dynamoTableProps",
        "existing_table_interface": "existingTableInterface",
    },
)
class BuildDynamoDBTableWithStreamProps:
    def __init__(
        self,
        *,
        dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_table_interface: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    ) -> None:
        '''
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_table_interface: Existing instance of dynamodb table object. Providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        '''
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = _aws_cdk_aws_dynamodb_ceddda9d.TableProps(**dynamo_table_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ab56403f4230368f270729e5586f7c282b901515ba0d833253c7c5934ac0f22)
            check_type(argname="argument dynamo_table_props", value=dynamo_table_props, expected_type=type_hints["dynamo_table_props"])
            check_type(argname="argument existing_table_interface", value=existing_table_interface, expected_type=type_hints["existing_table_interface"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if existing_table_interface is not None:
            self._values["existing_table_interface"] = existing_table_interface

    @builtins.property
    def dynamo_table_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_table_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps], result)

    @builtins.property
    def existing_table_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        '''Existing instance of dynamodb table object.

        Providing both this and ``dynamoTableProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_table_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildDynamoDBTableWithStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildDynamoDBTableWithStreamResponse",
    jsii_struct_bases=[],
    name_mapping={"table_interface": "tableInterface", "table_object": "tableObject"},
)
class BuildDynamoDBTableWithStreamResponse:
    def __init__(
        self,
        *,
        table_interface: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
        table_object: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    ) -> None:
        '''
        :param table_interface: -
        :param table_object: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__981983a3a87f559d92cb27756fba1d1d2d62daa4883bbb2f52de4d7ec73c647c)
            check_type(argname="argument table_interface", value=table_interface, expected_type=type_hints["table_interface"])
            check_type(argname="argument table_object", value=table_object, expected_type=type_hints["table_object"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table_interface": table_interface,
        }
        if table_object is not None:
            self._values["table_object"] = table_object

    @builtins.property
    def table_interface(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
        result = self._values.get("table_interface")
        assert result is not None, "Required property 'table_interface' is missing"
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, result)

    @builtins.property
    def table_object(self) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        result = self._values.get("table_object")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildDynamoDBTableWithStreamResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildElasticSearchProps",
    jsii_struct_bases=[],
    name_mapping={
        "cognito_authorized_role_arn": "cognitoAuthorizedRoleARN",
        "domain_name": "domainName",
        "identitypool": "identitypool",
        "userpool": "userpool",
        "client_domain_props": "clientDomainProps",
        "security_group_ids": "securityGroupIds",
        "service_role_arn": "serviceRoleARN",
        "vpc": "vpc",
    },
)
class BuildElasticSearchProps:
    def __init__(
        self,
        *,
        cognito_authorized_role_arn: builtins.str,
        domain_name: builtins.str,
        identitypool: _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool,
        userpool: _aws_cdk_aws_cognito_ceddda9d.UserPool,
        client_domain_props: typing.Optional[typing.Union[_aws_cdk_aws_elasticsearch_ceddda9d.CfnDomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_role_arn: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param cognito_authorized_role_arn: -
        :param domain_name: -
        :param identitypool: -
        :param userpool: -
        :param client_domain_props: -
        :param security_group_ids: -
        :param service_role_arn: -
        :param vpc: -
        '''
        if isinstance(client_domain_props, dict):
            client_domain_props = _aws_cdk_aws_elasticsearch_ceddda9d.CfnDomainProps(**client_domain_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ace54adaedb6afb446007117f1c60c4ced465e1865ffe38a2282ebf8ccec8f9)
            check_type(argname="argument cognito_authorized_role_arn", value=cognito_authorized_role_arn, expected_type=type_hints["cognito_authorized_role_arn"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument identitypool", value=identitypool, expected_type=type_hints["identitypool"])
            check_type(argname="argument userpool", value=userpool, expected_type=type_hints["userpool"])
            check_type(argname="argument client_domain_props", value=client_domain_props, expected_type=type_hints["client_domain_props"])
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument service_role_arn", value=service_role_arn, expected_type=type_hints["service_role_arn"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cognito_authorized_role_arn": cognito_authorized_role_arn,
            "domain_name": domain_name,
            "identitypool": identitypool,
            "userpool": userpool,
        }
        if client_domain_props is not None:
            self._values["client_domain_props"] = client_domain_props
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if service_role_arn is not None:
            self._values["service_role_arn"] = service_role_arn
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cognito_authorized_role_arn(self) -> builtins.str:
        result = self._values.get("cognito_authorized_role_arn")
        assert result is not None, "Required property 'cognito_authorized_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identitypool(self) -> _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool:
        result = self._values.get("identitypool")
        assert result is not None, "Required property 'identitypool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool, result)

    @builtins.property
    def userpool(self) -> _aws_cdk_aws_cognito_ceddda9d.UserPool:
        result = self._values.get("userpool")
        assert result is not None, "Required property 'userpool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.UserPool, result)

    @builtins.property
    def client_domain_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticsearch_ceddda9d.CfnDomainProps]:
        result = self._values.get("client_domain_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticsearch_ceddda9d.CfnDomainProps], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service_role_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("service_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildElasticSearchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildElasticSearchResponse",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain", "role": "role"},
)
class BuildElasticSearchResponse:
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_elasticsearch_ceddda9d.CfnDomain,
        role: _aws_cdk_aws_iam_ceddda9d.Role,
    ) -> None:
        '''
        :param domain: -
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35cc08d7e5c8cecd67f63cd630d2213224a588f2ef2baa8b0b71d4cc78b68286)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "role": role,
        }

    @builtins.property
    def domain(self) -> _aws_cdk_aws_elasticsearch_ceddda9d.CfnDomain:
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_elasticsearch_ceddda9d.CfnDomain, result)

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildElasticSearchResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildEventBusProps",
    jsii_struct_bases=[],
    name_mapping={
        "event_bus_props": "eventBusProps",
        "existing_event_bus_interface": "existingEventBusInterface",
    },
)
class BuildEventBusProps:
    def __init__(
        self,
        *,
        event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_event_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    ) -> None:
        '''
        :param event_bus_props: Optional user provided props to override the default props for the SNS topic. Default: - Default props are used.
        :param existing_event_bus_interface: Existing instance of SNS Topic object, providing both this and ``topicProps`` will cause an error. Default: - None.
        '''
        if isinstance(event_bus_props, dict):
            event_bus_props = _aws_cdk_aws_events_ceddda9d.EventBusProps(**event_bus_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__402df10e46ea685c3374efa6de25289f47ef9eea04092ab007b597af4696fe41)
            check_type(argname="argument event_bus_props", value=event_bus_props, expected_type=type_hints["event_bus_props"])
            check_type(argname="argument existing_event_bus_interface", value=existing_event_bus_interface, expected_type=type_hints["existing_event_bus_interface"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if event_bus_props is not None:
            self._values["event_bus_props"] = event_bus_props
        if existing_event_bus_interface is not None:
            self._values["existing_event_bus_interface"] = existing_event_bus_interface

    @builtins.property
    def event_bus_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBusProps]:
        '''Optional user provided props to override the default props for the SNS topic.

        :default: - Default props are used.
        '''
        result = self._values.get("event_bus_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBusProps], result)

    @builtins.property
    def existing_event_bus_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''Existing instance of SNS Topic object, providing both this and ``topicProps`` will cause an error.

        :default: - None.
        '''
        result = self._values.get("existing_event_bus_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildEventBusProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildGlueJobProps",
    jsii_struct_bases=[],
    name_mapping={
        "database": "database",
        "table": "table",
        "etl_code_asset": "etlCodeAsset",
        "existing_cfn_job": "existingCfnJob",
        "glue_job_props": "glueJobProps",
        "output_data_store": "outputDataStore",
    },
)
class BuildGlueJobProps:
    def __init__(
        self,
        *,
        database: _aws_cdk_aws_glue_ceddda9d.CfnDatabase,
        table: _aws_cdk_aws_glue_ceddda9d.CfnTable,
        etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        existing_cfn_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
        glue_job_props: typing.Any = None,
        output_data_store: typing.Optional[typing.Union["SinkDataStoreProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param database: AWS Glue database.
        :param table: AWS Glue table.
        :param etl_code_asset: Asset instance for the ETL code that performs Glue Job transformation. Default: - None
        :param existing_cfn_job: Existing instance of the S3 bucket object, if this is set then the script location is ignored.
        :param glue_job_props: Glue ETL job properties.
        :param output_data_store: Output storage options.
        '''
        if isinstance(output_data_store, dict):
            output_data_store = SinkDataStoreProps(**output_data_store)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf8f7cc42528bcc97b5baee443c3a742df7508c5f8a6f86fb48eee982b13dfa)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
            check_type(argname="argument etl_code_asset", value=etl_code_asset, expected_type=type_hints["etl_code_asset"])
            check_type(argname="argument existing_cfn_job", value=existing_cfn_job, expected_type=type_hints["existing_cfn_job"])
            check_type(argname="argument glue_job_props", value=glue_job_props, expected_type=type_hints["glue_job_props"])
            check_type(argname="argument output_data_store", value=output_data_store, expected_type=type_hints["output_data_store"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database": database,
            "table": table,
        }
        if etl_code_asset is not None:
            self._values["etl_code_asset"] = etl_code_asset
        if existing_cfn_job is not None:
            self._values["existing_cfn_job"] = existing_cfn_job
        if glue_job_props is not None:
            self._values["glue_job_props"] = glue_job_props
        if output_data_store is not None:
            self._values["output_data_store"] = output_data_store

    @builtins.property
    def database(self) -> _aws_cdk_aws_glue_ceddda9d.CfnDatabase:
        '''AWS Glue database.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnDatabase, result)

    @builtins.property
    def table(self) -> _aws_cdk_aws_glue_ceddda9d.CfnTable:
        '''AWS Glue table.'''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnTable, result)

    @builtins.property
    def etl_code_asset(self) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        '''Asset instance for the ETL code that performs Glue Job transformation.

        :default: - None
        '''
        result = self._values.get("etl_code_asset")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], result)

    @builtins.property
    def existing_cfn_job(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob]:
        '''Existing instance of the S3 bucket object, if this is set then the script location is ignored.'''
        result = self._values.get("existing_cfn_job")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob], result)

    @builtins.property
    def glue_job_props(self) -> typing.Any:
        '''Glue ETL job properties.'''
        result = self._values.get("glue_job_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def output_data_store(self) -> typing.Optional["SinkDataStoreProps"]:
        '''Output storage options.'''
        result = self._values.get("output_data_store")
        return typing.cast(typing.Optional["SinkDataStoreProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildGlueJobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildGlueJobResponse",
    jsii_struct_bases=[],
    name_mapping={
        "job": "job",
        "role": "role",
        "bucket": "bucket",
        "logging_bucket": "loggingBucket",
    },
)
class BuildGlueJobResponse:
    def __init__(
        self,
        *,
        job: _aws_cdk_aws_glue_ceddda9d.CfnJob,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    ) -> None:
        '''
        :param job: -
        :param role: -
        :param bucket: -
        :param logging_bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11a604b08bf1cad91185d9f9c8a5a6d00078574c65293412cd1679923fd362f8)
            check_type(argname="argument job", value=job, expected_type=type_hints["job"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument logging_bucket", value=logging_bucket, expected_type=type_hints["logging_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "job": job,
            "role": role,
        }
        if bucket is not None:
            self._values["bucket"] = bucket
        if logging_bucket is not None:
            self._values["logging_bucket"] = logging_bucket

    @builtins.property
    def job(self) -> _aws_cdk_aws_glue_ceddda9d.CfnJob:
        result = self._values.get("job")
        assert result is not None, "Required property 'job' is missing"
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnJob, result)

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def logging_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildGlueJobResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildKendraIndexProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_index_obj": "existingIndexObj",
        "kendra_index_props": "kendraIndexProps",
    },
)
class BuildKendraIndexProps:
    def __init__(
        self,
        *,
        existing_index_obj: typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex] = None,
        kendra_index_props: typing.Any = None,
    ) -> None:
        '''
        :param existing_index_obj: Existing instance of Kendra Index object, Providing both this and kendraIndexProps will cause an error. Default: - None
        :param kendra_index_props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97248fcc6a2ae901e8446e8b76807bca4718121ad43df2905dd67d4e945615dc)
            check_type(argname="argument existing_index_obj", value=existing_index_obj, expected_type=type_hints["existing_index_obj"])
            check_type(argname="argument kendra_index_props", value=kendra_index_props, expected_type=type_hints["kendra_index_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_index_obj is not None:
            self._values["existing_index_obj"] = existing_index_obj
        if kendra_index_props is not None:
            self._values["kendra_index_props"] = kendra_index_props

    @builtins.property
    def existing_index_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex]:
        '''Existing instance of Kendra Index object, Providing both this and kendraIndexProps will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_index_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex], result)

    @builtins.property
    def kendra_index_props(self) -> typing.Any:
        result = self._values.get("kendra_index_props")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildKendraIndexProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildKinesisAnalyticsAppProps",
    jsii_struct_bases=[],
    name_mapping={
        "kinesis_firehose": "kinesisFirehose",
        "kinesis_analytics_props": "kinesisAnalyticsProps",
    },
)
class BuildKinesisAnalyticsAppProps:
    def __init__(
        self,
        *,
        kinesis_firehose: _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream,
        kinesis_analytics_props: typing.Any = None,
    ) -> None:
        '''
        :param kinesis_firehose: A Kinesis Data Firehose for the Kinesis Streams application to connect to. Default: - Default props are used
        :param kinesis_analytics_props: Optional user provided props to override the default props for the Kinesis analytics app. Default: - Default props are used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d782131c01b404df6d09dce3e6a0b081487eeabfad4dcf5bf9b8675f66aaa00b)
            check_type(argname="argument kinesis_firehose", value=kinesis_firehose, expected_type=type_hints["kinesis_firehose"])
            check_type(argname="argument kinesis_analytics_props", value=kinesis_analytics_props, expected_type=type_hints["kinesis_analytics_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "kinesis_firehose": kinesis_firehose,
        }
        if kinesis_analytics_props is not None:
            self._values["kinesis_analytics_props"] = kinesis_analytics_props

    @builtins.property
    def kinesis_firehose(
        self,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream:
        '''A Kinesis Data Firehose for the Kinesis Streams application to connect to.

        :default: - Default props are used
        '''
        result = self._values.get("kinesis_firehose")
        assert result is not None, "Required property 'kinesis_firehose' is missing"
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream, result)

    @builtins.property
    def kinesis_analytics_props(self) -> typing.Any:
        '''Optional user provided props to override the default props for the Kinesis analytics app.

        :default: - Default props are used
        '''
        result = self._values.get("kinesis_analytics_props")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildKinesisAnalyticsAppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildKinesisStreamProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_stream_obj": "existingStreamObj",
        "kinesis_stream_props": "kinesisStreamProps",
    },
)
class BuildKinesisStreamProps:
    def __init__(
        self,
        *,
        existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
        kinesis_stream_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesis_ceddda9d.StreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param existing_stream_obj: Existing instance of Kinesis Stream, providing both this and ``kinesisStreamProps`` will cause an error. Default: - None
        :param kinesis_stream_props: Optional user provided props to override the default props for the Kinesis stream. Default: - Default props are used.
        '''
        if isinstance(kinesis_stream_props, dict):
            kinesis_stream_props = _aws_cdk_aws_kinesis_ceddda9d.StreamProps(**kinesis_stream_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d293590656a573587342e1cafc604c4eac77ead41a7bdf61115acb332a86bef)
            check_type(argname="argument existing_stream_obj", value=existing_stream_obj, expected_type=type_hints["existing_stream_obj"])
            check_type(argname="argument kinesis_stream_props", value=kinesis_stream_props, expected_type=type_hints["kinesis_stream_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_stream_obj is not None:
            self._values["existing_stream_obj"] = existing_stream_obj
        if kinesis_stream_props is not None:
            self._values["kinesis_stream_props"] = kinesis_stream_props

    @builtins.property
    def existing_stream_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream]:
        '''Existing instance of Kinesis Stream, providing both this and ``kinesisStreamProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_stream_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream], result)

    @builtins.property
    def kinesis_stream_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.StreamProps]:
        '''Optional user provided props to override the default props for the Kinesis stream.

        :default: - Default props are used.
        '''
        result = self._values.get("kinesis_stream_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.StreamProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildKinesisStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildLambdaFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_lambda_obj": "existingLambdaObj",
        "lambda_function_props": "lambdaFunctionProps",
        "vpc": "vpc",
    },
)
class BuildLambdaFunctionProps:
    def __init__(
        self,
        *,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param existing_lambda_obj: Existing instance of Lambda Function object, Providing both this and lambdaFunctionProps will cause an error. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param vpc: A VPC where the Lambda function will access internal resources. Default: - none
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c909e838eec4699e3b2bf33068f24227227f2e29c58156725d344e7b43ce564c)
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def existing_lambda_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''Existing instance of Lambda Function object, Providing both this and lambdaFunctionProps will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default props are used
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''A VPC where the Lambda function will access internal resources.

        :default: - none
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildLambdaFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildOpenSearchProps",
    jsii_struct_bases=[],
    name_mapping={
        "cognito_authorized_role_arn": "cognitoAuthorizedRoleARN",
        "identitypool": "identitypool",
        "open_search_domain_name": "openSearchDomainName",
        "userpool": "userpool",
        "client_domain_props": "clientDomainProps",
        "security_group_ids": "securityGroupIds",
        "service_role_arn": "serviceRoleARN",
        "vpc": "vpc",
    },
)
class BuildOpenSearchProps:
    def __init__(
        self,
        *,
        cognito_authorized_role_arn: builtins.str,
        identitypool: _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool,
        open_search_domain_name: builtins.str,
        userpool: _aws_cdk_aws_cognito_ceddda9d.UserPool,
        client_domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_role_arn: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param cognito_authorized_role_arn: -
        :param identitypool: -
        :param open_search_domain_name: -
        :param userpool: -
        :param client_domain_props: -
        :param security_group_ids: -
        :param service_role_arn: -
        :param vpc: -
        '''
        if isinstance(client_domain_props, dict):
            client_domain_props = _aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps(**client_domain_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99d575e7df229e6d535706fb7d502e7c815c863d7890f8d5daa6349619ba52f6)
            check_type(argname="argument cognito_authorized_role_arn", value=cognito_authorized_role_arn, expected_type=type_hints["cognito_authorized_role_arn"])
            check_type(argname="argument identitypool", value=identitypool, expected_type=type_hints["identitypool"])
            check_type(argname="argument open_search_domain_name", value=open_search_domain_name, expected_type=type_hints["open_search_domain_name"])
            check_type(argname="argument userpool", value=userpool, expected_type=type_hints["userpool"])
            check_type(argname="argument client_domain_props", value=client_domain_props, expected_type=type_hints["client_domain_props"])
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument service_role_arn", value=service_role_arn, expected_type=type_hints["service_role_arn"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cognito_authorized_role_arn": cognito_authorized_role_arn,
            "identitypool": identitypool,
            "open_search_domain_name": open_search_domain_name,
            "userpool": userpool,
        }
        if client_domain_props is not None:
            self._values["client_domain_props"] = client_domain_props
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if service_role_arn is not None:
            self._values["service_role_arn"] = service_role_arn
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cognito_authorized_role_arn(self) -> builtins.str:
        result = self._values.get("cognito_authorized_role_arn")
        assert result is not None, "Required property 'cognito_authorized_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identitypool(self) -> _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool:
        result = self._values.get("identitypool")
        assert result is not None, "Required property 'identitypool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool, result)

    @builtins.property
    def open_search_domain_name(self) -> builtins.str:
        result = self._values.get("open_search_domain_name")
        assert result is not None, "Required property 'open_search_domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def userpool(self) -> _aws_cdk_aws_cognito_ceddda9d.UserPool:
        result = self._values.get("userpool")
        assert result is not None, "Required property 'userpool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.UserPool, result)

    @builtins.property
    def client_domain_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps]:
        result = self._values.get("client_domain_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service_role_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("service_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildOpenSearchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildOpenSearchResponse",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain", "role": "role"},
)
class BuildOpenSearchResponse:
    def __init__(
        self,
        *,
        domain: _aws_cdk_aws_opensearchservice_ceddda9d.CfnDomain,
        role: _aws_cdk_aws_iam_ceddda9d.Role,
    ) -> None:
        '''
        :param domain: -
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__999af291cbe0b3ac93ce7fcd7ec44dc0cc2fba2cea7bfa0fb68b20e641effee2)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "role": role,
        }

    @builtins.property
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.CfnDomain:
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomain, result)

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildOpenSearchResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildQueueProps",
    jsii_struct_bases=[],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "enable_encryption_with_customer_managed_key": "enableEncryptionWithCustomerManagedKey",
        "encryption_key": "encryptionKey",
        "encryption_key_props": "encryptionKeyProps",
        "existing_queue_obj": "existingQueueObj",
        "queue_props": "queueProps",
    },
)
class BuildQueueProps:
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dead_letter_queue: Optional dead letter queue to pass bad requests to after the max receive count is reached. Default: - Default props are used.
        :param enable_encryption_with_customer_managed_key: If no key is provided, this flag determines whether the queue is encrypted with a new CMK or an AWS managed key. This flag is ignored if any of the following are defined: queueProps.encryptionMasterKey, encryptionKey or encryptionKeyProps. Default: - False if queueProps.encryptionMasterKey, encryptionKey, and encryptionKeyProps are all undefined.
        :param encryption_key: An optional, imported encryption key to encrypt the SQS Queue with. Default: - None
        :param encryption_key_props: Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SQS Queue with. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, providing both this and queueProps will cause an error. Default: - None.
        :param queue_props: Optional user provided props to override the default props for the primary queue. Default: - Default props are used.
        '''
        if isinstance(dead_letter_queue, dict):
            dead_letter_queue = _aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue(**dead_letter_queue)
        if isinstance(encryption_key_props, dict):
            encryption_key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**encryption_key_props)
        if isinstance(queue_props, dict):
            queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**queue_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6b0628b99348c4f52c56911b1d1df16b203612119c6a5d046c912ca315ff851)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument enable_encryption_with_customer_managed_key", value=enable_encryption_with_customer_managed_key, expected_type=type_hints["enable_encryption_with_customer_managed_key"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument encryption_key_props", value=encryption_key_props, expected_type=type_hints["encryption_key_props"])
            check_type(argname="argument existing_queue_obj", value=existing_queue_obj, expected_type=type_hints["existing_queue_obj"])
            check_type(argname="argument queue_props", value=queue_props, expected_type=type_hints["queue_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if enable_encryption_with_customer_managed_key is not None:
            self._values["enable_encryption_with_customer_managed_key"] = enable_encryption_with_customer_managed_key
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_key_props is not None:
            self._values["encryption_key_props"] = encryption_key_props
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if queue_props is not None:
            self._values["queue_props"] = queue_props

    @builtins.property
    def dead_letter_queue(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue]:
        '''Optional dead letter queue to pass bad requests to after the max receive count is reached.

        :default: - Default props are used.
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue], result)

    @builtins.property
    def enable_encryption_with_customer_managed_key(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''If no key is provided, this flag determines whether the queue is encrypted with a new CMK or an AWS managed key.

        This flag is ignored if any of the following are defined: queueProps.encryptionMasterKey, encryptionKey or encryptionKeyProps.

        :default: - False if queueProps.encryptionMasterKey, encryptionKey, and encryptionKeyProps are all undefined.
        '''
        result = self._values.get("enable_encryption_with_customer_managed_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''An optional, imported encryption key to encrypt the SQS Queue with.

        :default: - None
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def encryption_key_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        '''Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SQS Queue with.

        :default: - None
        '''
        result = self._values.get("encryption_key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        '''Existing instance of SQS queue object, providing both this and queueProps will cause an error.

        :default: - None.
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        '''Optional user provided props to override the default props for the primary queue.

        :default: - Default props are used.
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildQueueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildQueueResponse",
    jsii_struct_bases=[],
    name_mapping={"queue": "queue", "key": "key"},
)
class BuildQueueResponse:
    def __init__(
        self,
        *,
        queue: _aws_cdk_aws_sqs_ceddda9d.Queue,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> None:
        '''
        :param queue: -
        :param key: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a8eceeccf20ddfc7f75482ccc95d2cd1f427caa71417210872f02f26beeb4eb)
            check_type(argname="argument queue", value=queue, expected_type=type_hints["queue"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "queue": queue,
        }
        if key is not None:
            self._values["key"] = key

    @builtins.property
    def queue(self) -> _aws_cdk_aws_sqs_ceddda9d.Queue:
        result = self._values.get("queue")
        assert result is not None, "Required property 'queue' is missing"
        return typing.cast(_aws_cdk_aws_sqs_ceddda9d.Queue, result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildQueueResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildS3BucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_props": "bucketProps",
        "logging_bucket_props": "loggingBucketProps",
        "log_s3_access_logs": "logS3AccessLogs",
    },
)
class BuildS3BucketProps:
    def __init__(
        self,
        *,
        bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param bucket_props: User provided props to override the default props for the S3 Bucket. Default: - Default props are used
        :param logging_bucket_props: User provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for S3. Uses an S3 bucket with associated storage costs. Enabling Access Logging is a best practice. Default: - true
        '''
        if isinstance(bucket_props, dict):
            bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_props)
        if isinstance(logging_bucket_props, dict):
            logging_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**logging_bucket_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__477f8910cdb0bca2545f20be9fd9a69e561013fbe00f14e8780f43e3b607f732)
            check_type(argname="argument bucket_props", value=bucket_props, expected_type=type_hints["bucket_props"])
            check_type(argname="argument logging_bucket_props", value=logging_bucket_props, expected_type=type_hints["logging_bucket_props"])
            check_type(argname="argument log_s3_access_logs", value=log_s3_access_logs, expected_type=type_hints["log_s3_access_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_props is not None:
            self._values["bucket_props"] = bucket_props
        if logging_bucket_props is not None:
            self._values["logging_bucket_props"] = logging_bucket_props
        if log_s3_access_logs is not None:
            self._values["log_s3_access_logs"] = log_s3_access_logs

    @builtins.property
    def bucket_props(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''User provided props to override the default props for the S3 Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def logging_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''User provided props to override the default props for the S3 Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("logging_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def log_s3_access_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether to turn on Access Logs for S3.

        Uses an S3 bucket with associated storage costs.
        Enabling Access Logging is a best practice.

        :default: - true
        '''
        result = self._values.get("log_s3_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildS3BucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildS3BucketResponse",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "logging_bucket": "loggingBucket"},
)
class BuildS3BucketResponse:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
        logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    ) -> None:
        '''
        :param bucket: -
        :param logging_bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbb87cbe234079b3231368effad74ccd4f3add89bedc907550a84d27b74ccf1f)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument logging_bucket", value=logging_bucket, expected_type=type_hints["logging_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if logging_bucket is not None:
            self._values["logging_bucket"] = logging_bucket

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, result)

    @builtins.property
    def logging_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildS3BucketResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildSagemakerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_config_props": "endpointConfigProps",
        "endpoint_props": "endpointProps",
        "existing_sagemaker_endpoint_obj": "existingSagemakerEndpointObj",
        "model_props": "modelProps",
        "vpc": "vpc",
    },
)
class BuildSagemakerEndpointProps:
    def __init__(
        self,
        *,
        endpoint_config_props: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfigProps, typing.Dict[builtins.str, typing.Any]]] = None,
        endpoint_props: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_sagemaker_endpoint_obj: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint] = None,
        model_props: typing.Any = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param endpoint_config_props: User provided props to create Sagemaker Endpoint Configuration. Default: - None
        :param endpoint_props: User provided props to create Sagemaker Endpoint. Default: - None
        :param existing_sagemaker_endpoint_obj: Existing Sagemaker Endpoint object, if this is set then the modelProps, endpointConfigProps, and endpointProps are ignored. Default: - None
        :param model_props: User provided props to create Sagemaker Model. Default: - None
        :param vpc: A VPC where the Sagemaker Endpoint will be placed. Default: - None
        '''
        if isinstance(endpoint_config_props, dict):
            endpoint_config_props = _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfigProps(**endpoint_config_props)
        if isinstance(endpoint_props, dict):
            endpoint_props = _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps(**endpoint_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5fde21b1134934aa7c14818fc1bd40b664570c8ff0c7162e476f19f197b2ea4)
            check_type(argname="argument endpoint_config_props", value=endpoint_config_props, expected_type=type_hints["endpoint_config_props"])
            check_type(argname="argument endpoint_props", value=endpoint_props, expected_type=type_hints["endpoint_props"])
            check_type(argname="argument existing_sagemaker_endpoint_obj", value=existing_sagemaker_endpoint_obj, expected_type=type_hints["existing_sagemaker_endpoint_obj"])
            check_type(argname="argument model_props", value=model_props, expected_type=type_hints["model_props"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if endpoint_config_props is not None:
            self._values["endpoint_config_props"] = endpoint_config_props
        if endpoint_props is not None:
            self._values["endpoint_props"] = endpoint_props
        if existing_sagemaker_endpoint_obj is not None:
            self._values["existing_sagemaker_endpoint_obj"] = existing_sagemaker_endpoint_obj
        if model_props is not None:
            self._values["model_props"] = model_props
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def endpoint_config_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfigProps]:
        '''User provided props to create Sagemaker Endpoint Configuration.

        :default: - None
        '''
        result = self._values.get("endpoint_config_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfigProps], result)

    @builtins.property
    def endpoint_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps]:
        '''User provided props to create Sagemaker Endpoint.

        :default: - None
        '''
        result = self._values.get("endpoint_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps], result)

    @builtins.property
    def existing_sagemaker_endpoint_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint]:
        '''Existing Sagemaker Endpoint object, if this is set then the modelProps, endpointConfigProps, and endpointProps are ignored.

        :default: - None
        '''
        result = self._values.get("existing_sagemaker_endpoint_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint], result)

    @builtins.property
    def model_props(self) -> typing.Any:
        '''User provided props to create Sagemaker Model.

        :default: - None
        '''
        result = self._values.get("model_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''A VPC where the Sagemaker Endpoint will be placed.

        :default: - None
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildSagemakerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildSagemakerEndpointResponse",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint": "endpoint",
        "endpoint_config": "endpointConfig",
        "model": "model",
    },
)
class BuildSagemakerEndpointResponse:
    def __init__(
        self,
        *,
        endpoint: _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint,
        endpoint_config: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig] = None,
        model: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel] = None,
    ) -> None:
        '''
        :param endpoint: -
        :param endpoint_config: -
        :param model: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbc439cfcc9233f3830549ca49591814eb1a90e5ff9306cc080d2433ac634b42)
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument endpoint_config", value=endpoint_config, expected_type=type_hints["endpoint_config"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "endpoint": endpoint,
        }
        if endpoint_config is not None:
            self._values["endpoint_config"] = endpoint_config
        if model is not None:
            self._values["model"] = model

    @builtins.property
    def endpoint(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint:
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint, result)

    @builtins.property
    def endpoint_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig]:
        result = self._values.get("endpoint_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig], result)

    @builtins.property
    def model(self) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel]:
        result = self._values.get("model")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildSagemakerEndpointResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildSagemakerNotebookProps",
    jsii_struct_bases=[],
    name_mapping={
        "role": "role",
        "deploy_inside_vpc": "deployInsideVpc",
        "existing_notebook_obj": "existingNotebookObj",
        "sagemaker_notebook_props": "sagemakerNotebookProps",
    },
)
class BuildSagemakerNotebookProps:
    def __init__(
        self,
        *,
        role: _aws_cdk_aws_iam_ceddda9d.Role,
        deploy_inside_vpc: typing.Optional[builtins.bool] = None,
        existing_notebook_obj: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance] = None,
        sagemaker_notebook_props: typing.Any = None,
    ) -> None:
        '''
        :param role: IAM Role Arn for Sagemaker NoteBookInstance. Default: - None
        :param deploy_inside_vpc: Optional user provided props to deploy inside vpc. Default: - true
        :param existing_notebook_obj: An optional, Existing instance of notebook object. If this is set then the sagemakerNotebookProps is ignored Default: - None
        :param sagemaker_notebook_props: Optional user provided props for CfnNotebookInstanceProps. Default: - Default props are used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3f078a7bfd43b5d1505dfb95fd8d25b125648f08a25e307fc3bfeeb5122665c)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument deploy_inside_vpc", value=deploy_inside_vpc, expected_type=type_hints["deploy_inside_vpc"])
            check_type(argname="argument existing_notebook_obj", value=existing_notebook_obj, expected_type=type_hints["existing_notebook_obj"])
            check_type(argname="argument sagemaker_notebook_props", value=sagemaker_notebook_props, expected_type=type_hints["sagemaker_notebook_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
        }
        if deploy_inside_vpc is not None:
            self._values["deploy_inside_vpc"] = deploy_inside_vpc
        if existing_notebook_obj is not None:
            self._values["existing_notebook_obj"] = existing_notebook_obj
        if sagemaker_notebook_props is not None:
            self._values["sagemaker_notebook_props"] = sagemaker_notebook_props

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''IAM Role Arn for Sagemaker NoteBookInstance.

        :default: - None
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    @builtins.property
    def deploy_inside_vpc(self) -> typing.Optional[builtins.bool]:
        '''Optional user provided props to deploy inside vpc.

        :default: - true
        '''
        result = self._values.get("deploy_inside_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_notebook_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance]:
        '''An optional, Existing instance of notebook object.

        If this is set then the sagemakerNotebookProps is ignored

        :default: - None
        '''
        result = self._values.get("existing_notebook_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance], result)

    @builtins.property
    def sagemaker_notebook_props(self) -> typing.Any:
        '''Optional user provided props for CfnNotebookInstanceProps.

        :default: - Default props are used
        '''
        result = self._values.get("sagemaker_notebook_props")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildSagemakerNotebookProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildSagemakerNotebookResponse",
    jsii_struct_bases=[],
    name_mapping={
        "notebook": "notebook",
        "security_group": "securityGroup",
        "vpc": "vpc",
    },
)
class BuildSagemakerNotebookResponse:
    def __init__(
        self,
        *,
        notebook: _aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param notebook: -
        :param security_group: -
        :param vpc: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64202e3614dc62b35135f3089b90c18a208eff665aed57af301adc2b47fe7565)
            check_type(argname="argument notebook", value=notebook, expected_type=type_hints["notebook"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "notebook": notebook,
        }
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def notebook(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance:
        result = self._values.get("notebook")
        assert result is not None, "Required property 'notebook' is missing"
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]:
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildSagemakerNotebookResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildStateMachineResponse",
    jsii_struct_bases=[],
    name_mapping={"log_group": "logGroup", "state_machine": "stateMachine"},
)
class BuildStateMachineResponse:
    def __init__(
        self,
        *,
        log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
    ) -> None:
        '''
        :param log_group: -
        :param state_machine: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59bc37dbb01994ff547e71caebd074472187780f69d4ea13ee1b5dcb608c782b)
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "log_group": log_group,
            "state_machine": state_machine,
        }

    @builtins.property
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        result = self._values.get("log_group")
        assert result is not None, "Required property 'log_group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, result)

    @builtins.property
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildStateMachineResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildTopicProps",
    jsii_struct_bases=[],
    name_mapping={
        "enable_encryption_with_customer_managed_key": "enableEncryptionWithCustomerManagedKey",
        "encryption_key": "encryptionKey",
        "encryption_key_props": "encryptionKeyProps",
        "existing_topic_encryption_key": "existingTopicEncryptionKey",
        "existing_topic_obj": "existingTopicObj",
        "topic_props": "topicProps",
    },
)
class BuildTopicProps:
    def __init__(
        self,
        *,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param enable_encryption_with_customer_managed_key: If no key is provided, this flag determines whether the topic is encrypted with a new CMK or an AWS managed key. This flag is ignored if any of the following are defined: topicProps.masterKey, encryptionKey or encryptionKeyProps. Default: - False if topicProps.masterKey, encryptionKey, and encryptionKeyProps are all undefined.
        :param encryption_key: An optional, imported encryption key to encrypt the SNS topic with. Default: - None
        :param encryption_key_props: Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SNS topic with. Default: - None
        :param existing_topic_encryption_key: If an existing topic is provided in the ``existingTopicObj`` property, and that topic is encrypted with a customer managed KMS key, this property also needs to be set with same CMK. Default: - None
        :param existing_topic_obj: Existing SNS topic to be used instead of the default topic. Providing both this and ``topicProps`` will cause an error. If the SNS Topic is encrypted with a Customer-Managed managed KMS key, the key must be specified in the ``existingTopicEncryptionKey`` property. Default: - Default props are used
        :param topic_props: Optional user provided props to override the default props for the SNS topic. Default: - Default props are used.
        '''
        if isinstance(encryption_key_props, dict):
            encryption_key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**encryption_key_props)
        if isinstance(topic_props, dict):
            topic_props = _aws_cdk_aws_sns_ceddda9d.TopicProps(**topic_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb734897393ecced90b642fd1b813f4d1e01378c0fc8a7edbfb24ede093d9db7)
            check_type(argname="argument enable_encryption_with_customer_managed_key", value=enable_encryption_with_customer_managed_key, expected_type=type_hints["enable_encryption_with_customer_managed_key"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument encryption_key_props", value=encryption_key_props, expected_type=type_hints["encryption_key_props"])
            check_type(argname="argument existing_topic_encryption_key", value=existing_topic_encryption_key, expected_type=type_hints["existing_topic_encryption_key"])
            check_type(argname="argument existing_topic_obj", value=existing_topic_obj, expected_type=type_hints["existing_topic_obj"])
            check_type(argname="argument topic_props", value=topic_props, expected_type=type_hints["topic_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enable_encryption_with_customer_managed_key is not None:
            self._values["enable_encryption_with_customer_managed_key"] = enable_encryption_with_customer_managed_key
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_key_props is not None:
            self._values["encryption_key_props"] = encryption_key_props
        if existing_topic_encryption_key is not None:
            self._values["existing_topic_encryption_key"] = existing_topic_encryption_key
        if existing_topic_obj is not None:
            self._values["existing_topic_obj"] = existing_topic_obj
        if topic_props is not None:
            self._values["topic_props"] = topic_props

    @builtins.property
    def enable_encryption_with_customer_managed_key(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''If no key is provided, this flag determines whether the topic is encrypted with a new CMK or an AWS managed key.

        This flag is ignored if any of the following are defined: topicProps.masterKey, encryptionKey or encryptionKeyProps.

        :default: - False if topicProps.masterKey, encryptionKey, and encryptionKeyProps are all undefined.
        '''
        result = self._values.get("enable_encryption_with_customer_managed_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''An optional, imported encryption key to encrypt the SNS topic with.

        :default: - None
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def encryption_key_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        '''Optional user provided properties to override the default properties for the KMS encryption key used to encrypt the SNS topic with.

        :default: - None
        '''
        result = self._values.get("encryption_key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def existing_topic_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''If an existing topic is provided in the ``existingTopicObj`` property, and that topic is encrypted with a customer managed KMS key, this property also needs to be set with same CMK.

        :default: - None
        '''
        result = self._values.get("existing_topic_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def existing_topic_obj(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic]:
        '''Existing SNS topic to be used instead of the default topic.

        Providing both this and ``topicProps`` will cause an error.
        If the SNS Topic is encrypted with a Customer-Managed managed KMS key, the key must be specified in the
        ``existingTopicEncryptionKey`` property.

        :default: - Default props are used
        '''
        result = self._values.get("existing_topic_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic], result)

    @builtins.property
    def topic_props(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps]:
        '''Optional user provided props to override the default props for the SNS topic.

        :default: - Default props are used.
        '''
        result = self._values.get("topic_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildTopicProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildTopicResponse",
    jsii_struct_bases=[],
    name_mapping={"topic": "topic", "key": "key"},
)
class BuildTopicResponse:
    def __init__(
        self,
        *,
        topic: _aws_cdk_aws_sns_ceddda9d.Topic,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    ) -> None:
        '''
        :param topic: -
        :param key: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36d2b4d1a520196266ff49496e619764cc478cfe3248684fd519c5c544c8d04)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "topic": topic,
        }
        if key is not None:
            self._values["key"] = key

    @builtins.property
    def topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildTopicResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildVpcProps",
    jsii_struct_bases=[],
    name_mapping={
        "default_vpc_props": "defaultVpcProps",
        "construct_vpc_props": "constructVpcProps",
        "existing_vpc": "existingVpc",
        "user_vpc_props": "userVpcProps",
    },
)
class BuildVpcProps:
    def __init__(
        self,
        *,
        default_vpc_props: typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]],
        construct_vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        user_vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param default_vpc_props: One of the default VPC configurations available in vpc-defaults.
        :param construct_vpc_props: Construct specified props that override both the default props and user props for the VPC.
        :param existing_vpc: Existing instance of a VPC, if this is set then the all Props are ignored.
        :param user_vpc_props: User provided props to override the default props for the VPC.
        '''
        if isinstance(default_vpc_props, dict):
            default_vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**default_vpc_props)
        if isinstance(construct_vpc_props, dict):
            construct_vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**construct_vpc_props)
        if isinstance(user_vpc_props, dict):
            user_vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**user_vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba77dacfeb009599df76f2f3981f0e9d35104df22ff4d1aea91142e42745ba51)
            check_type(argname="argument default_vpc_props", value=default_vpc_props, expected_type=type_hints["default_vpc_props"])
            check_type(argname="argument construct_vpc_props", value=construct_vpc_props, expected_type=type_hints["construct_vpc_props"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument user_vpc_props", value=user_vpc_props, expected_type=type_hints["user_vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "default_vpc_props": default_vpc_props,
        }
        if construct_vpc_props is not None:
            self._values["construct_vpc_props"] = construct_vpc_props
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if user_vpc_props is not None:
            self._values["user_vpc_props"] = user_vpc_props

    @builtins.property
    def default_vpc_props(self) -> _aws_cdk_aws_ec2_ceddda9d.VpcProps:
        '''One of the default VPC configurations available in vpc-defaults.'''
        result = self._values.get("default_vpc_props")
        assert result is not None, "Required property 'default_vpc_props' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.VpcProps, result)

    @builtins.property
    def construct_vpc_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''Construct specified props that override both the default props and user props for the VPC.'''
        result = self._values.get("construct_vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''Existing instance of a VPC, if this is set then the all Props are ignored.'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def user_vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        '''User provided props to override the default props for the VPC.'''
        result = self._values.get("user_vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.BuildWebaclProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_webacl_obj": "existingWebaclObj",
        "webacl_props": "webaclProps",
    },
)
class BuildWebaclProps:
    def __init__(
        self,
        *,
        existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
        webacl_props: typing.Any = None,
    ) -> None:
        '''
        :param existing_webacl_obj: Existing instance of a WAF web ACL, if this is set then the all props are ignored.
        :param webacl_props: User provided props to override the default ACL props for WAF web ACL.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c35365146428e8cffe0bebcbe653e04ec2c2fec9c6fb055fbc3578eb6721b7b)
            check_type(argname="argument existing_webacl_obj", value=existing_webacl_obj, expected_type=type_hints["existing_webacl_obj"])
            check_type(argname="argument webacl_props", value=webacl_props, expected_type=type_hints["webacl_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_webacl_obj is not None:
            self._values["existing_webacl_obj"] = existing_webacl_obj
        if webacl_props is not None:
            self._values["webacl_props"] = webacl_props

    @builtins.property
    def existing_webacl_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL]:
        '''Existing instance of a WAF web ACL, if this is set then the all props are ignored.'''
        result = self._values.get("existing_webacl_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL], result)

    @builtins.property
    def webacl_props(self) -> typing.Any:
        '''User provided props to override the default ACL props for WAF web ACL.'''
        result = self._values.get("webacl_props")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildWebaclProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CfnNagSuppressRule",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "reason": "reason"},
)
class CfnNagSuppressRule:
    def __init__(self, *, id: builtins.str, reason: builtins.str) -> None:
        '''The CFN NAG suppress rule interface.

        :param id: -
        :param reason: -

        :interface: CfnNagSuppressRule
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e488fbb31c8c315fca374532df51ff6ae1a4249bebed411f394e2ae3fb74eef0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "reason": reason,
        }

    @builtins.property
    def id(self) -> builtins.str:
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def reason(self) -> builtins.str:
        result = self._values.get("reason")
        assert result is not None, "Required property 'reason' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnNagSuppressRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CloudFrontDistributionForApiGatewayResponse",
    jsii_struct_bases=[],
    name_mapping={
        "distribution": "distribution",
        "cloudfront_function": "cloudfrontFunction",
        "logging_bucket": "loggingBucket",
    },
)
class CloudFrontDistributionForApiGatewayResponse:
    def __init__(
        self,
        *,
        distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
        cloudfront_function: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function] = None,
        logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    ) -> None:
        '''
        :param distribution: -
        :param cloudfront_function: -
        :param logging_bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28e9958969b69d0c97ca692c45e5f4cd38c0a074d7bc482888050927296c29ff)
            check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
            check_type(argname="argument cloudfront_function", value=cloudfront_function, expected_type=type_hints["cloudfront_function"])
            check_type(argname="argument logging_bucket", value=logging_bucket, expected_type=type_hints["logging_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "distribution": distribution,
        }
        if cloudfront_function is not None:
            self._values["cloudfront_function"] = cloudfront_function
        if logging_bucket is not None:
            self._values["logging_bucket"] = logging_bucket

    @builtins.property
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        result = self._values.get("distribution")
        assert result is not None, "Required property 'distribution' is missing"
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, result)

    @builtins.property
    def cloudfront_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function]:
        result = self._values.get("cloudfront_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function], result)

    @builtins.property
    def logging_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFrontDistributionForApiGatewayResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CloudFrontDistributionForMediaStoreResponse",
    jsii_struct_bases=[],
    name_mapping={
        "distribution": "distribution",
        "request_policy": "requestPolicy",
        "cloudfront_function": "cloudfrontFunction",
        "logging_bucket": "loggingBucket",
    },
)
class CloudFrontDistributionForMediaStoreResponse:
    def __init__(
        self,
        *,
        distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
        request_policy: _aws_cdk_aws_cloudfront_ceddda9d.OriginRequestPolicy,
        cloudfront_function: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function] = None,
        logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    ) -> None:
        '''
        :param distribution: -
        :param request_policy: -
        :param cloudfront_function: -
        :param logging_bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39bce18a31569e2158389732534266e87e792a1af744d954a8b870e46d37ad50)
            check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
            check_type(argname="argument request_policy", value=request_policy, expected_type=type_hints["request_policy"])
            check_type(argname="argument cloudfront_function", value=cloudfront_function, expected_type=type_hints["cloudfront_function"])
            check_type(argname="argument logging_bucket", value=logging_bucket, expected_type=type_hints["logging_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "distribution": distribution,
            "request_policy": request_policy,
        }
        if cloudfront_function is not None:
            self._values["cloudfront_function"] = cloudfront_function
        if logging_bucket is not None:
            self._values["logging_bucket"] = logging_bucket

    @builtins.property
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        result = self._values.get("distribution")
        assert result is not None, "Required property 'distribution' is missing"
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, result)

    @builtins.property
    def request_policy(self) -> _aws_cdk_aws_cloudfront_ceddda9d.OriginRequestPolicy:
        result = self._values.get("request_policy")
        assert result is not None, "Required property 'request_policy' is missing"
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.OriginRequestPolicy, result)

    @builtins.property
    def cloudfront_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function]:
        result = self._values.get("cloudfront_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function], result)

    @builtins.property
    def logging_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFrontDistributionForMediaStoreResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CloudFrontProps",
    jsii_struct_bases=[],
    name_mapping={
        "insert_http_security_headers": "insertHttpSecurityHeaders",
        "response_headers_policy_props": "responseHeadersPolicyProps",
    },
)
class CloudFrontProps:
    def __init__(
        self,
        *,
        insert_http_security_headers: typing.Optional[builtins.bool] = None,
        response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param insert_http_security_headers: -
        :param response_headers_policy_props: -
        '''
        if isinstance(response_headers_policy_props, dict):
            response_headers_policy_props = _aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps(**response_headers_policy_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd3111b21580a09c6860dda1c78369e81b4db80bfcf046e07f6921b72d858ab8)
            check_type(argname="argument insert_http_security_headers", value=insert_http_security_headers, expected_type=type_hints["insert_http_security_headers"])
            check_type(argname="argument response_headers_policy_props", value=response_headers_policy_props, expected_type=type_hints["response_headers_policy_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if insert_http_security_headers is not None:
            self._values["insert_http_security_headers"] = insert_http_security_headers
        if response_headers_policy_props is not None:
            self._values["response_headers_policy_props"] = response_headers_policy_props

    @builtins.property
    def insert_http_security_headers(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("insert_http_security_headers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def response_headers_policy_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps]:
        result = self._values.get("response_headers_policy_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFrontProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CognitoOptions",
    jsii_struct_bases=[],
    name_mapping={
        "identitypool": "identitypool",
        "userpool": "userpool",
        "userpoolclient": "userpoolclient",
    },
)
class CognitoOptions:
    def __init__(
        self,
        *,
        identitypool: _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool,
        userpool: _aws_cdk_aws_cognito_ceddda9d.UserPool,
        userpoolclient: _aws_cdk_aws_cognito_ceddda9d.UserPoolClient,
    ) -> None:
        '''
        :param identitypool: -
        :param userpool: -
        :param userpoolclient: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ab3cd723e5c01a12a9f21b04d8cb1909bd59787d38342b627934c458e0bfeee)
            check_type(argname="argument identitypool", value=identitypool, expected_type=type_hints["identitypool"])
            check_type(argname="argument userpool", value=userpool, expected_type=type_hints["userpool"])
            check_type(argname="argument userpoolclient", value=userpoolclient, expected_type=type_hints["userpoolclient"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identitypool": identitypool,
            "userpool": userpool,
            "userpoolclient": userpoolclient,
        }

    @builtins.property
    def identitypool(self) -> _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool:
        result = self._values.get("identitypool")
        assert result is not None, "Required property 'identitypool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool, result)

    @builtins.property
    def userpool(self) -> _aws_cdk_aws_cognito_ceddda9d.UserPool:
        result = self._values.get("userpool")
        assert result is not None, "Required property 'userpool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.UserPool, result)

    @builtins.property
    def userpoolclient(self) -> _aws_cdk_aws_cognito_ceddda9d.UserPoolClient:
        result = self._values.get("userpoolclient")
        assert result is not None, "Required property 'userpoolclient' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.UserPoolClient, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CreateCloudFrontDistributionForS3Props",
    jsii_struct_bases=[],
    name_mapping={
        "source_bucket": "sourceBucket",
        "cloud_front_distribution_props": "cloudFrontDistributionProps",
        "cloud_front_logging_bucket_props": "cloudFrontLoggingBucketProps",
        "http_security_headers": "httpSecurityHeaders",
        "response_headers_policy_props": "responseHeadersPolicyProps",
    },
)
class CreateCloudFrontDistributionForS3Props:
    def __init__(
        self,
        *,
        source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        cloud_front_distribution_props: typing.Any = None,
        cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        http_security_headers: typing.Optional[builtins.bool] = None,
        response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param source_bucket: -
        :param cloud_front_distribution_props: -
        :param cloud_front_logging_bucket_props: -
        :param http_security_headers: -
        :param response_headers_policy_props: -
        '''
        if isinstance(cloud_front_logging_bucket_props, dict):
            cloud_front_logging_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**cloud_front_logging_bucket_props)
        if isinstance(response_headers_policy_props, dict):
            response_headers_policy_props = _aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps(**response_headers_policy_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90026d4ab83a876c6e64a2dacfaccc19f6269116b2ba36f77701cc6f4ea0fd6f)
            check_type(argname="argument source_bucket", value=source_bucket, expected_type=type_hints["source_bucket"])
            check_type(argname="argument cloud_front_distribution_props", value=cloud_front_distribution_props, expected_type=type_hints["cloud_front_distribution_props"])
            check_type(argname="argument cloud_front_logging_bucket_props", value=cloud_front_logging_bucket_props, expected_type=type_hints["cloud_front_logging_bucket_props"])
            check_type(argname="argument http_security_headers", value=http_security_headers, expected_type=type_hints["http_security_headers"])
            check_type(argname="argument response_headers_policy_props", value=response_headers_policy_props, expected_type=type_hints["response_headers_policy_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_bucket": source_bucket,
        }
        if cloud_front_distribution_props is not None:
            self._values["cloud_front_distribution_props"] = cloud_front_distribution_props
        if cloud_front_logging_bucket_props is not None:
            self._values["cloud_front_logging_bucket_props"] = cloud_front_logging_bucket_props
        if http_security_headers is not None:
            self._values["http_security_headers"] = http_security_headers
        if response_headers_policy_props is not None:
            self._values["response_headers_policy_props"] = response_headers_policy_props

    @builtins.property
    def source_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        result = self._values.get("source_bucket")
        assert result is not None, "Required property 'source_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def cloud_front_distribution_props(self) -> typing.Any:
        result = self._values.get("cloud_front_distribution_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cloud_front_logging_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        result = self._values.get("cloud_front_logging_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def http_security_headers(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("http_security_headers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def response_headers_policy_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps]:
        result = self._values.get("response_headers_policy_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateCloudFrontDistributionForS3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CreateCloudFrontDistributionForS3Response",
    jsii_struct_bases=[],
    name_mapping={
        "distribution": "distribution",
        "cloudfront_function": "cloudfrontFunction",
        "logging_bucket": "loggingBucket",
        "origin_access_control": "originAccessControl",
    },
)
class CreateCloudFrontDistributionForS3Response:
    def __init__(
        self,
        *,
        distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
        cloudfront_function: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function] = None,
        logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        origin_access_control: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl] = None,
    ) -> None:
        '''
        :param distribution: -
        :param cloudfront_function: -
        :param logging_bucket: -
        :param origin_access_control: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0059c54a562cae25a34d2e1d4ea54add942d0efeeab06ea1102d29badea86028)
            check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
            check_type(argname="argument cloudfront_function", value=cloudfront_function, expected_type=type_hints["cloudfront_function"])
            check_type(argname="argument logging_bucket", value=logging_bucket, expected_type=type_hints["logging_bucket"])
            check_type(argname="argument origin_access_control", value=origin_access_control, expected_type=type_hints["origin_access_control"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "distribution": distribution,
        }
        if cloudfront_function is not None:
            self._values["cloudfront_function"] = cloudfront_function
        if logging_bucket is not None:
            self._values["logging_bucket"] = logging_bucket
        if origin_access_control is not None:
            self._values["origin_access_control"] = origin_access_control

    @builtins.property
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        result = self._values.get("distribution")
        assert result is not None, "Required property 'distribution' is missing"
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, result)

    @builtins.property
    def cloudfront_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function]:
        result = self._values.get("cloudfront_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function], result)

    @builtins.property
    def logging_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def origin_access_control(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl]:
        result = self._values.get("origin_access_control")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateCloudFrontDistributionForS3Response(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CreateFargateServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "construct_vpc": "constructVpc",
        "client_cluster_props": "clientClusterProps",
        "client_container_definition_props": "clientContainerDefinitionProps",
        "client_fargate_service_props": "clientFargateServiceProps",
        "client_fargate_task_definition_props": "clientFargateTaskDefinitionProps",
        "ecr_image_version": "ecrImageVersion",
        "ecr_repository_arn": "ecrRepositoryArn",
    },
)
class CreateFargateServiceProps:
    def __init__(
        self,
        *,
        construct_vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        client_cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
        client_container_definition_props: typing.Any = None,
        client_fargate_service_props: typing.Any = None,
        client_fargate_task_definition_props: typing.Any = None,
        ecr_image_version: typing.Optional[builtins.str] = None,
        ecr_repository_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param construct_vpc: -
        :param client_cluster_props: -
        :param client_container_definition_props: -
        :param client_fargate_service_props: -
        :param client_fargate_task_definition_props: -
        :param ecr_image_version: -
        :param ecr_repository_arn: -
        '''
        if isinstance(client_cluster_props, dict):
            client_cluster_props = _aws_cdk_aws_ecs_ceddda9d.ClusterProps(**client_cluster_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c6e4df86cd93502707716761971bda5fd3bb19a72a702c7dfc4fb2c89254b67)
            check_type(argname="argument construct_vpc", value=construct_vpc, expected_type=type_hints["construct_vpc"])
            check_type(argname="argument client_cluster_props", value=client_cluster_props, expected_type=type_hints["client_cluster_props"])
            check_type(argname="argument client_container_definition_props", value=client_container_definition_props, expected_type=type_hints["client_container_definition_props"])
            check_type(argname="argument client_fargate_service_props", value=client_fargate_service_props, expected_type=type_hints["client_fargate_service_props"])
            check_type(argname="argument client_fargate_task_definition_props", value=client_fargate_task_definition_props, expected_type=type_hints["client_fargate_task_definition_props"])
            check_type(argname="argument ecr_image_version", value=ecr_image_version, expected_type=type_hints["ecr_image_version"])
            check_type(argname="argument ecr_repository_arn", value=ecr_repository_arn, expected_type=type_hints["ecr_repository_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "construct_vpc": construct_vpc,
        }
        if client_cluster_props is not None:
            self._values["client_cluster_props"] = client_cluster_props
        if client_container_definition_props is not None:
            self._values["client_container_definition_props"] = client_container_definition_props
        if client_fargate_service_props is not None:
            self._values["client_fargate_service_props"] = client_fargate_service_props
        if client_fargate_task_definition_props is not None:
            self._values["client_fargate_task_definition_props"] = client_fargate_task_definition_props
        if ecr_image_version is not None:
            self._values["ecr_image_version"] = ecr_image_version
        if ecr_repository_arn is not None:
            self._values["ecr_repository_arn"] = ecr_repository_arn

    @builtins.property
    def construct_vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        result = self._values.get("construct_vpc")
        assert result is not None, "Required property 'construct_vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def client_cluster_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ClusterProps]:
        result = self._values.get("client_cluster_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ClusterProps], result)

    @builtins.property
    def client_container_definition_props(self) -> typing.Any:
        result = self._values.get("client_container_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def client_fargate_service_props(self) -> typing.Any:
        result = self._values.get("client_fargate_service_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def client_fargate_task_definition_props(self) -> typing.Any:
        result = self._values.get("client_fargate_task_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def ecr_image_version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ecr_image_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecr_repository_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ecr_repository_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateFargateServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CreateFargateServiceResponse",
    jsii_struct_bases=[],
    name_mapping={"container_definition": "containerDefinition", "service": "service"},
)
class CreateFargateServiceResponse:
    def __init__(
        self,
        *,
        container_definition: _aws_cdk_aws_ecs_ceddda9d.ContainerDefinition,
        service: _aws_cdk_aws_ecs_ceddda9d.FargateService,
    ) -> None:
        '''
        :param container_definition: -
        :param service: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ddf26049ece8a7ca2d07de8a059523b50f38ce266281eb6f6a2c333647bc77a)
            check_type(argname="argument container_definition", value=container_definition, expected_type=type_hints["container_definition"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container_definition": container_definition,
            "service": service,
        }

    @builtins.property
    def container_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.ContainerDefinition:
        result = self._values.get("container_definition")
        assert result is not None, "Required property 'container_definition' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ContainerDefinition, result)

    @builtins.property
    def service(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateService:
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateService, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateFargateServiceResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.CreateSpecRestApiResponse",
    jsii_struct_bases=[],
    name_mapping={"api": "api", "log_group": "logGroup", "role": "role"},
)
class CreateSpecRestApiResponse:
    def __init__(
        self,
        *,
        api: _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi,
        log_group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param api: -
        :param log_group: -
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__958271d7a6ef26178c4bc3d921903ed81f28d55fff334bbdb2f005a34fa081a8)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api": api,
            "log_group": log_group,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.SpecRestApi, result)

    @builtins.property
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        result = self._values.get("log_group")
        assert result is not None, "Required property 'log_group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateSpecRestApiResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.DeployGlueJobResponse",
    jsii_struct_bases=[],
    name_mapping={
        "job": "job",
        "role": "role",
        "bucket": "bucket",
        "logging_bucket": "loggingBucket",
    },
)
class DeployGlueJobResponse:
    def __init__(
        self,
        *,
        job: _aws_cdk_aws_glue_ceddda9d.CfnJob,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    ) -> None:
        '''
        :param job: -
        :param role: -
        :param bucket: -
        :param logging_bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0133b791a4fb505bbd37620b5d8a5e3b8d656dc20e1134a297327ddab20258d3)
            check_type(argname="argument job", value=job, expected_type=type_hints["job"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument logging_bucket", value=logging_bucket, expected_type=type_hints["logging_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "job": job,
            "role": role,
        }
        if bucket is not None:
            self._values["bucket"] = bucket
        if logging_bucket is not None:
            self._values["logging_bucket"] = logging_bucket

    @builtins.property
    def job(self) -> _aws_cdk_aws_glue_ceddda9d.CfnJob:
        result = self._values.get("job")
        assert result is not None, "Required property 'job' is missing"
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnJob, result)

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def logging_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeployGlueJobResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.DeploySagemakerEndpointResponse",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint": "endpoint",
        "endpoint_config": "endpointConfig",
        "model": "model",
    },
)
class DeploySagemakerEndpointResponse:
    def __init__(
        self,
        *,
        endpoint: _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint,
        endpoint_config: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig] = None,
        model: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel] = None,
    ) -> None:
        '''
        :param endpoint: -
        :param endpoint_config: -
        :param model: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cc7c36afe92b0a37e3240ec5f8bd8933971fee5d99cf624253581e0d62fb68f)
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument endpoint_config", value=endpoint_config, expected_type=type_hints["endpoint_config"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "endpoint": endpoint,
        }
        if endpoint_config is not None:
            self._values["endpoint_config"] = endpoint_config
        if model is not None:
            self._values["model"] = model

    @builtins.property
    def endpoint(self) -> _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint:
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint, result)

    @builtins.property
    def endpoint_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig]:
        result = self._values.get("endpoint_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig], result)

    @builtins.property
    def model(self) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel]:
        result = self._values.get("model")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploySagemakerEndpointResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.DynamoDBProps",
    jsii_struct_bases=[],
    name_mapping={
        "dynamo_table_props": "dynamoTableProps",
        "existing_table_interface": "existingTableInterface",
        "existing_table_obj": "existingTableObj",
    },
)
class DynamoDBProps:
    def __init__(
        self,
        *,
        dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_table_interface: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    ) -> None:
        '''
        :param dynamo_table_props: -
        :param existing_table_interface: -
        :param existing_table_obj: -
        '''
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = _aws_cdk_aws_dynamodb_ceddda9d.TableProps(**dynamo_table_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb247f6ada82965a3afeba568ee3ee0a3bacfe3f70c90eb7a7d261e9aba05147)
            check_type(argname="argument dynamo_table_props", value=dynamo_table_props, expected_type=type_hints["dynamo_table_props"])
            check_type(argname="argument existing_table_interface", value=existing_table_interface, expected_type=type_hints["existing_table_interface"])
            check_type(argname="argument existing_table_obj", value=existing_table_obj, expected_type=type_hints["existing_table_obj"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if existing_table_interface is not None:
            self._values["existing_table_interface"] = existing_table_interface
        if existing_table_obj is not None:
            self._values["existing_table_obj"] = existing_table_obj

    @builtins.property
    def dynamo_table_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps]:
        result = self._values.get("dynamo_table_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.TableProps], result)

    @builtins.property
    def existing_table_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        result = self._values.get("existing_table_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], result)

    @builtins.property
    def existing_table_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        result = self._values.get("existing_table_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamoDBProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.EventBridgeProps",
    jsii_struct_bases=[],
    name_mapping={
        "event_bus_props": "eventBusProps",
        "existing_event_bus_interface": "existingEventBusInterface",
    },
)
class EventBridgeProps:
    def __init__(
        self,
        *,
        event_bus_props: typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]],
        existing_event_bus_interface: _aws_cdk_aws_events_ceddda9d.IEventBus,
    ) -> None:
        '''
        :param event_bus_props: -
        :param existing_event_bus_interface: -
        '''
        if isinstance(event_bus_props, dict):
            event_bus_props = _aws_cdk_aws_events_ceddda9d.EventBusProps(**event_bus_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93242b8fe544dd6ab96871ea0286ca1ca0675f344a0e8e2fd2116e52aa4fdabf)
            check_type(argname="argument event_bus_props", value=event_bus_props, expected_type=type_hints["event_bus_props"])
            check_type(argname="argument existing_event_bus_interface", value=existing_event_bus_interface, expected_type=type_hints["existing_event_bus_interface"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "event_bus_props": event_bus_props,
            "existing_event_bus_interface": existing_event_bus_interface,
        }

    @builtins.property
    def event_bus_props(self) -> _aws_cdk_aws_events_ceddda9d.EventBusProps:
        result = self._values.get("event_bus_props")
        assert result is not None, "Required property 'event_bus_props' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.EventBusProps, result)

    @builtins.property
    def existing_event_bus_interface(self) -> _aws_cdk_aws_events_ceddda9d.IEventBus:
        result = self._values.get("existing_event_bus_interface")
        assert result is not None, "Required property 'existing_event_bus_interface' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.IEventBus, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventBridgeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.EventSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_sqs_dlq_queue": "deploySqsDlqQueue",
        "event_source_props": "eventSourceProps",
        "sqs_dlq_queue_props": "sqsDlqQueueProps",
    },
)
class EventSourceProps:
    def __init__(
        self,
        *,
        deploy_sqs_dlq_queue: typing.Optional[builtins.bool] = None,
        event_source_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_event_sources_ceddda9d.StreamEventSourceProps, typing.Dict[builtins.str, typing.Any]]] = None,
        sqs_dlq_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param deploy_sqs_dlq_queue: -
        :param event_source_props: -
        :param sqs_dlq_queue_props: -
        '''
        if isinstance(event_source_props, dict):
            event_source_props = _aws_cdk_aws_lambda_event_sources_ceddda9d.StreamEventSourceProps(**event_source_props)
        if isinstance(sqs_dlq_queue_props, dict):
            sqs_dlq_queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**sqs_dlq_queue_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd9154864f9398b573005d4bb551334a4a15e90d5c251f215681508058cb7106)
            check_type(argname="argument deploy_sqs_dlq_queue", value=deploy_sqs_dlq_queue, expected_type=type_hints["deploy_sqs_dlq_queue"])
            check_type(argname="argument event_source_props", value=event_source_props, expected_type=type_hints["event_source_props"])
            check_type(argname="argument sqs_dlq_queue_props", value=sqs_dlq_queue_props, expected_type=type_hints["sqs_dlq_queue_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deploy_sqs_dlq_queue is not None:
            self._values["deploy_sqs_dlq_queue"] = deploy_sqs_dlq_queue
        if event_source_props is not None:
            self._values["event_source_props"] = event_source_props
        if sqs_dlq_queue_props is not None:
            self._values["sqs_dlq_queue_props"] = sqs_dlq_queue_props

    @builtins.property
    def deploy_sqs_dlq_queue(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("deploy_sqs_dlq_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_source_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_event_sources_ceddda9d.StreamEventSourceProps]:
        result = self._values.get("event_source_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_event_sources_ceddda9d.StreamEventSourceProps], result)

    @builtins.property
    def sqs_dlq_queue_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        result = self._values.get("sqs_dlq_queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.GlobalLambdaRestApiResponse",
    jsii_struct_bases=[],
    name_mapping={"api": "api", "group": "group", "role": "role"},
)
class GlobalLambdaRestApiResponse:
    def __init__(
        self,
        *,
        api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
        group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param api: -
        :param group: -
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a66c905c067e321062fc436583c2316dd1c39ba83fffe345fbb8186a95d3978)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api": api,
            "group": group,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, result)

    @builtins.property
    def group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlobalLambdaRestApiResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.GlobalRestApiResponse",
    jsii_struct_bases=[],
    name_mapping={"api": "api", "log_group": "logGroup", "role": "role"},
)
class GlobalRestApiResponse:
    def __init__(
        self,
        *,
        api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
        log_group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param api: -
        :param log_group: -
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb6d18a6974ba49897c4231d68397e8ad9509c9459c38c09cb51016796a0d455)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api": api,
            "log_group": log_group,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, result)

    @builtins.property
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        result = self._values.get("log_group")
        assert result is not None, "Required property 'log_group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlobalRestApiResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.GlueProps",
    jsii_struct_bases=[],
    name_mapping={
        "etl_code_asset": "etlCodeAsset",
        "existing_glue_job": "existingGlueJob",
        "existing_table": "existingTable",
        "field_schema": "fieldSchema",
        "glue_job_props": "glueJobProps",
        "table_propss": "tablePropss",
    },
)
class GlueProps:
    def __init__(
        self,
        *,
        etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        existing_glue_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
        existing_table: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable] = None,
        field_schema: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        glue_job_props: typing.Any = None,
        table_propss: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param etl_code_asset: -
        :param existing_glue_job: -
        :param existing_table: -
        :param field_schema: -
        :param glue_job_props: -
        :param table_propss: -
        '''
        if isinstance(table_propss, dict):
            table_propss = _aws_cdk_aws_glue_ceddda9d.CfnTableProps(**table_propss)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0512c4e0b6637c93558f3e29adea206d1e83e571d9700ae1ad6925b8f0ce5b98)
            check_type(argname="argument etl_code_asset", value=etl_code_asset, expected_type=type_hints["etl_code_asset"])
            check_type(argname="argument existing_glue_job", value=existing_glue_job, expected_type=type_hints["existing_glue_job"])
            check_type(argname="argument existing_table", value=existing_table, expected_type=type_hints["existing_table"])
            check_type(argname="argument field_schema", value=field_schema, expected_type=type_hints["field_schema"])
            check_type(argname="argument glue_job_props", value=glue_job_props, expected_type=type_hints["glue_job_props"])
            check_type(argname="argument table_propss", value=table_propss, expected_type=type_hints["table_propss"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if etl_code_asset is not None:
            self._values["etl_code_asset"] = etl_code_asset
        if existing_glue_job is not None:
            self._values["existing_glue_job"] = existing_glue_job
        if existing_table is not None:
            self._values["existing_table"] = existing_table
        if field_schema is not None:
            self._values["field_schema"] = field_schema
        if glue_job_props is not None:
            self._values["glue_job_props"] = glue_job_props
        if table_propss is not None:
            self._values["table_propss"] = table_propss

    @builtins.property
    def etl_code_asset(self) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        result = self._values.get("etl_code_asset")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], result)

    @builtins.property
    def existing_glue_job(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob]:
        result = self._values.get("existing_glue_job")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob], result)

    @builtins.property
    def existing_table(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable]:
        result = self._values.get("existing_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable], result)

    @builtins.property
    def field_schema(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty]]:
        result = self._values.get("field_schema")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty]], result)

    @builtins.property
    def glue_job_props(self) -> typing.Any:
        result = self._values.get("glue_job_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def table_propss(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTableProps]:
        result = self._values.get("table_propss")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTableProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.KinesisStreamProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_stream_obj": "existingStreamObj",
        "kinesis_stream_props": "kinesisStreamProps",
    },
)
class KinesisStreamProps:
    def __init__(
        self,
        *,
        existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
        kinesis_stream_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesis_ceddda9d.StreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param existing_stream_obj: -
        :param kinesis_stream_props: -
        '''
        if isinstance(kinesis_stream_props, dict):
            kinesis_stream_props = _aws_cdk_aws_kinesis_ceddda9d.StreamProps(**kinesis_stream_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db3d777f3fce2080f6b27b83b17d7be6eb873a69ffa58b131dc28af4c0a6d232)
            check_type(argname="argument existing_stream_obj", value=existing_stream_obj, expected_type=type_hints["existing_stream_obj"])
            check_type(argname="argument kinesis_stream_props", value=kinesis_stream_props, expected_type=type_hints["kinesis_stream_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_stream_obj is not None:
            self._values["existing_stream_obj"] = existing_stream_obj
        if kinesis_stream_props is not None:
            self._values["kinesis_stream_props"] = kinesis_stream_props

    @builtins.property
    def existing_stream_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream]:
        result = self._values.get("existing_stream_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream], result)

    @builtins.property
    def kinesis_stream_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.StreamProps]:
        result = self._values.get("kinesis_stream_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.StreamProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KinesisStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.LambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_lambda_obj": "existingLambdaObj",
        "lambda_function_props": "lambdaFunctionProps",
    },
)
class LambdaProps:
    def __init__(
        self,
        *,
        existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param existing_lambda_obj: -
        :param lambda_function_props: -
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = _aws_cdk_aws_lambda_ceddda9d.FunctionProps(**lambda_function_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d42be92054867170509a996825e08a868a93f029408e224c3d4c5f0a772762ec)
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props

    @builtins.property
    def existing_lambda_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps]:
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.FunctionProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.MediaStoreProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_media_store_container_obj": "existingMediaStoreContainerObj",
        "media_store_container_props": "mediaStoreContainerProps",
    },
)
class MediaStoreProps:
    def __init__(
        self,
        *,
        existing_media_store_container_obj: typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer] = None,
        media_store_container_props: typing.Optional[typing.Union[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param existing_media_store_container_obj: -
        :param media_store_container_props: -
        '''
        if isinstance(media_store_container_props, dict):
            media_store_container_props = _aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps(**media_store_container_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2aa532ddbd324fb791db84dcad85f906a5b71e1140b139d99d630f5200479af)
            check_type(argname="argument existing_media_store_container_obj", value=existing_media_store_container_obj, expected_type=type_hints["existing_media_store_container_obj"])
            check_type(argname="argument media_store_container_props", value=media_store_container_props, expected_type=type_hints["media_store_container_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_media_store_container_obj is not None:
            self._values["existing_media_store_container_obj"] = existing_media_store_container_obj
        if media_store_container_props is not None:
            self._values["media_store_container_props"] = media_store_container_props

    @builtins.property
    def existing_media_store_container_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer]:
        result = self._values.get("existing_media_store_container_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer], result)

    @builtins.property
    def media_store_container_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps]:
        result = self._values.get("media_store_container_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.ObtainAlbProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_api": "publicApi",
        "vpc": "vpc",
        "existing_load_balancer_obj": "existingLoadBalancerObj",
        "load_balancer_props": "loadBalancerProps",
        "log_access_logs": "logAccessLogs",
        "logging_bucket_props": "loggingBucketProps",
    },
)
class ObtainAlbProps:
    def __init__(
        self,
        *,
        public_api: builtins.bool,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        existing_load_balancer_obj: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer] = None,
        load_balancer_props: typing.Any = None,
        log_access_logs: typing.Optional[builtins.bool] = None,
        logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param public_api: -
        :param vpc: -
        :param existing_load_balancer_obj: -
        :param load_balancer_props: -
        :param log_access_logs: -
        :param logging_bucket_props: -
        '''
        if isinstance(logging_bucket_props, dict):
            logging_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**logging_bucket_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12b14feea16b19036cf050ea8dd837f794807f0bf081e9b64939210089265868)
            check_type(argname="argument public_api", value=public_api, expected_type=type_hints["public_api"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument existing_load_balancer_obj", value=existing_load_balancer_obj, expected_type=type_hints["existing_load_balancer_obj"])
            check_type(argname="argument load_balancer_props", value=load_balancer_props, expected_type=type_hints["load_balancer_props"])
            check_type(argname="argument log_access_logs", value=log_access_logs, expected_type=type_hints["log_access_logs"])
            check_type(argname="argument logging_bucket_props", value=logging_bucket_props, expected_type=type_hints["logging_bucket_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "public_api": public_api,
            "vpc": vpc,
        }
        if existing_load_balancer_obj is not None:
            self._values["existing_load_balancer_obj"] = existing_load_balancer_obj
        if load_balancer_props is not None:
            self._values["load_balancer_props"] = load_balancer_props
        if log_access_logs is not None:
            self._values["log_access_logs"] = log_access_logs
        if logging_bucket_props is not None:
            self._values["logging_bucket_props"] = logging_bucket_props

    @builtins.property
    def public_api(self) -> builtins.bool:
        result = self._values.get("public_api")
        assert result is not None, "Required property 'public_api' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def existing_load_balancer_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer]:
        result = self._values.get("existing_load_balancer_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer], result)

    @builtins.property
    def load_balancer_props(self) -> typing.Any:
        result = self._values.get("load_balancer_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def log_access_logs(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("log_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        result = self._values.get("logging_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObtainAlbProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.ObtainMemcachedClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "cache_security_group_id": "cacheSecurityGroupId",
        "cache_port": "cachePort",
        "cache_props": "cacheProps",
        "existing_cache": "existingCache",
        "vpc": "vpc",
    },
)
class ObtainMemcachedClusterProps:
    def __init__(
        self,
        *,
        cache_security_group_id: builtins.str,
        cache_port: typing.Any = None,
        cache_props: typing.Any = None,
        existing_cache: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param cache_security_group_id: -
        :param cache_port: -
        :param cache_props: -
        :param existing_cache: -
        :param vpc: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6259aab05fc4d80010f467a98da23803b608c0fb9c2637f8dc91b1be476b5e50)
            check_type(argname="argument cache_security_group_id", value=cache_security_group_id, expected_type=type_hints["cache_security_group_id"])
            check_type(argname="argument cache_port", value=cache_port, expected_type=type_hints["cache_port"])
            check_type(argname="argument cache_props", value=cache_props, expected_type=type_hints["cache_props"])
            check_type(argname="argument existing_cache", value=existing_cache, expected_type=type_hints["existing_cache"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cache_security_group_id": cache_security_group_id,
        }
        if cache_port is not None:
            self._values["cache_port"] = cache_port
        if cache_props is not None:
            self._values["cache_props"] = cache_props
        if existing_cache is not None:
            self._values["existing_cache"] = existing_cache
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cache_security_group_id(self) -> builtins.str:
        result = self._values.get("cache_security_group_id")
        assert result is not None, "Required property 'cache_security_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cache_port(self) -> typing.Any:
        result = self._values.get("cache_port")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cache_props(self) -> typing.Any:
        result = self._values.get("cache_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def existing_cache(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster]:
        result = self._values.get("existing_cache")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObtainMemcachedClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.OpenSearchProps",
    jsii_struct_bases=[],
    name_mapping={"open_search_domain_props": "openSearchDomainProps"},
)
class OpenSearchProps:
    def __init__(
        self,
        *,
        open_search_domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param open_search_domain_props: -
        '''
        if isinstance(open_search_domain_props, dict):
            open_search_domain_props = _aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps(**open_search_domain_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87594edd93213c38ce202aa16be748b2b19d103564cbf8a1b355560207fbecc6)
            check_type(argname="argument open_search_domain_props", value=open_search_domain_props, expected_type=type_hints["open_search_domain_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if open_search_domain_props is not None:
            self._values["open_search_domain_props"] = open_search_domain_props

    @builtins.property
    def open_search_domain_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps]:
        result = self._values.get("open_search_domain_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.RegionalLambdaRestApiResponse",
    jsii_struct_bases=[],
    name_mapping={"api": "api", "group": "group", "role": "role"},
)
class RegionalLambdaRestApiResponse:
    def __init__(
        self,
        *,
        api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
        group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param api: -
        :param group: -
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8de3143e71bde6dafd77c44cdaf6b172642b82573eeb0c78376630da9ff0f010)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api": api,
            "group": group,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, result)

    @builtins.property
    def group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegionalLambdaRestApiResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.RegionalRestApiResponse",
    jsii_struct_bases=[],
    name_mapping={"api": "api", "log_group": "logGroup", "role": "role"},
)
class RegionalRestApiResponse:
    def __init__(
        self,
        *,
        api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
        log_group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param api: -
        :param log_group: -
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69f9376c99111a4c77b49a86b91b6288516d5aafef42d7596270d8e3dab8a452)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api": api,
            "log_group": log_group,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, result)

    @builtins.property
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        result = self._values.get("log_group")
        assert result is not None, "Required property 'log_group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegionalRestApiResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_cloudfront_ceddda9d.IOrigin)
class S3OacOrigin(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/core.S3OacOrigin",
):
    '''A custom implementation of S3Origin that allows an origin access control (OAC) to be used instead of an origin access identity (OAI), which is currently the only option supported by default CDK.'''

    def __init__(
        self,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        *,
        origin_access_control: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl] = None,
        origin_path: typing.Optional[builtins.str] = None,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_id: typing.Optional[builtins.str] = None,
        origin_shield_enabled: typing.Optional[builtins.bool] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: -
        :param origin_access_control: The origin access control that will be used when calling your S3 bucket.
        :param origin_path: An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param connection_attempts: The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_id: A unique identifier for the origin. This value must be unique within the distribution. Default: - an originid will be generated for you
        :param origin_shield_enabled: Origin Shield is enabled by setting originShieldRegion to a valid region, after this to disable Origin Shield again you must set this flag to false. Default: - true
        :param origin_shield_region: When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44846869b9ecaeab140b843e216e72ede263e14e7846fdeed302ad40eedcc020)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        props = S3OacOriginProps(
            origin_access_control=origin_access_control,
            origin_path=origin_path,
            connection_attempts=connection_attempts,
            connection_timeout=connection_timeout,
            custom_headers=custom_headers,
            origin_id=origin_id,
            origin_shield_enabled=origin_shield_enabled,
            origin_shield_region=origin_shield_region,
        )

        jsii.create(self.__class__, self, [bucket, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        *,
        origin_id: builtins.str,
    ) -> _aws_cdk_aws_cloudfront_ceddda9d.OriginBindConfig:
        '''The method called when a given Origin is added (for the first time) to a Distribution.

        :param scope: -
        :param origin_id: The identifier of this Origin, as assigned by the Distribution this Origin has been used added to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62b0973bdb62c2264b514644e251318ac9dcde1b359c646d66b5a8a10db79f8b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        options = _aws_cdk_aws_cloudfront_ceddda9d.OriginBindOptions(
            origin_id=origin_id
        )

        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.OriginBindConfig, jsii.invoke(self, "bind", [scope, options]))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.S3OacOriginProps",
    jsii_struct_bases=[_aws_cdk_aws_cloudfront_ceddda9d.OriginProps],
    name_mapping={
        "connection_attempts": "connectionAttempts",
        "connection_timeout": "connectionTimeout",
        "custom_headers": "customHeaders",
        "origin_id": "originId",
        "origin_shield_enabled": "originShieldEnabled",
        "origin_shield_region": "originShieldRegion",
        "origin_path": "originPath",
        "origin_access_control": "originAccessControl",
    },
)
class S3OacOriginProps(_aws_cdk_aws_cloudfront_ceddda9d.OriginProps):
    def __init__(
        self,
        *,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_id: typing.Optional[builtins.str] = None,
        origin_shield_enabled: typing.Optional[builtins.bool] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_access_control: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl] = None,
    ) -> None:
        '''Properties to use to customize an S3 Origin.

        :param connection_attempts: The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_id: A unique identifier for the origin. This value must be unique within the distribution. Default: - an originid will be generated for you
        :param origin_shield_enabled: Origin Shield is enabled by setting originShieldRegion to a valid region, after this to disable Origin Shield again you must set this flag to false. Default: - true
        :param origin_shield_region: When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled
        :param origin_path: An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param origin_access_control: The origin access control that will be used when calling your S3 bucket.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4727907366b00308bea7c2d08561f315c9f243b37d0b3a99db676ce6963cb09)
            check_type(argname="argument connection_attempts", value=connection_attempts, expected_type=type_hints["connection_attempts"])
            check_type(argname="argument connection_timeout", value=connection_timeout, expected_type=type_hints["connection_timeout"])
            check_type(argname="argument custom_headers", value=custom_headers, expected_type=type_hints["custom_headers"])
            check_type(argname="argument origin_id", value=origin_id, expected_type=type_hints["origin_id"])
            check_type(argname="argument origin_shield_enabled", value=origin_shield_enabled, expected_type=type_hints["origin_shield_enabled"])
            check_type(argname="argument origin_shield_region", value=origin_shield_region, expected_type=type_hints["origin_shield_region"])
            check_type(argname="argument origin_path", value=origin_path, expected_type=type_hints["origin_path"])
            check_type(argname="argument origin_access_control", value=origin_access_control, expected_type=type_hints["origin_access_control"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_attempts is not None:
            self._values["connection_attempts"] = connection_attempts
        if connection_timeout is not None:
            self._values["connection_timeout"] = connection_timeout
        if custom_headers is not None:
            self._values["custom_headers"] = custom_headers
        if origin_id is not None:
            self._values["origin_id"] = origin_id
        if origin_shield_enabled is not None:
            self._values["origin_shield_enabled"] = origin_shield_enabled
        if origin_shield_region is not None:
            self._values["origin_shield_region"] = origin_shield_region
        if origin_path is not None:
            self._values["origin_path"] = origin_path
        if origin_access_control is not None:
            self._values["origin_access_control"] = origin_access_control

    @builtins.property
    def connection_attempts(self) -> typing.Optional[jsii.Number]:
        '''The number of times that CloudFront attempts to connect to the origin;

        valid values are 1, 2, or 3 attempts.

        :default: 3
        '''
        result = self._values.get("connection_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connection_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The number of seconds that CloudFront waits when trying to establish a connection to the origin.

        Valid values are 1-10 seconds, inclusive.

        :default: Duration.seconds(10)
        '''
        result = self._values.get("connection_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def custom_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of HTTP header names and values that CloudFront adds to requests it sends to the origin.

        :default: {}
        '''
        result = self._values.get("custom_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def origin_id(self) -> typing.Optional[builtins.str]:
        '''A unique identifier for the origin.

        This value must be unique within the distribution.

        :default: - an originid will be generated for you
        '''
        result = self._values.get("origin_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_shield_enabled(self) -> typing.Optional[builtins.bool]:
        '''Origin Shield is enabled by setting originShieldRegion to a valid region, after this to disable Origin Shield again you must set this flag to false.

        :default: - true
        '''
        result = self._values.get("origin_shield_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def origin_shield_region(self) -> typing.Optional[builtins.str]:
        '''When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance.

        :default: - origin shield not enabled

        :see: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html
        '''
        result = self._values.get("origin_shield_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_path(self) -> typing.Optional[builtins.str]:
        '''An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin.

        Must begin, but not end, with '/' (e.g., '/production/images').

        :default: '/'
        '''
        result = self._values.get("origin_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_access_control(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl]:
        '''The origin access control that will be used when calling your S3 bucket.'''
        result = self._values.get("origin_access_control")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3OacOriginProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.S3Props",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_props": "bucketProps",
        "existing_bucket_interface": "existingBucketInterface",
        "existing_bucket_obj": "existingBucketObj",
        "existing_logging_bucket_obj": "existingLoggingBucketObj",
        "logging_bucket_props": "loggingBucketProps",
        "log_s3_access_logs": "logS3AccessLogs",
    },
)
class S3Props:
    def __init__(
        self,
        *,
        bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_bucket_interface: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        existing_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        existing_logging_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param bucket_props: -
        :param existing_bucket_interface: -
        :param existing_bucket_obj: -
        :param existing_logging_bucket_obj: -
        :param logging_bucket_props: -
        :param log_s3_access_logs: -
        '''
        if isinstance(bucket_props, dict):
            bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**bucket_props)
        if isinstance(logging_bucket_props, dict):
            logging_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**logging_bucket_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88e247efc77c0ef836bf304cd9929e60e1bd45ac671a55344bb1cb842fc5d67f)
            check_type(argname="argument bucket_props", value=bucket_props, expected_type=type_hints["bucket_props"])
            check_type(argname="argument existing_bucket_interface", value=existing_bucket_interface, expected_type=type_hints["existing_bucket_interface"])
            check_type(argname="argument existing_bucket_obj", value=existing_bucket_obj, expected_type=type_hints["existing_bucket_obj"])
            check_type(argname="argument existing_logging_bucket_obj", value=existing_logging_bucket_obj, expected_type=type_hints["existing_logging_bucket_obj"])
            check_type(argname="argument logging_bucket_props", value=logging_bucket_props, expected_type=type_hints["logging_bucket_props"])
            check_type(argname="argument log_s3_access_logs", value=log_s3_access_logs, expected_type=type_hints["log_s3_access_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_props is not None:
            self._values["bucket_props"] = bucket_props
        if existing_bucket_interface is not None:
            self._values["existing_bucket_interface"] = existing_bucket_interface
        if existing_bucket_obj is not None:
            self._values["existing_bucket_obj"] = existing_bucket_obj
        if existing_logging_bucket_obj is not None:
            self._values["existing_logging_bucket_obj"] = existing_logging_bucket_obj
        if logging_bucket_props is not None:
            self._values["logging_bucket_props"] = logging_bucket_props
        if log_s3_access_logs is not None:
            self._values["log_s3_access_logs"] = log_s3_access_logs

    @builtins.property
    def bucket_props(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        result = self._values.get("bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def existing_bucket_interface(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        result = self._values.get("existing_bucket_interface")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def existing_bucket_obj(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        result = self._values.get("existing_bucket_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def existing_logging_bucket_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        result = self._values.get("existing_logging_bucket_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def logging_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        result = self._values.get("logging_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def log_s3_access_logs(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("log_s3_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.SagemakerProps",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_props": "endpointProps",
        "existing_sagemaker_endpoint_obj": "existingSagemakerEndpointObj",
    },
)
class SagemakerProps:
    def __init__(
        self,
        *,
        endpoint_props: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_sagemaker_endpoint_obj: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint] = None,
    ) -> None:
        '''
        :param endpoint_props: -
        :param existing_sagemaker_endpoint_obj: -
        '''
        if isinstance(endpoint_props, dict):
            endpoint_props = _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps(**endpoint_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__283c859cb26d60c5956aa575637cb020b0fca8aae26fb332e5cf234df91b38c2)
            check_type(argname="argument endpoint_props", value=endpoint_props, expected_type=type_hints["endpoint_props"])
            check_type(argname="argument existing_sagemaker_endpoint_obj", value=existing_sagemaker_endpoint_obj, expected_type=type_hints["existing_sagemaker_endpoint_obj"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if endpoint_props is not None:
            self._values["endpoint_props"] = endpoint_props
        if existing_sagemaker_endpoint_obj is not None:
            self._values["existing_sagemaker_endpoint_obj"] = existing_sagemaker_endpoint_obj

    @builtins.property
    def endpoint_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps]:
        result = self._values.get("endpoint_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps], result)

    @builtins.property
    def existing_sagemaker_endpoint_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint]:
        result = self._values.get("existing_sagemaker_endpoint_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SagemakerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.SecretsManagerProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_secret_obj": "existingSecretObj",
        "secret_props": "secretProps",
    },
)
class SecretsManagerProps:
    def __init__(
        self,
        *,
        existing_secret_obj: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
        secret_props: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param existing_secret_obj: -
        :param secret_props: -
        '''
        if isinstance(secret_props, dict):
            secret_props = _aws_cdk_aws_secretsmanager_ceddda9d.SecretProps(**secret_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6354a4887fd34fa60206fc7671e58c335a07947a56bf229c7f1ef1c1a7ea6775)
            check_type(argname="argument existing_secret_obj", value=existing_secret_obj, expected_type=type_hints["existing_secret_obj"])
            check_type(argname="argument secret_props", value=secret_props, expected_type=type_hints["secret_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if existing_secret_obj is not None:
            self._values["existing_secret_obj"] = existing_secret_obj
        if secret_props is not None:
            self._values["secret_props"] = secret_props

    @builtins.property
    def existing_secret_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret]:
        result = self._values.get("existing_secret_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret], result)

    @builtins.property
    def secret_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps]:
        result = self._values.get("secret_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretsManagerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.SecurityGroupRuleDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "connection": "connection",
        "peer": "peer",
        "description": "description",
        "remote_rule": "remoteRule",
    },
)
class SecurityGroupRuleDefinition:
    def __init__(
        self,
        *,
        connection: _aws_cdk_aws_ec2_ceddda9d.Port,
        peer: _aws_cdk_aws_ec2_ceddda9d.IPeer,
        description: typing.Optional[builtins.str] = None,
        remote_rule: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param connection: -
        :param peer: -
        :param description: -
        :param remote_rule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1b63a5b21e67fc626e311bcd9d47fed6238a24e4dfab400e1c7d46f35e380aa)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument remote_rule", value=remote_rule, expected_type=type_hints["remote_rule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection": connection,
            "peer": peer,
        }
        if description is not None:
            self._values["description"] = description
        if remote_rule is not None:
            self._values["remote_rule"] = remote_rule

    @builtins.property
    def connection(self) -> _aws_cdk_aws_ec2_ceddda9d.Port:
        result = self._values.get("connection")
        assert result is not None, "Required property 'connection' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Port, result)

    @builtins.property
    def peer(self) -> _aws_cdk_aws_ec2_ceddda9d.IPeer:
        result = self._values.get("peer")
        assert result is not None, "Required property 'peer' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IPeer, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_rule(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("remote_rule")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityGroupRuleDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-solutions-constructs/core.ServiceEndpointTypes")
class ServiceEndpointTypes(enum.Enum):
    DYNAMODB = "DYNAMODB"
    SNS = "SNS"
    SQS = "SQS"
    S3 = "S3"
    STEP_FUNCTIONS = "STEP_FUNCTIONS"
    SAGEMAKER_RUNTIME = "SAGEMAKER_RUNTIME"
    SECRETS_MANAGER = "SECRETS_MANAGER"
    SSM = "SSM"
    ECR_API = "ECR_API"
    ECR_DKR = "ECR_DKR"
    EVENTS = "EVENTS"
    KINESIS_FIREHOSE = "KINESIS_FIREHOSE"
    KINESIS_STREAMS = "KINESIS_STREAMS"
    KENDRA = "KENDRA"


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.SinkDataStoreProps",
    jsii_struct_bases=[],
    name_mapping={
        "datastore_type": "datastoreType",
        "existing_s3_output_bucket": "existingS3OutputBucket",
        "output_bucket_props": "outputBucketProps",
    },
)
class SinkDataStoreProps:
    def __init__(
        self,
        *,
        datastore_type: "SinkStoreType",
        existing_s3_output_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        output_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Interface to define potential outputs to allow the construct define additional output destinations for ETL transformation.

        :param datastore_type: Sink data store type.
        :param existing_s3_output_bucket: The output S3 location where the data should be written. The provided S3 bucket will be used to pass the output location to the etl script as an argument to the AWS Glue job. If no location is provided, it will check if @outputBucketProps are provided. If not it will create a new bucket if the @datastoreType is S3. The argument key is ``output_path``. The value of the argument can be retrieve in the python script as follows: getResolvedOptions(sys.argv, ["JOB_NAME", "output_path", ]) output_path = args["output_path"]
        :param output_bucket_props: If @existingS3OutputBUcket is provided, this parameter is ignored. If this parameter is not provided, the construct will create a new bucket if the @datastoreType is S3.
        '''
        if isinstance(output_bucket_props, dict):
            output_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**output_bucket_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cb5014b4d7319f98a3e761f0cdfddf1180509c575fcd7d2d58ae702d7f8493c)
            check_type(argname="argument datastore_type", value=datastore_type, expected_type=type_hints["datastore_type"])
            check_type(argname="argument existing_s3_output_bucket", value=existing_s3_output_bucket, expected_type=type_hints["existing_s3_output_bucket"])
            check_type(argname="argument output_bucket_props", value=output_bucket_props, expected_type=type_hints["output_bucket_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datastore_type": datastore_type,
        }
        if existing_s3_output_bucket is not None:
            self._values["existing_s3_output_bucket"] = existing_s3_output_bucket
        if output_bucket_props is not None:
            self._values["output_bucket_props"] = output_bucket_props

    @builtins.property
    def datastore_type(self) -> "SinkStoreType":
        '''Sink data store type.'''
        result = self._values.get("datastore_type")
        assert result is not None, "Required property 'datastore_type' is missing"
        return typing.cast("SinkStoreType", result)

    @builtins.property
    def existing_s3_output_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''The output S3 location where the data should be written.

        The provided S3 bucket will be used to pass
        the output location to the etl script as an argument to the AWS Glue job.

        If no location is provided, it will check if @outputBucketProps are provided. If not it will create a new
        bucket if the @datastoreType is S3.

        The argument key is ``output_path``. The value of the argument can be retrieve in the python script
        as follows:
        getResolvedOptions(sys.argv, ["JOB_NAME", "output_path",  ])
        output_path = args["output_path"]
        '''
        result = self._values.get("existing_s3_output_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def output_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''If @existingS3OutputBUcket is provided, this parameter is ignored.

        If this parameter is not provided,
        the construct will create a new bucket if the @datastoreType is S3.
        '''
        result = self._values.get("output_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SinkDataStoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-solutions-constructs/core.SinkStoreType")
class SinkStoreType(enum.Enum):
    '''Enumeration of data store types that could include S3, DynamoDB, DocumentDB, RDS or Redshift.

    Current
    construct implementation only supports S3, but potential to add other output types in the future
    '''

    S3 = "S3"


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.SnsProps",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_key": "encryptionKey",
        "encryption_key_props": "encryptionKeyProps",
        "existing_topic_obj": "existingTopicObj",
        "existing_topic_object": "existingTopicObject",
        "topic_props": "topicProps",
    },
)
class SnsProps:
    def __init__(
        self,
        *,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        existing_topic_object: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
        topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param encryption_key: -
        :param encryption_key_props: -
        :param existing_topic_obj: -
        :param existing_topic_object: -
        :param topic_props: -
        '''
        if isinstance(encryption_key_props, dict):
            encryption_key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**encryption_key_props)
        if isinstance(topic_props, dict):
            topic_props = _aws_cdk_aws_sns_ceddda9d.TopicProps(**topic_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bca360d8cee23ba56d2f45f6f01d513bcce80deec27a4677ff3e775452f6238)
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument encryption_key_props", value=encryption_key_props, expected_type=type_hints["encryption_key_props"])
            check_type(argname="argument existing_topic_obj", value=existing_topic_obj, expected_type=type_hints["existing_topic_obj"])
            check_type(argname="argument existing_topic_object", value=existing_topic_object, expected_type=type_hints["existing_topic_object"])
            check_type(argname="argument topic_props", value=topic_props, expected_type=type_hints["topic_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_key_props is not None:
            self._values["encryption_key_props"] = encryption_key_props
        if existing_topic_obj is not None:
            self._values["existing_topic_obj"] = existing_topic_obj
        if existing_topic_object is not None:
            self._values["existing_topic_object"] = existing_topic_object
        if topic_props is not None:
            self._values["topic_props"] = topic_props

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def encryption_key_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        result = self._values.get("encryption_key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def existing_topic_obj(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic]:
        result = self._values.get("existing_topic_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic], result)

    @builtins.property
    def existing_topic_object(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic]:
        result = self._values.get("existing_topic_object")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic], result)

    @builtins.property
    def topic_props(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps]:
        result = self._values.get("topic_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.TopicProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.SqsProps",
    jsii_struct_bases=[],
    name_mapping={
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "encryption_key": "encryptionKey",
        "encryption_key_props": "encryptionKeyProps",
        "existing_queue_obj": "existingQueueObj",
        "queue_props": "queueProps",
    },
)
class SqsProps:
    def __init__(
        self,
        *,
        dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dead_letter_queue_props: -
        :param deploy_dead_letter_queue: -
        :param encryption_key: -
        :param encryption_key_props: -
        :param existing_queue_obj: -
        :param queue_props: -
        '''
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**dead_letter_queue_props)
        if isinstance(encryption_key_props, dict):
            encryption_key_props = _aws_cdk_aws_kms_ceddda9d.KeyProps(**encryption_key_props)
        if isinstance(queue_props, dict):
            queue_props = _aws_cdk_aws_sqs_ceddda9d.QueueProps(**queue_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3536696b3fd1fdb7ce43c98c85cb8881b09b6c0b3f129c94eba97862116dbaaa)
            check_type(argname="argument dead_letter_queue_props", value=dead_letter_queue_props, expected_type=type_hints["dead_letter_queue_props"])
            check_type(argname="argument deploy_dead_letter_queue", value=deploy_dead_letter_queue, expected_type=type_hints["deploy_dead_letter_queue"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument encryption_key_props", value=encryption_key_props, expected_type=type_hints["encryption_key_props"])
            check_type(argname="argument existing_queue_obj", value=existing_queue_obj, expected_type=type_hints["existing_queue_obj"])
            check_type(argname="argument queue_props", value=queue_props, expected_type=type_hints["queue_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_key_props is not None:
            self._values["encryption_key_props"] = encryption_key_props
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if queue_props is not None:
            self._values["queue_props"] = queue_props

    @builtins.property
    def dead_letter_queue_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def encryption_key_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps]:
        result = self._values.get("encryption_key_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.KeyProps], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps]:
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.QueueProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.VpcPropsSet",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_vpc": "deployVpc",
        "existing_vpc": "existingVpc",
        "vpc_props": "vpcProps",
    },
)
class VpcPropsSet:
    def __init__(
        self,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param deploy_vpc: -
        :param existing_vpc: -
        :param vpc_props: -
        '''
        if isinstance(vpc_props, dict):
            vpc_props = _aws_cdk_aws_ec2_ceddda9d.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e2cfb976c78d7138f30cbe00e80016d7751fe28f01cfc46671c7ac62704821)
            check_type(argname="argument deploy_vpc", value=deploy_vpc, expected_type=type_hints["deploy_vpc"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def deploy_vpc(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("deploy_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps]:
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcPropsSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/core.WafWebAclProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_webacl_obj": "existingWebaclObj",
        "webacl_props": "webaclProps",
    },
)
class WafWebAclProps:
    def __init__(
        self,
        *,
        existing_webacl_obj: _aws_cdk_aws_wafv2_ceddda9d.CfnWebACL,
        webacl_props: typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACLProps, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param existing_webacl_obj: -
        :param webacl_props: -
        '''
        if isinstance(webacl_props, dict):
            webacl_props = _aws_cdk_aws_wafv2_ceddda9d.CfnWebACLProps(**webacl_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f99175f2cfd825669300bdabff3e768dcf3371a1530a916000af2c30f820110)
            check_type(argname="argument existing_webacl_obj", value=existing_webacl_obj, expected_type=type_hints["existing_webacl_obj"])
            check_type(argname="argument webacl_props", value=webacl_props, expected_type=type_hints["webacl_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "existing_webacl_obj": existing_webacl_obj,
            "webacl_props": webacl_props,
        }

    @builtins.property
    def existing_webacl_obj(self) -> _aws_cdk_aws_wafv2_ceddda9d.CfnWebACL:
        result = self._values.get("existing_webacl_obj")
        assert result is not None, "Required property 'existing_webacl_obj' is missing"
        return typing.cast(_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL, result)

    @builtins.property
    def webacl_props(self) -> _aws_cdk_aws_wafv2_ceddda9d.CfnWebACLProps:
        result = self._values.get("webacl_props")
        assert result is not None, "Required property 'webacl_props' is missing"
        return typing.cast(_aws_cdk_aws_wafv2_ceddda9d.CfnWebACLProps, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WafWebAclProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AddProxyMethodToApiResourceInputParams",
    "BuildDeadLetterQueueProps",
    "BuildDynamoDBTableProps",
    "BuildDynamoDBTableResponse",
    "BuildDynamoDBTableWithStreamProps",
    "BuildDynamoDBTableWithStreamResponse",
    "BuildElasticSearchProps",
    "BuildElasticSearchResponse",
    "BuildEventBusProps",
    "BuildGlueJobProps",
    "BuildGlueJobResponse",
    "BuildKendraIndexProps",
    "BuildKinesisAnalyticsAppProps",
    "BuildKinesisStreamProps",
    "BuildLambdaFunctionProps",
    "BuildOpenSearchProps",
    "BuildOpenSearchResponse",
    "BuildQueueProps",
    "BuildQueueResponse",
    "BuildS3BucketProps",
    "BuildS3BucketResponse",
    "BuildSagemakerEndpointProps",
    "BuildSagemakerEndpointResponse",
    "BuildSagemakerNotebookProps",
    "BuildSagemakerNotebookResponse",
    "BuildStateMachineResponse",
    "BuildTopicProps",
    "BuildTopicResponse",
    "BuildVpcProps",
    "BuildWebaclProps",
    "CfnNagSuppressRule",
    "CloudFrontDistributionForApiGatewayResponse",
    "CloudFrontDistributionForMediaStoreResponse",
    "CloudFrontProps",
    "CognitoOptions",
    "CreateCloudFrontDistributionForS3Props",
    "CreateCloudFrontDistributionForS3Response",
    "CreateFargateServiceProps",
    "CreateFargateServiceResponse",
    "CreateSpecRestApiResponse",
    "DeployGlueJobResponse",
    "DeploySagemakerEndpointResponse",
    "DynamoDBProps",
    "EventBridgeProps",
    "EventSourceProps",
    "GlobalLambdaRestApiResponse",
    "GlobalRestApiResponse",
    "GlueProps",
    "KinesisStreamProps",
    "LambdaProps",
    "MediaStoreProps",
    "ObtainAlbProps",
    "ObtainMemcachedClusterProps",
    "OpenSearchProps",
    "RegionalLambdaRestApiResponse",
    "RegionalRestApiResponse",
    "S3OacOrigin",
    "S3OacOriginProps",
    "S3Props",
    "SagemakerProps",
    "SecretsManagerProps",
    "SecurityGroupRuleDefinition",
    "ServiceEndpointTypes",
    "SinkDataStoreProps",
    "SinkStoreType",
    "SnsProps",
    "SqsProps",
    "VpcPropsSet",
    "WafWebAclProps",
]

publication.publish()

def _typecheckingstub__e4b1ec9338820a6eda8ebc288883f36b3164955512161b7cc4267de31aceffb1(
    *,
    api_gateway_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    api_method: builtins.str,
    api_resource: _aws_cdk_aws_apigateway_ceddda9d.IResource,
    request_template: builtins.str,
    service: builtins.str,
    action: typing.Optional[builtins.str] = None,
    additional_request_templates: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    aws_integration_props: typing.Any = None,
    content_type: typing.Optional[builtins.str] = None,
    integration_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.IntegrationResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
    method_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    path: typing.Optional[builtins.str] = None,
    request_model: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_apigateway_ceddda9d.IModel]] = None,
    request_validator: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IRequestValidator] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f79386b6162082a3848170974aab68319c4d3739960a82001b687d0237a8dddb(
    *,
    dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
    existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    max_receive_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e74904f1e6e5dba9531be9c242835b8575d1414c52bbe2797073d8398ac6d7f1(
    *,
    dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_table_interface: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d34caa67dda9b88eb51123471b0d296b6cb3b7f0c31ae08fa986cd195fa0acb(
    *,
    table_interface: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
    table_object: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ab56403f4230368f270729e5586f7c282b901515ba0d833253c7c5934ac0f22(
    *,
    dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_table_interface: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__981983a3a87f559d92cb27756fba1d1d2d62daa4883bbb2f52de4d7ec73c647c(
    *,
    table_interface: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
    table_object: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ace54adaedb6afb446007117f1c60c4ced465e1865ffe38a2282ebf8ccec8f9(
    *,
    cognito_authorized_role_arn: builtins.str,
    domain_name: builtins.str,
    identitypool: _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool,
    userpool: _aws_cdk_aws_cognito_ceddda9d.UserPool,
    client_domain_props: typing.Optional[typing.Union[_aws_cdk_aws_elasticsearch_ceddda9d.CfnDomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    service_role_arn: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35cc08d7e5c8cecd67f63cd630d2213224a588f2ef2baa8b0b71d4cc78b68286(
    *,
    domain: _aws_cdk_aws_elasticsearch_ceddda9d.CfnDomain,
    role: _aws_cdk_aws_iam_ceddda9d.Role,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__402df10e46ea685c3374efa6de25289f47ef9eea04092ab007b597af4696fe41(
    *,
    event_bus_props: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_event_bus_interface: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf8f7cc42528bcc97b5baee443c3a742df7508c5f8a6f86fb48eee982b13dfa(
    *,
    database: _aws_cdk_aws_glue_ceddda9d.CfnDatabase,
    table: _aws_cdk_aws_glue_ceddda9d.CfnTable,
    etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    existing_cfn_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
    glue_job_props: typing.Any = None,
    output_data_store: typing.Optional[typing.Union[SinkDataStoreProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11a604b08bf1cad91185d9f9c8a5a6d00078574c65293412cd1679923fd362f8(
    *,
    job: _aws_cdk_aws_glue_ceddda9d.CfnJob,
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97248fcc6a2ae901e8446e8b76807bca4718121ad43df2905dd67d4e945615dc(
    *,
    existing_index_obj: typing.Optional[_aws_cdk_aws_kendra_ceddda9d.CfnIndex] = None,
    kendra_index_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d782131c01b404df6d09dce3e6a0b081487eeabfad4dcf5bf9b8675f66aaa00b(
    *,
    kinesis_firehose: _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream,
    kinesis_analytics_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d293590656a573587342e1cafc604c4eac77ead41a7bdf61115acb332a86bef(
    *,
    existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
    kinesis_stream_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesis_ceddda9d.StreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c909e838eec4699e3b2bf33068f24227227f2e29c58156725d344e7b43ce564c(
    *,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99d575e7df229e6d535706fb7d502e7c815c863d7890f8d5daa6349619ba52f6(
    *,
    cognito_authorized_role_arn: builtins.str,
    identitypool: _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool,
    open_search_domain_name: builtins.str,
    userpool: _aws_cdk_aws_cognito_ceddda9d.UserPool,
    client_domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    service_role_arn: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__999af291cbe0b3ac93ce7fcd7ec44dc0cc2fba2cea7bfa0fb68b20e641effee2(
    *,
    domain: _aws_cdk_aws_opensearchservice_ceddda9d.CfnDomain,
    role: _aws_cdk_aws_iam_ceddda9d.Role,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6b0628b99348c4f52c56911b1d1df16b203612119c6a5d046c912ca315ff851(
    *,
    dead_letter_queue: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a8eceeccf20ddfc7f75482ccc95d2cd1f427caa71417210872f02f26beeb4eb(
    *,
    queue: _aws_cdk_aws_sqs_ceddda9d.Queue,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__477f8910cdb0bca2545f20be9fd9a69e561013fbe00f14e8780f43e3b607f732(
    *,
    bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_s3_access_logs: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbb87cbe234079b3231368effad74ccd4f3add89bedc907550a84d27b74ccf1f(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
    logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5fde21b1134934aa7c14818fc1bd40b664570c8ff0c7162e476f19f197b2ea4(
    *,
    endpoint_config_props: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfigProps, typing.Dict[builtins.str, typing.Any]]] = None,
    endpoint_props: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_sagemaker_endpoint_obj: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint] = None,
    model_props: typing.Any = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbc439cfcc9233f3830549ca49591814eb1a90e5ff9306cc080d2433ac634b42(
    *,
    endpoint: _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint,
    endpoint_config: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig] = None,
    model: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3f078a7bfd43b5d1505dfb95fd8d25b125648f08a25e307fc3bfeeb5122665c(
    *,
    role: _aws_cdk_aws_iam_ceddda9d.Role,
    deploy_inside_vpc: typing.Optional[builtins.bool] = None,
    existing_notebook_obj: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance] = None,
    sagemaker_notebook_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64202e3614dc62b35135f3089b90c18a208eff665aed57af301adc2b47fe7565(
    *,
    notebook: _aws_cdk_aws_sagemaker_ceddda9d.CfnNotebookInstance,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59bc37dbb01994ff547e71caebd074472187780f69d4ea13ee1b5dcb608c782b(
    *,
    log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb734897393ecced90b642fd1b813f4d1e01378c0fc8a7edbfb24ede093d9db7(
    *,
    enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_topic_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36d2b4d1a520196266ff49496e619764cc478cfe3248684fd519c5c544c8d04(
    *,
    topic: _aws_cdk_aws_sns_ceddda9d.Topic,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba77dacfeb009599df76f2f3981f0e9d35104df22ff4d1aea91142e42745ba51(
    *,
    default_vpc_props: typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]],
    construct_vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    user_vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c35365146428e8cffe0bebcbe653e04ec2c2fec9c6fb055fbc3578eb6721b7b(
    *,
    existing_webacl_obj: typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL] = None,
    webacl_props: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e488fbb31c8c315fca374532df51ff6ae1a4249bebed411f394e2ae3fb74eef0(
    *,
    id: builtins.str,
    reason: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28e9958969b69d0c97ca692c45e5f4cd38c0a074d7bc482888050927296c29ff(
    *,
    distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
    cloudfront_function: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function] = None,
    logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39bce18a31569e2158389732534266e87e792a1af744d954a8b870e46d37ad50(
    *,
    distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
    request_policy: _aws_cdk_aws_cloudfront_ceddda9d.OriginRequestPolicy,
    cloudfront_function: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function] = None,
    logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd3111b21580a09c6860dda1c78369e81b4db80bfcf046e07f6921b72d858ab8(
    *,
    insert_http_security_headers: typing.Optional[builtins.bool] = None,
    response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ab3cd723e5c01a12a9f21b04d8cb1909bd59787d38342b627934c458e0bfeee(
    *,
    identitypool: _aws_cdk_aws_cognito_ceddda9d.CfnIdentityPool,
    userpool: _aws_cdk_aws_cognito_ceddda9d.UserPool,
    userpoolclient: _aws_cdk_aws_cognito_ceddda9d.UserPoolClient,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90026d4ab83a876c6e64a2dacfaccc19f6269116b2ba36f77701cc6f4ea0fd6f(
    *,
    source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    cloud_front_distribution_props: typing.Any = None,
    cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    http_security_headers: typing.Optional[builtins.bool] = None,
    response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0059c54a562cae25a34d2e1d4ea54add942d0efeeab06ea1102d29badea86028(
    *,
    distribution: _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
    cloudfront_function: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function] = None,
    logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    origin_access_control: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c6e4df86cd93502707716761971bda5fd3bb19a72a702c7dfc4fb2c89254b67(
    *,
    construct_vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    client_cluster_props: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ClusterProps, typing.Dict[builtins.str, typing.Any]]] = None,
    client_container_definition_props: typing.Any = None,
    client_fargate_service_props: typing.Any = None,
    client_fargate_task_definition_props: typing.Any = None,
    ecr_image_version: typing.Optional[builtins.str] = None,
    ecr_repository_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ddf26049ece8a7ca2d07de8a059523b50f38ce266281eb6f6a2c333647bc77a(
    *,
    container_definition: _aws_cdk_aws_ecs_ceddda9d.ContainerDefinition,
    service: _aws_cdk_aws_ecs_ceddda9d.FargateService,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__958271d7a6ef26178c4bc3d921903ed81f28d55fff334bbdb2f005a34fa081a8(
    *,
    api: _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi,
    log_group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0133b791a4fb505bbd37620b5d8a5e3b8d656dc20e1134a297327ddab20258d3(
    *,
    job: _aws_cdk_aws_glue_ceddda9d.CfnJob,
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cc7c36afe92b0a37e3240ec5f8bd8933971fee5d99cf624253581e0d62fb68f(
    *,
    endpoint: _aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint,
    endpoint_config: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointConfig] = None,
    model: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnModel] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb247f6ada82965a3afeba568ee3ee0a3bacfe3f70c90eb7a7d261e9aba05147(
    *,
    dynamo_table_props: typing.Optional[typing.Union[_aws_cdk_aws_dynamodb_ceddda9d.TableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_table_interface: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    existing_table_obj: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93242b8fe544dd6ab96871ea0286ca1ca0675f344a0e8e2fd2116e52aa4fdabf(
    *,
    event_bus_props: typing.Union[_aws_cdk_aws_events_ceddda9d.EventBusProps, typing.Dict[builtins.str, typing.Any]],
    existing_event_bus_interface: _aws_cdk_aws_events_ceddda9d.IEventBus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd9154864f9398b573005d4bb551334a4a15e90d5c251f215681508058cb7106(
    *,
    deploy_sqs_dlq_queue: typing.Optional[builtins.bool] = None,
    event_source_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_event_sources_ceddda9d.StreamEventSourceProps, typing.Dict[builtins.str, typing.Any]]] = None,
    sqs_dlq_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a66c905c067e321062fc436583c2316dd1c39ba83fffe345fbb8186a95d3978(
    *,
    api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb6d18a6974ba49897c4231d68397e8ad9509c9459c38c09cb51016796a0d455(
    *,
    api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    log_group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0512c4e0b6637c93558f3e29adea206d1e83e571d9700ae1ad6925b8f0ce5b98(
    *,
    etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    existing_glue_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
    existing_table: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable] = None,
    field_schema: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    glue_job_props: typing.Any = None,
    table_propss: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTableProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3d777f3fce2080f6b27b83b17d7be6eb873a69ffa58b131dc28af4c0a6d232(
    *,
    existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
    kinesis_stream_props: typing.Optional[typing.Union[_aws_cdk_aws_kinesis_ceddda9d.StreamProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d42be92054867170509a996825e08a868a93f029408e224c3d4c5f0a772762ec(
    *,
    existing_lambda_obj: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    lambda_function_props: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.FunctionProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2aa532ddbd324fb791db84dcad85f906a5b71e1140b139d99d630f5200479af(
    *,
    existing_media_store_container_obj: typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer] = None,
    media_store_container_props: typing.Optional[typing.Union[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12b14feea16b19036cf050ea8dd837f794807f0bf081e9b64939210089265868(
    *,
    public_api: builtins.bool,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    existing_load_balancer_obj: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer] = None,
    load_balancer_props: typing.Any = None,
    log_access_logs: typing.Optional[builtins.bool] = None,
    logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6259aab05fc4d80010f467a98da23803b608c0fb9c2637f8dc91b1be476b5e50(
    *,
    cache_security_group_id: builtins.str,
    cache_port: typing.Any = None,
    cache_props: typing.Any = None,
    existing_cache: typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnCacheCluster] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87594edd93213c38ce202aa16be748b2b19d103564cbf8a1b355560207fbecc6(
    *,
    open_search_domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CfnDomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8de3143e71bde6dafd77c44cdaf6b172642b82573eeb0c78376630da9ff0f010(
    *,
    api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69f9376c99111a4c77b49a86b91b6288516d5aafef42d7596270d8e3dab8a452(
    *,
    api: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    log_group: _aws_cdk_aws_logs_ceddda9d.LogGroup,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44846869b9ecaeab140b843e216e72ede263e14e7846fdeed302ad40eedcc020(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    *,
    origin_access_control: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl] = None,
    origin_path: typing.Optional[builtins.str] = None,
    connection_attempts: typing.Optional[jsii.Number] = None,
    connection_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    origin_id: typing.Optional[builtins.str] = None,
    origin_shield_enabled: typing.Optional[builtins.bool] = None,
    origin_shield_region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b0973bdb62c2264b514644e251318ac9dcde1b359c646d66b5a8a10db79f8b(
    scope: _constructs_77d1e7e8.Construct,
    *,
    origin_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4727907366b00308bea7c2d08561f315c9f243b37d0b3a99db676ce6963cb09(
    *,
    connection_attempts: typing.Optional[jsii.Number] = None,
    connection_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    origin_id: typing.Optional[builtins.str] = None,
    origin_shield_enabled: typing.Optional[builtins.bool] = None,
    origin_shield_region: typing.Optional[builtins.str] = None,
    origin_path: typing.Optional[builtins.str] = None,
    origin_access_control: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.CfnOriginAccessControl] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88e247efc77c0ef836bf304cd9929e60e1bd45ac671a55344bb1cb842fc5d67f(
    *,
    bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_bucket_interface: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    existing_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    existing_logging_bucket_obj: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    log_s3_access_logs: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__283c859cb26d60c5956aa575637cb020b0fca8aae26fb332e5cf234df91b38c2(
    *,
    endpoint_props: typing.Optional[typing.Union[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpointProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_sagemaker_endpoint_obj: typing.Optional[_aws_cdk_aws_sagemaker_ceddda9d.CfnEndpoint] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6354a4887fd34fa60206fc7671e58c335a07947a56bf229c7f1ef1c1a7ea6775(
    *,
    existing_secret_obj: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
    secret_props: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1b63a5b21e67fc626e311bcd9d47fed6238a24e4dfab400e1c7d46f35e380aa(
    *,
    connection: _aws_cdk_aws_ec2_ceddda9d.Port,
    peer: _aws_cdk_aws_ec2_ceddda9d.IPeer,
    description: typing.Optional[builtins.str] = None,
    remote_rule: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cb5014b4d7319f98a3e761f0cdfddf1180509c575fcd7d2d58ae702d7f8493c(
    *,
    datastore_type: SinkStoreType,
    existing_s3_output_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    output_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bca360d8cee23ba56d2f45f6f01d513bcce80deec27a4677ff3e775452f6238(
    *,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_topic_obj: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    existing_topic_object: typing.Optional[_aws_cdk_aws_sns_ceddda9d.Topic] = None,
    topic_props: typing.Optional[typing.Union[_aws_cdk_aws_sns_ceddda9d.TopicProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3536696b3fd1fdb7ce43c98c85cb8881b09b6c0b3f129c94eba97862116dbaaa(
    *,
    dead_letter_queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
    deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    encryption_key_props: typing.Optional[typing.Union[_aws_cdk_aws_kms_ceddda9d.KeyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_queue_obj: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    queue_props: typing.Optional[typing.Union[_aws_cdk_aws_sqs_ceddda9d.QueueProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e2cfb976c78d7138f30cbe00e80016d7751fe28f01cfc46671c7ac62704821(
    *,
    deploy_vpc: typing.Optional[builtins.bool] = None,
    existing_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_props: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f99175f2cfd825669300bdabff3e768dcf3371a1530a916000af2c30f820110(
    *,
    existing_webacl_obj: _aws_cdk_aws_wafv2_ceddda9d.CfnWebACL,
    webacl_props: typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACLProps, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

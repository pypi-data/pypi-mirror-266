'''
# Amazon Textract IDP CDK Constructs

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

# Context

This CDK Construct can be used as Step Function task and call Textract in Asynchonous mode for DetectText and AnalyzeDocument APIs.

For samples on usage, look at [Amazon Textact IDP CDK Stack Samples](https://github.com/aws-samples/amazon-textract-idp-cdk-stack-samples)

## Input

Expects a Manifest JSON at 'Payload'.
Manifest description: https://pypi.org/project/schadem-tidp-manifest/

Example call in Python

```python
        textract_async_task = t_async.TextractGenericAsyncSfnTask(
            self,
            "textract-async-task",
            s3_output_bucket=s3_output_bucket,
            s3_temp_output_prefix=s3_temp_output_prefix,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            lambda_log_level="DEBUG",
            timeout=Duration.hours(24),
            input=sfn.TaskInput.from_object({
                "Token":
                sfn.JsonPath.task_token,
                "ExecutionId":
                sfn.JsonPath.string_at('$$.Execution.Id'),
                "Payload":
                sfn.JsonPath.entire_payload,
            }),
            result_path="$.textract_result")
```

#### Query Parameter

Example:

```python

            input=sfn.TaskInput.from_object({
                "Token":
                sfn.JsonPath.task_token,
                "ExecutionId":
                sfn.JsonPath.string_at('$$.Execution.Id'),
                "Payload":
                sfn.JsonPath.entire_payload,
                "Query": [
                           {
                                'Text': 'string',
                                'Alias': 'string',
                                'Pages': [
                                    'string',
                                ]
                            },
                                {
                                "Text": "What is the name of the realestate company",
                                "Alias": "APP_COMPANY_NAME"
                            },
                            {
                                "Text": "What is the name of the applicant or the prospective tenant",
                                "Alias": "APP_APPLICANT_NAME"
                            },
                ]
            }),

```

Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract/client/start_document_analysis.html

To add a query parameter to the Manifest JSON, we are going to leverage the 'convert_manifest_queries_config_to_caller'. It transforms a list of Query objects (as indicated by the type hint List[tm.Query]) into a QueriesConfig object (as indicated by the return type tc.QueriesConfig).

The function expects a list of Query objects as input. Each Query object should have the following attributes:

* text (required)
* alias (opt)
* pages (opt)

The function creates a new QueriesConfig object. If the input list is not empty, it creates a list comprehension that generates a new Query object for each Query object in the input list, maintaining the same text, alias, and pages values. If the input list is empty, it simply creates a QueriesConfig object with an empty queries list.

## Output

Adds the "TextractTempOutputJsonPath" to the Step Function ResultPath. At this location the Textract output is stored as individual JSON files. Use the CDK Construct schadem-cdk-construct-sfn-textract-output-config-to-json to combine them to one single JSON file.

example with ResultPath = textract_result (like configured above):

```
"textract_result": {
    "TextractTempOutputJsonPath": "s3://schademcdkstackpaystuban-schademcdkidpstackpaystu-bt0j5wq0zftu/textract-temp-output/c6e141e8f4e93f68321c17dcbc6bf7291d0c8cdaeb4869758604c387ce91a480"
  }
```

## Spacy Classification

Expect a Spacy textcat model at the root of the directory. Call the script <TO_INSERT) to copy a public one which classifies Paystub and W2.

aws s3 cp s3://amazon-textract-public-content/constructs/en_textcat_demo-0.0.0.tar.gz .

### How to use Workmail Integration

In order to demonstrate this functionality, I have used below architecture where once the inbound email is delivered to your Amazon workmail inbox and if the pattern/s matches, it will invoke the rule action which is inovocation of a lambda function in this case. You can use my sample code to fetch the inbound email message body and parse it properly as text.

![architecture](./images/Workmail_Lambda.png)

### Prerequisites

1. As I have used Python 3.6 as my Lambda function runtime hence some knowledge of python 3 version is required.

### Steps

1. First setup an Amazon workmail site, setup an organization and create a user access by following steps mentioned in 'Getting Started' document [here](https://docs.aws.amazon.com/workmail/latest/adminguide/howto-start.html). Once above setup process is done, you will have access to https://*your Organization*.awsapps.com/mail webmail url and you can login using your created user's username / password to access your emails.
2. Now we will create a lambda function which will be invoked once inbound email reaches the inbox and email flow rule pattern is matched (more on this in below steps). You can use the sample lambda python(3.6) code ( lambda_function.py) provided in the 'code' folder for the same. It will fetch the inbound email message body and then parse it properly to get the message body as text. Once you get it as text you can perform various operations on it.
3. Inbound email flow rules, also called rule actions, automatically apply to all email messages sent to anyone inside of the Amazon WorkMail organization. This differs from email rules for individual mailboxes. Now we will set up email flow rules to handle email flows based on email addresses or domains. Email flow rules are based on both the sender's and recipient's email addresses or domains.

To create an email flow rule, we need to specify a rule action to apply to an email when a specified pattern is matched. Follow the documenttion link [here](https://docs.aws.amazon.com/workmail/latest/adminguide/email-flows.html#email-flows-rule-actions) to create email flow rule for your organization which you created in step #1 above. you have to select Action=Run Lambda for your rule. Below is the email flow rule created by me:

![Email Flow Rule](./images/email_rule_1.png)

you can now follow documentation link [here](https://docs.aws.amazon.com/workmail/latest/adminguide/email-flows.html#email-flows-patterns) to create pattern/s which need to be satisfied first in order to invoke the rule action (in this case it will invoke our lambda function). For this sample code functionality I have used my email address as pattern in 'origns' and my domain as pattern in 'destinations'. so in this case the lambda function will only be invoke if inbound email sender is my email address and destination is my domain only but you can set patterns as per your requirements. Below screen shots depicts my patterns:

![Origin pattern](./images/email_rule_2.png)

![Destnation pattern](./images/email_rule_3.png)
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
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.aws_stepfunctions_tasks as _aws_cdk_aws_stepfunctions_tasks_ceddda9d
import constructs as _constructs_77d1e7e8


class CSVToAuroraTask(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.CSVToAuroraTask",
):
    '''CSVToAuroraTask is a demo construct to show import into a serverless Aurora DB.

    At the moment it also creates the Aurora Serverless RDS DB, initializes a table structure the matches the output of the GenerateCSV construct.
    The Step Functions flow expect a pointer to a CSV at "csv_output_location"."TextractOutputCSVPath" and uses that to execute a batch insert statement command.

    Example::

       csv_to_aurora_task = tcdk.CSVToAuroraTask(
        self,
        "CsvToAurora",
        vpc=vpc,
        integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
        lambda_log_level="DEBUG",
        timeout=Duration.hours(24),
        input=sfn.TaskInput.from_object({
          "Token":
          sfn.JsonPath.task_token,
          "ExecutionId":
          sfn.JsonPath.string_at('$$.Execution.Id'),
          "Payload":
          sfn.JsonPath.entire_payload
        }),
        result_path="$.textract_result")

    Input: "csv_output_location"."TextractOutputCSVPath"
    Output: CSV in Aurora Serverless DB, table name 'textractcsvimport"
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        aurora_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        csv_to_aurora_backoff_rate: typing.Optional[jsii.Number] = None,
        csv_to_aurora_interval: typing.Optional[jsii.Number] = None,
        csv_to_aurora_max_retries: typing.Optional[jsii.Number] = None,
        db_cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IServerlessCluster] = None,
        enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: Descriptive identifier for this chainable.
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param aurora_security_group: auroraSecurity Group for Cluster.
        :param csv_to_aurora_backoff_rate: default is 1.1.
        :param csv_to_aurora_interval: default is 1.
        :param csv_to_aurora_max_retries: 
        :param db_cluster: DBCluster to import into.
        :param enable_cloud_watch_metrics_and_dashboard: enable CloudWatch Metrics and Dashboard. Default: - false
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param lambda_log_level: 
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_security_group: lambdaSecurity Group for Cluster.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param textract_state_machine_timeout_minutes: 
        :param vpc: VPC to install the database into, optional if dbCluster is passed in.
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a2e915f2bf738499fb1487469c5a5e7b97f3ea53531d09db1a1bacc5f572542)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CSVToAuroraTaskProps(
            associate_with_parent=associate_with_parent,
            aurora_security_group=aurora_security_group,
            csv_to_aurora_backoff_rate=csv_to_aurora_backoff_rate,
            csv_to_aurora_interval=csv_to_aurora_interval,
            csv_to_aurora_max_retries=csv_to_aurora_max_retries,
            db_cluster=db_cluster,
            enable_cloud_watch_metrics_and_dashboard=enable_cloud_watch_metrics_and_dashboard,
            input=input,
            lambda_log_level=lambda_log_level,
            lambda_memory=lambda_memory,
            lambda_security_group=lambda_security_group,
            lambda_timeout=lambda_timeout,
            name=name,
            textract_state_machine_timeout_minutes=textract_state_machine_timeout_minutes,
            vpc=vpc,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig]:
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "taskPolicies"))

    @builtins.property
    @jsii.member(jsii_name="auroraSecurityGroup")
    def aurora_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "auroraSecurityGroup"))

    @aurora_security_group.setter
    def aurora_security_group(
        self,
        value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82837931957c3dd9d3602fad7af22ad0fcacfd3cd4cc6b9199599ad4623503c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auroraSecurityGroup", value)

    @builtins.property
    @jsii.member(jsii_name="csvToAuroraFunction")
    def csv_to_aurora_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "csvToAuroraFunction"))

    @csv_to_aurora_function.setter
    def csv_to_aurora_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f76fbf836296c7c37da75f18dabbda8311aeeb758c33dea2f339743fbfb9b3d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "csvToAuroraFunction", value)

    @builtins.property
    @jsii.member(jsii_name="dbCluster")
    def db_cluster(self) -> _aws_cdk_aws_rds_ceddda9d.IServerlessCluster:
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IServerlessCluster, jsii.get(self, "dbCluster"))

    @db_cluster.setter
    def db_cluster(self, value: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e962768ad2bfc77aaeda9d218418307d7d450329f1735abf8f7332a1bc4f9687)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbCluster", value)

    @builtins.property
    @jsii.member(jsii_name="lambdaSecurityGroup")
    def lambda_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "lambdaSecurityGroup"))

    @lambda_security_group.setter
    def lambda_security_group(
        self,
        value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaabceaa7d653a142ec9115e2e01f188d1f4a9be5bb0ffcef33b721cfde765d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lambdaSecurityGroup", value)

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40bc9b871f0e01af4838f0f7a8326ba8c48c05b812e3ea9cfb29c8eb921ad942)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e0969ad66f893b6d17a70a58d88d7d04ef99b2824366468bf6d55bc298423e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="csvToAuroraNumberRowsInsertedMetric")
    def csv_to_aurora_number_rows_inserted_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "csvToAuroraNumberRowsInsertedMetric"))

    @csv_to_aurora_number_rows_inserted_metric.setter
    def csv_to_aurora_number_rows_inserted_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ef4b9117bbdbe85cdc85ec1901714ddc9e6ef2395abb4701064b4a54099504)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "csvToAuroraNumberRowsInsertedMetric", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.CSVToAuroraTaskProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "associate_with_parent": "associateWithParent",
        "aurora_security_group": "auroraSecurityGroup",
        "csv_to_aurora_backoff_rate": "csvToAuroraBackoffRate",
        "csv_to_aurora_interval": "csvToAuroraInterval",
        "csv_to_aurora_max_retries": "csvToAuroraMaxRetries",
        "db_cluster": "dbCluster",
        "enable_cloud_watch_metrics_and_dashboard": "enableCloudWatchMetricsAndDashboard",
        "input": "input",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory": "lambdaMemory",
        "lambda_security_group": "lambdaSecurityGroup",
        "lambda_timeout": "lambdaTimeout",
        "name": "name",
        "textract_state_machine_timeout_minutes": "textractStateMachineTimeoutMinutes",
        "vpc": "vpc",
    },
)
class CSVToAuroraTaskProps(_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        aurora_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        csv_to_aurora_backoff_rate: typing.Optional[jsii.Number] = None,
        csv_to_aurora_interval: typing.Optional[jsii.Number] = None,
        csv_to_aurora_max_retries: typing.Optional[jsii.Number] = None,
        db_cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IServerlessCluster] = None,
        enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param aurora_security_group: auroraSecurity Group for Cluster.
        :param csv_to_aurora_backoff_rate: default is 1.1.
        :param csv_to_aurora_interval: default is 1.
        :param csv_to_aurora_max_retries: 
        :param db_cluster: DBCluster to import into.
        :param enable_cloud_watch_metrics_and_dashboard: enable CloudWatch Metrics and Dashboard. Default: - false
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param lambda_log_level: 
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_security_group: lambdaSecurity Group for Cluster.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param textract_state_machine_timeout_minutes: 
        :param vpc: VPC to install the database into, optional if dbCluster is passed in.
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c2ee7750549ff02b28f95157bc497795ddaa5f6133871e998e75e7abe2f0dd)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument associate_with_parent", value=associate_with_parent, expected_type=type_hints["associate_with_parent"])
            check_type(argname="argument aurora_security_group", value=aurora_security_group, expected_type=type_hints["aurora_security_group"])
            check_type(argname="argument csv_to_aurora_backoff_rate", value=csv_to_aurora_backoff_rate, expected_type=type_hints["csv_to_aurora_backoff_rate"])
            check_type(argname="argument csv_to_aurora_interval", value=csv_to_aurora_interval, expected_type=type_hints["csv_to_aurora_interval"])
            check_type(argname="argument csv_to_aurora_max_retries", value=csv_to_aurora_max_retries, expected_type=type_hints["csv_to_aurora_max_retries"])
            check_type(argname="argument db_cluster", value=db_cluster, expected_type=type_hints["db_cluster"])
            check_type(argname="argument enable_cloud_watch_metrics_and_dashboard", value=enable_cloud_watch_metrics_and_dashboard, expected_type=type_hints["enable_cloud_watch_metrics_and_dashboard"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory", value=lambda_memory, expected_type=type_hints["lambda_memory"])
            check_type(argname="argument lambda_security_group", value=lambda_security_group, expected_type=type_hints["lambda_security_group"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument textract_state_machine_timeout_minutes", value=textract_state_machine_timeout_minutes, expected_type=type_hints["textract_state_machine_timeout_minutes"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if associate_with_parent is not None:
            self._values["associate_with_parent"] = associate_with_parent
        if aurora_security_group is not None:
            self._values["aurora_security_group"] = aurora_security_group
        if csv_to_aurora_backoff_rate is not None:
            self._values["csv_to_aurora_backoff_rate"] = csv_to_aurora_backoff_rate
        if csv_to_aurora_interval is not None:
            self._values["csv_to_aurora_interval"] = csv_to_aurora_interval
        if csv_to_aurora_max_retries is not None:
            self._values["csv_to_aurora_max_retries"] = csv_to_aurora_max_retries
        if db_cluster is not None:
            self._values["db_cluster"] = db_cluster
        if enable_cloud_watch_metrics_and_dashboard is not None:
            self._values["enable_cloud_watch_metrics_and_dashboard"] = enable_cloud_watch_metrics_and_dashboard
        if input is not None:
            self._values["input"] = input
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory is not None:
            self._values["lambda_memory"] = lambda_memory
        if lambda_security_group is not None:
            self._values["lambda_security_group"] = lambda_security_group
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if name is not None:
            self._values["name"] = name
        if textract_state_machine_timeout_minutes is not None:
            self._values["textract_state_machine_timeout_minutes"] = textract_state_machine_timeout_minutes
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def associate_with_parent(self) -> typing.Optional[builtins.bool]:
        '''Pass the execution ID from the context object to the execution input.

        This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines.

        If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely.

        :default: - false

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-nested-workflows.html#nested-execution-startid
        '''
        result = self._values.get("associate_with_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def aurora_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''auroraSecurity Group for Cluster.'''
        result = self._values.get("aurora_security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def csv_to_aurora_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''default is 1.1.'''
        result = self._values.get("csv_to_aurora_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def csv_to_aurora_interval(self) -> typing.Optional[jsii.Number]:
        '''default is 1.'''
        result = self._values.get("csv_to_aurora_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def csv_to_aurora_max_retries(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("csv_to_aurora_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_cluster(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IServerlessCluster]:
        '''DBCluster to import into.'''
        result = self._values.get("db_cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IServerlessCluster], result)

    @builtins.property
    def enable_cloud_watch_metrics_and_dashboard(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''enable CloudWatch Metrics and Dashboard.

        :default: - false
        '''
        result = self._values.get("enable_cloud_watch_metrics_and_dashboard")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def input(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput]:
        '''The JSON input for the execution, same as that of StartExecution.

        :default: - The state input (JSON path '$')

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory(self) -> typing.Optional[jsii.Number]:
        '''Memory allocated to Lambda function, default 512.'''
        result = self._values.get("lambda_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''lambdaSecurity Group for Cluster.'''
        result = self._values.get("lambda_security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda Function Timeout in seconds, default 300.'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the execution, same as that of StartExecution.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_state_machine_timeout_minutes(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("textract_state_machine_timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC to install the database into, optional if dbCluster is passed in.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CSVToAuroraTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComprehendGenericSyncSfnTask(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.ComprehendGenericSyncSfnTask",
):
    '''Calls a Comprehend Classification endpoint and parses the result, filters on > 50 % confidence and sets the highest confidence score classification.

    Input: "textract_result"."txt_output_location"
    Output:  { "documentType": "AWS_PAYSTUBS" } (example will be at "classification"."documentType")

    Example (Python::

        comprehend_sync_task = tcdk.ComprehendGenericSyncSfnTask(
            self,
            "Classification",
            comprehend_classifier_arn=
            '<your comprehend classifier arn>',
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            lambda_log_level="DEBUG",
            timeout=Duration.hours(24),
            input=sfn.TaskInput.from_object({
                "Token":
                sfn.JsonPath.task_token,
                "ExecutionId":
                sfn.JsonPath.string_at('$$.Execution.Id'),
                "Payload":
                sfn.JsonPath.entire_payload,
            }),
            result_path="$.classification")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comprehend_classifier_arn: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        comprehend_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
        comprehend_async_call_interval: typing.Optional[jsii.Number] = None,
        comprehend_async_call_max_retries: typing.Optional[jsii.Number] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        s3_output_bucket: typing.Optional[builtins.str] = None,
        s3_output_prefix: typing.Optional[builtins.str] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: Descriptive identifier for this chainable.
        :param comprehend_classifier_arn: 
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param comprehend_async_call_backoff_rate: default is 1.1.
        :param comprehend_async_call_interval: default is 1.
        :param comprehend_async_call_max_retries: 
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: 
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_output_prefix: The prefix to use for the temporary output files (e. g. output from async process before stiching together)
        :param textract_state_machine_timeout_minutes: how long can we wait for the process (default is 60 minutes).
        :param workflow_tracing_enabled: 
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63c572f65dc7f491f95786c369eac23465969ddc2b18fc82124b18bbf54608ff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ComprehendGenericSyncSfnTaskProps(
            comprehend_classifier_arn=comprehend_classifier_arn,
            associate_with_parent=associate_with_parent,
            comprehend_async_call_backoff_rate=comprehend_async_call_backoff_rate,
            comprehend_async_call_interval=comprehend_async_call_interval,
            comprehend_async_call_max_retries=comprehend_async_call_max_retries,
            input=input,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory=lambda_memory,
            lambda_timeout=lambda_timeout,
            name=name,
            output_policy_statements=output_policy_statements,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            s3_output_bucket=s3_output_bucket,
            s3_output_prefix=s3_output_prefix,
            textract_state_machine_timeout_minutes=textract_state_machine_timeout_minutes,
            workflow_tracing_enabled=workflow_tracing_enabled,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig]:
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "taskPolicies"))

    @builtins.property
    @jsii.member(jsii_name="comprehendSyncCallFunction")
    def comprehend_sync_call_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "comprehendSyncCallFunction"))

    @comprehend_sync_call_function.setter
    def comprehend_sync_call_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b8c4f3a3b7df132617bb763e98f942130118e9e14cda98200ec63a3dd65302a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comprehendSyncCallFunction", value)

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88605655023bd2fb2a31c523e359bcdee1cc7c910354b7e49356a86711628c95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd1df667c4c218e3d6dc978377c6767932411e6c4cd185c49592593e34cee887)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.ComprehendGenericSyncSfnTaskProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "comprehend_classifier_arn": "comprehendClassifierArn",
        "associate_with_parent": "associateWithParent",
        "comprehend_async_call_backoff_rate": "comprehendAsyncCallBackoffRate",
        "comprehend_async_call_interval": "comprehendAsyncCallInterval",
        "comprehend_async_call_max_retries": "comprehendAsyncCallMaxRetries",
        "input": "input",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory": "lambdaMemory",
        "lambda_timeout": "lambdaTimeout",
        "name": "name",
        "output_policy_statements": "outputPolicyStatements",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "s3_output_bucket": "s3OutputBucket",
        "s3_output_prefix": "s3OutputPrefix",
        "textract_state_machine_timeout_minutes": "textractStateMachineTimeoutMinutes",
        "workflow_tracing_enabled": "workflowTracingEnabled",
    },
)
class ComprehendGenericSyncSfnTaskProps(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps,
):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        comprehend_classifier_arn: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        comprehend_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
        comprehend_async_call_interval: typing.Optional[jsii.Number] = None,
        comprehend_async_call_max_retries: typing.Optional[jsii.Number] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        s3_output_bucket: typing.Optional[builtins.str] = None,
        s3_output_prefix: typing.Optional[builtins.str] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param comprehend_classifier_arn: 
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param comprehend_async_call_backoff_rate: default is 1.1.
        :param comprehend_async_call_interval: default is 1.
        :param comprehend_async_call_max_retries: 
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: 
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_output_prefix: The prefix to use for the temporary output files (e. g. output from async process before stiching together)
        :param textract_state_machine_timeout_minutes: how long can we wait for the process (default is 60 minutes).
        :param workflow_tracing_enabled: 
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2b7726103e7a4c7cea8aea6f000ef6e4dc789c73d251956c09d384beee75afe)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument comprehend_classifier_arn", value=comprehend_classifier_arn, expected_type=type_hints["comprehend_classifier_arn"])
            check_type(argname="argument associate_with_parent", value=associate_with_parent, expected_type=type_hints["associate_with_parent"])
            check_type(argname="argument comprehend_async_call_backoff_rate", value=comprehend_async_call_backoff_rate, expected_type=type_hints["comprehend_async_call_backoff_rate"])
            check_type(argname="argument comprehend_async_call_interval", value=comprehend_async_call_interval, expected_type=type_hints["comprehend_async_call_interval"])
            check_type(argname="argument comprehend_async_call_max_retries", value=comprehend_async_call_max_retries, expected_type=type_hints["comprehend_async_call_max_retries"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory", value=lambda_memory, expected_type=type_hints["lambda_memory"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument output_policy_statements", value=output_policy_statements, expected_type=type_hints["output_policy_statements"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument s3_output_bucket", value=s3_output_bucket, expected_type=type_hints["s3_output_bucket"])
            check_type(argname="argument s3_output_prefix", value=s3_output_prefix, expected_type=type_hints["s3_output_prefix"])
            check_type(argname="argument textract_state_machine_timeout_minutes", value=textract_state_machine_timeout_minutes, expected_type=type_hints["textract_state_machine_timeout_minutes"])
            check_type(argname="argument workflow_tracing_enabled", value=workflow_tracing_enabled, expected_type=type_hints["workflow_tracing_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "comprehend_classifier_arn": comprehend_classifier_arn,
        }
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if associate_with_parent is not None:
            self._values["associate_with_parent"] = associate_with_parent
        if comprehend_async_call_backoff_rate is not None:
            self._values["comprehend_async_call_backoff_rate"] = comprehend_async_call_backoff_rate
        if comprehend_async_call_interval is not None:
            self._values["comprehend_async_call_interval"] = comprehend_async_call_interval
        if comprehend_async_call_max_retries is not None:
            self._values["comprehend_async_call_max_retries"] = comprehend_async_call_max_retries
        if input is not None:
            self._values["input"] = input
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory is not None:
            self._values["lambda_memory"] = lambda_memory
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if name is not None:
            self._values["name"] = name
        if output_policy_statements is not None:
            self._values["output_policy_statements"] = output_policy_statements
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if s3_output_bucket is not None:
            self._values["s3_output_bucket"] = s3_output_bucket
        if s3_output_prefix is not None:
            self._values["s3_output_prefix"] = s3_output_prefix
        if textract_state_machine_timeout_minutes is not None:
            self._values["textract_state_machine_timeout_minutes"] = textract_state_machine_timeout_minutes
        if workflow_tracing_enabled is not None:
            self._values["workflow_tracing_enabled"] = workflow_tracing_enabled

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def comprehend_classifier_arn(self) -> builtins.str:
        result = self._values.get("comprehend_classifier_arn")
        assert result is not None, "Required property 'comprehend_classifier_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associate_with_parent(self) -> typing.Optional[builtins.bool]:
        '''Pass the execution ID from the context object to the execution input.

        This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines.

        If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely.

        :default: - false

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-nested-workflows.html#nested-execution-startid
        '''
        result = self._values.get("associate_with_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def comprehend_async_call_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''default is 1.1.'''
        result = self._values.get("comprehend_async_call_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comprehend_async_call_interval(self) -> typing.Optional[jsii.Number]:
        '''default is 1.'''
        result = self._values.get("comprehend_async_call_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comprehend_async_call_max_retries(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("comprehend_async_call_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def input(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput]:
        '''The JSON input for the execution, same as that of StartExecution.

        :default: - The state input (JSON path '$')

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput], result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory(self) -> typing.Optional[jsii.Number]:
        '''Memory allocated to Lambda function, default 512.'''
        result = self._values.get("lambda_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda Function Timeout in seconds, default 300.'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the execution, same as that of StartExecution.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("output_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        '''location of input S3 objects - if left empty will generate rule for s3 access to all [*].'''
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.'''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_output_bucket(self) -> typing.Optional[builtins.str]:
        '''Bucketname to output data to.'''
        result = self._values.get("s3_output_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_output_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix to use for the temporary output files (e.

        g. output from async process before stiching together)
        '''
        result = self._values.get("s3_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_state_machine_timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''how long can we wait for the process (default is 60 minutes).'''
        result = self._values.get("textract_state_machine_timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def workflow_tracing_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("workflow_tracing_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComprehendGenericSyncSfnTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DocumentSplitter(
    _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineFragment,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.DocumentSplitter",
):
    '''This construct takes in a manifest definition with just the s3Path:.

    example s3Path:
    {"s3Path": "s3://bucketname/prefix/image.png"}

    then it generated single page versions of the multi-page file.
    For PDF the output are single PDF files, for TIFF the output are single TIFF files.

    Example (Python::
    '''

    def __init__(
        self,
        parent: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        max_number_of_pages_per_doc: typing.Optional[jsii.Number] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_document_splitter_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_document_splitter_interval: typing.Optional[jsii.Number] = None,
        textract_document_splitter_max_retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: Descriptive identifier for this chainable.
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_output_prefix: The prefix to use to output files to.
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: Lambda log level.
        :param lambda_memory_mb: Lambda function memory configuration (may need to increase for larger documents).
        :param lambda_timeout: Lambda function timeout (may need to increase for larger documents).
        :param max_number_of_pages_per_doc: 
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param textract_document_splitter_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_document_splitter_interval: 
        :param textract_document_splitter_max_retries: number of retries in Step Function flow. Default: is 100
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2639041e32a9dfde7241ef351ea92ed6441a727bea4f2f0cf8a56cc7f7cb0e6)
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DocumentSplitterProps(
            s3_output_bucket=s3_output_bucket,
            s3_output_prefix=s3_output_prefix,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
            max_number_of_pages_per_doc=max_number_of_pages_per_doc,
            output_policy_statements=output_policy_statements,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            textract_document_splitter_backoff_rate=textract_document_splitter_backoff_rate,
            textract_document_splitter_interval=textract_document_splitter_interval,
            textract_document_splitter_max_retries=textract_document_splitter_max_retries,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="splitterFunction")
    def splitter_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "splitterFunction"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.State:
        '''The start state of this state machine fragment.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.State, jsii.get(self, "startState"))


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.DocumentSplitterProps",
    jsii_struct_bases=[],
    name_mapping={
        "s3_output_bucket": "s3OutputBucket",
        "s3_output_prefix": "s3OutputPrefix",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
        "max_number_of_pages_per_doc": "maxNumberOfPagesPerDoc",
        "output_policy_statements": "outputPolicyStatements",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "textract_document_splitter_backoff_rate": "textractDocumentSplitterBackoffRate",
        "textract_document_splitter_interval": "textractDocumentSplitterInterval",
        "textract_document_splitter_max_retries": "textractDocumentSplitterMaxRetries",
    },
)
class DocumentSplitterProps:
    def __init__(
        self,
        *,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        max_number_of_pages_per_doc: typing.Optional[jsii.Number] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_document_splitter_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_document_splitter_interval: typing.Optional[jsii.Number] = None,
        textract_document_splitter_max_retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_output_prefix: The prefix to use to output files to.
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: Lambda log level.
        :param lambda_memory_mb: Lambda function memory configuration (may need to increase for larger documents).
        :param lambda_timeout: Lambda function timeout (may need to increase for larger documents).
        :param max_number_of_pages_per_doc: 
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param textract_document_splitter_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_document_splitter_interval: 
        :param textract_document_splitter_max_retries: number of retries in Step Function flow. Default: is 100
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99cd884facaff7b56a4ce1fd62f5a59a7644a182c07d44883c1d6ae3de02c232)
            check_type(argname="argument s3_output_bucket", value=s3_output_bucket, expected_type=type_hints["s3_output_bucket"])
            check_type(argname="argument s3_output_prefix", value=s3_output_prefix, expected_type=type_hints["s3_output_prefix"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument max_number_of_pages_per_doc", value=max_number_of_pages_per_doc, expected_type=type_hints["max_number_of_pages_per_doc"])
            check_type(argname="argument output_policy_statements", value=output_policy_statements, expected_type=type_hints["output_policy_statements"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument textract_document_splitter_backoff_rate", value=textract_document_splitter_backoff_rate, expected_type=type_hints["textract_document_splitter_backoff_rate"])
            check_type(argname="argument textract_document_splitter_interval", value=textract_document_splitter_interval, expected_type=type_hints["textract_document_splitter_interval"])
            check_type(argname="argument textract_document_splitter_max_retries", value=textract_document_splitter_max_retries, expected_type=type_hints["textract_document_splitter_max_retries"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_output_bucket": s3_output_bucket,
            "s3_output_prefix": s3_output_prefix,
        }
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if max_number_of_pages_per_doc is not None:
            self._values["max_number_of_pages_per_doc"] = max_number_of_pages_per_doc
        if output_policy_statements is not None:
            self._values["output_policy_statements"] = output_policy_statements
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if textract_document_splitter_backoff_rate is not None:
            self._values["textract_document_splitter_backoff_rate"] = textract_document_splitter_backoff_rate
        if textract_document_splitter_interval is not None:
            self._values["textract_document_splitter_interval"] = textract_document_splitter_interval
        if textract_document_splitter_max_retries is not None:
            self._values["textract_document_splitter_max_retries"] = textract_document_splitter_max_retries

    @builtins.property
    def s3_output_bucket(self) -> builtins.str:
        '''Bucketname to output data to.'''
        result = self._values.get("s3_output_bucket")
        assert result is not None, "Required property 's3_output_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_output_prefix(self) -> builtins.str:
        '''The prefix to use to output files to.'''
        result = self._values.get("s3_output_prefix")
        assert result is not None, "Required property 's3_output_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        '''Lambda log level.'''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''Lambda function memory configuration (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda function timeout (may need to increase for larger documents).'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_number_of_pages_per_doc(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("max_number_of_pages_per_doc")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def output_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("output_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        '''location of input S3 objects - if left empty will generate rule for s3 access to all [*].'''
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.'''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_document_splitter_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''retyr backoff rate.

        :default: is 1.1
        '''
        result = self._values.get("textract_document_splitter_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_document_splitter_interval(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("textract_document_splitter_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_document_splitter_max_retries(self) -> typing.Optional[jsii.Number]:
        '''number of retries in Step Function flow.

        :default: is 100
        '''
        result = self._values.get("textract_document_splitter_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DocumentSplitterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RDSAuroraServerless(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.RDSAuroraServerless",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: VPC to install the database into.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e11147041f993d47d56add049fc858c0d1df6c1127f7137d8661bd07a9f4d405)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RDSAuroraServerlessProps(vpc=vpc)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "RDSAuroraServerlessProps":
        return typing.cast("RDSAuroraServerlessProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="auroraSecurityGroup")
    def aurora_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "auroraSecurityGroup"))

    @aurora_security_group.setter
    def aurora_security_group(
        self,
        value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d557d1c2b59bb23d5cefecf9c7f57d343b756227ed7cf4a8fb8f2fa260e7f8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auroraSecurityGroup", value)

    @builtins.property
    @jsii.member(jsii_name="dbCluster")
    def db_cluster(self) -> _aws_cdk_aws_rds_ceddda9d.IServerlessCluster:
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IServerlessCluster, jsii.get(self, "dbCluster"))

    @db_cluster.setter
    def db_cluster(self, value: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8611db7dda185294a258507b8a8568f28d4356fc4ee494db89c9265f868ff1cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbCluster", value)

    @builtins.property
    @jsii.member(jsii_name="lambdaSecurityGroup")
    def lambda_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "lambdaSecurityGroup"))

    @lambda_security_group.setter
    def lambda_security_group(
        self,
        value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4ce4c6b56e174ea3d2a95f7b17f543c9cf19b46a5be14db0e0e0be863214c1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lambdaSecurityGroup", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.RDSAuroraServerlessProps",
    jsii_struct_bases=[],
    name_mapping={"vpc": "vpc"},
)
class RDSAuroraServerlessProps:
    def __init__(self, *, vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc) -> None:
        '''
        :param vpc: VPC to install the database into.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__187e75bcc1fc38138651a846c6db0b7e0ef1481679b93c68fa26f695a030e11e)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''VPC to install the database into.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RDSAuroraServerlessProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SFExecutionsStartThrottle(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.SFExecutionsStartThrottle",
):
    '''This construct starts State Machine executions based on events, but limits the number of concurrent running executions to a threshold number - S3 - API Gateway - SQS  This version does not yet support passing in a manifest for configuration of Textract features.

    That will be a future enhancement.
    The following resources are created:

    - Lambda function
    - DynamoDB table. For every document pass in an entry in a DynamoDB table is created with a status (RECEIVED, QUEUED, IN_PROGRESS)
    '''

    def __init__(
        self,
        parent: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        state_machine_arn: builtins.str,
        document_status_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        event_source: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
        executions_concurrency_threshold: typing.Optional[jsii.Number] = None,
        executions_counter_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_queue_worker_log_level: typing.Optional[builtins.str] = None,
        lambda_queue_worker_memory: typing.Optional[jsii.Number] = None,
        lambda_queue_worker_timeout: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        sqs_batch: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: -
        :param state_machine_arn: State Machine ARN.
        :param document_status_table: Status table - DynamoDB table with status information for the document execution.
        :param event_source: List of PolicyStatements to attach to the Lambda function.
        :param executions_concurrency_threshold: Executions concurrency, default is 100 should be set to whatever the bottleneck of the workflow is For Textract Asynchronous APIs, that would be the number of concurrent jobs that can be processed For Textract Synchronous APIs, that would be the TPS for the API.
        :param executions_counter_table: Step Functions Executions Counter - DynamoDB table with current count of executions.
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = INFO
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_queue_worker_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = DEBUG
        :param lambda_queue_worker_memory: Memory allocated to Lambda function, default 512.
        :param lambda_queue_worker_timeout: Lambda Function Timeout in seconds, default 300.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param s3_input_bucket: Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param sqs_batch: SQS Batch size when catchup up on queued documents (max 10, which is also the default).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72e5539db4ba9c10e720e52655ff6abf2c03775395aafc3cdd71a1d91c69aff9)
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SFExecutionsStartThrottleProps(
            state_machine_arn=state_machine_arn,
            document_status_table=document_status_table,
            event_source=event_source,
            executions_concurrency_threshold=executions_concurrency_threshold,
            executions_counter_table=executions_counter_table,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory=lambda_memory,
            lambda_queue_worker_log_level=lambda_queue_worker_log_level,
            lambda_queue_worker_memory=lambda_queue_worker_memory,
            lambda_queue_worker_timeout=lambda_queue_worker_timeout,
            lambda_timeout=lambda_timeout,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            sqs_batch=sqs_batch,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property
    @jsii.member(jsii_name="executionsQueueWorkerFunction")
    def executions_queue_worker_function(
        self,
    ) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "executionsQueueWorkerFunction"))

    @executions_queue_worker_function.setter
    def executions_queue_worker_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3abab5947799560a7880220092bc8766496d6cd1c862917d8582ac57a4cc1b36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionsQueueWorkerFunction", value)

    @builtins.property
    @jsii.member(jsii_name="executionsStartThrottleFunction")
    def executions_start_throttle_function(
        self,
    ) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "executionsStartThrottleFunction"))

    @executions_start_throttle_function.setter
    def executions_start_throttle_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f5130d5a60a73150b5abea6c79abb2acecfb9a27dbea8e9a1724eaf900ed3ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionsStartThrottleFunction", value)

    @builtins.property
    @jsii.member(jsii_name="executionsThrottleCounterResetFunction")
    def executions_throttle_counter_reset_function(
        self,
    ) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "executionsThrottleCounterResetFunction"))

    @executions_throttle_counter_reset_function.setter
    def executions_throttle_counter_reset_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__129e5511ad5a05c698fd71fcdb300cab4330ab5b3cd41d6efb0a8f8eb77075af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionsThrottleCounterResetFunction", value)

    @builtins.property
    @jsii.member(jsii_name="documentQueue")
    def document_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], jsii.get(self, "documentQueue"))

    @document_queue.setter
    def document_queue(
        self,
        value: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae42b52edc190822a38868deb658ae9ce847f755cf609cad61aa13633370f24a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "documentQueue", value)

    @builtins.property
    @jsii.member(jsii_name="documentStatusTable")
    def document_status_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], jsii.get(self, "documentStatusTable"))

    @document_status_table.setter
    def document_status_table(
        self,
        value: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a97ef827b78442fb4da04bab1c6919b8f402d05a0c19b6c96ad0e6d0323a2cae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "documentStatusTable", value)

    @builtins.property
    @jsii.member(jsii_name="executionsCounterTable")
    def executions_counter_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], jsii.get(self, "executionsCounterTable"))

    @executions_counter_table.setter
    def executions_counter_table(
        self,
        value: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f91e0a6e744fcfa1b42392cb32a4c95da7836f3df03638d61ac4c6303895fe6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionsCounterTable", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.SFExecutionsStartThrottleProps",
    jsii_struct_bases=[],
    name_mapping={
        "state_machine_arn": "stateMachineArn",
        "document_status_table": "documentStatusTable",
        "event_source": "eventSource",
        "executions_concurrency_threshold": "executionsConcurrencyThreshold",
        "executions_counter_table": "executionsCounterTable",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory": "lambdaMemory",
        "lambda_queue_worker_log_level": "lambdaQueueWorkerLogLevel",
        "lambda_queue_worker_memory": "lambdaQueueWorkerMemory",
        "lambda_queue_worker_timeout": "lambdaQueueWorkerTimeout",
        "lambda_timeout": "lambdaTimeout",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "sqs_batch": "sqsBatch",
    },
)
class SFExecutionsStartThrottleProps:
    def __init__(
        self,
        *,
        state_machine_arn: builtins.str,
        document_status_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        event_source: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
        executions_concurrency_threshold: typing.Optional[jsii.Number] = None,
        executions_counter_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_queue_worker_log_level: typing.Optional[builtins.str] = None,
        lambda_queue_worker_memory: typing.Optional[jsii.Number] = None,
        lambda_queue_worker_timeout: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        sqs_batch: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param state_machine_arn: State Machine ARN.
        :param document_status_table: Status table - DynamoDB table with status information for the document execution.
        :param event_source: List of PolicyStatements to attach to the Lambda function.
        :param executions_concurrency_threshold: Executions concurrency, default is 100 should be set to whatever the bottleneck of the workflow is For Textract Asynchronous APIs, that would be the number of concurrent jobs that can be processed For Textract Synchronous APIs, that would be the TPS for the API.
        :param executions_counter_table: Step Functions Executions Counter - DynamoDB table with current count of executions.
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = INFO
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_queue_worker_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = DEBUG
        :param lambda_queue_worker_memory: Memory allocated to Lambda function, default 512.
        :param lambda_queue_worker_timeout: Lambda Function Timeout in seconds, default 300.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param s3_input_bucket: Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param sqs_batch: SQS Batch size when catchup up on queued documents (max 10, which is also the default).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0419356c8968d9e5fe6e85d2ace136c9a4c171988fdb514af58a850a8503ad6c)
            check_type(argname="argument state_machine_arn", value=state_machine_arn, expected_type=type_hints["state_machine_arn"])
            check_type(argname="argument document_status_table", value=document_status_table, expected_type=type_hints["document_status_table"])
            check_type(argname="argument event_source", value=event_source, expected_type=type_hints["event_source"])
            check_type(argname="argument executions_concurrency_threshold", value=executions_concurrency_threshold, expected_type=type_hints["executions_concurrency_threshold"])
            check_type(argname="argument executions_counter_table", value=executions_counter_table, expected_type=type_hints["executions_counter_table"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory", value=lambda_memory, expected_type=type_hints["lambda_memory"])
            check_type(argname="argument lambda_queue_worker_log_level", value=lambda_queue_worker_log_level, expected_type=type_hints["lambda_queue_worker_log_level"])
            check_type(argname="argument lambda_queue_worker_memory", value=lambda_queue_worker_memory, expected_type=type_hints["lambda_queue_worker_memory"])
            check_type(argname="argument lambda_queue_worker_timeout", value=lambda_queue_worker_timeout, expected_type=type_hints["lambda_queue_worker_timeout"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument sqs_batch", value=sqs_batch, expected_type=type_hints["sqs_batch"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "state_machine_arn": state_machine_arn,
        }
        if document_status_table is not None:
            self._values["document_status_table"] = document_status_table
        if event_source is not None:
            self._values["event_source"] = event_source
        if executions_concurrency_threshold is not None:
            self._values["executions_concurrency_threshold"] = executions_concurrency_threshold
        if executions_counter_table is not None:
            self._values["executions_counter_table"] = executions_counter_table
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory is not None:
            self._values["lambda_memory"] = lambda_memory
        if lambda_queue_worker_log_level is not None:
            self._values["lambda_queue_worker_log_level"] = lambda_queue_worker_log_level
        if lambda_queue_worker_memory is not None:
            self._values["lambda_queue_worker_memory"] = lambda_queue_worker_memory
        if lambda_queue_worker_timeout is not None:
            self._values["lambda_queue_worker_timeout"] = lambda_queue_worker_timeout
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if sqs_batch is not None:
            self._values["sqs_batch"] = sqs_batch

    @builtins.property
    def state_machine_arn(self) -> builtins.str:
        '''State Machine ARN.'''
        result = self._values.get("state_machine_arn")
        assert result is not None, "Required property 'state_machine_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def document_status_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        '''Status table - DynamoDB table with status information for the document execution.'''
        result = self._values.get("document_status_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], result)

    @builtins.property
    def event_source(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.IEventSource]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("event_source")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.IEventSource]], result)

    @builtins.property
    def executions_concurrency_threshold(self) -> typing.Optional[jsii.Number]:
        '''Executions concurrency, default is 100 should be set to whatever the bottleneck of the workflow is For Textract Asynchronous APIs, that would be the number of concurrent jobs that can be processed For Textract Synchronous APIs, that would be the TPS for the API.'''
        result = self._values.get("executions_concurrency_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def executions_counter_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        '''Step Functions Executions Counter - DynamoDB table with current count of executions.'''
        result = self._values.get("executions_counter_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        '''log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.

        :default: = INFO
        '''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory(self) -> typing.Optional[jsii.Number]:
        '''Memory allocated to Lambda function, default 512.'''
        result = self._values.get("lambda_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_queue_worker_log_level(self) -> typing.Optional[builtins.str]:
        '''log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.

        :default: = DEBUG
        '''
        result = self._values.get("lambda_queue_worker_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_queue_worker_memory(self) -> typing.Optional[jsii.Number]:
        '''Memory allocated to Lambda function, default 512.'''
        result = self._values.get("lambda_queue_worker_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_queue_worker_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda Function Timeout in seconds, default 300.'''
        result = self._values.get("lambda_queue_worker_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda Function Timeout in seconds, default 300.'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        '''Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].'''
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.'''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs_batch(self) -> typing.Optional[jsii.Number]:
        '''SQS Batch size when catchup up on queued documents (max 10, which is also the default).'''
        result = self._values.get("sqs_batch")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SFExecutionsStartThrottleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SearchablePDF(
    _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineFragment,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.SearchablePDF",
):
    '''This construct takes in a JSON with two s3 Paths, s3TextractOutput, s3PDFBucket.

    example s3Path:
    {"s3TextractOutput": "s3://bucketname/prefix/1"}
    {"s3PDFBucket": "s3://bucketname/prefix/document.pdf"::
    '''

    def __init__(
        self,
        parent: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        s3_pdf_bucket: typing.Optional[builtins.str] = None,
        s3_textract_output_bucket: typing.Optional[builtins.str] = None,
        searchable_pdf_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: Descriptive identifier for this chainable.
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param s3_input_prefix: prefix for the incoming document. Will be used to create role
        :param s3_pdf_bucket: 
        :param s3_textract_output_bucket: 
        :param searchable_pdf_function: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bee1af2a47305e4c9ebfebed25bdaac56fb710fc8a1b14681164986c9f8ca72)
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SearchablePDFProps(
            input_policy_statements=input_policy_statements,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
            s3_input_prefix=s3_input_prefix,
            s3_pdf_bucket=s3_pdf_bucket,
            s3_textract_output_bucket=s3_textract_output_bucket,
            searchable_pdf_function=searchable_pdf_function,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="searchablePDFFunction")
    def searchable_pdf_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "searchablePDFFunction"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.State:
        '''The start state of this state machine fragment.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.State, jsii.get(self, "startState"))


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.SearchablePDFProps",
    jsii_struct_bases=[],
    name_mapping={
        "input_policy_statements": "inputPolicyStatements",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
        "s3_input_prefix": "s3InputPrefix",
        "s3_pdf_bucket": "s3PDFBucket",
        "s3_textract_output_bucket": "s3TextractOutputBucket",
        "searchable_pdf_function": "searchablePDFFunction",
    },
)
class SearchablePDFProps:
    def __init__(
        self,
        *,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        s3_pdf_bucket: typing.Optional[builtins.str] = None,
        s3_textract_output_bucket: typing.Optional[builtins.str] = None,
        searchable_pdf_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    ) -> None:
        '''
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param s3_input_prefix: prefix for the incoming document. Will be used to create role
        :param s3_pdf_bucket: 
        :param s3_textract_output_bucket: 
        :param searchable_pdf_function: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ae7a44b85c05636dbf0a4aa69c117d4b60d7a954fffcb44dd0fbe1731cf57f2)
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument s3_pdf_bucket", value=s3_pdf_bucket, expected_type=type_hints["s3_pdf_bucket"])
            check_type(argname="argument s3_textract_output_bucket", value=s3_textract_output_bucket, expected_type=type_hints["s3_textract_output_bucket"])
            check_type(argname="argument searchable_pdf_function", value=searchable_pdf_function, expected_type=type_hints["searchable_pdf_function"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if s3_pdf_bucket is not None:
            self._values["s3_pdf_bucket"] = s3_pdf_bucket
        if s3_textract_output_bucket is not None:
            self._values["s3_textract_output_bucket"] = s3_textract_output_bucket
        if searchable_pdf_function is not None:
            self._values["searchable_pdf_function"] = searchable_pdf_function

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for the incoming document.

        Will be used to create role
        '''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_pdf_bucket(self) -> typing.Optional[builtins.str]:
        result = self._values.get("s3_pdf_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_textract_output_bucket(self) -> typing.Optional[builtins.str]:
        result = self._values.get("s3_textract_output_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def searchable_pdf_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        result = self._values.get("searchable_pdf_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SearchablePDFProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SpacySfnTask(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.SpacySfnTask",
):
    '''Deploys a Lambda Container with a Spacy NLP model to call textcat.

    Input: "textract_result"."txt_output_location"
    Output:  { "documentType": "AWS_PAYSTUBS" } (example will be at "classification"."documentType")

    Example (Python::

        spacy_classification_task = tcdk.SpacySfnTask(
            self,
            "Classification",
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            lambda_log_level="DEBUG",
            timeout=Duration.hours(24),
            input=sfn.TaskInput.from_object({
                "Token":
                sfn.JsonPath.task_token,
                "ExecutionId":
                sfn.JsonPath.string_at('$$.Execution.Id'),
                "Payload":
                sfn.JsonPath.entire_payload,
            }),
            result_path="$.classification")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        docker_image_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        spacy_image_ecr_repository: typing.Optional[builtins.str] = None,
        spacy_lambda_memory_size: typing.Optional[jsii.Number] = None,
        spacy_lambda_timeout: typing.Optional[jsii.Number] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: Descriptive identifier for this chainable.
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param docker_image_function: Docker Container (to use in DockerImageCode.from_ecr() call).
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param spacy_image_ecr_repository: ECR Container URI for Spacy classification.
        :param spacy_lambda_memory_size: memorySize for Lambda function calling Spacy NLP, default is 4096 MB.
        :param spacy_lambda_timeout: timeout for Lambda function calling Spacy NLP, default is 900 seconds.
        :param textract_state_machine_timeout_minutes: how long can we wait for the process (default is 48 hours (60*48=2880)).
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e5b2dacdc4ccbbe289c86d0b2e0642e892f6433b39ce58a6fe48e2acbfb4a8e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SpacySfnTaskProps(
            associate_with_parent=associate_with_parent,
            docker_image_function=docker_image_function,
            input=input,
            lambda_log_level=lambda_log_level,
            name=name,
            spacy_image_ecr_repository=spacy_image_ecr_repository,
            spacy_lambda_memory_size=spacy_lambda_memory_size,
            spacy_lambda_timeout=spacy_lambda_timeout,
            textract_state_machine_timeout_minutes=textract_state_machine_timeout_minutes,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig]:
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "taskPolicies"))

    @builtins.property
    @jsii.member(jsii_name="spacyCallFunction")
    def spacy_call_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "spacyCallFunction"))

    @spacy_call_function.setter
    def spacy_call_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__694ee94304833a6e79e0bca7303386b8e4b72111e85d28fb732057fccdc02f5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spacyCallFunction", value)

    @builtins.property
    @jsii.member(jsii_name="spacySyncLambdaLogGroup")
    def spacy_sync_lambda_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "spacySyncLambdaLogGroup"))

    @spacy_sync_lambda_log_group.setter
    def spacy_sync_lambda_log_group(
        self,
        value: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__486073f1dec452daea44ef35232ecb1bdf7e6e23a70a2336ba8c26cad08bf1f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spacySyncLambdaLogGroup", value)

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f6940a72f68db11a722462d4039aae3cc0d0c73a3bdc0512708985818b03db6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79fefaf82c5d3331c016b89cabf1b700e769e8cb4f83b41120b7f5339726ad97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.SpacySfnTaskProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "associate_with_parent": "associateWithParent",
        "docker_image_function": "dockerImageFunction",
        "input": "input",
        "lambda_log_level": "lambdaLogLevel",
        "name": "name",
        "spacy_image_ecr_repository": "spacyImageEcrRepository",
        "spacy_lambda_memory_size": "spacyLambdaMemorySize",
        "spacy_lambda_timeout": "spacyLambdaTimeout",
        "textract_state_machine_timeout_minutes": "textractStateMachineTimeoutMinutes",
    },
)
class SpacySfnTaskProps(_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        docker_image_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        spacy_image_ecr_repository: typing.Optional[builtins.str] = None,
        spacy_lambda_memory_size: typing.Optional[jsii.Number] = None,
        spacy_lambda_timeout: typing.Optional[jsii.Number] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param docker_image_function: Docker Container (to use in DockerImageCode.from_ecr() call).
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param spacy_image_ecr_repository: ECR Container URI for Spacy classification.
        :param spacy_lambda_memory_size: memorySize for Lambda function calling Spacy NLP, default is 4096 MB.
        :param spacy_lambda_timeout: timeout for Lambda function calling Spacy NLP, default is 900 seconds.
        :param textract_state_machine_timeout_minutes: how long can we wait for the process (default is 48 hours (60*48=2880)).
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cba57b66cbd6ce930f6c12b56fbeabe9ee122bff2d8ff1e1dd3cf8b2690b030)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument associate_with_parent", value=associate_with_parent, expected_type=type_hints["associate_with_parent"])
            check_type(argname="argument docker_image_function", value=docker_image_function, expected_type=type_hints["docker_image_function"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument spacy_image_ecr_repository", value=spacy_image_ecr_repository, expected_type=type_hints["spacy_image_ecr_repository"])
            check_type(argname="argument spacy_lambda_memory_size", value=spacy_lambda_memory_size, expected_type=type_hints["spacy_lambda_memory_size"])
            check_type(argname="argument spacy_lambda_timeout", value=spacy_lambda_timeout, expected_type=type_hints["spacy_lambda_timeout"])
            check_type(argname="argument textract_state_machine_timeout_minutes", value=textract_state_machine_timeout_minutes, expected_type=type_hints["textract_state_machine_timeout_minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if associate_with_parent is not None:
            self._values["associate_with_parent"] = associate_with_parent
        if docker_image_function is not None:
            self._values["docker_image_function"] = docker_image_function
        if input is not None:
            self._values["input"] = input
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if name is not None:
            self._values["name"] = name
        if spacy_image_ecr_repository is not None:
            self._values["spacy_image_ecr_repository"] = spacy_image_ecr_repository
        if spacy_lambda_memory_size is not None:
            self._values["spacy_lambda_memory_size"] = spacy_lambda_memory_size
        if spacy_lambda_timeout is not None:
            self._values["spacy_lambda_timeout"] = spacy_lambda_timeout
        if textract_state_machine_timeout_minutes is not None:
            self._values["textract_state_machine_timeout_minutes"] = textract_state_machine_timeout_minutes

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def associate_with_parent(self) -> typing.Optional[builtins.bool]:
        '''Pass the execution ID from the context object to the execution input.

        This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines.

        If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely.

        :default: - false

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-nested-workflows.html#nested-execution-startid
        '''
        result = self._values.get("associate_with_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docker_image_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''Docker Container (to use in DockerImageCode.from_ecr() call).'''
        result = self._values.get("docker_image_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], result)

    @builtins.property
    def input(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput]:
        '''The JSON input for the execution, same as that of StartExecution.

        :default: - The state input (JSON path '$')

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        '''log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.'''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the execution, same as that of StartExecution.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spacy_image_ecr_repository(self) -> typing.Optional[builtins.str]:
        '''ECR Container URI for Spacy classification.'''
        result = self._values.get("spacy_image_ecr_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spacy_lambda_memory_size(self) -> typing.Optional[jsii.Number]:
        '''memorySize for Lambda function calling Spacy NLP, default is 4096 MB.'''
        result = self._values.get("spacy_lambda_memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def spacy_lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''timeout for Lambda function calling Spacy NLP, default is 900 seconds.'''
        result = self._values.get("spacy_lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_state_machine_timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''how long can we wait for the process (default is 48 hours (60*48=2880)).'''
        result = self._values.get("textract_state_machine_timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpacySfnTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractA2ISfnTask(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractA2ISfnTask",
):
    '''Calls and A2I endpoint arn with a task_token and waits for the A2I job to finish in order to continue the workflow.

    Basic implementation

    Input: "Payload"."a2iInputPath"
    Output::

       {
            'humanLoopStatus': human_loop_status,
            'humanLoopResultPath': human_loop_result,
            'humanLoopCreationTime': human_loop_creation_time,
        }

    Example::

       textract_a2i_task = tcdk.TextractA2ISfnTask(
            self,
            "TextractA2I",
            a2i_flow_definition_arn=
            "arn:aws:sagemaker:us-east-1:913165245630:flow-definition/textract-classifiction",
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            lambda_log_level="DEBUG",
            timeout=Duration.hours(24),
            input=sfn.TaskInput.from_object({
                "Token":
                sfn.JsonPath.task_token,
                "ExecutionId":
                sfn.JsonPath.string_at('$$.Execution.Id'),
                "Payload":
                sfn.JsonPath.entire_payload,
            }),
            result_path="$.a2i_result")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        a2i_flow_definition_arn: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        task_token_table_name: typing.Optional[builtins.str] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: Descriptive identifier for this chainable.
        :param a2i_flow_definition_arn: 
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param lambda_log_level: 
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param task_token_table_name: 
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b619aa6ebc30523ed1a4ede0dfa4561c736eb234c6188bc16548c755316455d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractA2ISfnTaskProps(
            a2i_flow_definition_arn=a2i_flow_definition_arn,
            associate_with_parent=associate_with_parent,
            input=input,
            lambda_log_level=lambda_log_level,
            name=name,
            task_token_table_name=task_token_table_name,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig]:
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "taskPolicies"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa58e1037670bf6f865151ae14fde4c506c8ccf219add886163ff1fd4c71a464)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)

    @builtins.property
    @jsii.member(jsii_name="taskTokenTableName")
    def task_token_table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskTokenTableName"))

    @task_token_table_name.setter
    def task_token_table_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f20e147bf1435d6fec1136f1d29571486028bb565306d3a7fa0cfa3ad0dc019)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskTokenTableName", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95c2ce188159df7952fbe555a47ef65ca727b36556032e46955433afe4d997bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractA2ISfnTaskProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "a2i_flow_definition_arn": "a2iFlowDefinitionARN",
        "associate_with_parent": "associateWithParent",
        "input": "input",
        "lambda_log_level": "lambdaLogLevel",
        "name": "name",
        "task_token_table_name": "taskTokenTableName",
    },
)
class TextractA2ISfnTaskProps(_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        a2i_flow_definition_arn: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        task_token_table_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param a2i_flow_definition_arn: 
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param lambda_log_level: 
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param task_token_table_name: 
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c11975a42fb4b6f10d693ecf8270e21a942db5cb5a69941787b5d4eb22ca9d44)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument a2i_flow_definition_arn", value=a2i_flow_definition_arn, expected_type=type_hints["a2i_flow_definition_arn"])
            check_type(argname="argument associate_with_parent", value=associate_with_parent, expected_type=type_hints["associate_with_parent"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument task_token_table_name", value=task_token_table_name, expected_type=type_hints["task_token_table_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "a2i_flow_definition_arn": a2i_flow_definition_arn,
        }
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if associate_with_parent is not None:
            self._values["associate_with_parent"] = associate_with_parent
        if input is not None:
            self._values["input"] = input
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if name is not None:
            self._values["name"] = name
        if task_token_table_name is not None:
            self._values["task_token_table_name"] = task_token_table_name

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def a2i_flow_definition_arn(self) -> builtins.str:
        result = self._values.get("a2i_flow_definition_arn")
        assert result is not None, "Required property 'a2i_flow_definition_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associate_with_parent(self) -> typing.Optional[builtins.bool]:
        '''Pass the execution ID from the context object to the execution input.

        This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines.

        If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely.

        :default: - false

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-nested-workflows.html#nested-execution-startid
        '''
        result = self._values.get("associate_with_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def input(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput]:
        '''The JSON input for the execution, same as that of StartExecution.

        :default: - The state input (JSON path '$')

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the execution, same as that of StartExecution.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_token_table_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("task_token_table_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractA2ISfnTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractAsyncToJSON(
    _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineFragment,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractAsyncToJSON",
):
    '''combines the potentially paginated response from async Textract calls and stores as one combines JSON.

    This construct is not memory optimzed (yet) and will combine all JSON by loading them to memory.
    Large responses could exceed the memory potentially, the memory size is set to Lambda max.

    Reduce the memory size to your needs if your processing does not yield large responses to save Lamda cost.

    Input: "textract_result"."TextractTempOutputJsonPath"
    Output: "TextractOutputJsonPath"

    Example (Python::

        textract_async_to_json = tcdk.TextractAsyncToJSON(
            self,
            "TextractAsyncToJSON2",
            s3_output_prefix=s3_output_prefix,
            s3_output_bucket=s3_output_bucket)
    '''

    def __init__(
        self,
        parent: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_async_to_json_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_async_to_json_interval: typing.Optional[jsii.Number] = None,
        textract_async_to_json_max_retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: Descriptive identifier for this chainable.
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_output_prefix: The prefix to use for the output files.
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents), set to 10240 (max) atm, decrease for smaller workloads.
        :param lambda_timeout: memory of Lambda function (may need to increase for larger documents).
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: 
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param textract_api: Which Textract API was used to create the OutputConfig? GENERIC and LENDING are supported. Default: - GENERIC
        :param textract_async_to_json_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_async_to_json_interval: 
        :param textract_async_to_json_max_retries: number of retries in Step Function flow. Default: is 100
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ca9c772465c2593ed244c3a9755826188394e55f282b0e1d0ea6cea4a252570)
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractAsyncToJSONProps(
            s3_output_bucket=s3_output_bucket,
            s3_output_prefix=s3_output_prefix,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
            output_policy_statements=output_policy_statements,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            textract_api=textract_api,
            textract_async_to_json_backoff_rate=textract_async_to_json_backoff_rate,
            textract_async_to_json_interval=textract_async_to_json_interval,
            textract_async_to_json_max_retries=textract_async_to_json_max_retries,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property
    @jsii.member(jsii_name="asyncToJSONFunction")
    def async_to_json_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "asyncToJSONFunction"))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.State:
        '''The start state of this state machine fragment.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.State, jsii.get(self, "startState"))


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractAsyncToJSONProps",
    jsii_struct_bases=[],
    name_mapping={
        "s3_output_bucket": "s3OutputBucket",
        "s3_output_prefix": "s3OutputPrefix",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
        "output_policy_statements": "outputPolicyStatements",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "textract_api": "textractAPI",
        "textract_async_to_json_backoff_rate": "textractAsyncToJSONBackoffRate",
        "textract_async_to_json_interval": "textractAsyncToJSONInterval",
        "textract_async_to_json_max_retries": "textractAsyncToJSONMaxRetries",
    },
)
class TextractAsyncToJSONProps:
    def __init__(
        self,
        *,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_async_to_json_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_async_to_json_interval: typing.Optional[jsii.Number] = None,
        textract_async_to_json_max_retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_output_prefix: The prefix to use for the output files.
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents), set to 10240 (max) atm, decrease for smaller workloads.
        :param lambda_timeout: memory of Lambda function (may need to increase for larger documents).
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: 
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param textract_api: Which Textract API was used to create the OutputConfig? GENERIC and LENDING are supported. Default: - GENERIC
        :param textract_async_to_json_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_async_to_json_interval: 
        :param textract_async_to_json_max_retries: number of retries in Step Function flow. Default: is 100
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a96e92b6b9d91c2e42618fd44ea1b0a731077a9db0fe8c4b847bf04d39dbe894)
            check_type(argname="argument s3_output_bucket", value=s3_output_bucket, expected_type=type_hints["s3_output_bucket"])
            check_type(argname="argument s3_output_prefix", value=s3_output_prefix, expected_type=type_hints["s3_output_prefix"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument output_policy_statements", value=output_policy_statements, expected_type=type_hints["output_policy_statements"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument textract_api", value=textract_api, expected_type=type_hints["textract_api"])
            check_type(argname="argument textract_async_to_json_backoff_rate", value=textract_async_to_json_backoff_rate, expected_type=type_hints["textract_async_to_json_backoff_rate"])
            check_type(argname="argument textract_async_to_json_interval", value=textract_async_to_json_interval, expected_type=type_hints["textract_async_to_json_interval"])
            check_type(argname="argument textract_async_to_json_max_retries", value=textract_async_to_json_max_retries, expected_type=type_hints["textract_async_to_json_max_retries"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_output_bucket": s3_output_bucket,
            "s3_output_prefix": s3_output_prefix,
        }
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if output_policy_statements is not None:
            self._values["output_policy_statements"] = output_policy_statements
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if textract_api is not None:
            self._values["textract_api"] = textract_api
        if textract_async_to_json_backoff_rate is not None:
            self._values["textract_async_to_json_backoff_rate"] = textract_async_to_json_backoff_rate
        if textract_async_to_json_interval is not None:
            self._values["textract_async_to_json_interval"] = textract_async_to_json_interval
        if textract_async_to_json_max_retries is not None:
            self._values["textract_async_to_json_max_retries"] = textract_async_to_json_max_retries

    @builtins.property
    def s3_output_bucket(self) -> builtins.str:
        '''Bucketname to output data to.'''
        result = self._values.get("s3_output_bucket")
        assert result is not None, "Required property 's3_output_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_output_prefix(self) -> builtins.str:
        '''The prefix to use for the output files.'''
        result = self._values.get("s3_output_prefix")
        assert result is not None, "Required property 's3_output_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        '''log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.'''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents), set to 10240 (max) atm, decrease for smaller workloads.'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents).'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def output_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("output_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.'''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_api(self) -> typing.Optional[builtins.str]:
        '''Which Textract API was used to create the OutputConfig?

        GENERIC and LENDING are supported.

        :default: - GENERIC
        '''
        result = self._values.get("textract_api")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_async_to_json_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''retyr backoff rate.

        :default: is 1.1
        '''
        result = self._values.get("textract_async_to_json_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_async_to_json_interval(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("textract_async_to_json_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_async_to_json_max_retries(self) -> typing.Optional[jsii.Number]:
        '''number of retries in Step Function flow.

        :default: is 100
        '''
        result = self._values.get("textract_async_to_json_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractAsyncToJSONProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractClassificationConfigurator(
    _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineFragment,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractClassificationConfigurator",
):
    '''Looks for a matching DOCYMENT_TYPE in the configurationTableName and sets the CONFIG value (when found) to the context, so subsequent calls to Textract use those values.

    This is an entry from the default config
    AWS_PAYSTUBS,"{""queriesConfig"": [{""alias"": ""PAYSTUB_PERIOD_START_DATE"", ""text"": ""What is the Pay Period Start Date?""}, {""alias"": ""PAYSTUB_PERIOD_END_DATE"", ""text"": ""What is the Pay Period End Date?""}, {""alias"": ""PAYSTUB_PERIOD_PAY_DATE"", ""text"": ""What is the Pay Date?""}, {""alias"": ""PAYSTUB_PERIOD_EMPLOYEE_NAME"", ""text"": ""What is the Employee Name?""}, {""alias"": ""PAYSTUB_PERIOD_COMPANY_NAME"", ""text"": ""What is the company Name?""}, {""alias"": ""PAYSTUB_PERIOD_CURRENT_GROSS_PAY"", ""text"": ""What is the Current Gross Pay?""}, {""alias"": ""PAYSTUB_PERIOD_YTD_GROSS_PAY"", ""text"": ""What is the YTD Gross Pay?""}, {""alias"": ""PAYSTUB_PERIOD_REGULAR_HOURLY_RATE"", ""text"": ""What is the regular hourly rate?""}, {""alias"": ""PAYSTUB_PERIOD_HOLIDAY_RATE"", ""text"": ""What is the holiday rate?""}], ""textractFeatures"": [""QUERIES""]}"

    So, if the "classification"."documentType" in the Step Function Input is AWS_PAYSTUBS
    then it will set the queriesConfig in the manifest for the subsequent Textract Calls in the Step Function flow

    Input: "classification"."documentType"
    Output: config set to manifest

    Example (Python::

        configurator_task = tcdk.TextractClassificationConfigurator(
            self, f"{workflow_name}-Configurator",
        )
    '''

    def __init__(
        self,
        parent: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        configuration_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: Descriptive identifier for this chainable.
        :param configuration_table: 
        :param lambda_log_level: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25e3098f5f1cf53a1843a288e473d473e85d772bf36df6560bffd0f7ca9d1528)
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractClassificationConfiguratorProps(
            configuration_table=configuration_table,
            lambda_log_level=lambda_log_level,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.State:
        '''The start state of this state machine fragment.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.State, jsii.get(self, "startState"))

    @builtins.property
    @jsii.member(jsii_name="configurationTable")
    def configuration_table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, jsii.get(self, "configurationTable"))

    @configuration_table.setter
    def configuration_table(self, value: _aws_cdk_aws_dynamodb_ceddda9d.ITable) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14bb9f79ce4a3987ca802dd759cf4ce888e01e2282bd21bfb687c194eec36f7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configurationTable", value)

    @builtins.property
    @jsii.member(jsii_name="configurationTableName")
    def configuration_table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationTableName"))

    @configuration_table_name.setter
    def configuration_table_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc36ab1233aeb7ad48805b89b5a7969522727c77067e66de6339fc76f860d2d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configurationTableName", value)

    @builtins.property
    @jsii.member(jsii_name="configuratorFunction")
    def configurator_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "configuratorFunction"))

    @configurator_function.setter
    def configurator_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48258c75c526b12e23a7d55d57df1574bfca1d4360d960d366340dff2ffc7907)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configuratorFunction", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractClassificationConfiguratorProps",
    jsii_struct_bases=[],
    name_mapping={
        "configuration_table": "configurationTable",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
    },
)
class TextractClassificationConfiguratorProps:
    def __init__(
        self,
        *,
        configuration_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param configuration_table: 
        :param lambda_log_level: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9730bcbe8d0810f0bc796cfc253d01edd04d3221100a5d22f84b45392f047fd)
            check_type(argname="argument configuration_table", value=configuration_table, expected_type=type_hints["configuration_table"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if configuration_table is not None:
            self._values["configuration_table"] = configuration_table
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout

    @builtins.property
    def configuration_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        result = self._values.get("configuration_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractClassificationConfiguratorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractDPPOCDeciderProps",
    jsii_struct_bases=[],
    name_mapping={
        "decider_function": "deciderFunction",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "textract_decider_backoff_rate": "textractDeciderBackoffRate",
        "textract_decider_interval": "textractDeciderInterval",
        "textract_decider_max_retries": "textractDeciderMaxRetries",
    },
)
class TextractDPPOCDeciderProps:
    def __init__(
        self,
        *,
        decider_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_decider_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_decider_interval: typing.Optional[jsii.Number] = None,
        textract_decider_max_retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param decider_function: 
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = DEBUG
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param s3_input_bucket: 
        :param s3_input_prefix: prefix for the incoming document. Will be used to create role
        :param textract_decider_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_decider_interval: 
        :param textract_decider_max_retries: number of retries in Step Function flow. Default: is 100
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fde0d8094bf4d559fa73876939c7216338ab9dc4ae355b97c25febd9cefec07)
            check_type(argname="argument decider_function", value=decider_function, expected_type=type_hints["decider_function"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument textract_decider_backoff_rate", value=textract_decider_backoff_rate, expected_type=type_hints["textract_decider_backoff_rate"])
            check_type(argname="argument textract_decider_interval", value=textract_decider_interval, expected_type=type_hints["textract_decider_interval"])
            check_type(argname="argument textract_decider_max_retries", value=textract_decider_max_retries, expected_type=type_hints["textract_decider_max_retries"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if decider_function is not None:
            self._values["decider_function"] = decider_function
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if textract_decider_backoff_rate is not None:
            self._values["textract_decider_backoff_rate"] = textract_decider_backoff_rate
        if textract_decider_interval is not None:
            self._values["textract_decider_interval"] = textract_decider_interval
        if textract_decider_max_retries is not None:
            self._values["textract_decider_max_retries"] = textract_decider_max_retries

    @builtins.property
    def decider_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        result = self._values.get("decider_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        '''log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.

        :default: = DEBUG
        '''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for the incoming document.

        Will be used to create role
        '''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_decider_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''retyr backoff rate.

        :default: is 1.1
        '''
        result = self._values.get("textract_decider_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_decider_interval(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("textract_decider_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_decider_max_retries(self) -> typing.Optional[jsii.Number]:
        '''number of retries in Step Function flow.

        :default: is 100
        '''
        result = self._values.get("textract_decider_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractDPPOCDeciderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractGenerateCSV(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractGenerateCSV",
):
    '''Generates a output based on Textract Forms and Queries. Supported output_types: "LINES" | "CSV".

    Input: "Payload"."textract_result"."TextractOutputJsonPath"
    Output: "TextractOutputCSVPath" TODO: rename

    Output as LINES
    Example (Python::

               generate_text = tcdk.TextractGenerateCSV(
                self,
                "GenerateText",
                csv_s3_output_bucket=document_bucket.bucket_name,
                csv_s3_output_prefix=s3_txt_output_prefix,
                output_type='LINES',
                lambda_log_level="DEBUG",
                integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
                input=sfn.TaskInput.from_object({
                    "Token":
                    sfn.JsonPath.task_token,
                    "ExecutionId":
                    sfn.JsonPath.string_at('$$.Execution.Id'),
                    "Payload":
                    sfn.JsonPath.entire_payload,
                }),
                result_path="$.txt_output_location")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        csv_s3_output_bucket: builtins.str,
        csv_s3_output_prefix: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        meta_data_to_append: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        opensearch_index_name: typing.Optional[builtins.str] = None,
        output_features: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        output_type: typing.Optional[builtins.str] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_generate_csv_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_generate_csv_interval: typing.Optional[jsii.Number] = None,
        textract_generate_csv_max_retries: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: Descriptive identifier for this chainable.
        :param csv_s3_output_bucket: 
        :param csv_s3_output_prefix: 
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param meta_data_to_append: The generated CSV can have any meta-data from the manifest file included. This is a list of all meta-data names to include If they are missed they will be "" MetaData keys have to be without ','
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param opensearch_index_name: 
        :param output_features: supports FORMS, TABLES, QUERIES, SIGNATURES as a comma seperated string and generates CSV files for the output from those default is "FORMS,TABLES,QUERIES,SIGNATURES".
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param output_type: 
        :param s3_input_bucket: Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param textract_api: 
        :param textract_generate_csv_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_generate_csv_interval: 
        :param textract_generate_csv_max_retries: number of retries in Step Function flow. Default: is 100
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c4862082059a8d5b6466d4d265f04eb4cba355498d58e92495f8fa815a1e1c0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractGenerateCSVProps(
            csv_s3_output_bucket=csv_s3_output_bucket,
            csv_s3_output_prefix=csv_s3_output_prefix,
            associate_with_parent=associate_with_parent,
            input=input,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
            meta_data_to_append=meta_data_to_append,
            name=name,
            opensearch_index_name=opensearch_index_name,
            output_features=output_features,
            output_policy_statements=output_policy_statements,
            output_type=output_type,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            textract_api=textract_api,
            textract_generate_csv_backoff_rate=textract_generate_csv_backoff_rate,
            textract_generate_csv_interval=textract_generate_csv_interval,
            textract_generate_csv_max_retries=textract_generate_csv_max_retries,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="generateCSVLambda")
    def generate_csv_lambda(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "generateCSVLambda"))

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig]:
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "taskPolicies"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a88a2676af3df102bdf86aca83a7162535d7aa9e7ece1b68f9ac7152fedfc6a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractGenerateCSVProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "csv_s3_output_bucket": "csvS3OutputBucket",
        "csv_s3_output_prefix": "csvS3OutputPrefix",
        "associate_with_parent": "associateWithParent",
        "input": "input",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
        "meta_data_to_append": "metaDataToAppend",
        "name": "name",
        "opensearch_index_name": "opensearchIndexName",
        "output_features": "outputFeatures",
        "output_policy_statements": "outputPolicyStatements",
        "output_type": "outputType",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "textract_api": "textractAPI",
        "textract_generate_csv_backoff_rate": "textractGenerateCSVBackoffRate",
        "textract_generate_csv_interval": "textractGenerateCSVInterval",
        "textract_generate_csv_max_retries": "textractGenerateCSVMaxRetries",
    },
)
class TextractGenerateCSVProps(_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        csv_s3_output_bucket: builtins.str,
        csv_s3_output_prefix: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        meta_data_to_append: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        opensearch_index_name: typing.Optional[builtins.str] = None,
        output_features: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        output_type: typing.Optional[builtins.str] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_generate_csv_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_generate_csv_interval: typing.Optional[jsii.Number] = None,
        textract_generate_csv_max_retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param csv_s3_output_bucket: 
        :param csv_s3_output_prefix: 
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param meta_data_to_append: The generated CSV can have any meta-data from the manifest file included. This is a list of all meta-data names to include If they are missed they will be "" MetaData keys have to be without ','
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param opensearch_index_name: 
        :param output_features: supports FORMS, TABLES, QUERIES, SIGNATURES as a comma seperated string and generates CSV files for the output from those default is "FORMS,TABLES,QUERIES,SIGNATURES".
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param output_type: 
        :param s3_input_bucket: Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param textract_api: 
        :param textract_generate_csv_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_generate_csv_interval: 
        :param textract_generate_csv_max_retries: number of retries in Step Function flow. Default: is 100
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724c205c78f00a297bd85ee70d9f29988a55704db03e156b18a7a13ce1ecc72c)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument csv_s3_output_bucket", value=csv_s3_output_bucket, expected_type=type_hints["csv_s3_output_bucket"])
            check_type(argname="argument csv_s3_output_prefix", value=csv_s3_output_prefix, expected_type=type_hints["csv_s3_output_prefix"])
            check_type(argname="argument associate_with_parent", value=associate_with_parent, expected_type=type_hints["associate_with_parent"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument meta_data_to_append", value=meta_data_to_append, expected_type=type_hints["meta_data_to_append"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument opensearch_index_name", value=opensearch_index_name, expected_type=type_hints["opensearch_index_name"])
            check_type(argname="argument output_features", value=output_features, expected_type=type_hints["output_features"])
            check_type(argname="argument output_policy_statements", value=output_policy_statements, expected_type=type_hints["output_policy_statements"])
            check_type(argname="argument output_type", value=output_type, expected_type=type_hints["output_type"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument textract_api", value=textract_api, expected_type=type_hints["textract_api"])
            check_type(argname="argument textract_generate_csv_backoff_rate", value=textract_generate_csv_backoff_rate, expected_type=type_hints["textract_generate_csv_backoff_rate"])
            check_type(argname="argument textract_generate_csv_interval", value=textract_generate_csv_interval, expected_type=type_hints["textract_generate_csv_interval"])
            check_type(argname="argument textract_generate_csv_max_retries", value=textract_generate_csv_max_retries, expected_type=type_hints["textract_generate_csv_max_retries"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "csv_s3_output_bucket": csv_s3_output_bucket,
            "csv_s3_output_prefix": csv_s3_output_prefix,
        }
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if associate_with_parent is not None:
            self._values["associate_with_parent"] = associate_with_parent
        if input is not None:
            self._values["input"] = input
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if meta_data_to_append is not None:
            self._values["meta_data_to_append"] = meta_data_to_append
        if name is not None:
            self._values["name"] = name
        if opensearch_index_name is not None:
            self._values["opensearch_index_name"] = opensearch_index_name
        if output_features is not None:
            self._values["output_features"] = output_features
        if output_policy_statements is not None:
            self._values["output_policy_statements"] = output_policy_statements
        if output_type is not None:
            self._values["output_type"] = output_type
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if textract_api is not None:
            self._values["textract_api"] = textract_api
        if textract_generate_csv_backoff_rate is not None:
            self._values["textract_generate_csv_backoff_rate"] = textract_generate_csv_backoff_rate
        if textract_generate_csv_interval is not None:
            self._values["textract_generate_csv_interval"] = textract_generate_csv_interval
        if textract_generate_csv_max_retries is not None:
            self._values["textract_generate_csv_max_retries"] = textract_generate_csv_max_retries

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def csv_s3_output_bucket(self) -> builtins.str:
        result = self._values.get("csv_s3_output_bucket")
        assert result is not None, "Required property 'csv_s3_output_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def csv_s3_output_prefix(self) -> builtins.str:
        result = self._values.get("csv_s3_output_prefix")
        assert result is not None, "Required property 'csv_s3_output_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associate_with_parent(self) -> typing.Optional[builtins.bool]:
        '''Pass the execution ID from the context object to the execution input.

        This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines.

        If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely.

        :default: - false

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-nested-workflows.html#nested-execution-startid
        '''
        result = self._values.get("associate_with_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def input(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput]:
        '''The JSON input for the execution, same as that of StartExecution.

        :default: - The state input (JSON path '$')

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput], result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def meta_data_to_append(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The generated CSV can have any meta-data from the manifest file included.

        This is a list of all meta-data names to include
        If they are missed they will be ""
        MetaData keys have to be without ','
        '''
        result = self._values.get("meta_data_to_append")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the execution, same as that of StartExecution.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def opensearch_index_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("opensearch_index_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_features(self) -> typing.Optional[builtins.str]:
        '''supports FORMS, TABLES, QUERIES, SIGNATURES as a comma seperated string and generates CSV files for the output from those default is "FORMS,TABLES,QUERIES,SIGNATURES".'''
        result = self._values.get("output_features")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("output_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def output_type(self) -> typing.Optional[builtins.str]:
        result = self._values.get("output_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        '''Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].'''
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.'''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_api(self) -> typing.Optional[builtins.str]:
        result = self._values.get("textract_api")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_generate_csv_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''retyr backoff rate.

        :default: is 1.1
        '''
        result = self._values.get("textract_generate_csv_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_generate_csv_interval(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("textract_generate_csv_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_generate_csv_max_retries(self) -> typing.Optional[jsii.Number]:
        '''number of retries in Step Function flow.

        :default: is 100
        '''
        result = self._values.get("textract_generate_csv_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractGenerateCSVProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractGenericAsyncSfnTask(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractGenericAsyncSfnTask",
):
    '''This Task calls the Textract through the asynchronous API.

    Which API to call is defined in

    When GENERIC is called with features in the manifest definition, will call the AnalzyeDocument API.

    Takes the configuration from "Payload"."manifest"

    Will retry on recoverable errors based on textractAsyncCallMaxRetries
    errors for retry: ['ThrottlingException', 'LimitExceededException', 'InternalServerError', 'ProvisionedThroughputExceededException'],

    Internally calls Start* calls with OutputConfig and SNSNotification.
    Another Lambda functions waits for SNS Notification event and notifies the Step Function flow with the task token.

    Step Function JSON input requirements

    **Input**: "Payload"."manifest"

    **Output**: "TextractTempOutputJsonPath" points to potentially paginated Textract JSON Schema output at "TextractTempOutputJsonPath" (using the example code it will be at: "textract_result"."TextractTempOutputJsonPath")

    Works together with TextractAsyncToJSON, which takes the s3_output_bucket/s3_temp_output_prefix location as input

    Example (Python::

        textract_async_task = tcdk.TextractGenericAsyncSfnTask(
            self,
            "TextractAsync",
            s3_output_bucket=s3_output_bucket,
            s3_temp_output_prefix=s3_temp_output_prefix,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            lambda_log_level="DEBUG",
            timeout=Duration.hours(24),
            input=sfn.TaskInput.from_object({
                "Token":
                sfn.JsonPath.task_token,
                "ExecutionId":
                sfn.JsonPath.string_at('$$.Execution.Id'),
                "Payload":
                sfn.JsonPath.entire_payload,
            }),
            result_path="$.textract_result")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        s3_output_bucket: builtins.str,
        s3_temp_output_prefix: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        sns_role_textract: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        task_token_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_async_call_interval: typing.Optional[jsii.Number] = None,
        textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: Descriptive identifier for this chainable.
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_temp_output_prefix: The prefix to use for the temporary output files (e. g. output from async process before stiching together)
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param enable_cloud_watch_metrics_and_dashboard: 
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = DEBUG
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param sns_role_textract: IAM Role to assign to Textract, by default new iam.Role(this, 'TextractAsyncSNSRole', { assumedBy: new iam.ServicePrincipal('textract.amazonaws.com'), managedPolicies: [ManagedPolicy.fromAwsManagedPolicyName('AmazonSQSFullAccess'), ManagedPolicy.fromAwsManagedPolicyName('AmazonSNSFullAccess'), ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'), ManagedPolicy.fromAwsManagedPolicyName('AmazonTextractFullAccess')], });
        :param task_token_table: task token table to use for mapping of Textract `JobTag <https://docs.aws.amazon.com/textract/latest/dg/API_StartDocumentTextDetection.html#Textract-StartDocumentTextDetection-request-JobTag>`_ to the `TaskToken <https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html>`_.
        :param textract_api: Which Textract API to call ALL asynchronous Textract API calls are supported. Valid values are GENERIC | EXPENSE | LENDING. For GENERIC, when called without features (e. g. FORMS, TABLES, QUERIES, SIGNATURE), StartDetectText is called and only OCR is returned. For GENERIC, when called with a feature (e. g. FORMS, TABLES, QUERIES, SIGNATURE), StartAnalyzeDocument is called. Default: - GENERIC
        :param textract_async_call_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_async_call_interval: time in seconds to wait before next retry. Default: is 1
        :param textract_async_call_max_retries: number of retries in Step Function flow. Default: is 100
        :param textract_state_machine_timeout_minutes: how long can we wait for the process. Default: - 2880 (48 hours (60 min * 48 hours = 2880))
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__777a9f850c82400b30b8e4947eac2c7b86afcc5422d945e75c147efa4878c28e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractGenericAsyncSfnTaskProps(
            s3_output_bucket=s3_output_bucket,
            s3_temp_output_prefix=s3_temp_output_prefix,
            associate_with_parent=associate_with_parent,
            enable_cloud_watch_metrics_and_dashboard=enable_cloud_watch_metrics_and_dashboard,
            input=input,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory=lambda_memory,
            lambda_timeout=lambda_timeout,
            name=name,
            output_policy_statements=output_policy_statements,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            sns_role_textract=sns_role_textract,
            task_token_table=task_token_table,
            textract_api=textract_api,
            textract_async_call_backoff_rate=textract_async_call_backoff_rate,
            textract_async_call_interval=textract_async_call_interval,
            textract_async_call_max_retries=textract_async_call_max_retries,
            textract_state_machine_timeout_minutes=textract_state_machine_timeout_minutes,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig]:
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "taskPolicies"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fdd037482db6dad099fdb4505606fea0c969958d0feece9a69c6eb96796920e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)

    @builtins.property
    @jsii.member(jsii_name="taskTokenTable")
    def task_token_table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, jsii.get(self, "taskTokenTable"))

    @task_token_table.setter
    def task_token_table(self, value: _aws_cdk_aws_dynamodb_ceddda9d.ITable) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd254ba32e5db6444c5a43b8c83cca7782f63802da3e5b0f6824799b49010e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskTokenTable", value)

    @builtins.property
    @jsii.member(jsii_name="taskTokenTableName")
    def task_token_table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskTokenTableName"))

    @task_token_table_name.setter
    def task_token_table_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31e881ad8384afc6bb5da8beed6c0c1b616b6eac541ef8d1e8da53d28c675d93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskTokenTableName", value)

    @builtins.property
    @jsii.member(jsii_name="textractAsyncCallFunction")
    def textract_async_call_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "textractAsyncCallFunction"))

    @textract_async_call_function.setter
    def textract_async_call_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb980df2a3ad4a409aa2e44833e1eeef93d5ca29d42b0e32b7463cebafb3bb61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textractAsyncCallFunction", value)

    @builtins.property
    @jsii.member(jsii_name="textractAsyncReceiveSNSFunction")
    def textract_async_receive_sns_function(
        self,
    ) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "textractAsyncReceiveSNSFunction"))

    @textract_async_receive_sns_function.setter
    def textract_async_receive_sns_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41cb1f9f496a6dba7a042c5ccde0e5a642d141e9be2a1db69458f90db745e9c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textractAsyncReceiveSNSFunction", value)

    @builtins.property
    @jsii.member(jsii_name="textractAsyncSNS")
    def textract_async_sns(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "textractAsyncSNS"))

    @textract_async_sns.setter
    def textract_async_sns(self, value: _aws_cdk_aws_sns_ceddda9d.ITopic) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__487b99befc7ec29928dda710f001ea11e64934a8d8053719a118bf80981fb983)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textractAsyncSNS", value)

    @builtins.property
    @jsii.member(jsii_name="textractAsyncSNSRole")
    def textract_async_sns_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "textractAsyncSNSRole"))

    @textract_async_sns_role.setter
    def textract_async_sns_role(self, value: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a2deb75ba6cf3eec0b097f8e1a52e2f9374c89716f54e4360f581caa0c2d146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textractAsyncSNSRole", value)

    @builtins.property
    @jsii.member(jsii_name="asyncDurationMetric")
    def async_duration_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "asyncDurationMetric"))

    @async_duration_metric.setter
    def async_duration_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33fb9b71b4c990d8b5382a06849fbf30c26f40b0c0955ff9256a001a5955440f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "asyncDurationMetric", value)

    @builtins.property
    @jsii.member(jsii_name="asyncJobFailureMetric")
    def async_job_failure_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "asyncJobFailureMetric"))

    @async_job_failure_metric.setter
    def async_job_failure_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f58ab12489357f5450bbfca9fe4badfee9dba50c0413209829be946d81a555fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "asyncJobFailureMetric", value)

    @builtins.property
    @jsii.member(jsii_name="asyncJobFinshedMetric")
    def async_job_finshed_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "asyncJobFinshedMetric"))

    @async_job_finshed_metric.setter
    def async_job_finshed_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef6a0a91d67a04217b9c2cc84fa1e0ef0a5bdc6eee9944b8440c5dd8ef8c003b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "asyncJobFinshedMetric", value)

    @builtins.property
    @jsii.member(jsii_name="asyncJobStartedMetric")
    def async_job_started_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "asyncJobStartedMetric"))

    @async_job_started_metric.setter
    def async_job_started_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b143769254733f3758938b4f5b564339ad262dc9427348e3a279ace88d90b66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "asyncJobStartedMetric", value)

    @builtins.property
    @jsii.member(jsii_name="asyncNumberPagesMetric")
    def async_number_pages_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "asyncNumberPagesMetric"))

    @async_number_pages_metric.setter
    def async_number_pages_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c16fb3ebb6242918219104d7eaf0d0cd1a95614836e825ce2f92b78295acc52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "asyncNumberPagesMetric", value)

    @builtins.property
    @jsii.member(jsii_name="asyncNumberPagesSendMetric")
    def async_number_pages_send_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "asyncNumberPagesSendMetric"))

    @async_number_pages_send_metric.setter
    def async_number_pages_send_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf0a1ee3eabc4d2e34f6b30eed569fa4d7a25f8fac3e5cc78c5528b8c8b987ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "asyncNumberPagesSendMetric", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractGenericAsyncSfnTaskProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "s3_output_bucket": "s3OutputBucket",
        "s3_temp_output_prefix": "s3TempOutputPrefix",
        "associate_with_parent": "associateWithParent",
        "enable_cloud_watch_metrics_and_dashboard": "enableCloudWatchMetricsAndDashboard",
        "input": "input",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory": "lambdaMemory",
        "lambda_timeout": "lambdaTimeout",
        "name": "name",
        "output_policy_statements": "outputPolicyStatements",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "sns_role_textract": "snsRoleTextract",
        "task_token_table": "taskTokenTable",
        "textract_api": "textractAPI",
        "textract_async_call_backoff_rate": "textractAsyncCallBackoffRate",
        "textract_async_call_interval": "textractAsyncCallInterval",
        "textract_async_call_max_retries": "textractAsyncCallMaxRetries",
        "textract_state_machine_timeout_minutes": "textractStateMachineTimeoutMinutes",
    },
)
class TextractGenericAsyncSfnTaskProps(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps,
):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        s3_output_bucket: builtins.str,
        s3_temp_output_prefix: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        sns_role_textract: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        task_token_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_async_call_interval: typing.Optional[jsii.Number] = None,
        textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param s3_output_bucket: Bucketname to output data to.
        :param s3_temp_output_prefix: The prefix to use for the temporary output files (e. g. output from async process before stiching together)
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param enable_cloud_watch_metrics_and_dashboard: 
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = DEBUG
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.
        :param sns_role_textract: IAM Role to assign to Textract, by default new iam.Role(this, 'TextractAsyncSNSRole', { assumedBy: new iam.ServicePrincipal('textract.amazonaws.com'), managedPolicies: [ManagedPolicy.fromAwsManagedPolicyName('AmazonSQSFullAccess'), ManagedPolicy.fromAwsManagedPolicyName('AmazonSNSFullAccess'), ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'), ManagedPolicy.fromAwsManagedPolicyName('AmazonTextractFullAccess')], });
        :param task_token_table: task token table to use for mapping of Textract `JobTag <https://docs.aws.amazon.com/textract/latest/dg/API_StartDocumentTextDetection.html#Textract-StartDocumentTextDetection-request-JobTag>`_ to the `TaskToken <https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html>`_.
        :param textract_api: Which Textract API to call ALL asynchronous Textract API calls are supported. Valid values are GENERIC | EXPENSE | LENDING. For GENERIC, when called without features (e. g. FORMS, TABLES, QUERIES, SIGNATURE), StartDetectText is called and only OCR is returned. For GENERIC, when called with a feature (e. g. FORMS, TABLES, QUERIES, SIGNATURE), StartAnalyzeDocument is called. Default: - GENERIC
        :param textract_async_call_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_async_call_interval: time in seconds to wait before next retry. Default: is 1
        :param textract_async_call_max_retries: number of retries in Step Function flow. Default: is 100
        :param textract_state_machine_timeout_minutes: how long can we wait for the process. Default: - 2880 (48 hours (60 min * 48 hours = 2880))
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bdfa5466a8208501dedc1e21f41ec52737b86fcaa1624267285219b717903b3)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument s3_output_bucket", value=s3_output_bucket, expected_type=type_hints["s3_output_bucket"])
            check_type(argname="argument s3_temp_output_prefix", value=s3_temp_output_prefix, expected_type=type_hints["s3_temp_output_prefix"])
            check_type(argname="argument associate_with_parent", value=associate_with_parent, expected_type=type_hints["associate_with_parent"])
            check_type(argname="argument enable_cloud_watch_metrics_and_dashboard", value=enable_cloud_watch_metrics_and_dashboard, expected_type=type_hints["enable_cloud_watch_metrics_and_dashboard"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory", value=lambda_memory, expected_type=type_hints["lambda_memory"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument output_policy_statements", value=output_policy_statements, expected_type=type_hints["output_policy_statements"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument sns_role_textract", value=sns_role_textract, expected_type=type_hints["sns_role_textract"])
            check_type(argname="argument task_token_table", value=task_token_table, expected_type=type_hints["task_token_table"])
            check_type(argname="argument textract_api", value=textract_api, expected_type=type_hints["textract_api"])
            check_type(argname="argument textract_async_call_backoff_rate", value=textract_async_call_backoff_rate, expected_type=type_hints["textract_async_call_backoff_rate"])
            check_type(argname="argument textract_async_call_interval", value=textract_async_call_interval, expected_type=type_hints["textract_async_call_interval"])
            check_type(argname="argument textract_async_call_max_retries", value=textract_async_call_max_retries, expected_type=type_hints["textract_async_call_max_retries"])
            check_type(argname="argument textract_state_machine_timeout_minutes", value=textract_state_machine_timeout_minutes, expected_type=type_hints["textract_state_machine_timeout_minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_output_bucket": s3_output_bucket,
            "s3_temp_output_prefix": s3_temp_output_prefix,
        }
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if associate_with_parent is not None:
            self._values["associate_with_parent"] = associate_with_parent
        if enable_cloud_watch_metrics_and_dashboard is not None:
            self._values["enable_cloud_watch_metrics_and_dashboard"] = enable_cloud_watch_metrics_and_dashboard
        if input is not None:
            self._values["input"] = input
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory is not None:
            self._values["lambda_memory"] = lambda_memory
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if name is not None:
            self._values["name"] = name
        if output_policy_statements is not None:
            self._values["output_policy_statements"] = output_policy_statements
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if sns_role_textract is not None:
            self._values["sns_role_textract"] = sns_role_textract
        if task_token_table is not None:
            self._values["task_token_table"] = task_token_table
        if textract_api is not None:
            self._values["textract_api"] = textract_api
        if textract_async_call_backoff_rate is not None:
            self._values["textract_async_call_backoff_rate"] = textract_async_call_backoff_rate
        if textract_async_call_interval is not None:
            self._values["textract_async_call_interval"] = textract_async_call_interval
        if textract_async_call_max_retries is not None:
            self._values["textract_async_call_max_retries"] = textract_async_call_max_retries
        if textract_state_machine_timeout_minutes is not None:
            self._values["textract_state_machine_timeout_minutes"] = textract_state_machine_timeout_minutes

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def s3_output_bucket(self) -> builtins.str:
        '''Bucketname to output data to.'''
        result = self._values.get("s3_output_bucket")
        assert result is not None, "Required property 's3_output_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_temp_output_prefix(self) -> builtins.str:
        '''The prefix to use for the temporary output files (e.

        g. output from async process before stiching together)
        '''
        result = self._values.get("s3_temp_output_prefix")
        assert result is not None, "Required property 's3_temp_output_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associate_with_parent(self) -> typing.Optional[builtins.bool]:
        '''Pass the execution ID from the context object to the execution input.

        This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines.

        If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely.

        :default: - false

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-nested-workflows.html#nested-execution-startid
        '''
        result = self._values.get("associate_with_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_cloud_watch_metrics_and_dashboard(
        self,
    ) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable_cloud_watch_metrics_and_dashboard")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def input(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput]:
        '''The JSON input for the execution, same as that of StartExecution.

        :default: - The state input (JSON path '$')

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput], result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        '''log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL.

        :default: = DEBUG
        '''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory(self) -> typing.Optional[jsii.Number]:
        '''Memory allocated to Lambda function, default 512.'''
        result = self._values.get("lambda_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda Function Timeout in seconds, default 300.'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the execution, same as that of StartExecution.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("output_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        '''Bucketname and prefix to read document from /** location of input S3 objects - if left empty will generate rule for s3 access to all [*].'''
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for input S3 objects - if left empty will generate rule for s3 access to all in bucket.'''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sns_role_textract(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''IAM Role to assign to Textract, by default new iam.Role(this, 'TextractAsyncSNSRole', { assumedBy: new iam.ServicePrincipal('textract.amazonaws.com'), managedPolicies: [ManagedPolicy.fromAwsManagedPolicyName('AmazonSQSFullAccess'),   ManagedPolicy.fromAwsManagedPolicyName('AmazonSNSFullAccess'),   ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'),   ManagedPolicy.fromAwsManagedPolicyName('AmazonTextractFullAccess')], });'''
        result = self._values.get("sns_role_textract")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def task_token_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable]:
        '''task token table to use for mapping of Textract `JobTag <https://docs.aws.amazon.com/textract/latest/dg/API_StartDocumentTextDetection.html#Textract-StartDocumentTextDetection-request-JobTag>`_ to the `TaskToken <https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html>`_.'''
        result = self._values.get("task_token_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable], result)

    @builtins.property
    def textract_api(self) -> typing.Optional[builtins.str]:
        '''Which Textract API to call ALL asynchronous Textract API calls are supported. Valid values are GENERIC | EXPENSE | LENDING.

        For GENERIC, when called without features (e. g. FORMS, TABLES, QUERIES, SIGNATURE), StartDetectText is called and only OCR is returned.
        For GENERIC, when called with a feature (e. g. FORMS, TABLES, QUERIES, SIGNATURE),  StartAnalyzeDocument is called.

        :default: - GENERIC
        '''
        result = self._values.get("textract_api")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_async_call_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''retyr backoff rate.

        :default: is 1.1
        '''
        result = self._values.get("textract_async_call_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_async_call_interval(self) -> typing.Optional[jsii.Number]:
        '''time in seconds to wait before next retry.

        :default: is 1
        '''
        result = self._values.get("textract_async_call_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_async_call_max_retries(self) -> typing.Optional[jsii.Number]:
        '''number of retries in Step Function flow.

        :default: is 100
        '''
        result = self._values.get("textract_async_call_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_state_machine_timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''how long can we wait for the process.

        :default: - 2880 (48 hours (60 min * 48 hours = 2880))
        '''
        result = self._values.get("textract_state_machine_timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractGenericAsyncSfnTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractGenericSyncSfnTask(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractGenericSyncSfnTask",
):
    '''Calls Textract synchronous API.

    Supports the Textract APIs:  'GENERIC' | 'ANALYZEID' | 'EXPENSE'
    When GENERIC is called with features in the manifest definition, will call the AnalzyeDocument API.
    Takes the configuration from "Payload"."manifest"
    Will retry on recoverable errors based on textractAsyncCallMaxRetries
    errors for retry: ['ThrottlingException', 'LimitExceededException', 'InternalServerError', 'ProvisionedThroughputExceededException'],

    Input: "Payload"."manifest"
    Output: Textract JSON Schema at  s3_output_bucket/s3_output_prefix

    Example (Python::

               textract_sync_task = tcdk.TextractGenericSyncSfnTask(
                self,
                "TextractSync",
                s3_output_bucket=document_bucket.bucket_name,
                s3_output_prefix=s3_output_prefix,
                integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
                lambda_log_level="DEBUG",
                timeout=Duration.hours(24),
                input=sfn.TaskInput.from_object({
                    "Token":
                    sfn.JsonPath.task_token,
                    "ExecutionId":
                    sfn.JsonPath.string_at('$$.Execution.Id'),
                    "Payload":
                    sfn.JsonPath.entire_payload,
                }),
                result_path="$.textract_result")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        custom_function: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke] = None,
        enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
        enable_dashboard: typing.Optional[builtins.bool] = None,
        enable_monitoring: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_async_call_interval: typing.Optional[jsii.Number] = None,
        textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: Descriptive identifier for this chainable.
        :param s3_output_bucket: 
        :param s3_output_prefix: The prefix to use for the output files.
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param custom_function: not implemented yet.
        :param enable_cloud_watch_metrics_and_dashboard: enable CloudWatch Metrics and Dashboard. Default: - false
        :param enable_dashboard: not implemented yet.
        :param enable_monitoring: not implemented yet.
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: Log level, can be DEBUG, INFO, WARNING, ERROR, FATAL.
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param textract_api: 
        :param textract_async_call_backoff_rate: default is 1.1.
        :param textract_async_call_interval: default is 1.
        :param textract_async_call_max_retries: 
        :param textract_state_machine_timeout_minutes: how long can we wait for the process (default is 48 hours (60*48=2880)).
        :param workflow_tracing_enabled: 
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__793a5ab15766407e031c419bf4d089e96abc4421156ef15e7f9749ffc4086ed8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractGenericSyncSfnTaskProps(
            s3_output_bucket=s3_output_bucket,
            s3_output_prefix=s3_output_prefix,
            associate_with_parent=associate_with_parent,
            custom_function=custom_function,
            enable_cloud_watch_metrics_and_dashboard=enable_cloud_watch_metrics_and_dashboard,
            enable_dashboard=enable_dashboard,
            enable_monitoring=enable_monitoring,
            input=input,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory=lambda_memory,
            lambda_timeout=lambda_timeout,
            name=name,
            output_policy_statements=output_policy_statements,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            textract_api=textract_api,
            textract_async_call_backoff_rate=textract_async_call_backoff_rate,
            textract_async_call_interval=textract_async_call_interval,
            textract_async_call_max_retries=textract_async_call_max_retries,
            textract_state_machine_timeout_minutes=textract_state_machine_timeout_minutes,
            workflow_tracing_enabled=workflow_tracing_enabled,
            comment=comment,
            credentials=credentials,
            heartbeat=heartbeat,
            heartbeat_timeout=heartbeat_timeout,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            state_name=state_name,
            task_timeout=task_timeout,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig]:
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "taskPolicies"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d06e25702bc2c6c8d8a28658e7429243b5032768a8390aaf26934a31686d4c33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)

    @builtins.property
    @jsii.member(jsii_name="textractSyncCallFunction")
    def textract_sync_call_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "textractSyncCallFunction"))

    @textract_sync_call_function.setter
    def textract_sync_call_function(
        self,
        value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d969ae74a43dd83502fa61354c655c16adbc642b29c354ccbe80b25e726e43f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textractSyncCallFunction", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3bc7f11cb150a5e48113ccb8ab4ffee26b93135122b42b7659d7815bfe5fb51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="syncDurationMetric")
    def sync_duration_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "syncDurationMetric"))

    @sync_duration_metric.setter
    def sync_duration_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33f7ad694796670888d8e3799055c1c911f916b7daafb1be179e59c404606951)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncDurationMetric", value)

    @builtins.property
    @jsii.member(jsii_name="syncNumberPagesMetric")
    def sync_number_pages_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "syncNumberPagesMetric"))

    @sync_number_pages_metric.setter
    def sync_number_pages_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c158f5aaa93987354325b0f60702bc529c5de9900d3614a00496ffb4e6f9ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncNumberPagesMetric", value)

    @builtins.property
    @jsii.member(jsii_name="syncNumberPagesSendMetric")
    def sync_number_pages_send_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "syncNumberPagesSendMetric"))

    @sync_number_pages_send_metric.setter
    def sync_number_pages_send_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9c063defca0576885ada84ec2819cb5f6043237d1e74c254edb157fee0644b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncNumberPagesSendMetric", value)

    @builtins.property
    @jsii.member(jsii_name="syncTimedOutMetric")
    def sync_timed_out_metric(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.get(self, "syncTimedOutMetric"))

    @sync_timed_out_metric.setter
    def sync_timed_out_metric(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b9af5e300c69cc6ec26b6862b39ad25743dc40cb36bed281a48779068fc674b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncTimedOutMetric", value)


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractGenericSyncSfnTaskProps",
    jsii_struct_bases=[_aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps],
    name_mapping={
        "comment": "comment",
        "credentials": "credentials",
        "heartbeat": "heartbeat",
        "heartbeat_timeout": "heartbeatTimeout",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "state_name": "stateName",
        "task_timeout": "taskTimeout",
        "timeout": "timeout",
        "s3_output_bucket": "s3OutputBucket",
        "s3_output_prefix": "s3OutputPrefix",
        "associate_with_parent": "associateWithParent",
        "custom_function": "customFunction",
        "enable_cloud_watch_metrics_and_dashboard": "enableCloudWatchMetricsAndDashboard",
        "enable_dashboard": "enableDashboard",
        "enable_monitoring": "enableMonitoring",
        "input": "input",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory": "lambdaMemory",
        "lambda_timeout": "lambdaTimeout",
        "name": "name",
        "output_policy_statements": "outputPolicyStatements",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
        "textract_api": "textractAPI",
        "textract_async_call_backoff_rate": "textractAsyncCallBackoffRate",
        "textract_async_call_interval": "textractAsyncCallInterval",
        "textract_async_call_max_retries": "textractAsyncCallMaxRetries",
        "textract_state_machine_timeout_minutes": "textractStateMachineTimeoutMinutes",
        "workflow_tracing_enabled": "workflowTracingEnabled",
    },
)
class TextractGenericSyncSfnTaskProps(
    _aws_cdk_aws_stepfunctions_ceddda9d.TaskStateBaseProps,
):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
        heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        state_name: typing.Optional[builtins.str] = None,
        task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        associate_with_parent: typing.Optional[builtins.bool] = None,
        custom_function: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke] = None,
        enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
        enable_dashboard: typing.Optional[builtins.bool] = None,
        enable_monitoring: typing.Optional[builtins.bool] = None,
        input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_api: typing.Optional[builtins.str] = None,
        textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_async_call_interval: typing.Optional[jsii.Number] = None,
        textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
        textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
        workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param comment: An optional description for this state. Default: - No comment
        :param credentials: Credentials for an IAM Role that the State Machine assumes for executing the task. This enables cross-account resource invocations. Default: - None (Task is executed using the State Machine's execution role)
        :param heartbeat: (deprecated) Timeout for the heartbeat. Default: - None
        :param heartbeat_timeout: Timeout for the heartbeat. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns. Depending on the AWS Service, the Service Integration Pattern availability will vary. Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param state_name: Optional name for this state. Default: - The construct ID will be used as state name
        :param task_timeout: Timeout for the task. [disable-awslint:duration-prop-type] is needed because all props interface in aws-stepfunctions-tasks extend this interface Default: - None
        :param timeout: (deprecated) Timeout for the task. Default: - None
        :param s3_output_bucket: 
        :param s3_output_prefix: The prefix to use for the output files.
        :param associate_with_parent: Pass the execution ID from the context object to the execution input. This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines. If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely. Default: - false
        :param custom_function: not implemented yet.
        :param enable_cloud_watch_metrics_and_dashboard: enable CloudWatch Metrics and Dashboard. Default: - false
        :param enable_dashboard: not implemented yet.
        :param enable_monitoring: not implemented yet.
        :param input: The JSON input for the execution, same as that of StartExecution. Default: - The state input (JSON path '$')
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param lambda_log_level: Log level, can be DEBUG, INFO, WARNING, ERROR, FATAL.
        :param lambda_memory: Memory allocated to Lambda function, default 512.
        :param lambda_timeout: Lambda Function Timeout in seconds, default 300.
        :param name: The name of the execution, same as that of StartExecution. Default: - None
        :param output_policy_statements: List of PolicyStatements to attach to the Lambda function.
        :param s3_input_bucket: location of input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param s3_input_prefix: prefix for input S3 objects - if left empty will generate rule for s3 access to all [*].
        :param textract_api: 
        :param textract_async_call_backoff_rate: default is 1.1.
        :param textract_async_call_interval: default is 1.
        :param textract_async_call_max_retries: 
        :param textract_state_machine_timeout_minutes: how long can we wait for the process (default is 48 hours (60*48=2880)).
        :param workflow_tracing_enabled: 
        '''
        if isinstance(credentials, dict):
            credentials = _aws_cdk_aws_stepfunctions_ceddda9d.Credentials(**credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4d6df050846f4b04d077141bc7412b5ebde87938736d06fd540eb22a4b968eb)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument heartbeat_timeout", value=heartbeat_timeout, expected_type=type_hints["heartbeat_timeout"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument state_name", value=state_name, expected_type=type_hints["state_name"])
            check_type(argname="argument task_timeout", value=task_timeout, expected_type=type_hints["task_timeout"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument s3_output_bucket", value=s3_output_bucket, expected_type=type_hints["s3_output_bucket"])
            check_type(argname="argument s3_output_prefix", value=s3_output_prefix, expected_type=type_hints["s3_output_prefix"])
            check_type(argname="argument associate_with_parent", value=associate_with_parent, expected_type=type_hints["associate_with_parent"])
            check_type(argname="argument custom_function", value=custom_function, expected_type=type_hints["custom_function"])
            check_type(argname="argument enable_cloud_watch_metrics_and_dashboard", value=enable_cloud_watch_metrics_and_dashboard, expected_type=type_hints["enable_cloud_watch_metrics_and_dashboard"])
            check_type(argname="argument enable_dashboard", value=enable_dashboard, expected_type=type_hints["enable_dashboard"])
            check_type(argname="argument enable_monitoring", value=enable_monitoring, expected_type=type_hints["enable_monitoring"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory", value=lambda_memory, expected_type=type_hints["lambda_memory"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument output_policy_statements", value=output_policy_statements, expected_type=type_hints["output_policy_statements"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
            check_type(argname="argument textract_api", value=textract_api, expected_type=type_hints["textract_api"])
            check_type(argname="argument textract_async_call_backoff_rate", value=textract_async_call_backoff_rate, expected_type=type_hints["textract_async_call_backoff_rate"])
            check_type(argname="argument textract_async_call_interval", value=textract_async_call_interval, expected_type=type_hints["textract_async_call_interval"])
            check_type(argname="argument textract_async_call_max_retries", value=textract_async_call_max_retries, expected_type=type_hints["textract_async_call_max_retries"])
            check_type(argname="argument textract_state_machine_timeout_minutes", value=textract_state_machine_timeout_minutes, expected_type=type_hints["textract_state_machine_timeout_minutes"])
            check_type(argname="argument workflow_tracing_enabled", value=workflow_tracing_enabled, expected_type=type_hints["workflow_tracing_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_output_bucket": s3_output_bucket,
            "s3_output_prefix": s3_output_prefix,
        }
        if comment is not None:
            self._values["comment"] = comment
        if credentials is not None:
            self._values["credentials"] = credentials
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if heartbeat_timeout is not None:
            self._values["heartbeat_timeout"] = heartbeat_timeout
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if state_name is not None:
            self._values["state_name"] = state_name
        if task_timeout is not None:
            self._values["task_timeout"] = task_timeout
        if timeout is not None:
            self._values["timeout"] = timeout
        if associate_with_parent is not None:
            self._values["associate_with_parent"] = associate_with_parent
        if custom_function is not None:
            self._values["custom_function"] = custom_function
        if enable_cloud_watch_metrics_and_dashboard is not None:
            self._values["enable_cloud_watch_metrics_and_dashboard"] = enable_cloud_watch_metrics_and_dashboard
        if enable_dashboard is not None:
            self._values["enable_dashboard"] = enable_dashboard
        if enable_monitoring is not None:
            self._values["enable_monitoring"] = enable_monitoring
        if input is not None:
            self._values["input"] = input
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory is not None:
            self._values["lambda_memory"] = lambda_memory
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if name is not None:
            self._values["name"] = name
        if output_policy_statements is not None:
            self._values["output_policy_statements"] = output_policy_statements
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix
        if textract_api is not None:
            self._values["textract_api"] = textract_api
        if textract_async_call_backoff_rate is not None:
            self._values["textract_async_call_backoff_rate"] = textract_async_call_backoff_rate
        if textract_async_call_interval is not None:
            self._values["textract_async_call_interval"] = textract_async_call_interval
        if textract_async_call_max_retries is not None:
            self._values["textract_async_call_max_retries"] = textract_async_call_max_retries
        if textract_state_machine_timeout_minutes is not None:
            self._values["textract_state_machine_timeout_minutes"] = textract_state_machine_timeout_minutes
        if workflow_tracing_enabled is not None:
            self._values["workflow_tracing_enabled"] = workflow_tracing_enabled

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials]:
        '''Credentials for an IAM Role that the State Machine assumes for executing the task.

        This enables cross-account resource invocations.

        :default: - None (Task is executed using the State Machine's execution role)

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-access-cross-acct-resources.html
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the heartbeat.

        :default: - None

        :deprecated: use ``heartbeatTimeout``

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def heartbeat_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the heartbeat.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("heartbeat_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns.

        Depending on the AWS Service, the Service Integration Pattern availability will vary.

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-supported-services.html
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def state_name(self) -> typing.Optional[builtins.str]:
        '''Optional name for this state.

        :default: - The construct ID will be used as state name
        '''
        result = self._values.get("state_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout]:
        '''Timeout for the task.

        [disable-awslint:duration-prop-type] is needed because all props interface in
        aws-stepfunctions-tasks extend this interface

        :default: - None
        '''
        result = self._values.get("task_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(deprecated) Timeout for the task.

        :default: - None

        :deprecated: use ``taskTimeout``

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def s3_output_bucket(self) -> builtins.str:
        result = self._values.get("s3_output_bucket")
        assert result is not None, "Required property 's3_output_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_output_prefix(self) -> builtins.str:
        '''The prefix to use for the output files.'''
        result = self._values.get("s3_output_prefix")
        assert result is not None, "Required property 's3_output_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associate_with_parent(self) -> typing.Optional[builtins.bool]:
        '''Pass the execution ID from the context object to the execution input.

        This allows the Step Functions UI to link child executions from parent executions, making it easier to trace execution flow across state machines.

        If you set this property to ``true``, the ``input`` property must be an object (provided by ``sfn.TaskInput.fromObject``) or omitted entirely.

        :default: - false

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-nested-workflows.html#nested-execution-startid
        '''
        result = self._values.get("associate_with_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke]:
        '''not implemented yet.'''
        result = self._values.get("custom_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke], result)

    @builtins.property
    def enable_cloud_watch_metrics_and_dashboard(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''enable CloudWatch Metrics and Dashboard.

        :default: - false
        '''
        result = self._values.get("enable_cloud_watch_metrics_and_dashboard")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_dashboard(self) -> typing.Optional[builtins.bool]:
        '''not implemented yet.'''
        result = self._values.get("enable_dashboard")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_monitoring(self) -> typing.Optional[builtins.bool]:
        '''not implemented yet.'''
        result = self._values.get("enable_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def input(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput]:
        '''The JSON input for the execution, same as that of StartExecution.

        :default: - The state input (JSON path '$')

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput], result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        '''Log level, can be DEBUG, INFO, WARNING, ERROR, FATAL.'''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory(self) -> typing.Optional[jsii.Number]:
        '''Memory allocated to Lambda function, default 512.'''
        result = self._values.get("lambda_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda Function Timeout in seconds, default 300.'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the execution, same as that of StartExecution.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function.'''
        result = self._values.get("output_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        '''location of input S3 objects - if left empty will generate rule for s3 access to all [*].'''
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for input S3 objects - if left empty will generate rule for s3 access to all [*].'''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_api(self) -> typing.Optional[builtins.str]:
        result = self._values.get("textract_api")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract_async_call_backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''default is 1.1.'''
        result = self._values.get("textract_async_call_backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_async_call_interval(self) -> typing.Optional[jsii.Number]:
        '''default is 1.'''
        result = self._values.get("textract_async_call_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_async_call_max_retries(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("textract_async_call_max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def textract_state_machine_timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''how long can we wait for the process (default is 48 hours (60*48=2880)).'''
        result = self._values.get("textract_state_machine_timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def workflow_tracing_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("workflow_tracing_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractGenericSyncSfnTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractPOCDecider(
    _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineFragment,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractPOCDecider",
):
    '''This construct takes in a manifest definition or a plain JSON with a s3Path:.

    example s3Path:
    {"s3Path": "s3://bucketname/prefix/image.png"}

    Then it generated the numberOfPages attribute and the mime on the context.
    The mime types checked against the supported mime types for Textract and if fails, will raise an Exception failing the workflow.

    Example (Python::

       decider_task_id = tcdk.TextractPOCDecider(
            self,
            f"InsuranceDecider",
       )
    '''

    def __init__(
        self,
        parent: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        decider_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
        textract_decider_backoff_rate: typing.Optional[jsii.Number] = None,
        textract_decider_interval: typing.Optional[jsii.Number] = None,
        textract_decider_max_retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: Descriptive identifier for this chainable.
        :param decider_function: 
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.
        :param lambda_log_level: log level for Lambda function, supports DEBUG|INFO|WARNING|ERROR|FATAL. Default: = DEBUG
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param s3_input_bucket: 
        :param s3_input_prefix: prefix for the incoming document. Will be used to create role
        :param textract_decider_backoff_rate: retyr backoff rate. Default: is 1.1
        :param textract_decider_interval: 
        :param textract_decider_max_retries: number of retries in Step Function flow. Default: is 100
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c04b9c5783206479fa4562fd8f4e84d755f71078456005bb09f27ece829a4a84)
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractDPPOCDeciderProps(
            decider_function=decider_function,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
            textract_decider_backoff_rate=textract_decider_backoff_rate,
            textract_decider_interval=textract_decider_interval,
            textract_decider_max_retries=textract_decider_max_retries,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property
    @jsii.member(jsii_name="deciderFunction")
    def decider_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "deciderFunction"))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.State:
        '''The start state of this state machine fragment.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.State, jsii.get(self, "startState"))


class TextractPdfMapperForFhir(
    _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineFragment,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.TextractPdfMapperForFhir",
):
    '''This construct takes in a manifest definition or a plain JSON with a s3Path:.

    example s3Path:
    {"s3Path": "s3://bucketname/prefix/image.png"}

    Then it generated the numberOfPages attribute and the mime on the context.
    The mime types checked against the supported mime types for Textract and if fails, will raise an Exception failing the workflow.

    Example (Python::

       decider_task_id = tcdk.TextractPOCDecider(
       self,
       f"InsuranceDecider",
       )
    '''

    def __init__(
        self,
        parent: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        healthlake_endpoint: typing.Optional[builtins.str] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        pdf_mapper_for_fhir_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: Descriptive identifier for this chainable.
        :param healthlake_endpoint: 
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.
        :param lambda_log_level: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param pdf_mapper_for_fhir_function: 
        :param s3_input_bucket: 
        :param s3_input_prefix: prefix for the incoming document. Will be used to create role
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24c2f438d42a1aebdfcfb2b07fe3b28b4071efa2c5d7cbe613542f0023e206b9)
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TextractPdfMapperForFhirProps(
            healthlake_endpoint=healthlake_endpoint,
            input_policy_statements=input_policy_statements,
            lambda_log_level=lambda_log_level,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
            pdf_mapper_for_fhir_function=pdf_mapper_for_fhir_function,
            s3_input_bucket=s3_input_bucket,
            s3_input_prefix=s3_input_prefix,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[_aws_cdk_aws_stepfunctions_ceddda9d.INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="pdfMapperForFhirFunction")
    def pdf_mapper_for_fhir_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "pdfMapperForFhirFunction"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.State:
        '''The start state of this state machine fragment.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.State, jsii.get(self, "startState"))


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.TextractPdfMapperForFhirProps",
    jsii_struct_bases=[],
    name_mapping={
        "healthlake_endpoint": "healthlakeEndpoint",
        "input_policy_statements": "inputPolicyStatements",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
        "pdf_mapper_for_fhir_function": "pdfMapperForFhirFunction",
        "s3_input_bucket": "s3InputBucket",
        "s3_input_prefix": "s3InputPrefix",
    },
)
class TextractPdfMapperForFhirProps:
    def __init__(
        self,
        *,
        healthlake_endpoint: typing.Optional[builtins.str] = None,
        input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        lambda_log_level: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
        pdf_mapper_for_fhir_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        s3_input_bucket: typing.Optional[builtins.str] = None,
        s3_input_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param healthlake_endpoint: 
        :param input_policy_statements: List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.
        :param lambda_log_level: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        :param lambda_timeout: 
        :param pdf_mapper_for_fhir_function: 
        :param s3_input_bucket: 
        :param s3_input_prefix: prefix for the incoming document. Will be used to create role
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aafa2ff073995cbd086e64592fa34d573e4d22cd94a183aff3a791bdbb73ba92)
            check_type(argname="argument healthlake_endpoint", value=healthlake_endpoint, expected_type=type_hints["healthlake_endpoint"])
            check_type(argname="argument input_policy_statements", value=input_policy_statements, expected_type=type_hints["input_policy_statements"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
            check_type(argname="argument pdf_mapper_for_fhir_function", value=pdf_mapper_for_fhir_function, expected_type=type_hints["pdf_mapper_for_fhir_function"])
            check_type(argname="argument s3_input_bucket", value=s3_input_bucket, expected_type=type_hints["s3_input_bucket"])
            check_type(argname="argument s3_input_prefix", value=s3_input_prefix, expected_type=type_hints["s3_input_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if healthlake_endpoint is not None:
            self._values["healthlake_endpoint"] = healthlake_endpoint
        if input_policy_statements is not None:
            self._values["input_policy_statements"] = input_policy_statements
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout
        if pdf_mapper_for_fhir_function is not None:
            self._values["pdf_mapper_for_fhir_function"] = pdf_mapper_for_fhir_function
        if s3_input_bucket is not None:
            self._values["s3_input_bucket"] = s3_input_bucket
        if s3_input_prefix is not None:
            self._values["s3_input_prefix"] = s3_input_prefix

    @builtins.property
    def healthlake_endpoint(self) -> typing.Optional[builtins.str]:
        result = self._values.get("healthlake_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''List of PolicyStatements to attach to the Lambda function for S3 GET and LIST.'''
        result = self._values.get("input_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pdf_mapper_for_fhir_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        result = self._values.get("pdf_mapper_for_fhir_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], result)

    @builtins.property
    def s3_input_bucket(self) -> typing.Optional[builtins.str]:
        result = self._values.get("s3_input_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_input_prefix(self) -> typing.Optional[builtins.str]:
        '''prefix for the incoming document.

        Will be used to create role
        '''
        result = self._values.get("s3_input_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractPdfMapperForFhirProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkmailS3IngestionPoint(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="amazon-textract-idp-cdk-constructs.WorkmailS3IngestionPoint",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        workmail_account_number: builtins.str,
        workmail_region: builtins.str,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param s3_output_bucket: Bucket name to output data to.
        :param s3_output_prefix: The prefix to use to output files to.
        :param workmail_account_number: Account number for WorkMail instance.
        :param workmail_region: Region where WorkMailail instance exists.
        :param lambda_memory_mb: Lambda function memory configuration (may need to increase for larger documents).
        :param lambda_timeout: Lambda function timeout (may need to increase for larger documents).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc9009b1e4be5967e6cd482a979819174535fbac2849b1d7b4b3ebc2abcc58a5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WorkmailS3IngestionPointProps(
            s3_output_bucket=s3_output_bucket,
            s3_output_prefix=s3_output_prefix,
            workmail_account_number=workmail_account_number,
            workmail_region=workmail_region,
            lambda_memory_mb=lambda_memory_mb,
            lambda_timeout=lambda_timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "WorkmailS3IngestionPointProps":
        return typing.cast("WorkmailS3IngestionPointProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="amazon-textract-idp-cdk-constructs.WorkmailS3IngestionPointProps",
    jsii_struct_bases=[],
    name_mapping={
        "s3_output_bucket": "s3OutputBucket",
        "s3_output_prefix": "s3OutputPrefix",
        "workmail_account_number": "workmailAccountNumber",
        "workmail_region": "workmailRegion",
        "lambda_memory_mb": "lambdaMemoryMB",
        "lambda_timeout": "lambdaTimeout",
    },
)
class WorkmailS3IngestionPointProps:
    def __init__(
        self,
        *,
        s3_output_bucket: builtins.str,
        s3_output_prefix: builtins.str,
        workmail_account_number: builtins.str,
        workmail_region: builtins.str,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
        lambda_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param s3_output_bucket: Bucket name to output data to.
        :param s3_output_prefix: The prefix to use to output files to.
        :param workmail_account_number: Account number for WorkMail instance.
        :param workmail_region: Region where WorkMailail instance exists.
        :param lambda_memory_mb: Lambda function memory configuration (may need to increase for larger documents).
        :param lambda_timeout: Lambda function timeout (may need to increase for larger documents).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55ee8bdcaeb142cce00840207986a2edbec46183c1b520e5570c9e838b2138e9)
            check_type(argname="argument s3_output_bucket", value=s3_output_bucket, expected_type=type_hints["s3_output_bucket"])
            check_type(argname="argument s3_output_prefix", value=s3_output_prefix, expected_type=type_hints["s3_output_prefix"])
            check_type(argname="argument workmail_account_number", value=workmail_account_number, expected_type=type_hints["workmail_account_number"])
            check_type(argname="argument workmail_region", value=workmail_region, expected_type=type_hints["workmail_region"])
            check_type(argname="argument lambda_memory_mb", value=lambda_memory_mb, expected_type=type_hints["lambda_memory_mb"])
            check_type(argname="argument lambda_timeout", value=lambda_timeout, expected_type=type_hints["lambda_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_output_bucket": s3_output_bucket,
            "s3_output_prefix": s3_output_prefix,
            "workmail_account_number": workmail_account_number,
            "workmail_region": workmail_region,
        }
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb
        if lambda_timeout is not None:
            self._values["lambda_timeout"] = lambda_timeout

    @builtins.property
    def s3_output_bucket(self) -> builtins.str:
        '''Bucket name to output data to.'''
        result = self._values.get("s3_output_bucket")
        assert result is not None, "Required property 's3_output_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_output_prefix(self) -> builtins.str:
        '''The prefix to use to output files to.'''
        result = self._values.get("s3_output_prefix")
        assert result is not None, "Required property 's3_output_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workmail_account_number(self) -> builtins.str:
        '''Account number for WorkMail instance.'''
        result = self._values.get("workmail_account_number")
        assert result is not None, "Required property 'workmail_account_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workmail_region(self) -> builtins.str:
        '''Region where WorkMailail instance exists.'''
        result = self._values.get("workmail_region")
        assert result is not None, "Required property 'workmail_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''Lambda function memory configuration (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lambda_timeout(self) -> typing.Optional[jsii.Number]:
        '''Lambda function timeout (may need to increase for larger documents).'''
        result = self._values.get("lambda_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkmailS3IngestionPointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CSVToAuroraTask",
    "CSVToAuroraTaskProps",
    "ComprehendGenericSyncSfnTask",
    "ComprehendGenericSyncSfnTaskProps",
    "DocumentSplitter",
    "DocumentSplitterProps",
    "RDSAuroraServerless",
    "RDSAuroraServerlessProps",
    "SFExecutionsStartThrottle",
    "SFExecutionsStartThrottleProps",
    "SearchablePDF",
    "SearchablePDFProps",
    "SpacySfnTask",
    "SpacySfnTaskProps",
    "TextractA2ISfnTask",
    "TextractA2ISfnTaskProps",
    "TextractAsyncToJSON",
    "TextractAsyncToJSONProps",
    "TextractClassificationConfigurator",
    "TextractClassificationConfiguratorProps",
    "TextractDPPOCDeciderProps",
    "TextractGenerateCSV",
    "TextractGenerateCSVProps",
    "TextractGenericAsyncSfnTask",
    "TextractGenericAsyncSfnTaskProps",
    "TextractGenericSyncSfnTask",
    "TextractGenericSyncSfnTaskProps",
    "TextractPOCDecider",
    "TextractPdfMapperForFhir",
    "TextractPdfMapperForFhirProps",
    "WorkmailS3IngestionPoint",
    "WorkmailS3IngestionPointProps",
]

publication.publish()

def _typecheckingstub__0a2e915f2bf738499fb1487469c5a5e7b97f3ea53531d09db1a1bacc5f572542(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    aurora_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    csv_to_aurora_backoff_rate: typing.Optional[jsii.Number] = None,
    csv_to_aurora_interval: typing.Optional[jsii.Number] = None,
    csv_to_aurora_max_retries: typing.Optional[jsii.Number] = None,
    db_cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IServerlessCluster] = None,
    enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82837931957c3dd9d3602fad7af22ad0fcacfd3cd4cc6b9199599ad4623503c8(
    value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f76fbf836296c7c37da75f18dabbda8311aeeb758c33dea2f339743fbfb9b3d1(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e962768ad2bfc77aaeda9d218418307d7d450329f1735abf8f7332a1bc4f9687(
    value: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaabceaa7d653a142ec9115e2e01f188d1f4a9be5bb0ffcef33b721cfde765d1(
    value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40bc9b871f0e01af4838f0f7a8326ba8c48c05b812e3ea9cfb29c8eb921ad942(
    value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e0969ad66f893b6d17a70a58d88d7d04ef99b2824366468bf6d55bc298423e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ef4b9117bbdbe85cdc85ec1901714ddc9e6ef2395abb4701064b4a54099504(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c2ee7750549ff02b28f95157bc497795ddaa5f6133871e998e75e7abe2f0dd(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    aurora_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    csv_to_aurora_backoff_rate: typing.Optional[jsii.Number] = None,
    csv_to_aurora_interval: typing.Optional[jsii.Number] = None,
    csv_to_aurora_max_retries: typing.Optional[jsii.Number] = None,
    db_cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IServerlessCluster] = None,
    enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63c572f65dc7f491f95786c369eac23465969ddc2b18fc82124b18bbf54608ff(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comprehend_classifier_arn: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    comprehend_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
    comprehend_async_call_interval: typing.Optional[jsii.Number] = None,
    comprehend_async_call_max_retries: typing.Optional[jsii.Number] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    s3_output_bucket: typing.Optional[builtins.str] = None,
    s3_output_prefix: typing.Optional[builtins.str] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b8c4f3a3b7df132617bb763e98f942130118e9e14cda98200ec63a3dd65302a(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88605655023bd2fb2a31c523e359bcdee1cc7c910354b7e49356a86711628c95(
    value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd1df667c4c218e3d6dc978377c6767932411e6c4cd185c49592593e34cee887(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2b7726103e7a4c7cea8aea6f000ef6e4dc789c73d251956c09d384beee75afe(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    comprehend_classifier_arn: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    comprehend_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
    comprehend_async_call_interval: typing.Optional[jsii.Number] = None,
    comprehend_async_call_max_retries: typing.Optional[jsii.Number] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    s3_output_bucket: typing.Optional[builtins.str] = None,
    s3_output_prefix: typing.Optional[builtins.str] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2639041e32a9dfde7241ef351ea92ed6441a727bea4f2f0cf8a56cc7f7cb0e6(
    parent: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    max_number_of_pages_per_doc: typing.Optional[jsii.Number] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_document_splitter_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_document_splitter_interval: typing.Optional[jsii.Number] = None,
    textract_document_splitter_max_retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99cd884facaff7b56a4ce1fd62f5a59a7644a182c07d44883c1d6ae3de02c232(
    *,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    max_number_of_pages_per_doc: typing.Optional[jsii.Number] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_document_splitter_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_document_splitter_interval: typing.Optional[jsii.Number] = None,
    textract_document_splitter_max_retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e11147041f993d47d56add049fc858c0d1df6c1127f7137d8661bd07a9f4d405(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d557d1c2b59bb23d5cefecf9c7f57d343b756227ed7cf4a8fb8f2fa260e7f8f(
    value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8611db7dda185294a258507b8a8568f28d4356fc4ee494db89c9265f868ff1cb(
    value: _aws_cdk_aws_rds_ceddda9d.IServerlessCluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4ce4c6b56e174ea3d2a95f7b17f543c9cf19b46a5be14db0e0e0be863214c1b(
    value: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187e75bcc1fc38138651a846c6db0b7e0ef1481679b93c68fa26f695a030e11e(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72e5539db4ba9c10e720e52655ff6abf2c03775395aafc3cdd71a1d91c69aff9(
    parent: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    state_machine_arn: builtins.str,
    document_status_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    event_source: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
    executions_concurrency_threshold: typing.Optional[jsii.Number] = None,
    executions_counter_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_queue_worker_log_level: typing.Optional[builtins.str] = None,
    lambda_queue_worker_memory: typing.Optional[jsii.Number] = None,
    lambda_queue_worker_timeout: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    sqs_batch: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3abab5947799560a7880220092bc8766496d6cd1c862917d8582ac57a4cc1b36(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f5130d5a60a73150b5abea6c79abb2acecfb9a27dbea8e9a1724eaf900ed3ae(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__129e5511ad5a05c698fd71fcdb300cab4330ab5b3cd41d6efb0a8f8eb77075af(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae42b52edc190822a38868deb658ae9ce847f755cf609cad61aa13633370f24a(
    value: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a97ef827b78442fb4da04bab1c6919b8f402d05a0c19b6c96ad0e6d0323a2cae(
    value: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f91e0a6e744fcfa1b42392cb32a4c95da7836f3df03638d61ac4c6303895fe6(
    value: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0419356c8968d9e5fe6e85d2ace136c9a4c171988fdb514af58a850a8503ad6c(
    *,
    state_machine_arn: builtins.str,
    document_status_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    event_source: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.IEventSource]] = None,
    executions_concurrency_threshold: typing.Optional[jsii.Number] = None,
    executions_counter_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_queue_worker_log_level: typing.Optional[builtins.str] = None,
    lambda_queue_worker_memory: typing.Optional[jsii.Number] = None,
    lambda_queue_worker_timeout: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    sqs_batch: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bee1af2a47305e4c9ebfebed25bdaac56fb710fc8a1b14681164986c9f8ca72(
    parent: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    s3_pdf_bucket: typing.Optional[builtins.str] = None,
    s3_textract_output_bucket: typing.Optional[builtins.str] = None,
    searchable_pdf_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae7a44b85c05636dbf0a4aa69c117d4b60d7a954fffcb44dd0fbe1731cf57f2(
    *,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    s3_pdf_bucket: typing.Optional[builtins.str] = None,
    s3_textract_output_bucket: typing.Optional[builtins.str] = None,
    searchable_pdf_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e5b2dacdc4ccbbe289c86d0b2e0642e892f6433b39ce58a6fe48e2acbfb4a8e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    docker_image_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    spacy_image_ecr_repository: typing.Optional[builtins.str] = None,
    spacy_lambda_memory_size: typing.Optional[jsii.Number] = None,
    spacy_lambda_timeout: typing.Optional[jsii.Number] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__694ee94304833a6e79e0bca7303386b8e4b72111e85d28fb732057fccdc02f5f(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__486073f1dec452daea44ef35232ecb1bdf7e6e23a70a2336ba8c26cad08bf1f0(
    value: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f6940a72f68db11a722462d4039aae3cc0d0c73a3bdc0512708985818b03db6(
    value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79fefaf82c5d3331c016b89cabf1b700e769e8cb4f83b41120b7f5339726ad97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cba57b66cbd6ce930f6c12b56fbeabe9ee122bff2d8ff1e1dd3cf8b2690b030(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    docker_image_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    spacy_image_ecr_repository: typing.Optional[builtins.str] = None,
    spacy_lambda_memory_size: typing.Optional[jsii.Number] = None,
    spacy_lambda_timeout: typing.Optional[jsii.Number] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b619aa6ebc30523ed1a4ede0dfa4561c736eb234c6188bc16548c755316455d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    a2i_flow_definition_arn: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    task_token_table_name: typing.Optional[builtins.str] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa58e1037670bf6f865151ae14fde4c506c8ccf219add886163ff1fd4c71a464(
    value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f20e147bf1435d6fec1136f1d29571486028bb565306d3a7fa0cfa3ad0dc019(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95c2ce188159df7952fbe555a47ef65ca727b36556032e46955433afe4d997bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c11975a42fb4b6f10d693ecf8270e21a942db5cb5a69941787b5d4eb22ca9d44(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    a2i_flow_definition_arn: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    task_token_table_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ca9c772465c2593ed244c3a9755826188394e55f282b0e1d0ea6cea4a252570(
    parent: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_async_to_json_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_async_to_json_interval: typing.Optional[jsii.Number] = None,
    textract_async_to_json_max_retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a96e92b6b9d91c2e42618fd44ea1b0a731077a9db0fe8c4b847bf04d39dbe894(
    *,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_async_to_json_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_async_to_json_interval: typing.Optional[jsii.Number] = None,
    textract_async_to_json_max_retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25e3098f5f1cf53a1843a288e473d473e85d772bf36df6560bffd0f7ca9d1528(
    parent: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    configuration_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14bb9f79ce4a3987ca802dd759cf4ce888e01e2282bd21bfb687c194eec36f7d(
    value: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc36ab1233aeb7ad48805b89b5a7969522727c77067e66de6339fc76f860d2d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48258c75c526b12e23a7d55d57df1574bfca1d4360d960d366340dff2ffc7907(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9730bcbe8d0810f0bc796cfc253d01edd04d3221100a5d22f84b45392f047fd(
    *,
    configuration_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fde0d8094bf4d559fa73876939c7216338ab9dc4ae355b97c25febd9cefec07(
    *,
    decider_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_decider_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_decider_interval: typing.Optional[jsii.Number] = None,
    textract_decider_max_retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c4862082059a8d5b6466d4d265f04eb4cba355498d58e92495f8fa815a1e1c0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    csv_s3_output_bucket: builtins.str,
    csv_s3_output_prefix: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    meta_data_to_append: typing.Optional[typing.Sequence[builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    opensearch_index_name: typing.Optional[builtins.str] = None,
    output_features: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    output_type: typing.Optional[builtins.str] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_generate_csv_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_generate_csv_interval: typing.Optional[jsii.Number] = None,
    textract_generate_csv_max_retries: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88a2676af3df102bdf86aca83a7162535d7aa9e7ece1b68f9ac7152fedfc6a6(
    value: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__724c205c78f00a297bd85ee70d9f29988a55704db03e156b18a7a13ce1ecc72c(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    csv_s3_output_bucket: builtins.str,
    csv_s3_output_prefix: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    meta_data_to_append: typing.Optional[typing.Sequence[builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    opensearch_index_name: typing.Optional[builtins.str] = None,
    output_features: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    output_type: typing.Optional[builtins.str] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_generate_csv_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_generate_csv_interval: typing.Optional[jsii.Number] = None,
    textract_generate_csv_max_retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__777a9f850c82400b30b8e4947eac2c7b86afcc5422d945e75c147efa4878c28e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    s3_output_bucket: builtins.str,
    s3_temp_output_prefix: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    sns_role_textract: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    task_token_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_async_call_interval: typing.Optional[jsii.Number] = None,
    textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fdd037482db6dad099fdb4505606fea0c969958d0feece9a69c6eb96796920e(
    value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd254ba32e5db6444c5a43b8c83cca7782f63802da3e5b0f6824799b49010e8(
    value: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31e881ad8384afc6bb5da8beed6c0c1b616b6eac541ef8d1e8da53d28c675d93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb980df2a3ad4a409aa2e44833e1eeef93d5ca29d42b0e32b7463cebafb3bb61(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41cb1f9f496a6dba7a042c5ccde0e5a642d141e9be2a1db69458f90db745e9c3(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__487b99befc7ec29928dda710f001ea11e64934a8d8053719a118bf80981fb983(
    value: _aws_cdk_aws_sns_ceddda9d.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2deb75ba6cf3eec0b097f8e1a52e2f9374c89716f54e4360f581caa0c2d146(
    value: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33fb9b71b4c990d8b5382a06849fbf30c26f40b0c0955ff9256a001a5955440f(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f58ab12489357f5450bbfca9fe4badfee9dba50c0413209829be946d81a555fd(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef6a0a91d67a04217b9c2cc84fa1e0ef0a5bdc6eee9944b8440c5dd8ef8c003b(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b143769254733f3758938b4f5b564339ad262dc9427348e3a279ace88d90b66(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c16fb3ebb6242918219104d7eaf0d0cd1a95614836e825ce2f92b78295acc52(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf0a1ee3eabc4d2e34f6b30eed569fa4d7a25f8fac3e5cc78c5528b8c8b987ca(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bdfa5466a8208501dedc1e21f41ec52737b86fcaa1624267285219b717903b3(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    s3_output_bucket: builtins.str,
    s3_temp_output_prefix: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    sns_role_textract: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    task_token_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.ITable] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_async_call_interval: typing.Optional[jsii.Number] = None,
    textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__793a5ab15766407e031c419bf4d089e96abc4421156ef15e7f9749ffc4086ed8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    custom_function: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke] = None,
    enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
    enable_dashboard: typing.Optional[builtins.bool] = None,
    enable_monitoring: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_async_call_interval: typing.Optional[jsii.Number] = None,
    textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d06e25702bc2c6c8d8a28658e7429243b5032768a8390aaf26934a31686d4c33(
    value: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d969ae74a43dd83502fa61354c655c16adbc642b29c354ccbe80b25e726e43f(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3bc7f11cb150a5e48113ccb8ab4ffee26b93135122b42b7659d7815bfe5fb51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33f7ad694796670888d8e3799055c1c911f916b7daafb1be179e59c404606951(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c158f5aaa93987354325b0f60702bc529c5de9900d3614a00496ffb4e6f9ba(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9c063defca0576885ada84ec2819cb5f6043237d1e74c254edb157fee0644b9(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b9af5e300c69cc6ec26b6862b39ad25743dc40cb36bed281a48779068fc674b(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4d6df050846f4b04d077141bc7412b5ebde87938736d06fd540eb22a4b968eb(
    *,
    comment: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.Credentials, typing.Dict[builtins.str, typing.Any]]] = None,
    heartbeat: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    heartbeat_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    state_name: typing.Optional[builtins.str] = None,
    task_timeout: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.Timeout] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    associate_with_parent: typing.Optional[builtins.bool] = None,
    custom_function: typing.Optional[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke] = None,
    enable_cloud_watch_metrics_and_dashboard: typing.Optional[builtins.bool] = None,
    enable_dashboard: typing.Optional[builtins.bool] = None,
    enable_monitoring: typing.Optional[builtins.bool] = None,
    input: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.TaskInput] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_api: typing.Optional[builtins.str] = None,
    textract_async_call_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_async_call_interval: typing.Optional[jsii.Number] = None,
    textract_async_call_max_retries: typing.Optional[jsii.Number] = None,
    textract_state_machine_timeout_minutes: typing.Optional[jsii.Number] = None,
    workflow_tracing_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c04b9c5783206479fa4562fd8f4e84d755f71078456005bb09f27ece829a4a84(
    parent: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    decider_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
    textract_decider_backoff_rate: typing.Optional[jsii.Number] = None,
    textract_decider_interval: typing.Optional[jsii.Number] = None,
    textract_decider_max_retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24c2f438d42a1aebdfcfb2b07fe3b28b4071efa2c5d7cbe613542f0023e206b9(
    parent: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    healthlake_endpoint: typing.Optional[builtins.str] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    pdf_mapper_for_fhir_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aafa2ff073995cbd086e64592fa34d573e4d22cd94a183aff3a791bdbb73ba92(
    *,
    healthlake_endpoint: typing.Optional[builtins.str] = None,
    input_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    lambda_log_level: typing.Optional[builtins.str] = None,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
    pdf_mapper_for_fhir_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    s3_input_bucket: typing.Optional[builtins.str] = None,
    s3_input_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc9009b1e4be5967e6cd482a979819174535fbac2849b1d7b4b3ebc2abcc58a5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    workmail_account_number: builtins.str,
    workmail_region: builtins.str,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55ee8bdcaeb142cce00840207986a2edbec46183c1b520e5570c9e838b2138e9(
    *,
    s3_output_bucket: builtins.str,
    s3_output_prefix: builtins.str,
    workmail_account_number: builtins.str,
    workmail_region: builtins.str,
    lambda_memory_mb: typing.Optional[jsii.Number] = None,
    lambda_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

'''
# S3DataCopy

Data copy from one bucket to another during deployment time.

## Overview

`S3DataCopy` construct provides a process to copy objects from one bucket to another during CDK deployment time:

* The copy is part of the CDK and CloudFormation deployment process. It's using a synchronous CDK Custom Resource running on AWS Lambda.
* The Lambda function is written in Typescript and copies objects between source and target buckets.
* The execution role used by the Lambda function is scoped to the least privileges. A custom role can be provided.
* The Lambda function can be executed in an Amazon VPC within private subnets. By default, it runs run inside VPCs owned by the AWS Lambda service.
* The Lambda function is granted read access on the source bucket and write access on the destination bucket using the execution role policy. The construct doesn't grant cross account access.

![S3 Data Copy](../../../website/static/img/s3-data-copy.png)

## Usage

```python
class ExampleDefaultS3DataCopyStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        source_bucket = Bucket.from_bucket_name(self, "sourceBucket", "nyc-tlc")
        target_bucket = Bucket.from_bucket_name(self, "destinationBucket", "staging-bucket")

        dsf.utils.S3DataCopy(self, "S3DataCopy",
            source_bucket=source_bucket,
            source_bucket_prefix="trip data/",
            source_bucket_region="us-east-1",
            target_bucket=target_bucket,
            target_bucket_prefix="staging-data/"
        )
```

## Private networks

The lambda Function used by the custom resource can be deployed in a VPC by passing the VPC and a list of private subnets.

Public subnets are not supported.

```python
vpc = Vpc.from_lookup(self, "Vpc", vpc_name="my-vpc")
subnets = vpc.select_subnets(subnet_type=SubnetType.PRIVATE_WITH_EGRESS)

dsf.utils.S3DataCopy(self, "S3DataCopy",
    source_bucket=source_bucket,
    source_bucket_prefix="trip data/",
    source_bucket_region="us-east-1",
    target_bucket=target_bucket,
    target_bucket_prefix="staging-data/",
    vpc=vpc,
    subnets=subnets
)
```

# DataVpc

Amazon VPC optimized for data solutions.

## Overview

`DataVpc` construct provides a standard Amazon VPC with best practices for security and data solutions implementations:

* The VPC is created with public and private subnets across 3 availability zones (1 of each per AZ) and 3 NAT gateways.
* VPC CIDR mask should be larger than 28. The CIDR is split between public and private subnets with private subnets being twice as large as public subnet.
* The flow logs maaged by a dedicated least-privilege IAM Role. The role can be customized.
* The flow logs exported to an Amazon CloudWatch LogGroup encrypted with an Amazon KMS customer managed key. The KMS key can be customized.
* A gateway VPC endpoint is created for S3 access.

## Usage

```python
class ExampleDefaultDataVpcStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        dsf.utils.DataVpc(self, "MyDataVpc",
            vpc_cidr="10.0.0.0/16"
        )
```

## VPC Flow Logs

The construct logs VPC Flow logs in a Cloudwatch Log Group that is encrypted with a customer managed KMS Key. Exporting VPC Flow Logs to CloudWatch requires an IAM Role.
You can customize the VPC Flow Logs management with:

* your own KMS Key. Be sure to attach the right permissions to your key.
  Refer to the [AWS documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/encrypt-log-data-kms.html) for full description.
* your own IAM Role. Be sure to configure the proper trust policy and permissions. Refer to the [AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html#flow-logs-iam-role) for full description.
* a custom log retention policy. Default is one week.

```python
flow_log_key = Key.from_key_arn(self, "FlowLogKey", "XXXXXXXXXXXXXXXXXXXXXXXX")

flow_log_role = Role.from_role_arn(self, "FlowLogRole", "XXXXXXXXXXXXXXXXXXXXXXXX")

dsf.utils.DataVpc(self, "MyDataVpc",
    vpc_cidr="10.0.0.0/16",
    flow_log_key=flow_log_key,
    flow_log_role=flow_log_role,
    flow_log_retention=RetentionDays.TWO_WEEKS
)
```

## Removal policy

You can specify if the Cloudwatch Log Group and the KMS encryption Key should be deleted when the CDK resource is destroyed using `removalPolicy`. To have an additional layer of protection, we require users to set a global context value for data removal in their CDK applications.

Log group and encryption key can be destroyed when the CDK resource is destroyed only if **both** data vpc removal policy and DSF on AWS global removal policy are set to remove objects.

You can set `@data-solutions-framework-on-aws/removeDataOnDestroy` (`true` or `false`) global data removal policy in `cdk.json`:

```json
{
  "context": {
    "@data-solutions-framework-on-aws/removeDataOnDestroy": true
  }
}
```

Or programmatically in your CDK app:

```python
# Set context value for global data removal policy
self.node.set_context("@data-solutions-framework-on-aws/removeDataOnDestroy", True)

dsf.utils.DataVpc(self, "MyDataVpc",
    vpc_cidr="10.0.0.0/16",
    removal_policy=RemovalPolicy.DESTROY
)
```

## Client VPN Endpoint

You can add client VPN endpoint to the DataVpc. Current impelementation supports SAML based authentication only and requires SSL certificate created in Amazon Certificate Manager.

If you don't have an SSL certificate, you can follow this [workshop lab](https://catalog.us-east-1.prod.workshops.aws/workshops/d903ff2b-f043-4126-a4f5-64a7cc2922ec/en-US/3-aws-client-vpn/1-rsacertificatecreation) to generate a self-signed certificate and import it into Amazon Certificate Manager.

Refer to the [documentation](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/federated-authentication.html) on setting up SAML federated authentication. If you don't currently use any IdP, we suggest AWS IAM Identity Center that can also be used with other DSF constructs, such as OpenSearch construct.

```python
class ExampleDefaultDataVpcStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        dsf.utils.DataVpc(self, "MyDataVpc",
            vpc_cidr="10.0.0.0/16",
            client_vpn_endpoint_props=dsf.utils.DataVpcClientVpnEndpointProps(
                server_certificate_arn="arn:aws:acm:us-east-1:XXXXXXXX:certificate/XXXXXXXXXX",
                saml_metadata_document="""<?xml version="1.0" encoding="UTF-8"?><md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="https://portal.sso.us-east-1.amazonaws.com/saml/assertion/XXXXXXXXXXXXXX">
                          <md:IDPSSODescriptor WantAuthnRequestsSigned="false" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
                            <md:KeyDescriptor use="signing">
                              <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
                                <ds:X509Data>
                                  <ds:X509Certificate>XXXXXXXXXXXXXXXXXXXXXXXXX</ds:X509Certificate>
                                </ds:X509Data>
                              </ds:KeyInfo>
                            </md:KeyDescriptor>
                            <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://portal.sso.us-east-1.amazonaws.com/saml/logout/XXXXXXXXXXXXXX"/>
                            <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://portal.sso.us-east-1.amazonaws.com/saml/logout/XXXXXXXXXXXXXX"/>
                            <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
                            <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://portal.sso.us-east-1.amazonaws.com/saml/assertion/XXXXXXXXXXXXXX"/>
                            <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://portal.sso.us-east-1.amazonaws.com/saml/assertion/XXXXXXXXXXXXXX"/>
                          </md:IDPSSODescriptor>
                        </md:EntityDescriptor>""",
                self_service_portal=False
            )
        )
```

# Customize DSF on AWS constructs

You can customize DSF on AWS constructs in several ways to adapt to your specific needs:

1. Use the Constructs properties instead of the smart defaults.
2. Extend existing constructs and override specific methods or properties.
3. Access CDK L1 resources and override any property.

## Constructs properties

Use the properties of the construct to adapt the behavior to your needs. With this approach, you bypass the smart defaults provided by the construct.
Refer to the documentation of each construct to evaluate if your requirements can be implemented.

:::note
This method should always be preferred because constructs properties are tested as part of the DSF on AWS build process.
:::

For example, you can use the `DataLakeStorage` properties to modify the lifecycle configurations for transitioning objects based on your needs instead of using the default rules:

```python
dsf.storage.DataLakeStorage(self, "MyDataLakeStorage",
    bronze_bucket_infrequent_access_delay=90,
    bronze_bucket_archive_delay=180,
    silver_bucket_infrequent_access_delay=180,
    silver_bucket_archive_delay=360,
    gold_bucket_infrequent_access_delay=180,
    gold_bucket_archive_delay=360
)
```

## Construct extension

AWS CDK allows developers to extend classes like any object-oriented programing language. You can use this method when you want to:

* Override a specific method exposed by a construct.
* Implement your own defaults. Refer to the example of the [`AnalyticsBucket`](https://github.com/awslabs/data-solutions-framework-on-aws/blob/main/framework/src/storage/analytics-bucket.ts) that extends the CDK L2 `Bucket` construct to enforce some of the parameters.

## CDK resources override

AWS CDK offers escape hatches to modify constructs that are encapsulated in DSF on AWS constructs. The constructs always expose the AWS resources that are encapsulated so you can manually modify their configuration. For achieving this you have 3 options:

* Modify the L2 construct using its CDK API. For example, you can modify the buckets' policies provided by the [`DataLakeStorage`](https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/data-lake-storage) to provide cross account write access. All the [buckets](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.Bucket.html) L2 constructs are exposed as an object parameter:

```python
# Create a data lake using DSF on AWS L3 construct
storage = dsf.storage.DataLakeStorage(self, "MyDataLakeStorage")

# Access the CDK L2 Bucket construct exposed by the L3 construct
gold_bucket = storage.gold_bucket

# Use the Bucket CDK API to modify the Bucket Policy and add cross account write access
gold_bucket.add_to_resource_policy(aws_iam.PolicyStatement(
    actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucketMultipartUploads", "s3:ListMultipartUploadParts", "s3:AbortMultipartUpload", "s3:ListBucket"
    ],
    effect=aws_iam.Effect.ALLOW,
    principals=[aws_iam.AccountPrincipal("123456789012")]
))
```

* [Modify the L1 construct resource](https://docs.aws.amazon.com/cdk/v2/guide/cfn_layer.html#cfn_layer_resource) when there is a CDK property available on the L1 construct.
  For example, you can override CDK L1 property for setting the S3 transfer Acceleration on the gold bucket of the `DataLakeStorage`:

```python
# Create a data lake using DSF on AWS L3 construct
storage = dsf.storage.DataLakeStorage(self, "MyDataLakeStorage")

# Access the CDK L1 Bucket construct exposed by the L3 construct
cfn_bucket = storage.gold_bucket.node.default_child

# Override the CDK L1 property for transfer acceleration
cfn_bucket.accelerate_configuration = CfnBucket.AccelerateConfigurationProperty(
    acceleration_status="Enabled"
)
```

* [Override the CloudFormation properties](https://docs.aws.amazon.com/cdk/v2/guide/cfn_layer.html#cfn_layer_raw) when there isn't any CDK property, and you need to modify the CFN template directly.
  For example, you can override CloudFormation property for setting the S3 transfer Acceleration on the gold bucket of the `DataLakeStorage`:

```python
# Create a data lake using DSF on AWS L3 construct
storage = dsf.storage.DataLakeStorage(self, "MyDataLakeStorage")

# Access the CDK L1 Bucket construct exposed by the L3 construct
cfn_bucket = storage.gold_bucket.node.default_child

# Override the CloudFormation property for transfer acceleration
cfn_bucket.add_override("Properties.AccelerateConfiguration.AccelerationStatus", "Enabled")
```

# Create custom resources with the DsfProvider

DSF provides an internal construct named `DsfProvider` to facilitate the creation of custom resources in DSF constructs.
The `DsfProvider` construct handles the undifferentiated tasks for you so you can focus on the custom resource logic.
This construct is an opinionated implementation of the [CDK Custom Resource Provider Framework](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib-readme.html#the-custom-resource-provider-framework).
It creates:

* A custom resource provider to manage the entire custom resource lifecycle
* An onEvent Lambda function from the provided code to perform actions you need in your custom resource
* An optional isComplete Lambda function from the provided code when using [asynchronous custom resources](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.custom_resources-readme.html#asynchronous-providers-iscomplete)
* The `onEvent` and `isComplete `Lambda functions are scoped down through a resource policy to be invoked only by the `Provider`.
* CloudWatch Logs log groups for each Lambda function
* IAM roles for each Lambda function and associated permissions

:::note
You still need to provide an IAM Managed Policy required by the actions of the Lambda functions.
:::

## Configuring handlers for the custom resource

The `DsfProvider` construct requires a Lambda function handler called `onEvent` to perform the actions of the custom resource. It also supports an optional Lambda function handler called `isComplete` to regularly perform status checks for asynchronous operation triggered in the `onEvent` handler.

Both Lambda functions are implemented in Typescript.
`esbuild` is used to package the Lambda code and is automatically installed by `Projen`. If `esbuild` is available, `docker` will be used.
You need to configure the path of the Lambda code (entry file) and the path of the dependency lock file (`package-lock.json`) for each handler.

To generate the `package-lock.json` file, run from the Lambda code folder:

```bash
npm install --package-lock-only
```

Then you can configure the `onEvent` and `isComplete` handlers in the `DsfProvider` construct:

```python
from ...lib.dsf_provider import DsfProvider

cdk.Stack):
scope, id):
super().__init__(scope, id)my_provider = DsfProvider(self, "Provider",
    provider_name="my-provider",
    on_event_handler_definition=HandlerDefinition(
        managed_policy=my_on_event_managed_policy,
        handler="on-event.handler",
        deps_lock_file_path=path.join(__dirname, "./resources/lambda/my-cr/package-lock.json"),
        entry_file=path.join(__dirname, "./resources/lambda/my-cr/on-event.mjs")
    ),
    is_complete_handler_definition=HandlerDefinition(
        managed_policy=my_is_complete_managed_policy,
        handler="is-complete.handler",
        deps_lock_file_path=path.join(__dirname, "./resources/lambda/my-cr/package-lock.json"),
        entry_file=path.join(__dirname, "./resources/lambda/my-cr/is-complete.mjs")
    )
)

cdk.CustomResource(self, "CustomResource",
    service_token=my_provider.service_token,
    resource_type="Custom::MyCustomResource"
)
```

## Packaging dependencies in the Lambda function

Dependencies can be added to the Lambda handlers using the bundling options. For example, the following code adds the AWS SDK S3 client to the `onEvent` handler:

```python
my_provider = DsfProvider(self, "Provider",
    provider_name="my-provider",
    on_event_handler_definition=HandlerDefinition(
        managed_policy=my_managed_policy,
        handler="on-event.handler",
        deps_lock_file_path=path.join(__dirname, "./resources/lambda/my-cr/package-lock.json"),
        entry_file=path.join(__dirname, "./resources/lambda/my-cr/on-event.mjs"),
        bundling=cdk.aws_lambda_nodejs.BundlingOptions(
            node_modules=["@aws-sdk/client-s3"
            ],
            command_hooks={
                "after_bundling": () => [],
                "before_bundling": () => [
                              'npx esbuild --version'
                            ],
                "before_install": () => [
                            ]
            }
        )
    )
)
```

## Running the Custom Resource in VPC

You can configure the `DsfProvider` to run all the Lambda functions within a VPC (for example in private subnets). It includes the Lambda handlers (`onEvent` and `isComplete`) and the Lambda functions used by the custom resource framework. The following configurations are available when running the custom resource in a VPC:

* The VPC where you want to run the custom resource.
* The subnets where you want to run the Lambda functions. Subnets are optional. If not configured, the construct uses the VPC default strategy to select subnets.
* The EC2 security groups to attach to the Lambda functions. Security groups are optional. If not configured, a single security group is created for all the Lambda functions.

:::danger
The `DsfProvider` construct implements a custom process to efficiently clean up ENIs when deleting the custom resource. Without this process it can take up to one hour to delete the ENI and dependant resources.
This process requires the security groups to be dedicated to the custom resource. If you configure security groups, ensure they are dedicated.
:::

```python
vpc = Vpc.from_lookup(self, "Vpc", vpc_name="my-vpc")
subnets = vpc.select_subnets(subnet_type=SubnetType.PRIVATE_WITH_EGRESS)
security_group = SecurityGroup.from_security_group_id(self, "SecurityGroup", "sg-123456")

my_provider = DsfProvider(self, "Provider",
    provider_name="my-provider",
    on_event_handler_definition=HandlerDefinition(
        managed_policy=my_managed_policy,
        handler="on-event.handler",
        deps_lock_file_path=path.join(__dirname, "./resources/lambda/my-cr/package-lock.json"),
        entry_file=path.join(__dirname, "./resources/lambda/my-cr/on-event.mjs")
    ),
    vpc=vpc,
    subnets=subnets,
    # the security group should be dedicated to the custom resource
    security_groups=[security_group]
)
```

## Configuring environment variables of Lambda handlers

Lambda handlers can leverage environment variables to pass values to the Lambda code. You can configure environment variables for each of the Lambda handlers:

```python
my_provider = DsfProvider(self, "Provider",
    provider_name="my-provider",
    on_event_handler_definition=HandlerDefinition(
        managed_policy=my_managed_policy,
        handler="on-event.handler",
        deps_lock_file_path=path.join(__dirname, "./resources/lambda/my-cr/package-lock.json"),
        entry_file=path.join(__dirname, "./resources/lambda/my-cr/on-event.mjs"),
        environment={
            "MY_ENV_VARIABLE": "my-env-variable-value"
        }
    )
)
```

## Removal policy

You can specify if the Cloudwatch Log Groups should be deleted when the CDK resource is destroyed using `removalPolicy`. To have an additional layer of protection, we require users to set a global context value for data removal in their CDK applications.

Log groups can be destroyed when the CDK resource is destroyed only if **both** `DsfProvider` removal policy and DSF on AWS global removal policy are set to remove objects.

You can set `@data-solutions-framework-on-aws/removeDataOnDestroy` (`true` or `false`) global data removal policy in `cdk.json`:

```json
{
  "context": {
    "@data-solutions-framework-on-aws/removeDataOnDestroy": true
  }
}
```

Or programmatically in your CDK app:

```python
self.node.set_context("@data-solutions-framework-on-aws/removeDataOnDestroy", True)

my_provider = DsfProvider(self, "Provider",
    provider_name="my-provider",
    on_event_handler_definition=HandlerDefinition(
        managed_policy=my_on_event_managed_policy,
        handler="on-event.handler",
        deps_lock_file_path=path.join(__dirname, "./resources/lambda/my-cr/package-lock.json"),
        entry_file=path.join(__dirname, "./resources/lambda/my-cr/on-event.mjs")
    ),
    removal_policy=cdk.RemovalPolicy.DESTROY
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

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class ApplicationStackFactory(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.ApplicationStackFactory",
):
    '''Abstract class that needs to be implemented to pass the application Stack to the CICD pipeline.

    :exampleMetadata: fixture=imports-only

    Example::

        class MyApplicationStack(cdk.Stack):
            def __init__(self, scope, id, *, stage, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None, crossRegionReferences=None, permissionsBoundary=None, suppressTemplateIndentation=None):
                super().__init__(scope, id, stage=stage, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting, crossRegionReferences=crossRegionReferences, permissionsBoundary=permissionsBoundary, suppressTemplateIndentation=suppressTemplateIndentation)
        
        class MyApplicationStackFactory(dsf.utils.ApplicationStackFactory):
            def create_stack(self, scope, stage):
                return MyApplicationStack(scope, "MyApplication",
                    stage=stage
                )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="createStack")
    @abc.abstractmethod
    def create_stack(
        self,
        scope: _constructs_77d1e7e8.Construct,
        stage: "CICDStage",
    ) -> _aws_cdk_ceddda9d.Stack:
        '''Abstract method that needs to be implemented to return the application Stack.

        :param scope: The scope to create the stack in.
        :param stage: The stage of the pipeline.
        '''
        ...


class _ApplicationStackFactoryProxy(ApplicationStackFactory):
    @jsii.member(jsii_name="createStack")
    def create_stack(
        self,
        scope: _constructs_77d1e7e8.Construct,
        stage: "CICDStage",
    ) -> _aws_cdk_ceddda9d.Stack:
        '''Abstract method that needs to be implemented to return the application Stack.

        :param scope: The scope to create the stack in.
        :param stage: The stage of the pipeline.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eef9172971b514785a6ce2346308753b3a0e87079b7ff4a145e5bb81378146a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.invoke(self, "createStack", [scope, stage]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ApplicationStackFactory).__jsii_proxy_class__ = lambda : _ApplicationStackFactoryProxy


class ApplicationStage(
    _aws_cdk_ceddda9d.Stage,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.ApplicationStage",
):
    '''ApplicationStage class that creates a CDK Pipelines Stage from an ApplicationStackFactory.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_stack_factory: ApplicationStackFactory,
        stage: "CICDStage",
        outputs_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Construct a new instance of the SparkCICDStage class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param application_stack_factory: The application CDK Stack Factory used to create application Stacks.
        :param stage: The Stage to deploy the application CDK Stack in. Default: - No stage is passed to the application stack
        :param outputs_env: The list of values to create CfnOutputs. Default: - No CfnOutputs are created
        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b5ac3de86725230614eaa05d4d588181e4795f348801b8e9846f7a8ade6698)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApplicationStageProps(
            application_stack_factory=application_stack_factory,
            stage=stage,
            outputs_env=outputs_env,
            env=env,
            outdir=outdir,
            permissions_boundary=permissions_boundary,
            policy_validation_beta1=policy_validation_beta1,
            stage_name=stage_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="stackOutputsEnv")
    def stack_outputs_env(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.CfnOutput]]:
        '''The list of CfnOutputs created by the CDK Stack.'''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.CfnOutput]], jsii.get(self, "stackOutputsEnv"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.ApplicationStageProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StageProps],
    name_mapping={
        "env": "env",
        "outdir": "outdir",
        "permissions_boundary": "permissionsBoundary",
        "policy_validation_beta1": "policyValidationBeta1",
        "stage_name": "stageName",
        "application_stack_factory": "applicationStackFactory",
        "stage": "stage",
        "outputs_env": "outputsEnv",
    },
)
class ApplicationStageProps(_aws_cdk_ceddda9d.StageProps):
    def __init__(
        self,
        *,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
        application_stack_factory: ApplicationStackFactory,
        stage: "CICDStage",
        outputs_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Properties for the ``ApplicationStage`` class.

        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        :param application_stack_factory: The application CDK Stack Factory used to create application Stacks.
        :param stage: The Stage to deploy the application CDK Stack in. Default: - No stage is passed to the application stack
        :param outputs_env: The list of values to create CfnOutputs. Default: - No CfnOutputs are created
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d0cd7bb2c6f89ceae419e95586371f2db805a9f35f0aa2ec97dcf48aa8c0209)
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument policy_validation_beta1", value=policy_validation_beta1, expected_type=type_hints["policy_validation_beta1"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument application_stack_factory", value=application_stack_factory, expected_type=type_hints["application_stack_factory"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument outputs_env", value=outputs_env, expected_type=type_hints["outputs_env"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_stack_factory": application_stack_factory,
            "stage": stage,
        }
        if env is not None:
            self._values["env"] = env
        if outdir is not None:
            self._values["outdir"] = outdir
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if policy_validation_beta1 is not None:
            self._values["policy_validation_beta1"] = policy_validation_beta1
        if stage_name is not None:
            self._values["stage_name"] = stage_name
        if outputs_env is not None:
            self._values["outputs_env"] = outputs_env

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''Default AWS environment (account/region) for ``Stack``s in this ``Stage``.

        Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing
        from its env will use the corresponding field given here.

        If either ``region`` or ``account``is is not configured for ``Stack`` (either on
        the ``Stack`` itself or on the containing ``Stage``), the Stack will be
        *environment-agnostic*.

        Environment-agnostic stacks can be deployed to any environment, may not be
        able to take advantage of all features of the CDK. For example, they will
        not be able to use environmental context lookups, will not automatically
        translate Service Principals to the right format based on the environment's
        AWS partition, and other such enhancements.

        :default: - The environments should be configured on the ``Stack``s.

        Example::

            // Use a concrete account and region to deploy this Stage to
            new Stage(app, 'Stage1', {
              env: { account: '123456789012', region: 'us-east-1' },
            });
            
            // Use the CLI's current credentials to determine the target environment
            new Stage(app, 'Stage2', {
              env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
            });
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''The output directory into which to emit synthesized artifacts.

        Can only be specified if this stage is the root stage (the app). If this is
        specified and this stage is nested within another stage, an error will be
        thrown.

        :default:

        - for nested stages, outdir will be determined as a relative
        directory to the outdir of the app. For apps, if outdir is not specified, a
        temporary directory will be created.
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def policy_validation_beta1(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]]:
        '''Validation plugins to run during synthesis.

        If any plugin reports any violation,
        synthesis will be interrupted and the report displayed to the user.

        :default: - no validation plugins are used
        '''
        result = self._values.get("policy_validation_beta1")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Name of this stage.

        :default: - Derived from the id.
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_stack_factory(self) -> ApplicationStackFactory:
        '''The application CDK Stack Factory used to create application Stacks.'''
        result = self._values.get("application_stack_factory")
        assert result is not None, "Required property 'application_stack_factory' is missing"
        return typing.cast(ApplicationStackFactory, result)

    @builtins.property
    def stage(self) -> "CICDStage":
        '''The Stage to deploy the application CDK Stack in.

        :default: - No stage is passed to the application stack
        '''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast("CICDStage", result)

    @builtins.property
    def outputs_env(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The list of values to create CfnOutputs.

        :default: - No CfnOutputs are created
        '''
        result = self._values.get("outputs_env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.utils.Architecture")
class Architecture(enum.Enum):
    '''List of supported CPU architecture, either  X86_64 or ARM64.'''

    X86_64 = "X86_64"
    ARM64 = "ARM64"


class BucketUtils(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.BucketUtils",
):
    '''Utils for working with Amazon S3 Buckets.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="generateUniqueBucketName")
    @builtins.classmethod
    def generate_unique_bucket_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> builtins.str:
        '''Generate a unique Amazon S3 bucket name based on the provided name, CDK construct ID and CDK construct scope.

        The bucket name is suffixed the AWS account ID, the AWS region and a unique 8 characters hash.
        The maximum length for name is 26 characters.

        :param scope: the current scope where the construct is created (generally ``this``).
        :param id: the CDK ID of the construct.
        :param name: the name of the bucket.

        :return: the unique Name for the bucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88bcefb5e5ed5389168d4178ba329d512cd1938b816b8cfe7bc44a5b3124986f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "generateUniqueBucketName", [scope, id, name]))


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.utils.CICDStage")
class CICDStage(enum.Enum):
    '''The list of CICD Stages used in CICD Pipelines.'''

    STAGING = "STAGING"
    PROD = "PROD"


class DataVpc(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.DataVpc",
):
    '''Creates a VPC with best practices for securely deploying data solutions.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Utils/data-vpc

    Example::

        vpc = dsf.utils.DataVpc(self, "DataVpc",
            vpc_cidr="10.0.0.0/16"
        )
        
        vpc.tag_vpc("Name", "My VPC")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc_cidr: builtins.str,
        client_vpn_endpoint_props: typing.Optional[typing.Union["DataVpcClientVpnEndpointProps", typing.Dict[builtins.str, typing.Any]]] = None,
        flow_log_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        flow_log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        flow_log_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc_cidr: The CIDR to use to create the subnets in the VPC.
        :param client_vpn_endpoint_props: ClientVpnEndpoint propertioes. Required if client vpn endpoint is needed Default: None
        :param flow_log_key: The KMS key used to encrypt the VPC Flow Logs in the CloudWatch Log Group. The resource policy of the key must be configured according to the AWS documentation. Default: - A new KMS key is created
        :param flow_log_retention: The retention period to apply to VPC Flow Logs. Default: - One week retention
        :param flow_log_role: The IAM Role used to send the VPC Flow Logs in CloudWatch. The role must be configured as described in the AWS VPC Flow Log documentation. Default: - A new IAM role is created
        :param nat_gateways: Number of NAT Gateways. Default: 3 or the AZs defined in the context
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9563cd6cefb38ed980d4672a429ac3bfb7e0fdf90feea5a4f416b4ff13b018a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataVpcProps(
            vpc_cidr=vpc_cidr,
            client_vpn_endpoint_props=client_vpn_endpoint_props,
            flow_log_key=flow_log_key,
            flow_log_retention=flow_log_retention,
            flow_log_role=flow_log_role,
            nat_gateways=nat_gateways,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="tagVpc")
    def tag_vpc(self, key: builtins.str, value: builtins.str) -> None:
        '''Tag the VPC and the subnets.

        :param key: the tag key.
        :param value: the tag value.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__006cefc76fdc1dca834321b036a66ceab95669c6f8f2eb4389a95b6405c5ca3a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "tagVpc", [key, value]))

    @builtins.property
    @jsii.member(jsii_name="flowLogGroup")
    def flow_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group created for the VPC flow logs.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "flowLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="flowLogKey")
    def flow_log_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS Key used to encrypt VPC flow logs.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "flowLogKey"))

    @builtins.property
    @jsii.member(jsii_name="flowLogRole")
    def flow_log_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM role used to publish VPC Flow Logs.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "flowLogRole"))

    @builtins.property
    @jsii.member(jsii_name="s3VpcEndpoint")
    def s3_vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.IGatewayVpcEndpoint:
        '''The S3 VPC endpoint gateway.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IGatewayVpcEndpoint, jsii.get(self, "s3VpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The amazon VPC created.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="clientVpnEndpoint")
    def client_vpn_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ClientVpnEndpoint]:
        '''The Client VPN Endpoint.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ClientVpnEndpoint], jsii.get(self, "clientVpnEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="vpnLogGroup")
    def vpn_log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The log group for Client VPN Endpoint.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "vpnLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="vpnSecurityGroups")
    def vpn_security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security group for Client VPN Endpoint.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "vpnSecurityGroups"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.DataVpcClientVpnEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "saml_metadata_document": "samlMetadataDocument",
        "server_certificate_arn": "serverCertificateArn",
        "authorize_all_users_to_vpc_cidr": "authorizeAllUsersToVpcCidr",
        "dns_servers": "dnsServers",
        "logging": "logging",
        "log_group": "logGroup",
        "port": "port",
        "security_groups": "securityGroups",
        "self_service_portal": "selfServicePortal",
        "session_timeout": "sessionTimeout",
        "split_tunnel": "splitTunnel",
        "transport_protocol": "transportProtocol",
    },
)
class DataVpcClientVpnEndpointProps:
    def __init__(
        self,
        *,
        saml_metadata_document: builtins.str,
        server_certificate_arn: builtins.str,
        authorize_all_users_to_vpc_cidr: typing.Optional[builtins.bool] = None,
        dns_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
        logging: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        port: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpnPort] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        self_service_portal: typing.Optional[builtins.bool] = None,
        session_timeout: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ClientVpnSessionTimeout] = None,
        split_tunnel: typing.Optional[builtins.bool] = None,
        transport_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.TransportProtocol] = None,
    ) -> None:
        '''The properties for the ClientVPnEndpoint in DataVpc construct.

        :param saml_metadata_document: An XML document generated by an identity provider (IdP) that supports SAML 2.0. The document includes the issuer's name, expiration information, and keys that can be used to validate the SAML authentication response (assertions) that are received from the IdP. You must generate the metadata document using the identity management software that is used as your organization's IdP.
        :param server_certificate_arn: The ARN of the server certificate.
        :param authorize_all_users_to_vpc_cidr: Whether to authorize all users to the VPC CIDR. Default: true
        :param dns_servers: Information about the DNS servers to be used for DNS resolution. Default: DNS server in VPC, e.g. 10.0.0.2
        :param logging: A CloudWatch Logs log group for connection logging. Default: true
        :param log_group: A CloudWatch Logs log group for connection logging. Default: new LogGroup is created
        :param port: The port number to assign to the Client VPN endpoint for TCP and UDP traffic. Default: true
        :param security_groups: The security groups to apply to the target network. Default: new Securoty Group is created, allowing the incoming connections on port 443
        :param self_service_portal: Specify whether to enable the self-service portal for the Client VPN endpoint. Default: true
        :param session_timeout: The maximum VPN session duration time. Default: 480 minutes
        :param split_tunnel: Indicates whether split-tunnel is enabled on the AWS Client VPN endpoint. Default: true
        :param transport_protocol: The transport protocol to be used by the VPN session. Default: TCP
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f9e02adbd79c0e13152c12f983d4f942b325d9b511985bec14c1b11b1ad7cb9)
            check_type(argname="argument saml_metadata_document", value=saml_metadata_document, expected_type=type_hints["saml_metadata_document"])
            check_type(argname="argument server_certificate_arn", value=server_certificate_arn, expected_type=type_hints["server_certificate_arn"])
            check_type(argname="argument authorize_all_users_to_vpc_cidr", value=authorize_all_users_to_vpc_cidr, expected_type=type_hints["authorize_all_users_to_vpc_cidr"])
            check_type(argname="argument dns_servers", value=dns_servers, expected_type=type_hints["dns_servers"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument self_service_portal", value=self_service_portal, expected_type=type_hints["self_service_portal"])
            check_type(argname="argument session_timeout", value=session_timeout, expected_type=type_hints["session_timeout"])
            check_type(argname="argument split_tunnel", value=split_tunnel, expected_type=type_hints["split_tunnel"])
            check_type(argname="argument transport_protocol", value=transport_protocol, expected_type=type_hints["transport_protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "saml_metadata_document": saml_metadata_document,
            "server_certificate_arn": server_certificate_arn,
        }
        if authorize_all_users_to_vpc_cidr is not None:
            self._values["authorize_all_users_to_vpc_cidr"] = authorize_all_users_to_vpc_cidr
        if dns_servers is not None:
            self._values["dns_servers"] = dns_servers
        if logging is not None:
            self._values["logging"] = logging
        if log_group is not None:
            self._values["log_group"] = log_group
        if port is not None:
            self._values["port"] = port
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if self_service_portal is not None:
            self._values["self_service_portal"] = self_service_portal
        if session_timeout is not None:
            self._values["session_timeout"] = session_timeout
        if split_tunnel is not None:
            self._values["split_tunnel"] = split_tunnel
        if transport_protocol is not None:
            self._values["transport_protocol"] = transport_protocol

    @builtins.property
    def saml_metadata_document(self) -> builtins.str:
        '''An XML document generated by an identity provider (IdP) that supports SAML 2.0. The document includes the issuer's name, expiration information, and keys that can be used to validate the SAML authentication response (assertions) that are received from the IdP. You must generate the metadata document using the identity management software that is used as your organization's IdP.'''
        result = self._values.get("saml_metadata_document")
        assert result is not None, "Required property 'saml_metadata_document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_certificate_arn(self) -> builtins.str:
        '''The ARN of the server certificate.'''
        result = self._values.get("server_certificate_arn")
        assert result is not None, "Required property 'server_certificate_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorize_all_users_to_vpc_cidr(self) -> typing.Optional[builtins.bool]:
        '''Whether to authorize all users to the VPC CIDR.

        :default: true
        '''
        result = self._values.get("authorize_all_users_to_vpc_cidr")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dns_servers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Information about the DNS servers to be used for DNS resolution.

        :default: DNS server in VPC, e.g. 10.0.0.2
        '''
        result = self._values.get("dns_servers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def logging(self) -> typing.Optional[builtins.bool]:
        '''A CloudWatch Logs log group for connection logging.

        :default: true
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''A CloudWatch Logs log group for connection logging.

        :default: new LogGroup is created
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def port(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpnPort]:
        '''The port number to assign to the Client VPN endpoint for TCP and UDP traffic.

        :default: true
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpnPort], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to apply to the target network.

        :default: new Securoty Group is created, allowing the incoming connections on port 443
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def self_service_portal(self) -> typing.Optional[builtins.bool]:
        '''Specify whether to enable the self-service portal for the Client VPN endpoint.

        :default: true
        '''
        result = self._values.get("self_service_portal")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def session_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ClientVpnSessionTimeout]:
        '''The maximum VPN session duration time.

        :default: 480 minutes
        '''
        result = self._values.get("session_timeout")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ClientVpnSessionTimeout], result)

    @builtins.property
    def split_tunnel(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether split-tunnel is enabled on the AWS Client VPN endpoint.

        :default: true
        '''
        result = self._values.get("split_tunnel")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def transport_protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.TransportProtocol]:
        '''The transport protocol to be used by the VPN session.

        :default: TCP
        '''
        result = self._values.get("transport_protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.TransportProtocol], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVpcClientVpnEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.DataVpcProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc_cidr": "vpcCidr",
        "client_vpn_endpoint_props": "clientVpnEndpointProps",
        "flow_log_key": "flowLogKey",
        "flow_log_retention": "flowLogRetention",
        "flow_log_role": "flowLogRole",
        "nat_gateways": "natGateways",
        "removal_policy": "removalPolicy",
    },
)
class DataVpcProps:
    def __init__(
        self,
        *,
        vpc_cidr: builtins.str,
        client_vpn_endpoint_props: typing.Optional[typing.Union[DataVpcClientVpnEndpointProps, typing.Dict[builtins.str, typing.Any]]] = None,
        flow_log_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        flow_log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        flow_log_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''The properties for the ``DataVpc`` construct.

        :param vpc_cidr: The CIDR to use to create the subnets in the VPC.
        :param client_vpn_endpoint_props: ClientVpnEndpoint propertioes. Required if client vpn endpoint is needed Default: None
        :param flow_log_key: The KMS key used to encrypt the VPC Flow Logs in the CloudWatch Log Group. The resource policy of the key must be configured according to the AWS documentation. Default: - A new KMS key is created
        :param flow_log_retention: The retention period to apply to VPC Flow Logs. Default: - One week retention
        :param flow_log_role: The IAM Role used to send the VPC Flow Logs in CloudWatch. The role must be configured as described in the AWS VPC Flow Log documentation. Default: - A new IAM role is created
        :param nat_gateways: Number of NAT Gateways. Default: 3 or the AZs defined in the context
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if isinstance(client_vpn_endpoint_props, dict):
            client_vpn_endpoint_props = DataVpcClientVpnEndpointProps(**client_vpn_endpoint_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f5bd0a66c070362158feeb021d04ddf2268154575ded55b8382334b30740e6)
            check_type(argname="argument vpc_cidr", value=vpc_cidr, expected_type=type_hints["vpc_cidr"])
            check_type(argname="argument client_vpn_endpoint_props", value=client_vpn_endpoint_props, expected_type=type_hints["client_vpn_endpoint_props"])
            check_type(argname="argument flow_log_key", value=flow_log_key, expected_type=type_hints["flow_log_key"])
            check_type(argname="argument flow_log_retention", value=flow_log_retention, expected_type=type_hints["flow_log_retention"])
            check_type(argname="argument flow_log_role", value=flow_log_role, expected_type=type_hints["flow_log_role"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc_cidr": vpc_cidr,
        }
        if client_vpn_endpoint_props is not None:
            self._values["client_vpn_endpoint_props"] = client_vpn_endpoint_props
        if flow_log_key is not None:
            self._values["flow_log_key"] = flow_log_key
        if flow_log_retention is not None:
            self._values["flow_log_retention"] = flow_log_retention
        if flow_log_role is not None:
            self._values["flow_log_role"] = flow_log_role
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def vpc_cidr(self) -> builtins.str:
        '''The CIDR to use to create the subnets in the VPC.'''
        result = self._values.get("vpc_cidr")
        assert result is not None, "Required property 'vpc_cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_vpn_endpoint_props(
        self,
    ) -> typing.Optional[DataVpcClientVpnEndpointProps]:
        '''ClientVpnEndpoint propertioes.

        Required if client vpn endpoint is needed

        :default: None
        '''
        result = self._values.get("client_vpn_endpoint_props")
        return typing.cast(typing.Optional[DataVpcClientVpnEndpointProps], result)

    @builtins.property
    def flow_log_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used to encrypt the VPC Flow Logs in the CloudWatch Log Group.

        The resource policy of the key must be configured according to the AWS documentation.

        :default: - A new KMS key is created

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/encrypt-log-data-kms.html
        '''
        result = self._values.get("flow_log_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def flow_log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The retention period to apply to VPC Flow Logs.

        :default: - One week retention
        '''
        result = self._values.get("flow_log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def flow_log_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used to send the VPC Flow Logs in CloudWatch.

        The role must be configured as described in the AWS VPC Flow Log documentation.

        :default: - A new IAM role is created

        :see: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html#flow-logs-iam-role
        '''
        result = self._values.get("flow_log_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''Number of NAT Gateways.

        :default: 3 or the AZs defined in the context
        '''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3DataCopy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.S3DataCopy",
):
    '''Copy data from one S3 bucket to another.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Utils/s3-data-copy

    Example::

        from aws_cdk.aws_s3 import Bucket
        
        
        source_bucket = Bucket.from_bucket_name(self, "SourceBucket", "nyc-tlc")
        bucket_name = f"test-{this.region}-{this.account}-{dsf.utils.Utils.generateUniqueHash(this, 'TargetBucket')}"
        
        target_bucket = Bucket(self, "TargetBucket")
        
        dsf.utils.S3DataCopy(self, "S3DataCopy",
            source_bucket=source_bucket,
            source_bucket_prefix="trip data/",
            source_bucket_region="us-east-1",
            target_bucket=target_bucket
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        source_bucket_region: builtins.str,
        target_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        source_bucket_prefix: typing.Optional[builtins.str] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        target_bucket_prefix: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param source_bucket: The source S3 Bucket containing the data to copy.
        :param source_bucket_region: The source S3 Bucket region.
        :param target_bucket: The target S3 Bucket.
        :param execution_role: The IAM Role to use in the custom resource for copying data. Default: - A new role is created
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param security_groups: The list of security groups to attach to the custom resource. Default: - If ``vpc`` is not supplied, no security groups are attached. Otherwise, a dedicated security group is created for each function.
        :param source_bucket_prefix: The source bucket prefix with a slash at the end. Default: - No prefix is used
        :param subnets: The subnets to deploy the custom resource in. Default: - The Custom Resource is executed in VPCs owned by AWS Lambda service.
        :param target_bucket_prefix: The target S3 Bucket prefix with a slash at the end. Default: - No prefix is used
        :param vpc: The VPC to deploy the custom resource in. Default: - The Custom Resource is executed in VPCs owned by AWS Lambda service.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__517cea3b12f758ad38d48578dca87a1f97c700253daf18d0fa4f1079fa3b310b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = S3DataCopyProps(
            source_bucket=source_bucket,
            source_bucket_region=source_bucket_region,
            target_bucket=target_bucket,
            execution_role=execution_role,
            removal_policy=removal_policy,
            security_groups=security_groups,
            source_bucket_prefix=source_bucket_prefix,
            subnets=subnets,
            target_bucket_prefix=target_bucket_prefix,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="copyFunction")
    def copy_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the copy.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "copyFunction"))

    @builtins.property
    @jsii.member(jsii_name="copyLogGroup")
    def copy_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the S3 data copy.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "copyLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="copyRole")
    def copy_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the copy Lambba Function.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "copyRole"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpFunction")
    def clean_up_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function for the S3 data copy cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "cleanUpFunction"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpLogGroup")
    def clean_up_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group for the S3 data copy cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "cleanUpLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpRole")
    def clean_up_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role for the the S3 data copy cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "cleanUpRole"))

    @builtins.property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The list of EC2 Security Groups used by the Lambda Functions.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "securityGroups"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.S3DataCopyProps",
    jsii_struct_bases=[],
    name_mapping={
        "source_bucket": "sourceBucket",
        "source_bucket_region": "sourceBucketRegion",
        "target_bucket": "targetBucket",
        "execution_role": "executionRole",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "source_bucket_prefix": "sourceBucketPrefix",
        "subnets": "subnets",
        "target_bucket_prefix": "targetBucketPrefix",
        "vpc": "vpc",
    },
)
class S3DataCopyProps:
    def __init__(
        self,
        *,
        source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        source_bucket_region: builtins.str,
        target_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        source_bucket_prefix: typing.Optional[builtins.str] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        target_bucket_prefix: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Properties for S3DataCopy construct.

        :param source_bucket: The source S3 Bucket containing the data to copy.
        :param source_bucket_region: The source S3 Bucket region.
        :param target_bucket: The target S3 Bucket.
        :param execution_role: The IAM Role to use in the custom resource for copying data. Default: - A new role is created
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param security_groups: The list of security groups to attach to the custom resource. Default: - If ``vpc`` is not supplied, no security groups are attached. Otherwise, a dedicated security group is created for each function.
        :param source_bucket_prefix: The source bucket prefix with a slash at the end. Default: - No prefix is used
        :param subnets: The subnets to deploy the custom resource in. Default: - The Custom Resource is executed in VPCs owned by AWS Lambda service.
        :param target_bucket_prefix: The target S3 Bucket prefix with a slash at the end. Default: - No prefix is used
        :param vpc: The VPC to deploy the custom resource in. Default: - The Custom Resource is executed in VPCs owned by AWS Lambda service.
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0f1736d011e3dabe341959f89b9b95889c7c24aa7cdfa70fa1893401fa55286)
            check_type(argname="argument source_bucket", value=source_bucket, expected_type=type_hints["source_bucket"])
            check_type(argname="argument source_bucket_region", value=source_bucket_region, expected_type=type_hints["source_bucket_region"])
            check_type(argname="argument target_bucket", value=target_bucket, expected_type=type_hints["target_bucket"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument source_bucket_prefix", value=source_bucket_prefix, expected_type=type_hints["source_bucket_prefix"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument target_bucket_prefix", value=target_bucket_prefix, expected_type=type_hints["target_bucket_prefix"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_bucket": source_bucket,
            "source_bucket_region": source_bucket_region,
            "target_bucket": target_bucket,
        }
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if source_bucket_prefix is not None:
            self._values["source_bucket_prefix"] = source_bucket_prefix
        if subnets is not None:
            self._values["subnets"] = subnets
        if target_bucket_prefix is not None:
            self._values["target_bucket_prefix"] = target_bucket_prefix
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def source_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The source S3 Bucket containing the data to copy.'''
        result = self._values.get("source_bucket")
        assert result is not None, "Required property 'source_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def source_bucket_region(self) -> builtins.str:
        '''The source S3 Bucket region.'''
        result = self._values.get("source_bucket_region")
        assert result is not None, "Required property 'source_bucket_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The target S3 Bucket.'''
        result = self._values.get("target_bucket")
        assert result is not None, "Required property 'target_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role to use in the custom resource for copying data.

        :default: - A new role is created
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The list of security groups to attach to the custom resource.

        :default:

        - If ``vpc`` is not supplied, no security groups are attached. Otherwise, a dedicated security
        group is created for each function.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def source_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''The source bucket prefix with a slash at the end.

        :default: - No prefix is used
        '''
        result = self._values.get("source_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to deploy the custom resource in.

        :default: - The Custom Resource is executed in VPCs owned by AWS Lambda service.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def target_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''The target S3 Bucket prefix with a slash at the end.

        :default: - No prefix is used
        '''
        result = self._values.get("target_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC to deploy the custom resource in.

        :default: - The Custom Resource is executed in VPCs owned by AWS Lambda service.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3DataCopyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StepFunctionUtils(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.StepFunctionUtils",
):
    '''Utils for working with AWS Step Functions.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="camelToPascal")
    @builtins.classmethod
    def camel_to_pascal(
        cls,
        config: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''Convert camel case properties to pascal case as required by AWS Step Functions API.

        :param config: -

        :return: config converted to pascal case.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8900956bb9a5e837ad18d5f562d4d1129e080f940075a87fdda2f93cb4467b66)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.sinvoke(cls, "camelToPascal", [config]))


class Utils(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.utils.Utils",
):
    '''Utilities class used across the different resources.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="generateHash")
    @builtins.classmethod
    def generate_hash(cls, text: builtins.str) -> builtins.str:
        '''Generate an 8 character hash from a string based on HMAC algorithm.

        :param text: the text to hash.

        :return: the hash
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4e130c83849df0af7b3beb5e50b0f00a681650d748a723d6c81079ec6f34336)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "generateHash", [text]))

    @jsii.member(jsii_name="generateUniqueHash")
    @builtins.classmethod
    def generate_unique_hash(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''Generate a unique hash of 8 characters from the CDK scope using its path and the stack name.

        :param scope: the CDK construct scope.
        :param id: the CDK ID of the construct.

        :return: the hash
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f70aa0e068d4cfe35caac3551a2937a15c623193142ac0abb9ea73184612ded3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "generateUniqueHash", [scope, id]))

    @jsii.member(jsii_name="loadYaml")
    @builtins.classmethod
    def load_yaml(cls, document: builtins.str) -> typing.Any:
        '''Take a document stored as string and load it as YAML.

        :param document: the document stored as string.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f08bfe619a6fde71b5609a00f036443fb3dcf2ab30d09c795dbe0f7f0475a43d)
            check_type(argname="argument document", value=document, expected_type=type_hints["document"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "loadYaml", [document]))

    @jsii.member(jsii_name="randomize")
    @builtins.classmethod
    def randomize(cls, name: builtins.str) -> builtins.str:
        '''Create a random string to be used as a seed for IAM User password.

        :param name: the string to which to append a random string.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e46f5024bfd2dc86af961c4cd184819afa4b4f01044da9ca6940bee2c2dcc0b)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "randomize", [name]))

    @jsii.member(jsii_name="readYamlDocument")
    @builtins.classmethod
    def read_yaml_document(cls, path: builtins.str) -> builtins.str:
        '''Read a YAML file from the path provided and return it.

        :param path: the path to the file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8fc6dd438a6c31ad0cb5346cde32a499294a5ff963bf4c6bdfaa41fc70c2db4)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "readYamlDocument", [path]))

    @jsii.member(jsii_name="stringSanitizer")
    @builtins.classmethod
    def string_sanitizer(cls, to_sanitize: builtins.str) -> builtins.str:
        '''Sanitize a string by removing upper case and replacing special characters except underscore.

        :param to_sanitize: the string to sanitize.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__025e16c10d80d5bc5e52559e8abad325d61eab41c0f9f27dff7670f8cc0ddb1a)
            check_type(argname="argument to_sanitize", value=to_sanitize, expected_type=type_hints["to_sanitize"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "stringSanitizer", [to_sanitize]))

    @jsii.member(jsii_name="toPascalCase")
    @builtins.classmethod
    def to_pascal_case(cls, text: builtins.str) -> builtins.str:
        '''Convert a string to PascalCase.

        :param text: the string to convert to PascalCase.

        :return: the string in Pascal case
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0331f7f31994294da6d4af34e71088170ba59a4c2a25908dab263b4710f4408a)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "toPascalCase", [text]))


__all__ = [
    "ApplicationStackFactory",
    "ApplicationStage",
    "ApplicationStageProps",
    "Architecture",
    "BucketUtils",
    "CICDStage",
    "DataVpc",
    "DataVpcClientVpnEndpointProps",
    "DataVpcProps",
    "S3DataCopy",
    "S3DataCopyProps",
    "StepFunctionUtils",
    "Utils",
]

publication.publish()

def _typecheckingstub__4eef9172971b514785a6ce2346308753b3a0e87079b7ff4a145e5bb81378146a(
    scope: _constructs_77d1e7e8.Construct,
    stage: CICDStage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b5ac3de86725230614eaa05d4d588181e4795f348801b8e9846f7a8ade6698(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_stack_factory: ApplicationStackFactory,
    stage: CICDStage,
    outputs_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d0cd7bb2c6f89ceae419e95586371f2db805a9f35f0aa2ec97dcf48aa8c0209(
    *,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
    application_stack_factory: ApplicationStackFactory,
    stage: CICDStage,
    outputs_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88bcefb5e5ed5389168d4178ba329d512cd1938b816b8cfe7bc44a5b3124986f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9563cd6cefb38ed980d4672a429ac3bfb7e0fdf90feea5a4f416b4ff13b018a7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc_cidr: builtins.str,
    client_vpn_endpoint_props: typing.Optional[typing.Union[DataVpcClientVpnEndpointProps, typing.Dict[builtins.str, typing.Any]]] = None,
    flow_log_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    flow_log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    flow_log_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__006cefc76fdc1dca834321b036a66ceab95669c6f8f2eb4389a95b6405c5ca3a(
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f9e02adbd79c0e13152c12f983d4f942b325d9b511985bec14c1b11b1ad7cb9(
    *,
    saml_metadata_document: builtins.str,
    server_certificate_arn: builtins.str,
    authorize_all_users_to_vpc_cidr: typing.Optional[builtins.bool] = None,
    dns_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
    logging: typing.Optional[builtins.bool] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    port: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.VpnPort] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    self_service_portal: typing.Optional[builtins.bool] = None,
    session_timeout: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ClientVpnSessionTimeout] = None,
    split_tunnel: typing.Optional[builtins.bool] = None,
    transport_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.TransportProtocol] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f5bd0a66c070362158feeb021d04ddf2268154575ded55b8382334b30740e6(
    *,
    vpc_cidr: builtins.str,
    client_vpn_endpoint_props: typing.Optional[typing.Union[DataVpcClientVpnEndpointProps, typing.Dict[builtins.str, typing.Any]]] = None,
    flow_log_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    flow_log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    flow_log_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__517cea3b12f758ad38d48578dca87a1f97c700253daf18d0fa4f1079fa3b310b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    source_bucket_region: builtins.str,
    target_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    source_bucket_prefix: typing.Optional[builtins.str] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    target_bucket_prefix: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0f1736d011e3dabe341959f89b9b95889c7c24aa7cdfa70fa1893401fa55286(
    *,
    source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    source_bucket_region: builtins.str,
    target_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    source_bucket_prefix: typing.Optional[builtins.str] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    target_bucket_prefix: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8900956bb9a5e837ad18d5f562d4d1129e080f940075a87fdda2f93cb4467b66(
    config: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4e130c83849df0af7b3beb5e50b0f00a681650d748a723d6c81079ec6f34336(
    text: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f70aa0e068d4cfe35caac3551a2937a15c623193142ac0abb9ea73184612ded3(
    scope: _constructs_77d1e7e8.Construct,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f08bfe619a6fde71b5609a00f036443fb3dcf2ab30d09c795dbe0f7f0475a43d(
    document: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e46f5024bfd2dc86af961c4cd184819afa4b4f01044da9ca6940bee2c2dcc0b(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8fc6dd438a6c31ad0cb5346cde32a499294a5ff963bf4c6bdfaa41fc70c2db4(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__025e16c10d80d5bc5e52559e8abad325d61eab41c0f9f27dff7670f8cc0ddb1a(
    to_sanitize: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0331f7f31994294da6d4af34e71088170ba59a4c2a25908dab263b4710f4408a(
    text: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

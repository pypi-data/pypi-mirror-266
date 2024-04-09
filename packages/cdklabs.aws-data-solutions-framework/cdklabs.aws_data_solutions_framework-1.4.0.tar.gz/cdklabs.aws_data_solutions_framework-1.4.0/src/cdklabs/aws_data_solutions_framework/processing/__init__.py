'''
# Spark EMR Serverless Runtime

A [Spark EMR Serverless Application](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/getting-started.html) with IAM roles and permissions helpers.

## Overview

The construct creates a Spark EMR Serverless Application, with the latest EMR runtime as the default runtime. You can change the runtime by passing your own as a `Resource property` to construct initializer. It also provides methods to create a principal or grant an existing principal (ie IAM Role or IAM User) with the permission to start a job on this EMR Serverless application.

The construct creates a default VPC that is used by EMR Serverless Application. The VPC has `10.0.0.0/16` CIDR range, and comes with an S3 VPC Endpoint Gateway attached to it. The construct also creates a security group for the EMR Serverless Application. You can override this by defining your own `NetworkConfiguration` as defined in the `Resource properties` of the construct initializer.

The construct has the following interfaces:

* A construct Initializer that takes an object as `Resource properties` to modify the default properties. The properties are defined in `SparkEmrServerlessRuntimeProps` interface.
* A method to create an execution role for EMR Serverless. The execution role is scoped down to the EMR Serverless Application ARN created by the construct.
* A method that takes an IAM role to call the `StartJobRun`, and monitors the status of the job.

  * The IAM policies attached to the provided IAM role is as [follow](https://github.com/awslabs/data-solutions-framework-on-aws/blob/c965202f48088f5ae51ce0e719cf92adefac94ac/framework/src/processing/spark-runtime/emr-serverless/spark-emr-runtime-serverless.ts#L117).
  * The role has a `PassRole` permission scoped as [follow](https://github.com/awslabs/data-solutions-framework-on-aws/blob/c965202f48088f5ae51ce0e719cf92adefac94ac/framework/src/processing/spark-runtime/emr-serverless/spark-emr-runtime-serverless.ts#L106).

The construct has the following attributes:

* applicationArn: EMR Serverless Application ARN
* applicationId: EMR Serverless Application ID
* vpc: VPC is created if none is provided
* emrApplicationSecurityGroup: security group created with VPC
* s3GatewayVpcEndpoint: S3 Gateway endpoint attached to VPC

The construct is depicted below:

![Spark Runtime Serverless](../../../website/static/img/adsf-spark-runtime.png)

## Usage

The code snippet below shows a usage example of the `SparkEmrServerlessRuntime` construct.

```python
class ExampleSparkEmrServerlessStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        runtime_serverless = dsf.processing.SparkEmrServerlessRuntime(self, "SparkRuntimeServerless",
            name="spark-serverless-demo"
        )

        s3_read_policy_document = PolicyDocument(
            statements=[
                PolicyStatement.from_json({
                    "actions": ["s3:GetObject"],
                    "resources": ["arn:aws:s3:::bucket_name"]
                })
            ]
        )

        # The IAM role that will trigger the Job start and will monitor it
        job_trigger = Role(self, "EMRServerlessExecutionRole",
            assumed_by=ServicePrincipal("lambda.amazonaws.com")
        )

        execution_role = dsf.processing.SparkEmrServerlessRuntime.create_execution_role(self, "EmrServerlessExecutionRole", s3_read_policy_document)

        runtime_serverless.grant_start_execution(job_trigger, execution_role.role_arn)

        cdk.CfnOutput(self, "SparkRuntimeServerlessStackApplicationArn",
            value=runtime_serverless.application.attr_arn
        )
```

# Spark EMR Serverless job

An [Amazon EMR Serverless](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/getting-started.html) Spark job orchestrated through AWS Step Functions state machine.

## Overview

The construct creates an AWS Step Functions state machine that is used to submit a Spark job and orchestrate the lifecycle of the job. The construct leverages the [AWS SDK service integrations](https://docs.aws.amazon.com/step-functions/latest/dg/supported-services-awssdk.html) to submit the jobs. The state machine can take a cron expression to trigger the job at a given interval. The schema below shows the state machine:

![Spark EMR Serverless Job](../../../website/static/img/adsf-spark-emr-serverless-job.png)

## Usage

The example stack below shows how to use `EmrServerlessSparkJob` construct. The stack also contains a `SparkEmrServerlessRuntime` to show how to create an EMR Serverless Application and pass it as an argument to the `Spark job` and use it as a runtime for the job.

```python
cdk.Stack):
scope, id):
super().__init__(scope, id)night_job = dsf.processing.SparkEmrServerlessJob(self, "PiJob",
    application_id=runtime.application.attr_application_id,
    name="PiCalculation",
    execution_role=execution_role,
    execution_timeout=cdk.Duration.minutes(15),
    s3_log_bucket=Bucket.from_bucket_name(self, "LogBucket", "emr-job-logs-EXAMPLE"),
    s3_log_prefix="logs",
    spark_submit_entry_point="local:///usr/lib/spark/examples/src/main/python/pi.py"
)

CfnOutput(self, "job-state-machine",
    value=night_job.state_machine.state_machine_arn
)
```

## Using the EMR Serverless `StartJobRun` parameters

The `SparkEmrServerlessJobProps` interface provides a simple abstraction to create an EMR Serverless Job. For deeper control on the job configuration, you can also use the `SparkEmrServerlessJobApiProps` inteface which provide the same interface as the [StartJobRun API](https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_StartJobRun.html) from EMR Serverless.

# PySpark Application Package

A PySpark application packaged with its dependencies and uploaded on an S3 artifact bucket.

## Overview

The construct package your PySpark application (the entrypoint, supporting files and virtual environment)
and upload it to an Amazon S3 bucket. In the rest of the documentation we call the entrypoint,
supporting files and virtual environment as artifacts.

The PySpark Application Package has two responsibilities:

* Upload your PySpark entrypoint application to an artifact bucket
* Package your PySpark virtual environment (venv) and upload it to an artifact bucket. The package of venv is done using docker,
  an example in the [Usage](#usage) section shows how to write the Dockerfile to package the application.

The construct uses the [Asset](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3_assets.Asset.html)
to upload the PySpark Application artifacts to CDK Asset bucket. These are then copied to an S3 bucket we call artifact bucket.

To manage the lifecycle of the artifacts as CDK assets, the constructs need Docker daemon running on the local machine.
Make sure to have Docker running before using the construct.

### Construct attributes

The construct exposes the artifacts through the following interfaces:

* entrypointS3Uri: The S3 location where the entry point is saved in S3. You pass this location to your Spark job.
* venvArchiveS3Uri: The S3 location where the archive of the Python virtual environment with all dependencies is stored. You pass this location to your Spark job.
* sparkVenvConf: The Spark config containing the configuration of virtual environment archive with all dependencies.

### Resources created

* An Amazon S3 Bucket to store the PySpark Application artifacts. You can also provide your own if you have already a bucket that you want to use. This bucket comes with configuration to enforce `TLS`, `Block Public Access` and encrypt objects with `SSE-KMS`,
* An IAM role used by a Lambda to copy from the CDK Asset bucket to the artifact bucket created above or provided.

The schema below shows the resources created and the responsible of the construct:

![PySpark Application Package](../../../website/static/img/adsf-pyspark-application-package.png)

## Usage

In this example we will show you how you can use the construct to package a PySpark application
and submit a job to EMR Serverless leveraging DSF `SparkEmrServerlessRuntime` and `SparkJob` constructs.

For this example we assume we will have the folder structure as shown below. We have two folders, one containing
the `PySpark` application called `spark` folder and a second containing the `CDK` code called `cdk`.
The PySpark code, follows the standards `Python` structure. The `spark` also contains the `Dockerfile` to build the `venv`.
In the next [section](#dockerfile-definition) will describe how to structure the `Dockerfile`.

```bash
root
|--spark
|    |--test
|    |--src
|       |--__init__.py
|       |--entrypoint.py
|       |--dir1
|        |--__init__.py
|        |--helpers.py
|    |--requirement.txt
|    |--Dockerfile #contains the build instructions to package the virtual environment for PySpark
|--cdk #contains the CDK application that deploys CDK stack with the PySparkApplicationPackage
```

### PySpark Application Definition

For this example we define the PySparkApplicationPackage resource as follows:

```python
dsf.processing.PySparkApplicationPackage(self, "PySparkApplicationPackage",
    application_name="nightly-job-aggregation",
    entrypoint_path="./../spark/src/entrypoint.py",
    dependencies_folder="./../spark",
    venv_archive_path="/venv-package/pyspark-env.tar.gz"
)
```

### Dockerfile definition

The steps below describe how to create the `Dockerfile` so it can be used to be package `venv` by the construct

* In order to build the virtual environment, the docker container will mount the `dependencies_folder`, in our case we define it as `./../spark`.
* Then to package the `venv` we need to build `COPY` all the files in `./spark` to the docker container.
* Last we execute the `venv-package`, in the [PySparkApplication](#pyspark-application-definition) we passed the `venv_archive_path` as `/venv-package/pyspark-env.tar.gz`.
  So we need to create it with `mkdir /venv-package` and then pass it to the `venv-package` as `venv-pack -o /venv-package/pyspark-env.tar.gz`

```Dockerfile
FROM --platform=linux/amd64 public.ecr.aws/amazonlinux/amazonlinux:latest AS base

RUN dnf install -y python3

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . .

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install venv-pack==0.2.0 && \
    python3 -m pip install .

RUN mkdir /venv-package && venv-pack -o /venv-package/pyspark-env.tar.gz && chmod ugo+r /venv-package/pyspark-env.tar.gz
```

### Define a CDK stack upload PySpark application and run the job

The stack below leverages the resources defined above for PySpark to build the end to end example for building and submitting a PySpark job.

```python
runtime = dsf.processing.SparkEmrServerlessRuntime(self, "SparkRuntime",
    name="mySparkRuntime"
)application_package = dsf.processing.PySparkApplicationPackage(self, "PySparkApplicationPackage",
    application_name="nightly-job-aggregation",
    entrypoint_path="./../spark/src/entrypoint.py",
    dependencies_folder="./../spark",
    venv_archive_path="/venv-package/pyspark-env.tar.gz"
)

dsf.processing.SparkEmrServerlessJob(self, "SparkNightlyJob",
    application_id=runtime.application.attr_application_id,
    name="nightly_job",
    execution_role=execution_role,
    execution_timeout=cdk.Duration.minutes(15),
    s3_log_bucket=Bucket.from_bucket_arn(self, "LogBucket", "emr-job-logs-EXAMPLE"),
    s3_log_prefix="logs",
    spark_submit_entry_point=application_package.entrypoint_uri,  # use the application package entrypoint
    spark_submit_parameters="--conf spark.executor.instances=2 --conf spark.executor.memory=2G --conf spark.driver.memory=2G --conf spark.executor.cores=2 {sparkEnvConf}"
)
```

# Spark CI/CD Pipeline

Self-mutable CI/CD pipeline for a Spark application based on [Amazon EMR](https://aws.amazon.com/fr/emr/) runtime.

## Overview

The CI/CD pipeline uses [CDK Pipeline](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html) and provisions all the resources needed to implement a CI/CD pipeline for a Spark application on Amazon EMR, including:

* A CodeCommit repository to host the code
* A CodePipeline triggered from the main branch of the CodeCommit repository to process the CI/CD tasks
* A CodeBuild stage to build the CDK assets and run the Spark unit tests
* A Staging stage to deploy the application stack in the staging environment and run optional integration tests
* A Production stage to deploy the application stack in the production environment

![Spark CI/CD Pipeline](../../../website/static/img/adsf-spark-cicd.png)

## Cross-account deployment

You can use the same account or optionally use different accounts for CI/CD (where this construct is deployed), staging and production (where the application stack is deployed).
If using different accounts, bootstrap staging and production accounts with CDK and add a trust relationship from the CI/CD account:

```bash
cdk bootstrap --profile staging \
aws://<STAGING_ACCOUNT_ID>/<REGION> \
--trust <CICD_ACCOUNT_ID> \
--cloudformation-execution-policies "POLICY_ARN"
```

More information is available [here](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html#cdk_pipeline_bootstrap)

You need to also provide the accounts information in the cdk.json in the form of:

```json
{
  "staging": {
    "account": "<STAGING_ACCOUNT_ID>",
    "region": "<REGION>"
  },
  "prod": {
    "account": "<PROD_ACCOUNT_ID>",
    "region": "<REGION>"
  }
}
```

## Defining a CDK Stack for the Spark application

The `SparkCICDPipeline` construct deploys an application stack, which contains your business logic, into staging and production environments.
The application stack is a standard CDK stack that you provide. It's expected to be passed via a factory class.

To do this, implement the `ApplicationStackFactory` and its `createStack()` method.
The `createStack()` method needs to return a `Stack` instance within the scope passed to the factory method.
This is used to create the application stack within the scope of the CDK Pipeline stage.

The `CICDStage` parameter is automatically passed by the CDK Pipeline via the factory method and allows you to customize the behavior of the Stack based on the stage.
For example, staging stage is used for integration tests so testing a processing job should be done via manually triggering it.
In opposition to production stage where the processing job could be automated on a regular basis.

Create your application stack using the factory pattern:

```python
class EmrApplicationStackFactory(dsf.utils.ApplicationStackFactory):
    def create_stack(self, scope, stage):
        return EmrApplicationStack(scope, "EmrApplicationStack", stage)

class EmrApplicationStack(cdk.Stack):
    def __init__(self, scope, id, stage):
        super().__init__(scope, id)

        # DEFINE YOUR APPLICATION STACK HERE
        # USE STAGE PARAMETER TO CUSTOMIZE THE STACK BEHAVIOR

        if stage == dsf.utils.CICDStage.PROD:
            pass
```

Use the factory to pass your application stack to the `SparkCICDPipeline` construct:

```python
class CICDPipelineStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        dsf.processing.SparkEmrCICDPipeline(self, "SparkCICDPipeline",
            spark_application_name="SparkTest",
            application_stack_factory=EmrApplicationStackFactory()
        )
```

## Unit tests

The construct triggers the unit tests as part of the CI/CD process using the EMR docker image and a fail fast approach.
The unit tests are run during the first build step and the entire pipeline stops if the unit tests fail.

Units tests are expected to be run with `pytest` command after a `pip install .` is run from the Spark root folder configured via `sparkPath`.

In your Pytest script, use a Spark session with a local master and client mode as the unit tests run in a local EMR docker container:

```python
spark = (
        SparkSession.builder.master("local[1]")
        .appName("local-tests")
        .config("spark.submit.deployMode", "client")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
```

## Integration tests

You can optionally run integration tests as part of the CI/CD process using the AWS CLI in a bash script that return `0` exit code if success and `1` if failure.
The integration tests are triggered after the deployment of the application stack in the staging environment.

You can run them via `integTestScript` path that should point to a bash script. For example:

```bash
root
|--spark
|    |--integ.sh
|--cdk
```

`integ.sh` is a standard bash script using the AWS CLI to validate the application stack. In the following script example, a Step Function from the application stack is triggered and the result of its execution should be successful:

```bash
#!/bin/bash
EXECUTION_ARN=$(aws stepfunctions start-execution --state-machine-arn $STEP_FUNCTION_ARN | jq -r '.executionArn')
while true
do
    STATUS=$(aws stepfunctions describe-execution --execution-arn $EXECUTION_ARN | jq -r '.status')
    if [ $STATUS = "SUCCEEDED" ]; then
        exit 0
    elif [ $STATUS = "FAILED" ] || [ $STATUS = "TIMED_OUT" ] || [ $STATUS = "ABORTED" ]; then
        exit 1
    else
        sleep 10
        continue
    fi
done
```

To use resources that are deployed by the Application Stack like the Step Functions state machine ARN in the previous example:

1. Create a `CfnOutput` in your application stack with the value of your resource

```python
class EmrApplicationStack(cdk.Stack):
    def __init__(self, scope, id, _stage):
        super().__init__(scope, id)

        processing_state_machine = StateMachine(self, "ProcessingStateMachine")

        cdk.CfnOutput(self, "ProcessingStateMachineArn",
            value=processing_state_machine.state_machine_arn
        )
```

1. Pass an environment variable to the `SparkCICDPipeline` construct in the form of a key/value pair via `integTestEnv`:

* Key is the name of the environment variable used in the script: `STEP_FUNCTION_ARN` in the script example above.
* Value is the CloudFormation output name from the application stack: `ProcessingStateMachineArn` in the application stack example above.
* Add permissions required to run the integration tests script. In this example, `states:StartExecution` and `states:DescribeExecution`.

```python
dsf.processing.SparkEmrCICDPipeline(self, "SparkCICDPipeline",
    spark_application_name="SparkTest",
    application_stack_factory=EmrApplicationStackFactory(),
    integ_test_script="spark/integ.sh",
    integ_test_env={
        "STEP_FUNCTION_ARN": "ProcessingStateMachineArn"
    },
    integ_test_permissions=[
        PolicyStatement(
            actions=["states:StartExecution", "states:DescribeExecution"
            ],
            resources=["*"]
        )
    ]
)
```

# Spark EMR Containers Runtime

An EMR on EKS runtime with preconfigured EKS cluster.

## Overview

The constructs creates an EKS cluster, install the necessary controllers and enable it to be used by EMR on EKS service as described in this [documentation](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/setting-up-cluster-access.html). The following are the details of the components deployed.

* An EKS cluster (VPC configuration can be customized)
* A tooling nodegroup to run various tools including controllers
* Kubernetes controlers: EBS CSI Driver, Karpenter, ALB Ingress Controller, cert-manager
* Optional default Kaprenter `NodePools` and `EC2NodeClass` as listed [here](https://github.com/awslabs/data-solutions-framework-on-aws/tree/main/framework/src/processing/lib/spark-runtime/emr-containers/resources/k8s/karpenter-provisioner-config).
* An S3 bucket to store the pod templates for the `NodePools` created above.

Additionally, the construct exposes methods to facilitate the creation of EC2 capacity, Virtual Cluster and Execution roles.

## Usage

The code snippet below shows a usage example of the `SparkEmrContainersRuntime` construct.

```python
class ExampleSparkEmrContainersStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        # Layer must be changed according to the Kubernetes version used
        kubectl_layer = KubectlV27Layer(self, "kubectlLayer")

        emr_eks_cluster = SparkEmrContainersRuntime.get_or_create(self,
            eks_admin_role=Role.from_role_arn(self, "EksAdminRole", "arn:aws:iam::12345678912:role/role-name-with-path"),
            public_access_cIDRs=["10.0.0.0/32"],  # The list of public IP addresses from which the cluster can be accessible
            create_emr_on_eks_service_linked_role=True,  # if the the service linked role already exists set this to false
            kubectl_lambda_layer=kubectl_layer
        )

        s3_read = PolicyDocument(
            statements=[PolicyStatement(
                actions=["s3:GetObject"
                ],
                resources=["arn:aws:s3:::aws-data-analytics-workshop", "arn:aws:s3:::aws-data-analytics-workshop/*"
                ]
            )]
        )

        s3_read_policy = ManagedPolicy(self, "s3ReadPolicy",
            document=s3_read
        )

        virtual_cluster = emr_eks_cluster.add_emr_virtual_cluster(self,
            name="dailyjob",
            create_namespace=True,
            eks_namespace="dailyjobns"
        )

        exec_role = emr_eks_cluster.create_execution_role(self, "ExecRole", s3_read_policy, "dailyjobns", "s3ReadExecRole") # the IAM role name

        cdk.CfnOutput(self, "virtualClusterArn",
            value=virtual_cluster.attr_arn
        )

        cdk.CfnOutput(self, "execRoleArn",
            value=exec_role.role_arn
        )

        # Driver pod template
        cdk.CfnOutput(self, "driverPodTemplate",
            value=emr_eks_cluster.pod_template_s3_location_critical_driver
        )

        # Executor pod template
        cdk.CfnOutput(self, "executorPodTemplate",
            value=emr_eks_cluster.pod_template_s3_location_critical_executor
        )
```

The sceenshot below show how the cloudformation will look like once you deploy the example.

![Spark EMR Containers Cloudfromation Output](../../../website/static/img/emr-eks-construct-cloudformation-output.png)

You can execute the following command to run a sample job with the infratructure deployed using SparkEmrContainerRuntime:

```sh
aws emr-containers start-job-run \
--virtual-cluster-id FROM-CFNOUTPUT-VIRTUAL_CLUSTER_ID \
--name spark-pi \
--execution-role-arn FROM-CFNOUTPUT-jOB_EXECUTION_ROLE_ARN \
--release-label emr-7.0.0-latest \
--job-driver '{
    "sparkSubmitJobDriver": {
        "entryPoint": "s3://aws-data-analytics-workshops/emr-eks-workshop/scripts/pi.py",
        "sparkSubmitParameters": "--conf spark.executor.instances=8 --conf spark.executor.memory=2G --conf spark.executor.cores=2 --conf spark.driver.cores=1 --conf spark.kubernetes.driver.podTemplateFile=FROM-CFNOUTPUT-DRIVER-POD-TEMPLATE --conf spark.kubernetes.executor.podTemplateFile=FROM-CFNOUTPUT-EXECUTOR-POD-TEMPLATE"
        }
    }'
```

:::warning IAM role requirements

Make sure the role used for running has the correct [IAM policy](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonemroneksemrcontainers.html#amazonemroneksemrcontainers-actions-as-permissions) with `StartJobRun` permission to execute the job.

:::

### Isolating workloads on a shared cluster

With EMR on EKS you can leverage the same EKS cluster to run Spark jobs from multiple teams leveraging namespace segragation through the EMR virtual cluster. The `SparkEMRContainersRuntime` simplifies the creation of an EMR virtual cluster.
The `addEmrVirtualCluster()` method enables the EKS cluster to be used by EMR on EKS through the creation EMR on EKS virtual cluster.
The method configures the right Kubernetes RBAC as described [here](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/setting-up-cluster-access.html). It can optionally create the namespace for you.

```python
virtual_cluster = emr_eks_cluster.add_emr_virtual_cluster(self,
    name="dailyjob",
    create_namespace=True,
    eks_namespace="dailyjobns"
)

cdk.CfnOutput(self, "virtualClusterArn",
    value=virtual_cluster.attr_arn
)
```

### EC2 Capacity

The EC2 capacity to execute the jobs is defined with [Karpenter](https://karpenter.sh/docs/getting-started/) `NodePools` and `EC2NodeClass`. By default, the construct configure Karpenter `NodePools` and `EC2NodeClass` for 3 types of workloads:

* Critical workloads
* Shared workloads
* Notebook workloads
  You can opt out from their creation by setting the `default_nodes` to `False`.

To run EMR on EKS jobs on this EC2 capacity, the construct creates [Pod templates](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/pod-templates.html) and uploads them to an S3 bucket (created by the construct).
The pod template are provided for both the Spark driver and the Spark executors and for each of the workload types. They are configured to schedule the Spark pods on the corresponding Karpenter `NodePools` and `EC2NodeClass`.
The pod templates locations are stored as class attribute and can be exposed via CloudFormation outputs.
The usage example below shows how to provide these as CloudFormation output. The pod templates are referenced in your `spark configuration` that is part of your job defintion.

```python
emr_eks_cluster = SparkEmrContainersRuntime.get_or_create(self,
    eks_admin_role=Role.from_role_arn(self, "EksAdminRole", "arn:aws:iam::12345678912:role/role-name-with-path"),
    public_access_cIDRs=["10.0.0.0/32"],  # The list of public IP addresses from which the cluster can be accessible
    create_emr_on_eks_service_linked_role=True,  # if the the service linked role already exists set this to false
    kubectl_lambda_layer=kubectl_layer,
    default_nodes=True
)

# Driver pod template for critical workloads
cdk.CfnOutput(self, "driverPodTemplate",
    value=emr_eks_cluster.pod_template_s3_location_critical_driver
)

# Executor pod template for critical workloads
cdk.CfnOutput(self, "executorPodTemplate",
    value=emr_eks_cluster.pod_template_s3_location_critical_executor
)
```

The construct also exposes the `addKarpenterNodePoolAndNodeClass()` method to define your own EC2 capacity. This method takes a YAML file as defined in [Karpenter](https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/#5-create-nodepool) and apply it to the EKS cluster. You can consult an example [here](https://github.com/awslabs/data-solutions-framework-on-aws/blob/main/framework/src/processing/lib/spark-runtime/emr-containers/resources/k8s/karpenter-provisioner-config/v0.32.1/critical-provisioner.yml).

### Execution role

The execution role is the IAM role that is used by the Spark job to access AWS resources. For example, the job may need to access an S3 bucket that stores the source data or to which the job writes the data. The `createExecutionRole()` method simplifies the creation of an IAM role that can be used to execute a Spark job on the EKS cluster and in a specific EMR EKS virtual cluster namespace. The method attaches an IAM policy provided by the user and a policy to access the pod templates when using the default EC2 capacity.

```python
emr_eks_cluster.add_emr_virtual_cluster(self,
    name="dailyjob",
    create_namespace=True,
    eks_namespace="dailyjobns"
)

exec_role = emr_eks_cluster.create_execution_role(self, "ExecRole", s3_read_policy, "dailyjobns", "s3ReadExecRole")

cdk.CfnOutput(self, "execRoleArn",
    value=exec_role.role_arn
)
```

### Interactive endpoint

The interactive endpoint provides the capability for interactive clients like Amazon EMR Studio or a self-hosted Jupyter notebook to connect to Amazon EMR on EKS clusters to run interactive workloads. The interactive endpoint is backed by a Jupyter Enterprise Gateway that provides the remote kernel lifecycle management capability that interactive clients need.

```python
virtual_cluster = emr_eks_cluster.add_emr_virtual_cluster(self,
    name="dailyjob",
    create_namespace=True,
    eks_namespace="dailyjobns"
)

exec_role = emr_eks_cluster.create_execution_role(self, "ExecRole", s3_read_policy, "dailyjobns", "s3ReadExecRole")

interactive_session = emr_eks_cluster.add_interactive_endpoint(self, "interactiveSession",
    virtual_cluster_id=virtual_cluster.attr_id,
    managed_endpoint_name="interactiveSession",
    execution_role=exec_role
)

# Virtual Cluster ARN
cdk.CfnOutput(self, "virtualClusterArn",
    value=virtual_cluster.attr_arn
)

# Interactive session ARN
cdk.CfnOutput(self, "interactiveSessionArn",
    value=interactive_session.get_att_string("arn")
)
```

### Grant Job Execution

The Grant Job Execution allow you to provide an IAM role the rights to start the execution of a job and monitor it in a given virtual cluster. The policy attached will be as follow.

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Action": [
				"emr-containers:DescribeJobRun",
				"emr-containers:ListJobRuns"
			],
			"Resource": "arn:aws:emr-containers:REGION:ACCOUNT-ID:/virtualclusters/aaabbccmmm",
			"Effect": "Allow"
		},
		{
			"Condition": {
				"ArnEquals": {
					"emr-containers:ExecutionRoleArn": [
						"arn:aws:iam::ACCOUNT-ID:role/s3ReadExecRole"
					]
				}
			},
			"Action": "emr-containers:StartJobRun",
			"Resource": "arn:aws:emr-containers:REGION:ACCOUNT-ID:/virtualclusters/aaabbccmmm",
			"Effect": "Allow"
		},
		{
			"Action": "emr-containers:TagResource",
			"Resource": "arn:aws:emr-containers:REGION:ACCOUNT-ID:/virtualclusters/aaabbccmmm/jobruns/*",
			"Effect": "Allow"
		}
	]
}
```

```python
# IAM role that is used to start the execution and monitor its state
start_job_role = Role.from_role_name(self, "StartJobRole", "StartJobRole")

SparkEmrContainersRuntime.grant_start_job_execution(start_job_role, [exec_role.role_arn], virtual_cluster.attr_arn)
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
import aws_cdk.aws_codecommit as _aws_cdk_aws_codecommit_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_eks as _aws_cdk_aws_eks_ceddda9d
import aws_cdk.aws_emrcontainers as _aws_cdk_aws_emrcontainers_ceddda9d
import aws_cdk.aws_emrserverless as _aws_cdk_aws_emrserverless_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.aws_stepfunctions_tasks as _aws_cdk_aws_stepfunctions_tasks_ceddda9d
import aws_cdk.pipelines as _aws_cdk_pipelines_ceddda9d
import constructs as _constructs_77d1e7e8
from ..storage import AccessLogsBucket as _AccessLogsBucket_4c14c00a
from ..utils import (
    ApplicationStackFactory as _ApplicationStackFactory_52ae437f,
    Architecture as _Architecture_b811f66d,
)


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.EmrContainersRuntimeVersion"
)
class EmrContainersRuntimeVersion(enum.Enum):
    V7_0 = "V7_0"
    V6_15 = "V6_15"
    V6_14 = "V6_14"
    V6_13 = "V6_13"
    V6_12 = "V6_12"
    V6_11_1 = "V6_11_1"
    V6_11 = "V6_11"
    V6_10_1 = "V6_10_1"
    V6_10 = "V6_10"
    V6_9 = "V6_9"
    V6_8 = "V6_8"
    V6_7 = "V6_7"
    V6_6 = "V6_6"
    V6_5 = "V6_5"
    V6_4 = "V6_4"
    V6_3 = "V6_3"
    V6_2 = "V6_2"
    V5_33 = "V5_33"
    V5_32 = "V5_32"


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.EmrRuntimeVersion"
)
class EmrRuntimeVersion(enum.Enum):
    '''Enum defining the EMR version as defined in the `Amazon EMR documentation <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html>`_.'''

    V7_0 = "V7_0"
    V6_15 = "V6_15"
    V6_14 = "V6_14"
    V6_13 = "V6_13"
    V6_12 = "V6_12"
    V6_11_1 = "V6_11_1"
    V6_11 = "V6_11"
    V6_10_1 = "V6_10_1"
    V6_10 = "V6_10"
    V6_9 = "V6_9"
    V6_8 = "V6_8"
    V6_7 = "V6_7"
    V6_6 = "V6_6"
    V6_5 = "V6_5"
    V6_4 = "V6_4"
    V6_3 = "V6_3"
    V6_2 = "V6_2"
    V5_33 = "V5_33"
    V5_32 = "V5_32"


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.EmrVirtualClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "create_namespace": "createNamespace",
        "eks_namespace": "eksNamespace",
        "set_namespace_resource_quota": "setNamespaceResourceQuota",
        "tags": "tags",
    },
)
class EmrVirtualClusterProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        create_namespace: typing.Optional[builtins.bool] = None,
        eks_namespace: typing.Optional[builtins.str] = None,
        set_namespace_resource_quota: typing.Optional[builtins.bool] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''The properties for the ``EmrVirtualCluster`` Construct class.

        :param name: The name of the Amazon EMR Virtual Cluster to be created.
        :param create_namespace: The flag to create EKS namespace. Default: - Do not create the namespace
        :param eks_namespace: The name of the EKS namespace to be linked to the EMR virtual cluster. Default: - Use the default namespace
        :param set_namespace_resource_quota: The namespace will be create with ResourceQuota and LimitRange As defined here https://github.com/awslabs/data-solutions-framework-on-aws/blob/main/framework/src/processing/lib/spark-runtime/emr-containers/resources/k8s/resource-management.yaml. Default: - true
        :param tags: The tags assigned to the Virtual Cluster. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3eacff78ea6ec7021e0b59026f040a0268c2232c203599c99b35d629a6b01cd4)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument create_namespace", value=create_namespace, expected_type=type_hints["create_namespace"])
            check_type(argname="argument eks_namespace", value=eks_namespace, expected_type=type_hints["eks_namespace"])
            check_type(argname="argument set_namespace_resource_quota", value=set_namespace_resource_quota, expected_type=type_hints["set_namespace_resource_quota"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if create_namespace is not None:
            self._values["create_namespace"] = create_namespace
        if eks_namespace is not None:
            self._values["eks_namespace"] = eks_namespace
        if set_namespace_resource_quota is not None:
            self._values["set_namespace_resource_quota"] = set_namespace_resource_quota
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Amazon EMR Virtual Cluster to be created.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_namespace(self) -> typing.Optional[builtins.bool]:
        '''The flag to create EKS namespace.

        :default: - Do not create the namespace
        '''
        result = self._values.get("create_namespace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eks_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the EKS namespace to be linked to the EMR virtual cluster.

        :default: - Use the default namespace
        '''
        result = self._values.get("eks_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def set_namespace_resource_quota(self) -> typing.Optional[builtins.bool]:
        '''The namespace will be create with ResourceQuota and LimitRange As defined here https://github.com/awslabs/data-solutions-framework-on-aws/blob/main/framework/src/processing/lib/spark-runtime/emr-containers/resources/k8s/resource-management.yaml.

        :default: - true
        '''
        result = self._values.get("set_namespace_resource_quota")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The tags assigned to the Virtual Cluster.

        :default: - none
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrVirtualClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.KarpenterVersion"
)
class KarpenterVersion(enum.Enum):
    '''The list of supported Karpenter versions as defined `here <https://github.com/aws/karpenter/releases>`_ At this time only v0.32.1 is supported.'''

    V0_32_1 = "V0_32_1"


class PySparkApplicationPackage(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.PySparkApplicationPackage",
):
    '''A construct that takes your PySpark application, packages its virtual environment and uploads it along its entrypoint to an Amazon S3 bucket This construct requires Docker daemon installed locally to run.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Processing/pyspark-application-package

    Example::

        pyspark_packer = dsf.processing.PySparkApplicationPackage(self, "pysparkPacker",
            application_name="my-pyspark",
            entrypoint_path="/Users/my-user/my-spark-job/app/app-pyspark.py",
            dependencies_folder="/Users/my-user/my-spark-job/app",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_name: builtins.str,
        entrypoint_path: builtins.str,
        artifacts_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        asset_upload_memory_size: typing.Optional[jsii.Number] = None,
        asset_upload_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        asset_upload_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        dependencies_folder: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        venv_archive_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param application_name: The name of the PySpark application. This name is used as a parent directory in S3 to store the entrypoint and the optional virtual environment archive
        :param entrypoint_path: The source path in the code base where the entrypoint is stored. example ``~/my-project/src/entrypoint.py``
        :param artifacts_bucket: The S3 bucket where to upload the artifacts of the Spark Job This is where the entry point and archive of the virtual environment will be stored. Default: - An S3 Bucket is created
        :param asset_upload_memory_size: The memory size (in MiB) used by the Lambda function to upload and unzip the assets (entrypoint and dependencies). If you are deploying large files, you will need to increase this number accordingly. Default: - 512 MB
        :param asset_upload_role: The IAM Role used by the Lambda function to upload assets (entrypoint and dependencies). Additional permissions would be granted to this role such as S3 Bucket permissions. Default: - A new Role would be created with least privilege permissions
        :param asset_upload_storage_size: The ephemeral storage size used by the Lambda function to upload and unzip the assets (entrypoint and dependencies). If you are deploying large files, you will need to increase this number accordingly. Default: - 1024 MB
        :param dependencies_folder: The source directory where ``requirements.txt`` or ``pyproject.toml`` file is stored. These files are used to install external AND internal Python packages. If your PySpark application has more than one Python file, you need to `package your Python project <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_. This location must also contain a ``Dockerfile`` that can `create a virtual environment and build an archive <https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/using-python-libraries.html#building-python-virtual-env>`_. Default: - No dependencies (internal or external) are packaged. Only the entrypoint is used in the Spark Job.
        :param removal_policy: The removal policy when deleting the CDK resource. Resources like Amazon cloudwatch log or Amazon S3 bucket. If DESTROY is selected, the context value '@data-solutions-framework-on-aws/removeDataOnDestroy' in the 'cdk.json' or 'cdk.context.json' must be set to true. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param venv_archive_path: The path of the Python virtual environment archive generated in the Docker container. This is the output path used in the ``venv-pack -o`` command in your Dockerfile. Default: - No virtual environment archive is packaged. Only the entrypoint can be used in the Spark Job. It is required if the ``dependenciesFolder`` is provided.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f090fca4792f38c321086e79a1854d7d328b1646646610fa2828c5a8d7def302)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PySparkApplicationPackageProps(
            application_name=application_name,
            entrypoint_path=entrypoint_path,
            artifacts_bucket=artifacts_bucket,
            asset_upload_memory_size=asset_upload_memory_size,
            asset_upload_role=asset_upload_role,
            asset_upload_storage_size=asset_upload_storage_size,
            dependencies_folder=dependencies_folder,
            removal_policy=removal_policy,
            venv_archive_path=venv_archive_path,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ARTIFACTS_PREFIX")
    def ARTIFACTS_PREFIX(cls) -> builtins.str:
        '''The prefix used to store artifacts on the artifact bucket.'''
        return typing.cast(builtins.str, jsii.sget(cls, "ARTIFACTS_PREFIX"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="artifactsBucket")
    def artifacts_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 Bucket for storing the artifacts (entrypoint and virtual environment archive).'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "artifactsBucket"))

    @builtins.property
    @jsii.member(jsii_name="assetUploadManagedPolicy")
    def asset_upload_managed_policy(self) -> _aws_cdk_aws_iam_ceddda9d.IManagedPolicy:
        '''The IAM Managed Policy used by the custom resource for the assets deployment.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IManagedPolicy, jsii.get(self, "assetUploadManagedPolicy"))

    @builtins.property
    @jsii.member(jsii_name="assetUploadRole")
    def asset_upload_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role used by the BucketDeployment to upload the artifacts to an s3 bucket.

        In case you provide your own S3 Bucket for storing the artifacts (entrypoint and virtual environment archive),
        you must provide S3 write access to this role to upload the artifacts.
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "assetUploadRole"))

    @builtins.property
    @jsii.member(jsii_name="entrypointUri")
    def entrypoint_uri(self) -> builtins.str:
        '''The location (generally it's an S3 URI) where the entry point is saved.

        You can pass this location to your Spark job.
        '''
        return typing.cast(builtins.str, jsii.get(self, "entrypointUri"))

    @builtins.property
    @jsii.member(jsii_name="artifactsAccessLogsBucket")
    def artifacts_access_logs_bucket(
        self,
    ) -> typing.Optional[_AccessLogsBucket_4c14c00a]:
        '''The access logs bucket to log accesses on the artifacts bucket.'''
        return typing.cast(typing.Optional[_AccessLogsBucket_4c14c00a], jsii.get(self, "artifactsAccessLogsBucket"))

    @builtins.property
    @jsii.member(jsii_name="sparkVenvConf")
    def spark_venv_conf(self) -> typing.Optional[builtins.str]:
        '''The Spark Config containing the configuration of virtual environment archive with all dependencies.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sparkVenvConf"))

    @builtins.property
    @jsii.member(jsii_name="venvArchiveUri")
    def venv_archive_uri(self) -> typing.Optional[builtins.str]:
        '''The location (generally an S3 URI) where the archive of the Python virtual environment with all dependencies is stored.

        You can pass this location to your Spark job.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "venvArchiveUri"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.PySparkApplicationPackageProps",
    jsii_struct_bases=[],
    name_mapping={
        "application_name": "applicationName",
        "entrypoint_path": "entrypointPath",
        "artifacts_bucket": "artifactsBucket",
        "asset_upload_memory_size": "assetUploadMemorySize",
        "asset_upload_role": "assetUploadRole",
        "asset_upload_storage_size": "assetUploadStorageSize",
        "dependencies_folder": "dependenciesFolder",
        "removal_policy": "removalPolicy",
        "venv_archive_path": "venvArchivePath",
    },
)
class PySparkApplicationPackageProps:
    def __init__(
        self,
        *,
        application_name: builtins.str,
        entrypoint_path: builtins.str,
        artifacts_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        asset_upload_memory_size: typing.Optional[jsii.Number] = None,
        asset_upload_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        asset_upload_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        dependencies_folder: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        venv_archive_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for the ``PySparkApplicationPackage`` construct.

        :param application_name: The name of the PySpark application. This name is used as a parent directory in S3 to store the entrypoint and the optional virtual environment archive
        :param entrypoint_path: The source path in the code base where the entrypoint is stored. example ``~/my-project/src/entrypoint.py``
        :param artifacts_bucket: The S3 bucket where to upload the artifacts of the Spark Job This is where the entry point and archive of the virtual environment will be stored. Default: - An S3 Bucket is created
        :param asset_upload_memory_size: The memory size (in MiB) used by the Lambda function to upload and unzip the assets (entrypoint and dependencies). If you are deploying large files, you will need to increase this number accordingly. Default: - 512 MB
        :param asset_upload_role: The IAM Role used by the Lambda function to upload assets (entrypoint and dependencies). Additional permissions would be granted to this role such as S3 Bucket permissions. Default: - A new Role would be created with least privilege permissions
        :param asset_upload_storage_size: The ephemeral storage size used by the Lambda function to upload and unzip the assets (entrypoint and dependencies). If you are deploying large files, you will need to increase this number accordingly. Default: - 1024 MB
        :param dependencies_folder: The source directory where ``requirements.txt`` or ``pyproject.toml`` file is stored. These files are used to install external AND internal Python packages. If your PySpark application has more than one Python file, you need to `package your Python project <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_. This location must also contain a ``Dockerfile`` that can `create a virtual environment and build an archive <https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/using-python-libraries.html#building-python-virtual-env>`_. Default: - No dependencies (internal or external) are packaged. Only the entrypoint is used in the Spark Job.
        :param removal_policy: The removal policy when deleting the CDK resource. Resources like Amazon cloudwatch log or Amazon S3 bucket. If DESTROY is selected, the context value '@data-solutions-framework-on-aws/removeDataOnDestroy' in the 'cdk.json' or 'cdk.context.json' must be set to true. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param venv_archive_path: The path of the Python virtual environment archive generated in the Docker container. This is the output path used in the ``venv-pack -o`` command in your Dockerfile. Default: - No virtual environment archive is packaged. Only the entrypoint can be used in the Spark Job. It is required if the ``dependenciesFolder`` is provided.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a9c55335a32c81401f78a9db5843ed203f0bdbfd4bfbaaafd82da582d424426)
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument entrypoint_path", value=entrypoint_path, expected_type=type_hints["entrypoint_path"])
            check_type(argname="argument artifacts_bucket", value=artifacts_bucket, expected_type=type_hints["artifacts_bucket"])
            check_type(argname="argument asset_upload_memory_size", value=asset_upload_memory_size, expected_type=type_hints["asset_upload_memory_size"])
            check_type(argname="argument asset_upload_role", value=asset_upload_role, expected_type=type_hints["asset_upload_role"])
            check_type(argname="argument asset_upload_storage_size", value=asset_upload_storage_size, expected_type=type_hints["asset_upload_storage_size"])
            check_type(argname="argument dependencies_folder", value=dependencies_folder, expected_type=type_hints["dependencies_folder"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument venv_archive_path", value=venv_archive_path, expected_type=type_hints["venv_archive_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_name": application_name,
            "entrypoint_path": entrypoint_path,
        }
        if artifacts_bucket is not None:
            self._values["artifacts_bucket"] = artifacts_bucket
        if asset_upload_memory_size is not None:
            self._values["asset_upload_memory_size"] = asset_upload_memory_size
        if asset_upload_role is not None:
            self._values["asset_upload_role"] = asset_upload_role
        if asset_upload_storage_size is not None:
            self._values["asset_upload_storage_size"] = asset_upload_storage_size
        if dependencies_folder is not None:
            self._values["dependencies_folder"] = dependencies_folder
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if venv_archive_path is not None:
            self._values["venv_archive_path"] = venv_archive_path

    @builtins.property
    def application_name(self) -> builtins.str:
        '''The name of the PySpark application.

        This name is used as a parent directory in S3 to store the entrypoint and the optional virtual environment archive
        '''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def entrypoint_path(self) -> builtins.str:
        '''The source path in the code base where the entrypoint is stored.

        example ``~/my-project/src/entrypoint.py``
        '''
        result = self._values.get("entrypoint_path")
        assert result is not None, "Required property 'entrypoint_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The S3 bucket where to upload the artifacts of the Spark Job This is where the entry point and archive of the virtual environment will be stored.

        :default: - An S3 Bucket is created
        '''
        result = self._values.get("artifacts_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def asset_upload_memory_size(self) -> typing.Optional[jsii.Number]:
        '''The memory size (in MiB) used by the Lambda function to upload and unzip the assets (entrypoint and dependencies).

        If you are deploying large files, you will need to increase this number accordingly.

        :default: - 512 MB
        '''
        result = self._values.get("asset_upload_memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def asset_upload_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Lambda function to upload assets (entrypoint and dependencies).

        Additional permissions would be granted to this role such as S3 Bucket permissions.

        :default: - A new Role would be created with least privilege permissions
        '''
        result = self._values.get("asset_upload_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def asset_upload_storage_size(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''The ephemeral storage size used by the Lambda function to upload and unzip the assets (entrypoint and dependencies).

        If you are deploying large files, you will need to increase this number accordingly.

        :default: - 1024 MB
        '''
        result = self._values.get("asset_upload_storage_size")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def dependencies_folder(self) -> typing.Optional[builtins.str]:
        '''The source directory where ``requirements.txt`` or ``pyproject.toml`` file is stored. These files are used to install external AND internal Python packages. If your PySpark application has more than one Python file, you need to `package your Python project <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_. This location must also contain a ``Dockerfile`` that can `create a virtual environment and build an archive <https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/using-python-libraries.html#building-python-virtual-env>`_.

        :default: - No dependencies (internal or external) are packaged. Only the entrypoint is used in the Spark Job.
        '''
        result = self._values.get("dependencies_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        Resources like Amazon cloudwatch log or Amazon S3 bucket.
        If DESTROY is selected, the context value '@data-solutions-framework-on-aws/removeDataOnDestroy'
        in the 'cdk.json' or 'cdk.context.json' must be set to true.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def venv_archive_path(self) -> typing.Optional[builtins.str]:
        '''The path of the Python virtual environment archive generated in the Docker container.

        This is the output path used in the ``venv-pack -o`` command in your Dockerfile.

        :default: - No virtual environment archive is packaged. Only the entrypoint can be used in the Spark Job. It is required if the ``dependenciesFolder`` is provided.
        '''
        result = self._values.get("venv_archive_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PySparkApplicationPackageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SparkEmrCICDPipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrCICDPipeline",
):
    '''A CICD Pipeline to test and deploy a Spark application on Amazon EMR in cross-account environments using CDK Pipelines.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Processing/spark-cicd-pipeline
    :exampleMetadata: fixture=imports-only

    Example::

        from aws_cdk.aws_s3 import Bucket
        
        
        class MyApplicationStack(cdk.Stack):
            def __init__(self, scope, *, stage, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None, crossRegionReferences=None, permissionsBoundary=None, suppressTemplateIndentation=None):
                super().__init__(scope, "MyApplicationStack")
                bucket = Bucket(self, "TestBucket",
                    auto_delete_objects=True,
                    removal_policy=cdk.RemovalPolicy.DESTROY
                )
                cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        
        class MyStackFactory(dsf.utils.ApplicationStackFactory):
            def create_stack(self, scope, stage):
                return MyApplicationStack(scope, stage=stage)
        
        class MyCICDStack(cdk.Stack):
            def __init__(self, scope, id):
                super().__init__(scope, id)
                dsf.processing.SparkEmrCICDPipeline(self, "TestConstruct",
                    spark_application_name="test",
                    application_stack_factory=MyStackFactory(),
                    cdk_application_path="cdk/",
                    spark_application_path="spark/",
                    spark_image=dsf.processing.SparkImage.EMR_6_12,
                    integ_test_script="cdk/integ-test.sh",
                    integ_test_env={
                        "TEST_BUCKET": "BucketName"
                    }
                )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_stack_factory: _ApplicationStackFactory_52ae437f,
        spark_application_name: builtins.str,
        cdk_application_path: typing.Optional[builtins.str] = None,
        integ_test_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        integ_test_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        integ_test_script: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        spark_application_path: typing.Optional[builtins.str] = None,
        spark_image: typing.Optional["SparkImage"] = None,
    ) -> None:
        '''Construct a new instance of the SparkCICDPipeline class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param application_stack_factory: The application CDK Stack to deploy in the different CDK Pipelines Stages.
        :param spark_application_name: The name of the Spark application to be deployed.
        :param cdk_application_path: The path to the folder that contains the CDK Application. Default: - The root of the repository
        :param integ_test_env: The environment variables to create from the Application CDK Stack outputs and to pass to the integration tests. This is used to interact with resources created by the Application CDK Stack from within the integration tests script. Key is the name of the environment variable to create. Value is generally a CfnOutput name from the Application CDK Stack. Default: - No environment variables
        :param integ_test_permissions: The IAM Policy statements to add permissions for running the integration tests. Default: - No permissions
        :param integ_test_script: The path to the Shell script that contains integration tests. Default: - No integration tests are run
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param spark_application_path: The path to the folder that contains the Spark Application. Default: - The root of the repository
        :param spark_image: The EMR Spark image to use to run the unit tests. Default: - `DEFAULT_SPARK_IMAGE <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L51>`_
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38571fed7c1c1182e0e221f9c4b475a7538d4819638aeacc0a37098ed8937873)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SparkEmrCICDPipelineProps(
            application_stack_factory=application_stack_factory,
            spark_application_name=spark_application_name,
            cdk_application_path=cdk_application_path,
            integ_test_env=integ_test_env,
            integ_test_permissions=integ_test_permissions,
            integ_test_script=integ_test_script,
            removal_policy=removal_policy,
            spark_application_path=spark_application_path,
            spark_image=spark_image,
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
    @jsii.member(jsii_name="artifactAccessLogsBucket")
    def artifact_access_logs_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 Bucket for storing the access logs on the artifact S3 Bucket.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "artifactAccessLogsBucket"))

    @builtins.property
    @jsii.member(jsii_name="artifactBucket")
    def artifact_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 Bucket for storing the artifacts.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "artifactBucket"))

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> _aws_cdk_pipelines_ceddda9d.CodePipeline:
        '''The CodePipeline created as part of the Spark CICD Pipeline.'''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodePipeline, jsii.get(self, "pipeline"))

    @builtins.property
    @jsii.member(jsii_name="pipelineLogGroup")
    def pipeline_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for storing the CodePipeline logs.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "pipelineLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> _aws_cdk_aws_codecommit_ceddda9d.Repository:
        '''The CodeCommit Repository created as part of the Spark CICD Pipeline.'''
        return typing.cast(_aws_cdk_aws_codecommit_ceddda9d.Repository, jsii.get(self, "repository"))

    @builtins.property
    @jsii.member(jsii_name="integrationTestStage")
    def integration_test_stage(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep]:
        '''The CodeBuild Step for the staging stage.'''
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildStep], jsii.get(self, "integrationTestStage"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrCICDPipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "application_stack_factory": "applicationStackFactory",
        "spark_application_name": "sparkApplicationName",
        "cdk_application_path": "cdkApplicationPath",
        "integ_test_env": "integTestEnv",
        "integ_test_permissions": "integTestPermissions",
        "integ_test_script": "integTestScript",
        "removal_policy": "removalPolicy",
        "spark_application_path": "sparkApplicationPath",
        "spark_image": "sparkImage",
    },
)
class SparkEmrCICDPipelineProps:
    def __init__(
        self,
        *,
        application_stack_factory: _ApplicationStackFactory_52ae437f,
        spark_application_name: builtins.str,
        cdk_application_path: typing.Optional[builtins.str] = None,
        integ_test_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        integ_test_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        integ_test_script: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        spark_application_path: typing.Optional[builtins.str] = None,
        spark_image: typing.Optional["SparkImage"] = None,
    ) -> None:
        '''Properties for the ``SparkEmrCICDPipeline`` construct.

        :param application_stack_factory: The application CDK Stack to deploy in the different CDK Pipelines Stages.
        :param spark_application_name: The name of the Spark application to be deployed.
        :param cdk_application_path: The path to the folder that contains the CDK Application. Default: - The root of the repository
        :param integ_test_env: The environment variables to create from the Application CDK Stack outputs and to pass to the integration tests. This is used to interact with resources created by the Application CDK Stack from within the integration tests script. Key is the name of the environment variable to create. Value is generally a CfnOutput name from the Application CDK Stack. Default: - No environment variables
        :param integ_test_permissions: The IAM Policy statements to add permissions for running the integration tests. Default: - No permissions
        :param integ_test_script: The path to the Shell script that contains integration tests. Default: - No integration tests are run
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param spark_application_path: The path to the folder that contains the Spark Application. Default: - The root of the repository
        :param spark_image: The EMR Spark image to use to run the unit tests. Default: - `DEFAULT_SPARK_IMAGE <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L51>`_
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ed1ce57c4d326181a7695ce8cc994691b5a683bea0b04d81008a11d627ea7c3)
            check_type(argname="argument application_stack_factory", value=application_stack_factory, expected_type=type_hints["application_stack_factory"])
            check_type(argname="argument spark_application_name", value=spark_application_name, expected_type=type_hints["spark_application_name"])
            check_type(argname="argument cdk_application_path", value=cdk_application_path, expected_type=type_hints["cdk_application_path"])
            check_type(argname="argument integ_test_env", value=integ_test_env, expected_type=type_hints["integ_test_env"])
            check_type(argname="argument integ_test_permissions", value=integ_test_permissions, expected_type=type_hints["integ_test_permissions"])
            check_type(argname="argument integ_test_script", value=integ_test_script, expected_type=type_hints["integ_test_script"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument spark_application_path", value=spark_application_path, expected_type=type_hints["spark_application_path"])
            check_type(argname="argument spark_image", value=spark_image, expected_type=type_hints["spark_image"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_stack_factory": application_stack_factory,
            "spark_application_name": spark_application_name,
        }
        if cdk_application_path is not None:
            self._values["cdk_application_path"] = cdk_application_path
        if integ_test_env is not None:
            self._values["integ_test_env"] = integ_test_env
        if integ_test_permissions is not None:
            self._values["integ_test_permissions"] = integ_test_permissions
        if integ_test_script is not None:
            self._values["integ_test_script"] = integ_test_script
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if spark_application_path is not None:
            self._values["spark_application_path"] = spark_application_path
        if spark_image is not None:
            self._values["spark_image"] = spark_image

    @builtins.property
    def application_stack_factory(self) -> _ApplicationStackFactory_52ae437f:
        '''The application CDK Stack to deploy in the different CDK Pipelines Stages.'''
        result = self._values.get("application_stack_factory")
        assert result is not None, "Required property 'application_stack_factory' is missing"
        return typing.cast(_ApplicationStackFactory_52ae437f, result)

    @builtins.property
    def spark_application_name(self) -> builtins.str:
        '''The name of the Spark application to be deployed.'''
        result = self._values.get("spark_application_name")
        assert result is not None, "Required property 'spark_application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cdk_application_path(self) -> typing.Optional[builtins.str]:
        '''The path to the folder that contains the CDK Application.

        :default: - The root of the repository
        '''
        result = self._values.get("cdk_application_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integ_test_env(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The environment variables to create from the Application CDK Stack outputs and to pass to the integration tests.

        This is used to interact with resources created by the Application CDK Stack from within the integration tests script.
        Key is the name of the environment variable to create. Value is generally a CfnOutput name from the Application CDK Stack.

        :default: - No environment variables
        '''
        result = self._values.get("integ_test_env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def integ_test_permissions(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''The IAM Policy statements to add permissions for running the integration tests.

        :default: - No permissions
        '''
        result = self._values.get("integ_test_permissions")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def integ_test_script(self) -> typing.Optional[builtins.str]:
        '''The path to the Shell script that contains integration tests.

        :default: - No integration tests are run
        '''
        result = self._values.get("integ_test_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def spark_application_path(self) -> typing.Optional[builtins.str]:
        '''The path to the folder that contains the Spark Application.

        :default: - The root of the repository
        '''
        result = self._values.get("spark_application_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spark_image(self) -> typing.Optional["SparkImage"]:
        '''The EMR Spark image to use to run the unit tests.

        :default: - `DEFAULT_SPARK_IMAGE <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L51>`_
        '''
        result = self._values.get("spark_image")
        return typing.cast(typing.Optional["SparkImage"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrCICDPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SparkEmrContainersRuntime(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrContainersRuntime",
):
    '''A construct to create an EKS cluster, configure it and enable it with EMR on EKS.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Processing/spark-emr-containers-runtime

    Example::

        from aws_cdk.aws_iam import ManagedPolicy, PolicyDocument, PolicyStatement
        from aws_cdk.lambda_layer_kubectl_v27 import KubectlV27Layer
        
        
        kubectl_layer = KubectlV27Layer(self, "kubectlLayer")
        
        emr_eks_cluster = dsf.processing.SparkEmrContainersRuntime.get_or_create(self,
            public_access_cIDRs=["10.0.0.0/16"],
            kubectl_lambda_layer=kubectl_layer
        )
        
        virtual_cluster = emr_eks_cluster.add_emr_virtual_cluster(self,
            name="example",
            create_namespace=True,
            eks_namespace="example"
        )
        
        s3_read = PolicyDocument(
            statements=[PolicyStatement(
                actions=["s3:GetObject"
                ],
                resources=["arn:aws:s3:::aws-data-analytics-workshop"]
            )]
        )
        
        s3_read_policy = ManagedPolicy(self, "s3ReadPolicy",
            document=s3_read
        )
        
        exec_role = emr_eks_cluster.create_execution_role(self, "ExecRole", s3_read_policy, "example", "s3ReadExecRole")
    '''

    @jsii.member(jsii_name="getOrCreate")
    @builtins.classmethod
    def get_or_create(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        *,
        kubectl_lambda_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
        public_access_cid_rs: typing.Sequence[builtins.str],
        create_emr_on_eks_service_linked_role: typing.Optional[builtins.bool] = None,
        default_nodes: typing.Optional[builtins.bool] = None,
        ec2_instance_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        eks_admin_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        eks_cluster: typing.Optional[_aws_cdk_aws_eks_ceddda9d.Cluster] = None,
        eks_cluster_name: typing.Optional[builtins.str] = None,
        eks_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        karpenter_version: typing.Optional[KarpenterVersion] = None,
        kubernetes_version: typing.Optional[_aws_cdk_aws_eks_ceddda9d.KubernetesVersion] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
    ) -> "SparkEmrContainersRuntime":
        '''Get an existing EmrEksCluster based on the cluster name property or create a new one only one EKS cluster can exist per stack.

        :param scope: the CDK scope used to search or create the cluster.
        :param kubectl_lambda_layer: The Lambda Layer with Kubectl to use for EKS Cluster setup. Starting k8s 1.22, CDK no longer bundle the Kubectl layer with the code due to breaking npm package size. A layer needs to be passed to the Construct. The CDK `documentation <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_eks.KubernetesVersion.html#static-v1_22>`_ contains the libraries that you should add for the right Kubernetes version.
        :param public_access_cid_rs: The CIDR blocks that are allowed to access to your cluster’s public Kubernetes API server endpoint.
        :param create_emr_on_eks_service_linked_role: Flag to create an IAM Service Linked Role for EMR on EKS. Default: - true
        :param default_nodes: The flag to create default Karpenter Node Provisioners for: * Critical jobs which use on-demand instances, high speed disks and workload isolation * Shared workloads which use EC2 Spot Instances and no isolation to optimize costs * Notebooks which leverage a cost optimized configuration for running EMR managed endpoints and spark drivers/executors. Default: - true
        :param ec2_instance_role: The IAM Role used for the cluster nodes instance profile. Default: - A role is created with AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryReadOnly, AmazonSSMManagedInstanceCore and AmazonEKS_CNI_Policy AWS managed policies.
        :param eks_admin_role: The IAM Role to configure in the EKS master roles. It will give access to kubernetes cluster from the AWS console. You will use this role to manage the EKS cluster and grant other access to it. Default: - An admin role must be passed if ``eksCluster`` property is not set.
        :param eks_cluster: The EKS Cluster to setup EMR on. The cluster needs to be created in the same CDK Stack. If the EKS Cluster is provided, the cluster AddOns and all the controllers (ALB Ingress controller, Karpenter...) need to be configured. When providing an EKS cluster, the methods for adding nodegroups can still be used. They implement the best practices for running Spark on EKS. Default: - An EKS Cluster is created
        :param eks_cluster_name: The name of the EKS cluster to create. Default: - The `DEFAULT_CLUSTER_NAME <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/spark-runtime/emr-containers/spark-emr-containers-runtime.ts#L65>`_
        :param eks_vpc: The VPC to use when creating the EKS cluster. VPC should have at least two private and public subnets in different Availability Zones. All private subnets must have the following tags: - 'for-use-with-amazon-emr-managed-policies'='true' - 'kubernetes.io/role/internal-elb'='1' All public subnets must have the following tag: - 'kubernetes.io/role/elb'='1' Cannot be combined with ``vpcCidr``. If combined, ``vpcCidr`` takes precedence and a new VPC is created. Default: - A new VPC is created.
        :param karpenter_version: The Karpenter version to use for autoscaling nodes in the EKS Cluster. Default: - `DEFAULT_KARPENTER_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/karpenter-releases.ts#L11>`_
        :param kubernetes_version: The Kubernetes version used to create the EKS Cluster. Default: - `DEFAULT_EKS_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/spark-runtime/emr-containers/spark-emr-containers-runtime.ts#L61>`_
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param tags: The tags assigned to the EKS cluster. Default: - none
        :param vpc_cidr: The CIDR of the VPC to use when creating the EKS cluster. If provided, a VPC with three public subnets and three private subnets is created. The size of the private subnets is four time the one of the public subnet. Default: - The CIDR 10.0.0.0/16 is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a77fbf2d70f2dbc9f109068a582011e2e95e47ce83ad5a5851a10a01d18fdd7c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props = SparkEmrContainersRuntimeProps(
            kubectl_lambda_layer=kubectl_lambda_layer,
            public_access_cid_rs=public_access_cid_rs,
            create_emr_on_eks_service_linked_role=create_emr_on_eks_service_linked_role,
            default_nodes=default_nodes,
            ec2_instance_role=ec2_instance_role,
            eks_admin_role=eks_admin_role,
            eks_cluster=eks_cluster,
            eks_cluster_name=eks_cluster_name,
            eks_vpc=eks_vpc,
            karpenter_version=karpenter_version,
            kubernetes_version=kubernetes_version,
            removal_policy=removal_policy,
            tags=tags,
            vpc_cidr=vpc_cidr,
        )

        return typing.cast("SparkEmrContainersRuntime", jsii.sinvoke(cls, "getOrCreate", [scope, props]))

    @jsii.member(jsii_name="grantStartJobExecution")
    @builtins.classmethod
    def grant_start_job_execution(
        cls,
        start_job_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        execution_role_arn: typing.Sequence[builtins.str],
        virtual_cluster_arn: builtins.str,
    ) -> None:
        '''A static method granting the right to start and monitor a job to an IAM Role.

        The method will scope the following actions ``DescribeJobRun``, ``TagResource`` and ``ListJobRuns`` to the provided virtual cluster.
        It will also scope ``StartJobRun`` as defined in the
        `EMR on EKS official documentation <https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/iam-execution-role.html>`_

        :param start_job_role: the role that will call the start job api and which needs to have the iam:PassRole permission.
        :param execution_role_arn: the role used by EMR on EKS to access resources during the job execution.
        :param virtual_cluster_arn: the EMR Virtual Cluster ARN to which the job is submitted.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__931f90ff0171c67483277d67df76d04a03cf1132d70869f146ea53d6a1c92fce)
            check_type(argname="argument start_job_role", value=start_job_role, expected_type=type_hints["start_job_role"])
            check_type(argname="argument execution_role_arn", value=execution_role_arn, expected_type=type_hints["execution_role_arn"])
            check_type(argname="argument virtual_cluster_arn", value=virtual_cluster_arn, expected_type=type_hints["virtual_cluster_arn"])
        return typing.cast(None, jsii.sinvoke(cls, "grantStartJobExecution", [start_job_role, execution_role_arn, virtual_cluster_arn]))

    @jsii.member(jsii_name="addEmrVirtualCluster")
    def add_emr_virtual_cluster(
        self,
        scope: _constructs_77d1e7e8.Construct,
        *,
        name: builtins.str,
        create_namespace: typing.Optional[builtins.bool] = None,
        eks_namespace: typing.Optional[builtins.str] = None,
        set_namespace_resource_quota: typing.Optional[builtins.bool] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> _aws_cdk_aws_emrcontainers_ceddda9d.CfnVirtualCluster:
        '''Add a new Amazon EMR Virtual Cluster linked to Amazon EKS Cluster.

        :param scope: of the stack where virtual cluster is deployed.
        :param name: The name of the Amazon EMR Virtual Cluster to be created.
        :param create_namespace: The flag to create EKS namespace. Default: - Do not create the namespace
        :param eks_namespace: The name of the EKS namespace to be linked to the EMR virtual cluster. Default: - Use the default namespace
        :param set_namespace_resource_quota: The namespace will be create with ResourceQuota and LimitRange As defined here https://github.com/awslabs/data-solutions-framework-on-aws/blob/main/framework/src/processing/lib/spark-runtime/emr-containers/resources/k8s/resource-management.yaml. Default: - true
        :param tags: The tags assigned to the Virtual Cluster. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__927fa0229d8dda7caa502f18c7a9f51981e71e4c0cc270f54d8f67c054db1634)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        options = EmrVirtualClusterProps(
            name=name,
            create_namespace=create_namespace,
            eks_namespace=eks_namespace,
            set_namespace_resource_quota=set_namespace_resource_quota,
            tags=tags,
        )

        return typing.cast(_aws_cdk_aws_emrcontainers_ceddda9d.CfnVirtualCluster, jsii.invoke(self, "addEmrVirtualCluster", [scope, options]))

    @jsii.member(jsii_name="addInteractiveEndpoint")
    def add_interactive_endpoint(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        managed_endpoint_name: builtins.str,
        virtual_cluster_id: builtins.str,
        configuration_overrides: typing.Any = None,
        emr_on_eks_version: typing.Optional[EmrContainersRuntimeVersion] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a new Amazon EMR managed endpoint to be used with Amazon EMR Virtual Cluster .

        CfnOutput can be customized.

        :param scope: the scope of the stack where managed endpoint is deployed.
        :param id: the CDK id for endpoint.
        :param execution_role: The Amazon IAM role used as the execution role, this role must provide access to all the AWS resource a user will interact with These can be S3, DynamoDB, Glue Catalog.
        :param managed_endpoint_name: The name of the EMR managed endpoint.
        :param virtual_cluster_id: The Id of the Amazon EMR virtual cluster containing the managed endpoint.
        :param configuration_overrides: The JSON configuration overrides for Amazon EMR on EKS configuration attached to the managed endpoint. Default: - Configuration related to the [default nodegroup for notebook]{@link EmrEksNodegroup.NOTEBOOK_EXECUTOR }
        :param emr_on_eks_version: The Amazon EMR version to use. Default: - The [default Amazon EMR version]{@link EmrEksCluster.DEFAULT_EMR_VERSION }
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2c935910c81be69288fc2aa9fbc97c99bfffa5ec62bb858af28466956ca08c4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        interactive_session_options = SparkEmrContainersRuntimeInteractiveSessionProps(
            execution_role=execution_role,
            managed_endpoint_name=managed_endpoint_name,
            virtual_cluster_id=virtual_cluster_id,
            configuration_overrides=configuration_overrides,
            emr_on_eks_version=emr_on_eks_version,
        )

        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "addInteractiveEndpoint", [scope, id, interactive_session_options]))

    @jsii.member(jsii_name="addKarpenterNodePoolAndNodeClass")
    def add_karpenter_node_pool_and_node_class(
        self,
        id: builtins.str,
        manifest: typing.Any,
    ) -> typing.Any:
        '''Apply the provided manifest and add the CDK dependency on EKS cluster.

        :param id: the unique ID of the CDK resource.
        :param manifest: The manifest to apply. You can use the Utils class that offers method to read yaml file and load it as a manifest
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__601f721a4284cc744cbcd5810fe27b439ac2a96d173a458ca4b1d67a1bd7151b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument manifest", value=manifest, expected_type=type_hints["manifest"])
        return typing.cast(typing.Any, jsii.invoke(self, "addKarpenterNodePoolAndNodeClass", [id, manifest]))

    @jsii.member(jsii_name="createExecutionRole")
    def create_execution_role(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        policy: _aws_cdk_aws_iam_ceddda9d.IManagedPolicy,
        eks_namespace: builtins.str,
        name: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''Create and configure a new Amazon IAM Role usable as an execution role.

        This method makes the created role assumed by the Amazon EKS cluster Open ID Connect provider.

        :param scope: of the IAM role.
        :param id: of the CDK resource to be created, it should be unique across the stack.
        :param policy: the execution policy to attach to the role.
        :param eks_namespace: The namespace from which the role is going to be used. MUST be the same as the namespace of the Virtual Cluster from which the job is submitted
        :param name: Name to use for the role, required and is used to scope the iam role.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e2821f4b5dcbd7a6f122cd2be5bd7dcbcd511232bda21361311446b972bd638)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument eks_namespace", value=eks_namespace, expected_type=type_hints["eks_namespace"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.invoke(self, "createExecutionRole", [scope, id, policy, eks_namespace, name]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.member(jsii_name="uploadPodTemplate")
    def upload_pod_template(self, id: builtins.str, file_path: builtins.str) -> None:
        '''Upload podTemplates to the Amazon S3 location used by the cluster.

        :param id: the unique ID of the CDK resource.
        :param file_path: The local path of the yaml podTemplate files to upload.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9a6c1b3b29d69a1313c1942c1370fef49d07e8cc8b8fa91ca4ffa3902a5ebe4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument file_path", value=file_path, expected_type=type_hints["file_path"])
        return typing.cast(None, jsii.invoke(self, "uploadPodTemplate", [id, file_path]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_CLUSTER_NAME")
    def DEFAULT_CLUSTER_NAME(cls) -> builtins.str:
        '''The default name of the EKS cluster.'''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_CLUSTER_NAME"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_EKS_VERSION")
    def DEFAULT_EKS_VERSION(cls) -> _aws_cdk_aws_eks_ceddda9d.KubernetesVersion:
        '''The default EKS version.'''
        return typing.cast(_aws_cdk_aws_eks_ceddda9d.KubernetesVersion, jsii.sget(cls, "DEFAULT_EKS_VERSION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_EMR_EKS_VERSION")
    def DEFAULT_EMR_EKS_VERSION(cls) -> EmrContainersRuntimeVersion:
        '''The default EMR on EKS version.'''
        return typing.cast(EmrContainersRuntimeVersion, jsii.sget(cls, "DEFAULT_EMR_EKS_VERSION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_VPC_CIDR")
    def DEFAULT_VPC_CIDR(cls) -> builtins.str:
        '''The default CIDR when the VPC is created.'''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_VPC_CIDR"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="ec2InstanceNodeGroupRole")
    def ec2_instance_node_group_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM role used by the tooling managed nodegroup hosting core Kubernetes controllers like EBS CSI driver, core dns.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "ec2InstanceNodeGroupRole"))

    @builtins.property
    @jsii.member(jsii_name="eksCluster")
    def eks_cluster(self) -> _aws_cdk_aws_eks_ceddda9d.Cluster:
        '''The EKS cluster created by the construct if it is not provided.'''
        return typing.cast(_aws_cdk_aws_eks_ceddda9d.Cluster, jsii.get(self, "eksCluster"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC used by the EKS cluster.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="assetBucket")
    def asset_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The bucket holding podtemplates referenced in the configuration override for the job.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], jsii.get(self, "assetBucket"))

    @builtins.property
    @jsii.member(jsii_name="assetUploadBucketRole")
    def asset_upload_bucket_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role used to upload assets (pod templates) on S3.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "assetUploadBucketRole"))

    @builtins.property
    @jsii.member(jsii_name="awsNodeRole")
    def aws_node_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by IRSA for the aws-node daemonset.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "awsNodeRole"))

    @builtins.property
    @jsii.member(jsii_name="criticalDefaultConfig")
    def critical_default_config(self) -> typing.Optional[builtins.str]:
        '''The configuration override for the spark application to use with the default nodes for criticale jobs.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "criticalDefaultConfig"))

    @builtins.property
    @jsii.member(jsii_name="csiDriverIrsaRole")
    def csi_driver_irsa_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role created for the EBS CSI controller.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "csiDriverIrsaRole"))

    @builtins.property
    @jsii.member(jsii_name="eksSecretKmsKey")
    def eks_secret_kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used for storing EKS secrets.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "eksSecretKmsKey"))

    @builtins.property
    @jsii.member(jsii_name="emrServiceRole")
    def emr_service_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.CfnServiceLinkedRole]:
        '''The Service Linked role created for EMR.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.CfnServiceLinkedRole], jsii.get(self, "emrServiceRole"))

    @builtins.property
    @jsii.member(jsii_name="flowLogGroup")
    def flow_log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group for the VPC flow log when the VPC is created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "flowLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="flowLogKey")
    def flow_log_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key used for the VPC flow logs when the VPC is created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "flowLogKey"))

    @builtins.property
    @jsii.member(jsii_name="flowLogRole")
    def flow_log_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used for the VPC flow logs when the VPC is created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "flowLogRole"))

    @builtins.property
    @jsii.member(jsii_name="karpenterEventRules")
    def karpenter_event_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRule]]:
        '''The rules used by Karpenter to track node health, rules are defined in the cloudformation below https://raw.githubusercontent.com/aws/karpenter/"${KARPENTER_VERSION}"/website/content/en/preview/getting-started/getting-started-with-karpenter/cloudformation.yaml.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRule]], jsii.get(self, "karpenterEventRules"))

    @builtins.property
    @jsii.member(jsii_name="karpenterIrsaRole")
    def karpenter_irsa_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role created for the Karpenter controller.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "karpenterIrsaRole"))

    @builtins.property
    @jsii.member(jsii_name="karpenterQueue")
    def karpenter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue]:
        '''The SQS queue used by Karpenter to receive critical events from AWS services which may affect your nodes.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.IQueue], jsii.get(self, "karpenterQueue"))

    @builtins.property
    @jsii.member(jsii_name="karpenterSecurityGroup")
    def karpenter_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group used by the EC2NodeClass of the default nodes.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "karpenterSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="notebookDefaultConfig")
    def notebook_default_config(self) -> typing.Any:
        '''The configuration override for the spark application to use with the default nodes dedicated for notebooks.'''
        return typing.cast(typing.Any, jsii.get(self, "notebookDefaultConfig"))

    @builtins.property
    @jsii.member(jsii_name="podTemplateS3LocationCriticalDriver")
    def pod_template_s3_location_critical_driver(self) -> typing.Optional[builtins.str]:
        '''The S3 location holding the driver pod tempalte for critical nodes.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "podTemplateS3LocationCriticalDriver"))

    @builtins.property
    @jsii.member(jsii_name="podTemplateS3LocationCriticalExecutor")
    def pod_template_s3_location_critical_executor(
        self,
    ) -> typing.Optional[builtins.str]:
        '''The S3 location holding the executor pod tempalte for critical nodes.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "podTemplateS3LocationCriticalExecutor"))

    @builtins.property
    @jsii.member(jsii_name="podTemplateS3LocationDriverShared")
    def pod_template_s3_location_driver_shared(self) -> typing.Optional[builtins.str]:
        '''The S3 location holding the driver pod tempalte for shared nodes.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "podTemplateS3LocationDriverShared"))

    @builtins.property
    @jsii.member(jsii_name="podTemplateS3LocationExecutorShared")
    def pod_template_s3_location_executor_shared(self) -> typing.Optional[builtins.str]:
        '''The S3 location holding the executor pod tempalte for shared nodes.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "podTemplateS3LocationExecutorShared"))

    @builtins.property
    @jsii.member(jsii_name="podTemplateS3LocationNotebookDriver")
    def pod_template_s3_location_notebook_driver(self) -> typing.Optional[builtins.str]:
        '''The S3 location holding the driver pod tempalte for interactive sessions.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "podTemplateS3LocationNotebookDriver"))

    @builtins.property
    @jsii.member(jsii_name="podTemplateS3LocationNotebookExecutor")
    def pod_template_s3_location_notebook_executor(
        self,
    ) -> typing.Optional[builtins.str]:
        '''The S3 location holding the executor pod tempalte for interactive sessions.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "podTemplateS3LocationNotebookExecutor"))

    @builtins.property
    @jsii.member(jsii_name="s3VpcEndpoint")
    def s3_vpc_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IGatewayVpcEndpoint]:
        '''The S3 VPC endpoint attached to the private subnets of the VPC when VPC is created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IGatewayVpcEndpoint], jsii.get(self, "s3VpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="sharedDefaultConfig")
    def shared_default_config(self) -> typing.Optional[builtins.str]:
        '''The configuration override for the spark application to use with the default nodes for none criticale jobs.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sharedDefaultConfig"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrContainersRuntimeInteractiveSessionProps",
    jsii_struct_bases=[],
    name_mapping={
        "execution_role": "executionRole",
        "managed_endpoint_name": "managedEndpointName",
        "virtual_cluster_id": "virtualClusterId",
        "configuration_overrides": "configurationOverrides",
        "emr_on_eks_version": "emrOnEksVersion",
    },
)
class SparkEmrContainersRuntimeInteractiveSessionProps:
    def __init__(
        self,
        *,
        execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        managed_endpoint_name: builtins.str,
        virtual_cluster_id: builtins.str,
        configuration_overrides: typing.Any = None,
        emr_on_eks_version: typing.Optional[EmrContainersRuntimeVersion] = None,
    ) -> None:
        '''The properties for the EMR Managed Endpoint to create.

        :param execution_role: The Amazon IAM role used as the execution role, this role must provide access to all the AWS resource a user will interact with These can be S3, DynamoDB, Glue Catalog.
        :param managed_endpoint_name: The name of the EMR managed endpoint.
        :param virtual_cluster_id: The Id of the Amazon EMR virtual cluster containing the managed endpoint.
        :param configuration_overrides: The JSON configuration overrides for Amazon EMR on EKS configuration attached to the managed endpoint. Default: - Configuration related to the [default nodegroup for notebook]{@link EmrEksNodegroup.NOTEBOOK_EXECUTOR }
        :param emr_on_eks_version: The Amazon EMR version to use. Default: - The [default Amazon EMR version]{@link EmrEksCluster.DEFAULT_EMR_VERSION }
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cac0f55f7f430c4f64c3e56df1172bf72f1f6675159abc90c51decfe6613fdd4)
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument managed_endpoint_name", value=managed_endpoint_name, expected_type=type_hints["managed_endpoint_name"])
            check_type(argname="argument virtual_cluster_id", value=virtual_cluster_id, expected_type=type_hints["virtual_cluster_id"])
            check_type(argname="argument configuration_overrides", value=configuration_overrides, expected_type=type_hints["configuration_overrides"])
            check_type(argname="argument emr_on_eks_version", value=emr_on_eks_version, expected_type=type_hints["emr_on_eks_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "execution_role": execution_role,
            "managed_endpoint_name": managed_endpoint_name,
            "virtual_cluster_id": virtual_cluster_id,
        }
        if configuration_overrides is not None:
            self._values["configuration_overrides"] = configuration_overrides
        if emr_on_eks_version is not None:
            self._values["emr_on_eks_version"] = emr_on_eks_version

    @builtins.property
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The Amazon IAM role used as the execution role, this role must provide access to all the AWS resource a user will interact with These can be S3, DynamoDB, Glue Catalog.'''
        result = self._values.get("execution_role")
        assert result is not None, "Required property 'execution_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def managed_endpoint_name(self) -> builtins.str:
        '''The name of the EMR managed endpoint.'''
        result = self._values.get("managed_endpoint_name")
        assert result is not None, "Required property 'managed_endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_cluster_id(self) -> builtins.str:
        '''The Id of the Amazon EMR virtual cluster containing the managed endpoint.'''
        result = self._values.get("virtual_cluster_id")
        assert result is not None, "Required property 'virtual_cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configuration_overrides(self) -> typing.Any:
        '''The JSON configuration overrides for Amazon EMR on EKS configuration attached to the managed endpoint.

        :default: - Configuration related to the [default nodegroup for notebook]{@link EmrEksNodegroup.NOTEBOOK_EXECUTOR }
        '''
        result = self._values.get("configuration_overrides")
        return typing.cast(typing.Any, result)

    @builtins.property
    def emr_on_eks_version(self) -> typing.Optional[EmrContainersRuntimeVersion]:
        '''The Amazon EMR version to use.

        :default: - The [default Amazon EMR version]{@link EmrEksCluster.DEFAULT_EMR_VERSION }
        '''
        result = self._values.get("emr_on_eks_version")
        return typing.cast(typing.Optional[EmrContainersRuntimeVersion], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrContainersRuntimeInteractiveSessionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrContainersRuntimeProps",
    jsii_struct_bases=[],
    name_mapping={
        "kubectl_lambda_layer": "kubectlLambdaLayer",
        "public_access_cid_rs": "publicAccessCIDRs",
        "create_emr_on_eks_service_linked_role": "createEmrOnEksServiceLinkedRole",
        "default_nodes": "defaultNodes",
        "ec2_instance_role": "ec2InstanceRole",
        "eks_admin_role": "eksAdminRole",
        "eks_cluster": "eksCluster",
        "eks_cluster_name": "eksClusterName",
        "eks_vpc": "eksVpc",
        "karpenter_version": "karpenterVersion",
        "kubernetes_version": "kubernetesVersion",
        "removal_policy": "removalPolicy",
        "tags": "tags",
        "vpc_cidr": "vpcCidr",
    },
)
class SparkEmrContainersRuntimeProps:
    def __init__(
        self,
        *,
        kubectl_lambda_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
        public_access_cid_rs: typing.Sequence[builtins.str],
        create_emr_on_eks_service_linked_role: typing.Optional[builtins.bool] = None,
        default_nodes: typing.Optional[builtins.bool] = None,
        ec2_instance_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        eks_admin_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        eks_cluster: typing.Optional[_aws_cdk_aws_eks_ceddda9d.Cluster] = None,
        eks_cluster_name: typing.Optional[builtins.str] = None,
        eks_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        karpenter_version: typing.Optional[KarpenterVersion] = None,
        kubernetes_version: typing.Optional[_aws_cdk_aws_eks_ceddda9d.KubernetesVersion] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc_cidr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The properties for the ``SparkEmrContainerRuntime`` Construct class.

        :param kubectl_lambda_layer: The Lambda Layer with Kubectl to use for EKS Cluster setup. Starting k8s 1.22, CDK no longer bundle the Kubectl layer with the code due to breaking npm package size. A layer needs to be passed to the Construct. The CDK `documentation <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_eks.KubernetesVersion.html#static-v1_22>`_ contains the libraries that you should add for the right Kubernetes version.
        :param public_access_cid_rs: The CIDR blocks that are allowed to access to your cluster’s public Kubernetes API server endpoint.
        :param create_emr_on_eks_service_linked_role: Flag to create an IAM Service Linked Role for EMR on EKS. Default: - true
        :param default_nodes: The flag to create default Karpenter Node Provisioners for: * Critical jobs which use on-demand instances, high speed disks and workload isolation * Shared workloads which use EC2 Spot Instances and no isolation to optimize costs * Notebooks which leverage a cost optimized configuration for running EMR managed endpoints and spark drivers/executors. Default: - true
        :param ec2_instance_role: The IAM Role used for the cluster nodes instance profile. Default: - A role is created with AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryReadOnly, AmazonSSMManagedInstanceCore and AmazonEKS_CNI_Policy AWS managed policies.
        :param eks_admin_role: The IAM Role to configure in the EKS master roles. It will give access to kubernetes cluster from the AWS console. You will use this role to manage the EKS cluster and grant other access to it. Default: - An admin role must be passed if ``eksCluster`` property is not set.
        :param eks_cluster: The EKS Cluster to setup EMR on. The cluster needs to be created in the same CDK Stack. If the EKS Cluster is provided, the cluster AddOns and all the controllers (ALB Ingress controller, Karpenter...) need to be configured. When providing an EKS cluster, the methods for adding nodegroups can still be used. They implement the best practices for running Spark on EKS. Default: - An EKS Cluster is created
        :param eks_cluster_name: The name of the EKS cluster to create. Default: - The `DEFAULT_CLUSTER_NAME <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/spark-runtime/emr-containers/spark-emr-containers-runtime.ts#L65>`_
        :param eks_vpc: The VPC to use when creating the EKS cluster. VPC should have at least two private and public subnets in different Availability Zones. All private subnets must have the following tags: - 'for-use-with-amazon-emr-managed-policies'='true' - 'kubernetes.io/role/internal-elb'='1' All public subnets must have the following tag: - 'kubernetes.io/role/elb'='1' Cannot be combined with ``vpcCidr``. If combined, ``vpcCidr`` takes precedence and a new VPC is created. Default: - A new VPC is created.
        :param karpenter_version: The Karpenter version to use for autoscaling nodes in the EKS Cluster. Default: - `DEFAULT_KARPENTER_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/karpenter-releases.ts#L11>`_
        :param kubernetes_version: The Kubernetes version used to create the EKS Cluster. Default: - `DEFAULT_EKS_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/spark-runtime/emr-containers/spark-emr-containers-runtime.ts#L61>`_
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param tags: The tags assigned to the EKS cluster. Default: - none
        :param vpc_cidr: The CIDR of the VPC to use when creating the EKS cluster. If provided, a VPC with three public subnets and three private subnets is created. The size of the private subnets is four time the one of the public subnet. Default: - The CIDR 10.0.0.0/16 is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a45f77e4f1615abf22aa897dea1c5e0b6dbc0179bda92346a2cc173bd41ce3df)
            check_type(argname="argument kubectl_lambda_layer", value=kubectl_lambda_layer, expected_type=type_hints["kubectl_lambda_layer"])
            check_type(argname="argument public_access_cid_rs", value=public_access_cid_rs, expected_type=type_hints["public_access_cid_rs"])
            check_type(argname="argument create_emr_on_eks_service_linked_role", value=create_emr_on_eks_service_linked_role, expected_type=type_hints["create_emr_on_eks_service_linked_role"])
            check_type(argname="argument default_nodes", value=default_nodes, expected_type=type_hints["default_nodes"])
            check_type(argname="argument ec2_instance_role", value=ec2_instance_role, expected_type=type_hints["ec2_instance_role"])
            check_type(argname="argument eks_admin_role", value=eks_admin_role, expected_type=type_hints["eks_admin_role"])
            check_type(argname="argument eks_cluster", value=eks_cluster, expected_type=type_hints["eks_cluster"])
            check_type(argname="argument eks_cluster_name", value=eks_cluster_name, expected_type=type_hints["eks_cluster_name"])
            check_type(argname="argument eks_vpc", value=eks_vpc, expected_type=type_hints["eks_vpc"])
            check_type(argname="argument karpenter_version", value=karpenter_version, expected_type=type_hints["karpenter_version"])
            check_type(argname="argument kubernetes_version", value=kubernetes_version, expected_type=type_hints["kubernetes_version"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument vpc_cidr", value=vpc_cidr, expected_type=type_hints["vpc_cidr"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "kubectl_lambda_layer": kubectl_lambda_layer,
            "public_access_cid_rs": public_access_cid_rs,
        }
        if create_emr_on_eks_service_linked_role is not None:
            self._values["create_emr_on_eks_service_linked_role"] = create_emr_on_eks_service_linked_role
        if default_nodes is not None:
            self._values["default_nodes"] = default_nodes
        if ec2_instance_role is not None:
            self._values["ec2_instance_role"] = ec2_instance_role
        if eks_admin_role is not None:
            self._values["eks_admin_role"] = eks_admin_role
        if eks_cluster is not None:
            self._values["eks_cluster"] = eks_cluster
        if eks_cluster_name is not None:
            self._values["eks_cluster_name"] = eks_cluster_name
        if eks_vpc is not None:
            self._values["eks_vpc"] = eks_vpc
        if karpenter_version is not None:
            self._values["karpenter_version"] = karpenter_version
        if kubernetes_version is not None:
            self._values["kubernetes_version"] = kubernetes_version
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if tags is not None:
            self._values["tags"] = tags
        if vpc_cidr is not None:
            self._values["vpc_cidr"] = vpc_cidr

    @builtins.property
    def kubectl_lambda_layer(self) -> _aws_cdk_aws_lambda_ceddda9d.ILayerVersion:
        '''The Lambda Layer with Kubectl to use for EKS Cluster setup.

        Starting k8s 1.22, CDK no longer bundle the Kubectl layer with the code due to breaking npm package size.
        A layer needs to be passed to the Construct.

        The CDK `documentation <https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_eks.KubernetesVersion.html#static-v1_22>`_
        contains the libraries that you should add for the right Kubernetes version.
        '''
        result = self._values.get("kubectl_lambda_layer")
        assert result is not None, "Required property 'kubectl_lambda_layer' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.ILayerVersion, result)

    @builtins.property
    def public_access_cid_rs(self) -> typing.List[builtins.str]:
        '''The CIDR blocks that are allowed to access to your cluster’s public Kubernetes API server endpoint.'''
        result = self._values.get("public_access_cid_rs")
        assert result is not None, "Required property 'public_access_cid_rs' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def create_emr_on_eks_service_linked_role(self) -> typing.Optional[builtins.bool]:
        '''Flag to create an IAM Service Linked Role for EMR on EKS.

        :default: - true
        '''
        result = self._values.get("create_emr_on_eks_service_linked_role")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def default_nodes(self) -> typing.Optional[builtins.bool]:
        '''The flag to create default Karpenter Node Provisioners for:  * Critical jobs which use on-demand instances, high speed disks and workload isolation  * Shared workloads which use EC2 Spot Instances and no isolation to optimize costs  * Notebooks which leverage a cost optimized configuration for running EMR managed endpoints and spark drivers/executors.

        :default: - true
        '''
        result = self._values.get("default_nodes")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2_instance_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used for the cluster nodes instance profile.

        :default:

        - A role is created with AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryReadOnly,
        AmazonSSMManagedInstanceCore and AmazonEKS_CNI_Policy AWS managed policies.
        '''
        result = self._values.get("ec2_instance_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def eks_admin_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role to configure in the EKS master roles.

        It will give access to kubernetes cluster from the AWS console.
        You will use this role to manage the EKS cluster and grant other access to it.

        :default: - An admin role must be passed if ``eksCluster`` property is not set.
        '''
        result = self._values.get("eks_admin_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def eks_cluster(self) -> typing.Optional[_aws_cdk_aws_eks_ceddda9d.Cluster]:
        '''The EKS Cluster to setup EMR on.

        The cluster needs to be created in the same CDK Stack.
        If the EKS Cluster is provided, the cluster AddOns and all the controllers (ALB Ingress controller, Karpenter...) need to be configured.
        When providing an EKS cluster, the methods for adding nodegroups can still be used. They implement the best practices for running Spark on EKS.

        :default: - An EKS Cluster is created
        '''
        result = self._values.get("eks_cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_eks_ceddda9d.Cluster], result)

    @builtins.property
    def eks_cluster_name(self) -> typing.Optional[builtins.str]:
        '''The name of the EKS cluster to create.

        :default: - The `DEFAULT_CLUSTER_NAME <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/spark-runtime/emr-containers/spark-emr-containers-runtime.ts#L65>`_
        '''
        result = self._values.get("eks_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC to use when creating the EKS cluster.

        VPC should have at least two private and public subnets in different Availability Zones.
        All private subnets must have the following tags:

        - 'for-use-with-amazon-emr-managed-policies'='true'
        - 'kubernetes.io/role/internal-elb'='1'
          All public subnets must have the following tag:
        - 'kubernetes.io/role/elb'='1'
          Cannot be combined with ``vpcCidr``. If combined, ``vpcCidr`` takes precedence and a new VPC is created.

        :default: - A new VPC is created.
        '''
        result = self._values.get("eks_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def karpenter_version(self) -> typing.Optional[KarpenterVersion]:
        '''The Karpenter version to use for autoscaling nodes in the EKS Cluster.

        :default: - `DEFAULT_KARPENTER_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/karpenter-releases.ts#L11>`_
        '''
        result = self._values.get("karpenter_version")
        return typing.cast(typing.Optional[KarpenterVersion], result)

    @builtins.property
    def kubernetes_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_eks_ceddda9d.KubernetesVersion]:
        '''The Kubernetes version used to create the EKS Cluster.

        :default: - `DEFAULT_EKS_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/spark-runtime/emr-containers/spark-emr-containers-runtime.ts#L61>`_
        '''
        result = self._values.get("kubernetes_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_eks_ceddda9d.KubernetesVersion], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The tags assigned to the EKS cluster.

        :default: - none
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def vpc_cidr(self) -> typing.Optional[builtins.str]:
        '''The CIDR of the VPC to use when creating the EKS cluster.

        If provided, a VPC with three public subnets and three private subnets is created.
        The size of the private subnets is four time the one of the public subnet.

        :default: - The CIDR 10.0.0.0/16 is used
        '''
        result = self._values.get("vpc_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrContainersRuntimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SparkEmrServerlessRuntime(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrServerlessRuntime",
):
    '''A construct to create a Spark EMR Serverless Application, along with methods to create IAM roles having the least privilege.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Processing/spark-emr-serverless-runtime

    Example::

        from aws_cdk.aws_iam import Role, AccountRootPrincipal
        
        
        serverless_runtime = dsf.processing.SparkEmrServerlessRuntime(self, "EmrApp",
            name="SparkRuntimeServerless"
        )
        
        execution_role = dsf.processing.SparkEmrServerlessRuntime.create_execution_role(self, "ExecutionRole")
        
        submitter_role = Role(self, "SubmitterRole",
            assumed_by=AccountRootPrincipal()
        )
        
        dsf.processing.SparkEmrServerlessRuntime.grant_start_job_execution(submitter_role, [execution_role.role_arn], ["EMR-serverless-app-ID"])
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        architecture: typing.Optional[_Architecture_b811f66d] = None,
        auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_label: typing.Optional[EmrRuntimeVersion] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]] = None,
        worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    ) -> None:
        '''
        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param name: The name of the application. The name must be less than 64 characters. *Pattern* : ``^[A-Za-z0-9._\\\\/#-]+$``
        :param architecture: The CPU architecture type of the application. Default: - x86_64
        :param auto_start_configuration: The configuration for an application to automatically start on job submission. Default: - True
        :param auto_stop_configuration: The configuration for an application to automatically stop after a certain amount of time being idle. Default: - The application is stopped after 15 minutes of idle time
        :param image_configuration: The unique custom image configuration used for both the Spark Driver and the Spark Executor. Default: - EMR base image is used for both the Spark Driver and the Spark Executor
        :param initial_capacity: The pre-initialized capacity of the application. Default: - No pre-initialized capacity is used
        :param maximum_capacity: The maximum capacity of the application. This is cumulative across all workers at any given point in time during the lifespan of the application is created. No new resources will be created once any one of the defined limits is hit. Default: - Depending on the EMR version
        :param network_configuration: The network configuration for customer VPC connectivity for the application. If no configuration is created, the a VPC with 3 public subnets and 3 private subnets is created The 3 public subnets and 3 private subnets are each created in an Availability Zone (AZ) The VPC has one NAT Gateway per AZ and an S3 endpoint Default: - a VPC and a security group are created, these are accessed as construct attribute.
        :param release_label: The EMR release version associated with the application. The EMR release can be found in this `documentation <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html>`_ Default: `EMR_DEFAULT_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L46>`_
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param runtime_configuration: The runtime and monitoring configurations to used as defaults for all of the job runs of this application. Default: - No custom configuration is used
        :param worker_type_specifications: The different custom image configurations used for the Spark Driver and the Spark Executor. Default: - EMR base image is used for both the Spark Driver and the Spark Executor
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ff128785929fb50a3c575346aa3fdc433fd1cc2e7e69efe27b37f38c4a0e14d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SparkEmrServerlessRuntimeProps(
            name=name,
            architecture=architecture,
            auto_start_configuration=auto_start_configuration,
            auto_stop_configuration=auto_stop_configuration,
            image_configuration=image_configuration,
            initial_capacity=initial_capacity,
            maximum_capacity=maximum_capacity,
            network_configuration=network_configuration,
            release_label=release_label,
            removal_policy=removal_policy,
            runtime_configuration=runtime_configuration,
            worker_type_specifications=worker_type_specifications,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createExecutionRole")
    @builtins.classmethod
    def create_execution_role(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        execution_role_policy_document: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        iam_policy_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''A static method creating an execution IAM role that can be assumed by EMR Serverless The method returns the role it creates.

        If no ``executionRolePolicyDocument`` or ``iamPolicyName``
        The method will return a role with only a trust policy to EMR Servereless service principal.
        You can use this role then to grant access to any resources you control.

        :param scope: the scope in which to create the role.
        :param id: passed to the IAM Role construct object.
        :param execution_role_policy_document: the inline policy document to attach to the role. These are IAM policies needed by the job. This parameter is mutually execlusive with iamPolicyName.
        :param iam_policy_name: the IAM policy name to attach to the role, this is mutually execlusive with executionRolePolicyDocument.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf458fcad8d4f2991ec79ae36da0359407a6b85df13fecd2b6514a7641b19dc6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument execution_role_policy_document", value=execution_role_policy_document, expected_type=type_hints["execution_role_policy_document"])
            check_type(argname="argument iam_policy_name", value=iam_policy_name, expected_type=type_hints["iam_policy_name"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.sinvoke(cls, "createExecutionRole", [scope, id, execution_role_policy_document, iam_policy_name]))

    @jsii.member(jsii_name="grantStartJobExecution")
    @builtins.classmethod
    def grant_start_job_execution(
        cls,
        start_job_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        execution_role_arn: typing.Sequence[builtins.str],
        application_arns: typing.Sequence[builtins.str],
    ) -> None:
        '''A static method granting the right to start and monitor a job to an IAM Role.

        The method will also attach an iam:PassRole permission limited to the IAM Job Execution roles passed

        :param start_job_role: the role that will call the start job api and which needs to have the iam:PassRole permission.
        :param execution_role_arn: the role used by EMR Serverless to access resources during the job execution.
        :param application_arns: the EMR Serverless aplication ARN, this is used by the method to limit the EMR Serverless applications the role can submit job to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f44185a448635116f97f58d4c9eefe1100885b3161858f3fe7876c20700962f)
            check_type(argname="argument start_job_role", value=start_job_role, expected_type=type_hints["start_job_role"])
            check_type(argname="argument execution_role_arn", value=execution_role_arn, expected_type=type_hints["execution_role_arn"])
            check_type(argname="argument application_arns", value=application_arns, expected_type=type_hints["application_arns"])
        return typing.cast(None, jsii.sinvoke(cls, "grantStartJobExecution", [start_job_role, execution_role_arn, application_arns]))

    @jsii.member(jsii_name="grantStartExecution")
    def grant_start_execution(
        self,
        start_job_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        execution_role_arn: builtins.str,
    ) -> None:
        '''A method which will grant an IAM Role the right to start and monitor a job.

        The method will also attach an iam:PassRole permission to limited to the IAM Job Execution roles passed.
        The excution role will be able to submit job to the EMR Serverless application created by the construct.

        :param start_job_role: the role that will call the start job api and which need to have the iam:PassRole permission.
        :param execution_role_arn: the role use by EMR Serverless to access resources during the job execution.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa0057b875c053777bbb69a3ca41c8d91bc6dfb1da713059ddede2fe71fd51a4)
            check_type(argname="argument start_job_role", value=start_job_role, expected_type=type_hints["start_job_role"])
            check_type(argname="argument execution_role_arn", value=execution_role_arn, expected_type=type_hints["execution_role_arn"])
        return typing.cast(None, jsii.invoke(self, "grantStartExecution", [start_job_role, execution_role_arn]))

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
    @jsii.member(jsii_name="application")
    def application(self) -> _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication:
        '''The EMR Serverless application.'''
        return typing.cast(_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication, jsii.get(self, "application"))

    @builtins.property
    @jsii.member(jsii_name="emrApplicationSecurityGroup")
    def emr_application_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''If no VPC is provided, one is created by default along with a security group attached to the EMR Serverless Application This attribute is used to expose the security group, if you provide your own security group through the {@link SparkEmrServerlessRuntimeProps} the attribute will be ``undefined``.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "emrApplicationSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="flowLogGroup")
    def flow_log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group for the VPC flow log when the VPC is created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "flowLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="flowLogKey")
    def flow_log_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key used for the VPC flow log when the VPC is created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "flowLogKey"))

    @builtins.property
    @jsii.member(jsii_name="flowLogRole")
    def flow_log_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used for the VPC flow log when the VPC is created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "flowLogRole"))

    @builtins.property
    @jsii.member(jsii_name="s3VpcEndpoint")
    def s3_vpc_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IGatewayVpcEndpoint]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IGatewayVpcEndpoint], jsii.get(self, "s3VpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC used by the EKS cluster.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrServerlessRuntimeProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "architecture": "architecture",
        "auto_start_configuration": "autoStartConfiguration",
        "auto_stop_configuration": "autoStopConfiguration",
        "image_configuration": "imageConfiguration",
        "initial_capacity": "initialCapacity",
        "maximum_capacity": "maximumCapacity",
        "network_configuration": "networkConfiguration",
        "release_label": "releaseLabel",
        "removal_policy": "removalPolicy",
        "runtime_configuration": "runtimeConfiguration",
        "worker_type_specifications": "workerTypeSpecifications",
    },
)
class SparkEmrServerlessRuntimeProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        architecture: typing.Optional[_Architecture_b811f66d] = None,
        auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        release_label: typing.Optional[EmrRuntimeVersion] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]] = None,
        worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    ) -> None:
        '''Properties for the ``SparkEmrServerlessRuntime`` construct.

        :param name: The name of the application. The name must be less than 64 characters. *Pattern* : ``^[A-Za-z0-9._\\\\/#-]+$``
        :param architecture: The CPU architecture type of the application. Default: - x86_64
        :param auto_start_configuration: The configuration for an application to automatically start on job submission. Default: - True
        :param auto_stop_configuration: The configuration for an application to automatically stop after a certain amount of time being idle. Default: - The application is stopped after 15 minutes of idle time
        :param image_configuration: The unique custom image configuration used for both the Spark Driver and the Spark Executor. Default: - EMR base image is used for both the Spark Driver and the Spark Executor
        :param initial_capacity: The pre-initialized capacity of the application. Default: - No pre-initialized capacity is used
        :param maximum_capacity: The maximum capacity of the application. This is cumulative across all workers at any given point in time during the lifespan of the application is created. No new resources will be created once any one of the defined limits is hit. Default: - Depending on the EMR version
        :param network_configuration: The network configuration for customer VPC connectivity for the application. If no configuration is created, the a VPC with 3 public subnets and 3 private subnets is created The 3 public subnets and 3 private subnets are each created in an Availability Zone (AZ) The VPC has one NAT Gateway per AZ and an S3 endpoint Default: - a VPC and a security group are created, these are accessed as construct attribute.
        :param release_label: The EMR release version associated with the application. The EMR release can be found in this `documentation <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html>`_ Default: `EMR_DEFAULT_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L46>`_
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param runtime_configuration: The runtime and monitoring configurations to used as defaults for all of the job runs of this application. Default: - No custom configuration is used
        :param worker_type_specifications: The different custom image configurations used for the Spark Driver and the Spark Executor. Default: - EMR base image is used for both the Spark Driver and the Spark Executor
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb7370f53b2007953cbbb308224a013d555ba02de4f43ab678e1a50f670c7f34)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument auto_start_configuration", value=auto_start_configuration, expected_type=type_hints["auto_start_configuration"])
            check_type(argname="argument auto_stop_configuration", value=auto_stop_configuration, expected_type=type_hints["auto_stop_configuration"])
            check_type(argname="argument image_configuration", value=image_configuration, expected_type=type_hints["image_configuration"])
            check_type(argname="argument initial_capacity", value=initial_capacity, expected_type=type_hints["initial_capacity"])
            check_type(argname="argument maximum_capacity", value=maximum_capacity, expected_type=type_hints["maximum_capacity"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument runtime_configuration", value=runtime_configuration, expected_type=type_hints["runtime_configuration"])
            check_type(argname="argument worker_type_specifications", value=worker_type_specifications, expected_type=type_hints["worker_type_specifications"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if architecture is not None:
            self._values["architecture"] = architecture
        if auto_start_configuration is not None:
            self._values["auto_start_configuration"] = auto_start_configuration
        if auto_stop_configuration is not None:
            self._values["auto_stop_configuration"] = auto_stop_configuration
        if image_configuration is not None:
            self._values["image_configuration"] = image_configuration
        if initial_capacity is not None:
            self._values["initial_capacity"] = initial_capacity
        if maximum_capacity is not None:
            self._values["maximum_capacity"] = maximum_capacity
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if release_label is not None:
            self._values["release_label"] = release_label
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if runtime_configuration is not None:
            self._values["runtime_configuration"] = runtime_configuration
        if worker_type_specifications is not None:
            self._values["worker_type_specifications"] = worker_type_specifications

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the application.

        The name must be less than 64 characters.
        *Pattern* : ``^[A-Za-z0-9._\\\\/#-]+$``
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def architecture(self) -> typing.Optional[_Architecture_b811f66d]:
        '''The CPU architecture type of the application.

        :default: - x86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[_Architecture_b811f66d], result)

    @builtins.property
    def auto_start_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty]]:
        '''The configuration for an application to automatically start on job submission.

        :default: - True
        '''
        result = self._values.get("auto_start_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty]], result)

    @builtins.property
    def auto_stop_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty]]:
        '''The configuration for an application to automatically stop after a certain amount of time being idle.

        :default: - The application is stopped after 15 minutes of idle time
        '''
        result = self._values.get("auto_stop_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty]], result)

    @builtins.property
    def image_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty]]:
        '''The unique custom image configuration used for both the Spark Driver and the Spark Executor.

        :default: - EMR base image is used for both the Spark Driver and the Spark Executor

        :see: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/application-custom-image.html
        '''
        result = self._values.get("image_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty]], result)

    @builtins.property
    def initial_capacity(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty]]]]:
        '''The pre-initialized capacity of the application.

        :default: - No pre-initialized capacity is used

        :see: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/pre-init-capacity.html
        '''
        result = self._values.get("initial_capacity")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty]]]], result)

    @builtins.property
    def maximum_capacity(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty]]:
        '''The maximum capacity of the application.

        This is cumulative across all workers at any given point in time during the lifespan of the application is created. No new resources will be created once any one of the defined limits is hit.

        :default: - Depending on the EMR version
        '''
        result = self._values.get("maximum_capacity")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty]], result)

    @builtins.property
    def network_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty]]:
        '''The network configuration for customer VPC connectivity for the application.

        If no configuration is created, the a VPC with 3 public subnets and 3 private subnets is created
        The 3 public subnets and 3 private subnets are each created in an Availability Zone (AZ)
        The VPC has one NAT Gateway per AZ and an S3 endpoint

        :default: - a VPC and a security group are created, these are accessed as construct attribute.
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty]], result)

    @builtins.property
    def release_label(self) -> typing.Optional[EmrRuntimeVersion]:
        '''The EMR release version associated with the application.

        The EMR release can be found in this `documentation <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html>`_

        :default: `EMR_DEFAULT_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L46>`_
        '''
        result = self._values.get("release_label")
        return typing.cast(typing.Optional[EmrRuntimeVersion], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def runtime_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty]]]:
        '''The runtime and monitoring configurations to used as defaults for all of the job runs of this application.

        :default: - No custom configuration is used

        :see: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/default-configs.html
        '''
        result = self._values.get("runtime_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty]]], result)

    @builtins.property
    def worker_type_specifications(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty]]]]:
        '''The different custom image configurations used for the Spark Driver and the Spark Executor.

        :default: - EMR base image is used for both the Spark Driver and the Spark Executor

        :see: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/application-custom-image.html
        '''
        result = self._values.get("worker_type_specifications")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty]]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrServerlessRuntimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkImage")
class SparkImage(enum.Enum):
    '''The list of supported Spark images to use in the SparkCICDPipeline.'''

    EMR_7_0 = "EMR_7_0"
    EMR_6_15 = "EMR_6_15"
    EMR_6_14 = "EMR_6_14"
    EMR_6_13 = "EMR_6_13"
    EMR_6_12 = "EMR_6_12"
    EMR_6_11 = "EMR_6_11"
    EMR_6_10 = "EMR_6_10"
    EMR_6_9 = "EMR_6_9"


class SparkJob(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkJob",
):
    '''A base construct to run Spark Jobs.

    Creates an AWS Step Functions State Machine that orchestrates the Spark Job.

    :see:

    https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Processing/spark-emr-serverless-job

    Available implementations:

    - {@link SparkEmrServerlessJob } for Emr Serverless implementation
    - {@link SparkEmrEksJob } for EMR On EKS implementation
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        tracking_tag: builtins.str,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''Constructs a new instance of the SparkJob class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param tracking_tag: -
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param schedule: The Schedule to run the Step Functions state machine. Default: - The Step Functions State Machine is not scheduled.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b46ce074c66eb8fbf61ac4f9d6d05a3956159aaff2397a4bd1ca091482afdad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tracking_tag", value=tracking_tag, expected_type=type_hints["tracking_tag"])
        props = SparkJobProps(removal_policy=removal_policy, schedule=schedule)

        jsii.create(self.__class__, self, [scope, id, tracking_tag, props])

    @jsii.member(jsii_name="createCloudWatchLogsLogGroup")
    def _create_cloud_watch_logs_log_group(
        self,
        name: builtins.str,
        encryption_key_arn: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''Creates an encrypted CloudWatch Logs group to store the Spark job logs.

        :param name: CloudWatch Logs group name of cloudwatch log group to store the Spark job logs.
        :param encryption_key_arn: KMS Key ARN for encryption.

        :default: - Server-side encryption managed by CloudWatch Logs.

        :return: LogGroup CloudWatch Logs group.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd9de1b490002aff5cc9e89a8915a5df3f030e1ac317b39493f473190627d439)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument encryption_key_arn", value=encryption_key_arn, expected_type=type_hints["encryption_key_arn"])
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.invoke(self, "createCloudWatchLogsLogGroup", [name, encryption_key_arn]))

    @jsii.member(jsii_name="createS3LogBucket")
    def _create_s3_log_bucket(
        self,
        s3_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        s3_log_prefix: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> builtins.str:
        '''Creates or import an S3 bucket to store the logs of the Spark job.

        The bucket is created with SSE encryption (KMS managed or provided by user).

        :param s3_log_bucket: The S3 Bucket to store the logs of the Spark job.
        :param s3_log_prefix: The prefix to store logs in the Log Bucket.
        :param encryption_key: The KMS Key for encryption.

        :default: - Master KMS key of the account

        :return: string S3 path to store the logs.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__928342d401671b9066231b19946bece7cbccc2153476b6fda36afb0676f47e2e)
            check_type(argname="argument s3_log_bucket", value=s3_log_bucket, expected_type=type_hints["s3_log_bucket"])
            check_type(argname="argument s3_log_prefix", value=s3_log_prefix, expected_type=type_hints["s3_log_prefix"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
        return typing.cast(builtins.str, jsii.invoke(self, "createS3LogBucket", [s3_log_bucket, s3_log_prefix, encryption_key]))

    @jsii.member(jsii_name="createStateMachine")
    def _create_state_machine(
        self,
        job_timeout: _aws_cdk_ceddda9d.Duration,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''Creates a State Machine that orchestrates the Spark Job.

        This is a default implementation that can be overridden by the extending class.

        :param job_timeout: Timeout for the state machine.
        :param schedule: Schedule to run the state machine.

        :default: no schedule

        :return: StateMachine

        :defautl: 30 minutes
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10cc4976ae85391a5f2a8a3056343b905407fd9dbd62a49da8ad2981674a5d07)
            check_type(argname="argument job_timeout", value=job_timeout, expected_type=type_hints["job_timeout"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.invoke(self, "createStateMachine", [job_timeout, schedule]))

    @jsii.member(jsii_name="grantExecutionRole")
    @abc.abstractmethod
    def _grant_execution_role(self, role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''Grants the execution role to the Step Functions state machine.

        :param role: -
        '''
        ...

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.member(jsii_name="returnJobFailTaskProps")
    @abc.abstractmethod
    def _return_job_fail_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.FailProps:
        '''Parameters for Step Functions task that fails the Spark job.

        :return: FailProps
        '''
        ...

    @jsii.member(jsii_name="returnJobMonitorTaskProps")
    @abc.abstractmethod
    def _return_job_monitor_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Parameters for Step Functions task that monitors the Spark job.

        :return: CallAwsServiceProps
        '''
        ...

    @jsii.member(jsii_name="returnJobStartTaskProps")
    @abc.abstractmethod
    def _return_job_start_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Parameters for Step Functions task that runs the Spark job.

        :return: CallAwsServiceProps
        '''
        ...

    @jsii.member(jsii_name="returnJobStatusCancelled")
    @abc.abstractmethod
    def _return_job_status_cancelled(self) -> builtins.str:
        '''Returns the status of the Spark job that is cancelled based on the GetJobRun API response.'''
        ...

    @jsii.member(jsii_name="returnJobStatusFailed")
    @abc.abstractmethod
    def _return_job_status_failed(self) -> builtins.str:
        '''Returns the status of the Spark job that failed based on the GetJobRun API response.

        :return: string
        '''
        ...

    @jsii.member(jsii_name="returnJobStatusSucceed")
    @abc.abstractmethod
    def _return_job_status_succeed(self) -> builtins.str:
        '''Returns the status of the Spark job that succeeded based on the GetJobRun API response.

        :return: string
        '''
        ...

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="emrJobLogGroup")
    def _emr_job_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The loudWatch Logs Group for the Spark job logs.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "emrJobLogGroup"))

    @_emr_job_log_group.setter
    def _emr_job_log_group(
        self,
        value: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__223659f083d952cd4a943949e12330a9d6a991cf1a9057a8c4f950353ff8a3b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emrJobLogGroup", value)

    @builtins.property
    @jsii.member(jsii_name="s3LogBucket")
    def _s3_log_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The S3 Bucket for the Spark job logs.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], jsii.get(self, "s3LogBucket"))

    @_s3_log_bucket.setter
    def _s3_log_bucket(
        self,
        value: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dd675e43931483584ef06f9389a9b5c1ac642e585a5ad647dbbb0b15e912150)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3LogBucket", value)

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine]:
        '''The Step Functions State Machine created to orchestrate the Spark Job.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine], jsii.get(self, "stateMachine"))

    @state_machine.setter
    def state_machine(
        self,
        value: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d63fb6cc0f082e5380e5c5a5b1a97059409ed12f2ff5c1c9ca3b0dcc98b2ed26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachine", value)

    @builtins.property
    @jsii.member(jsii_name="stateMachineLogGroup")
    def state_machine_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group used by the State Machine.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "stateMachineLogGroup"))

    @state_machine_log_group.setter
    def state_machine_log_group(
        self,
        value: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbd196ec4802b268cdc82b1778fe7db3c7337933ea458c5fcf97b1b893125bfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachineLogGroup", value)


class _SparkJobProxy(SparkJob):
    @jsii.member(jsii_name="grantExecutionRole")
    def _grant_execution_role(self, role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''Grants the execution role to the Step Functions state machine.

        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a6f0a1184cb90dc918c07815fffa6746da42c8a5c1fbf7b78a4c6be64bd1f77)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(None, jsii.invoke(self, "grantExecutionRole", [role]))

    @jsii.member(jsii_name="returnJobFailTaskProps")
    def _return_job_fail_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.FailProps:
        '''Parameters for Step Functions task that fails the Spark job.

        :return: FailProps
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.FailProps, jsii.invoke(self, "returnJobFailTaskProps", []))

    @jsii.member(jsii_name="returnJobMonitorTaskProps")
    def _return_job_monitor_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Parameters for Step Functions task that monitors the Spark job.

        :return: CallAwsServiceProps
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps, jsii.invoke(self, "returnJobMonitorTaskProps", []))

    @jsii.member(jsii_name="returnJobStartTaskProps")
    def _return_job_start_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Parameters for Step Functions task that runs the Spark job.

        :return: CallAwsServiceProps
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps, jsii.invoke(self, "returnJobStartTaskProps", []))

    @jsii.member(jsii_name="returnJobStatusCancelled")
    def _return_job_status_cancelled(self) -> builtins.str:
        '''Returns the status of the Spark job that is cancelled based on the GetJobRun API response.'''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusCancelled", []))

    @jsii.member(jsii_name="returnJobStatusFailed")
    def _return_job_status_failed(self) -> builtins.str:
        '''Returns the status of the Spark job that failed based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusFailed", []))

    @jsii.member(jsii_name="returnJobStatusSucceed")
    def _return_job_status_succeed(self) -> builtins.str:
        '''Returns the status of the Spark job that succeeded based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusSucceed", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SparkJob).__jsii_proxy_class__ = lambda : _SparkJobProxy


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkJobProps",
    jsii_struct_bases=[],
    name_mapping={"removal_policy": "removalPolicy", "schedule": "schedule"},
)
class SparkJobProps:
    def __init__(
        self,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''The properties for the ``SparkJob`` construct.

        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param schedule: The Schedule to run the Step Functions state machine. Default: - The Step Functions State Machine is not scheduled.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca9f736db1e60c03ac2e3311780bbfdd65a92742325e77e5ea245bbabd816049)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The Schedule to run the Step Functions state machine.

        :default: - The Step Functions State Machine is not scheduled.
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkJobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SparkEmrContainersJob(
    SparkJob,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrContainersJob",
):
    '''A construct to run Spark Jobs using EMR Container runtime (EMR on EKS).

    It creates a Step Functions State Machine that orchestrates the Spark Job.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Processing/spark-emr-serverless-job

    Example::

        from aws_cdk.aws_stepfunctions import JsonPath
        
        
        job = dsf.processing.SparkEmrContainersJob(self, "SparkJob",
            job_config={
                "Name": JsonPath.format("ge_profile-{}", JsonPath.uuid()),
                "VirtualClusterId": "virtualClusterId",
                "ExecutionRoleArn": "ROLE-ARN",
                "JobDriver": {
                    "SparkSubmit": {
                        "EntryPoint": "s3://S3-BUCKET/pi.py",
                        "EntryPointArguments": [],
                        "SparkSubmitParameters": "--conf spark.executor.instances=2 --conf spark.executor.memory=2G --conf spark.driver.memory=2G --conf spark.executor.cores=4"
                    }
                }
            }
        )
        
        cdk.CfnOutput(self, "SparkJobStateMachine",
            value=job.state_machine.state_machine_arn
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Union[typing.Union["SparkEmrContainersJobProps", typing.Dict[builtins.str, typing.Any]], typing.Union["SparkEmrContainersJobApiProps", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf608b3fc77c6d9856f7aa927a1785da24e08760630a40ca167262caa0194024)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantExecutionRole")
    def _grant_execution_role(self, role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''Grants the necessary permissions to the Step Functions StateMachine to be able to start EMR on EKS job.

        :param role: Step Functions StateMachine IAM role.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65cf3fbfa0a42b552961215c2e42b33d95b9ba7c2b79ae62e442cf5827eaab9c)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(None, jsii.invoke(self, "grantExecutionRole", [role]))

    @jsii.member(jsii_name="returnJobFailTaskProps")
    def _return_job_fail_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.FailProps:
        '''Returns the props for the Step Functions task that handles the failure  if the EMR Serverless job fails.

        :return: FailProps The error details of the failed Spark Job
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.FailProps, jsii.invoke(self, "returnJobFailTaskProps", []))

    @jsii.member(jsii_name="returnJobMonitorTaskProps")
    def _return_job_monitor_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Returns the props for the Step Functions CallAwsService Construct that checks the execution status of the Spark job.

        :return: CallAwsServiceProps

        :see: CallAwsService
        :link: [https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_stepfunctions_tasks.CallAwsService.html]
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps, jsii.invoke(self, "returnJobMonitorTaskProps", []))

    @jsii.member(jsii_name="returnJobStartTaskProps")
    def _return_job_start_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Returns the props for the Step Functions CallAwsService Construct that starts the Spark job.

        The State Machine uses `StartJobRun API <https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html>`_.

        :return: CallAwsServiceProps

        :see: CallAwsService
        :link: [https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_stepfunctions_tasks.CallAwsService.html]
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps, jsii.invoke(self, "returnJobStartTaskProps", []))

    @jsii.member(jsii_name="returnJobStatusCancelled")
    def _return_job_status_cancelled(self) -> builtins.str:
        '''Returns the status of the EMR Serverless job that is cancelled based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusCancelled", []))

    @jsii.member(jsii_name="returnJobStatusFailed")
    def _return_job_status_failed(self) -> builtins.str:
        '''Returns the status of the EMR on EKS job that failed based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusFailed", []))

    @jsii.member(jsii_name="returnJobStatusSucceed")
    def _return_job_status_succeed(self) -> builtins.str:
        '''Returns the status of the EMR on EKS job that succeeded  based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusSucceed", []))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrContainersJobApiProps",
    jsii_struct_bases=[SparkJobProps],
    name_mapping={
        "removal_policy": "removalPolicy",
        "schedule": "schedule",
        "job_config": "jobConfig",
        "execution_timeout": "executionTimeout",
    },
)
class SparkEmrContainersJobApiProps(SparkJobProps):
    def __init__(
        self,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        job_config: typing.Mapping[builtins.str, typing.Any],
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''Configuration for the EMR on EKS job.

        Use this interface when ``SparkEmrContainerJobProps`` doesn't give you access to the configuration parameters you need.

        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param schedule: The Schedule to run the Step Functions state machine. Default: - The Step Functions State Machine is not scheduled.
        :param job_config: EMR on EKS StartJobRun API configuration.
        :param execution_timeout: Job execution timeout. Default: - 30 minutes

        :link: [https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html]
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2294c4739f96f8aaf5904bda10141a59227860735e4bbf1090aae3f75d632e26)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument job_config", value=job_config, expected_type=type_hints["job_config"])
            check_type(argname="argument execution_timeout", value=execution_timeout, expected_type=type_hints["execution_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "job_config": job_config,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if schedule is not None:
            self._values["schedule"] = schedule
        if execution_timeout is not None:
            self._values["execution_timeout"] = execution_timeout

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The Schedule to run the Step Functions state machine.

        :default: - The Step Functions State Machine is not scheduled.
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def job_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''EMR on EKS StartJobRun API configuration.

        :link: [https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html]
        '''
        result = self._values.get("job_config")
        assert result is not None, "Required property 'job_config' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def execution_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Job execution timeout.

        :default: - 30 minutes
        '''
        result = self._values.get("execution_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrContainersJobApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrContainersJobProps",
    jsii_struct_bases=[SparkJobProps],
    name_mapping={
        "removal_policy": "removalPolicy",
        "schedule": "schedule",
        "execution_role": "executionRole",
        "name": "name",
        "spark_submit_entry_point": "sparkSubmitEntryPoint",
        "virtual_cluster_id": "virtualClusterId",
        "application_configuration": "applicationConfiguration",
        "cloud_watch_log_group": "cloudWatchLogGroup",
        "cloud_watch_log_group_stream_prefix": "cloudWatchLogGroupStreamPrefix",
        "execution_timeout": "executionTimeout",
        "max_retries": "maxRetries",
        "release_label": "releaseLabel",
        "s3_log_bucket": "s3LogBucket",
        "s3_log_prefix": "s3LogPrefix",
        "spark_submit_entry_point_arguments": "sparkSubmitEntryPointArguments",
        "spark_submit_parameters": "sparkSubmitParameters",
        "tags": "tags",
    },
)
class SparkEmrContainersJobProps(SparkJobProps):
    def __init__(
        self,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        name: builtins.str,
        spark_submit_entry_point: builtins.str,
        virtual_cluster_id: builtins.str,
        application_configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        cloud_watch_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        cloud_watch_log_group_stream_prefix: typing.Optional[builtins.str] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        release_label: typing.Optional[EmrRuntimeVersion] = None,
        s3_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        s3_log_prefix: typing.Optional[builtins.str] = None,
        spark_submit_entry_point_arguments: typing.Optional[typing.Sequence[builtins.str]] = None,
        spark_submit_parameters: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''Simplified configuration for the ``SparkEmrEksJob`` construct.

        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param schedule: The Schedule to run the Step Functions state machine. Default: - The Step Functions State Machine is not scheduled.
        :param execution_role: The IAM execution Role ARN for the EMR on EKS job.
        :param name: The Spark job name.
        :param spark_submit_entry_point: The entry point for the Spark submit job run.
        :param virtual_cluster_id: The EMR on EKS virtual cluster ID.
        :param application_configuration: The application configuration override for the Spark submit job run. Default: - No configuration is passed to the job.
        :param cloud_watch_log_group: The CloudWatch Log Group name for log publishing. Default: - CloudWatch is not used for logging
        :param cloud_watch_log_group_stream_prefix: The CloudWatch Log Group stream prefix for log publishing. Default: - The application name is used as the prefix
        :param execution_timeout: The execution timeout. Default: - 30 minutes
        :param max_retries: The maximum number of retries. Default: - No retry
        :param release_label: The EMR release version associated with the application. The EMR release can be found in this `documentation <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html>`_ Default: `EMR_DEFAULT_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L46>`_
        :param s3_log_bucket: The S3 Bucket for log publishing. Default: - No logging to S3
        :param s3_log_prefix: The S3 Bucket prefix for log publishing. Default: - No logging to S3
        :param spark_submit_entry_point_arguments: The arguments for the Spark submit job run. Default: - No arguments are passed to the job.
        :param spark_submit_parameters: The parameters for the Spark submit job run. Default: - No parameters are passed to the job.
        :param tags: Tags to be added to the EMR Serverless job. Default: - No tags are added
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__455642341a460c5395b9d20088cdd0585965ef1072e1977e693f6fc41ec0e870)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument spark_submit_entry_point", value=spark_submit_entry_point, expected_type=type_hints["spark_submit_entry_point"])
            check_type(argname="argument virtual_cluster_id", value=virtual_cluster_id, expected_type=type_hints["virtual_cluster_id"])
            check_type(argname="argument application_configuration", value=application_configuration, expected_type=type_hints["application_configuration"])
            check_type(argname="argument cloud_watch_log_group", value=cloud_watch_log_group, expected_type=type_hints["cloud_watch_log_group"])
            check_type(argname="argument cloud_watch_log_group_stream_prefix", value=cloud_watch_log_group_stream_prefix, expected_type=type_hints["cloud_watch_log_group_stream_prefix"])
            check_type(argname="argument execution_timeout", value=execution_timeout, expected_type=type_hints["execution_timeout"])
            check_type(argname="argument max_retries", value=max_retries, expected_type=type_hints["max_retries"])
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument s3_log_bucket", value=s3_log_bucket, expected_type=type_hints["s3_log_bucket"])
            check_type(argname="argument s3_log_prefix", value=s3_log_prefix, expected_type=type_hints["s3_log_prefix"])
            check_type(argname="argument spark_submit_entry_point_arguments", value=spark_submit_entry_point_arguments, expected_type=type_hints["spark_submit_entry_point_arguments"])
            check_type(argname="argument spark_submit_parameters", value=spark_submit_parameters, expected_type=type_hints["spark_submit_parameters"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "execution_role": execution_role,
            "name": name,
            "spark_submit_entry_point": spark_submit_entry_point,
            "virtual_cluster_id": virtual_cluster_id,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if schedule is not None:
            self._values["schedule"] = schedule
        if application_configuration is not None:
            self._values["application_configuration"] = application_configuration
        if cloud_watch_log_group is not None:
            self._values["cloud_watch_log_group"] = cloud_watch_log_group
        if cloud_watch_log_group_stream_prefix is not None:
            self._values["cloud_watch_log_group_stream_prefix"] = cloud_watch_log_group_stream_prefix
        if execution_timeout is not None:
            self._values["execution_timeout"] = execution_timeout
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if release_label is not None:
            self._values["release_label"] = release_label
        if s3_log_bucket is not None:
            self._values["s3_log_bucket"] = s3_log_bucket
        if s3_log_prefix is not None:
            self._values["s3_log_prefix"] = s3_log_prefix
        if spark_submit_entry_point_arguments is not None:
            self._values["spark_submit_entry_point_arguments"] = spark_submit_entry_point_arguments
        if spark_submit_parameters is not None:
            self._values["spark_submit_parameters"] = spark_submit_parameters
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The Schedule to run the Step Functions state machine.

        :default: - The Step Functions State Machine is not scheduled.
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM execution Role ARN for the EMR on EKS job.'''
        result = self._values.get("execution_role")
        assert result is not None, "Required property 'execution_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The Spark job name.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def spark_submit_entry_point(self) -> builtins.str:
        '''The entry point for the Spark submit job run.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("spark_submit_entry_point")
        assert result is not None, "Required property 'spark_submit_entry_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_cluster_id(self) -> builtins.str:
        '''The EMR on EKS virtual cluster ID.'''
        result = self._values.get("virtual_cluster_id")
        assert result is not None, "Required property 'virtual_cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_configuration(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The application configuration override for the Spark submit job run.

        :default: - No configuration is passed to the job.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("application_configuration")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def cloud_watch_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group name for log publishing.

        :default: - CloudWatch is not used for logging
        '''
        result = self._values.get("cloud_watch_log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def cloud_watch_log_group_stream_prefix(self) -> typing.Optional[builtins.str]:
        '''The CloudWatch Log Group stream prefix for log publishing.

        :default: - The application name is used as the prefix
        '''
        result = self._values.get("cloud_watch_log_group_stream_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The execution timeout.

        :default: - 30 minutes
        '''
        result = self._values.get("execution_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of retries.

        :default: - No retry
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def release_label(self) -> typing.Optional[EmrRuntimeVersion]:
        '''The EMR release version associated with the application.

        The EMR release can be found in this `documentation <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html>`_

        :default: `EMR_DEFAULT_VERSION <https://github.com/awslabs/data-solutions-framework-on-aws/blob/HEAD/framework/src/processing/lib/emr-releases.ts#L46>`_
        '''
        result = self._values.get("release_label")
        return typing.cast(typing.Optional[EmrRuntimeVersion], result)

    @builtins.property
    def s3_log_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The S3 Bucket for log publishing.

        :default: - No logging to S3
        '''
        result = self._values.get("s3_log_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def s3_log_prefix(self) -> typing.Optional[builtins.str]:
        '''The S3 Bucket prefix for log publishing.

        :default: - No logging to S3
        '''
        result = self._values.get("s3_log_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spark_submit_entry_point_arguments(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''The arguments for the Spark submit job run.

        :default: - No arguments are passed to the job.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("spark_submit_entry_point_arguments")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def spark_submit_parameters(self) -> typing.Optional[builtins.str]:
        '''The parameters for the Spark submit job run.

        :default: - No parameters are passed to the job.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("spark_submit_parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Tags to be added to the EMR Serverless job.

        :default: - No tags are added
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrContainersJobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SparkEmrServerlessJob(
    SparkJob,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrServerlessJob",
):
    '''A construct to run Spark Jobs using EMR Serverless.

    Creates a State Machine that orchestrates the Spark Job.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Processing/spark-emr-serverless-job

    Example::

        from aws_cdk.aws_iam import PolicyDocument, PolicyStatement
        from aws_cdk.aws_stepfunctions import JsonPath
        
        
        my_execution_role = dsf.processing.SparkEmrServerlessRuntime.create_execution_role(self, "execRole1")
        job = dsf.processing.SparkEmrServerlessJob(self, "SparkJob",
            job_config={
                "Name": JsonPath.format("ge_profile-{}", JsonPath.uuid()),
                "ApplicationId": "APPLICATION_ID",
                "ExecutionRoleArn": my_execution_role.role_arn,
                "JobDriver": {
                    "SparkSubmit": {
                        "EntryPoint": "s3://S3-BUCKET/pi.py",
                        "EntryPointArguments": [],
                        "SparkSubmitParameters": "--conf spark.executor.instances=2 --conf spark.executor.memory=2G --conf spark.driver.memory=2G --conf spark.executor.cores=4"
                    }
                }
            }
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Union[typing.Union["SparkEmrServerlessJobProps", typing.Dict[builtins.str, typing.Any]], typing.Union["SparkEmrServerlessJobApiProps", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9e9fa311438a71a5339a3e1217e1111ddca103d8887c7683da09e0981dd3551)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantExecutionRole")
    def _grant_execution_role(self, role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''Grants the necessary permissions to the Step Functions StateMachine to be able to start EMR Serverless job.

        :param role: Step Functions StateMachine IAM role.

        :see: SparkRuntimeServerless.grantJobExecution
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baebdb2d83adfd5e8b4a5d3b2195e0a09fca99c32873552880bb510036c2cc12)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(None, jsii.invoke(self, "grantExecutionRole", [role]))

    @jsii.member(jsii_name="returnJobFailTaskProps")
    def _return_job_fail_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.FailProps:
        '''Returns the props for the step function task that handles the failure if the EMR Serverless job fails.

        :return: FailProps The error details of the failed Spark Job
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.FailProps, jsii.invoke(self, "returnJobFailTaskProps", []))

    @jsii.member(jsii_name="returnJobMonitorTaskProps")
    def _return_job_monitor_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Returns the props for the Step Functions CallAwsService Construct that checks the execution status of the Spark job, it calls the `GetJobRun API <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_GetJobRun.html>`_.

        :return: CallAwsServiceProps

        :see: CallAwsService
        :link: [https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_stepfunctions_tasks.CallAwsService.html]
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps, jsii.invoke(self, "returnJobMonitorTaskProps", []))

    @jsii.member(jsii_name="returnJobStartTaskProps")
    def _return_job_start_task_props(
        self,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps:
        '''Returns the props for the Step Functions CallAwsService Construct that starts the Spark job, it calls the `StartJobRun API <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_StartJobRun.html>`_.

        :return: CallAwsServiceProps

        :see: CallAwsService
        :link: [https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_stepfunctions_tasks.CallAwsService.html]
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.CallAwsServiceProps, jsii.invoke(self, "returnJobStartTaskProps", []))

    @jsii.member(jsii_name="returnJobStatusCancelled")
    def _return_job_status_cancelled(self) -> builtins.str:
        '''Returns the status of the EMR Serverless job that is cancelled based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusCancelled", []))

    @jsii.member(jsii_name="returnJobStatusFailed")
    def _return_job_status_failed(self) -> builtins.str:
        '''Returns the status of the EMR Serverless job that failed based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusFailed", []))

    @jsii.member(jsii_name="returnJobStatusSucceed")
    def _return_job_status_succeed(self) -> builtins.str:
        '''Returns the status of the EMR Serverless job that succeeded based on the GetJobRun API response.

        :return: string
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "returnJobStatusSucceed", []))

    @builtins.property
    @jsii.member(jsii_name="sparkJobExecutionRole")
    def spark_job_execution_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The Spark job execution role.

        Use this property to add additional IAM permissions if necessary.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "sparkJobExecutionRole"))

    @spark_job_execution_role.setter
    def spark_job_execution_role(
        self,
        value: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe0d4bcffa152cbc27c3740ca87000501f8cd1de45e8a4a8086fa5f6c509f61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkJobExecutionRole", value)


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrServerlessJobApiProps",
    jsii_struct_bases=[SparkJobProps],
    name_mapping={
        "removal_policy": "removalPolicy",
        "schedule": "schedule",
        "job_config": "jobConfig",
    },
)
class SparkEmrServerlessJobApiProps(SparkJobProps):
    def __init__(
        self,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        job_config: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        '''Configuration for the EMR Serverless Job API.

        Use this interface when ``SparkEmrServerlessJobProps`` doesn't give you access to the configuration parameters you need.

        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param schedule: The Schedule to run the Step Functions state machine. Default: - The Step Functions State Machine is not scheduled.
        :param job_config: EMR Serverless Job Configuration.

        :link: [https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_StartJobRun.html]
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3715d19b3d27a55da4211f5a03616044ea68b7645fb93006f6c4ab7fb873617)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument job_config", value=job_config, expected_type=type_hints["job_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "job_config": job_config,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The Schedule to run the Step Functions state machine.

        :default: - The Step Functions State Machine is not scheduled.
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def job_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''EMR Serverless Job Configuration.

        :link: [https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_StartJobRun.html]
        '''
        result = self._values.get("job_config")
        assert result is not None, "Required property 'job_config' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrServerlessJobApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.processing.SparkEmrServerlessJobProps",
    jsii_struct_bases=[SparkJobProps],
    name_mapping={
        "removal_policy": "removalPolicy",
        "schedule": "schedule",
        "application_id": "applicationId",
        "execution_role": "executionRole",
        "name": "name",
        "spark_submit_entry_point": "sparkSubmitEntryPoint",
        "application_configuration": "applicationConfiguration",
        "cloud_watch_encryption_key": "cloudWatchEncryptionKey",
        "cloud_watch_log_group": "cloudWatchLogGroup",
        "cloud_watch_log_group_stream_prefix": "cloudWatchLogGroupStreamPrefix",
        "cloud_watch_logtypes": "cloudWatchLogtypes",
        "execution_timeout": "executionTimeout",
        "persistent_app_ui": "persistentAppUi",
        "persistent_app_ui_key": "persistentAppUIKey",
        "s3_log_bucket": "s3LogBucket",
        "s3_log_encryption_key": "s3LogEncryptionKey",
        "s3_log_prefix": "s3LogPrefix",
        "spark_submit_entry_point_arguments": "sparkSubmitEntryPointArguments",
        "spark_submit_parameters": "sparkSubmitParameters",
        "tags": "tags",
    },
)
class SparkEmrServerlessJobProps(SparkJobProps):
    def __init__(
        self,
        *,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        application_id: builtins.str,
        execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        name: builtins.str,
        spark_submit_entry_point: builtins.str,
        application_configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        cloud_watch_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        cloud_watch_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        cloud_watch_log_group_stream_prefix: typing.Optional[builtins.str] = None,
        cloud_watch_logtypes: typing.Optional[builtins.str] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        persistent_app_ui: typing.Optional[builtins.bool] = None,
        persistent_app_ui_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        s3_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        s3_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        s3_log_prefix: typing.Optional[builtins.str] = None,
        spark_submit_entry_point_arguments: typing.Optional[typing.Sequence[builtins.str]] = None,
        spark_submit_parameters: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param schedule: The Schedule to run the Step Functions state machine. Default: - The Step Functions State Machine is not scheduled.
        :param application_id: The EMR Serverless Application to execute the Spark Job.
        :param execution_role: The IAM execution Role for the EMR Serverless job.
        :param name: The Spark Job name.
        :param spark_submit_entry_point: The entry point for the Spark submit job run.
        :param application_configuration: The application configuration override for the Spark submit job run. Default: - No configuration is passed to the job.
        :param cloud_watch_encryption_key: The KMS Key for encrypting logs on CloudWatch. Default: - No encryption
        :param cloud_watch_log_group: The CloudWatch Log Group name for log publishing. Default: - No logging to CloudWatch
        :param cloud_watch_log_group_stream_prefix: The CloudWatch Log Group Stream prefix for log publishing. Default: - No prefix is used
        :param cloud_watch_logtypes: The types of logs to log in CloudWatch Log.
        :param execution_timeout: The execution timeout. Default: - 30 minutes
        :param persistent_app_ui: Enable Spark persistent UI logs in EMR managed storage. Default: - true
        :param persistent_app_ui_key: The KMS Key ARN to encrypt Spark persistent UI logs in EMR managed storage. Default: - Use EMR managed Key
        :param s3_log_bucket: The S3 Bucket for log publishing. Default: - No logging to S3
        :param s3_log_encryption_key: The KMS Key for encrypting logs on S3. Default: - No encryption
        :param s3_log_prefix: The S3 Bucket prefix for log publishing. Default: - No logging to S3
        :param spark_submit_entry_point_arguments: The arguments for the Spark submit job run. Default: - No arguments are passed to the job.
        :param spark_submit_parameters: The parameters for the Spark submit job run. Default: - No parameters are passed to the job.
        :param tags: Tags to be added to the EMR Serverless job. Default: - No tags are added
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__110b6ea56b7255580d3f94b0c3c08013ac9a8554186795bb49a5024715d80e23)
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument application_id", value=application_id, expected_type=type_hints["application_id"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument spark_submit_entry_point", value=spark_submit_entry_point, expected_type=type_hints["spark_submit_entry_point"])
            check_type(argname="argument application_configuration", value=application_configuration, expected_type=type_hints["application_configuration"])
            check_type(argname="argument cloud_watch_encryption_key", value=cloud_watch_encryption_key, expected_type=type_hints["cloud_watch_encryption_key"])
            check_type(argname="argument cloud_watch_log_group", value=cloud_watch_log_group, expected_type=type_hints["cloud_watch_log_group"])
            check_type(argname="argument cloud_watch_log_group_stream_prefix", value=cloud_watch_log_group_stream_prefix, expected_type=type_hints["cloud_watch_log_group_stream_prefix"])
            check_type(argname="argument cloud_watch_logtypes", value=cloud_watch_logtypes, expected_type=type_hints["cloud_watch_logtypes"])
            check_type(argname="argument execution_timeout", value=execution_timeout, expected_type=type_hints["execution_timeout"])
            check_type(argname="argument persistent_app_ui", value=persistent_app_ui, expected_type=type_hints["persistent_app_ui"])
            check_type(argname="argument persistent_app_ui_key", value=persistent_app_ui_key, expected_type=type_hints["persistent_app_ui_key"])
            check_type(argname="argument s3_log_bucket", value=s3_log_bucket, expected_type=type_hints["s3_log_bucket"])
            check_type(argname="argument s3_log_encryption_key", value=s3_log_encryption_key, expected_type=type_hints["s3_log_encryption_key"])
            check_type(argname="argument s3_log_prefix", value=s3_log_prefix, expected_type=type_hints["s3_log_prefix"])
            check_type(argname="argument spark_submit_entry_point_arguments", value=spark_submit_entry_point_arguments, expected_type=type_hints["spark_submit_entry_point_arguments"])
            check_type(argname="argument spark_submit_parameters", value=spark_submit_parameters, expected_type=type_hints["spark_submit_parameters"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_id": application_id,
            "execution_role": execution_role,
            "name": name,
            "spark_submit_entry_point": spark_submit_entry_point,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if schedule is not None:
            self._values["schedule"] = schedule
        if application_configuration is not None:
            self._values["application_configuration"] = application_configuration
        if cloud_watch_encryption_key is not None:
            self._values["cloud_watch_encryption_key"] = cloud_watch_encryption_key
        if cloud_watch_log_group is not None:
            self._values["cloud_watch_log_group"] = cloud_watch_log_group
        if cloud_watch_log_group_stream_prefix is not None:
            self._values["cloud_watch_log_group_stream_prefix"] = cloud_watch_log_group_stream_prefix
        if cloud_watch_logtypes is not None:
            self._values["cloud_watch_logtypes"] = cloud_watch_logtypes
        if execution_timeout is not None:
            self._values["execution_timeout"] = execution_timeout
        if persistent_app_ui is not None:
            self._values["persistent_app_ui"] = persistent_app_ui
        if persistent_app_ui_key is not None:
            self._values["persistent_app_ui_key"] = persistent_app_ui_key
        if s3_log_bucket is not None:
            self._values["s3_log_bucket"] = s3_log_bucket
        if s3_log_encryption_key is not None:
            self._values["s3_log_encryption_key"] = s3_log_encryption_key
        if s3_log_prefix is not None:
            self._values["s3_log_prefix"] = s3_log_prefix
        if spark_submit_entry_point_arguments is not None:
            self._values["spark_submit_entry_point_arguments"] = spark_submit_entry_point_arguments
        if spark_submit_parameters is not None:
            self._values["spark_submit_parameters"] = spark_submit_parameters
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The Schedule to run the Step Functions state machine.

        :default: - The Step Functions State Machine is not scheduled.
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def application_id(self) -> builtins.str:
        '''The EMR Serverless Application to execute the Spark Job.'''
        result = self._values.get("application_id")
        assert result is not None, "Required property 'application_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM execution Role for the EMR Serverless job.'''
        result = self._values.get("execution_role")
        assert result is not None, "Required property 'execution_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The Spark Job name.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def spark_submit_entry_point(self) -> builtins.str:
        '''The entry point for the Spark submit job run.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("spark_submit_entry_point")
        assert result is not None, "Required property 'spark_submit_entry_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_configuration(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The application configuration override for the Spark submit job run.

        :default: - No configuration is passed to the job.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("application_configuration")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def cloud_watch_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key for encrypting logs on CloudWatch.

        :default: - No encryption
        '''
        result = self._values.get("cloud_watch_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def cloud_watch_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group name for log publishing.

        :default: - No logging to CloudWatch
        '''
        result = self._values.get("cloud_watch_log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def cloud_watch_log_group_stream_prefix(self) -> typing.Optional[builtins.str]:
        '''The CloudWatch Log Group Stream prefix for log publishing.

        :default: - No prefix is used
        '''
        result = self._values.get("cloud_watch_log_group_stream_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_watch_logtypes(self) -> typing.Optional[builtins.str]:
        '''The types of logs to log in CloudWatch Log.'''
        result = self._values.get("cloud_watch_logtypes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The execution timeout.

        :default: - 30 minutes
        '''
        result = self._values.get("execution_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def persistent_app_ui(self) -> typing.Optional[builtins.bool]:
        '''Enable Spark persistent UI logs in EMR managed storage.

        :default: - true
        '''
        result = self._values.get("persistent_app_ui")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def persistent_app_ui_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key ARN to encrypt Spark persistent UI logs in EMR managed storage.

        :default: - Use EMR managed Key
        '''
        result = self._values.get("persistent_app_ui_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def s3_log_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The S3 Bucket for log publishing.

        :default: - No logging to S3
        '''
        result = self._values.get("s3_log_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def s3_log_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key for encrypting logs on S3.

        :default: - No encryption
        '''
        result = self._values.get("s3_log_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def s3_log_prefix(self) -> typing.Optional[builtins.str]:
        '''The S3 Bucket prefix for log publishing.

        :default: - No logging to S3
        '''
        result = self._values.get("s3_log_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spark_submit_entry_point_arguments(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''The arguments for the Spark submit job run.

        :default: - No arguments are passed to the job.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("spark_submit_entry_point_arguments")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def spark_submit_parameters(self) -> typing.Optional[builtins.str]:
        '''The parameters for the Spark submit job run.

        :default: - No parameters are passed to the job.

        :see: https://docs.aws.amazon.com/emr-on-eks/latest/APIReference/API_StartJobRun.html
        '''
        result = self._values.get("spark_submit_parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Tags to be added to the EMR Serverless job.

        :default: - No tags are added
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SparkEmrServerlessJobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EmrContainersRuntimeVersion",
    "EmrRuntimeVersion",
    "EmrVirtualClusterProps",
    "KarpenterVersion",
    "PySparkApplicationPackage",
    "PySparkApplicationPackageProps",
    "SparkEmrCICDPipeline",
    "SparkEmrCICDPipelineProps",
    "SparkEmrContainersJob",
    "SparkEmrContainersJobApiProps",
    "SparkEmrContainersJobProps",
    "SparkEmrContainersRuntime",
    "SparkEmrContainersRuntimeInteractiveSessionProps",
    "SparkEmrContainersRuntimeProps",
    "SparkEmrServerlessJob",
    "SparkEmrServerlessJobApiProps",
    "SparkEmrServerlessJobProps",
    "SparkEmrServerlessRuntime",
    "SparkEmrServerlessRuntimeProps",
    "SparkImage",
    "SparkJob",
    "SparkJobProps",
]

publication.publish()

def _typecheckingstub__3eacff78ea6ec7021e0b59026f040a0268c2232c203599c99b35d629a6b01cd4(
    *,
    name: builtins.str,
    create_namespace: typing.Optional[builtins.bool] = None,
    eks_namespace: typing.Optional[builtins.str] = None,
    set_namespace_resource_quota: typing.Optional[builtins.bool] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f090fca4792f38c321086e79a1854d7d328b1646646610fa2828c5a8d7def302(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_name: builtins.str,
    entrypoint_path: builtins.str,
    artifacts_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    asset_upload_memory_size: typing.Optional[jsii.Number] = None,
    asset_upload_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    asset_upload_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    dependencies_folder: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    venv_archive_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a9c55335a32c81401f78a9db5843ed203f0bdbfd4bfbaaafd82da582d424426(
    *,
    application_name: builtins.str,
    entrypoint_path: builtins.str,
    artifacts_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    asset_upload_memory_size: typing.Optional[jsii.Number] = None,
    asset_upload_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    asset_upload_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    dependencies_folder: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    venv_archive_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38571fed7c1c1182e0e221f9c4b475a7538d4819638aeacc0a37098ed8937873(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_stack_factory: _ApplicationStackFactory_52ae437f,
    spark_application_name: builtins.str,
    cdk_application_path: typing.Optional[builtins.str] = None,
    integ_test_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    integ_test_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    integ_test_script: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    spark_application_path: typing.Optional[builtins.str] = None,
    spark_image: typing.Optional[SparkImage] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ed1ce57c4d326181a7695ce8cc994691b5a683bea0b04d81008a11d627ea7c3(
    *,
    application_stack_factory: _ApplicationStackFactory_52ae437f,
    spark_application_name: builtins.str,
    cdk_application_path: typing.Optional[builtins.str] = None,
    integ_test_env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    integ_test_permissions: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    integ_test_script: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    spark_application_path: typing.Optional[builtins.str] = None,
    spark_image: typing.Optional[SparkImage] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a77fbf2d70f2dbc9f109068a582011e2e95e47ce83ad5a5851a10a01d18fdd7c(
    scope: _constructs_77d1e7e8.Construct,
    *,
    kubectl_lambda_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
    public_access_cid_rs: typing.Sequence[builtins.str],
    create_emr_on_eks_service_linked_role: typing.Optional[builtins.bool] = None,
    default_nodes: typing.Optional[builtins.bool] = None,
    ec2_instance_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    eks_admin_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    eks_cluster: typing.Optional[_aws_cdk_aws_eks_ceddda9d.Cluster] = None,
    eks_cluster_name: typing.Optional[builtins.str] = None,
    eks_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    karpenter_version: typing.Optional[KarpenterVersion] = None,
    kubernetes_version: typing.Optional[_aws_cdk_aws_eks_ceddda9d.KubernetesVersion] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    vpc_cidr: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__931f90ff0171c67483277d67df76d04a03cf1132d70869f146ea53d6a1c92fce(
    start_job_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    execution_role_arn: typing.Sequence[builtins.str],
    virtual_cluster_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__927fa0229d8dda7caa502f18c7a9f51981e71e4c0cc270f54d8f67c054db1634(
    scope: _constructs_77d1e7e8.Construct,
    *,
    name: builtins.str,
    create_namespace: typing.Optional[builtins.bool] = None,
    eks_namespace: typing.Optional[builtins.str] = None,
    set_namespace_resource_quota: typing.Optional[builtins.bool] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2c935910c81be69288fc2aa9fbc97c99bfffa5ec62bb858af28466956ca08c4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    managed_endpoint_name: builtins.str,
    virtual_cluster_id: builtins.str,
    configuration_overrides: typing.Any = None,
    emr_on_eks_version: typing.Optional[EmrContainersRuntimeVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__601f721a4284cc744cbcd5810fe27b439ac2a96d173a458ca4b1d67a1bd7151b(
    id: builtins.str,
    manifest: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e2821f4b5dcbd7a6f122cd2be5bd7dcbcd511232bda21361311446b972bd638(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    policy: _aws_cdk_aws_iam_ceddda9d.IManagedPolicy,
    eks_namespace: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9a6c1b3b29d69a1313c1942c1370fef49d07e8cc8b8fa91ca4ffa3902a5ebe4(
    id: builtins.str,
    file_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cac0f55f7f430c4f64c3e56df1172bf72f1f6675159abc90c51decfe6613fdd4(
    *,
    execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    managed_endpoint_name: builtins.str,
    virtual_cluster_id: builtins.str,
    configuration_overrides: typing.Any = None,
    emr_on_eks_version: typing.Optional[EmrContainersRuntimeVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a45f77e4f1615abf22aa897dea1c5e0b6dbc0179bda92346a2cc173bd41ce3df(
    *,
    kubectl_lambda_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
    public_access_cid_rs: typing.Sequence[builtins.str],
    create_emr_on_eks_service_linked_role: typing.Optional[builtins.bool] = None,
    default_nodes: typing.Optional[builtins.bool] = None,
    ec2_instance_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    eks_admin_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    eks_cluster: typing.Optional[_aws_cdk_aws_eks_ceddda9d.Cluster] = None,
    eks_cluster_name: typing.Optional[builtins.str] = None,
    eks_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    karpenter_version: typing.Optional[KarpenterVersion] = None,
    kubernetes_version: typing.Optional[_aws_cdk_aws_eks_ceddda9d.KubernetesVersion] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    vpc_cidr: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ff128785929fb50a3c575346aa3fdc433fd1cc2e7e69efe27b37f38c4a0e14d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    architecture: typing.Optional[_Architecture_b811f66d] = None,
    auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    release_label: typing.Optional[EmrRuntimeVersion] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]] = None,
    worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf458fcad8d4f2991ec79ae36da0359407a6b85df13fecd2b6514a7641b19dc6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    execution_role_policy_document: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    iam_policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f44185a448635116f97f58d4c9eefe1100885b3161858f3fe7876c20700962f(
    start_job_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    execution_role_arn: typing.Sequence[builtins.str],
    application_arns: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa0057b875c053777bbb69a3ca41c8d91bc6dfb1da713059ddede2fe71fd51a4(
    start_job_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    execution_role_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb7370f53b2007953cbbb308224a013d555ba02de4f43ab678e1a50f670c7f34(
    *,
    name: builtins.str,
    architecture: typing.Optional[_Architecture_b811f66d] = None,
    auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    release_label: typing.Optional[EmrRuntimeVersion] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]] = None,
    worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b46ce074c66eb8fbf61ac4f9d6d05a3956159aaff2397a4bd1ca091482afdad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    tracking_tag: builtins.str,
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd9de1b490002aff5cc9e89a8915a5df3f030e1ac317b39493f473190627d439(
    name: builtins.str,
    encryption_key_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__928342d401671b9066231b19946bece7cbccc2153476b6fda36afb0676f47e2e(
    s3_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    s3_log_prefix: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10cc4976ae85391a5f2a8a3056343b905407fd9dbd62a49da8ad2981674a5d07(
    job_timeout: _aws_cdk_ceddda9d.Duration,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__223659f083d952cd4a943949e12330a9d6a991cf1a9057a8c4f950353ff8a3b9(
    value: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dd675e43931483584ef06f9389a9b5c1ac642e585a5ad647dbbb0b15e912150(
    value: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d63fb6cc0f082e5380e5c5a5b1a97059409ed12f2ff5c1c9ca3b0dcc98b2ed26(
    value: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbd196ec4802b268cdc82b1778fe7db3c7337933ea458c5fcf97b1b893125bfd(
    value: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a6f0a1184cb90dc918c07815fffa6746da42c8a5c1fbf7b78a4c6be64bd1f77(
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca9f736db1e60c03ac2e3311780bbfdd65a92742325e77e5ea245bbabd816049(
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf608b3fc77c6d9856f7aa927a1785da24e08760630a40ca167262caa0194024(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Union[typing.Union[SparkEmrContainersJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[SparkEmrContainersJobApiProps, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65cf3fbfa0a42b552961215c2e42b33d95b9ba7c2b79ae62e442cf5827eaab9c(
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2294c4739f96f8aaf5904bda10141a59227860735e4bbf1090aae3f75d632e26(
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    job_config: typing.Mapping[builtins.str, typing.Any],
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__455642341a460c5395b9d20088cdd0585965ef1072e1977e693f6fc41ec0e870(
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    name: builtins.str,
    spark_submit_entry_point: builtins.str,
    virtual_cluster_id: builtins.str,
    application_configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    cloud_watch_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    cloud_watch_log_group_stream_prefix: typing.Optional[builtins.str] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    release_label: typing.Optional[EmrRuntimeVersion] = None,
    s3_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    s3_log_prefix: typing.Optional[builtins.str] = None,
    spark_submit_entry_point_arguments: typing.Optional[typing.Sequence[builtins.str]] = None,
    spark_submit_parameters: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9e9fa311438a71a5339a3e1217e1111ddca103d8887c7683da09e0981dd3551(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Union[typing.Union[SparkEmrServerlessJobProps, typing.Dict[builtins.str, typing.Any]], typing.Union[SparkEmrServerlessJobApiProps, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baebdb2d83adfd5e8b4a5d3b2195e0a09fca99c32873552880bb510036c2cc12(
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe0d4bcffa152cbc27c3740ca87000501f8cd1de45e8a4a8086fa5f6c509f61(
    value: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3715d19b3d27a55da4211f5a03616044ea68b7645fb93006f6c4ab7fb873617(
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    job_config: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__110b6ea56b7255580d3f94b0c3c08013ac9a8554186795bb49a5024715d80e23(
    *,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    application_id: builtins.str,
    execution_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    name: builtins.str,
    spark_submit_entry_point: builtins.str,
    application_configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    cloud_watch_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    cloud_watch_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    cloud_watch_log_group_stream_prefix: typing.Optional[builtins.str] = None,
    cloud_watch_logtypes: typing.Optional[builtins.str] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    persistent_app_ui: typing.Optional[builtins.bool] = None,
    persistent_app_ui_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    s3_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    s3_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    s3_log_prefix: typing.Optional[builtins.str] = None,
    spark_submit_entry_point_arguments: typing.Optional[typing.Sequence[builtins.str]] = None,
    spark_submit_parameters: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

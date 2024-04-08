from os import path

from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk.aws_apigateway import Cors, CorsOptions
from constructs import Construct


class CommonServiceStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, stage_name="dev", **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._stage_name = stage_name

    def _create_general_dynamo_table(self, name: str, stage_name: str):
        return dynamodb.TableV2(
            self,
            f"{self._stage_name}-{name}-table",
            table_name=f"{self._stage_name}-{name}-table",
            partition_key=dynamodb.Attribute(
                name="pk", type=dynamodb.AttributeType.STRING
            ),
            contributor_insights=True,
            table_class=dynamodb.TableClass.STANDARD,
            point_in_time_recovery=True,
            removal_policy=(
                RemovalPolicy.RETAIN
                if stage_name in ["prod"]
                else RemovalPolicy.DESTROY
            ),
        )

    def _create_python_lambda_function(
        self,
        identifier: str,
        source: str,
        lambda_layers: list,
        envs: dict,
        function_handler: str,
    ):
        _lambda_function = lambda_.Function(
            self,
            identifier,
            function_name=identifier,
            code=lambda_.Code.from_asset(path.join(source)),
            handler=function_handler,
            runtime=lambda_.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(300),
            layers=lambda_layers,
            environment=envs,
        )
        return _lambda_function

    def _create_node_lambda_function(
        self,
        identifier: str,
        source: str,
        lambda_layers: list,
        envs: dict,
        function_handler: str,
    ):
        _lambda_function = lambda_.Function(
            self,
            identifier,
            function_name=identifier,
            code=lambda_.Code.from_asset(path.join(source)),
            handler=function_handler,
            runtime=lambda_.Runtime.NODEJS_20_X,
            timeout=Duration.seconds(300),
            layers=lambda_layers,
            environment=envs,
        )
        return _lambda_function

    def _create_api_gw(self, identifier: str, handler_function):
        api_gateway_resource = apigw.LambdaRestApi(
            self,
            identifier,
            handler=handler_function,
            proxy=False,
            default_cors_preflight_options=CorsOptions(
                allow_origins=Cors.ALL_ORIGINS,
                allow_methods=Cors.ALL_METHODS,
                allow_credentials=True,
                allow_headers=Cors.DEFAULT_HEADERS,
            ),
        )
        return api_gateway_resource

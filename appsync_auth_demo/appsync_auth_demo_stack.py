from aws_cdk import CfnOutput, Stack
from aws_cdk.aws_appsync import AuthorizationConfig, AuthorizationMode, AuthorizationType, Definition, FieldLogLevel, \
  GraphqlApi, \
  LambdaAuthorizerConfig, Resolver
from aws_cdk.aws_iam import ManagedPolicy, Role, ServicePrincipal
from aws_cdk.aws_lambda import Code, Function, LayerVersion, Runtime, Tracing
from constructs import Construct


class AppsyncAuthDemoStack(Stack):

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    powertools_layer = LayerVersion.from_layer_version_arn(self, "PowertoolsLayer",
                                                           f'arn:aws:lambda:{Stack.of(self).region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:79')

    auth_function = Function(self, "AuthFunction",
                             runtime=Runtime.PYTHON_3_12,
                             handler="auth.handler",
                             code=Code.from_asset("appsync_auth_demo"),
                             tracing=Tracing.ACTIVE,
                             layers=[powertools_layer],
                             )

    app_function = Function(self, "ListPostsFunction",
                            runtime=Runtime.PYTHON_3_12,
                            handler="app.handler",
                            tracing=Tracing.ACTIVE,
                            code=Code.from_asset("appsync_auth_demo"),
                            layers=[powertools_layer],
                            )

    log_role = Role(self, "AppSyncLogRole",
                    assumed_by=ServicePrincipal("appsync.amazonaws.com"),
                    managed_policies=[
                      ManagedPolicy.from_aws_managed_policy_name("service-role/AWSAppSyncPushToCloudWatchLogs")
                    ])

    api = GraphqlApi(self, "Api",
                     name="demo=api",
                     definition=Definition.from_file("schema.graphql"),
                     authorization_config=AuthorizationConfig(
                       default_authorization=AuthorizationMode(
                         authorization_type=AuthorizationType.LAMBDA,
                         lambda_authorizer_config=LambdaAuthorizerConfig(
                           handler=auth_function
                         )
                       )
                     ),
                     xray_enabled=True,
                     log_config={"field_log_level": FieldLogLevel.ALL,
                                 "exclude_verbose_content": False,
                                 "role": log_role
                                 })

    list_posts_data_source = api.add_lambda_data_source("ListPostsDataSource",
                                                        app_function)

    create_posts_data_source = api.add_lambda_data_source("CreatePostsDataSource",
                                                          app_function)

    list_posts_resolver = Resolver(self, "ListPostsResolver",
                                   api=api,
                                   type_name="Query",
                                   field_name="listPosts",
                                   data_source=list_posts_data_source,
                                   )

    create_post_resolver = Resolver(self, "CreatePostResolver",
                                    api=api,
                                    type_name="Mutation",
                                    field_name="createPost",
                                    data_source=create_posts_data_source,
                                    )

    auth_function.add_permission("AppSyncInvokePermission",
                                 principal=ServicePrincipal("appsync.amazonaws.com"),
                                 action="lambda:InvokeFunction")

    CfnOutput(self, "GraphQLAPIURL", value=api.graphql_url)

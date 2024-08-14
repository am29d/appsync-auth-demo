from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.appsync_authorizer_event import AppSyncAuthorizerEvent, \
  AppSyncAuthorizerResponse

logger = Logger()


def get_user_from_token(token):
  if token == "42":
    return {
      "id": "42",
      "name": "Arthur Dent",
      "role": "admin"
    }

  if token == "43":
    return {
      "id": "43",
      "name": "Ford Prefect",
      "role": "user"
    }
  raise ValueError("Invalid token")


@logger.inject_lambda_context(log_event=True, correlation_id_path=correlation_paths.APPSYNC_RESOLVER)
@event_source(data_class=AppSyncAuthorizerEvent)
def handler(event, context):
  try:
    user = get_user_from_token(event.authorization_token)
    return AppSyncAuthorizerResponse(
      authorize=True,
      resolver_context=user,
      deny_fields=['Mutation.createPost'] if user["role"] == "user" else []
    ).asdict()
  except ValueError as e:
    logger.exception(e)
    return AppSyncAuthorizerResponse(
      authorize=False,
    ).asdict()

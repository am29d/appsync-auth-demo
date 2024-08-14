import hashlib
import uuid
from typing import List
from uuid import uuid5

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from typing_extensions import TypedDict

logger = Logger()
tracer = Tracer()


class Comment(TypedDict):
  id: str
  postId: str
  content: str


class Post(TypedDict):
  id: str
  title: str
  content: str
  comments: list[Comment]


posts = [
  {
    "id": "1",
    "title": "First Post",
    "content": "This is the content of the first post.",
    "comments": [
      {"id": "1", "postId": "1", "content": "First comment on first post."},
      {"id": "2", "postId": "1", "content": "Second comment on first post."}
    ]
  },
  {
    "id": "2",
    "title": "Second Post",
    "content": "This is the content of the second post.",
    "comments": [
      {"id": "3", "postId": "2", "content": "First comment on second post."}
    ]
  },
  {
    "id": "3",
    "title": "Third Post",
    "content": "This is the content of the third post.",
    "comments": []
  },
  {
    "id": "4",
    "title": "Fourth Post",
    "content": "This is the content of the fourth post.",
    "comments": [
      {"id": "4", "postId": "4", "content": "First comment on fourth post."},
      {"id": "5", "postId": "4", "content": "Second comment on fourth post."},
      {"id": "6", "postId": "4", "content": "Third comment on fourth post."}
    ]
  },
  {
    "id": "5",
    "title": "Fifth Post",
    "content": "This is the content of the fifth post.",
    "comments": [
      {"id": "7", "postId": "5", "content": "First comment on fifth post."}
    ]
  }
]

app = AppSyncResolver()


def generate_id():
  # Generate a random UUID
  random_uuid = uuid.uuid4()
  # Hash the UUID using SHA-256 and take the first 8 characters
  hash_object = hashlib.sha256(random_uuid.bytes)
  return hash_object.hexdigest()[:8]


@app.resolver(type_name="Query", field_name="listPosts")
def list_posts() -> List[Post]:
  return posts


@app.resolver(type_name="Mutation", field_name="createPost")
def create_post(title: str, content: str) -> Post:
  post = {
    "id": generate_id(),
    "title": title,
    "content": content,
    "comments": []
  }
  posts.append(post)
  return post


@tracer.capture_lambda_handler()
@logger.inject_lambda_context(log_event=True, correlation_id_path=correlation_paths.APPSYNC_RESOLVER)
def handler(event, context):
  return app.resolve(event, context)

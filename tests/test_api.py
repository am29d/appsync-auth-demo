# tests/test_api.py
import faker
import pytest
from faker import Faker
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

API_URL = "https://XXXX.appsync-api.eu-west-1.amazonaws.com/graphql"  # Replace with your actual AppSync API URL
LIST_POSTS_QUERY = gql("""
        query ListPosts {
            listPosts {
                id
                title
                content
            }
        }
        """)

CREATE_POST_MUTATION = gql("""
    mutation CreatePost($title: String!, $content: String!) {
        createPost(title: $title, content: $content) {
            id
            title
            content
        }
    }
            """)

fake = Faker()


class TestNoAuthorization:
  @classmethod
  def setup_class(cls):
    transport = RequestsHTTPTransport(
      url=API_URL,
      headers={"Content-Type": "application/json"},
      use_json=True
    )
    cls.client = Client(transport=transport)

  def test_list_posts(self):
    with pytest.raises(Exception):
      self.client.execute(LIST_POSTS_QUERY)


class TestAuthorization42:
  @classmethod
  def setup_class(cls):
    transport = RequestsHTTPTransport(
      url=API_URL,
      headers={"Content-Type": "application/json", "Authorization": "42"},  # admin
      use_json=True
    )
    cls.client = Client(transport=transport)

  def test_list_posts(self):
    response = self.client.execute(LIST_POSTS_QUERY)
    assert "errors" not in response
    assert "listPosts" in response

  def test_create_post(self):
    response = self.client.execute(CREATE_POST_MUTATION, variable_values={"title": fake.sentence(nb_words=5),
                                                                          "content": fake.text(max_nb_chars=200)})
    assert "errors" not in response
    assert "createPost" in response
    assert "id" in response["createPost"]


class TestAuthorization43:
  @classmethod
  def setup_class(cls):
    transport = RequestsHTTPTransport(
      url=API_URL,
      headers={"Content-Type": "application/json", "Authorization": "43"},  # user
      use_json=True
    )
    cls.client = Client(transport=transport)

  def test_list_posts(self):
    response = self.client.execute(LIST_POSTS_QUERY)
    assert "errors" not in response
    assert "listPosts" in response

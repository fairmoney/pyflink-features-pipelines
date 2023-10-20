from typing import Optional, Any
from unittest import TestCase
import boto3
from boto3 import Session
from testcontainers import localstack
from testcontainers.localstack import LocalStackContainer

from pfp.test_utils.kinesis.client import TestKinesisClient


class KinesisIntegrationTestCase(TestCase):

    _localstack: LocalStackContainer
    _boto3_endpoint_url: str
    _boto3_session: Session
    _client: TestKinesisClient
    _stream_names: list[str]

    def __init__(self, stream_names: list[str]):
        super().__init__()
        self._stream_names = stream_names

    def setUp(self) -> None:
        self._localstack = LocalStackContainer(image="localstack/localstack:2.1.0").with_services("kinesis")
        self._localstack.start()
        self._boto3_endpoint_url = self._localstack.get_url()
        self._boto3_session = boto3.Session(
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            aws_session_token="test-token",
            region_name="test-region"
        )
        self._client = TestKinesisClient(boto3_endpoint_url=self._boto3_endpoint_url)
        for s in self._stream_names:
            self._client.create_stream(stream_name=s)

    def tearDown(self) -> None:
        for s in self._stream_names:
            self._client.delete_stream(s)

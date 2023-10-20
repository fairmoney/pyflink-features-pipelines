from time import sleep
from typing import Optional, Any
import logging
import boto3

logger = logging.getLogger("TestKinesisClient")


class TestKinesisClient:
    _client: Any

    def __init__(self, boto3_endpoint_url: Optional[str] = None):
        super().__init__()
        session = boto3.Session()
        client_args = dict(service_name="kinesis")
        if boto3_endpoint_url is not None:
            client_args.update(dict(endpoint_url=boto3_endpoint_url))
        self._client = session.client(**client_args)

    def _stream_exists(self, kinesis_stream_name: str) -> bool:
        try:
            status: str = self._client \
                .describe_stream(StreamName=kinesis_stream_name) \
                .get("StreamDescription") \
                .get("StreamStatus")
            return status == "ACTIVE"
        except:
            return False

    @staticmethod
    def _is_boto3_response_success(boto3_response: dict) -> bool:
        return boto3_response.get("ResponseMetadata").get("HTTPStatusCode") == 200

    def _list_shards(self, stream_name: str) -> list[str]:
        boto3_response = self._client.list_shards(StreamName=stream_name)
        if self._is_boto3_response_success(boto3_response=boto3_response):
            shards = boto3_response.get("Shards")
            return [s.get("ShardId") for s in shards]

    def _get_shard_iterator(self, stream_name: str, shard_id: str, shard_iterator_type) -> str:
        boto3_response = self._client.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType=shard_iterator_type
        )
        if self._is_boto3_response_success(boto3_response=boto3_response):
            return boto3_response.get("ShardIterator")
        else:
            raise Exception(f"Error while getting shard iterator: {boto3_response}")

    def _get_shard_iterators(
            self,
            stream_name: str,
            shard_iterator_type: Optional[str] = "TRIM_HORIZON"
    ) -> list[tuple[str, str]]:
        return [(
            shard_id,
            self._get_shard_iterator(
                stream_name=stream_name,
                shard_id=shard_id,
                shard_iterator_type=shard_iterator_type
            )
        ) for shard_id in self._list_shards(stream_name=stream_name)]

    def _get_records(self, first_shard_iterator: str):

        res = []

        def _loop(shard_iterator: str):
            boto3_response = self._client.get_records(
                ShardIterator=shard_iterator
            )
            if self._is_boto3_response_success(boto3_response=boto3_response):
                records = boto3_response["Records"]
                if not records:
                    return
                for r in records:
                    res.append(r)
                next_shard_iterator = boto3_response.get("NextShardIterator")
                if next_shard_iterator is not None:
                    return _loop(shard_iterator=next_shard_iterator)
                else:
                    return res

        return _loop(shard_iterator=first_shard_iterator)

    def fetch_records(self, stream_name: str, shard_iterator_type: Optional[str] = "TRIM_HORIZON"):
        shard_iterators = self._get_shard_iterators(stream_name=stream_name, shard_iterator_type=shard_iterator_type)
        if len(shard_iterators) > 1:
            raise NotImplemented("Consumer of Kinesis streams with more than 1 shard is not yet implemented for "
                                 "testing. Please use this consumer on a Kinesis stream with only 1 shard.")
        shard_iterator = shard_iterators[0][1]
        self._get_records(first_shard_iterator=shard_iterator)

    def create_stream(self, stream_name: str):
        response = self._client.create_stream(
            StreamName=stream_name,
            ShardCount=1,
            StreamModeDetails={
                "StreamMode": "PROVISIONED"
            }
        )
        if self._is_boto3_response_success(response):
            n_tries: int = 0
            max_tries: int = 3
            while n_tries < max_tries and not self._stream_exists(kinesis_stream_name=stream_name):
                logger.info(f"Waiting for stream {stream_name} to be created")
                n_tries += 1
                sleep(n_tries)
            if n_tries == max_tries:
                raise Exception(f"Reached maximum attempts at creating Kinesis stream {stream_name}")
        else:
            raise Exception(f"Error while creating stream {stream_name}: {response}")

    def delete_stream(self, stream_name: str):
        response = self._client.delete_stream(
            StreamName=stream_name,
            EnforceConsumerDeletion=True
        )
        if self._is_boto3_response_success(response):
            return
        else:
            raise Exception(f"Error while deleting Kinesis stream {stream_name}= {response}")
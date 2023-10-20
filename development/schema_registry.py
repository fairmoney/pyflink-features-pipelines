from pfp.schema_registry.core import LocalSchemaRegistryClient

src = LocalSchemaRegistryClient()
print(src.fetch_avro_schema(address="avro/kinesis/algo/algo-predictions-risk.avsc"))

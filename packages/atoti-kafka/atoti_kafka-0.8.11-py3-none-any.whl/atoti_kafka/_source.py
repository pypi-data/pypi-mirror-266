from __future__ import annotations

from collections.abc import Mapping
from datetime import timedelta

from atoti._java_api import JavaApi
from atoti._sources.data_source import DataSource
from atoti_core import TableIdentifier
from typing_extensions import override


class KafkaDataSource(DataSource):
    @property
    @override
    def key(self) -> str:
        return "KAFKA"

    def load_kafka_into_table(
        self,
        identifier: TableIdentifier,
        *,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        batch_duration: timedelta,
        consumer_config: Mapping[str, str],
        scenario_name: str,
    ) -> None:
        """Consume a Kafka topic and stream its records in an existing table."""
        params: dict[str, object] = {
            "bootstrapServers": bootstrap_servers,
            "topic": topic,
            "consumerGroupId": group_id,
            "keyDeserializerClass": "org.apache.kafka.common.serialization.StringDeserializer",
            "batchDuration": int(batch_duration.total_seconds() * 1000),
            "additionalParameters": consumer_config,
        }
        self.load_data_into_table(
            identifier,
            params,
            scenario_name=scenario_name,
        )


def load_kafka(
    identifier: TableIdentifier,
    /,
    bootstrap_server: str,
    topic: str,
    *,
    group_id: str,
    batch_duration: timedelta,
    consumer_config: Mapping[str, str],
    java_api: JavaApi,
    scenario_name: str,
) -> None:
    KafkaDataSource(
        load_data_into_table=java_api.load_data_into_table
    ).load_kafka_into_table(
        identifier,
        bootstrap_servers=bootstrap_server,
        topic=topic,
        group_id=group_id,
        batch_duration=batch_duration,
        consumer_config=consumer_config,
        scenario_name=scenario_name,
    )

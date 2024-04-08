from kafka import KafkaConsumer

def get_consumer(topic: str, api_id: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers='kafka.in.dalpha.so:9092',
        group_id=f'ai-worker-{api_id}',
    )

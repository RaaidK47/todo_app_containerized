import asyncio
from aiokafka import AIOKafkaConsumer
import streamlit as st

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

KAFKA_TOPIC = "your_topic"
KAFKA_BOOTSTRAP_SERVERS = "broker:19092"

async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="streamlit-group",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            st.write(f"Received message: {msg.value.decode('utf-8')}")
    finally:
        await consumer.stop()

def main():
    st.title("Kafka Consumer with Streamlit")
    st.write("Waiting for messages...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(consume())

if __name__ == "__main__":
    main()



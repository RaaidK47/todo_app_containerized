import asyncio
from aiokafka import AIOKafkaConsumer
import streamlit as st
import json
import re

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
            msg = msg.value.decode('utf-8')
            data = json.loads(msg)
            data = json.loads(data)  #msg string converted to json

            for key, value in data.items():
                if key == "Info":
                    text = f'<span style="color: blue;">{key}:</span> <span > {value}</span>.'
                    st.markdown(text, unsafe_allow_html=True)

                elif key == "Success":
                    text = f'<span style="color: green;">{key}:</span> <span > {value}</span>.'
                    st.markdown(text, unsafe_allow_html=True)

                elif key == "Error":
                    text = f'<span style="color: red;">{key}:</span> <span > {value}</span>.'
                    st.markdown(text, unsafe_allow_html=True)


    finally:
        await consumer.stop()

def main():
    st.title("Application Logs")
    st.write("Kafka Broker Initiated...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(consume())

if __name__ == "__main__":
    main()



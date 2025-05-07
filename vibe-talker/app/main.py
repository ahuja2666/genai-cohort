from dotenv import load_dotenv
import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from .graph import create_chat_graph
import asyncio
from openai.helpers import LocalAudioPlayer

from openai import AsyncOpenAI

load_dotenv()

openai = AsyncOpenAI()

MONGODB_URI = "mongodb://admin:admin@localhost:27017"
config = {"configurable": {"thread_id": "7"}}
 

def main():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer=checkpointer)
        
        
        r = sr.Recognizer()

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            r.pause_threshold = 2

            while True:
                print("Say something!")
                audio = r.listen(source)

                print("Processing audio...")
                sst = r.recognize_google(audio)

                print("You Said:", sst)
                for event in graph.stream({ "messages": [{"role": "user", "content": sst}] }, config, stream_mode="values"):
                    if "messages" in event:
                            event["messages"][-1].pretty_print()


async def speak(text: str):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

main()

# if __name__ == "__main__":
#      asyncio.run(speak(text="This is a sample voice. Hi Piyush"))
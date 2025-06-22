from agents import Runner, Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runconfig
from openai.types.responses import ResponseTextDeltaEvent
import os 
from dotenv import load_dotenv
import chainlit as cl

load_dotenv()

gemini_api_key= os.getenv("GEMINI_API_KEY")

# step 01
external_client= AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# step 02
model= OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# step 03
config= Runconfig(
    model=model,
    model_provider=external_client,
    Tracing_disabled=True
)
# step 04
agent= Agent(
    name="python expert",
    instructions="you are a python Programmer...."
)

# step 05
@cl.on_chat_start
async def handle_start():
    cl.user_session.set("history",[])
    await cl.Message(content="Hello, How can I help you today?").send()

# step 06
@cl.on_message
async def handle_message(message : cl.Message):
    history= cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

# step 07
    msg= cl.message(content="")
    await msg.send()

    result= Runner.run_streamed(
        agent,
        input=history,
        run_config=config
    )
    # step 08
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.dalta)

# step 09
    history.append({"role":"assistant", "content": result.final_output})
    history= cl.user_session.set("history", history)
    # await cl.Message(content=result.final_output).send()

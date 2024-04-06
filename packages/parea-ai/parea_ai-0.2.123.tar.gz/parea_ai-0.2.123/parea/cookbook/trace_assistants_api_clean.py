import os
import time

import openai
from dotenv import load_dotenv
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import ThreadMessage
from pydantic import BaseModel

from parea import Parea, trace

load_dotenv()

p = Parea(api_key=os.getenv("PAREA_API_KEY"))


# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI()
p.wrap_openai_client(client)


class DataObj(BaseModel):
    instructions: str
    content: str


set_up = DataObj(
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
)


@trace
def sub_func(set_up: DataObj) -> tuple[Assistant, Thread, ThreadMessage]:
    assistant = client.beta.assistants.create(
        name="Math Tutor",
        instructions=set_up.instructions,
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-1106-preview",
    )

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=set_up.content,
    )
    return assistant, thread, message


@trace
def new_main(instructions: str, set_up: DataObj) -> ThreadMessage:
    assistant, thread, message = sub_func(set_up)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=instructions,
    )

    print("checking assistant status. ")
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            print("done!")
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            print("messages: ")
            for message in messages:
                assert message.content[0].type == "text"
                print({"role": message.role, "message": message.content[0].text.value})

            client.beta.assistants.delete(assistant.id)
            return messages
        else:
            print("in progress...")
            time.sleep(5)


if __name__ == "__main__":
    new_main(
        "Please address the user as Jane Doe. The user has a premium account.",
        set_up,
    )

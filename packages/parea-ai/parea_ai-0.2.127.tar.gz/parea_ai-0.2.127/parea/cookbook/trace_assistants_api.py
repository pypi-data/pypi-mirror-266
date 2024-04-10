import asyncio
import json
import os
import time

import openai
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import ThreadMessage
from pydantic import BaseModel

from parea import Parea, trace
from parea.evals import call_openai
from parea.schemas import Log

load_dotenv()

p = Parea(api_key=os.getenv("PAREA_API_KEY"))


# def friendliness(log: Log) -> float:
#     output = log.output
#     response = call_openai(
#         [
#             {
#                 "role": "system",
#                 "content": "You evaluate the friendliness of the following response on a scale of 0 to 10. You must only return a number.",
#             },
#             {"role": "assistant", "content": output},
#         ],
#         model="gpt-4",
#     )
#     try:
#         return float(response) / 10.0
#     except TypeError:
#         return 0.0


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
    # client2 = AsyncOpenAI()
    # p.wrap_openai_client(client2)

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


# @trace
# def init():
#     assistant = client.beta.assistants.create(
#         name="Math Tutor",
#         instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
#         model="gpt-4-1106-preview",
#     )
#     MATH_ASSISTANT_ID = assistant.id  # or a hard-coded ID like "asst-..."
#     assistant = client.beta.assistants.update(
#         MATH_ASSISTANT_ID,
#         tools=[
#             {"type": "code_interpreter"},
#             {"type": "retrieval"},
#             {"type": "function", "function": function_json},
#         ],
#     )
#     return MATH_ASSISTANT_ID, assistant
#
#
# @trace
# def submit_message(assistant_id, thread, user_message):
#     client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)
#     return client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant_id,
#     )
#
#
# @trace
# def create_thread_and_run(user_input, MATH_ASSISTANT_ID):
#     thread = client.beta.threads.create()
#     run = submit_message(MATH_ASSISTANT_ID, thread, user_input)
#     return thread, run
#
#
# def pretty_print(messages):
#     print("# Messages")
#     for m in messages:
#         print(f"{m.role}: {m.content[0].text.value}")
#     print()
#
#
# @trace
# def wait_on_run(run, thread):
#     while run.status == "queued" or run.status == "in_progress":
#         run = client.beta.threads.runs.retrieve(
#             thread_id=thread.id,
#             run_id=run.id,
#         )
#         time.sleep(0.5)
#     return run
#
#
# def get_mock_response_from_user_multiple_choice():
#     return "a"
#
#
# def get_mock_response_from_user_free_response():
#     return "I don't know."


# def display_quiz(title, questions):
#     print("Quiz:", title)
#     print()
#     responses = []
#
#     for q in questions:
#         print(q["question_text"])
#         response = ""
#
#         # If multiple choice, print options
#         if q["question_type"] == "MULTIPLE_CHOICE":
#             for i, choice in enumerate(q["choices"]):
#                 print(f"{i}. {choice}")
#             response = get_mock_response_from_user_multiple_choice()
#
#         # Otherwise, just get response
#         elif q["question_type"] == "FREE_RESPONSE":
#             response = get_mock_response_from_user_free_response()
#
#         responses.append(response)
#         print()
#
#     return responses
#
#
# responses = display_quiz(
#     "Sample Quiz",
#     [
#         {"question_text": "What is your name?", "question_type": "FREE_RESPONSE"},
#         {
#             "question_text": "What is your favorite color?",
#             "question_type": "MULTIPLE_CHOICE",
#             "choices": ["Red", "Blue", "Green", "Yellow"],
#         },
#     ],
# )
# # print("Responses:", responses)

function_json = {
    "name": "display_quiz",
    "description": "Displays a quiz to the student, and returns the student's response. A single quiz can have multiple questions.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "questions": {
                "type": "array",
                "description": "An array of questions, each with a title and potentially options (if multiple choice).",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "question_type": {
                            "type": "string",
                            "enum": ["MULTIPLE_CHOICE", "FREE_RESPONSE"],
                        },
                        "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["question_text"],
                },
            },
        },
        "required": ["title", "questions"],
    },
}


# @trace
# def get_response(thread):
#     return client.beta.threads.messages.list(thread_id=thread.id, order="asc")
#
#
# @trace
# def main2():
#     MATH_ASSISTANT_ID, assistant = init()
#     thread, run = create_thread_and_run("Make a quiz with 2 questions: One open ended, one multiple choice. Then, give me feedback for the responses.", MATH_ASSISTANT_ID)
#     run = wait_on_run(run, thread)
#     print(run.status)
#     tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
#     name = tool_call.function.name
#     arguments = json.loads(tool_call.function.arguments)
#
#     print("Function Name:", name)
#     print("Function Arguments:", arguments)
#
#     responses = display_quiz(arguments["title"], arguments["questions"])
#     print("Responses:", responses)
#     run = client.beta.threads.runs.submit_tool_outputs(
#         thread_id=thread.id,
#         run_id=run.id,
#         tool_outputs=[
#             {
#                 "tool_call_id": tool_call.id,
#                 "output": json.dumps(responses),
#             }
#         ],
#     )
#     run = wait_on_run(run, thread)
#     o = get_response(thread)
#     pretty_print(o)
#     return o
#
#
# @trace
# async def assistant_test():
#     # client = AsyncOpenAI()
#     # p.wrap_openai_client(client)
#
#     assistant = await client.beta.assistants.create(
#         name="Math Tutor",
#         instructions="You are a personal math tutor. Write and run code to answer math questions.",
#         tools=[{"type": "code_interpreter"}],
#         model="gpt-4-1106-preview",
#     )
#
#     thread = await client.beta.threads.create()
#
#     message = await client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
#     )
#     return assistant, thread, message
#
#
# async def create_assistant() -> Assistant:
#     client = AsyncOpenAI()
#     p.wrap_openai_client(client)
#     return await client.beta.assistants.create(
#         name="Math Tutor",
#         instructions="You are a personal math tutor. Write and run code to answer math questions.",
#         tools=[{"type": "code_interpreter"}],
#         model="gpt-4-1106-preview",
#     )


if __name__ == "__main__":
    # print(asyncio.run(create_assistant()))
    new_main(
        "Please address the user as Jane Doe. The user has a premium account.",
        set_up,
    )

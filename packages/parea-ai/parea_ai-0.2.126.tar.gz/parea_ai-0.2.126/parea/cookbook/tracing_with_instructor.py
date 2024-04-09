from typing import Iterable

import asyncio
import inspect
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

# import openai
from pydantic import BaseModel


def print_levels(func):
    level = 0
    print(f"{level}th level: {inspect.iscoroutinefunction(func)}")
    while hasattr(func, "__wrapped__"):
        level += 1
        func = func.__wrapped__
        print(f"{level}th level: {inspect.iscoroutinefunction(func)}")


client = OpenAI()
print("Before patching")
print_levels(client.chat.completions.create)

from parea import Parea

# load_dotenv()

p = Parea(api_key=os.getenv("PAREA_API_KEY"), project_name="testing")
p.wrap_openai_client(client)
print("patched with parea")
# print_levels(client.chat.completions.create)


import instructor

client2 = instructor.patch(client, mode=instructor.Mode.TOOLS)
# print(inspect.iscoroutine(client.chat.completions.create))
print("patched with instructor")
# print_levels(client.chat.completions.create)


class UserExtract(BaseModel):
    name: str
    age: int


async def print_iterable_results():
    # model = await openai.ChatCompletion.acreate(
    #     model="gpt-4",
    #     # response_model=Iterable[UserExtract],
    #     # max_retries=2,
    #     stream=True,
    #     messages=[
    #         {"role": "user", "content": "Make two up people"},
    #     ],
    # )
    model = client.chat.completions.create(
        model="gpt-4",
        response_model=Iterable[UserExtract],
        max_retries=2,
        stream=True,
        messages=[
            {"role": "user", "content": "Make two up people"},
        ],
    )
    print(type(model))
    for m in model:
        print(m)
        # > name='John Smith' age=30
        # > name='Mary Jane' age=28


if __name__ == "__main__":
    asyncio.run(print_iterable_results())

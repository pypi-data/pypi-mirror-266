import asyncio
import os
import time

from anthropic import AsyncAnthropic

from parea import Parea, trace, trace_insert


class AnthropicActionStrategy:
    @classmethod
    def get_client(cls) -> AsyncAnthropic:
        p_api_key = os.getenv("PAREA_API_KEY", "")
        p = Parea(p_api_key)

        anthropic_client = AsyncAnthropic()

        p.wrap_anthropic_client(anthropic_client)
        return anthropic_client


class SomeClass:
    @classmethod
    @trace
    async def some_fn(cls, val: str):
        async with AnthropicActionStrategy.get_client() as client:
            start = time.time()
            resp = await client.messages.create(
                max_tokens=4096,
                model="claude-3-opus-20240229",
                temperature=0.0,
                system="claude",
                messages=[{"role": "user", "content": val}],
            )
            end = time.time()
        print(f"Time taken: {end - start}")
        trace_insert({"metadata": {"time_taken": end - start}})
        return resp.content[0].text


if __name__ == "__main__":
    asyncio.run(SomeClass.some_fn("Hello, Claude"))

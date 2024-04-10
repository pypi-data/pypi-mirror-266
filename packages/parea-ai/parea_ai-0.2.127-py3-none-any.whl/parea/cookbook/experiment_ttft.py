import os

from dotenv import load_dotenv
from openai import OpenAI

from parea import Parea, trace
from parea.cookbook.data.openai_input_examples import long_example_json, medium_example_json, simple_example_json
from parea.schemas import Log, TraceLog
from parea.utils.trace_utils import trace_data

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

p = Parea(api_key=os.getenv("PAREA_API_KEY"), project_name="ttft")
p.wrap_openai_client(client)


def find_child(trace_id: str) -> TraceLog:
    traces = trace_data.get()
    parent_trace = traces[trace_id]
    for _trace_id, _trace in traces.items():
        if _trace_id != trace_id and traces[_trace_id].parent_trace_id == parent_trace.trace_id:
            return traces[_trace_id]


def ttft(log: Log) -> float:
    return find_child(log.trace_id).time_to_first_token


@trace(eval_funcs=[ttft])
def call_openai_stream(data: dict):
    data["stream"] = True
    stream = client.chat.completions.create(**data)
    for _ in stream:
        pass


data = [
    {"name": "25-input-tokens_gpt-35-turbo-0125", "data": simple_example_json},
    {"name": "1000-input-tokens_gpt-35-turbo-0125", "data": medium_example_json},
    {"name": "5000-input-tokens_gpt-35-turbo-0125", "data": long_example_json},
]


if __name__ == "__main__":
    for d in data:
        p.experiment(
            data=[{"data": d["data"]}] * 10,
            func=call_openai_stream,
            n_workers=1,
        ).run(name=d["name"])

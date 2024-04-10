from typing import Tuple

import json
import os
from datetime import datetime

from attrs import asdict
from dotenv import load_dotenv

from parea import Parea, get_current_trace_id, trace
from parea.schemas import Completion, CompletionResponse, FeedbackRequest

load_dotenv()

p = Parea(api_key=os.getenv("PAREA_API_KEY"), project_name="tweets-analysis")


def deployed_argument_generator(tweet: str) -> str:
    return p.completion(
        Completion(
            deployment_id="p-joWOg0Xdj2I0hafg-x83N",
            llm_inputs={
                "tweet": tweet,
            },
        )
    ).content


deployed_argument_generator("Information Interesting for NVIDIA = via ARM. nvidianews. nvidia. About com / exclusive news / nvidia - to …")
deployed_argument_generator("I love the new iPhone 13 Pro Max. It's the best phone I've ever had. I can't wait to get my hands on it. #iPhone13ProMax")

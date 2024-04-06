import os
import uuid

from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader

from parea import Parea, trace
from parea.evals.general import answer_matches_target_llm_grader_factory
from parea.schemas import Completion, LLMInputs, Message, ModelParams, Role

load_dotenv()

p = Parea(api_key=os.getenv("PAREA_API_KEY"), project_name="pg-essay")


def call_llm(content: str, model: str) -> str:
    return p.completion(
        data=Completion(
            llm_configuration=LLMInputs(
                model=model,
                model_params=ModelParams(temp=0.0),
                messages=[Message(role=Role.user, content=content)],
            )
        )
    ).content


paul_graham_essay = SimpleDirectoryReader("data/pg-essay").load_data()


def factory(model: str) -> callable:
    @trace
    def summarize_paul_graham_essay(context: str, question: str) -> str:
        content = f"""
        Review the following document:\n{context}
        \nAnswer the following question:{question}
        \n\nResponse:
        """
        return call_llm(content, model)

    return summarize_paul_graham_essay


def run():
    # for model in ["gpt-4-32k-0613", "claude-2.1", "gemini-pro", "gpt-4-0125-preview"]:
    for model in ["gpt-4-0125-preview"]:
        for question in [
            "What company did Paul leave after returning to painting",
            "What seminal event helped Paul Graham realize the potential power of publishing content online, and how did this realization impact his work?",
        ]:
            func = factory(model)
            response = func(context=paul_graham_essay[0].text, question=question)
            print(f"{model} response: {response}")
            print()


if __name__ == "__main__":
    run()

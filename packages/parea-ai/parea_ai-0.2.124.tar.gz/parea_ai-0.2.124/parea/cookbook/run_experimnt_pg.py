import os
import uuid

from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader

from parea import Parea, trace
from parea.evals.general import answer_matches_target_llm_grader_factory
from parea.schemas import Completion, LLMInputs, Message, ModelParams, Role

load_dotenv()

p = Parea(api_key=os.getenv("PAREA_API_KEY"), project_name="pg-essay")


def make_expr_name(name: str) -> str:
    # remove spaces, special characters, periods and make lowercase
    clean_name = name.replace(" ", "-").replace(".", "-").lower()
    return f"{clean_name}-{str(uuid.uuid4())[:2]}"


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
matches_target = answer_matches_target_llm_grader_factory(model="gpt-4-32k-0613")


def factory(model: str) -> callable:
    @trace(eval_funcs=[matches_target])
    def summarize_paul_graham_essay(context: str, question: str) -> str:
        content = f"""
        Review the following document:\n{context}
        \nAnswer the following question:{question}
        \n\nResponse:
        """
        return call_llm(content, model)

    return summarize_paul_graham_essay


def run():
    for model in ["gpt-4-32k-0613", "claude-2.1", "gemini-pro"]:
        e = p.experiment(
            data=[
                {
                    "context": paul_graham_essay[0].text,
                    "question": "What company did Paul leave after returning to painting?",
                    "target": "Yahoo",
                },
                {
                    "context": paul_graham_essay[0].text,
                    "question": "What seminal event helped Paul Graham realize the potential power of publishing content online, and how did this realization impact his work?",
                    "target": "When Paul Graham posted a postscript file of his talk on Lisp online and it received 30,000 page views in one day after being shared on Slashdot. This unexpected event helped Graham realize the power of online publishing, leading him to understand that the internet allowed for a broader dissemination of essays than traditional publishing ever could. This realization significantly influenced his work, as he decided there would be a new generation of essays that could be published online, directly to a wide audience, and he committed himself to writing them.",
                },
            ],
            func=factory(model),
        )
        e.run(name=make_expr_name(model))
        print(e.avg_scores)
        assert all(score > 0.5 for score in e.avg_scores.values()), "Some scores are below 0.5"


if __name__ == "__main__":
    run()

from objects.question import Question
from pandas import DataFrame


def get_prompt_template(question: Question, context: DataFrame) -> str:
    formatted_context = ", ".join(
        f"{row['url']}: {row['text']}" for _, row in context.iterrows()
    )
    return f"""
        Follow these steps exactly:
        1. Read this question as an experienced graph data scientist at Neo4j: {question.question}
        2. Read and summarize the following context documents, ignoring any that do not relate to the user question:
                {formatted_context}
        3. Use this context and your knowledge to answer the user question.
        4. Return your answer with sources.
    """


def get_prompt_no_context_template(question: Question) -> str:
    return f"""
        Follow these steps exactly:
        1. Read this question as an experienced graph data scientist at Neo4j: {question.question}
        2. Use your knowledge to answer the user question.
        3. Return your answer with sources if possible.
    """


def get_prompt_no_context() -> str:
    return """
        Follow these steps exactly:
        1. Read this question as an experienced graph data scientist at Neo4j:
        2. Use your knowledge to answer the user question.
        3. Return your answer with sources if possible.
    """

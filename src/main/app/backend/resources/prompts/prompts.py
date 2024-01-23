prompt_template = """
                    Follow these steps exactly:
                    1. Read this question as an experienced graph data scientist at Neo4j: {question} 
                    2. Read and summarize the following context documents, ignoring any that do not relate to the user question: {context}
                    3. Use this context and your knowledge to answer the user question.
                    4. Return your answer with sources.
                              """

prompt_no_context_template = """
                    Follow these steps exactly:
                    1. Read this question as an experienced graph data scientist at Neo4j: {question} 
                    2. Use your knowledge to answer the user question.
                    3. Return your answer with sources if possible.
                              """
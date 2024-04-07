from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import StrOutputParser
from trulens_eval import TruChain, Tru
from trulens_eval.app import App
from trulens_eval.feedback import Feedback, Groundedness
from trulens_eval.feedback.provider import OpenAI
from langchain_community.vectorstores import Chroma
import numpy as np


class TruLensEvaluator:
    def __init__(self):
        pass

    
    def format_docs(docs):
        """
        Formats a list of Documents into a single string, concatenating the page_content of each Document.

        Args:
            docs (List[Document]): The list of Documents to format.

        Returns:
            str: The concatenated page_content of the Documents.
        """
        try:
            return "\n\n".join(doc.page_content for doc in docs)
        except Exception as e:
            print(f"Error in format_docs: {e}")
            return ""

    
    def get_rag_chain(evaluation_question, retriever):
        """
        Returns a Retrieval-Augmented Generation (RAG) chain that can be used to evaluate a code assistant on a set of questions.

        Args:
            evaluation_question (str): The question to evaluate the code assistant on.
            retriever (SelfQueryRetriever): A retriever that can be used to retrieve relevant documents from a vector store.

        Returns:
            LLMChain: A RAG chain that can be used to evaluate the code assistant.
        """
        try:
            template = """You are an expert in browsing through documents and generating the best possible response from the given context.
                    If the relevant information is not available in the given document, then you can respond with 'I do not have information for your query'.
                    Draft the response in simple and short sentences.
                    
                    Question: {question}
                    Document: {context}
                    Response:"""
            prompt = PromptTemplate(
                input_variables=["question", "context"],
                template=template,
            )
            llm = ChatOpenAI()

            rag_chain = (
                {"context": retriever | TruLensEvaluator.format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            return rag_chain
        except Exception as e:
            print(f"Error in get_rag_chain: {e}")
            return None

   
    def trulens_evaluation(evaluation_questions, vectorstore, chunking_type):
        """
        Evaluate a response using the TruLens framework.

        Args:
            evaluation_questions (List[str]): A list of questions to evaluate the code assistant on.
            vectorstore (Chroma): A vector store containing documents and their embeddings.
            chunking_type (str): The type of code chunking to evaluate, e.g., "SimpleTextSplitter".

        Returns:
            Dict[str, Any]: A dictionary containing the evaluation results.
        """
        try:
            tru = Tru()
            tru.reset_database()

            for question in evaluation_questions:
                retriever = vectorstore.as_retriever()
                rag_chain = TruLensEvaluator.get_rag_chain(question, retriever)
                # Initialize provider class
                provider = OpenAI()
                context = App.select_context(rag_chain)

                grounded = Groundedness(groundedness_provider=OpenAI())
                f_groundedness = (
                    Feedback(grounded.groundedness_measure_with_cot_reasons, name="Groundedness")
                    .on(context.collect())
                    .on_output()
                    .aggregate(grounded.grounded_statements_aggregator)
                )

                f_answer_relevance = (
                    Feedback(provider.relevance, name="Answer Relevance")
                    .on_input_output()
                )

                f_context_relevance = (
                    Feedback(provider.context_relevance, name="Context Relevance")
                    .on_input()
                    .on(context)
                    .aggregate(np.mean)
                )

                tru_recorder = TruChain(rag_chain,
                                        app_id=chunking_type,
                                        feedbacks=[f_answer_relevance, f_context_relevance, f_groundedness])

                with tru_recorder as recording:
                    response = rag_chain.invoke(question)

            rec = recording.get()
            for feedback, feedback_result in rec.wait_for_feedback_results().items():
                pass

            records, feedback = tru.get_records_and_feedback(app_ids=[chunking_type])
            return records
        except Exception as e:
            print(f"Error in trulens_evaluation: {e}")
            return {}


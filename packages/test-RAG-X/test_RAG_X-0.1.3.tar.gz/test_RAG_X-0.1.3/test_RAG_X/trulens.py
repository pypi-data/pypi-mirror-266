

# Imports main tools:
from trulens_eval import TruChain, Tru
# Imports from langchain to build app
import bs4
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.schema import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain


from trulens_eval.feedback.provider import OpenAI
from trulens_eval import Feedback
import numpy as np
from langchain.retrievers.self_query.base import SelfQueryRetriever


def format_docs(docs):
        """
        Formats a list of Documents into a single string, concatenating the page_content of each Document.

        Args:
            docs (List[Document]): The list of Documents to format.

        Returns:
            str: The concatenated page_content of the Documents.
        """
        # print("\n\nAbout docs:\n",type(docs), 'type doc')
        # print(docs)
        # print("\n\n\n")
        return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain(evaluation_question, retriever):
    """
    Returns a Retrieval-Augmented Generation (RAG) chain that can be used to evaluate a code assistant on a set of questions.

    Args:
        evaluation_question (str): The question to evaluate the code assistant on.
        retriever (SelfQueryRetriever): A retriever that can be used to retrieve relevant documents from a vector store.

    Returns:
        LLMChain: A RAG chain that can be used to evaluate the code assistant.
    """
    template = """You are an expert in browsing through document and generate best possible response from the given document.
            If the relevant information is not available in the given document, then you can 'I do now have information for your query'.
            Draft the response in a simple and short sentences.
            
            Question: {question}
            Document: {context}
            Response:"""
    prompt = PromptTemplate(
        input_variables = ["question","context"],
        template=template,
    )
    # llm=OpenAI()
    llm = ChatOpenAI()

    
    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    # rag_chain = LLMChain(llm=ChatOpenAI(model='gpt-3.5-turbo',temperature=0.2), prompt=prompt)
    return rag_chain

from trulens_eval.app import App
def trulens_evaluation(evalation_questions, vectorstore, chunking_type):
    """
    Evaluate a response using the TruLens framework.

    Args:
        evalation_questions (List[str]): A list of questions to evaluate the code assistant on.
        vectorstore (Chroma): A vector store containing documents and their embeddings.
        chunking_type (str): The type of code chunking to evaluate, e.g. "SimpleTextSplitter".

    Returns:
        Dict[str, Any]: A dictionary containing the evaluation results.
    """
    tru = Tru()
    tru.reset_database()

    for question in evalation_questions:
        # docs = vectorstore.similarity_search(question)
        # print(len(docs) , 'relevant doc found')
        
        retriever = vectorstore.as_retriever()
        
        rag_chain = get_rag_chain(question, retriever)


        # Initialize provider class
        provider = OpenAI()

        # select context to be used in feedback. the location of context is app specific.
        
        context = App.select_context(rag_chain)
        # context = ["\n\n".join(doc.page_content for doc in docs)]

        from trulens_eval.feedback import Groundedness
        grounded = Groundedness(groundedness_provider=OpenAI())
        # Define a groundedness feedback function
        f_groundedness = (
            Feedback(grounded.groundedness_measure_with_cot_reasons, name="Groundedness") # groundedness_measure_with_cot_reasons
            .on(context.collect()) # collect context chunks into a list
            .on_output()
            .aggregate(grounded.grounded_statements_aggregator)
        )

        # Question/answer relevance between overall question and answer.
        f_answer_relevance = (
            Feedback(provider.relevance, name="Answer Relevance")
            .on_input_output()
        )
        # Question/statement relevance between question and each context chunk.
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

            # if want to print response: uncomment below section
            # print(f"Question: {question}\nAnswer: {response}\n\n")
        
    rec = recording.get()
    for feedback, feedback_result in rec.wait_for_feedback_results().items():
        # print(feedback.name, feedback_result.result)
        pass

        
    records, feedback = tru.get_records_and_feedback(app_ids=[chunking_type])
    return records




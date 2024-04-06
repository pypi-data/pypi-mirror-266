
from .chunk_it import Chunker
from .extractor import DocumentExtractor
from .clean_it import TextCleaner
from .get_evaluation_question import GenerateEvaluationQuestions
import pandas as pd

from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from .trulens import *

from dotenv import load_dotenv

load_dotenv()

class parent_class:
    def __init__(self, file_path, **kwargs):
        expected_types = {
                'number_of_questions': int,
                'chunk_size': int, 
                'chunk_overlap': int, 
                'separator': str, 
                'strip_whitespace': bool,
                'sentence_buffer_window': int,
                'sentence_cutoff_percentile': int,
            }

        default_attributes = {
            'number_of_questions': 5,
            'chunk_size': 250, 
            'chunk_overlap': 0, 
            'separator': '', 
            'strip_whitespace': False,
            'sentence_buffer_window': 3,
            'sentence_cutoff_percentile': 80,
        }
            
        default_attributes.update(kwargs)
    
        for key, value in default_attributes.items():
            expected_type = expected_types.get(key)
            if expected_type and not isinstance(value, expected_type):
                raise TypeError(f"{key} must be of type {expected_type.__name__}")
            setattr(self, key, value)

        self.file_path = file_path

        def __str__(self):
            return self.text    




    def get_params(self):
        """
        Returns a dictionary containing the parameters used in the chunking process.

        This function reset all the parameters.
        """
        return {
                'chunk_size': '-', 
                'chunk_overlap': '-', 
                'separator': '-', 
                'strip_whitespace': '-',
                'sentence_buffer_window': '-',
                'sentence_cutoff_percentile': '-',
            }
    

    def eval_function(self, chunks, method_name, eval_questions):
        """
        Evaluate the performance of a chunking method using the TruLens framework.

        Parameters
        ----------
        chunks : list of str
            The list of chunks to evaluate.
        method_name : str
            The name of the chunking method.
        eval_questions : list of str
            The list of evaluation questions.

        Returns
        -------
        float
            The performance score (Padas DataFrame) of the chunking method.

        """
        persist_directory="01_coding/crucible/db"
        embedding_function = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-l6-v2")

        db = Chroma.from_documents(chunks, embedding_function, persist_directory=persist_directory)
        score = trulens_evaluation(evalation_questions = eval_questions, 
                            vectorstore=db, chunking_type=method_name)
        return score

    
    def get_best_param(self):
        """
        This function returns the best parameters for the chunking method based on the evaluation of the performance of the chunking method.

        Returns:
            pandas.DataFrame: The parameters summary for the chunking method based on the evaluation of the performance of the chunking method.
        """
        extractor_instance = DocumentExtractor(file_path=self.file_path)
        uncleaned_text = extractor_instance.extract_data()

        cleaner_instance = TextCleaner(uncleaned_text=uncleaned_text)
        cleaned_text = cleaner_instance.unstructured_text()

        eval_questions = GenerateEvaluationQuestions(document=cleaned_text, number_of_questions=self.number_of_questions).get_evaluation_questions()

        methods_list = [method for method in dir(Chunker)
                if callable(getattr(Chunker, method)) and not method.startswith('__')]
        
        chunk_instance = Chunker(clean_text=cleaned_text, parent_instance=self)

        method_eval_score = []
        for method_name in methods_list:
            print(method_name)
            method = getattr(chunk_instance, method_name, None)  
            if method:
                chunks, params = method()
                
                model_results = self.eval_function(chunks=chunks, method_name=method_name, eval_questions=eval_questions)
                params_df = pd.DataFrame([params])
                repeated_params_df = pd.concat([params_df] * len(model_results), ignore_index=True)

                out = pd.concat([model_results, repeated_params_df], axis=1)
                method_eval_score.append(out)
        

        selected_df_filtered=[]
        param_list = [
            'chunk_size', 
            'chunk_overlap', 
            'separator', 
            'strip_whitespace',
            'sentence_buffer_window',
            'sentence_cutoff_percentile',
        ]
        # Selected columns
        selected_columns = ["app_id","input", "output", "Answer Relevance", "Context Relevance", "Groundedness"]
        selected_columns.extend(param_list)
        for df in method_eval_score:
            selected_df = df[[col for col in selected_columns if col in df.columns]]
            selected_df_filtered.append(selected_df)
        merged_df = pd.concat(selected_df_filtered, ignore_index=True)
        groupby_columns = ['app_id'] + param_list
        grouped_df = merged_df.groupby(groupby_columns)[["Answer Relevance", "Context Relevance", "Groundedness"]].mean().reset_index()
        return grouped_df




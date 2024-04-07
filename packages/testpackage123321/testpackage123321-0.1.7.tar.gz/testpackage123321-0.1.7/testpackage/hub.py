import pandas as pd
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from .tru_lens_evaluator import Chroma, TruLensEvaluator
from .text_chunker import TextChunker
from .document_extractor import DocumentExtractor
from .text_cleaner import TextCleaner
from .evaluation_question_generator import EvaluationQuestionGenerator
from dotenv import load_dotenv
import os

load_dotenv()

class ChunkEvaluator:
    """
    A class containing methods for evaluating chunking methods and determining the best parameters.
    """
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

    def reset_params(self):
        """
        Returns a dictionary containing the default parameters used in the chunking process.
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
        """
        # persist_directory = "01_coding/crucible/db"
        embedding_function = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-l6-v2")

        db = Chroma.from_documents(chunks, embedding_function)
        score = TruLensEvaluator.trulens_evaluation(evaluation_questions=eval_questions, vectorstore=db, chunking_type=method_name)
        return score

    def get_best_param(self):
        """
        Return the best parameters for the chunking method based on the evaluation of its performance.
        """
        extractor_instance = DocumentExtractor(file_path=self.file_path)
        uncleaned_text = extractor_instance.extract_data()

        cleaner_instance = TextCleaner(uncleaned_text=uncleaned_text)
        cleaned_text = cleaner_instance.unstructured_text()

        eval_questions = EvaluationQuestionGenerator(document=cleaned_text, number_of_questions=self.number_of_questions).get_evaluation_questions()

        methods_list = [method for method in dir(TextChunker)
                        if callable(getattr(TextChunker, method)) and not method.startswith('__')]

        chunk_instance = TextChunker(clean_text=cleaned_text, parent_instance=self)

        method_eval_score = []
        for method_name in methods_list:
            method = getattr(chunk_instance, method_name, None)  
            if method:
                print("Executing",method)
                chunks, params = method()
                
                model_results = self.eval_function(chunks=chunks, method_name=method_name, eval_questions=eval_questions)
                params_df = pd.DataFrame([params])
                repeated_params_df = pd.concat([params_df] * len(model_results), ignore_index=True)

                out = pd.concat([model_results, repeated_params_df], axis=1)
                method_eval_score.append(out)
            
        selected_df_filtered = []
        param_list = [
            'chunk_size', 
            'chunk_overlap', 
            'separator', 
            'strip_whitespace',
            'sentence_buffer_window',
            'sentence_cutoff_percentile',
        ]
        selected_columns = ["app_id","input", "output", "Answer Relevance", "Context Relevance", "Groundedness"]
        selected_columns.extend(param_list)
        for df in method_eval_score:
            selected_df = df[[col for col in selected_columns if col in df.columns]]
            selected_df_filtered.append(selected_df)
        merged_df = pd.concat(selected_df_filtered, ignore_index=True)
        groupby_columns = ['app_id'] + param_list
        grouped_df = merged_df.groupby(groupby_columns)[["Answer Relevance", "Context Relevance", "Groundedness"]].mean().reset_index()
        return grouped_df

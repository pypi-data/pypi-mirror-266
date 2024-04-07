from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from .text_utils import *
import re
from langchain.docstore.document import Document


class TextChunker:
    def __init__(self, clean_text: str, parent_instance=None) -> None:
        self.clean_text = clean_text
        self.parent_instance = parent_instance

    def SimpleTextSplitter(self):
        """
        Split the input text into chunks using CharacterTextSplitter.
        Returns a list of chunks and a dictionary containing chunking parameters.
        """
        try:
            params = self.parent_instance.reset_params()
            text_splitter = CharacterTextSplitter(chunk_size=self.parent_instance.chunk_size, 
                                                chunk_overlap=self.parent_instance.chunk_overlap, 
                                                separator=self.parent_instance.separator, 
                                                strip_whitespace=self.parent_instance.strip_whitespace)
            
            split_text = text_splitter.create_documents([self.clean_text])
            
            params['chunk_size'] = self.parent_instance.chunk_size
            params['chunk_overlap'] = self.parent_instance.chunk_overlap
            params['separator'] = self.parent_instance.separator
            params['strip_whitespace'] = self.parent_instance.strip_whitespace
            return split_text, params
        except Exception as e:
            raise "Error occurred during text splitting: {}".format(str(e))

    def RecursiveCharTextSplitter(self):
        """
        Split the input text into chunks using RecursiveCharacterTextSplitter.
        Returns a list of chunks and a dictionary containing chunking parameters.
        """
        try:
            params = self.parent_instance.reset_params()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size = self.parent_instance.chunk_size, chunk_overlap=self.parent_instance.chunk_overlap)
            split_text = text_splitter.create_documents([self.clean_text])
            params['chunk_size'] = self.parent_instance.chunk_size
            params['chunk_overlap'] = self.parent_instance.chunk_overlap
            return split_text, params
        except Exception as e:
            raise "Error occurred during text splitting: {}".format(str(e))

    def SentenseWindowSplitter(self):
        """
        Split the input text into chunks based on the sentence window buffer.
        Returns a list of chunks and a dictionary containing chunking parameters.
        """
        try:
            
            params = self.parent_instance.reset_params()
            input_text = str(self.clean_text)
            single_sentences_list = re.split(r'(?<=[.?!])\s+', input_text)
            sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
            sentences = combine_sentences(sentences, buffer_size=self.parent_instance.sentence_buffer_window)
            chunks=[]
            for i, sentence in enumerate(sentences):
                doc = Document(page_content=sentence['combined_sentence'], metadata={"source": f"chunk:{i}"})
                chunks.append(doc)
            
            params['sentence_buffer_window']=self.parent_instance.sentence_buffer_window
            return chunks, params
        except Exception as e:
            raise "Error occurred during text splitting: {}".format(str(e))

    def SemanticSentenseSplitter(self):
        """
        Split the input text into semantically similar sentences using OpenAI API.
        Returns a list of chunks and a dictionary containing chunking parameters.
        """
        try:
            params = self.parent_instance.reset_params()
            input_text = str(self.clean_text)
            single_sentences_list = re.split(r'(?<=[.?!])\s+', input_text)
            sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
            sentences = combine_sentences(sentences, buffer_size=self.parent_instance.sentence_buffer_window)
            oaiembeds = OpenAIEmbeddings()
            embeddings = oaiembeds.embed_documents([x['combined_sentence'] for x in sentences])
            for i, sentence in enumerate(sentences):
                sentence['combined_sentence_embedding'] = embeddings[i]
            distances, sentences = calculate_cosine_distances(sentences)
            chunks = create_chunk(distances, sentences, cutoff_percentile=self.parent_instance.sentence_cutoff_percentile)
            
            params['sentence_buffer_window']=self.parent_instance.sentence_buffer_window
            params['sentence_cutoff_percentile'] = self.parent_instance.sentence_cutoff_percentile

            return chunks, params
        except Exception as e:
            raise "Error occurred during text splitting: {}".format(str(e))



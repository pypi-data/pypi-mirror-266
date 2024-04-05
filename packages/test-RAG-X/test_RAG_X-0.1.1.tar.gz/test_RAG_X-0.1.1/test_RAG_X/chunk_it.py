from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from .utils import *
import re


# from prag import parent_class

class Chunker:
    def __init__(self, clean_text:str, parent_instance=None) -> None:
        # super().__init__()
        self.clean_text = clean_text
        self.parent_instance=parent_instance

    # Chunking Method: 1
    def SimpleTextSplitter(self):
        """
        This function uses the CharacterTextSplitter from the langchain.text_splitter module to split the input text into chunks.
        The chunking parameters are taken from the parent instance.
        The function returns a list of chunks and a dictionary containing the chunking parameters.
        """
        params = self.parent_instance.get_params()
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


    # Chunking Method: 2
    def RecursiveCharTextSplitter(self):
        """
        This function uses the RecursiveCharacterTextSplitter from the langchain.text_splitter module to split the input text into chunks.
        The chunking parameters are taken from the parent instance.
        The function returns a list of chunks and a dictionary containing the chunking parameters.
        """
        params = self.parent_instance.get_params()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = self.parent_instance.chunk_size, chunk_overlap=self.parent_instance.chunk_overlap)
        split_text = text_splitter.create_documents([self.clean_text])
        params['chunk_size'] = self.parent_instance.chunk_size
        params['chunk_overlap'] = self.parent_instance.chunk_overlap
        
        return split_text, params

    # Chunking Method: 3
    def SentenseWindowSplitter(self):
        """
        This function takes the input text and splits it into chunks based on the sentence window buffer.
        The chunking parameters are taken from the parent instance.
        The function returns a list of chunks and a dictionary containing the chunking parameters.
        """
        params = self.parent_instance.get_params()
        input_text = str(self.clean_text)
        single_sentences_list = re.split(r'(?<=[.?!])\s+', input_text)
        sentences = [{'sentence': x, 'index' : i} for i, x in enumerate(single_sentences_list)]
        sentences = combine_sentences(sentences, buffer_size=self.parent_instance.sentence_buffer_window)
        chunks=[]
        for i, sentence in enumerate(sentences):
          doc = Document(page_content=sentence['combined_sentence'], metadata={"source": f"chunk:{i}"})
          chunks.append(doc)


        params['sentence_buffer_window']=self.parent_instance.sentence_buffer_window
        return chunks, params

    # Chunking Method: 4
    def SemanticSentenseSplitter(self):
      """
      This function takes the input text and splits it into semantically similar sentences using the OpenAI API.
      The chunking parameters are taken from the parent instance.
      The function returns a list of chunks and a dictionary containing the chunking parameters.
      """
      params = self.parent_instance.get_params()
      input_text = str(self.clean_text)
      single_sentences_list = re.split(r'(?<=[.?!])\s+', input_text)
      sentences = [{'sentence': x, 'index' : i} for i, x in enumerate(single_sentences_list)]
      sentences = combine_sentences(sentences, buffer_size=self.parent_instance.sentence_buffer_window)
      oaiembeds = OpenAIEmbeddings()
      embeddings = oaiembeds.embed_documents([x['combined_sentence'] for x in sentences])
      for i, sentence in enumerate(sentences):
        sentence['combined_sentence_embedding'] = embeddings[i]
      distances, sentences = calculate_cosine_distances(sentences)
      chunks=create_chunk(distances, sentences, cutoff_percentile=self.parent_instance.sentence_cutoff_percentile)

      params['sentence_buffer_window']=self.parent_instance.sentence_buffer_window
      params['sentence_cutoff_percentile'] = self.parent_instance.sentence_cutoff_percentile

      return chunks, params
    




import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings


# class TextUtils:
    
def combine_sentences(sentences, buffer_size=1):
    try:
        for i in range(len(sentences)):
            combined_sentence = ''
            for j in range(i - buffer_size, i):
                if j >= 0:
                    combined_sentence += sentences[j]['sentence'] + ' '
            combined_sentence += sentences[i]['sentence']
            for j in range(i + 1, i + 1 + buffer_size):
                if j < len(sentences):
                    combined_sentence += ' ' + sentences[j]['sentence']
            sentences[i]['combined_sentence'] = combined_sentence
        return sentences
    except Exception as e:
        print(f"Error in combine_sentences: {e}")
        return []


def calculate_cosine_distances(sentences):
    try:
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]['combined_sentence_embedding']
            embedding_next = sentences[i + 1]['combined_sentence_embedding']
            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]
            distance = 1 - similarity
            distances.append(distance)
            sentences[i]['distance_to_next'] = distance
        return distances, sentences
    except Exception as e:
        print(f"Error in calculate_cosine_distances: {e}")
        return [], []


def create_chunk(distances, sentences, cutoff_percentile=90):
    try:
        breakpoint_distance_threshold = np.percentile(distances, cutoff_percentile)
        indices_above_thresh = [i for i, x in enumerate(distances) if x > breakpoint_distance_threshold]
        start_index = 0
        chunks = []
        for index in indices_above_thresh:
            end_index = index
            group = sentences[start_index:end_index + 1]
            combined_text = ' '.join([d['sentence'] for d in group])
            chunks.append(combined_text)
            start_index = index + 1
        if start_index < len(sentences):
            combined_text = ' '.join([d['sentence'] for d in sentences[start_index:]])
            chunks.append(combined_text)
        chunks_doc = []
        for i, chunk in enumerate(chunks):
            doc = Document(page_content=chunk, metadata={"source": f"chunk:{i}"})
            chunks_doc.append(doc)
        return chunks_doc
    except Exception as e:
        print(f"Error in create_chunk: {e}")
        return []

    

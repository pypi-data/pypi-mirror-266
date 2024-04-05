import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from langchain.docstore.document import Document


def combine_sentences(sentences, buffer_size=1):
    # Go through each sentence dict
    for i in range(len(sentences)):

        # Create a string that will hold the sentences which are joined
        combined_sentence = ''

        # Add sentences before the current one, based on the buffer size.
        for j in range(i - buffer_size, i):
            # Check if the index j is not negative (to avoid index out of range like on the first one)
            if j >= 0:
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += sentences[j]['sentence'] + ' '

        # Add the current sentence
        combined_sentence += sentences[i]['sentence']

        # Add sentences after the current one, based on the buffer size
        for j in range(i + 1, i + 1 + buffer_size):
            # Check if the index j is within the range of the sentences list
            if j < len(sentences):
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += ' ' + sentences[j]['sentence']

        # Then add the whole thing to your dict
        # Store the combined sentence in the current sentence dict
        sentences[i]['combined_sentence'] = combined_sentence

    return sentences


def calculate_cosine_distances(sentences):
    distances = []
    
    for i in range(len(sentences) - 1):
        embedding_current = sentences[i]['combined_sentence_embedding']
        embedding_next = sentences[i + 1]['combined_sentence_embedding']

        # Calculate cosine similarity
        similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]

        # Convert to cosine distance
        distance = 1 - similarity

        # Append cosine distance to the list
        distances.append(distance)

        # Store distance in the dictionary
        sentences[i]['distance_to_next'] = distance

    # Optionally handle the last sentence
    # sentences[-1]['distance_to_next'] = None  # or a default value

    return distances, sentences



def create_chunk(distances, sentences, cutoff_percentile=90):

    breakpoint_distance_threshold = np.percentile(distances, cutoff_percentile) # If you want more chunks, lower the percentile cutoff

    # Then we'll get the index of the distances that are above the threshold. This will tell us where we should split our text
    indices_above_thresh = [i for i, x in enumerate(distances) if x > breakpoint_distance_threshold] # The indices of those breakpoints on your list

    # Initialize the start index
    start_index = 0

    # Create a list to hold the grouped sentences
    chunks = []

    # Iterate through the breakpoints to slice the sentences
    for index in indices_above_thresh:
        # The end index is the current breakpoint
        end_index = index

        # Slice the sentence_dicts from the current start index to the end index
        group = sentences[start_index:end_index + 1]
        combined_text = ' '.join([d['sentence'] for d in group])
        chunks.append(combined_text)

        # Update the start index for the next group
        start_index = index + 1

    # The last group, if any sentences remain
    if start_index < len(sentences):
        combined_text = ' '.join([d['sentence'] for d in sentences[start_index:]])
        chunks.append(combined_text)

    chunks_doc = []
    for i, chunk in enumerate(chunks):
      doc = Document(page_content=chunk, metadata={"source": f"chunk:{i}"})
      chunks_doc.append(doc)

    return chunks_doc




from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings


def create_embeddings(chunks):
  embedding_function = HuggingFaceInferenceAPIEmbeddings(
        api_key=os.environ["HF_TOKEN"], model_name="sentence-transformers/all-MiniLM-l6-v2"
    )
  chunk_embeddings = []

  for chunk in chunks:
    chunk_embed = embedding_function.embed_query(chunk)
    chunk_embeddings.append(chunk_embed)

  return chunk_embeddings



"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
import os
import time
import logging
import numpy as np
from numpy.typing import NDArray
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity 

logger = logging.getLogger("FS")
# os.makedirs("save",exist_ok=True)

COSINE_SIMILARITY_MINVALUE = 0.6
class MrVectorExpert:
    def __init__(self):
        logger.info('MrVectorExpert init...')
        # model: SentenceTransformer model
        self.model = None
        self.isModelLoaded = False
        self.average_contextS_time = None

    def load_model(self)->None:
        logger.info(r"model\\all-MiniLM-L6-v2")

        self.model = SentenceTransformer(r"model\\all-MiniLM-L6-v2")
        self.isModelLoaded = True

        logger.info("all_miniLM model loaded successfully")

    def background_task_step(self)->bool:
        if not self.isModelLoaded:
            self.load_model()
            return True
        return False

    # ---------------- Core Operations ---------------- #

    def convert_tags_to_vector(self, tags:List[str])->Optional[NDArray[np.float32]]:
        """
        Convert a list of tags to a single mean vector.
        Args:
            tags: List of tag strings
        Returns:
            numpy array: Mean vector of all tag embeddings
        """
        if not tags:
            return None
        if self.isModelLoaded:
            # Get embeddings for all tags
            embeddings = self.model.encode(tags)
            # Calculate mean vectors
            mean_vector = np.mean(embeddings, axis=0)

            return mean_vector
        return None
    @staticmethod
    def calculate_cosine_similarity( vector1:np.ndarray, vector2:np.ndarray)->float:
        """
        Calculate cosine similarity between two vectors.
        Args:
            vector1: First vector (numpy array)
            vector2: Second vector (numpy array)
        Returns:
            float: Cosine similarity score (between -1 and 1)
        """
        # Reshape vectors for sklearn
        v1 = vector1.reshape(1, -1)
        v2 = vector2.reshape(1, -1)
        # Calculate cosine similarity
        similarity = cosine_similarity(v1, v2)[0][0]
        return similarity

    def match_tag_sets(self, tags1:List[str], tags2:List[str])->float:
        """
        Compare two sets of tags and return their similarity score.
        Args:
            tags1: First list of tags
            tags2: Second list of tags
        Returns:
            float: Similarity score between the two tag sets
        """
        vector1 = self.convert_tags_to_vector(tags1)
        vector2 = self.convert_tags_to_vector(tags2)

        if vector1 is None or vector2 is None:
            return 0.0

        similarity = MrVectorExpert.calculate_cosine_similarity(vector1, vector2)
        return similarity

        
    # ---------------- Search ---------------- #

    def search_by_vector(self,vector1:np.ndarray,vectors:List[np.ndarray],ids:List[int])->List[int]:
        result:List[int] = []
        ns1 = time.perf_counter_ns()

        for id,vector2 in zip(ids,vectors):
            score = MrVectorExpert.calculate_cosine_similarity(vector1,vector2)
            print(score,"<<<<<<<<<<<<<")
            if score >= COSINE_SIMILARITY_MINVALUE:
                result.append(id)

        ns2 = time.perf_counter_ns()
        self.average_contextS_time = ns2-ns1
        return result

"""
retriever.py
------------
Implements the retrieval half of Retrieval-Augmented Generation (RAG).

For this assignment demo we use scikit-learn's TF-IDF + cosine similarity
as a lightweight, fully offline stand-in for a production vector database
(e.g. FAISS / Chroma / Pinecone with dense embeddings). The interface
(`Retriever.retrieve(query, k)`) is written so it could be swapped for a
real embedding-based vector store without changing any other module.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from knowledge_base import KNOWLEDGE_BASE


class Retriever:
    def __init__(self, documents=None):
        self.documents = documents or KNOWLEDGE_BASE
        self.texts = [d["text"] for d in self.documents]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(self.texts)

    def retrieve(self, query, profile_topics=None, k=3):
        """
        Return the top-k most relevant documents for a query.

        If `profile_topics` (from the user's personalization profile) is
        provided, matching documents are boosted, which is a simple way
        of injecting personalization into retrieval rather than only into
        the final prompt.
        """
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.doc_matrix)[0]

        boosted_scores = []
        for score, doc in zip(scores, self.documents):
            boost = 0.15 if profile_topics and doc["topic"] in profile_topics else 0.0
            boosted_scores.append(score + boost)

        ranked = sorted(
            zip(boosted_scores, self.documents), key=lambda x: x[0], reverse=True
        )
        top_docs = [doc for score, doc in ranked[:k] if score > 0]
        return top_docs

import fitz
import os
import tempfile
import requests
import re
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

class Generator:
    def __init__(self):
        self.generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            tokenizer="google/flan-t5-base"
        )
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    @staticmethod
    def load_pdf(pdf_path, min_chunk_words=150, max_chunk_words=300, overlap_words=50):
        if pdf_path.startswith("http"):
            response = requests.get(pdf_path)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(response.content)
                    tmp_pdf_path = tmp_file.name
            else:
                raise Exception("Failed to download PDF.")
        else:
            tmp_pdf_path = pdf_path
        doc = fitz.open(tmp_pdf_path)
        chunks = []
        metadata = []

        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if not text:
                continue

            sentences = re.split(r'(?<=[.!?])\s+', text)
            current_chunk = []
            current_len = 0

            for sentence in sentences:
                words = sentence.split()
                if not words:
                    continue

                current_chunk.extend(words)
                current_len += len(words)

                if current_len >= max_chunk_words:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(chunk_text)
                    metadata.append({
                        "page": i + 1,
                        "chunk_size": len(current_chunk)
                    })
                    current_chunk = current_chunk[-overlap_words:]
                    current_len = len(current_chunk)

            if min_chunk_words <= current_len < max_chunk_words:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                metadata.append({
                    "page": i + 1,
                    "chunk_size": len(current_chunk)
                })

        doc.close()
        if pdf_path.startswith("http") and os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)

        return chunks, metadata

    def get_best_chunk(self, query, chunks, metadata):
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        chunk_embeddings = self.embedder.encode(chunks, convert_to_tensor=True)
        similarities = util.cos_sim(query_embedding, chunk_embeddings)[0]
        best_idx = int(similarities.argmax())
        best_chunk = chunks[best_idx]
        meta = metadata[best_idx]
        similarity_score = float(similarities[best_idx])
        return best_chunk, meta["page"], similarity_score, meta["chunk_size"]

    def generate(self, query, context, page_number, chunk_size, similarity_score):
        prompt = f"Answer the following question based on the context:\n\nContext: {context}\n\nQuestion: {query}"
        output = self.generator(prompt, max_new_tokens=200)
        answer = output[0]['generated_text']
        return {
            "answer": answer.strip(),
            "source_page": int(page_number),
            "confidence_score": round(similarity_score, 2),
            "chunk_size": chunk_size
        }
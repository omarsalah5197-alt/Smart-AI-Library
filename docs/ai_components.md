<!-- Ctrl + Shift + V عشان نشغل المخطط -->
# Smart AI Library - AI Components

## 1. Smart Semantic Search

### Purpose
Allow students to find books using natural language instead of relying only on exact keyword matching.

### Technology
- Sentence Transformers
- paraphrase-multilingual-MiniLM-L12-v2
- Cosine Similarity

### How It Works
1. Retrieve book information from the database.
2. Combine each book's title, author, category, and description.
3. Convert book information into numerical embeddings.
4. Convert the student's query into an embedding.
5. Calculate cosine similarity between the query and books.
6. Sort books by similarity score.
7. Return the most relevant results above the similarity threshold.

## 2. Book Recommendation System

### Purpose
Recommend books that are similar to a selected book.

### Technology
- TF-IDF Vectorization
- Cosine Similarity

### How It Works
1. Collect book information.
2. Convert book text into TF-IDF vectors.
3. Compare the selected book with other books.
4. Calculate similarity scores.
5. Exclude the selected book.
6. Sort recommendations by similarity.
7. Return the top three recommendations.

## 3. Smart Assistant

### Purpose
Understand student questions and provide useful library-related responses.

### Technology
- Sentence Transformers
- Semantic Intent Detection
- Keyword-Based Intent Detection
- Cosine Similarity

### Supported Intents
- Available Books
- Book Recommendation
- Borrowing Status
- Book Search
- Help
- Unknown

### How It Works
1. Receive the student's question.
2. Detect the question's intent using semantic similarity.
3. Use keyword-based detection when semantic detection returns unknown.
4. Retrieve the relevant information from the database when needed.
5. Generate a response based on the detected intent.
6. Save the conversation in Chat_History.

## 4. AI Technologies Summary

| Component | Main Technique |
|---|---|
| Smart Search | Sentence Embeddings |
| Search Matching | Cosine Similarity |
| Recommendation | TF-IDF |
| Recommendation Matching | Cosine Similarity |
| Smart Assistant | Semantic Intent Detection |
| Fallback Detection | Keyword Matching |

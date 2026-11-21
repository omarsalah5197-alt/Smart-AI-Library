<!-- Ctrl + Shift + V عشان نشغل المخطط -->
# Smart AI Library - System Architecture

## System Architecture Diagram

```mermaid
flowchart TD
    U["Student / Admin"] --> UI["Web Browser"]
    UI --> F["Flask Application"]

    F --> AUTH["Authentication & Session Management"]
    F --> ROUTES["Application Routes"]

    ROUTES --> SEARCH["Smart Semantic Search"]
    ROUTES --> REC["Book Recommendation"]
    ROUTES --> AI["Smart Assistant"]
    ROUTES --> BORROW["Borrowing & Favorites"]
    ROUTES --> ADMIN["Admin Management"]

    SEARCH --> EMB["Sentence Transformer Embeddings"]
    EMB --> COS["Cosine Similarity"]

    REC --> TFIDF["TF-IDF Vectorization"]
    TFIDF --> RCOS["Cosine Similarity"]

    AI --> INTENT["Intent Detection"]
    INTENT --> RESPONSE["Assistant Response"]

    ROUTES --> DB[("MySQL Database")]
    BORROW --> DB
    ADMIN --> DB
    AI --> DB
    SEARCH --> DB
    REC --> DB
```

## Architecture Description

The Smart AI Library system uses Flask as its backend framework. Students and administrators interact with the application through a web browser.

The Flask application handles authentication, application routes, and communication with the MySQL database.

The AI layer contains three main components:

1. Smart Semantic Search.
2. Book Recommendation System.
3. Smart Assistant.

The database stores information about students, books, borrowing records, favorites, and assistant chat history.

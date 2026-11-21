<!-- Ctrl + Shift + V عشان نشغل المخطط -->
# Smart AI Library
## Project Documentation Report

**Project Name:** Smart AI Library  
**Project Type:** Artificial Intelligence Web Application  
**Backend Framework:** Python Flask  
**Database:** MySQL  
**AI Technologies:** Sentence Transformers, TF-IDF, Cosine Similarity

**Student Name:** [Your Name]  
**Department:** Computer Science  
**Course:** Artificial Intelligence  
**Academic Year:** [Academic Year]

---

# 1. Abstract

Smart AI Library is an intelligent web-based library management system designed to improve the way students search for books, discover related content, and manage their borrowing activities.

The system combines traditional library management features with Artificial Intelligence techniques.

It provides semantic book search, content-based book recommendations, and a smart assistant that understands common library-related questions.

The application is developed using Python and Flask, with MySQL as its database management system.

---

# 2. Introduction

Traditional library systems usually depend on exact keyword matching, which may make it difficult for students to find books using natural language.

Students may also need help discovering books related to their interests or checking their borrowing information.

Smart AI Library addresses these challenges by introducing AI-powered features into a web-based library management system.

---

# 3. Problem Statement

Traditional library systems may have the following limitations:

1. Searching for books often depends on exact keywords.
2. Students may struggle to discover books related to their interests.
3. Finding borrowing information can require navigating several pages.
4. Traditional systems may not provide an interactive assistant.

These limitations can make the library experience less efficient and less convenient.

---

# 4. Project Objectives

The main objectives are:

1. Develop a web-based library management system.
2. Implement semantic search to improve book discovery.
3. Build a recommendation system for suggesting similar books.
4. Create a smart assistant for answering library-related questions.
5. Provide student registration and authentication.
6. Allow students to borrow and return books.
7. Provide an administration dashboard for managing books and borrowings.
8. Store application data in a MySQL database.

---

# 5. Proposed Solution

The proposed system integrates Artificial Intelligence with a traditional library management application.

It provides the following main features:

- Student registration and login.
- Book browsing and semantic search.
- Similar book recommendations.
- Smart Assistant.
- Favorites management.
- Book borrowing and returning.
- Borrowing history.
- Administrator dashboard.

---

# 6. System Users

## 6.1 Student

Students can:

- Create an account.
- Log in and log out.
- Browse available books.
- Search for books using natural language.
- View book recommendations.
- Add and remove favorite books.
- Borrow and return books.
- View their borrowing history.
- Interact with the Smart Assistant.

## 6.2 Administrator

Administrators can:

- Access the administration dashboard.
- Add new books.
- Edit existing books.
- Delete books when permitted.
- View borrowing records.
- Manage library information.

---

# 7. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall allow students to register. |
| FR-02 | The system shall authenticate registered students. |
| FR-03 | The system shall display available books. |
| FR-04 | The system shall provide semantic book search. |
| FR-05 | The system shall recommend similar books. |
| FR-06 | The system shall allow students to manage favorites. |
| FR-07 | The system shall allow students to borrow books. |
| FR-08 | The system shall allow students to return borrowed books. |
| FR-09 | The system shall display borrowing history. |
| FR-10 | The system shall provide a Smart Assistant. |
| FR-11 | The administrator shall manage books. |
| FR-12 | The administrator shall view borrowing records. |

---

# 8. Non-Functional Requirements

## Performance
The system should retrieve and display relevant information efficiently.

## Security
- Passwords should be stored as secure password hashes.
- Protected pages should require authentication.
- Administrative pages should require administrator privileges.
- Database credentials and secret keys should not be exposed in source code.

## Usability
The application should provide a simple and understandable user interface.

## Reliability
The application should handle database connection failures and invalid user input appropriately.

## Maintainability
The application should use separate modules for AI functionality, database connections, routes, and tests.

---

# 9. System Architecture

The application consists of the following layers:

1. Presentation Layer: HTML, CSS, and browser interface.
2. Application Layer: Flask routes and business logic.
3. AI Layer: Semantic Search, Recommendation System, and Smart Assistant.
4. Database Layer: MySQL database.

The architecture diagram is documented separately in `architecture.md`.

---

# 10. Artificial Intelligence Components

## 10.1 Smart Semantic Search

### Purpose
Find books based on the meaning of a student's query rather than relying only on exact keyword matching.

### Technologies
- Sentence Transformers.
- Multilingual MiniLM model.
- Cosine Similarity.

### Model
`paraphrase-multilingual-MiniLM-L12-v2`

### Process
1. Retrieve books from the database.
2. Combine title, author, category, and description.
3. Convert book information into numerical embeddings.
4. Convert the search query into an embedding.
5. Calculate cosine similarity.
6. Rank books according to similarity scores.
7. Return relevant results.

The implementation also uses caching to avoid repeatedly calculating embeddings for an unchanged collection of books.

## 10.2 Book Recommendation System

### Purpose
Recommend books that have similar content to a selected book.

### Technologies
- TF-IDF Vectorization.
- Cosine Similarity.

### Process
1. Collect book information.
2. Convert book text into TF-IDF vectors.
3. Compare the selected book with other books.
4. Calculate similarity scores.
5. Exclude the selected book.
6. Rank the remaining books.
7. Return the top three recommendations.

## 10.3 Smart Assistant

### Purpose
Understand common library-related questions and provide appropriate responses.

### Technologies
- Sentence Transformers.
- Semantic Intent Detection.
- Keyword-Based Intent Detection.
- Cosine Similarity.

### Supported Intents

| Intent | Description |
|---|---|
| available_books | Display available books. |
| recommendation | Suggest books. |
| borrowing_status | Retrieve borrowing information. |
| book_search | Search for books. |
| help | Explain assistant capabilities. |
| unknown | Handle unrecognized questions. |

### Process
1. Receive the student's question.
2. Identify its intent using semantic similarity.
3. Use keyword-based detection when semantic detection returns unknown.
4. Retrieve the required information when applicable.
5. Prepare an appropriate response.
6. Save the conversation in the chat history.

---

# 11. Database Design

The system uses MySQL to store and manage application information.

The main database tables are:

| Table | Purpose |
|---|---|
| Students | Stores student accounts and authentication information. |
| Books | Stores book details and available copies. |
| Borrowings | Stores book borrowing and returning records. |
| Favorites | Stores students' favorite books. |
| Chat_History | Stores Smart Assistant conversations. |

The database relationships connect students with their borrowed books, favorite books, and assistant conversations.

---

# 12. Technologies Used

| Technology | Usage |
|---|---|
| Python | Main programming language. |
| Flask | Web application framework. |
| MySQL | Database management system. |
| HTML | Web page structure. |
| CSS | User interface styling. |
| JavaScript | Client-side interactions. |
| Sentence Transformers | Text embeddings and semantic understanding. |
| TF-IDF | Content vectorization. |
| Cosine Similarity | Similarity measurement. |
| Scikit-learn | Machine learning utilities. |
| Pytest | Automated testing. |

---

# 13. Testing

The project uses Pytest to test application functionality.

The testing process includes:

- Authentication tests.
- Database connection tests.
- Book search tests.
- Recommendation tests.
- Smart Assistant tests.
- Borrowing and returning tests.
- Favorites tests.
- Administrator functionality tests.
- Error handling tests.

Mocks are used in several tests to simulate database connections and AI responses without requiring external services.

**Final Testing Results:**

- Total Tests: [Insert latest test count]
- Passed Tests: [Insert passed count]
- Failed Tests: [Insert failed count]
- Overall Coverage: [Insert latest overall coverage]

The final values should be taken from the latest successful test execution.

---

# 14. Limitations

The current system has some limitations:

1. Search quality depends on the quality of book descriptions and metadata.
2. Recommendations depend on the available book information.
3. The Smart Assistant supports predefined library-related intents rather than unrestricted conversational knowledge.
4. The semantic similarity threshold may require tuning.
5. The recommendation system currently focuses on book content rather than learning from student behavior.

---

# 15. Future Improvements

Possible future improvements include:

1. Adding online payment or fine management if required.
2. Improving recommendations using student preferences and borrowing history.
3. Expanding Smart Assistant capabilities.
4. Adding more advanced analytics to the administrator dashboard.
5. Supporting additional languages and more complex queries.
6. Improving deployment, monitoring, and database backup procedures.

---

# 16. Conclusion

Smart AI Library demonstrates how Artificial Intelligence techniques can improve a traditional library management system.

By combining semantic search, content-based recommendations, and an intelligent assistant, the system provides students with improved ways to discover books and manage their library activities.

The project also demonstrates the integration of Python, Flask, MySQL, and machine learning techniques in a practical web application.

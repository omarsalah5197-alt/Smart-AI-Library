from ai.smart_search import semantic_search
from ai.recommendation import get_recommendations
from sentence_transformers import util
from ai.smart_search import model


def detect_intent(query):
    if not query:
        return "unknown"

    query = query.lower().strip()

    # Normalize Arabic text
    query = (
        query.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
    )

    intents = {
        "available_books": [
            "available books",
            "what books are available",
            "show available",
            "books available",
            "الكتب المتاحة",
            "كتب متاحة",
            "المتاح للاستعارة",
            "الكتب الموجودة",
            "الكتب اللي موجودة",
            "الكتب اللي عندكم",
            "ايه الكتب الموجودة",
            "ايه الكتب المتاحة",
            "ايه الكتب اللي عندكم",
            "الكتب المتوفرة",
            "ايه الكتب المتوفرة",
            "كل الكتب",
            "عرض الكتب",
            "في كتب ايه",
            "عايز اشوف الكتب",
        ],
        "recommendation": [
            "recommend",
            "suggest",
            "similar books",
            "recommend me",
            "suggest me",
            "رشحلي",
            "رشح لي",
            "اقترح",
            "اقترحلي",
            "عايز ترشيحات",
            "كتب مشابهة",
        ],
        "borrowing_status": [
            "my borrowings",
            "borrowed books",
            "my loans",
            "استعاراتي",
            "الكتب اللي استعرتها",
            "الكتب المستعارة",
            "حالة الاستعارة",
            "استعرت ايه",
            "الكتب اللي معايا",
        ],
        "book_search": [
            "search",
            "find",
            "looking for",
            "books about",
            "book about",
            "ابحث عن",
            "بدور على",
            "عايز كتاب",
            "عاوز كتاب",
            "عايز كتب",
            "عاوز كتب",
            "كتاب عن",
            "كتب عن",
            "هاتلي كتاب",
        ],
        "help": [
            "help",
            "what can you do",
            "how to use",
            "مساعدة",
            "تقدر تعمل ايه",
            "ازاي استخدم المكتبة",
            "ممكن تساعدني",
        ],
    }

    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in query:
                return intent

    return "unknown"


def semantic_detect_intent(query):

    if not query:
        return "unknown"

    examples = {
        "available_books": [
            "Show me available books",
            "What books do you have?",
            "Show all books in the library",
            "الكتب المتاحة في المكتبة",
            "ايه الكتب الموجودة عندكم",
            "عايز اشوف الكتب الموجودة",
            "ممكن اعرف الكتب المتوفرة",
        ],
        "recommendation": [
            "Recommend books for me",
            "Suggest similar books",
            "I want book recommendations",
            "رشحلي كتب",
            "اقترح عليا كتب",
            "عايز ترشيحات كتب",
            "رشحلي كتاب عن الذكاء الاصطناعي",
        ],
        "borrowing_status": [
            "Show my borrowed books",
            "What books have I borrowed?",
            "Check my borrowing history",
            "ايه الكتب اللي استعرتها",
            "وريني استعاراتي",
            "عايز اعرف الكتب اللي معايا",
        ],
        "book_search": [
            "Find books about Python",
            "Search for artificial intelligence books",
            "I am looking for programming books",
            "عايز كتاب عن البرمجة",
            "ابحث عن كتب الذكاء الاصطناعي",
            "بدور على كتاب عن Python",
        ],
        "help": [
            "What can you do?",
            "Help me use the library",
            "How does this assistant work?",
            "ممكن تساعدني",
            "تقدر تعمل ايه",
            "ازاي استخدم المكتبة",
        ],
    }

    labels = []
    sentences = []

    for intent, questions in examples.items():
        for question in questions:
            labels.append(intent)
            sentences.append(question)

    query_embedding = model.encode(query, convert_to_tensor=True)

    example_embeddings = model.encode(sentences, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, example_embeddings)[0]

    best_index = int(scores.argmax())
    best_score = float(scores[best_index])

    if best_score < 0.40:
        return "unknown"

    return labels[best_index]


def assistant_response(query, books, borrowings=None):

    intent = semantic_detect_intent(query)

    if intent == "unknown":
        intent = detect_intent(query)

    if intent == "book_search":
        results = semantic_search(query, books)

        if not results:
            return {
                "intent": intent,
                "message": "Sorry, I couldn't find matching books.",
                "books": [],
            }

        return {
            "intent": intent,
            "message": "Here are the books I found for you:",
            "books": results,
        }

    elif intent == "recommendation":
        matching_books = semantic_search(query, books, top_k=1)

        if not matching_books:
            return {
                "intent": intent,
                "message": "I couldn't find a suitable book to recommend.",
                "books": [],
            }

        selected_book = matching_books[0]

        results = get_recommendations(selected_book, books, limit=3)

        return {
            "intent": intent,
            "message": "Here are some recommended books:",
            "books": results,
        }

    elif intent == "available_books":

        available = [
            book for book in books if int(book.get("Available_Copies") or 0) > 0
        ]

        return {
            "intent": intent,
            "message": f"Found {len(available)} available books.",
            "books": available,
        }

    elif intent == "borrowing_status":

        borrowings = borrowings or []

        return {
            "intent": intent,
            "message": f"You have {len(borrowings)} borrowing records.",
            "books": borrowings,
        }

    elif intent == "help":

        return {
            "intent": intent,
            "message": (
                "I can help you search for books, "
                "recommend books, find available books, "
                "and check your borrowing records."
            ),
            "books": [],
        }

    return {
        "intent": "unknown",
        "message": (
            "Sorry, I didn't understand your question. "
            "Try asking me about books, recommendations, "
            "available books, or your borrowings."
        ),
        "books": [],
    }

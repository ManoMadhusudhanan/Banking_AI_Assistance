# Chapter 4: Intent Detection
Welcome back, future AI banking experts! In our last chapter,[ Text Preprocessing & Normalization](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%203%3A%20Text%20Preprocessing%20%26%20Normalization.md), we learned how your raw, sometimes messy, banking questions get cleaned up and standardized. This is a crucial step to make sure our AI understands the words you're using.

But once the AI has your clean text, like "what is my account balance", what's the very next logical step? It needs to figure out what you actually want to do! Are you asking about your balance? Trying to apply for a loan? Or perhaps looking for credit card support? This is where **Intent Detection** comes into play.

## What Problem Does it Solve?
Imagine our Banking AI Assistant is like a very smart receptionist at a bank. When you walk in and say something, the receptionist doesn't just hear the words; they immediately try to understand your reason for being there.
- If you say, "I need to check how much money is in my savings account," the receptionist knows your **intent** is "Account Balance Inquiry" and directs you to the self-service portal or a teller.
- If you say, "I want to apply for a new loan," the receptionist understands your **intent** is "Loan Application" and directs you to the loans department.
Without this smart receptionist (our Intent Detection), your clean text would just be a string of words. The AI wouldn't know which part of its "brain" to use, leading to confusion and unhelpful answers.

**Intent Detection** is this "smart receptionist" for our AI. It's responsible for **understanding your goal or topic** from your query, whether it's typed text or even text extracted from an image. It then helps the system decide which "department" or "path" to take to answer you correctly.

## Key Concepts
Let's break down the important ideas behind Intent Detection:

### 1. What is an "Intent"?
In AI, an **intent** is simply the user's **goal or purpose** behind their message. It's what they want to achieve or what topic they are talking about.

For our Banking AI, intents are usually predefined, like:
- Account_Balance_Inquiry
- Loan_Application_Assistance
- Credit_Card_Support
- Transaction_History
- General_Banking_Query
  
### 2. Machine Learning Comparison
How does the AI figure out your intent? It uses **machine learning**. Think of it like this:

1.**Known Examples**: The AI has been "taught" by seeing many examples of questions related to each intent. For instance, it knows that "what's in my account" and "check my funds" are usually `Account_Balance_Inquiry`.
2.**User Query**: When you type "tell me my balance", the AI takes this clean text.
3.**Similarity Check**: It then compares your question with all its known examples for each intent. It's like finding the closest match in a big library of questions. The closer the match, the higher the "score" or "confidence."

### 3. Handling Images
Sometimes, you might upload a picture, like a screenshot of a transaction. Intent Detection needs to work with that too!

- **Text Extraction:** First, our AI uses a tool called **OCR (Optical Character Recognition)** to "read" the text from the image.
- **Intent from Text:** Once the text is extracted, it's treated just like a typed query, and the machine learning comparison process begins.
  
### 4. Confidence Score and Threshold
The AI doesn't just pick an intent; it also gives a **confidence score** (a number, often between 0 and 1) showing how sure it is about its choice.

- **Threshold**: We set a minimum confidence level, called a **threshold**. If the AI's score for its best guess is below this threshold, it might decide it's not confident enough. In such cases, it might return a "General Banking Query" intent or ask for more clarification.
  
## How Intent Detection Helps Our Use Case
Let's use our example query from previous chapters: "What is my account balance?" (after it's been cleaned up to "what is my account balance").

**1. Clean Text Input**: Our Intent Detection system receives the clean text: "what is my account balance".

**2. AI Compares**: It compares this phrase to all the banking intents it knows.

**3. Best Match Found**: It finds a very strong match with the Account_Balance_Inquiry intent.

**4. Result**: It tells the rest of the AI system: "The user's intent is Account_Balance_Inquiry with a high confidence score!"

This allows the [API Gateway & Orchestration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%202%3A%20API%20Gateway%20%26%20Orchestration.md) to direct the request to the correct next step, which might involve looking up your actual account balance.

What if you uploaded an image of a bank statement?

**1. Image Input:** You upload an image.

**2. OCR Extracts Text:** The system uses OCR to read the text from the image, let's say it extracts "Your current balance is $1234.56".

**3. AI Compares:** Intent Detection then processes this extracted text.

**4. Result:** It detects the Account_Balance_Inquiry intent.

## What Happens Under the Hood? (Internal Implementation)
Let's peek behind the curtain to see how Intent Detection works using the `intent_router.py` file.

### The Flow
When the [API Gateway & Orchestration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%202%3A%20API%20Gateway%20%26%20Orchestration.md) needs to figure out your intent, here's how the steps unfold:

<img width="70%" height="615" alt="image" src="https://github.com/user-attachments/assets/774a961b-4f39-4b82-85f0-bd96e9e009b5" />


The **intent_router.py** File
The core logic for intent detection lives in intent_router.py.

**1. Loading the Brain and Known Intents:** Our system first loads a special machine learning model (called `SentenceTransformer`) that can turn sentences into numerical "embeddings" (like turning ideas into coordinates on a map). It also loads our list of predefined intents from `auto_intents.json`.
```
# From intent_router.py
from sentence_transformers import SentenceTransformer, util
import json
from typing import Optional, Tuple

# Load the brain (model) that understands sentence meanings
intent_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load our list of known banking intents from a file
with open("auto_intents.json", "r", encoding="utf-8") as f:
    INTENT_MAP = json.load(f)

# Before we even get a user query, we turn all our known intents into numbers
INTENT_EMBEDDINGS = {
    intent: intent_model.encode(texts, convert_to_tensor=True)
    for intent, texts in INTENT_MAP.items()
}
```

**Explanation:**

- `SentenceTransformer` is our special tool that can convert text into numerical representations (embeddings). Sentences with similar meanings will have similar numerical representations.
- `INTENT_MAP` loads all the example phrases we have for each banking intent (e.g., "what's my balance" for `intent_0`). These example intents are generated using `auto_intent_generator.py` (which processes our banking documents to find common themes and groups them, creating these intent_0, intent_1, etc.).
- `INTENT_EMBEDDINGS` pre-calculates the numerical representations for all our known intents. This makes comparing new user queries much faster!
  
**2. Detecting Intent from Text:** This is the heart of the comparison process. It takes your cleaned query, converts it into numbers, and then finds the closest match among the predefined intent embeddings.
```
# From intent_router.py
def _detect_from_text(text: str, threshold: float) -> Tuple[Optional[str], float]:
    if not text:
        return None, 0.0

    # Turn the user's query into numbers
    query_emb = intent_model.encode(text, convert_to_tensor=True)

    best_intent = None
    best_score = 0.0

    # Compare user's query numbers with all known intent numbers
    for intent, emb in INTENT_EMBEDDINGS.items():
        # 'cos_sim' calculates how similar the numbers are (closer to 1 means more similar)
        score = util.cos_sim(query_emb, emb).max().item()
        if score > best_score:
            best_score = score
            best_intent = intent

    # Only return an intent if the confidence score is high enough
    if best_score < threshold:
        return None, best_score

    return best_intent, best_score
```
**Explanation**:

- `_detect_from_text` is a helper function that does the actual comparison.
- `query_emb = intent_model.encode(text, convert_to_tensor=True)` converts your question ("what is my account balance") into its numerical `query_emb`.
- The code then loops through each of our pre-computed `INTENT_EMBEDDINGS`.
- `util.cos_sim` calculates the **cosine similarity**, which is a way to measure how "similar" two sets of numbers (embeddings) are. A score close to 1 means they are very similar in meaning.
- It keeps track of the `best_intent` (the one with the highest similarity score) and `best_score`.
Finally, it checks if `best_score` meets our `threshold`. If not, it means the AI isn't confident enough, and None is returned for the intent.

**3. The Public** `detect_intent` **Function (Handles Text and Images)**: This is the main function that the [API Gateway & Orchestration calls](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%202%3A%20API%20Gateway%20%26%20Orchestration.md). It acts as a switch, deciding if it needs to process an image first or directly use the text.
```
# From intent_router.py
from ocr_utils import extract_text_from_image # Needed for image processing

def detect_intent(
    query: Optional[str] = None,
    image_path: Optional[str] = None,
    threshold: float = 0.45 # Our minimum confidence level
) -> Tuple[Optional[str], float, str]:

    extracted_text = ""

    # Check if an image was provided
    if image_path:
        print(f"📷 Image received: {image_path}")
        # Use OCR to get text from the image (from ocr_utils.py)
        extracted_text = extract_text_from_image(image_path)
        print(f"📝 OCR extracted text: {extracted_text}")

        # Now detect intent from the extracted text
        intent, score = _detect_from_text(extracted_text, threshold)
        return intent, score, extracted_text

    # If no image, then use the provided text query
    if query:
        intent, score = _detect_from_text(query, threshold)
        return intent, score, query

    # If neither image nor text, return nothing
    return None, 0.0, ""
```
**Explanation**:

- This function can take either a `query` (your typed text) or an `image_path`.
- If `image_path` is present, it first calls `extract_text_from_image()` (from `ocr_utils.py`) to get the text from the picture.
- Then, regardless of whether the text came from typing or an image, it passes that text to the `_detect_from_text`() helper function we just discussed.
- It returns the `intent` (e.g., `intent_0`), the `score` (confidence), and the `text_used` (either your original query or the text extracted from the image).
  
### How `main.py` Uses It
Recall from [API Gateway & Orchestration calls](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%202%3A%20API%20Gateway%20%26%20Orchestration.md), that main.py orchestrates the entire process. It calls `detect_intent` right after text preprocessing:
```
# From main.py (inside the chatbot function)

    # ... (after raw_query becomes normalized_query from Chapter 3) ...

    # This calls our Intent Detection service
    intent, score, detected_text = detect_intent(
        query=normalized_query if normalized_query else None,
        image_path=image_path # Pass the image path if available
    )

    # ... Now, based on 'intent', the API Gateway decides the next step ...
```
**Explanation**: The `normalized_query` (your clean text) and `image_path` (if an image was uploaded) are passed to `detect_intent`. The `intent` and `score` returned are then used by the API Gateway to decide whether to apply [Rule-based Banking Logic](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%205%3A%20Rule-based%20Banking%20Logic.md), engage the [Graph Retrieval Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md), or send to the [Large Language Model (LLM) Integration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md).

## Conclusion
You've now uncovered the crucial role of **Intent Detection** in our Banking AI Assistant! It acts as the intelligent receptionist, understanding the true goal behind your questions or images. By transforming your input into a recognized banking intent (like **Account_Balance_Inquiry**), it efficiently guides the AI system to the right resources and decision-making paths. This ensures you get an accurate and relevant answer every time.

Now that our AI knows what you want to do, what if your request is very specific and simple, like "I want to change my contact number"? Our system has smart, pre-set rules for such cases. Let's explore how these rules work in the next chapter: [Rule-based Banking Logic]([Rule-based Banking Logic](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%205%3A%20Rule-based%20Banking%20Logic.md)).

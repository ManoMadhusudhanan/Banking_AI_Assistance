# Chapter 2: Chatbot API and Orchestration
Welcome to the exciting world of building a Banking AI Assistant! In this first chapter, we'll start with the "brain" of our entire system: the Chatbot API and Orchestration.

Imagine you walk into a big, busy bank. There are many counters: one for opening accounts, another for loans, one for customer service, and so on. Now, imagine a friendly receptionist greeting you at the entrance. Your interaction with this receptionist is like talking to our **Chatbot API**. This receptionist needs to understand what you need and guide you to the correct counter or person. This process of understanding and guiding is what we call **Orchestration**.

## What Problem Does It Solve?
Let's say a user wants to interact with our AI banking assistant. For example, they might type: "What documents do I need to open a savings account?"

This simple question is actually quite complex for a computer! It involves several steps:

1. **Receiving the message**: How does the computer get the user's text?
2. **Understanding the intent**: Is the user asking about accounts, loans, or something else?
3. **Finding the answer**: Where should the system look for information about "documents for savings account"? In a database? By asking a smart AI?
4. **Giving a clear reply** : How does it send the final answer back to the user?
   
The **Chatbot API and Orchestration** is the "central control room" that handles all these steps. It’s like the main conductor of an orchestra, making sure all the different "musicians" (specialized AI modules) play their parts at the right time to create a harmonious and helpful response.

## Key Concepts
Let's break down these two main ideas:

### 1. The Chatbot API (Application Programming Interface)
Think of an API as a "menu" of services that our chatbot offers. When you use an app on your phone, you're interacting with its API without even knowing it! You tap a button, and the app "calls" a specific function (API endpoint) that tells it what to do.

Our chatbot needs a way for users (or other programs) to send messages to it. The API provides specific "doorways" or "endpoints" where requests can enter. For our banking assistant, this means a special address on the internet where users can send their questions and receive answers.

In simple terms, the API is how you **talk to** the chatbot.

### 2. Orchestration
Once the chatbot receives a message through its API, it needs to figure out what to do. This is where **orchestration** comes in.

Imagine the conductor of an orchestra. They don't play all the instruments themselves. Instead, they read the music, understand what's needed, and then direct different sections (violins, flutes, drums) to play their parts at the right moment.

Our chatbot's orchestrator does the same thing:

- It receives the user's request (e.g., text or even an image).
- It analyzes the request to understand its purpose (the "intent").
- It decides which specialized "expert" module to send the request to (e.g., a module to find information, a module to identify text in an image, or a powerful language AI).
- It gathers the results from these modules.
- It combines everything into a single, helpful answer.
- It sends that answer back through the API to the user.
In simple terms, orchestration is how the chatbot **decides what to do** and **manages all its specialized parts**.

## How Our Chatbot Uses API and Orchestration
Let's go back to our example: "What documents do I need to open a savings account?"

1. **User sends message**: You type this question into a chat interface.
2. **API receives request**: Our Banking_AI_Assistance's main API endpoint (/chatbot/ask) gets your message.
3. **Orchestrator takes over**:
- It first performs some initial steps like cleaning up your text (we'll learn more about this in [Text Preprocessing and Normalization](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%203%3A%20Text%20Preprocessing%20%26%20Normalization.md)).
- It then tries to understand what you want using an[ Intent Detection System](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%204%3A%20Intent%20Detection.md). Is it about account opening?
- It might decide that this question requires looking up information from a specific knowledge base, so it sends the question to the [Graph Retrieval-Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md).
- The RAG Engine finds relevant bank documents and returns snippets.
- The orchestrator then combines these snippets with your original question and sends them to a [Large Language Model (LLM)](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md) Service to generate a friendly, clear answer.
- Sometimes, if it's a very specific banking task (like changing your mobile number), the orchestrator might consult [Domain-Specific Banking Policy & Logic](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%205:%20Domain-Specific%20Banking%20Policy%20&%20Logic%20.md) to give you the most accurate and safe advice directly.
4. **API sends reply**: The orchestrator gives the final answer to the API, which then sends it back to you.
You type a simple question, and behind the scenes, a whole chain of smart decisions and actions takes place!

## The Chatbot API in Code
Our `Banking_AI_Assistance` project uses a framework called FastAPI to create its API. `FastAPI` makes it easy to build web "endpoints" that can receive requests and send responses.

Here's how our main API endpoint looks in `main.py`:
```
# main.py
from fastapi import FastAPI, Form, UploadFile, File
import time
# ... (other imports) ...

app = FastAPI()

# ... (other setup like middleware, environment variables) ...

@app.post("/chatbot/ask")
async def chatbot(
    session_id: str = Form(...),
    message: str = Form(""),
    image: UploadFile = File(None)
):
    start_time = time.time()
    image_path = None
    # ... (orchestration logic goes here) ...
```
-` @app.post("/chatbot/ask")`: This line tells FastAPI that when someone sends a "POST" request to the internet address ending with `/chatbot/ask`, the `chatbot` function should be called. "POST" is typically used when you're sending data (like your message) to the server.
- `async def chatbot(...)`: This is our main function that handles all incoming chat requests.
- `session_id: str = Form(...)`: This helps us remember your conversation history.
- `message: str = Form("")`: This is where your typed question comes in.
- `image: UploadFile = File(None)`: This allows users to also upload an image, for example, if they want to ask a question about text within a document.
This small block is the "front door" through which all user requests enter our system.

## The Orchestration in Code: Under the Hood
Let's look at a simplified sequence of what happens inside that `chatbot` function when a request comes in. This is where the orchestrator makes its decisions.

First, the system receives the message and performs some initial processing:
```
# main.py - inside the chatbot function

    # ... (start_time and image_path setup) ...

    # 1. Get raw query and preprocess it
    raw_query = (message or "").strip()
    normalized_query = normalize_text(raw_query) # Cleans and prepares text

    # 2. Detect the user's intent (what they want)
    intent, score, detected_text = detect_intent(
        query=normalized_query if normalized_query else None,
        image_path=image_path
    )
    final_query = normalized_query # Or detected_text if from image
    latency = round(time.time() - start_time, 2)

    # ... (more orchestration logic) ...
```
- `normalize_text(raw_query)`: Before doing anything else, the orchestrator first sends your raw message to a text cleaning service. This step is crucial and will be covered in [Text Preprocessing and Normalization](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%205:%20Domain-Specific%20Banking%20Policy%20&%20Logic%20.md).
- `detect_intent(...)`: The orchestrator then asks the [Intent Detection System](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%204%3A%20Intent%20Detection.md) to figure out the user's goal. For example, is the user asking "how to open an account" or "what is my balance"? This helps the orchestrator route the request correctly.
  
## Orchestration Decision-Making Example: Contact Update Policy
One of the clever things the orchestrator does is handle specific, sensitive banking tasks very carefully. For instance, if you ask to change your mobile number, the bank has strict rules. The orchestrator has a special "policy logic" for this:
```
 main.py - inside the chatbot function

    # ... (previous code) ...

    contact_update_keywords = [
        "change contact number", "update mobile",
        # ... more keywords ...
    ]

    # Check if the query is about updating contact information
    if final_query and any(k in final_query for k in contact_update_keywords):
        # The orchestrator decides to use a specific policy helper
        mode = decide_contact_update_path(final_query)
        reply = build_contact_update_response(mode)
        follow_up = suggest_follow_up(mode)

        return {
            "reply": reply,
            "follow_up": follow_up,
            "metrics": { "used_rag": False, "latency": latency }
        }

    # ... (more orchestration logic for other banking queries) ...
```
Here's how the orchestration works in this specific case:

1. The orchestrator checks if your message contains keywords related to updating contact information.
2. If it does, instead of sending it to a general AI, it calls a specialized helper function `decide_contact_update_path`. This function, part of our [Domain-Specific Banking Policy & Logic](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%205%3A%20Domain-Specific%20Banking%20Policy%20%26%20Logic%20.md), determines how to handle the request (e.g., "visit branch only," "contact customer care first").
3. It then uses another helper `build_contact_update_response` to craft a precise, policy-compliant reply.
4.This specific, safe reply is then sent back to you. This is a great example of the orchestrator directing traffic to the most appropriate "expert."

## Orchestration for General Banking and Information Retrieval

If the query isn't a special policy case, the orchestrator then decides if it's a general banking question that might need information from our knowledge base (RAG) or simply needs a smart reply from the main AI (LLM).
```
# main.py - inside the chatbot function

    # ... (previous code including contact update logic) ...

    BANKING_HINTS = [
        "bank", "banking", "account", "loan", "card",
        # ... many more banking keywords ...
    ]

    is_probable_banking = any(hint in final_query for hint in BANKING_HINTS)
    image_uploaded = bool(image)

    # If it's a banking-related query or an image was uploaded (implies potential banking document)
    if intent is not None or is_probable_banking or image_uploaded:
        use_rag = True # Our orchestrator defaults to trying RAG for banking questions

        if use_rag:
            # Try to find specific context from our banking knowledge base
            context_chunks = rag_search(final_query) # Uses RAG Engine
            context = "\n".join(context_chunks) if isinstance(context_chunks, list) else context_chunks

            if not context or len(context.strip()) < 50:
                # If RAG didn't find enough specific info, ask the general LLM
                reply = groq_chat(session_id, final_query) # Uses LLM Service
                return {
                    "reply": reply,
                    "metrics": { "used_rag": False, "latency": latency }
                }

            # If RAG found good context, combine it with the query and ask the LLM
            prompt = f"""... (system instructions for LLM with CONTEXT and USER QUESTION) ..."""
            answer = groq_chat(session_id, prompt) # Uses LLM Service

            # ... (faithfulness check) ...

            return {
                "reply": answer,
                "metrics": { "used_rag": True, "latency": latency }
            }
        # ... (other cases like LLM ONLY for general banking) ...

    # ... (fallback for purely conversational queries) ...
```
Here's the orchestration flow for general banking questions:

1. **Banking Check**: The orchestrator first checks if the query contains common "banking hints" or if an intent was already detected by the [Intent Detection System](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%204%3A%20Intent%20Detection.md). If an image was uploaded, it also assumes it's banking-related.
2. **RAG Attempt**: It then tries to find specific answers using the [Graph Retrieval-Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md). This is like looking up information in a specialized bank encyclopedia.
3. **LLM with Context**: If RAG finds relevant information (`context`), the orchestrator sends both your original question and this found context to the powerful [Large Language Model (LLM) Service](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md) to generate a well-informed answer.
4. **LLM Only**: If RAG doesn't find enough specific information, the orchestrator still sends the question to the [Large Language Model (LLM) Service](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md), relying on its general banking knowledge.
   
## Visualizing Orchestration
Let's summarize the contact update scenario with a simple sequence diagram:

<img width="70%" height="622" alt="image" src="https://github.com/user-attachments/assets/f6e5258f-2d72-41d0-bfad-97abb06f81f9" />

## Conclusion

In this chapter, we've explored the foundational concepts of the Chatbot API and Orchestration. We learned that the API is the main entry point for user requests, and the Orchestrator acts as the intelligent conductor, directing user queries to the right modules and combining their outputs to form a coherent reply. We saw how this "brain" makes decisions, from pre-processing text to applying specific banking policies and using advanced AI models.

Now that we understand how requests are received and managed, our next step is to dive into the very first action the orchestrator takes: making sense of the raw text input.

Next Chapter: [Text Preprocessing and Normalization](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%203%3A%20Text%20Preprocessing%20%26%20Normalization.md)

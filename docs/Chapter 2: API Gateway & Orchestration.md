# Chapter 2: API Gateway & Orchestration
Welcome back! In our previous chapter, Frontend User Interface, you learned about the friendly chat window where you type your questions to our Banking AI Assistant. You saw how your message, like "What is my account balance?", gets sent off when you click "Send".

But what happens next? Where does your message go after it leaves the Frontend? How does the AI know what to do with it? That's exactly what we'll explore in this chapter: **the API Gateway & Orchestration.**

## What Problem Does it Solve?
Imagine you're at a grand concert, and many musicians are ready to play different instruments: violins, trumpets, drums, etc. Each musician is an expert at their own instrument. Now, imagine a user (you!) asks the orchestra to play a specific song. How do they know which instrument plays when? Which part comes first?

Our Banking AI Assistant is like that orchestra. It has many "expert musicians" (internal services) that do different jobs:
- One "musician" understands the intent of your question (e.g., "Is this about my balance or a loan?").
- Another "musician" searches through banking documents for relevant information.
- A "lead singer" (a powerful AI model) generates the actual human-like response.
Without a central director, it would be chaos! Your message would arrive, and all these services might try to process it at once, or worse, none would know they needed to act.

This is where the **API Gateway & Orchestration** comes in. It's the **central control hub** and the **conductor** of our AI orchestra.

## Key Concepts: API Gateway and Orchestration
Let's break down these two important ideas:

### 1. API Gateway: The Smart Receptionist
Think of the API Gateway as the **main entrance** or the **smart receptionist** of our entire AI system.

- **Receives Requests**: When you click "Send" in the Frontend User Interface, your message (and possibly an image) first arrives here. It's the only door to our AI's brain.
  
- **Checks and Routes**: Just like a receptionist might ask "Do you have an appointment?" or "Who are you here to see?", the API Gateway can perform initial checks (like ensuring the request is valid). Then, it directs the request to the correct internal process.
  
- **Simplifies Frontend**: The Frontend doesn't need to know about all the different internal services. It just sends everything to the API Gateway, which handles the rest.
  
### 2. Orchestration: The Master Conductor
Once the API Gateway has received a request, the **Orchestration** part takes over. This is like the **main conductor** of our orchestra, directing the flow of information and calling different services in the right order.

- **Decision Maker**: It decides what steps are needed to answer your question. Does it need to check your intent first? Does it need to search for specific banking documents?
  
- **Coordinates Services**: It calls the right internal services (our "musicians") one by one, giving them the necessary information and combining their outputs.

- **Builds the Final Response**: After all the services have done their part, the Orchestration collects their findings and crafts the final answer to send back to you.
  
### Our Use Case: "What is my account balance?"
Let's revisit our example: you ask, "What is my account balance?"

 **1.From Frontend to Gateway:** You type "What is my account balance?" in the [Frontend User Interface](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%201%3A%20Frontend%20User%20Interface.md) and click "Send". Your message travels over the internet and arrives at the API Gateway.
 **2.Gateway Orchestrates:** The API Gateway immediately starts its orchestration process.
- It first sends your question to an [Intent Detection](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%204%3A%20Intent%20Detection.md) service to figure out you're asking about your "Account Balance".

- Next, it might decide if it needs to look up specific information using the [Graph Retrieval Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md). For a simple balance inquiry, it might not need RAG, or it might search for how to check a balance.
- Finally, it sends the gathered information (your original question, detected intent, any RAG context) to the [Large Language Model (LLM) Integration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md) to generate a friendly and accurate answer.
 **3.Back to Frontend**: The LLM generates the reply, for example, "Your current account balance is $1,250.75." This reply travels back through the API Gateway, which then sends it to the [Frontend User Interface](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%201%3A%20Frontend%20User%20Interface.md).
**4.You See the Answer:** The Frontend displays the AI's answer in the chat window.
  
### What Happens Under the Hood? (Internal Implementation)

Let's peek behind the scenes and see how the `main.py` file acts as our API Gateway and Orchestrator.

Here's a simplified step-by-step flow of what happens:
<img width="70%" height="616" alt="image" src="https://github.com/user-attachments/assets/307d1d5e-4708-44b5-9f5d-62e88c35bdd7" />

### The API Gateway Entry Point
Our `main.py` file uses a framework called FastAPI to create the API Gateway. The `/chatbot/ask` is the specific "door" that handles chat requests.
```
# From main.py
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# ... other imports ...

app = FastAPI()

# This allows our Frontend (running on a different address) to talk to the Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows requests from any origin (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is the main function that handles incoming chat requests
@app.post("/chatbot/ask")
async def chatbot(
    session_id: str = Form(...), # Unique ID for each chat conversation
    message: str = Form(""),     # The text message from the user
    image: UploadFile = File(None) # Optional image file
):
    raw_query = (message or "").strip()
    # ... orchestration logic begins here ...
```
**Explanation**: This code sets up our FastAPI application. The `@app.post("/chatbot/ask")` part defines an endpoint (a specific URL) that the Frontend can send `POST` requests to. When the Frontend sends your message, this `chatbot` function is activated, receiving your `message` and `session_id`.

### The Orchestration Logic
Inside the `chatbot` function, the orchestration begins. It's like a series of instructions for the conductor:
```
# From main.py (inside the chatbot function)

    # 1. First, we clean up the user's raw message
    # This calls our Text Preprocessing & Normalization service
    normalized_query = normalize_text(raw_query)

    # 2. Next, we figure out what the user *really* wants to do
    # This calls our Intent Detection service
    intent, score, detected_text = detect_intent(
        query=normalized_query if normalized_query else None,
        image_path=image_path
    )

    final_query = normalized_query # We'll use the cleaned query

    # 3. Handle special banking policies (e.g., changing contact info)
    # This is an example of Rule-based Banking Logic
    contact_update_keywords = [
        "change contact number", "update mobile",
        # ... more keywords ...
    ]
    if final_query and any(k in final_query for k in contact_update_keywords):
        # If it's a contact update, we have special, predefined rules.
        # We don't need the RAG or LLM for this specific case.
        mode = decide_contact_update_path(final_query)
        reply = build_contact_update_response(mode)
        # We send the reply back immediately after this rule-based decision
        return {"reply": reply, "follow_up": suggest_follow_up(mode), "metrics": {...}}
```
**Explanation:** Here, the API Gateway starts directing traffic:

1.It sends the `raw_query` to `normalize_text()` (a function that acts as our [Text Preprocessing & Normalization service](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md)) to clean it up.

2.Then, it calls `detect_intent()` (our [Intent Detection](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%204%3A%20Intent%20Detection.md) service) to understand the user's goal.

3.It also checks if the query matches certain "rule-based" banking logic, like updating a contact number. If it does, it directly provides a pre-defined answer, bypassing the more complex AI steps. This is a common way to handle predictable requests efficiently, covered further in [Rule-based Banking Logic](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%205%3A%20Rule-based%20Banking%20Logic.md).

### Calling RAG and LLM
If the request isn't handled by a specific rule, the orchestration continues to decide if it needs to fetch external information (using RAG) or directly ask the LLM.

```
# From main.py (inside the chatbot function, continuing the flow)

    # ... (After intent detection and rule-based logic) ...

    is_probable_banking = any(hint in final_query for hint in BANKING_HINTS)
    image_uploaded = bool(image)

    # If it's likely a banking query or an image was uploaded, consider RAG.
    if intent is not None or is_probable_banking or image_uploaded:
        # Our simplified logic for this tutorial always tries RAG if it's banking-related.
        use_rag = True

        if use_rag:
            # This calls our Retrieval Augmented Generation (RAG) Engine
            context_chunks = rag_search(final_query)
            context = "\n".join(context_chunks) if isinstance(context_chunks, list) else context_chunks

            if context: # If RAG found useful context
                # We build a special prompt for the LLM using the context found by RAG
                prompt = f"""
                You are a professional banking assistant. Use the CONTEXT below as a reference...
                CONTEXT: {context}
                USER QUESTION: {final_query}
                """
                answer = groq_chat(session_id, prompt) # Call the LLM with context
                return {"reply": answer, "metrics": {"used_rag": True, ...}}
            else: # If RAG found no context, just ask the LLM directly
                reply = groq_chat(session_id, final_query) # Call the LLM without context
                return {"reply": reply, "metrics": {"used_rag": False, ...}}
```

**Explanation:** This part is the core decision-making:

1.The orchestrator checks if the query is banking-related.

2.If `use_rag` is true (meaning we want to search for information), it calls `rag_search()` (our [Graph Retrieval Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md)).

3.If RAG finds relevant `context`, this context is cleverly added to the user's question to create a super-informed `prompt`.

4.Finally, `groq_chat()` (our [Large Language Model (LLM) Integration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md) service) is called with this `prompt`. The LLM generates the answer.

The API Gateway then takes this `answer` and sends it back to the Frontend.

## Conclusion
You've now seen how the **API Gateway & Orchestration** acts as the crucial central hub for our Banking AI Assistant. It's the receptionist that greets your requests and the conductor that directs the symphony of internal services, ensuring that your questions are processed efficiently and accurately, and that a helpful response is crafted and sent back to you.

It efficiently manages the flow:
- Receiving your message from the Frontend User Interface.
- Guiding it through Text Preprocessing & Normalization and Intent Detection.
- Deciding if Rule-based Banking Logic can handle it, or if it needs to consult the Retrieval Augmented Generation (RAG) Engine and the Large Language Model (LLM) Integration.
- Sending the final answer back.

Next, we'll dive deeper into the first step of this orchestration process: cleaning and preparing your text so the AI can understand it perfectly in [Text Preprocessing & Normalization](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%203%3A%20Text%20Preprocessing%20%26%20Normalization.md).

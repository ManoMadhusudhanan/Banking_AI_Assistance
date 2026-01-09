# Chapter 7: Large Language Model (LLM) Service

In Chapter 6: Domain-Specific Banking Policy & Logic, we learned how our Banking_AI_Assistance meticulously follows strict rules for sensitive banking tasks, ensuring security and compliance. This is crucial for actions like updating your mobile number.

But what about questions that are not tied to specific policies, situations where the Retrieval-Augmented Generation (RAG) Engine does not find exact factual context, or even general chit-chat? This is where the **Large Language Model (LLM) Service** comes into play. It provides the chatbot with the ability to think, understand, and respond like a human, delivering helpful and coherent answers across a wide range of inquiries.

---

## What Problem Does It Solve?

Imagine you ask our AI banking assistant:

- *"Hello, how are you today?"*  
- *"Can you explain what a credit score is in simple terms?"*  
- *"What are the benefits of having a savings account?"* (when RAG does not find specific bank documents)  
- *"Tell me a joke!"*  

For these types of questions, hard-coded rules or document retrieval alone are not enough. We need an AI that can:

- **Understand nuances:** Go beyond keywords to grasp the overall intent.
- **Generate human-like text:** Produce fluent, natural responses instead of fixed templates.
- **Handle general knowledge:** Answer questions not present in the bank’s internal documents.
- **Maintain conversation flow:** Respond naturally while keeping context from earlier messages.

If our assistant relied only on strict policies or retrieved facts, it would feel rigid and unengaging. It might even respond with something like *"No policy available for jokes."*

The **Large Language Model (LLM) Service** solves this by acting as the chatbot’s eloquent speaker and general knowledge expert.

---

## How the LLM Service Helps

The LLM Service is powered by advanced AI models (such as Groq’s `llama-3.1-8b-instant` or OpenAI’s GPT models). These models are trained on vast amounts of text data, enabling them to generate human-like responses on almost any topic.

In our system, the LLM functions as the chatbot’s **primary conversational brain**, handling:

- General banking explanations  
- Non-policy questions  
- Casual conversation  
- Natural dialogue flow  

---

## Key Concepts

### 1. Human-like Text Responses

The core strength of an LLM is its ability to generate natural-sounding text. It can construct sentences, paragraphs, and detailed explanations, making the chatbot feel conversational rather than robotic.

---

### 2. General Knowledge

LLMs are trained on large and diverse datasets, giving them broad general knowledge. This allows them to answer questions such as:

- What a credit score is  
- Why savings accounts are useful  
- Common financial concepts  

Even when these details are not explicitly available in the bank’s internal documents.

---

### 3. Conversational Fluency

With the help of conversation memory, an LLM can maintain context across multiple turns. This enables smooth, continuous interactions instead of disconnected responses.

---

### 4. Sophisticated AI Models (Groq / OpenAI)

Our Banking_AI_Assistance uses external LLM providers like **Groq**, which expose powerful AI models through APIs. This allows the chatbot to leverage advanced AI capabilities without requiring local high-performance hardware.

---

### LLM Capabilities Overview

| LLM Feature | How It Helps the Banking AI |
|------------|-----------------------------|
| Human-like Text | Produces friendly, easy-to-understand replies |
| General Knowledge | Answers broad banking and non-banking questions |
| Conversational Flow | Keeps interactions natural and engaging |
| External Power | Uses cloud-hosted AI models to handle complex reasoning |

---

## How to Use It (The `groq_chat` Function)

The Orchestrator decides when to invoke the LLM Service. If a query:

- Is not covered by strict policy logic, and  
- Does not have sufficient factual context from the RAG Engine  

the Orchestrator forwards the request to the LLM.

This is handled using the `groq_chat` function in `main.py`.

---

## `main.py` – LLM Invocation (Simplified)

```python
# main.py - inside the chatbot function (simplified)

    # ... (previous code) ...

    # If RAG didn't find specific info for a banking question...
    if not context or len(context.strip()) < 50:
        reply = groq_chat(session_id, final_query) # Uses LLM Service
        return {
            "reply": reply,
            "metrics": { "used_rag": False, "latency": latency }
        }

    # ... Or if it's a general conversational query ...
    if final_query:
       reply = clean_response(groq_chat(session_id, final_query))
       return {
            "reply": reply,
            "metrics": {
                "used_rag": False,
                "latency": latency
            }
        }
    # ...
```
The `groq_chat` function takes your `session_id` (to remember your conversation) and your `user_prompt` (the cleaned-up question) as input. It then returns a human-like reply generated by the LLM.

Let's look at some examples:
| Input (`user_prompt`) | Output (`reply`) |
|----------------------|------------------|
| "Hi there!" | "Hello! How can I assist you today?" |
| "Explain what a credit score is." | "A credit score is a numerical representation of your creditworthiness. It's used by lenders to assess your ability to repay debt." |
| "What are the benefits of having a savings account?" | "Savings accounts offer a secure place to keep your money, earn interest, and provide easy access to funds for your financial needs." |


## Under the Hood: How the LLM Service Works
Let's explore how the `groq_chat` function interacts with the powerful AI model.

### The Flow of an LLM Interaction
Here's a simplified sequence of what happens when the Orchestrator sends a question to the LLM Service:

<img width="70%" height="620" alt="image" src="https://github.com/user-attachments/assets/ef369d5c-ac9d-46b7-92cc-68afe53a4954" />

### The Code: `main.py` (The groq_chat Function)
The `groq_chat` function in `main.py` is responsible for communicating with the Groq LLM API.

First, we need the API key to connect to Groq's services:
```
# main.py

import os
import requests # Used to make requests to the Groq API
# ... other imports ...

GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Get API key from environment variables

# CHAT MEMORY to keep track of conversation history
CHAT_MEMORY = defaultdict(list)
```
- `GROQ_API_KEY = os.getenv("GROQ_API_KEY")`: This line securely retrieves your unique API key for Groq from your system's environment variables. This key authenticates your requests to Groq.
- `CHAT_MEMORY = defaultdict(list)`: This is where we store the history of our conversation with each user (`session_id`). This allows the LLM to "remember" what was said earlier.
  
Now, let's look at the `groq_chat` function itself:
```
# main.py

def groq_chat(session_id: str, user_prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Prepare messages for the LLM
    messages = [
        {
            "role": "system", # Instructions for the AI
           "content": (
                "You are a professional, polite banking assistant. "
                "Respond clearly and formally. "
                "Provide only general and safe guidance for banking-related questions. "
                "Guide users using universally applicable channels such as visiting a bank branch "
                "or contacting official customer care. "
                "Do not assume the availability of specific online or mobile banking features "
                "unless they are explicitly stated in the provided context. "
                "Never request passwords, OTPs, CVV, account numbers, customer IDs, "
                "or any personally identifiable or sensitive information."
            )
        }
    ]

    # Add previous conversation turns
    messages.extend(CHAT_MEMORY[session_id])
    # Add the current user's question
    messages.append({"role": "user", "content": user_prompt})

    # 2. Define the payload (what we send to the Groq API)
    payload = {
        "model": "llama-3.1-8b-instant", # The specific AI model we want to use
        "temperature": 0.7, # How creative/random the AI's response should be (0.0 for factual, 1.0 for very creative)
        "messages": messages
    }

    # 3. Send the request to Groq and get the response
    res = requests.post(url, json=payload, headers=headers).json()

    # Handle cases where the API doesn't return a valid response
    if "choices" not in res:
        return "Hello! How can I assist you today?"

    # 4. Extract the AI's reply
    reply = res["choices"][0]["message"]["content"].strip()

    # 5. Store the current user message and AI reply in chat history
    CHAT_MEMORY[session_id].append({"role": "user", "content": user_prompt})
    CHAT_MEMORY[session_id].append({"role": "assistant", "content": reply})

    return reply
```
Here's a breakdown of the key parts:

- `url, headers`: These set up how we connect to Groq's API. The Authorization header includes our `GROQ_API_KEY`.
- `messages list`: This is crucial for guiding the LLM.
- `{"role": "system", "content": "..."}`: This is a system prompt. It tells the AI who it is (a professional banking assistant) and how it should behave (polite, safe, never ask for sensitive info). This ensures the AI always acts appropriately within a banking context.
- `messages.extend(CHAT_MEMORY[session_id])`: We add the entire previous conversation history for this `session_id`. This allows the LLM to understand the context of the current question.
- `messages.append({"role": "user", "content": user_prompt})`: Finally, we add the user's current question.
- `payload`: This is the data we send to Groq.
- `"model": "llama-3.1-8b-instant"`: Specifies which Groq LLM model to use. Different models have different capabilities and speeds.
- `"temperature": 0.7`: This controls how "creative" the AI's answer will be. A lower number (e.g., 0.2) means more factual and less varied responses, while a higher number (e.g., 0.9) encourages more diverse and imaginative text. For a banking bot, we keep it moderate for balance.
- `requests.post(url, json=payload, headers=headers).json()`: This line sends the `payload` to the Groq API and gets the JSON response back.
- `reply = res["choices"][0]["message"]["content"].strip()`: We extract the actual text of the AI's generated response from the JSON.
- `CHAT_MEMORY[session_id].append(...)`: We update the `CHAT_MEMORY` with both the user's question and the AI's reply. This way, in the next turn, the LLM will have the full context.
  
This entire process ensures that our `Banking_AI_Assistance` can engage in flexible, intelligent, and safe conversations, making it truly helpful beyond just strict rule-following.

## Conclusion
We've now explored the **Large Language Model (LLM) Service**, which provides our Banking_AI_Assistance with its primary conversational ability. It acts as the bot's eloquent speaker, generating human-like text responses, leveraging general knowledge, and maintaining conversational fluency. By integrating powerful models like `Groq's Llama-3.1-8b-instant`, our chatbot can handle a wide array of inquiries, from general banking explanations to casual greetings, making the user experience natural and engaging. This crucial component ties together the entire system, ensuring that whether a query requires specific policy adherence, factual retrieval, or just a friendly chat, our banking assistant is ready to provide a smart and helpful response.

This concludes our deep dive into the core components of the `Banking_AI_Assistance` project. We've journeyed from the central orchestrator to text preprocessing, intent detection, OCR, RAG, domain-specific logic, and finally, the powerful LLM, understanding how each piece contributes to building a sophisticated and intelligent banking assistant.




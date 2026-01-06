# Chapter 5: Rule-based Banking Logic
Welcome back, future AI banking experts! In our last chapter, Intent Detection, we saw how our AI assistant intelligently figures out the core goal or purpose behind your banking questions. Once it knows what you want, the system needs to decide the best way to answer.

Sometimes, your request is very specific, critical, and requires a precise, non-negotiable answer. It's not a question that needs creative thinking or deep research; it needs a direct, policy-compliant instruction. This is where **Rule-based Banking Logic** steps in.

## What Problem Does it Solve?
Imagine you're at the bank, and you say, "I've lost my debit card; please block it!" or "I need to update my contact number." These aren't questions where you want the bank to ponder and come up with a slightly different, creative answer each time. You need:

1. **Immediate Action:** Fast response because it's often urgent.
2. **Accuracy:** The steps must be 100% correct and compliant with banking policies.
3. **Consistency:** Everyone should get the exact same, correct instructions for sensitive actions.
 
Our smart AI assistant faces a similar challenge. While a Large Language Model (LLM) Integration is excellent for nuanced conversations and complex queries, it might sometimes "hallucinate" or provide slightly varying advice for critical, rule-bound banking actions.

**Rule-based Banking Logic** solves this by providing **immediate, pre-programmed responses** for these specific, critical, or very frequently asked banking queries. It's like having a set of emergency buttons or a quick-reference guide for important scenarios, ensuring speed, consistency, and strict adherence to banking guidelines.

## Key Concepts
Let's break down the core ideas behind Rule-based Banking Logic:

### 1. Rules, Not Guessing
Instead of asking a complex AI model to "think" about the answer, this component relies on simple, predefined rules. If a specific condition is met (e.g., certain keywords are present), a specific, pre-written answer is immediately given. This means no "thinking" is needed; it's a direct lookup.

### 2. Keywords and Patterns
How does the system know when to use a rule? It looks for specific **keywords or patterns** in your cleaned query (which came from [Text Preprocessing & Normalization](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%203%3A%20Text%20Preprocessing%20%26%20Normalization.md)). For example:

- "block card", "lost card"
- "change contact number", "update mobile"
- "check balance" (for simple, direct balance inquiries)
  
### 3. Pre-programmed Responses
The answers for these rule-based queries are **already written and stored**. They are crafted by banking experts to be precise, safe, and policy-compliant. They are not generated dynamically by an AI model.

### 4. Speed and Consistency
Because the answers are pre-set and triggered by simple keyword matches, the system can respond almost instantly. This also guarantees that every user asking the same rule-based question gets the exact same correct answer, avoiding any variations.

## How Rule-based Banking Logic Helps Our Use Case
Let's consider a practical example: updating your contact details.

**User's Query (after cleaning and intent detection):** "I want to change my contact number, but I lost my phone."

Here's how Rule-based Banking Logic would handle it:

1. **Keyword Detection**: The system scans the query for keywords like "change contact number" and "lost phone."
2. **Rule Match:** It finds a rule that says: "If the user wants to change their contact number AND mentions 'lost phone' or 'SIM lost', then provide the 'branch_only' response."
3. **Immediate Response:** Instead of sending this to a complex AI, it instantly pulls the predefined response: "For security reasons, updating the registered mobile number in this case requires a visit to the nearest IndusInd Bank branch with valid photo identification."
4. **No AI Guesswork:**   The answer is precise, secure, and doesn't rely on the AI interpreting policies on the fly.
   
This ensures that sensitive banking actions are handled with utmost care and accuracy.

## What Happens Under the Hood? (Internal Implementation)

Let's see how our main.py file implements this Rule-based Banking Logic. It comes into play after [Text Preprocessing & Normalization](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%203%3A%20Text%20Preprocessing%20%26%20Normalization.md) and [Intent Detection](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%204%3A%20Intent%20Detection.md), but before engaging the more general [Graph Retrieval Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md) or Large [Language Model (LLM) Integration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md).

The Flow

<img width="70%" height="543" alt="image" src="https://github.com/user-attachments/assets/c1dd0ac1-c1ad-4e88-8c5e-fa5075eeb2b6" />

As you can see, if a rule is matched, the request doesn't even go to the more complex (and potentially slower) RAG or LLM parts of the system. It gets an immediate, pre-defined answer.

## Code Walkthrough (main.py)
The rule-based logic is integrated directly into the chatbot function in main.py.

**1. Defining Keywords and Helper Functions**: First, we define the keywords that trigger our rule, and helper functions to build the appropriate responses.
```
# From main.py

# ... (other imports and app setup) ...

# These keywords trigger our special contact update logic
contact_update_keywords = [
    "change contact number", "update contact number",
    "change mobile", "update mobile",
    "registered mobile", "passbook update"
]

# This function decides *which* specific response to give
def decide_contact_update_path(query: str) -> str:
    q = query.lower()

    if any(x in q for x in ["lost phone", "sim lost", "number inactive"]):
        return "branch_only" # If phone lost, must visit branch

    if any(x in q for x in ["can't visit", "cannot visit", "far", "busy", "no time"]):
        return "customer_care_first" # Suggest customer care first

    if any(x in q for x in ["app", "net banking", "online"]):
        return "digital_optional" # Suggest digital options

    return "default" # General advice

# This function builds the actual message based on the decision
def build_contact_update_response(mode: str) -> str:
    if mode == "branch_only":
        return "For security reasons, updating the registered mobile number in this case requires a visit to the nearest IndusInd Bank branch with valid photo identification."
    # ... (other 'mode' responses like 'customer_care_first', 'digital_optional', 'default') ...
    return "You may update the registered mobile number by visiting a nearby IndusInd Bank branch or by contacting customer care at 1860 267 7777. Identity verification is mandatory for such updates."
```
**Explanation:**

- `contact_update_keywords:` This list holds the specific phrases that tell our system, "Hey, this is about updating contact info!"
- `decide_contact_update_path(query)`: This is a mini-rule engine itself! It takes the user's `query` and looks for additional keywords (like "lost phone" or "can't visit") to figure out the specific scenario. This allows us to give tailored advice.
- `build_contact_update_response(mode)`: Once `decide_contact_update_path` tells us the `mode` (e.g., "branch_only"), this function retrieves the exact, pre-written response for that scenario.
  
**2. Applying the Rule in the Main Chatbot Function:** Inside our main `chatbot` function, after cleaning the query and detecting intent, we check for these rules.
```
# From main.py (inside the chatbot function)

    # ... (After image upload, raw_query, normalized_query, and intent detection) ...

    final_query = normalized_query # We use the cleaned query for checking rules
    latency = round(time.time() - start_time, 2)

    # ---------------- POLICY-GUARDED CONTACT UPDATE ----------------
    # Check if the user's query contains any of our rule-triggering keywords
    if final_query and any(k in final_query for k in contact_update_keywords):
        # If a keyword is found, determine the specific path (e.g., branch_only)
        mode = decide_contact_update_path(final_query)
        # Get the pre-written reply for that path
        reply = build_contact_update_response(mode)
        # Suggest a follow-up question
        follow_up = suggest_follow_up(mode) # Helper function to suggest next steps

        # Immediately send this rule-based reply back to the user
        return {
            "reply": reply,
            "follow_up": follow_up,
            "metrics": {
                "used_rag": False, # We didn't use RAG or LLM for this
                "latency": latency
            }
        }

    # ... (If no rule matched, the code would continue to RAG/LLM sections) ...
```
**Explanation:**

- `if final_query and any(k in final_query for k in contact_update_keywords):`: This is the core rule! It checks if the `final_query` contains any of the keywords we defined in `contact_update_keywords`.
- If the condition is `True`, it means our rule is triggered.
- `mode = decide_contact_update_path(final_query)`: We then use our helper function to figure out the exact scenario (e.g., "lost phone" means "branch_only").
- `reply = build_contact_update_response(mode)`: The specific, pre-written answer for that `mode` is retrieved.
- `return {...}`: **Crucially**, the function immediately returns this reply. This means the query never goes to the [Graph Retrieval Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md) or [Large Language Model (LLM) Integration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md). The rule has done its job, providing a fast and accurate response.
This makes our system highly efficient and reliable for critical banking functions.

## Conclusion
You've now explored the vital role of **Rule-based Banking Logic**! It acts as our AI's set of quick-reference guides or emergency buttons, providing instant, precise, and policy-compliant answers for sensitive or frequently asked banking queries. By using specific keywords to trigger pre-programmed responses, we ensure speed, accuracy, and unwavering adherence to banking guidelines, especially for critical actions like updating contact details or blocking cards. This approach complements the more flexible AI models, allowing our assistant to be both smart and strictly reliable.

With our rules in place for predictable scenarios, what happens when a question is more complex, requiring deep knowledge from banking documents? That's what we'll explore next!

Let's move on to discover how our AI can search through vast amounts of information to provide detailed answers in the next chapter: [Graph Retrieval Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md).

# Chapter 5: Domain-Specific Banking Policy & Logic

In [Chapter 6: Graph Retrieval-Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md), we will explore how our Banking_AI_Assistance will act as a smart "research assistant," retrieving factual information from official bank documents to answer user questions accurately. This approach will be particularly useful for general inquiries such as "What are the loan eligibility criteria?".

However, banking will involve many actions that require strict adherence to specific rules, procedures, and security protocols. For these sensitive or critical tasks, simply looking up facts or relying on a general AI response will not be sufficient. We will need a system that behaves like a bank’s official rulebook, ensuring that every step is followed precisely.


## What Problem Does It Solve?

Imagine you want to update your registered mobile number with the bank. You might ask our AI assistant:

> *"I need to change my mobile number."*

This isn't a simple question that can be answered with a general fact or a creative AI response. Changing contact details involves:

- **Security:** Verifying your identity is paramount to prevent fraud.
- **Compliance:** Banks must follow strict regulatory guidelines for such updates.
- **Specific Procedures:** Different procedures depending on the situation (for example, if you lost your phone versus getting a new number).

If our AI assistant just gave a generic answer—or worse, made up a procedure—it could lead to serious security risks or non-compliance. This is where **Domain-Specific Banking Policy & Logic** comes in.

---

This part of our system contains specific, hard-coded rules and policies for handling sensitive or common banking requests. It's like the bank's official policy manual built directly into the AI. When the Orchestrator identifies a request that touches upon these critical areas, it routes it here. This layer ensures:

- **Safety:** By enforcing strict security procedures.
- **Compliance:** By following all necessary regulations.
- **Accuracy:** By providing precise, approved steps.
- **Consistency:** By giving the same, correct guidance every time.

Instead of relying solely on the general Large Language Model (LLM) Service, this layer provides structured, safe, and compliant responses, ensuring critical procedures are followed precisely.

---

## Key Concepts

Let's break down the main ideas behind this internal "policy manual" within our AI.

### 1. Hard-Coded Rules

These are specific *if–then* statements programmed directly into the system. They are not learned by an AI model but are explicitly defined by banking experts.

**Example:**  
IF a user wants to update their mobile number **AND** mentions *"lost phone"*,  
THEN the policy dictates a **branch visit only**.

---

### 2. Sensitive Banking Requests

These are actions that have direct implications for a customer's account security or financial well-being.

**Examples:**
- Updating contact details  
- Blocking a lost card  
- Applying for sensitive products  
- Making high-value transfers  

For these scenarios, generic AI responses are too risky.

---

### 3. Safety & Compliance First

The primary goal of this layer is to ensure that all interactions related to sensitive requests are handled with the highest level of security and in full compliance with banking regulations. It prevents the AI from suggesting unsafe or non-standard procedures.

---

### 4. Predictable, Structured Responses

For critical actions, users need clear and unambiguous instructions. This layer generates pre-approved, consistent messages, eliminating any possibility of a creative (but potentially incorrect) AI response.

| Feature | General LLM Response (Risk) | Domain-Specific Policy (Benefit) |
|-------|-----------------------------|----------------------------------|
| Accuracy | Might hallucinate procedures | Provides precise, verified banking procedures |
| Security | Could suggest less secure options | Enforces strict security protocols (e.g., branch visit for lost phone) |
| Consistency | Responses may vary by phrasing | Always provides approved guidance |
| Compliance | Not inherently regulation-aware | Designed to strictly adhere to regulatory requirements |

---

## How to Use It (The Orchestrator’s Role)

The orchestrator in our Banking_AI_Assistance is smart enough to know when to use the general Retrieval-Augmented Generation (RAG) Engine or Large Language Model (LLM) Service, and when to defer to the strict Domain-Specific Banking Policy & Logic.

As introduced earlier, when a user asks to change their mobile number, the orchestrator checks for specific keywords.

---

## `main.py` – Inside the Chatbot Function (Simplified)

```python
# Check if the query is about updating contact information
contact_update_keywords = [
    "change contact number",
    "update mobile",
    # ... more keywords ...
]

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

# ... other logic for banking and conversational queries ...
```
In this snippet, if your cleaned-up query (`final_query`) matches any of the `contact_update_keywords`, the orchestrator immediately calls specialized functions:

- `decide_contact_update_path`(`final_query`): This function analyzes your query further to determine the specific policy path (e.g., if you lost your phone, or want to do it online).
- `build_contact_update_response`(mode): This function then uses the determined policy `mode` to craft a precise, compliant response.
- `suggest_follow_up`(mode): This provides a relevant next question to guide the user.
Let's look at some examples of how these functions guide the conversation:

| Input (`final_query`) | Mode (`decide_contact_update_path`) | Reply (`build_contact_update_response`) | Follow-up (`suggest_follow_up`) |
|----------------------|------------------------------------|-----------------------------------------|---------------------------------|
| "I lost my phone, change my number" | `branch_only` | For security reasons, updating the registered mobile number in this case requires a visit to the nearest IndusInd Bank branch with valid photo identification. | Would you like to know the documents required for the branch visit? |
| "update mobile, but I can't visit" | `customer_care_first` | If visiting a branch is not convenient, you may contact IndusInd Bank customer care at 1860 267 7777 for guidance on the required process. | Would you like the customer care working hours? |
| "change contact number online" | `digital_optional` | Customers registered for official digital banking services may check whether a mobile number update option is available under profile settings. If unavailable, a branch visit is recommended. | Would you like guidance on checking this through digital banking? |
| "update my mobile number" | `default` | You may update the registered mobile number by visiting a nearby IndusInd Bank branch or by contacting customer care at 1860 267 7777. Identity verification is mandatory for such updates. | Would you like to know the documents required to update your mobile number? |

## Under the Hood: How Policy Logic Works
Let's see how these policy-guided responses are generated.

### The Flow of a Policy-Guarded Request
Here's a simple sequence of what happens when the orchestrator detects a sensitive request:

<img width="70%" height="590" alt="image" src="https://github.com/user-attachments/assets/e18d8307-ba99-441a-92e1-1beb0de02f10" />

### The Code: `main.py` (Policy Helpers)
The policy decision-making and response generation logic are implemented directly within the main.py file to keep it close to the orchestrator's decision flow.

### 1. Deciding the Policy Path (`decide_contact_update_path`)
This function examines the user's query to determine the most appropriate policy mode.
```
# main.py

def decide_contact_update_path(query: str) -> str:
    q = query.lower()

    # Rule 1: If keywords like "lost phone" are present, it's branch-only
    if any(x in q for x in ["lost phone", "sim lost", "number inactive"]):
        return "branch_only"

    # Rule 2: If user expresses inability to visit, suggest customer care
    if any(x in q for x in ["can't visit", "cannot visit", "far", "busy", "no time"]):
        return "customer_care_first"

    # Rule 3: If user asks about digital channels, offer that option
    if any(x in q for x in ["app", "net banking", "online"]):
        return "digital_optional"

    # Default rule if no specific scenario matches
    return "default"
```
This function uses simple if statements to check for specific keywords. Each if block represents a distinct banking policy scenario (e.g., losing a phone often implies higher fraud risk, hence a stricter policy).

### 2. Building the Policy Response (`build_contact_update_response`)
Based on the mode returned by the previous function, this function crafts the exact message to send to the user.
```
# main.py

def build_contact_update_response(mode: str) -> str:
    if mode == "branch_only":
        return (
            "For security reasons, updating the registered mobile number in this case "
            "requires a visit to the nearest IndusInd Bank branch with valid photo identification."
        )

    if mode == "customer_care_first":
        return (
            "If visiting a branch is not convenient, you may contact IndusInd Bank customer care "
            "at 1860 267 7777 for guidance on the required process."
        )

    if mode == "digital_optional":
        return (
            "Customers registered for official digital banking services may check whether a "
            "mobile number update option is available under profile settings. "
            "If unavailable, a branch visit is recommended."
        )

    return ( # Default response
        "You may update the registered mobile number by visiting a nearby IndusInd Bank branch "
        "or by contacting customer care at 1860 267 7777. "
        "Identity verification is mandatory for such updates."
    )
```
Each if block provides a pre-written, carefully worded response that is compliant and secure. Notice how there are no creative AI elements here; the response is fixed based on the determined mode.

### 3. Suggesting a Follow-up Question (`suggest_follow_up`)
To make the interaction more helpful, a relevant follow-up question is provided.
```
# main.py

def suggest_follow_up(mode: str) -> str | None:
    if mode == "branch_only":
        return "Would you like to know the documents required for the branch visit?"

    if mode == "customer_care_first":
        return "Would you like the customer care working hours?"

    if mode == "digital_optional":
        return "Would you like guidance on checking this through digital banking?"

    # Default follow-up
    return "Would you like to know the documents required to update your mobile number?"
```
This function ensures the bot proactively guides the user to the next logical step, improving the user experience while adhering to policies.

By having these hard-coded policies, our `Banking_AI_Assistance` can handle crucial and sensitive banking requests with utmost care, security, and precision, without risking inaccurate or unsafe advice from a more general AI model.

### Conclusion
We've learned that the **Domain-Specific Banking Policy & Logic** layer acts as the `Banking_AI_Assistance`'s internal "rulebook." It provides specific, pre-defined procedures and responses for sensitive banking requests like updating contact details. This ensures that even the smartest AI operates within strict security and compliance guidelines, delivering accurate, safe, and consistent advice when it matters most. This layer handles the critical, rule-bound tasks, allowing other components to focus on information retrieval and conversational aspects.

Now that we understand how specific banking policies are handled, our next step is to explore the powerful brain that ties everything together and generates human-like responses for more general and conversational queries: the [Large Language Model (LLM) Service](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md).

Next Chapter: [Graph Retrieval Augmented Generation (RAG) Engine](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md)

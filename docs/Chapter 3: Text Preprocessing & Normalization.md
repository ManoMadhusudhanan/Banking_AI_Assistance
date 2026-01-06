# Chapter 3: Text Preprocessing & Normalization
Welcome back, future AI experts! In our last chapter, [API Gateway & Orchestration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%202%3A%20API%20Gateway%20%26%20Orchestration.md), we learned how your message, after leaving the [Frontend User Interface](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%201%3A%20Frontend%20User%20Interface.md), first arrives at a central hub. This hub, our "conductor," then decides the next steps. The very first step the conductor often directs your message to is exactly what we'll explore now: **Text Preprocessing & Normalization.**

## What Problem Does it Solve?
Imagine you're trying to talk to a very precise, but very literal, friend. If you say "whaat is my acount balence??!", they might stare blankly because they don't understand "whaat" or "balence", and the extra question marks confuse them. Our AI assistant is a bit like that literal friend.

Computers and AI models are amazing, but they thrive on consistency. If you ask "What is my account balance?" and another user asks "what is my accnt balance?", an AI might treat these as two completely different questions unless we "clean up" and "standardize" the text first.

This is exactly the problem **Text Preprocessing & Normalization** solves. It's like a **quality control stage** that cleans and polishes raw text input.

**Our Goal for This Chapter:** By the end of this chapter, you'll understand how a messy user query like "pleez tell me my currunt balence plz!!" gets transformed into a clean, standard format like "please tell me my current balance please", making it much easier for the AI to understand.

## Key Concepts
Text Preprocessing & Normalization involves several steps to make text consistent:

### 1. Lowercase Conversion
- **What it is**: Changing all letters in the text to lowercase.
- **Why it's important**: "Hello", "HELLO", and "hello" all mean the same thing to a human. But to a computer, they are seen as different sequences of characters. Converting everything to lowercase ensures that the AI treats "What is my account balance?" and "what is my account balance?" as the exact same question.
### 2. Punctuation Removal
- **What it is:** Getting rid of special characters like !, ?, ., ,, _, etc.
- **Why it's important**: Punctuation usually doesn't change the core meaning of a query for an AI. "What is my balance?" and "What is my balance???" should be understood identically. Removing punctuation helps simplify the text and focus on the actual words.
### 3. Correcting Common Spelling Errors (Spell Correction)
- **What it is:** Automatically fixing common typos or misspellings.
- **Why it's important:** We all make typos! If a user types "balence" instead of "balance" or "acount" instead of "account", the AI might struggle to understand. Spell correction helps the AI understand the intended word.
### 4. Protecting Specific Banking Terms
- **What it is:** This is a **crucial step** for our Banking AI! It involves identifying and preventing certain banking-specific words (like "NEFT", "UPI", "KYC", "PAN", "Credit") from being spell-corrected, even if they look like typos to a general spell checker.
- **Why it's important:** A standard spell checker might try to "correct" "NEFT" to "left" or "PAN" to "pain". This would be a disaster for a banking AI! We need to protect these terms to ensure their meaning is preserved, leading to accurate banking assistance.
  
## How Text Preprocessing Helps Our Use Case
Let's take our example from the previous chapter, "What is my account balance?", but imagine a slightly messier user:

Original User Input: "Hii, pleez tell me my currunt acc balence plz!!"

Here's how preprocessing would clean it up:

Step	Transformation	Result	Explanation
| Step | Transformation | Result | Explanation |
|------|----------------|--------|-------------|
| **Original Query** | — | `"Hii, pleez tell me my currunt acc balance plz!!"` | Raw input from the user. |
| **1. Lowercase Conversion** | All to lowercase | `"hii, pleez tell me my currunt acc balance plz!!"` | Makes `"Hii"` → `"hii"`. |
| **2. Punctuation Removal** | Remove `,`, `!!` | `"hii pleez tell me my currunt acc balance plz"` | Removes noise. |
| **3. Spell Correction** | Correct `"hii"`, `"pleez"`, `"currunt"`, `"balance"` | `"hi please tell me my current acc balance please"` | Fixes common typos. |
| **4. Extra Space Removal** | (Implicit part of cleaning) | `"hi please tell me my current acc balance please"` | Ensures single spaces between words. |
| **Final Processed Query** | — | **"hi please tell me my current acc balance please"** | Ready for the AI to understand the core intent: *account balance inquiry*. |

Notice how the cleaned text is much more standardized and easier for an AI to process reliably.

## What Happens Under the Hood? (Internal Implementation)
Let's see how our Banking AI Assistant performs this crucial preprocessing step.

### The Flow
When you type your question and send it, the process unfolds like this:

<img width="70%" height="502" alt="image" src="https://github.com/user-attachments/assets/daf872a1-8ed8-42d1-ab20-a293e55a611f" />


The [API Gateway & Orchestration](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%202%3A%20API%20Gateway%20%26%20Orchestration.md) calls a dedicated utility, `text_utils.py`, to handle all this cleaning.

The `text_utils.py` File
Our preprocessing logic lives in a file named `text_utils.py`. Let's look at the key parts of the `normalize_text` function within it.

First, we define a list of banking terms that should never be changed:
```
# From text_utils.py
PROTECTED_TERMS = {
    # Core banking & payments
    "neft", "imps", "rtgs", "upi", "atm", "ifsc", "swift",
    "emi", "fd", "rd", "pan", "cvv", "pin", "otp",
    "aadhaar", "aadhar", "kyc", "cibil",
    # ... many more banking terms ...
}
```
**Explanation:** This `PROTECTED_TERMS` set holds words that are critical banking terms. If a user types "neft", we want to ensure it stays "neft" and doesn't get corrected to "left" by a general spell checker. This set acts as a guard against accidental corruption of important financial language.

Now, let's look at the `normalize_text` function itself, broken down into smaller, understandable pieces:
```
# From text_utils.py (inside the normalize_text function)
import re
from spellchecker import SpellChecker

spell = SpellChecker() # Our spell checker tool

def normalize_text(text: str) -> str:
    if not text:
        return "" # Handle empty text gracefully

    # Step 1: Lowercase and strip extra spaces
    text = text.lower().strip()
    # Output Example: "hii, pleez tell me my currunt acc balence plz!!" -> "hii, pleez tell me my currunt acc balence plz!!"
```
**Explanation:** We start by importing necessary tools: re for regular expressions (pattern matching) and `SpellChecker` for correcting typos. The `normalize_text` function takes the user's input text. It first makes everything lowercase (`.lower()`) and removes any extra spaces from the beginning or end (`.strip()`).

```
# From text_utils.py (inside the normalize_text function, continued)
    # Step 2: Remove punctuation and replace with single spaces
    text = re.sub(r"[^\w\s]", " ", text)
    # Output Example: "hii, pleez tell me my currunt acc balence plz!!" -> "hii pleez tell me my currunt acc balence plz  "
```
**Explanation**: Here, `re.sub(r"[^\w\s]", " ", text)` is a powerful line. It finds any character that is not a word character (`\w`) or a whitespace character (`\s`) and replaces it with a single space. This effectively removes all punctuation.

```
# From text_utils.py (inside the normalize_text function, continued)
    # Step 3: Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text)
    # Output Example: "hii pleez tell me my currunt acc balence plz  " -> "hii pleez tell me my currunt acc balence plz"
```
**Explanation**: After removing punctuation, there might be multiple spaces in a row (e.g., "hello there"). This line `re.sub(r"\s+", " ", text)` cleans that up by replacing any sequence of one or more whitespace characters (`\s+`) with a single space.

```
# From text_utils.py (inside the normalize_text function, continued)
    corrected_words = []
    for word in text.split(): # Go through each word
        # Step 4: Protect banking terms from correction
        if word in PROTECTED_TERMS:
            corrected_words.append(word)

        # Step 5: Correct spelling for other words
        elif word.isalpha() and len(word) > 2: # Only correct actual words longer than 2 letters
            corrected_words.append(spell.correction(word) or word)

        # Step 6: Keep numbers or short words as is
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)
    # Output Example: "hii pleez tell me my currunt acc balence plz" -> "hi please tell me my current acc balance please"
```
**Explanation**: This is the heart of the spell correction and protection.

- We loop through each word in the cleaned text.
- `if word in PROTECTED_TERMS:`: If the word is one of our critical banking terms (like "upi" or "pan"), we add it to `corrected_words` without changing it.
- `elif word.isalpha() and len(word) > 2:`: If it's a regular word (contains only letters) and is long enough to be a meaningful word, we use `spell.correction(word) `to try and fix any typos. If spell.correction can't find a better word, it returns `None`, so `or word` ensures we keep the original word.
- **else**: For numbers or very short words, we simply add them as they are.
- Finally, `return " ".join(corrected_words)` combines all the processed words back into a single clean string.
  
### How `main.py` Uses It
The API Gateway & Orchestration calls this normalize_text function right at the beginning of processing a user's request:
```
# From main.py (inside the chatbot function)

    raw_query = (message or "").strip() # This is the original message from the user
    # This calls our Text Preprocessing & Normalization service
    normalized_query = normalize_text(raw_query)

    # ... The AI continues processing with the now clean 'normalized_query' ...
```
**Explanation:** The `raw_query` is your original message. The `normalize_text` function (which we just explored) is called on this raw text, and the result is stored in `normalized_query`. This `normalized_query` is then used for all subsequent steps in the AI's processing pipeline, like Intent Detection.

## Conclusion
You've now seen the powerful, yet often invisible, work of **Text Preprocessing & Normalization**! It's the essential first step that transforms your raw, often messy, input into a clean, consistent format that our AI can confidently understand. By converting to lowercase, removing punctuation, correcting spelling, and critically, protecting banking terms, we ensure the AI starts with the best possible data, setting the stage for accurate and helpful responses.

Now that our text is squeaky clean and standardized, the next logical step is to figure out what you actually want to do with your question. Let's move on to discover how our AI figures out your goal in the next chapter: [Intent Detection](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%204%3A%20Intent%20Detection.md).

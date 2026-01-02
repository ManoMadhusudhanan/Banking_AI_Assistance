from services.llm_engine import smart_llm_reply

def process_banking_query(user_input: str, customer_id: str = None):
    user_input = user_input.lower()

    # Rule-based
    if "balance" in user_input:
        return "Your current account balance is ₹56,420. (sample data)"

    if "transaction" in user_input:
        return (
            "Here are your last 5 transactions:\n"
            "1. -₹500 Grocery\n"
            "2. -₹1200 Fuel\n"
            "3. +₹18,000 Salary\n"
            "4. -₹250 UPI\n"
            "5. -₹1,100 Shopping"
        )

    if "block card" in user_input or "lost card" in user_input:
        return "I can help you block your card immediately. Please confirm whether it's a debit or credit card."

    # AI fallback (OpenAI)
    try:
        return smart_llm_reply(user_input)
    except Exception as e:
        return f"AI system error: {e}"

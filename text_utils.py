from spellchecker import SpellChecker
import re

spell = SpellChecker()

# 🔐 Banking / financial terms that must NEVER be spell-corrected
PROTECTED_TERMS = {
    # Core banking & payments
    "neft", "imps", "rtgs", "upi", "atm", "ifsc", "swift",
    "emi", "fd", "rd", "pan", "cvv", "pin", "otp",
    "aadhaar", "aadhar", "kyc", "cibil",

    # Cards & networks
    "visa", "mastercard", "rupay",
    "credit", "debit",
    "pos", "ecom", "nfc", "tap",

    # Accounts & channels
    "savings", "current", "salary",
    "netbanking", "netbank",
    "mobilebanking", "internetbanking",
    "indie", "bhim", "upiid",

    # Loans & credit
    "loan", "homeloan", "carloan", "goldloan",
    "businessloan", "personalloan",
    "foreclosure", "preclosure", "prepayment",
    "principal", "tenure", "interest",

    # Fees & limits
    "apr", "roi", "slab", "penalty",
    "charges", "fees", "limit", "balance",

    # Statements & compliance
    "statement", "passbook",
    "nominee", "mandate", "nach",
    "ecs", "ach",

    # Identifiers & codes
    "micr", "iban", "bic", "swiftcode"
}
def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    corrected_words = []
    for word in text.split():
        # Do NOT correct protected banking terms
        if word in PROTECTED_TERMS:
            corrected_words.append(word)

        # Safe correction for normal words
        elif word.isalpha() and len(word) > 2:
            corrected_words.append(spell.correction(word) or word)

        else:
            corrected_words.append(word)

    return " ".join(corrected_words)

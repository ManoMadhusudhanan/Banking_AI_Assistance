import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from rag_engine import build_rag_index

build_rag_index(
    os.path.join(BASE_DIR, "Source_Document.docx")
)

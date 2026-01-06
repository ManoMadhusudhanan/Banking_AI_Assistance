# Banking AI Assistant using Hybrid RAG & Graph-RAG
## OVERVIEW:

This project implements an AI-powered Banking Assistant using a hybrid Retrieval-Augmented Generation (RAG) and Graph-RAG architecture, designed to deliver accurate, context-aware, and policy-safe banking responses and OCR (Optical Character Recognition) converts images of text, such as scanned documents or photos, into machine-readable, editable text support to simulate a production-grade banking chatbot.

The system combines semantic document retrieval with relationship-aware knowledge traversal, enabling the assistant to answer both fact-based banking queries (e.g., NEFT, RTGS, KYC, account services) and contextual, multi-step questions that require understanding relationships between banking entities such as accounts, services, processes, and compliance rules.

## WHY NOT GRAPH RAG?

Using only Graph-RAG introduces unnecessary complexity and overhead because:

- Banking knowledge primarily exists as unstructured documents (policies, FAQs, circulars)
- Simple informational queries do not require graph traversal
- Graph-only systems demand strict schema design, entity extraction, and continuous maintenance
- Retrieval latency increases for straightforward questions
- To address this, the system intentionally uses RAG for efficiency and scalability, while Graph-RAG strengthens contextual understanding where relationships matter.

## HYBRID INTELLIGENCE DESGIN

RAG (Retrieval-Augmented Generation) is used to:

- Embed banking documents using Sentence Transformers
- Perform semantic similarity search via cosine similarity
- Retrieve relevant knowledge chunks efficiently
- Ground LLM responses strictly in verified source documents
  
Graph-RAG (Relationship-Aware Retrieval) enhances the assistant by:

- Preserving relationships between banking entities (services, rules, workflows)
- Supporting multi-hop reasoning for follow-up questions
- Improving conversational continuity
- Enabling future integration with knowledge graphs (e.g., Neo4j)
- This layered approach ensures the assistant remains fast, accurate, scalable, and enterprise-ready, while avoiding the pitfalls of a graph-only system.

<img width="1136" height="587" alt="image" src="https://github.com/user-attachments/assets/dec47ad0-5551-4fd9-9828-d42a6c29d8ad" />

CHAPTERS:

[Chapter 1: Frontend User Interface.](Chapter 1: Frontend User Interface./README.md)

API Gateway & Orchestration
Text Preprocessing & Normalization
Intent Detection
Rule-based Banking Logic
Retrieval Augmented Generation (RAG) Engine
Large Language Model (LLM) Integration

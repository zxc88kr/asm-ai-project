# AI Product Engineer — Foreign / Global Company Target Resume

## Daniel Kim | AI Product Engineer

Email: daniel.kim.ai@gmail.com  
GitHub: https://github.com/danielkim-ai  
Portfolio: https://danielkim-ai.dev  
Blog: https://blog.danielkim-ai.dev  
LinkedIn: https://linkedin.com/in/danielkim-ai  

---

## Summary

Entry-level AI Product Engineer with hands-on experience building LLM-powered products, RAG systems, AI workflow automation, and user-facing AI features. Experienced in translating ambiguous user problems into measurable AI product experiments, implementing end-to-end prototypes, and improving response quality, latency, cost, and user experience.

Built and deployed AI applications using Python, FastAPI, React, TypeScript, LangChain, OpenAI API, PostgreSQL, Redis, Docker, and AWS. Strong interest in building trustworthy AI products that combine product thinking, backend engineering, prompt evaluation, retrieval quality, and user feedback loops.

---

## Skills

### AI / LLM

- LLM Applications
- RAG
- Prompt Engineering
- Prompt Evaluation
- Function Calling
- Tool Calling
- LangChain
- LlamaIndex
- OpenAI API
- Claude API
- Hugging Face
- Sentence Transformers
- Embedding Search
- Reranking
- Hallucination Analysis

### Engineering

- Python
- FastAPI
- JavaScript
- TypeScript
- React
- Next.js
- Docker
- GitHub Actions
- AWS EC2
- AWS S3

### Data / Product

- PostgreSQL
- Redis
- Chroma
- FAISS
- Pinecone Basic
- Pandas
- Product Analytics
- User Feedback Loop
- A/B Testing Basic
- Activation Rate
- Retention
- API Cost per User
- Latency Monitoring

---

## Experience

### AI Product Engineer Intern

**PromptWorks AI Korea**  
Jul 2025 - Dec 2025

Worked on an AI productivity SaaS that helps teams search internal documents, summarize meetings, and extract action items from unstructured text.

- Built a RAG-based document Q&A feature using FastAPI, LangChain, OpenAI API, PostgreSQL, and Chroma, improving top-3 retrieval accuracy from 72% to 87%.
- Designed prompt evaluation datasets with 480 real user questions and categorized failures into hallucination, missing context, ambiguous query, and formatting issues.
- Reduced average LLM response latency from 5.1s to 3.0s by optimizing chunk size, retrieval top-k, Redis caching, and streaming responses.
- Decreased estimated monthly LLM API cost by 28% by introducing prompt compression, response caching, and model routing for low-complexity requests.
- Implemented source-grounded answers with document title, page number, chunk ID, and confidence score to improve user trust.
- Collaborated with product managers and designers to redesign AI answer UX, including citation highlights, regeneration controls, and feedback buttons.
- Built a feedback loop that stored thumbs-up/down, edited answers, and failed queries for future prompt and retrieval improvements.
- Refactored prototype-level LangChain code into modular production-style services for retriever, generator, evaluator, and logging.
- Created weekly quality reports that connected AI metrics such as answer relevance and hallucination rate with product metrics such as repeat usage and task completion.

---

## Projects

### AskFlow AI — AI Workspace Assistant

GitHub: https://github.com/danielkim-ai/askflow-ai  
Demo: https://askflow-ai.dev  
Period: Mar 2025 - Jun 2025  
Role: AI Product Engineer

AI assistant that allows users to upload documents, ask questions, generate summaries, and extract structured action items.

- Designed an end-to-end RAG pipeline for PDF, Markdown, and Notion-exported documents using chunking, embedding, vector search, reranking, and grounded answer generation.
- Improved answer relevance from 3.6/5.0 to 4.4/5.0 on a 300-question evaluation dataset by tuning chunk size, overlap, query rewriting, and prompt templates.
- Reduced hallucination rate from 16% to 6% by enforcing source-based answering, confidence thresholds, and refusal behavior when context was insufficient.
- Built a FastAPI backend with document upload, embedding generation, vector indexing, answer generation, feedback collection, and evaluation APIs.
- Implemented a React and TypeScript frontend with document viewer, highlighted citations, answer feedback, and structured summary views.
- Added Redis caching for repeated questions, reducing response time for cached queries by 73%.
- Created an evaluation dashboard to compare prompt versions by answer relevance, groundedness, conciseness, refusal accuracy, latency, and cost.
- Conducted usability tests with 38 beta users and improved the task completion rate from 61% to 78% after redesigning the answer and source navigation UI.

Tech Stack: Python, FastAPI, LangChain, OpenAI API, Chroma, FAISS, PostgreSQL, Redis, React, TypeScript, Docker, AWS EC2

---

### MeetingPilot AI — Meeting-to-Task Automation

GitHub: https://github.com/danielkim-ai/meetingpilot-ai  
Period: Nov 2024 - Feb 2025  
Role: AI Product Engineer

AI workflow tool that converts meeting transcripts into summaries, decisions, action items, owners, due dates, and integrations with Slack and Notion.

- Built an LLM function-calling pipeline that extracted action items, owners, due dates, risks, and follow-up questions into a validated JSON schema.
- Increased action-item extraction accuracy from 74% to 89% through prompt A/B testing, schema validation, and error analysis on 220 meeting samples.
- Implemented Slack and Notion API integrations that allowed users to export extracted tasks directly into existing team workflows.
- Reduced transcript processing failures by adding chunked summarization, retry logic, schema repair, and fallback summaries.
- Tracked export rate, edit rate, deletion rate, and regeneration rate to measure whether AI output was useful in the product flow.
- Improved task export conversion from 38% to 52% after simplifying the review UI and adding inline editing.

Tech Stack: Next.js, TypeScript, Python, FastAPI, OpenAI API, PostgreSQL, Slack API, Notion API, Vercel

---

## Education

### Korea University of Technology — B.S. in Computer Science

Mar 2020 - Feb 2026 expected  
GPA: 4.18 / 4.5

Relevant Coursework:

- Data Structures
- Algorithms
- Database Systems
- Operating Systems
- Computer Networks
- Artificial Intelligence
- Machine Learning
- Natural Language Processing
- Human-Computer Interaction
- Software Engineering

---

## Awards & Activities

### Grand Prize — University AI Service Hackathon

May 2025

- Won grand prize with AskFlow AI, a source-grounded document Q&A product.
- Presented RAG architecture, evaluation methodology, hallucination reduction strategy, and product UX improvements.

### AI Product Study Lead

Sep 2024 - Jun 2025

- Led a 12-member study group on LLM applications, RAG, prompt evaluation, AI agents, and AI product metrics.
- Delivered sessions on retrieval quality, hallucination analysis, product feedback loops, and AI UX.

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner
- Google Analytics Certification
- TensorFlow Developer Certificate, in progress

---

## Keywords

AI Product Engineer, AI Engineer, LLM Application, RAG, Retrieval-Augmented Generation, Prompt Engineering, Prompt Evaluation, LangChain, OpenAI API, Claude API, Vector Database, Embedding Search, FastAPI, React, TypeScript, Product Analytics, AI UX, User Feedback Loop, Latency Optimization, Cost Optimization, Hallucination Reduction
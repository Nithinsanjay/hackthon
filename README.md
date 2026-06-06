🚀 Hackathon Project: AI-Powered Web Scraping & Enrichment System
Description:  
Built an end-to-end pipeline that automates web scraping, structured data enrichment, and deployment. The system extracts relevant company information from websites, enriches it using an LLM, and exposes the results through a FastAPI backend with clean JSON output.

Key Features:

🔎 Scraper Module: Uses requests + BeautifulSoup to fetch and parse website content.

🤖 AI Enrichment: Integrates OpenAI API to transform raw text into structured fields (company name, services, pain points, outreach opener).

⚡ FastAPI Backend: Provides REST endpoints (/enrich, /results) for real-time enrichment and retrieval.

📂 Results Storage: Saves enriched data into results.json for persistence.

🛠️ Deployment Ready: Lightweight, modular design with requirements.txt for easy setup.

Tech Stack:

Python, FastAPI, Uvicorn

Requests, BeautifulSoup4, LXML

OpenAI API (LLM integration)

JSON for structured output

Impact:  
This project demonstrates how AI can be combined with automation to build scalable solutions for lead generation, company profiling, and outreach personalization.

import json
import os
import re

import requests
from bs4 import BeautifulSoup
from openai import OpenAI


SCHEMA = {
    "website_name": "N/A",
    "company_name": "N/A",
    "address": "N/A",
    "mobile_number": "N/A",
    "mail": [],
    "core_service": "N/A",
    "target_customer": "N/A",
    "probable_pain_point": "N/A",
    "outreach_opener": "N/A",
}


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def fixed_schema(data, website_name):
    result = SCHEMA.copy()
    result.update(data or {})
    result["website_name"] = clean(result.get("website_name")) or website_name
    result["mail"] = result["mail"] if isinstance(result.get("mail"), list) else []

    for key in result:
        if key != "mail":
            result[key] = clean(result[key]) or "N/A"

    return result


def scrape_text(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"(?:\+?\d[\d\s().-]{7,}\d)", text)

    return {
        "title": clean(soup.title.string if soup.title else ""),
        "text": text[:6000],
        "emails": sorted(set(emails)),
        "phones": sorted(set(clean(phone) for phone in phones)),
    }


def enrich_company(url, website_name=None):
    website_name = clean(website_name) or url

    try:
        scraped = scrape_text(url)
    except Exception:
        return fixed_schema({"website_name": website_name}, website_name)

    if not os.getenv("OPENAI_API_KEY"):
        return fixed_schema(
            {
                "website_name": website_name,
                "company_name": scraped["title"] or website_name,
                "mobile_number": scraped["phones"][0] if scraped["phones"] else "N/A",
                "mail": scraped["emails"],
                "core_service": scraped["title"] or "N/A",
                "outreach_opener": f"Hi, I reviewed {website_name} and had a quick idea to share.",
            },
            website_name,
        )

    prompt = f"""
Return only JSON with exactly these keys:
{json.dumps(SCHEMA, indent=2)}

Use "N/A" when missing and [] for mail.
Website name: {website_name}
Scraped data: {json.dumps(scraped, indent=2)}
"""

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return fixed_schema(json.loads(response.choices[0].message.content), website_name)
    except Exception:
        return fixed_schema({"website_name": website_name}, website_name)

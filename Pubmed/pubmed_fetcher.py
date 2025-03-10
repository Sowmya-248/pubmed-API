import requests
import pandas as pd
import re
import argparse
import os
from typing import List, Dict, Tuple, Optional
from bs4 import BeautifulSoup

# Constants
PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PHARMA_KEYWORDS = [
    "pharma", "biotech", "therapeutics", "biosciences", "genomics", "biopharma",
    "life sciences", "laboratories", "inc.", "corp", "llc", "gmbh", "s.a.",
    "drug discovery", "biologics", "biomedicine", "diagnostics", "pharmaceutical",
    "clinical research", "medtech", "bioprocessing", "CRISPR"
]

EMAIL_PATTERN = re.compile(r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,6}")

def fetch_paper_ids(query: str, max_results: int = 50, debug: bool = False) -> List[str]:
    """Fetch paper IDs from PubMed based on user query."""
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": max_results}
    response = requests.get(PUBMED_API_URL, params=params)
    response.raise_for_status()
    
    if debug:
        print(f"\n🔍 Debug: API Response JSON (First 500 chars): {str(response.json())[:500]}")

    return response.json().get("esearchresult", {}).get("idlist", [])

def fetch_paper_details(paper_ids: List[str], debug: bool = False) -> List[Dict]:
    """Fetch paper details including authors and affiliations."""
    if not paper_ids:
        return []
    
    params = {"db": "pubmed", "id": ",".join(paper_ids), "retmode": "xml"}
    response = requests.get(PUBMED_FETCH_URL, params=params)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml-xml")

    articles = soup.find_all("PubmedArticle")
    if debug:
        print(f"✅ Debug: Found {len(articles)} articles in XML response.")

    relevant_papers = []
    for article in articles:
        paper_id = article.PMID.text if article.PMID else "Unknown ID"
        title = article.find("ArticleTitle").text if article.find("ArticleTitle") else "Unknown Title"
        pub_date = article.find("PubDate").text if article.find("PubDate") else "Unknown Date"
        
        authors, affiliations = extract_authors_and_affiliations(article)
        company_authors, company_affiliations = filter_company_authors(authors)

        if company_authors:
            relevant_papers.append({
                "PubmedID": paper_id,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": "; ".join(company_authors),
                "Company Affiliation(s)": "; ".join(company_affiliations),
                "Corresponding Author Email": find_corresponding_email(authors)
            })
    
    return relevant_papers

def extract_authors_and_affiliations(article) -> Tuple[List[Dict], List[str]]:
    """Extract authors and their affiliations."""
    authors = []
    affiliations = []
    for author in article.find_all("Author"):
        last_name = author.find("LastName")
        fore_name = author.find("ForeName")
        affiliation = author.find("Affiliation")
        name = f"{fore_name.text} {last_name.text}" if last_name and fore_name else "Unknown Author"
        affil_text = affiliation.text if affiliation else "No Affiliation"
        email = extract_email(affil_text)
        authors.append({"name": name, "affiliation": affil_text, "email": email})
        affiliations.append(affil_text)
    return authors, affiliations

def filter_company_authors(authors: List[Dict]) -> Tuple[List[str], List[str]]:
    """Identify authors affiliated with a pharmaceutical or biotech company."""
    company_authors, company_affiliations = [], []
    for author in authors:
        if any(keyword in author["affiliation"].lower() for keyword in PHARMA_KEYWORDS):
            company_authors.append(author["name"])
            company_affiliations.append(author["affiliation"])
    return company_authors, company_affiliations

def extract_email(text: str) -> Optional[str]:
    """Extract email from text using regex."""
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else "N/A"

def find_corresponding_email(authors: List[Dict]) -> Optional[str]:
    """Find the corresponding author's email."""
    for author in authors:
        if author["email"] != "N/A":
            return author["email"]
    return "N/A"

def save_to_csv(papers: List[Dict], filename: str = "papers.csv", debug: bool = False):
    """Save fetched papers to a CSV file."""
    if not papers:
        print("⚠️ No relevant papers found.")
        return

    save_path = os.path.join(os.getcwd(), filename)
    df = pd.DataFrame(papers)

    # Append instead of overwriting
    if os.path.exists(save_path):
        df.to_csv(save_path, mode='a', header=False, index=False)
    else:
        df.to_csv(save_path, index=False)

    print(f"📁 Results saved to {save_path}")

    if debug:
        print(f"📌 Debug: First 3 rows of saved data:\n{df.head(3)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="PubMed search query")
    parser.add_argument("-f", "--file", type=str, default="papers.csv", help="Filename to save results")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()

    print(f"\n🔎 Searching for papers related to: {args.query}")
    paper_ids = fetch_paper_ids(args.query, max_results=50, debug=args.debug)

    if not paper_ids:
        print("❌ No papers found for the given query.")
    else:
        print(f"✅ Found {len(paper_ids)} papers. Fetching details...")
        papers = fetch_paper_details(paper_ids, debug=args.debug)
        save_to_csv(papers, args.file, debug=args.debug)

    print("\n✅ Done!")


import argparse
from pubmed_fetcher import fetch_paper_ids, fetch_paper_details, save_to_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with non-academic authors.")
    parser.add_argument("query", type=str, help="Search query for PubMed.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("-f", "--file", type=str, help="Output filename (CSV). If not provided, prints to console.")
    args = parser.parse_args()
    
    if args.debug:
        print(f"[DEBUG] Query: {args.query}")
    
    paper_ids = fetch_paper_ids(args.query)
    if not paper_ids:
        print("No papers found.")
        return
    
    papers = fetch_paper_details(paper_ids)
    if not papers:
        print("No relevant papers with non-academic authors found.")
        return
    
    if args.file:
        save_to_csv(papers, args.file)
        print(f"Results saved to {args.file}")
    else:
        from pprint import pprint
        pprint(papers)

if __name__ == "_main_":
    main()
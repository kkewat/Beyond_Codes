import requests
import json

def get_data(url):
    data = []
    while url:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            response_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}",e)
            break
        except requests.exceptions.JSONDecodeError:
            print("Error: Invalid JSON response from API.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}",e)
            break

        page_data = response_data.get("data", {}).get("data", [])
        data.extend(page_data)
        url = response_data.get("data", {}).get("next_page_url")
    #print(data)
    return data

from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def identify_citations(response, sources):
    citations = []
    response_lower = response.lower()
    for source in sources:
        context = source["context"]
        link = source.get("link", "")
        if isinstance(context, str) and similar(context.lower(), response_lower) > 0.2 and link:
            citations.append({"id": source["id"], "link": link})
        elif isinstance(context, list):
            for ctx in context:
                if similar(ctx.lower(), response_lower) > 0.2 and link:
                    citations.append({"id": source["id"], "link": link})
                    break
    return citations

def main():
  url = "https://devapi.beyondchats.com/api/get_message_with_sources"
  all_data = get_data(url)

  citations = []
  for item in all_data:
    response = item["response"]
    sources = item["source"]
    citation = identify_citations(response, sources)
    citations.extend(citation)

  print("Citations:")
  print(citations)
  for citation in citations:
    #print(citation)
    print(f"\tID: {citation['id']}, Link: {citation.get('link', '')}")

if __name__ == "__main__":
  main()

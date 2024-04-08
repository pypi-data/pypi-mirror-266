import difflib 
import requests 
def fetch_webpage(url): 
    try: 
        response = requests.get(url) 
        if response.status_code == 200: 
            return response.text 
        else: 
            print("Failed to fetch webpage:", response.status_code) 
            return None 
    except Exception as e: 
        print("Error fetching webpage:", e) 
        return None 
def compare_similarity(page1_content, page2_content): 
    # Use difflib to compare similarity 
    similarity_ratio = difflib.SequenceMatcher(None, page1_content, page2_content).ratio() 
    return similarity_ratio 
def main(): 
    # URLs of the web pages to compare 
    url1 = "https://en.wikipedia.org/wiki/Computer_science" 
    url2 = "https://en.wikipedia.org/wiki/Information_retrieval" 
    # Fetch content of the web pages 
    page1_content = fetch_webpage(url1) 
    page2_content = fetch_webpage(url2) 
    if page1_content and page2_content: 
    # Compare similarity 
        similarity_ratio = compare_similarity(page1_content, page2_content) 
        print("Similarity ratio:", similarity_ratio) 
    else: 
        print("Failed to fetch content of one or both web pages.") 
    if __name__ == "__main__": 
        main() 
import requests
import base64
import os
from dotenv import load_dotenv

class AzureDevOpsWikiExtractor:
    def __init__(self, organization, project, wiki_identifier, pat):
        base_url = f"https://dev.azure.com/{organization}/{project}/"

        self.base_api_url = f"{base_url}_apis/wiki/wikis/{wiki_identifier}/pagesbatch?api-version=7.1-preview.1"
        self.base_page_url = f"{base_url}_wiki/wikis/{wiki_identifier}/"

        encoded_pat = base64.b64encode(f":{pat}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_pat}",
            "Content-Type": "application/json"
        }

    def get_wiki_page_urls(self):
        """
        Retrieve all wiki pages' URLs.
        """
        page_urls = []
        continuation_token = None

        while True:
            url = self.base_api_url
            if continuation_token:
                url += f"?continuationToken={continuation_token}"
                
            response = requests.post(url, headers=self.headers, json={
                "top": 100
            })
            if response.status_code == 200:
                if response.headers.get('Content-Type').startswith('application/json'):
                    data = response.json()

                    page_urls += [f"{self.base_page_url}{page["id"]}{page["path"]}" for page in data["value"]]
                    
                    continuation_token = response.headers.get('x-ms-continuationtoken')
                    if not continuation_token:
                        break
                else:
                    print("Response is not in JSON format. Response content:", response.text)
                    break
            else:
                print(f"Failed to fetch wiki pages, status code: {response.status_code}")
                break  # Handle errors or implement retry logic as needed

        return page_urls
    
# Usage example
if __name__ == "__main__":
    load_dotenv()

    ORGANIZATION = os.getenv("AZURE_DEVOPS_ORGANIZATION")
    PROJECT = os.getenv("AZURE_DEVOPS_PROJECT")
    WIKI_IDENTIFIER = os.getenv("AZURE_DEVOPS_WIKI_IDENTIFIER")
    PAT = os.getenv("AZURE_DEVOPS_PAT")

    wiki_extractor = AzureDevOpsWikiExtractor(ORGANIZATION, PROJECT, WIKI_IDENTIFIER, PAT)
    urls = wiki_extractor.get_wiki_page_urls()
    for url in urls:
        print(url)
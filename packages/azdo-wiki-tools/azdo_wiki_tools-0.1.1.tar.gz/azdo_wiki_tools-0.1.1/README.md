# Usage Example

```
if __name__ == "__main__":
    ORGANIZATION = "<your organization>"
    PROJECT = "<your project>"
    WIKI_IDENTIFIER = "<your wiki identifier>"
    PAT = os.getenv("AZURE_DEVOPS_PAT")

    wiki_extractor = AzureDevOpsWikiExtractor(ORGANIZATION, PROJECT, WIKI_IDENTIFIER, PAT)
    urls = wiki_extractor.get_wiki_page_urls()
    for url in urls:
        print(url)
```
import os
from ast import literal_eval

import requests
from urllib.parse import urlparse
from config import Config
import json

class PDFSearcherDownloader:
    def __init__(self, api_key=Config.GOOGLE_API_KEY, cse_id=Config.GOOGLE_CSE_ID, download_path="downloads"):
        """
        Initialize the PDFSearcherDownloader.

        :param api_key: Google Search API key.
        :param cse_id: Google Custom Search Engine ID.
        :param download_path: Directory to save downloaded PDFs.
        """
        self.api_key = api_key
        self.cse_id = cse_id
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)

    def search_pdfs(self, query, count=10):
        """
        Search for PDFs using Google Custom Search API.

        :param query: Search query.
        :param count: Number of results to fetch.
        :return: List of PDF URLs.
        """
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": f"{query} filetype:pdf",
            "num": min(count, 10)  # Google API allows a max of 10 results per request
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        file_path = "results.json"
        # Write the JSON data to the file
        with open(file_path, "w") as file:
            json.dump(results, file, indent=4)

        pdf_urls = []
        for item in results.get("items", []):
            pdf_url = item.get("link")
            if pdf_url and pdf_url.endswith(".pdf"):
                pdf_urls.append(pdf_url)

        return pdf_urls

    def download_pdf(self, url):
        """
        Download a PDF from a given URL.

        :param url: URL of the PDF.
        """
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        filepath = os.path.join(self.download_path, filename)

        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)

        print(f"Downloaded: {filepath}")

    def search_and_download(self, inp):
        """
        Search and download PDFs for a given query.

        :param query: Search query.
        :param count: Number of PDFs to download.
        """
        inp=literal_eval(inp)
        query = inp["query"]
        count = inp["count"]
        pdf_urls = self.search_pdfs(query, count)

        for url in pdf_urls:
            try:
                self.download_pdf(url)
            except Exception as e:
                print(f"Failed to download {url}: {e}")
        return str(pdf_urls)
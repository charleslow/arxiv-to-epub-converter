import os
import time
import requests
from typing import Dict, List
import arxiv
import pypandoc
from bs4 import BeautifulSoup
import argparse
from urllib.parse import urljoin, urlparse
import base64
import re
from urllib.parse import quote

INPUT_FILE: str = "arxiv_urls.txt"
OUTPUT_FOLDER: str = "epubs"
AR5IV_BASE_URL: str = "https://ar5iv.labs.arxiv.org/html/"

def fetch_ar5iv_html_and_images(arxiv_id: str, output_folder: str) -> str:
    url: str = f"{AR5IV_BASE_URL}{arxiv_id}"
    response: requests.Response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Create a subdirectory for images
    image_dir = os.path.join(output_folder, f"{arxiv_id}_images")
    os.makedirs(image_dir, exist_ok=True)
    
    # Download images and update their paths in the HTML
    for i, img in enumerate(soup.find_all('img')):
        src = img.get('src')
        if src:
            if src.startswith('data:'):
                # Handle data URLs
                continue
            else:
                # Handle regular URLs
                full_url = urljoin(url, src)
                filename = os.path.basename(urlparse(full_url).path)
                local_path = os.path.join(image_dir, filename)
                
                try:
                    img_response = requests.get(full_url)
                    if img_response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(img_response.content)
                        img['src'] = os.path.abspath(local_path)
                except requests.RequestException:
                    print(f"Failed to download image: {full_url}")
    
    return str(soup)

def generate_epub(html_content: str, output_path: str) -> None:
    # Convert to EPUB using Pandoc with built-in LaTeX to MathML conversion
    pypandoc.convert_text(
        html_content,
        to='epub',
        format='html',
        outputfile=output_path,
        extra_args=[
            '--mathml',
            '--epub-stylesheet=custom.css'
        ]
    )

# Create a custom CSS file for equation styling
custom_css = '''
.math {
    font-size: 1em;
}
'''

with open('custom.css', 'w') as f:
    f.write(custom_css)

def get_arxiv_metadata(arxiv_id: str) -> Dict[str, str]:
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    paper: arxiv.Result = next(client.results(search))
    return {
        'title': paper.title,
        'authors': paper.authors[0].name.split()[-1] if paper.authors else '',
        'year': str(paper.published.year)
    }

def get_output_filename(url: str, output_folder: str) -> str:
    arxiv_id: str = url.split('/')[-1]
    html_content: str = fetch_ar5iv_html_and_images(arxiv_id, output_folder)
    metadata: Dict[str, str] = get_arxiv_metadata(arxiv_id)
    
    filename: str = f"{metadata['authors']} {metadata['year']} - {metadata['title']}"
    filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return os.path.join(output_folder, f"{filename}.epub")

def process_arxiv_url(url: str, output_folder: str) -> None:
    print(f"Processing {url}..")
    arxiv_id: str = url.split('/')[-1]
    html_content: str = fetch_ar5iv_html_and_images(arxiv_id, output_folder)
    output_path: str = get_output_filename(url, output_folder)
    
    generate_epub(html_content, output_path)
    print(f"Generated EPUB: {output_path}")

def process_input_file(input_file: str, output_folder: str):
    if os.path.exists(input_file):
        with open(input_file, 'r') as f:
            urls: List[str] = f.read().splitlines()
        for url in urls:
            if url.strip():
                output_path = get_output_filename(url.strip(), output_folder)
                if os.path.exists(output_path):
                    print(f"Skipping {url} - EPUB already exists: {output_path}")
                else:
                    process_arxiv_url(url.strip(), output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process arXiv URLs to EPUB files.")
    parser.add_argument("-in", "--input", required=True, help="Input file containing arXiv URLs")
    parser.add_argument("-out", "--output", required=True, help="Output folder for EPUB files")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    process_input_file(args.input, args.output)
    print("Finished processing.")

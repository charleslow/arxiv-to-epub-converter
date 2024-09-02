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
import shutil

INPUT_FILE: str = "arxiv_urls.txt"
AR5IV_BASE_URL: str = "https://ar5iv.labs.arxiv.org/html/"
ARXIV_PDF_BASE_URL: str = "https://arxiv.org/pdf/"

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
            '--webtex',
        ]
    )

def download_pdf(arxiv_id: str, pdf_output_path: str) -> None:
    pdf_url = f"{ARXIV_PDF_BASE_URL}{arxiv_id}.pdf"
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(pdf_output_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF: {pdf_output_path}")
    else:
        print(f"Failed to download PDF: {pdf_url}")

def get_arxiv_metadata(arxiv_id: str) -> Dict[str, str]:
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    paper: arxiv.Result = next(client.results(search))
    return {
        'title': paper.title,
        'authors': paper.authors[0].name.split()[-1] if paper.authors else '',
        'year': str(paper.published.year)
    }

def get_output_filename(url: str) -> str:
    arxiv_id: str = url.split('/')[-1]
    metadata: Dict[str, str] = get_arxiv_metadata(arxiv_id)
    filename: str = f"{metadata['authors']} {metadata['year']} - {metadata['title']}"
    filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return filename

def process_arxiv_url(url: str, epub_output_folder: str = None, pdf_output_folder: str = None) -> None:
    print(f"Processing {url}..")
    arxiv_id: str = url.split('/')[-1]
    filename: str = get_output_filename(url)
    
    if epub_output_folder:
        epub_output_path: str = os.path.join(epub_output_folder, f"{filename}.epub")
        if not os.path.exists(epub_output_path):
            html_content: str = fetch_ar5iv_html_and_images(arxiv_id, epub_output_folder)
            generate_epub(html_content=html_content, output_path=epub_output_path)
            print(f"Generated EPUB: {epub_output_path}")
            
            # Cleanup image folder after EPUB generation
            image_dir = os.path.join(epub_output_folder, f"{arxiv_id}_images")
            if os.path.exists(image_dir):
                shutil.rmtree(image_dir)
                print(f"Removed image folder: {image_dir}")
        else:
            print(f"Skipping EPUB generation - file already exists: {epub_output_path}")
    
    if pdf_output_folder:
        pdf_output_path: str = os.path.join(pdf_output_folder, f"{filename}.pdf")
        if not os.path.exists(pdf_output_path):
            download_pdf(arxiv_id=arxiv_id, pdf_output_path=pdf_output_path)
        else:
            print(f"Skipping PDF download - file already exists: {pdf_output_path}")

def process_input_file(input_file: str, epub_output_folder: str = None, pdf_output_folder: str = None):
    if os.path.exists(input_file):
        with open(input_file, 'r') as f:
            urls: List[str] = f.read().splitlines()
        for url in urls:
            if url.strip():
                process_arxiv_url(url.strip(), epub_output_folder, pdf_output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process arXiv URLs to EPUB and/or PDF files.")
    parser.add_argument("-in", "--input", required=True, help="Input file containing arXiv URLs")
    parser.add_argument("--epub-output", help="Output folder for EPUB files (optional)")
    parser.add_argument("--pdf-output", help="Output folder for PDF files (optional)")
    args = parser.parse_args()

    if args.epub_output:
        os.makedirs(args.epub_output, exist_ok=True)
    if args.pdf_output:
        os.makedirs(args.pdf_output, exist_ok=True)
    process_input_file(args.input, args.epub_output, args.pdf_output)
    print("Finished processing.")

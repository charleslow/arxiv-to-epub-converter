# arXiv to EPUB Converter

This project provides a tool to automatically convert arXiv papers to EPUB format. It watches for changes in an input file containing arXiv URLs and generates EPUB files for each paper.

## Features

- Converts arXiv papers to EPUB format
- Watches for changes in the input file and processes new URLs automatically
- Downloads and includes images from the arXiv HTML version
- Handles LaTeX math rendering in the generated EPUBs
- Skips already processed papers to avoid duplication

## Prerequisites

- Docker
- Python 3.10+
- Poetry (for local development)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/charleslow/arxiv-to-epub-converter.git
   cd arxiv-to-epub-converter
   ```

2. Build the Docker image:
   ```
   docker build -t arxiv-to-epub .
   ```

## Usage

1. Create a file named `arxiv_urls.txt` in the project directory and add arXiv URLs, one per line:
   ```
   https://arxiv.org/abs/2104.08653
   https://arxiv.org/abs/2103.14030
   ```

2. Run the Docker container.
   ```
   docker run -v $(pwd)/arxiv_urls.txt:/app/arxiv_urls.txt -v $(pwd)/epubs:/app/epubs arxiv-to-epub
   ```

   This command mounts your local `arxiv_urls.txt` file and `epubs` directory to the container. Note that these folders do not need to be in the project directory, they can be anywhere on your local file system.

3. The script will start watching for changes in `arxiv_urls.txt`. When new URLs are added, it will process them and generate EPUB files in the `epubs` directory.

# arXiv to EPUB Converter

This project provides a tool to automatically convert arXiv papers to EPUB format. It watches for changes in an input file containing arXiv URLs and generates EPUB files for each paper.

## Features

- Converts arXiv papers to EPUB format
- Optionally downloads PDFs of arXiv papers
- Watches for changes in the input file and processes new URLs automatically
- Downloads and includes images from the arXiv HTML version
- Handles LaTeX math rendering in the generated EPUBs
- Skips already processed papers to avoid duplication

## Prerequisites

- Docker

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

## Add to systemd

To run the arXiv to EPUB converter as a systemd service, follow these steps:

1. Create a systemd service file:

   ```sh
   sudo vi /etc/systemd/system/arxiv-to-epub.service
   ```

2. Add the following content to the service file:

   ```ini
   [Unit]
   Description=ArXiv to EPUB Docker Container
   Requires=docker.service
   After=docker.service

   [Service]
   Restart=always
   StandardOutput=journal
   StandardError=journal
   ExecStartPre=-/usr/bin/docker rm -f arxiv-to-epub
   ExecStart=/usr/bin/docker run --rm \
       -v /path/to/your/arxiv_urls.txt:/app/arxiv_urls.txt \
       -v /path/to/your/epubs:/app/epubs \
       -v /path/to/your/pdfs:/app/pdfs \
       arxiv-to-epub
   ExecStop=/usr/bin/docker stop arxiv-to-epub

   [Install]
   WantedBy=multi-user.target
   ```

3. Reload the systemd daemon to recognize the new service:

   ```sh
   sudo systemctl daemon-reload
   ```

4. Enable the service to start on boot:

   ```sh
   sudo systemctl enable arxiv-to-epub
   ```

5. Start the service:

   ```sh
   sudo systemctl start arxiv-to-epub
   ```

6. Check the status of the service to ensure it is running:

   ```sh
   sudo systemctl status arxiv-to-epub
   ```

This will set up the arXiv to EPUB converter to run as a systemd service, automatically starting on boot and restarting if it fails.

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./

# Install project dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the main script
COPY main.py main.sh ./

# Create input and output directories with default names
RUN mkdir epubs && mkdir pdfs && touch arxiv_urls.txt

# Run the script with default values
CMD bash main.sh --input ./arxiv_urls.txt --epub-output ./epubs/ --pdf-output ./pdfs/

#!/usr/bin/env bash
# Render build script

set -o errexit  # exit on error

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download required NLTK data
python -m nltk.downloader punkt stopwords wordnet vader_lexicon

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Run the vector database setup
# python3 src/vector_database.py --prepare-data
python3 src/vector_database.py --setup-pinecone
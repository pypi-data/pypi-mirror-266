
---

# RAG-X Library

## Overview

RAG-X is a comprehensive library designed to optimize Retrieval-Augmented Generation (RAG) processes. It provides a suite of tools to automatically determine the best parameters for processing specific documents. This includes selecting appropriate chunking techniques, embedding models, vector databases, and Language Model (LLM) configurations.

### Key Features:
- **Adaptive Chunking:** Incorporates four advanced text chunking methodologies to enhance the handling of diverse document structures.
  - Specific Text Splitting
  - Recursive Text Splitting
  - Sentence Window Splitting
  - Semantic Window Splitting
- **Expandability:** Future versions will introduce additional chunking strategies and enhancements based on user feedback and ongoing research.
- **Compatibility:** Designed to seamlessly integrate with a wide range of embedding models and vector databases.

## Getting Started

### Installation

To get started, install the test_RAG_X library using the following command:

```bash
pip install test-RAG-X
```

To verify the installation and view library details, execute:

```bash
pip show test_RAG_X
```

### Setting Up Your Environment

Before diving into the functionality of test-RAG-X, ensure that your environment variables are properly configured with your OpenAI API key and your Hugging Face token:

```python
import os

os.environ['OPENAI_API_KEY'] = "YOUR_OPENAI_API_KEY"
os.environ['HF_TOKEN'] = "YOUR_HUGGINGFACE_TOKEN"
```

## Usage

The following steps guide you through the process of utilizing the test-RAG-X library to optimize your RAG parameters:

```python
from test_RAG_X.prag import parent_class

# Specify the path to your PDF document
file_path = "PATH_TO_YOUR_PDF_FILE"

# Initialize the RAG-X instance
my_instance = parent_class(file_path)

# Generate the optimal RAG parameters for your document
score_card = my_instance.get_best_param()

# Output the results
print(score_card)
```


## Set parameters

If you wish to analyse the performance of your parameters, you can pass the parameters as below:
```python
kwarg = {
        'number_of_questions': 5, # Number of questions: type(int)
        'chunk_size': 250, # Chunk size: type(int)
        'chunk_overlap': 0, # Chunk overlap size: type(int)
        'separator': '',  # Separator to be used for chunking if any, type(str)
        'strip_whitespace': False, # Strip white space, type(bool)
        'sentence_buffer_window': 3, # Sentence Buffer window, type(int) 
        'sentence_cutoff_percentile': 80, # Sentence chunk split percentile for spliting context, type(int), range(1,100)
        }

# Specify the path to your PDF document
file_path = "PATH_TO_YOUR_PDF_FILE"

# Initialize the RAG-X instance
my_instance = parent_class(file_path, **kwargs)

# Generate the optimal RAG parameters for your document
score_card = my_instance.get_best_param()

# Output the results
print(score_card)
```

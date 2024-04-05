
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

### Prerequisites

Due to existing dependency conflicts, it is crucial to install the required dependencies before using the RAG-X library. We are actively working on a resolution and appreciate your understanding.

```bash
pip install tiktoken chromadb trulens-eval 'unstructured[pdf]' openai -q
```

### Installation

After resolving the dependencies, install the RAG-X library using the following command:

```bash
pip install -i https://test.pypi.org/simple/ RAG-X -q
```

To verify the installation and view library details, execute:

```bash
pip show RAG-X
```

### Setting Up Your Environment

Before diving into the functionality of RAG-X, ensure that your environment variables are properly configured with your OpenAI API key and your Hugging Face token:

```python
import os

os.environ['OPENAI_API_KEY'] = "YOUR_OPENAI_API_KEY"
os.environ['HF_TOKEN'] = "YOUR_HUGGINGFACE_TOKEN"
```

## Usage

The following steps guide you through the process of utilizing the RAG-X library to optimize your RAG parameters:

```python
from RAG_X.prag import parent_class

# Specify the path to your PDF document
file_path = "PATH_TO_YOUR_PDF_FILE"

# Initialize the RAG-X instance
my_instance = parent_class(file_path)

# Generate the optimal RAG parameters for your document
score_card = my_instance.get_best_param()

# Output the results
print(score_card)
```


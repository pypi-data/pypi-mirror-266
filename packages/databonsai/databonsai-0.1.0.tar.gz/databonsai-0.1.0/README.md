# databonsai

clean &amp; curate your data with LLMs.
![databonsai logo](https://raw.githubusercontent.com/databonsai/databonsai/main/logo.png)

[![PyPI version](https://badge.fury.io/py/databonsai.svg)](https://badge.fury.io/py/databonsai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/databonsai.svg)](https://pypi.org/project/databonsai/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

databonsai is a Python library that leverages Large Language Models (LLMs) to
perform data cleaning, transformation, and categorization tasks. It provides a
set of tools and utilities to simplify the process of working with LLMs and
integrating them into your data pipelines.

## Features

-   Categorization of data into predefined categories using LLMs
-   Transformation of data based on custom prompts and schemas
-   Decomposition of data into structured formats using LLMs
-   Retry logic with exponential backoff for handling rate limits and transient
    errors
-   Pydantic-based validation and configuration management

## Installation

You can install databonsai using pip:

```bash
pip install databonsai
```

## Usage

#!/usr/bin/env python3
"""

Script to extract tables from pdfs or image files. This will be piped through the textract 

"""
import os
import sys
import json
import tempfile
import click

from llmsdk.lib.extractors import extract_text_from_file

@click.group()
def process():
    """
    Extract images/text from documents
    """

@process.command()
@click.argument("filename")
@click.argument("output")
@click.option("--provider",
              default="aws",
              help="Extractor implementation to use")
def extract(filename, output, provider):
    """
    Extract tables from filename

    PDF and imag formats supported
    """

    allresults = extract_text_from_file(filename, provider)
    
    with open(output, 'w') as fd:
        fd.write(json.dumps(allresults, indent=4))
    print(f"Output is in {output}")

def main():
    process()

if __name__ == "__main__":
    main()


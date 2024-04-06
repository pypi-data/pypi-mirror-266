"""
This module provides functions to convert a PDF to text.

Here you can type more detailed explanation.
"""
from pathlib import Path


class Converter:
    """
    A simple converter to convert PDFs to text.
    """

    def convert(self, path):
        """
        Convert the given PDF to text.

        Here you can type more detailed explanation.

        Parameters:
        path (str): The path to a PDF file.

        Returns:
        str: The content of the PDF file as text.
        """
        actual_path = Path(path)

        with open(actual_path, "r", encoding="utf-8") as text:
            print(text)

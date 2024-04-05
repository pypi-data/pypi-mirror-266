from unstructured.cleaners.core import (
    replace_unicode_quotes,
    clean,
    clean_bullets,
    clean_dashes,
    clean_extra_whitespace,
    clean_non_ascii_chars,
    clean_ordered_bullets,
    clean_postfix,
    clean_prefix,
    clean_trailing_punctuation,
    group_broken_paragraphs,
    remove_punctuation,
    replace_unicode_quotes,
)
from unstructured.partition.html import partition_html
from unstructured.documents.elements import Text




class TextCleaner():

    def __init__(self, uncleaned_text:str):
        self.uncleaned_text = uncleaned_text

    def unstructured_text(self):
        """
        Clean the unstructured text by applying all the cleaning operations.

        Args:
            uncleaned_text (str): The unstructured text to be cleaned.

        Returns:
            str: The cleaned text.
        """
        # Creating an element from the text
        text = self.uncleaned_text
        element = Text(text)

        # Applying all available operations
        element.apply(replace_unicode_quotes)
        # element.apply(bytes_string_to_string)
        element.apply(clean)
        element.apply(clean_bullets)
        element.apply(clean_dashes)
        element.apply(clean_extra_whitespace)
        element.apply(clean_non_ascii_chars)
        element.apply(clean_ordered_bullets)
        element.apply(lambda text: clean_postfix(text, r"(END|STOP)", ignore_case=True))
        element.apply(lambda text: clean_prefix(text, r"(SUMMARY|DESCRIPTION):", ignore_case=True))
        element.apply(clean_trailing_punctuation)
        element.text = group_broken_paragraphs(element.text)
        # element.text = remove_punctuation(element.text)
        elements = partition_html(text=element.text)
        if elements:
            element = elements[0]  # Considering only the first element

        return element.text

    

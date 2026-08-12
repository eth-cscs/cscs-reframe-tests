import re
import os

class StringUtils:
    """Utility class providing static methods for string manipulation and sanitization."""

    @staticmethod
    def sanitize_for_filename(name: str) -> str:
        """
        Removes characters that are unsafe for filenames.

        Replaces any character that is not alphanumeric, a period, a dash, or an 
        underscore with an underscore.

        Args:
            name (str): The string to be sanitized.

        Returns:
            str: The sanitized string safe for use as a filename.
        """
        # Replace non-alphanumeric/dash/underscore with underscore
        return re.sub(r'[^\w\.\-]', '_', name)

    @staticmethod
    def truncate_template_part(name: str, max_length: int = 50) -> str:
        """
        Truncates a string part while preserving the core identifier.

        Args:
            name (str): The string to truncate.
            max_length (int): Maximum allowed length before truncation. Defaults to 50.

        Returns:
            str: The truncated string with an ellipsis if it exceeded max_length.
        """
        if len(name) <= max_length:
            return name
        return name[:max_length] + "..."

    @staticmethod
    def truncate_filename_int(name: str, max_length: int = 100) -> str:
        """
        Truncates a filename while preserving the file extension.

        Args:
            name (str): The full filename to truncate.
            max_length: Maximum allowed length of the resulting filename. Defaults to 100.

        Returns:
            str: The truncated filename, maintaining the extension and adding an ellipsis.
        """
        base, ext = os.path.splitext(name)
        if len(name) <= max_length:
            return name
        # Ensure we don't over-truncate and break the structure
        new_base_len = max_length - len(ext) - 3
        return base[:new_base_len] + "..." + ext if (new_base_len > 0) else base[:max_length]

    @staticmethod
    def split_name_and_params(test_name: str) -> tuple[str, list[str]]:
        """
        Splits a ReFrame test name into its base name and a list of parameters.

        Example: 'my_test(param1=val1, param2=val2)' -> ('my_test', ['param1=val1', 'param2=val2'])

        Args:
            test_name (str): The full test name string.

        Returns:
            tuple[str, list[str]]: A tuple containing the base name and a list of parameter strings.
        """
        # Assumes params are in parentheses like 'test_name(param1, param2)'
        match = re.search(r'^(.*?)\((.*)\)$', test_name)
        if match:
            base_name = match.group(1)
            params = [p.strip() for p in match.group(2).split(',') if p.strip()]
            return base_name, params
        return test_name, []

    @staticmethod
    def normalize_table_string(text: str) -> str:
        """
        Converts newline characters to HTML <br> tags for Markdown table compatibility.

        Args:
            text (str): The input string containing potential newlines.

        Returns:
            str: The processed string with <br> instead of \n.
        """
        return text.replace("\n", "<br>")

from typing import Callable


class TextFormatter:
    def __init__(self, text: str):
        self.text = text

    def format_transcript(self, formatter_func: Callable[[str], str] = None) -> str:
        """
        Formats the transcript using a formatter function if provided.
        If no formatter function is given, returns the original text.

        :param formatter_func: Optional function to apply custom formatting logic.
        :return: Formatted transcript string.
        """
        try:
            if self.text:
                if formatter_func:
                    formatted_text = formatter_func(self.text)
                else:
                    formatted_text = self.text  # Default to returning the original text
                return formatted_text
            else:
                raise ValueError("No text to format.")
        except ValueError as e:
            return str(e)

    def __str__(self) -> str:
        """
        Returns the string representation of the TextFormatter object.
        """
        return self.text

    def __repr__(self) -> str:
        """
        Returns a more detailed string representation of the object.
        """
        return f"TextFormatter(text={self.text})"

    def __call__(self, formatter_func: Callable[[str], str] = None) -> str:
        """
        Makes the object callable, applying format_transcript as the callable function.

        :param formatter_func: Optional function to apply formatting logic.
        :return: Formatted transcript string.
        """
        return self.format_transcript(formatter_func)

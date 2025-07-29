import datetime
from pathlib import Path
from apa.domain.exceptions import APAError

class ResponseHandler:
    """Application service for handling LLM responses."""

    def __init__(self, file_writer):
        self.file_writer = file_writer

    def generate_filename(self) -> str:
        """Generate a filename with the format: {day}-{month}-{year}-{hours}-{minute}-{AM or PM}.txt"""
        now = datetime.datetime.now()
        hour = now.hour
        am_pm = "AM" if hour < 12 else "PM"

        # Convert to 12-hour format (1-12)
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12  # 0 in 24-hour format is 12 in 12-hour format

        return f"{now.day:02d}-{now.month:02d}-{now.year}-{hour_12:02d}-{now.minute:02d}-{am_pm}.txt"

    def save_response(self, response: str) -> Path:
        """Save the LLM response to a file."""
        filename = self.generate_filename()
        try:
            return self.file_writer.write(filename, response, encoding="utf-8")
        except Exception as e:
            raise APAError(f"Failed to save response: {str(e)}") from e

from pathlib import Path
from typing import Optional
from apa.domain.exceptions import APAError

class FileWriter:
    """Adapter for writing files to the filesystem."""

    def write(
        self,
        filename: str,
        content: str,
        encoding: Optional[str] = None,
        mode: str = "w"
    ) -> Path:
        """Write content to a file."""
        try:
            file_path = Path(filename)
            with file_path.open(mode=mode, encoding=encoding) as f:
                f.write(content)
            return file_path
        except Exception as e:
            raise APAError(f"Failed to write to file {filename}: {str(e)}") from e

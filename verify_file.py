import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileVerifier:
    """
    Simple PDF file verification:
      1. Exists and is .pdf
      2. Has valid PDF magic header
      3. If pikepdf is installed, checks for encryption
    """
    PDF_MAGIC = b"%PDF-"

    @staticmethod
    def check_exists(path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"No such file: {path}")

    @staticmethod
    def check_magic_bytes(path: Path) -> None:
        with open(path, "rb") as f:
            header = f.read(len(FileVerifier.PDF_MAGIC))
        if header != FileVerifier.PDF_MAGIC:
            raise ValueError(f"{path.name} is not a valid PDF (bad header)")

    @staticmethod
    def check_not_encrypted(path: Path) -> None:
        try:
            import pikepdf
        except ImportError:
            logger.debug("pikepdf not installed; skipping encryption check")
            return

        try:
            pdf = pikepdf.open(path)
            if pdf.is_encrypted:
                raise ValueError(f"{path.name} is password‑protected")
        except pikepdf.PasswordError:
            # Raised when PDF is encrypted with a password
            raise ValueError(f"{path.name} is password‑protected")
        except pikepdf.PdfError as e:
            # Non‑encryption structural errors are logged but not fatal
            logger.warning(f"pikepdf error on {path.name} ({e}); skipping encryption check")

    @classmethod
    def verify_pdf(cls, path: Path) -> None:
        """Run all checks; raises on fatal issues."""
        cls.check_exists(path)
        cls.check_magic_bytes(path)
        cls.check_not_encrypted(path)
        logger.info(f"{path.name} passed verification")

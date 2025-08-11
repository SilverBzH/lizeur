import base64
from pathlib import Path
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from mistralai import Mistral, OCRResponse
from dotenv import dotenv_values
import logging

config = dotenv_values("$HOME/.lizeur.env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("lizeur")


class Lizeur:
    def __init__(self):
        if config["MISTRAL_API_KEY"] is None:
            raise ValueError("MISTRAL_API_KEY is not set")
        self.mistral = Mistral(api_key=config["MISTRAL_API_KEY"])
        self.cache_path = (
            Path("$HOME/.cache/lizeur")
            if config["CACHE_PATH"] is None
            else Path(config["CACHE_PATH"])
        )
        self.cache_path.mkdir(parents=True, exist_ok=True)
        # TODO: Add cache for OCR'ed documents

    def _read_document(self, path: Path) -> OCRResponse | None:
        base64_image = self._encode_pdf(path)
        if base64_image is None:
            return None
        ocr_response = self.mistral.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_image}",
            },
            include_image_base64=True,
        )

        return ocr_response

    def _encode_pdf(self, pdf_path: Path) -> str | None:
        """Encode the pdf to base64."""
        try:
            with open(pdf_path, "rb") as pdf_file:
                header = pdf_file.read(4)
                if header != b"%PDF":
                    logger.error(f"encode_pdf: The file {pdf_path} is not a valid PDF file.")
                    return None
                pdf_file.seek(0)

                return base64.b64encode(pdf_file.read()).decode("utf-8")
        except FileNotFoundError:
            logger.error(f"encode_pdf: The file {pdf_path} was not found.")
            return None
        except Exception as e:
            logger.error(f"encode_pdf: {e}", exc_info=True)
            return None


@mcp.tool()
async def read_pdf(pdf_path: str) -> str:
    """Read a PDF file and return the text content."""
    return ""

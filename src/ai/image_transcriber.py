from PIL import Image
import pytesseract
import os
from datetime import datetime
import logging
from typing import Optional, Dict


class ImageTranscriber:
    """Handles OCR processing of images containing handwritten text."""

    def __init__(self, output_dir: str = "data/transcriptions"):
        """
        Initialize the transcriber with output directory.

        Args:
            output_dir (str): Directory to save transcriptions
        """
        self.output_dir = output_dir
        self._setup_logging()
        self._ensure_output_dir()

    def _setup_logging(self):
        """Configure logging for the transcriber."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")

    def transcribe_image(self, image_path: str) -> Optional[Dict[str, str]]:
        """
        Extract text from an image and save the transcription.

        Args:
            image_path (str): Path to the image file

        Returns:
            Optional[Dict[str, str]]: Dictionary containing transcription details or None if failed
        """
        try:
            # Open and process image
            self.logger.info(f"Processing image: {image_path}")
            image = Image.open(image_path)

            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(image)

            if not extracted_text.strip():
                self.logger.warning("No text was extracted from the image")
                return None

            # Create transcription record
            transcription = {
                "original_image": image_path,
                "timestamp": datetime.now().isoformat(),
                "text": extracted_text.strip()
            }

            # Save transcription
            self._save_transcription(transcription)

            self.logger.info("Successfully transcribed image")
            return transcription

        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return None

    def _save_transcription(self, transcription: Dict[str, str]):
        """
        Save transcription to a text file.

        Args:
            transcription (Dict[str, str]): Transcription data to save
        """
        # Create filename based on timestamp
        filename = f"transcription_{transcription['timestamp'].replace(':', '-')}.txt"
        filepath = os.path.join(self.output_dir, filename)

        # Write transcription to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Original Image: {transcription['original_image']}\n")
            f.write(f"Timestamp: {transcription['timestamp']}\n")
            f.write("\nTranscribed Text:\n")
            f.write(transcription['text'])

        self.logger.info(f"Saved transcription to: {filepath}")


def main():
    """Example usage of the ImageTranscriber."""
    transcriber = ImageTranscriber()

    # Example image path
    image_path = "data/writting_examples/images/img_1.jpg"

    if os.path.exists(image_path):
        result = transcriber.transcribe_image(image_path)
        if result:
            print(f"Successfully transcribed image:\n{result['text']}")
        else:
            print("Failed to transcribe image")
    else:
        print(f"Image not found: {image_path}")


if __name__ == "__main__":
    main()

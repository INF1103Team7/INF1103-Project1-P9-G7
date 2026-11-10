# Class to assitst with AI operations with helper functions for image handling and mimetype detection
class AiHelper:
    @staticmethod
    # Get mimetype based on the image filename extension
    def _get_mime_type(filename: str) -> str:
        """_summary_
            Helper function to get mimetype based on the image filename extension
        Args:
            filename (str): Image filename

        Returns:
            str: Mimetype to be passed in AI API request
        """
        extension = filename.lower().rsplit(".", 1)[-1]
        if extension in ["jpg", "jpeg"]:
            return "image/jpeg"
        elif extension == "png":
            return "image/png"
        
        # Universal fallback in case of any unexpected issues
        return "application/octet-stream"

    # Load image bytes from the specified path and create a Part object for the AI API request
    def load_image_part(self, image_path: str):
        """_summary_
            Helper function to load image bytes from the specified path and create a Part object for the AI API request
        Args:
            image_path (str): Path to image file

        Returns:
            bytes: Image bytes to be passed in AI API request
        """
        from pathlib import Path
        from google.genai import types
        try:
            if image_path.find("CASE-") != -1:
                with open(Path(__file__).parent.parent / f"images/{image_path}", "rb") as f:
                    image_bytes = f.read()
            else:
                with open(Path(__file__).parent.parent / f"temp/{image_path}", "rb") as f:
                    image_bytes = f.read()

            contents = types.Part.from_bytes(data = image_bytes, mime_type = self._get_mime_type(image_path))

            print("[+] Image successfully added to prompt!")
            return contents
        # Handle File not found error
        except FileNotFoundError:
            print(f"[!] File {image_path} not found, continuing extraction without image")

        # Handle any other unexpected exceptions
        except Exception as e:
            print(f"[!] Exception occured: {e}")

# Import control
__all__ = ["AiHelper"]

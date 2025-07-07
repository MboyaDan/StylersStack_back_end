import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cloudinary will read config from CLOUDINARY_URL automatically

def upload_image_to_cloudinary(file_obj, filename):
    try:
        result = cloudinary.uploader.upload(
            file_obj,
            public_id=filename,
            folder="fashion-products"
        )
        return result["secure_url"]
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}")
# Ensure Cloudinary is configured
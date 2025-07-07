from firebase_admin import storage
import uuid

def upload_image_to_firebase(image_file, filename: str) -> str:
    bucket = storage.bucket()
    blob = bucket.blob(f"products/{uuid.uuid4()}/{filename}")
    blob.upload_from_file(image_file, content_type=image_file.content_type)
    return blob.public_url  # or use generate_signed_url() if needed

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
import os
from dotenv import load_dotenv
from typing import Union, List
import uuid

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


def upload_images(
    files: Union[UploadFile, List[UploadFile]],
    folder: str = None
) -> Union[str, List[str]]:
    def _upload_single(file: UploadFile) -> str:
        try:
            # Read file content
            file_content = file.file.read()
            file.file.seek(0)  # Reset file pointer

            # Generate unique public_id
            public_id = f"{uuid.uuid4()}_{file.filename.split('.')[0]}"

            # Upload parameters
            upload_params = {
                "public_id": public_id,
                "overwrite": True,
                "resource_type": "image"
            }

            if folder:
                upload_params["folder"] = folder

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file_content, **upload_params)

            return result["secure_url"]

        except Exception as e:
            print(f"Upload failed for {file.filename}: {str(e)}")
            return None

    # Handle single file
    if isinstance(files, UploadFile):
        return _upload_single(files)

    # Handle multiple files
    urls = []
    for file in files:
        url = _upload_single(file)
        if url:  # Only append successful uploads
            urls.append(url)

    return urls

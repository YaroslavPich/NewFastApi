import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from src.settings import CLOUDINARY_API_KEY, CLOUDINARY_SECRET_KEY, CLOUDINARY_NAME


cloudinary.config(
    cloud_name=CLOUDINARY_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_SECRET_KEY,
    secure=True
)

def upload_file_to_cloudinary(file, filename):
    r = cloudinary.uploader.upload(
        file,
        public_id=f'NotesApp/{filename}',
        overwrite=True)
    return cloudinary.CloudinaryImage(
        f'NotesApp/{filename}'
    ).build_url(
        width=250, height=250, crop='fill', version=r.get('version')
    )

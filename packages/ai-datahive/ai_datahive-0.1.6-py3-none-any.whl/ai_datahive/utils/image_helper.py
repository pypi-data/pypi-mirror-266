import base64
import requests

from io import BytesIO
from PIL import Image


def encode_image_url_to_base64(image_url, max_image=512):
    # Das Bild von der URL holen
    response = requests.get(image_url)
    # Sicherstellen, dass die Anfrage erfolgreich war
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        max_dim = max(width, height)
        if max_dim > max_image:
            scale_factor = max_image / max_dim
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height))

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")

import os
import time
from PIL import Image
from io import BytesIO
import base64
import io
import uuid
import piexif
import piexif.helper
from datetime import datetime, timezone
import logging.config
import uvicorn

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

# -------------deoldify imports-------------
from deoldify.visualize import get_image_colorizer
from pathlib import Path
import torch


logger = logging.getLogger(__name__)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_img_path(directory_name):
    current_dir = '/tmp'
    img_directory = current_dir + '/.temp' + directory_name
    os.makedirs(img_directory, exist_ok=True)
    img_file_name = uuid.uuid4().hex[:20] + '.jpg'
    return img_directory + img_file_name


def decode_base64_to_image(img_string):
    img = Image.open(BytesIO(base64.b64decode(img_string)))
    return img


def encode_pil_to_base64(image):
    with io.BytesIO() as output_bytes:
        if image.mode == "RGBA":
            image = image.convert("RGB")
        parameters = image.info.get('parameters', None)
        exif_bytes = piexif.dump({
            "Exif": {piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(parameters or "",
                                                                                encoding="unicode")}
        })
        image.save(output_bytes, format="JPEG", exif=exif_bytes)
        bytes_data = output_bytes.getvalue()
    return base64.b64encode(bytes_data)


@app.post("/ai/api/v1/deoldify_image")
async def deoldify_image(
    image: str = Body("", title="input image"),
    render_factor: int = Body(35, title="render factor"),
    artistic: bool = Body(False, title="artistic")
):
    utc_time = datetime.now(timezone.utc)
    start_time = time.time()
    models_dir = Path(os.path.join(os.path.dirname(os.path.realpath(__name__)), "models"))
    vis = get_image_colorizer(root_folder=models_dir, render_factor=render_factor, artistic=artistic)
    if image.startswith("http"):
        img = vis._get_image_from_url(image)
    else:
        img = Image.open(BytesIO(base64.b64decode(image)))
    outImg = vis.get_transformed_image_from_image(img, render_factor=render_factor)
    # outImg = encode_pil_to_base64(outImg).decode("utf-8")
    out_images_directory_name = '/deoldify_images/'
    out_image_path = get_img_path(out_images_directory_name)
    outImg.save(out_image_path)
    torch.cuda.empty_cache()
    return {
        "success": True,
        "message": "Returned output successfully",
        "server_process_time": time.time() - start_time,
        "output_image_url": '/media' + out_images_directory_name + out_image_path.split('/')[-1]
    }

@app.get("/ai/api/v1/deoldify-server-test")
async def deoldify_server_test():

    return {
        "success": True,
        "message": "Server is OK."
    }


# uvicorn main:app --host 0.0.0.0 --port 8001 --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

'''
Author: SpenserCai
Date: 2023-07-28 14:37:40
version: 
LastEditors: SpenserCai
LastEditTime: 2023-08-09 22:31:43
Description: file content
'''
# DeOldify API
from fastapi import FastAPI, Body

from modules.api.models import *
from modules.api import api
from modules import paths_internal
from scripts.deoldify_base import *
import gradio as gr
from PIL import Image
import time
from datetime import datetime, timezone
import torch

from main import app

import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")
warnings.filterwarnings("ignore", category=UserWarning, message="The parameter 'pretrained' is deprecated since 0.13 and may be removed in the future, please use 'weights' instead.")
warnings.filterwarnings("ignore", category=FutureWarning, message="Arguments other than a weight enum or `None`.*?")


@app.post("/sdwebui/ai/deoldify/image")
async def deoldify_image(
    input_image: str = Body("",title="image input"),
    render_factor: int = Body(35,title="render factor"),
    artistic: bool = Body(False,title="artistic")
):
    utc_time = datetime.now(timezone.utc)
    start_time = time.time()
    vis = get_image_colorizer(root_folder=Path(paths_internal.models_path),render_factor=render_factor, artistic=artistic)
    # 判断input_image是否是url
    if input_image.startswith("http"):
        img = vis._get_image_from_url(input_image)
    else:
        # 把base64转换成图片 PIL.Image
        img = Image.open(BytesIO(base64.b64decode(input_image)))
    outImg = vis.get_transformed_image_from_image(img, render_factor=render_factor)
    # return {"image": api.encode_pil_to_base64(outImg).decode("utf-8"), "server_process_time": time.time()-start_time}
    outImg = api.encode_pil_to_base64(outImg).decode("utf-8")
    torch.cuda.empty_cache()
    return {
        "image": outImg,
        "server_hit_time": str(utc_time),
        "server_time": time.time() - start_time
    }


import json
import requests
import time
import re
import threading
import random
import os
import shutil
import configparser

config = configparser.ConfigParser()
config["config"] = {
    "gpt_url": os.environ.get("GPT_URL", ""),
    "gpt_key": os.environ.get("GPT_KEY", ""),
    "draw_key": os.environ.get("DRAW_KEY", "")
}
with open("config.ini", "w") as configfile:
    config.write(configfile)

config.read('config.ini')

base_url = config.get("config", "gpt_url")
threads = []
online_draw_key = config.get("config", "draw_key")
url = "https://cn.tensorart.net/v1/jobs"
tams_headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {online_draw_key}"
}
pic_url_list = []
key = config.get("config", "gpt_key")
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

config = configparser.ConfigParser()
config.read('config.ini')


def zip_folder(name):
    output_filename = os.path.splitext(name)[0]
    shutil.make_archive(output_filename, 'zip', name)


def extract_python_code(markdown_text, word):
    pattern = re.compile(rf"```{word}\s+(.*?)```", re.DOTALL)
    match = pattern.search(markdown_text)
    return match.group(1) if match else None


def online_generate(prompt, mode, width, height):
    model = "757279507095956705"
    requests_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    if mode == "static":
        height = int(height)
        width = int(width)
        if min(height, width) < 512:
            if height < width:
                width = int((512 / height) * width)
                height = 512
            else:
                height = int((512 / width) * height)
                width = 512
    else:
        width = 1152
        height = 768

    tams_data = {
        "request_id": str(requests_id),
        "stages": [
            {
                "type": "INPUT_INITIALIZE",
                "inputInitialize": {
                    "seed": -1,
                    "count": 1
                }
            },
            {
                "type": "DIFFUSION",
                "diffusion": {
                    "width": width,
                    "height": height,
                    "prompts": [{"text": prompt}],
                    "steps": 30,
                    "sdVae": "vae-ft-mse-840000-ema-pruned.ckpt",
                    "sd_model": model,
                    "clip_skip": 2,
                    "cfg_scale": 1,
                    "clipEncoderName": "t5xxl_fp16.safetensors",
                    "lora": {
                        "items": [
                            {
                                "loraModel": "765053307455602351",
                                "weight": 1
                            }
                        ]
                    }
                }
            },
        ]
    }
    if mode == "static":
        del tams_data["stages"][1]["diffusion"]["lora"]
    response = requests.post(url, headers=tams_headers, data=json.dumps(tams_data))

    if response.status_code == 200:
        id = json.loads(response.text)['job']['id']
        return id
    else:
        print(f"请求失败，状态码：{response.status_code}，请检查是否正确填写了key")


def get_result(job_id, name, mode):
    while True:
        time.sleep(1)
        response = requests.get(f"{url}/{job_id}", headers=tams_headers)
        get_job_response_data = json.loads(response.text)
        if 'job' in get_job_response_data:
            job_dict = get_job_response_data['job']
            job_status = job_dict.get('status')
            if job_status == 'SUCCESS':
                url2 = job_dict["successInfo"]["images"][0]["url"]
                response = requests.get(url2)
                pic_url_list.append(url2)
                if mode == "static":
                    os.makedirs(os.path.dirname(fr'{name}.png'), exist_ok=True)
                    with open(fr'{name}.png', 'wb') as f:
                        f.write(response.content)
                else:
                    with open(fr'page/{job_id}.png', 'wb') as f:
                        f.write(response.content)
                break
            elif job_status == 'FAILED':
                break


def generate_image_pro(prompt, name, mode, width, height):
    pic_id = online_generate(prompt, mode, width, height)
    get_result(pic_id, name, mode)


def gpt(system, prompt, mode="default"):
    global base_url
    model = "chatgpt-4o-latest"
    response_format = {'type': 'json_object'} if mode != "default" else {}

    payload = json.dumps({
        "model": model,
        **({"response_format": response_format} if response_format else {}),
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = requests.request("POST", base_url, headers=headers, data=payload)
    parsed_data = json.loads(response.text)
    content = parsed_data['choices'][0]['message']['content']
    return content


def gpt_pic(pic_url):
    global base_url

    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "你是前端专家，可以帮我把图片转前端页面,图片中的文字有些乱码，请你修改为合理的单词文字,如果页面有图片则名字是-合理的英文名.png来代替,"
                           "图片的细节都要全部还原，包括圆角和页面布局那些"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "帮我转成前端页面,html和css要分离"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": pic_url,
                        },
                    },
                ]
            }
        ]
    })

    response = requests.request("POST", base_url, headers=headers, data=payload)
    parsed_data = json.loads(response.text)
    content = parsed_data['choices'][0]['message']['content']
    return content


def start_online_draw_threads(prompt, name, mode, width, height):
    global threads
    thread = threading.Thread(target=generate_image_pro, args=(prompt, name, mode, width, height))
    thread.start()
    threads.append(thread)


def merge_html_css(html_file, css_file, output_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    with open(css_file, 'r', encoding='utf-8') as file:
        css_content = file.read()

    merged_content = html_content.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>\n{css_content}\n</style>'
    )
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(merged_content)

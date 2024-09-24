import json
import requests
import time
import random
import re
import threading
import tqdm
import math
import random
import os
import shutil

threads = []
online_draw_key = "0d2977d8d84048f5a8102fdd5c7ddd1d"
url = "https://cn.tensorart.net/v1/jobs"
tams_headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {online_draw_key}"
}
pic_url_list = []
key = "sk-Lf7dN6r59Dv9KvHM4b353a777a6247F7Bd4729C6B0E87a28"
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}


def zip_folder(name):
    output_filename = os.path.splitext(name)[0]

    # 使用 shutil.make_archive 来打包文件夹
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
    id = online_generate(prompt, mode, width, height)
    get_result(id, name, mode)


def gpt(system, prompt, mode="default"):
    url = "https://api.bltcy.ai/v1/chat/completions"
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

    response = requests.request("POST", url, headers=headers, data=payload)
    parsed_data = json.loads(response.text)
    content = parsed_data['choices'][0]['message']['content']
    return content


def gpt2(pic_url):
    url = "https://api.bltcy.ai/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "你是前端专家，可以帮我把图片转前端页面,图片中的文字有些乱码，请你修改为合理的单词文字,如果页面有图片则名字是-合理的英文名.png来代替"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "帮我转成前端页面,html和css分离"},
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

    response = requests.request("POST", url, headers=headers, data=payload)
    parsed_data = json.loads(response.text)
    print(pic_url)
    print(parsed_data)
    content = parsed_data['choices'][0]['message']['content']
    return content


def start_online_draw_threads(prompt, name, mode, width, height):
    global threads
    thread = threading.Thread(target=generate_image_pro, args=(prompt, name, mode, width, height))
    thread.start()
    threads.append(thread)


def progress_bar(duration, threads=None):
    with tqdm.tqdm(total=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} %', colour="white") as pbar:
        start_time = time.time()
        elapsed_time = 0
        progress = 0

        while elapsed_time < duration:
            elapsed_time = time.time() - start_time

            if progress < 83:
                progress = min(83, int(100 * math.log1p(elapsed_time) / math.log1p(duration)))
                pbar.n = progress
                pbar.refresh()

            time.sleep(0.2)

        if progress < 83:
            pbar.n = 83
            pbar.refresh()

        for thread in threads:
            thread.join()

        pbar.n = 100
        pbar.refresh()


def merge_html_css(html_file, css_file, output_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # 读取CSS文件
    with open(css_file, 'r', encoding='utf-8') as file:
        css_content = file.read()

    # 替换<link>标签为<style>标签，并插入CSS内容
    merged_content = html_content.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>\n{css_content}\n</style>'
    )
    # 将合并后的内容写入输出文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(merged_content)


def main():
    start_time = time.time()
    user_prompt = input("请输入希望的前端页面")
    print("提示词生成中...")
    prompt = gpt(
        "你是一个前端prompt优化大师，根据我给的描述生成详细的英文prompt,比较简短不要分段，不要使用markdown语法，只需要说前端页面的图像描述就行，你的描述中必须提到这是一个网络页面",
        user_prompt)
    print("prompt:", prompt)
    while True:
        for _ in range(4):
            start_online_draw_threads(
                prompt + "only one page and it's windows page,The front-end page is positive and full of "
                         "images", None, "default", None, None)
        progress_bar(duration=120, threads=threads)
        print("图片生成完成！")
        pic_id = str(input("请输入你想要做成前端的图片id(输入r重新生成图片):"))
        if pic_id != "r":
            print("图片正在重新生成...")
            break
    print("页面分析中...")
    data = gpt2(my_dict[pic_id])
    html = extract_python_code(data, "html")
    css = extract_python_code(data, "css")
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(html)
    with open('styles.css', 'w', encoding='utf-8') as file:
        file.write(css)
    print("分析完成！html与css文件已写入")
    png_json = gpt(
        "找出html里面所有的png图片，给这个图片合适的大小(一定要给一个数字)，返回json格式{'images':[{'pic_name':'图片的名字.png','describe':'图片英文的描述',"
        "'width':'图片在html中的宽度像素(纯数字)','height':'图片在html中的高度像素(纯数字)'}，{以此类推...}]}",
        html + css,
        mode="json")
    print(png_json)
    png_json = json.loads(png_json)['images']
    for obj in png_json:
        start_online_draw_threads(obj['describe'], obj['pic_name'].removesuffix(".png"), "static", obj['width'],
                                  obj['height'])
    progress_bar(duration=60, threads=threads)
    end_time = time.time()
    print(f"执行耗时：{end_time - start_time}秒")

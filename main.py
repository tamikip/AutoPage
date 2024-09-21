import json
import requests
import time
import random
import re
import threading
import tqdm
import numpy as np

threads = []
online_draw_key = "xxx"
url = "https://cn.tensorart.net/v1/jobs"
tams_headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {online_draw_key}"
}
my_dict = {}
key = "xxx"
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}


def extract_python_code(markdown_text, word):
    pattern = re.compile(rf"```{word}\s+(.*?)```", re.DOTALL)
    match = pattern.search(markdown_text)
    return match.group(1) if match else None


def online_generate(prompt, mode, width, height):
    model = "757279507095956705"
    requests_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    if mode == "static":
        if min(height, width) < 512:
            if height < width:
                height = 512
                width = int((512 / height) * width)
            else:
                width = 512
                height = int((512 / width) * height)
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
                    "sdVae": "animevae.pt",
                    "sd_model": model,
                    "clip_skip": 2,
                    "cfg_scale": 3,
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
                my_dict[job_id] = url2
                if mode == "static":
                    with open(fr'{name}.png', 'wb') as f:
                        f.write(response.content)
                else:
                    with open(fr'{job_id}.png', 'wb') as f:
                        f.write(response.content)
                break
            elif job_status == 'FAILED':
                break


def generate_image_pro(prompt, name, width, height, mode):
    id = online_generate(prompt, mode, width, height)
    get_result(id, name, mode)


def gpt(system, prompt, mode="default"):
    url = "xxx"
    if mode == "default":
        payload = json.dumps({
            "model": "chatgpt-4o-latest",
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
    else:
        payload = json.dumps({
            "model": "chatgpt-4o-latest",
            "response_format": {'type': 'json_object'},
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
    url = "xxx"

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
                progress = min(83, int(100 * np.log1p(elapsed_time) / np.log1p(duration)))
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


start_time = time.time()
user_prompt = input("请输入希望的前端页面")
print("提示词生成中...")
prompt = gpt(
    "你是一个prompt优化大师，根据我给的描述生成详细的英文prompt,比较简短不要分段，不要使用markdown语法，只需要说前端页面的图像描述就行",
    user_prompt)
print("prompt:", prompt)
for _ in range(4):
    start_online_draw_threads(prompt + "only one page and it's windows page,The front-end page is positive and full of "
                                       "images", None, "default", None, None)
progress_bar(duration=120, threads=threads)
print("图片生成完成！")
pic_id = str(input("请输入你想要做成前端的图片id:"))
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
    start_online_draw_threads(obj[0]['pic_name'], obj[0]['describe'], "static", obj[0]['width'], obj[0]['height'])
progress_bar(duration=120, threads=threads)
end_time = time.time()
print(f"执行耗时：{end_time - start_time}秒")

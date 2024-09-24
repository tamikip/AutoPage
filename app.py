from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from main import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/handle-image-click', methods=['POST'])
def handle_image_click():
    global page_id
    page_id = str(random.randint(10 ** 11, 10 ** 12 - 1))
    data = request.get_json()
    image_url = data.get('imageUrl')
    data = gpt2(image_url)
    html = extract_python_code(data, "html")
    css = extract_python_code(data, "css")
    os.makedirs(page_id)
    with open(f'{page_id}/index.html', 'w', encoding='utf-8') as file:
        file.write(html)
    with open(f'{page_id}/styles.css', 'w', encoding='utf-8') as file:
        file.write(css)
    merge_html_css(f'{page_id}/index.html', f'{page_id}/styles.css', f"{page_id}/full_index.html")
    png_json = gpt(
        "找出html里面所有的png图片，给这个图片合适的大小(一定要给一个数字)，返回json格式{'images':[{'pic_name':'图片的名字.png','describe':'图片英文的描述',"
        "'width':'图片在html中的宽度像素(纯数字)','height':'图片在html中的高度像素(纯数字)'}，{以此类推...}]}",
        html + css,
        mode="json")
    png_json = json.loads(png_json)['images']
    for obj in png_json:
        start_online_draw_threads(obj['describe'], f'{page_id}/{obj["pic_name"]}'.removesuffix(".png"), "static",
                                  obj['width'],
                                  obj['height'])
    for thread in threads:
        thread.join()

    return jsonify({'status': 'success', 'message': 'Image processing completed successfully!', 'imageUrl': image_url,
                    'page_id': page_id})


@app.route('/submit-textarea', methods=['POST'])
def submit_textarea():
    data = request.get_json()
    page_prompt = data.get('textareaContent')
    pic_url_list.clear()
    for _ in range(4):
        start_online_draw_threads(
            page_prompt + "only one page and it's windows page,The front-end page is positive and full of "
                          "images", None, "default", None, None)
    for thread in threads:
        thread.join()
    return jsonify({'pic_url_list': pic_url_list})


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    user_input = data.get('userInput')
    result = gpt(
        "你是一个前端prompt优化大师，根据我给的描述生成详细的英文·prompt,比较简短不要分段，不要使用markdown语法，只需要说前端页面的图像描述就行，你的描述中必须提到这是一个网络页面",
        user_input)
    return jsonify({'message': result})


@app.route('/preview/<page_id>')
def preview(page_id):
    return send_from_directory(page_id, 'full_index.html')


@app.route('/download/<page_id>', methods=['POST'])
def download_file(page_id):
    zip_folder(page_id)

    try:
        return send_file(f'{page_id}.zip', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

# AutoPage
![AI前端生成器.png](https://img.picui.cn/free/2024/09/25/66f3baad0737f.png)
AutoPage 是一个基于 AI 的工具，能够通过用户输入的提示生成图像，并将图像自动转换为前端网页。该项目使用了多种 AI 模型来生成图像、处理网页布局，并优化最终的网页展示效果。
## 功能特点

- **图像生成**: 通过提示生成高质量的FLUX图像。
- **图像转网页**: 自动将生成的图像转换为前端网页，支持 HTML 和 CSS 分离。
- **网页布局优化**: 使用 AI 自动优化生成的网页布局，使其更加美观。
- **可在线预览**: 可以在线预览生成的网页效果
- **文件打包下载**: 支持将生成的网页打包为 ZIP 文件供下载。
- - **文件隔离**: 自动隔离不同的任务文件

## 依赖

在运行本项目之前，请确保安装以下依赖：

```bash
pip install flask requests configparser
```

## 配置文件

项目使用 `config.ini` 文件来读取必要的配置信息。请确保 `config.ini` 文件包含以下内容：

```ini
[config]
gpt_url = <your_gpt_api_url>
draw_key = <your_draw_api_key>
gpt_key = <your_gpt_api_key>
```

## 快速开始

1. 克隆项目：

```bash
git clone https://github.com/tamikip/AutoPage.git
cd AutoPage
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置 `config.ini` 文件，填写你的 API 密钥和相关信息。

4. 运行项目：

```bash
python app.py
```

5. 打开浏览器访问 `http://127.0.0.1:5000`，使用图形界面生成图像并自动生成网页。

## API 端点

### 1. `/submit-textarea` (POST)
通过用户输入的提示生成图像。

**请求体示例：**

```json
{
  "textareaContent": "A beautiful sunset over the mountains"
}
```

**响应示例：**

```json
{
  "pic_url_list": [
    "https://example.com/image1.png",
    "https://example.com/image2.png"
  ]
}
```

### 2. `/handle-image-click` (POST)
处理用户点击图像的请求，并生成对应的网页。

**请求体示例：**

```json
{
  "imageUrl": "https://example.com/image.png"
}
```

**响应示例：**

```json
{
  "status": "success",
  "message": "Image processing completed successfully!",
  "page_id": "1234567890"
}
```

### 3. `/preview/<page_id>` (GET)
预览生成的网页。

**请求示例：**

```bash
GET /preview/1234567890
```

### 4. `/download/<page_id>` (POST)
下载生成的网页打包文件。

**请求示例：**

```bash
POST /download/1234567890
```

## 文件结构

```
ArtPromptAI/
│
├── app.py                  # 主应用文件
├── utils.py                # 工具函数
├── templates/
│   └── index.html          # 前端页面模板
├── static/
│   └── styles.css          # 静态资源
├── config.ini              # 配置文件
└── requirements.txt        # 依赖文件
```

## 贡献

欢迎对本项目进行贡献！请提交 Pull Request 或 Issue 来提出建议和改进。

## 许可证

本项目使用 [MIT 许可证](LICENSE)。
```

// api/submit-textarea.js
export default async function handler(req, res) {
  try {
    // 假设你请求的是一个较慢的 API
    const apiUrl = 'https://cn.tensorart.net';

    // 发起 API 请求
    const response = await fetch(apiUrl, {
      method: req.method,
      headers: req.headers,
      body: req.body, // 如果是 POST 请求，传递请求体
    });

    // 如果 API 请求失败，返回 502 错误
    if (!response.ok) {
      return res.status(502).json({ error: 'API 请求失败' });
    }

    // 将 API 返回的 JSON 数据转发给客户端
    const data = await response.json();
    return res.status(200).json(data);

  } catch (error) {
    console.error(error);
    return res.status(504).json({ error: '请求超时或出错' });
  }
}

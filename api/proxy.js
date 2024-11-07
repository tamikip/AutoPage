// api/proxy.js
export default async function handler(req) {
  const apiUrl = 'https://cn.tensorart.net'; // 国内 API 地址

  // 你可以根据需要修改请求方式和数据
  const response = await fetch(apiUrl, {
    method: req.method,
    headers: req.headers,
    body: req.body, // 如果是 POST 请求，传递 body
  });

  // 将 API 响应返回给客户端
  const data = await response.json(); // 如果响应是 JSON
  return new Response(JSON.stringify(data), {
    status: response.status,
    headers: { 'Content-Type': 'application/json' }
  });
}

export default async function handler(req) {
  const apiUrl = 'https://your-domestic-api.com/path'; // 国内 API 地址

  try {
    const response = await fetch(apiUrl, {
      method: req.method,
      headers: req.headers,
      body: req.body,
      timeout: 1000000 
    });

    if (!response.ok) {
      return new Response('API 请求失败', { status: 502 });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error(error);
    return new Response('请求超时或出错', { status: 504 });
  }
}

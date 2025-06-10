import axios from "axios";

// 共通インスタンス作成
const api = axios.create({
  baseURL: "http://localhost:8000/api/",
});

// リクエスト前にトークンを自動付与
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// レスポンスで401が返ってきたら自動リフレッシュ（1回だけ）
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    const isUnauthorized = error.response?.status === 401;
    const hasRefreshToken = !!localStorage.getItem("refresh_token");
    const hasNotRetried = !originalRequest._retry;

    if (isUnauthorized && hasNotRetried && hasRefreshToken) {
      originalRequest._retry = true;

      try {
        const res = await axios.post("http://localhost:8000/api/token/refresh/", {
          refresh: localStorage.getItem("refresh_token"),
        });

        const newAccessToken = res.data.access;
        const newRefreshToken = res.data.refresh;

        localStorage.setItem("access_token", newAccessToken);
        if (newRefreshToken) {
          localStorage.setItem("refresh_token", newRefreshToken); // 更新があれば必ず保存
        }

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest); // 🔁 リトライ
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.assign("/login");
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

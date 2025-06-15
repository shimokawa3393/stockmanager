import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import "../styles/StockDetailPage.css";

export default function StockDetailPage() {
  const { symbol } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [isSaved, setIsSaved] = useState(false);
  const [username, setUsername] = useState(null);
  const navigate = useNavigate();

  const token = localStorage.getItem("access_token");

  useEffect(() => {

    if (token) {
      api
        .get("accounts/user/")
        .then((res) => setUsername(res.data.username))
        .catch(() => setUsername(null));
    }

    const fetchDetails = async () => {
      try {
        const response = await api.get(
          "https://stockmanager-n3b7.onrender.com/api/stockmanager/fetch/",
          { params: { symbol } },
        );
        setData(response.data);
        setIsSaved(response.data.is_saved || false); // ← API側が保存済み情報も返してたらこれ
      } catch (err) {
        setError("銘柄の詳細情報を取得できませんでした。");
      }
    };

    fetchDetails();
  }, [symbol]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUsername(null);
    navigate("/login");
  };

  const toggleSave = async () => {
    try {
      if (isSaved) {
        await api.post("stockmanager/remove/", { symbol });
        setIsSaved(false);
      } else {
        await api.post("stockmanager/save/", { symbol });
        setIsSaved(true);
      }
    } catch (err) {
      alert("ログインしてください。");
    }
  };


  if (error) return <p className="error-message">{error}</p>;
  if (!data) return <p>読み込み中...</p>;

  return (
    <div className="detail-container">
      <header className="header">
        <div className="nav-links">
          {username ? (
            <>
              <Link to="/mypage" className="nav-link">
                マイページ
              </Link>
              <button onClick={handleLogout} className="nav-link logout-button">
                ログアウト
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">
                ログイン
              </Link>
              <Link to="/register" className="nav-link">
                ユーザー登録
              </Link>
            </>
          )}
        </div>
      </header>
      <strong>{data.symbol}</strong>
      <h1>
        {data.metrics?.["企業名"] || "取得失敗"}{" "}
        <span
          className={`heart-icon ${isSaved ? "saved" : ""}`}
          onClick={toggleSave}
          title="お気に入りに追加/削除"
        >
          {isSaved ? "❤️" : "🤍"}
        </span>
      </h1>
      <h2>
        <strong>株価:</strong> {data.metrics?.["株価"] || "-"}
      </h2>
      <h3>財務指標一覧</h3>
      <ul>
        {Object.entries(data.metrics || {})
          .filter(([key]) => key !== "企業名" && key !== "株価")
          .map(([key, value]) => (
            <li key={key}>
              <strong>{key}:</strong> {value}
            </li>
          ))}
      </ul>
      <Link to="/" className="back-link">
        ← 一覧に戻る
      </Link>
    </div>
  );
}

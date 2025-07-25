import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import "../styles/Common.css";
import "../styles/StockDetailPage.css";

export default function StockDetailPage() {
  const { symbol } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [isSaved, setIsSaved] = useState(false);
  const [username, setUsername] = useState(null);
  const navigate = useNavigate();

  const token = localStorage.getItem("access_token");

  useEffect(() => {

    // ユーザー名を取得
    if (token) {
      api
        .get("accounts/user/")
        .then((res) => setUsername(res.data.username))
        .catch(() => setUsername(null));
    }

    // 銘柄の詳細情報を取得
    const fetchDetails = async () => {
      try {
        const response = await api.get(
          `${process.env.REACT_APP_API_URL}/stockmanager/fetch/`,
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


  // data が更新されたら isSaved をセット
  useEffect(() => {
    if (data && typeof data.is_saved !== "undefined") {
      setIsSaved(data.is_saved);
    }
  }, [data]);


  // 検索ボタンを押したら、検索ワードをAPIに送信して、銘柄のシンボルを取得
  // 銘柄のシンボルを取得したら、銘柄の詳細ページに遷移
  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      alert("企業名を入力してください。");
      return;
    }

    try {
      const response = await api.post("/stockmanager/search/", {
        company_name: searchTerm,
      });

      const symbol = response.data.symbol;

      if (!symbol) {
        alert("シンボルが取得できませんでした。");
        return;
      }

      // 🔸 ユーザー入力は変えず、ページだけ遷移
      navigate(`/stockdetail/${symbol}`);
    } catch (err) {
      console.error("検索エラー:", err);
      alert("銘柄の取得に失敗しました。");
    }
  };

  // ログアウト
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUsername(null);
    navigate("/login");
  };

  // お気に入りに追加/削除
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

  // エラー表示
  if (error) return <span className="error-message">{error}</span>;
  if (!data)
    return (
      <div className="loading-overlay">
        <div className="spinner" />
        読み込み中...
      </div>
    );
    
  return (
    <div className="main-container">
      <div className="detail-common-wrapper">
        <header className="header">
          <div className="greeting">
            {username ? `${username} さん` : "ゲスト さん"}
          </div>
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
        <div className="search-box">
          <input
            type="text"
            placeholder="企業名で検索"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button onClick={handleSearch} className="search-button">
            検索
          </button>
        </div>
      </div>

      <div className="detail-stock-card">
        <strong>
          {data.symbol}
          <span
            className={`heart-icon ${isSaved ? "saved" : ""}`}
            onClick={toggleSave}
            title="お気に入りに追加/削除"
          >
            {isSaved ? "❤️" : "🤍"}
          </span>
        </strong>
        <h1>
          {data.metrics?.["企業名"] || "取得失敗"}{" "}
        </h1>
        <div className="info-item">
          <span className="info-label">WEBサイト:</span>
          {data.metrics?.["WEBサイト"] ? (
            <a
              href={data.metrics["WEBサイト"]}
              target="_blank"
              rel="noopener noreferrer"
              className="info-link"
            >
              {data.metrics["WEBサイト"]}
            </a>
          ) : (
            <span className="info-placeholder">-</span>
          )}
        </div>
        <div className="info-item">
          <span className="info-label">企業概要:</span>
          <p className="info-text summary-scroll">
            {data.metrics?.["企業概要"] || <span className="info-placeholder">-</span>}
          </p>
        </div>
        <h2>
          <strong>株価:</strong> {data.metrics?.["株価"] || "-"}
        </h2>
        <ul>
          {Object.entries(data.metrics || {})
            .filter(([key]) => key !== "企業名" && key !== "WEBサイト" && key !== "企業概要" && key !== "株価")
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
    </div>
  );
}

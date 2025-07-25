import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import "../styles/Common.css";
import "../styles/MainPage.css";

export default function MainPage() {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [username, setUsername] = useState(null);
  const navigate = useNavigate();

  // ページが読み込まれたら、トークンを更新
  useEffect(() => {
    const init = async () => {
      setLoading(true);

      // ユーザー情報取得
      try {
        const res = await api.get("accounts/user/");
        setUsername(res.data.username);
      } catch {
        setUsername(null);
      }

      // ポートフォリオ取得
      try {
        const res = await api.get("stockmanager/main/");
        setData(res.data.results);
      } catch (err) {
        if (err.response?.status === 401) {
          // 非ログイン状態での想定通りの挙動
          setError("ポートフォリオ機能はログイン後にご利用になれます。");
        } else {
          setError("データ取得に失敗しました。");
        }
      } finally {
        setLoading(false);
      }
    };

    init();
  }, []);


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
  const toggleSave = async (symbol, index) => {
    try {
      const updatedData = [...data];
      if (data[index].is_saved) {
        await api.post(
          `${process.env.REACT_APP_API_URL}/stockmanager/remove/`,
          { symbol },
        );
        updatedData[index].is_saved = false;
      } else {
        await api.post(
          `${process.env.REACT_APP_API_URL}/stockmanager/save/`,
          { symbol },
        );
        updatedData[index].is_saved = true;
      }
      setData(updatedData);
    } catch (err) {
      alert("ログインしてください。");
    }
  };


  return (
    <div className="main-container">
      <div className="main-common-wrapper">
        <header className="header">
          <div className="greeting">
            <span className="greeting-username">{username ? `${username}` : "ゲスト"}</span>
            <span className="greeting-text">さん</span>
          </div>
          <div className="nav-links">
            {username ? (
              <>
                <Link to="/mypage" className="nav-link">
                  マイページ
                </Link>
                <button onClick={handleLogout} className="nav-link">
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

      {loading ? (
        <div className="loading-overlay">
          <div className="spinner" />
          読み込み中...
        </div>
      ) : error ? (
        <span className="error-message">{error}</span>
      ) : (
        data.length === 0 ? (
          <p className="empty-message">お気に入りを追加してみましょう！</p>
        ) : (
          <ul className="stock-list">
            {data.map((item, index) => (
              <div key={index} className="main-stock-card">
                <strong>
                  {item.symbol}
                  <span
                    className={`heart-icon ${item.is_saved ? "saved" : ""}`}
                    onClick={() => toggleSave(item.symbol, index)}
                    title="お気に入りに追加/削除"
                  >
                    {item.is_saved ? "❤️" : "🤍"}
                  </span>
                </strong>
                <h1>
                  <Link to={`/stockdetail/${item.symbol}`} className="stock-link">
                    {item.metrics?.["企業名"] || "取得失敗"}
                  </Link>
                </h1>
                <h2>
                  <strong>株価:</strong> {item.metrics?.["株価"] || "-"}
                </h2>
                <ul>
                  {Object.entries(item.metrics || {})
                    .filter(([key]) => key !== "企業名" && key !== "WEBサイト" && key !== "企業概要" && key !== "株価")
                    .map(([key, value]) => (
                      <li key={key}>
                        <strong>{key}:</strong> {value}
                      </li>
                    ))}
                </ul>
              </div>
            ))}
          </ul>
        )
      )}
    </div>
  );
}

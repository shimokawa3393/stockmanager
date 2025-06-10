import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import "../styles/MainPage.css";

export default function MainPage() {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
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

    const fetchData = async () => {
      if (!token) {
        setError("ポートフォリオ機能は、ログイン後にご利用になれます。");
        setLoading(false);
        return;
      }

      try {
        const response = await api.get("stockmanager/main/");
        setData(response.data.results);
      } catch (err) {
        setError("データ取得に失敗しました。ログインが必要かもしれません。");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUsername(null);
    navigate("/login");
  };


  const toggleSave = async (symbol, index) => {
    try {
      const updatedData = [...data];
      if (data[index].is_saved) {
        await api.post(
          "http://localhost:8000/api/stockmanager/remove/",
          { symbol },
        );
        updatedData[index].is_saved = false;
      } else {
        await api.post(
          "http://localhost:8000/api/stockmanager/save/",
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
      <header className="header">
        <div className="greeting">
          ようこそ {username ? `${username} さん` : "ゲスト さん"}
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

      {username && (
        <h1 className="main-title">{username} さんのポートフォリオ</h1>
      )}

      {loading ? (
        <p>読み込み中...</p>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : (
        <ul className="stock-list">
          {data.map((item, index) => (
            <div key={index} className="stock-card">
              <strong>{item.symbol}</strong>
              <h1>
                <Link to={`/stockdetail/${item.symbol}`} className="stock-link">
                  {item.metrics?.["企業名"] || "取得失敗"}
                </Link>
                <span
                  className={`heart-icon ${item.is_saved ? "saved" : ""}`}
                  onClick={() => toggleSave(item.symbol, index)}
                  title="お気に入りに追加/削除"
                >
                  {item.is_saved ? "❤️" : "🤍"}
                </span>
              </h1>
              <h2>
                <strong>株価:</strong> {item.metrics?.["株価"] || "-"}
              </h2>
              <h3>財務指標一覧</h3>
              <ul>
                {Object.entries(item.metrics || {})
                  .filter(([key]) => key !== "企業名" && key !== "株価")
                  .map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}:</strong> {value}
                    </li>
                  ))}
              </ul>
            </div>
          ))}
        </ul>
      )}
    </div>
  );
}

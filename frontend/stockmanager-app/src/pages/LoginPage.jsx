import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/LoginPage.css"; // CSSファイルを読み込む

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const response = await axios.post("https://stockmanager-n3b7.onrender.com/api/token/", {
        email,
        password,
      });
      localStorage.setItem("access_token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);
      axios.defaults.headers.common["Authorization"] = `Bearer ${response.data.access}`;
      navigate("/");
    } catch (err) {
      setError("ログインに失敗しました。メールアドレスまたはパスワードを確認してください。");
    }
  };

  return (
      <div className="login-container">
        <Link to="/" className="nav-link">
        メインページへ
      </Link>
      <h2 className="login-title">ログイン</h2>
      {error && <p className="login-error">{error}</p>}
      <form onSubmit={handleLogin}>
        <div className="login-field">
          <label>メールアドレス</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="login-field">
          <label>パスワード</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="login-button">
          ログイン
        </button>
      </form>
    </div>
  );
}

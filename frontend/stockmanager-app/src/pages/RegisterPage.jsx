import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/axios";
import "../styles/Common.css";
import "../styles/RegisterPage.css";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await api.post("accounts/register/", formData);
      alert("登録完了！");
      navigate("/");
    } catch (err) {
      setError("登録に失敗しました。");
    }
  };

  return (
    <div className="main-container">
      <div className="auth-container">
        <h2>ユーザー登録</h2>
        <form onSubmit={handleRegister}>
          <input
            type="text"
            name="username"
            placeholder="ユーザー名"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <input
            type="email"
            name="email"
            placeholder="メールアドレス"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="パスワード"
            value={formData.password}
            onChange={handleChange}
            required
          />
          {error && <p className="error-message">{error}</p>}
          <button type="submit">登録</button>
        </form>
        <p>
          すでに登録済み？ <Link to="/login">ログイン</Link>
        </p>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import "../styles/Common.css";
import "../styles/MyPage.css";

export default function MyPage() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("accounts/user/")
      .then((res) => setUser(res.data))
      .catch(() => navigate("/login"));
  }, []);

  const handleDeleteAccount = async () => {
    if (!window.confirm("本当にアカウントを削除しますか？")) return;
    try {
      await api.delete("accounts/delete/");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      alert("アカウントを削除しました。");
      navigate("/register");
    } catch (err) {
      alert("削除に失敗しました。");
    }
  };

  if (!user)
    return (
      <div className="loading-overlay">
        <div className="spinner" />
        読み込み中...
      </div>
    );
    
  return (
    <div className="mypage-container">
      <h1>マイページ</h1>
      <p><strong>ユーザー名:</strong> {user.username}</p>
      <p><strong>メールアドレス:</strong> {user.email}</p>
      <button className="delete-button" onClick={handleDeleteAccount}>
        アカウント削除
      </button>
    </div>
  );
}

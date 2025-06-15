# 📊 StockManager

**Django + React製 財務指標閲覧ツール**  
お気に入り銘柄の登録、検索、財務指標の取得までできる、個人開発ポートフォリオです。

---

## 🚀 主な機能

- 🔍 企業名で銘柄検索（ChatGPTでシンボルを自動変換）
- 🧾 財務指標をyfinanceから取得・表示
- ❤️ お気に入り登録・解除（JWT認証）
- 🗂 ユーザー登録 / ログイン / マイページ
- ⚡ Djangoキャッシュによる高速表示

---

## 🛠 使用技術

- **フロントエンド**：React / Axios / React Router
- **バックエンド**：Django REST Framework / Simple JWT
- **データ取得**：yfinance / OpenAI API
- **データベース**：MySQL
- **その他**：環境変数管理（dotenv）/ キャッシュ機能

---

## 📁 ディレクトリ構成

```
stockmanagerProject/
├── backend/ # Djangoアプリ
│ ├── accounts/ # カスタムユーザー認証
│ ├── stockmanager/ # 銘柄データ取得・保存
│ └── manage.py
├── frontend/
│ └── stockmanager-app/ # Reactフロント
└── .gitignore
```

---

## 👤 作者

shimokawa3393
実務未経験の日曜エンジニアです。
このアプリが気に入ったら ⭐️ をポチッとお願いします！

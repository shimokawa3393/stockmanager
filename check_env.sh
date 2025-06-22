#!/bin/bash

# .envが存在しないと死ぬ
if [ ! -f .env ]; then
  echo "🚨 .env ファイルが存在しません。デプロイ中止。"
  exit 1
fi

# .envの内容を読み込む（exportはつけない）
set -o allexport
source .env
set +o allexport

# 1. DEBUGがTrueだったら中止
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
  echo "❌ DEBUG=True は本番環境では致命的です。"
  exit 1
fi

# 2. 開発用DB（localhost, 127.0.0.1）を使ってたら中止
if [[ "$DATABASE_URL" == *"localhost"* ]] || [[ "$DATABASE_URL" == *"127.0.0.1"* ]]; then
  echo "❌ DATABASE_URL がローカルDB（localhost）を指しています。"
  exit 1
fi

# 3. APIキーがdev用（例：sk-testなど）なら警告（APIに応じて調整）
if [[ "$OPENAI_API_KEY" == *"sk-test"* ]]; then
  echo "⚠️ 警告：OPENAI_API_KEY がテスト用キーっぽいです。"
fi

# 4. SECRET_KEYが弱い（デフォルトとか）場合
if [[ "$SECRET_KEY" == "changeme" ]] || [[ "$SECRET_KEY" == "dummy" ]]; then
  echo "❌ SECRET_KEY が脆弱です。"
  exit 1
fi

echo "✅ 環境チェックOK。デプロイしてよし。"
exit 0


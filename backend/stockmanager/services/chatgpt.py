# CompanyCodeFetcher クラス
# OpenAI API（GPT）を利用して、企業名から証券コード（日本株の場合）またはティッカーシンボル（米国株など）を取得するクラス。
# 初期化時に company_name を渡し、getSymbol() メソッドでシンボルを取得する。
# ChatGPTには「数字、またはアルファベットだけで返答してください。」と指示し、"7203" や "AAPL" などの形式で返ってくることを期待している。
# ※ APIキーは .env ファイルから取得される。ファイルのルートは __file__ の2階層上にあることを前提。
# ※ OpenAI のレスポンスは自由形式のため、予期しない出力への耐性が必要。将来的にバリデーション処理を追加してもよい。


import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI


# プロジェクトのルートを取得
BASE_DIR = Path(__file__).resolve().parents[2]

# .envを読み込み
load_dotenv(dotenv_path=BASE_DIR / '.env')


class SymbolFetcher:
    def __init__(self, company_name):
        self.company_name = company_name
        self.symbol = None
        self.api_key = os.getenv("OpenAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)


    def getSymbol(self):
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "数字、またはアルファベットだけで返答してください。"},
                {"role": "user", "content": f"{self.company_name}の企業コード、またはティッカーを教えて。すでに企業コード、ティッカーの場合は、渡された値をそのまま返答してください。"},
            ]
        )
        self.symbol = response.choices[0].message.content.strip()
        return self.symbol

import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI


# プロジェクトのルートを取得
BASE_DIR = Path(__file__).resolve().parents[2]

# .envを読み込み
load_dotenv(dotenv_path=BASE_DIR / ".env")

# ChatGPTを使用するクラス
class ChatGPT:
    def __init__(self):
        self.symbol = None
        self.api_key = os.getenv("OpenAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    # 企業名から証券コード（日本株）またはティッカーシンボル（米国株）を取得する関数
    def getSymbol(self, company_name):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                        以下のルールに従って返答してください：
                        1. 入力されたテキストが企業名の場合、該当する証券コード（日本株）またはティッカーシンボル（米国株）を、英数字のみで返答してください（例：7203, AAPL）。
                        2. 入力されたテキストがすでに企業コード、ティッカーの場合は、渡された値をそのまま返答してください。
                        3. 入力が企業名ではない場合は 'Invalid' と返答してください。
                        4. 回答は必ず1単語のみ、余計な説明は不要です。
                        """,
                },
                {
                    "role": "user",
                    "content": f"{company_name}の企業コード、またはティッカーを教えてください。",
                },
            ],
        )
        content = response.choices[0].message.content
        self.symbol = content.strip() if content else ""
        return self.symbol
    
    
    # 企業概要の英文を日本語に翻訳する関数
    def getTranslation(self, text):   
        if text == "N/A" or text == "":
            return "N/A"
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "英文を日本語に翻訳してください。",
                },
                {
                    "role": "user",
                    "content": f"{text}",
                },
            ],
        )
        content = response.choices[0].message.content
        translation = content.strip() if content else ""
        return translation

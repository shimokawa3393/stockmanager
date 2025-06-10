# CompanyFinancialsFetcher クラス
# 企業の財務データ（info / BS / PL）を yfinance を使って取得するクラス。
# symbol には 'AAPL' や '7203.T' のようなティッカーシンボルを渡す。
# 日本株で int 型（例：7203）を渡した場合、自動で ".T" を付与し、yfinance のシンボル形式に対応。
# getCompanyFinancials() を呼び出すと、以下の3つをタプルで返す：
# - company_info（企業基本情報：stock.info）
# - company_bs（バランスシート：stock.balance_sheet）
# - company_pl（損益計算書：stock.financials）
# ※ データ取得にはインターネット接続が必要。

# 注意：
# - PL・BSはDataFrame形式、infoは辞書型で返る。
# - yfinance 側の仕様変更や接続エラーにより、項目が NaN や空になる場合がある。
# - 将来的にキャッシュ化や例外処理の追加を検討する。


import yfinance as yf


# 小数点以下2桁に四捨五入する関数
def safe_round(value, digits=2):
    try:
        return round(value, digits)
    except Exception:
        return "N/A"

# 財務諸表の項目が存在しない場合はNoneを返す関数
def get_values_or_error(df, keys, source_name=""):
    values = {}
    for key in keys:
        try:
            values[key] = df.loc[key].iloc[0]
        except KeyError:
            print(f"❌ {source_name} から '{key}' を取得できませんでした")
            return None  # 一つでも欠けたら中断
    return values

# 財務諸表を取得するクラス
class CompanyFinancialsFetcher:
    def __init__(self, symbol):
        self.symbol = symbol
        self.symbol_type = type(symbol)
        self.company_info = None
        self.company_bs = None
        self.company_pl = None

    # yfinanceを利用して財務諸表を取得する関数
    def getCompanyFinancials(self):
        if isinstance(self.symbol, int) or (
            isinstance(self.symbol, str) and self.symbol.isdigit()
        ):
            # 数字（証券コード）なら.Tをつける（日本株）
            stock = yf.Ticker(f"{self.symbol}.T")
        else:
            # それ以外（ティッカーそのまま、例: AAPL, HMC）
            stock = yf.Ticker(self.symbol)

        self.company_info = stock.info
        self.company_bs = stock.balance_sheet
        self.company_pl = stock.financials
        return self.company_info, self.company_bs, self.company_pl

    # ROICを計算する関数
    def calculateROIC(self):
        pl_keys = ["EBIT", "Tax Rate For Calcs"]
        bs_keys = ["Invested Capital"]

        pl_values = get_values_or_error(self.company_pl, pl_keys, source_name="PL")
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")

        if not pl_values or not bs_values:
            return "データなし"

        ebit = pl_values["EBIT"]
        tax_rate = pl_values["Tax Rate For Calcs"]
        invested_capital = bs_values["Invested Capital"]

        nopat = ebit * (1 - tax_rate)
        return safe_round(nopat / invested_capital * 100)


    # 純利益率を計算する関数
    def calculateProfitMargin(self):
        pl_keys = ["Net Income", "Total Revenue"]
        pl_values = get_values_or_error(self.company_pl, pl_keys, source_name="PL")
        if not pl_values:
            return "データなし"
        net_income = pl_values["Net Income"]
        total_revenue = pl_values["Total Revenue"]
        return safe_round(net_income / total_revenue * 100)

    # 自己資本比率を計算する関数
    def calculateEquityRatio(self):
        bs_keys = ["Stockholders Equity", "Total Assets"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        if not bs_values:
            return "データなし"
        equity = bs_values["Stockholders Equity"]
        total_assets = bs_values["Total Assets"]
        return safe_round(equity / total_assets * 100)

    # 流動比率を計算する関数
    def calculateCurrentRatio(self):
        bs_keys = ["Current Assets", "Current Liabilities"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        if not bs_values:
            return "データなし"
        current_assets = bs_values["Current Assets"]
        current_liabilities = bs_values["Current Liabilities"]
        return safe_round(current_assets / current_liabilities * 100)

    # 当座比率を計算する関数
    def calculateQuickRatio(self):
        bs_keys = ["Current Assets", "Inventory", "Current Liabilities"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        if not bs_values:
            return "データなし"
        current_assets = bs_values["Current Assets"]
        inventory = bs_values["Inventory"]
        current_liabilities = bs_values["Current Liabilities"]
        return safe_round((current_assets - inventory) / current_liabilities * 100)

    # 固定比率を計算する関数
    def calculateFixedRatio(self):
        bs_keys = ["Net Tangible Assets", "Stockholders Equity"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        if not bs_values:
            return "データなし"
        fixed_assets = bs_values["Net Tangible Assets"]
        equity = bs_values["Stockholders Equity"]
        return safe_round(fixed_assets / equity * 100)

    # 固定長期適合率を計算する関数
    def calculateFixedLongTermAppropriatenessRatio(self):
        bs_keys = ["Net Tangible Assets", "Stockholders Equity", "Long Term Debt"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        if not bs_values:
            return "データなし"
        fixed_assets = bs_values["Net Tangible Assets"]
        equity = bs_values["Stockholders Equity"]
        long_term_liabilities = bs_values["Long Term Debt"]
        return safe_round(fixed_assets / (equity + long_term_liabilities) * 100)

    # 負債比率を計算する関数
    def calculateDebtRatio(self):
        bs_keys = ["Total Liabilities Net Minority Interest", "Total Assets"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        if not bs_values:
            return "データなし"
        total_liabilities = bs_values["Total Liabilities Net Minority Interest"]
        total_assets = bs_values["Total Assets"]
        return safe_round(total_liabilities / total_assets * 100)

    # ネットD/Eレシオを計算する関数
    def calculateNetDERatio(self):
        bs_keys = ["Total Debt", "Cash And Cash Equivalents", "Stockholders Equity"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        if not bs_values:
            return "データなし"
        net_debt = bs_values["Total Debt"] - bs_values["Cash And Cash Equivalents"]
        equity = bs_values["Stockholders Equity"]
        return safe_round(net_debt / equity * 100)

    # 上記の項目をJSONデータセットにまとめる関数
    def get_all_metrics(self):
        if self.company_bs is None or self.company_pl is None:
            raise ValueError("先に getCompanyFinancials() を呼び出してください。")

        metrics = {}

        metrics["企業名"] = self.company_info.get("shortName", "N/A")

        price = self.company_info.get("regularMarketPrice")
        currency_symbol = "\u00a5" if self.symbol_type == int else "$"
        metrics["株価"] = f"{currency_symbol}{price}" if price is not None else "N/A"

        metrics["粗利率"] = safe_round(self.company_info.get("grossMargins", 0) * 100)
        metrics["営業利益率"] = safe_round(
            self.company_info.get("operatingMargins", 0) * 100
        )
        metrics["EBITDAマージン"] = safe_round(
            self.company_info.get("ebitdaMargins", 0) * 100
        )
        metrics["純利益率"] = self.calculateProfitMargin()
        metrics["PER"] = safe_round(self.company_info.get("trailingPE", 0))
        metrics["PBR"] = safe_round(self.company_info.get("priceToBook", 0))
        metrics["ROE"] = safe_round(self.company_info.get("returnOnEquity", 0) * 100)
        metrics["ROA"] = safe_round(self.company_info.get("returnOnAssets", 0) * 100)
        metrics["ROIC"] = self.calculateROIC()
        metrics["自己資本比率"] = self.calculateEquityRatio()
        metrics["流動比率"] = self.calculateCurrentRatio()
        metrics["当座比率"] = self.calculateQuickRatio()
        metrics["固定比率"] = self.calculateFixedRatio()
        metrics["固定長期適合率"] = self.calculateFixedLongTermAppropriatenessRatio()
        metrics["負債比率"] = self.calculateDebtRatio()
        metrics["ネットD/Eレシオ"] = self.calculateNetDERatio()

        return metrics



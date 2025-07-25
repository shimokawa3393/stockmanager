import math
import yfinance as yf
from .chatgpt import ChatGPT


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
            return None  
    return values


# 指定したキーの値を float に変換し、NaN や欠損をチェックする関数
def extract_and_validate(values_dict, keys, allow_zero_divisor=False):
    """
    指定したキーの値を float に変換し、NaN や欠損をチェックする。
    
    :param values_dict: 対象の辞書
    :param keys: 必要なキーのリスト（順番が意味を持つ）
    :param allow_zero_divisor: 最後の要素（除数）が0でも許容するならTrue
    :return: [float値のリスト] または None（不正な場合）
    """
    try:
        floats = [float(values_dict[k]) for k in keys]
        if any(math.isnan(x) for x in floats):
            return None
        if not allow_zero_divisor and floats[-1] == 0:
            return None
        return floats
    except (KeyError, ValueError, TypeError):
        return None


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

        validated_pl = extract_and_validate(pl_values, pl_keys)
        validated_bs = extract_and_validate(bs_values, bs_keys)
        if not validated_pl or not validated_bs:
            return "データなし"

        ebit, tax_rate, invested_capital = validated_pl[0], validated_pl[1], validated_bs[0]
        return safe_round(ebit * (1 - tax_rate) / invested_capital * 100)


    # 純利益率を計算する関数
    def calculateProfitMargin(self):
        pl_keys = ["Net Income", "Total Revenue"]
        pl_values = get_values_or_error(self.company_pl, pl_keys, source_name="PL")
        validated_pl = extract_and_validate(pl_values, pl_keys)
        if not validated_pl:
            return "データなし"
        net_income, total_revenue = validated_pl[0], validated_pl[1]        
        return safe_round(net_income / total_revenue * 100)


    # 自己資本比率を計算する関数
    def calculateEquityRatio(self):
        bs_keys = ["Stockholders Equity", "Total Assets"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        validated_bs = extract_and_validate(bs_values, bs_keys, allow_zero_divisor=True)
        if not validated_bs:
            return "データなし"
        stockholders_equity, total_assets = validated_bs[0], validated_bs[1]
        return safe_round(stockholders_equity / total_assets * 100)

    # 流動比率を計算する関数
    def calculateCurrentRatio(self):
        bs_keys = ["Current Assets", "Current Liabilities"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")                
        validated_bs = extract_and_validate(bs_values, bs_keys)
        if not validated_bs:
            return "データなし"
        current_assets, current_liabilities = validated_bs[0], validated_bs[1]
        return safe_round(current_assets / current_liabilities * 100)

    # 当座比率を計算する関数
    def calculateQuickRatio(self):
        bs_keys = ["Current Assets", "Inventory", "Current Liabilities"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        validated_bs = extract_and_validate(bs_values, bs_keys)
        if not validated_bs:
            return "データなし"
        current_assets, inventory, current_liabilities = validated_bs[0], validated_bs[1], validated_bs[2]
        return safe_round((current_assets - inventory) / current_liabilities * 100)

    # 固定比率を計算する関数
    def calculateFixedRatio(self):
        bs_keys = ["Net Tangible Assets", "Stockholders Equity"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        validated_bs = extract_and_validate(bs_values, bs_keys)
        if not validated_bs:
            return "データなし"
        net_tangible_assets, stockholders_equity = validated_bs[0], validated_bs[1]
        return safe_round(net_tangible_assets / stockholders_equity * 100)

    # 固定長期適合率を計算する関数
    def calculateFixedLongTermAppropriatenessRatio(self):
        bs_keys = ["Net Tangible Assets", "Stockholders Equity", "Long Term Debt"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        validated_bs = extract_and_validate(bs_values, bs_keys)
        if not validated_bs:
            return "データなし"
        net_tangible_assets, stockholders_equity, long_term_debt = validated_bs[0], validated_bs[1], validated_bs[2]
        return safe_round(net_tangible_assets / (stockholders_equity + long_term_debt) * 100)

    # 負債比率を計算する関数
    def calculateDebtRatio(self):
        bs_keys = ["Total Liabilities Net Minority Interest", "Total Assets"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        validated_bs = extract_and_validate(bs_values, bs_keys)
        if not validated_bs:
            return "データなし"
        total_liabilities_net_minority_interest, total_assets = validated_bs[0], validated_bs[1]
        return safe_round(total_liabilities_net_minority_interest / total_assets * 100)

    # ネットD/Eレシオを計算する関数
    def calculateNetDERatio(self):
        bs_keys = ["Total Debt", "Cash And Cash Equivalents", "Stockholders Equity"]
        bs_values = get_values_or_error(self.company_bs, bs_keys, source_name="BS")
        validated_bs = extract_and_validate(bs_values, bs_keys)
        if not validated_bs:
            return "データなし"
        total_debt, cash_and_cash_equivalents, stockholders_equity = validated_bs[0], validated_bs[1], validated_bs[2]
        return safe_round(total_debt / (cash_and_cash_equivalents + stockholders_equity) * 100)


    # 上記の項目をJSONデータセットにまとめる関数
    def get_all_metrics(self):
        if self.company_bs is None or self.company_pl is None or self.company_info is None:
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
        metrics["PER"] = safe_round(self.company_info.get("forwardPE", 0))
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
    
    # 詳細画面で銘柄の追加情報を表示させる関数
    def get_company_overview(self):
        metrics = {}
        metrics["WEBサイト"] = self.company_info.get("website", "N/A")
        
        translation = ChatGPT().getTranslation(self.company_info.get("longBusinessSummary", "N/A"))
        metrics["企業概要"] = translation
        
        return metrics
    
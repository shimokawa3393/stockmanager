import time
from django.core.cache import cache
from .services.chatgpt import UseChatGPT
from .services.yahoofinance import CompanyFinancialsFetcher
from .utils import convert_symbol

CACHE_TIMEOUT = 60 * 60  # 1時間

# 検索から銘柄を表示する関数（会社名→シンボル）
def search_symbol(company_name, request):
    symbol_fetcher = UseChatGPT()
    symbol = symbol_fetcher.getSymbol(company_name)
    if symbol == "Invalid":
        raise ValueError("企業名が正しくありません。")
    return symbol


# 銘柄を表示させる関数(条件分岐で一覧画面・詳細画面で使い分ける)
def fetch_company_data(symbol, request, include_overview=False):
    symbol = convert_symbol(symbol)
    cache_key = f"metrics_{request.user.id}_{symbol}_{'detail' if include_overview else 'list'}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data
    else:
        time.sleep(3)

    try:
        fetcher = CompanyFinancialsFetcher(symbol)
        fetcher.getCompanyFinancials()
        metrics = fetcher.get_all_metrics()

        # 詳細画面で銘柄の追加情報を表示させる
        if include_overview:
            overview = fetcher.get_company_overview()
            metrics["WEBサイト"] = overview.get("WEBサイト", "N/A")
            metrics["企業概要"] = overview.get("企業概要", "N/A")

    except Exception as e:
        import traceback
        print("❌ エラー発生:", str(e))
        traceback.print_exc()
        raise

    cache.set(cache_key, metrics, CACHE_TIMEOUT)
    return metrics

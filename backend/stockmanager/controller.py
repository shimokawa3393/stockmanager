import time
from django.core.cache import cache
from .services.chatgpt import SymbolFetcher
from .services.yahoofinance import CompanyFinancialsFetcher
from .utils import convert_symbol

CACHE_TIMEOUT = 60 * 60  # 1時間

# 検索から銘柄を表示する関数（会社名→シンボル）
def search_symbol(company_name, request):
    symbol_fetcher = SymbolFetcher(company_name)
    symbol = symbol_fetcher.getSymbol()
    return symbol


# 銘柄指定で銘柄を表示させる関数(今は、一覧画面・詳細画面で共通の関数)
def fetch_company_data(symbol, request):
    symbol = convert_symbol(symbol)  # ←ここで変換
    cache_key = f"metrics_{request.user.id}_{symbol}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"✅ Cache hit: {cache_key}")
        return cached_data
    else:
        print(f"❌ Cache miss: {cache_key}")
        time.sleep(3)  # ← MISS時だけにする！
        
    try:
        financials_fetcher = CompanyFinancialsFetcher(symbol)
        financials_fetcher.getCompanyFinancials()
        metrics = financials_fetcher.get_all_metrics()
    except Exception as e:
        import traceback
        print("❌ エラー発生:", str(e))
        traceback.print_exc()
        raise  # 必ず再スローしてHTTP 500出すように

    cache.set(cache_key, metrics, CACHE_TIMEOUT)
    return metrics

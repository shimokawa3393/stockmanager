from django.core.cache import cache
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .controller import search_symbol, fetch_company_data  
from .models import StockSymbol


# メインページでお気に入り一覧を取得
class MainView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # ログインユーザーのお気に入り銘柄を取得
            symbols = StockSymbol.objects.filter(user=request.user).values_list(
                "symbol", flat=True
            )

            all_data = []
            for symbol in symbols:
                try:
                    metrics = fetch_company_data(symbol, request, include_overview=False) # 一覧画面で銘柄の追加情報を表示させない
                    all_data.append(
                        {
                            "symbol": symbol,
                            "metrics": metrics,
                            "is_saved": True,  # ← 保存されてるものだけなのでTrueでOK
                        }
                    )
                except Exception as e:
                    all_data.append(
                        {
                            "symbol": symbol,
                            "error": f"{symbol} のデータ取得に失敗しました: {str(e)}",
                            "is_saved": True,
                        }
                    )

            return Response({"results": all_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 検索ボックスの企業名からシンボルを取得
class SearchSymbolView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        company_name = request.data.get("company_name")

        if not company_name:
            return Response({"error": "company_name を指定してください"}, status=400)

        try:
            symbol = search_symbol(company_name, request)

            return Response(
                {
                    "symbol": symbol,
                }
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 銘柄詳細ページで銘柄詳細情報を取得
class FetchCompanyDataView(APIView):
    permission_classes = [AllowAny]  # ← ここを変更（認証不要に）

    def get(self, request):
        symbol = request.query_params.get("symbol")

        try:
            metrics = fetch_company_data(symbol, request, include_overview=True) # 詳細画面で銘柄の追加情報を表示させる
            
            # デフォルトは False（ログインしてない or お気に入りじゃない）
            is_saved = False

            if request.user.is_authenticated:
                is_saved = StockSymbol.objects.filter(user=request.user, symbol=symbol).exists()

            return Response(
                {
                    "symbol": symbol,
                    "is_saved": is_saved,
                    "metrics": metrics,
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# symbolだけ保存（お気に入り登録）
class SaveStockSymbolView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        symbol = request.data.get("symbol")

        if not symbol:
            return Response(
                {"error": "symbolが必要です"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 重複登録チェック（任意）
            if StockSymbol.objects.filter(symbol=symbol, user=request.user).exists():
                return Response(
                    {"message": "すでに登録されています"}, status=status.HTTP_200_OK
                )

            StockSymbol.objects.create(symbol=symbol, user=request.user)
            return Response({"message": "保存成功！"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# symbolだけ削除（お気に入り削除）
class RemoveStockSymbolView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        symbol = request.data.get("symbol")

        if not symbol:
            return Response(
                {"error": "symbolが必要です"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 該当のレコードを取得して削除
            favorite = StockSymbol.objects.filter(
                symbol=symbol, user=request.user
            ).first()
            if favorite:
                favorite.delete()

                # キャッシュ削除
                cache_key = f"metrics_{request.user.id}_{symbol}"
                cache.delete(cache_key)

                return Response({"message": "削除しました"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "登録されていません"}, status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

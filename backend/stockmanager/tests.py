from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class StockSymbolFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "http://localhost:8000/api/accounts/register/"
        self.login_url = "http://localhost:8000/api/token/"
        self.main_url = "http://localhost:8000/api/stockmanager/main/"
        self.search_url = "http://localhost:8000/api/stockmanager/financials/"
        self.save_url = "http://localhost:8000/api/stockmanager/save/"
        self.remove_url = "http://localhost:8000/api/stockmanager/remove/"
        self.current_user_url = "http://localhost:8000/api/accounts/logout/"

        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123!",
        }

        self.symbol = "AAPL"
        self.company_name = "Apple"

    def test_stock_symbol_flow(self):
        # ユーザー登録
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ログイン
        response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        # お気に入りなしの一覧表示
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

        # 株式検索
        response = self.client.post(self.search_url, {"company_name": self.company_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"].upper(), self.symbol)

        # お気に入り保存
        response = self.client.post(self.save_url, {"symbol": self.symbol})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

        # 再度一覧表示
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["symbol"].upper(), self.symbol)

        # お気に入り解除
        response = self.client.post(self.remove_url, {"symbol": self.symbol})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 再度一覧表示
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

        # ログアウト
        self.client.credentials()
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

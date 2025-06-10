from django.db import models
from django.conf import settings

class StockSymbol(models.Model):
    symbol = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_symbols')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('symbol', 'user')  # 同一ユーザーが同じ銘柄を複数登録しないようにする

    def __str__(self):
        return self.symbol

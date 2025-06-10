

# 取得したsymbolを数値変換する関数
def convert_symbol(symbol):
    try:
        return int(symbol)
    except ValueError:
        return symbol  # 数字にできない＝そのまま返す

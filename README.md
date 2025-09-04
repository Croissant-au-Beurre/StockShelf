# 📊 StockShelf

**StockShelf** は Python で作成した株式・暗号資産の情報取得＆分類ツールです。  
設定ファイルで自由に分類と銘柄コードを定義し、分類ごとにまとめて株価データを取得できます。  
結果は **CSV / Excel** に保存されるので、後で分析や記録に利用可能です。  

対応市場：
- ✅ 米国株（AAPL、MSFT、GOOGL …）
- ✅ 日本株（7203.T トヨタ、7974.T 任天堂 …）
- ✅ 暗号資産（BTC-USD、ETH-USD …）
- ✅ Yahoo Finance で取得可能なその他資産

---

## 🚀 特徴
- 銘柄のグループ分け（ウォッチリスト）を自由に作成可能  
- 分類単位での一括取得  
- 出力形式：
  - CSV（標準）
  - Excel（分類ごとにシート分け）  
- データソース：yfinance（Yahoo Finance API wrapper、APIキー不要）  
- 保存されるフィールド：
  - `fast_info` の全項目（例：`lastPrice`, `previousClose`, `regularMarketPreviousClose`, `dayHigh`, `dayLow`, `yearHigh`, `yearLow`, `marketCap`, `currency`, `exchange` など）  
  - `info` に含まれる詳細項目（会社名、PER、配当利回りなど）。同名の場合は `info_` プレフィックス付きで保存  

---

## 📦 インストール

```bash
pip install yfinance pandas openpyxl


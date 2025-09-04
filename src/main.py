# import sys
# import traceback
#
# from controller.stock_shelf_controller import StockShelfController
# from util.factory_logger import get_logger
#
#
# logger = get_logger(__name__)
#
# class Job:
#     @classmethod
#     def run(cls):
#         try:
#             StockShelfController().handle()
#         except Exception:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#             # スタックトレースを文字列として取得
#             traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
#             logger.error(traceback_details)
#         else:
#             text = "プログラム実行終了。"
#             logger.info(text)
#
#
# if __name__ == "__main__":
#     Job.run()


import json
import os
import sys
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import pandas as pd
import yfinance as yf

CONFIG_FILE = "categories.json"
BASE_DIR = Path(__file__).resolve().parent.parent  # プログラムの上位ディレクトリ
OUTPUT_DIR = BASE_DIR / "temp"

def load_categories(path: str) -> Dict[str, List[str]]:
    if not os.path.exists(path):
        print(f"{path} が見つかりません。空のテンプレートを作成します。")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"マイウォッチリスト": []}, f, ensure_ascii=False, indent=2)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_categories(path: str, data: Dict[str, List[str]]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def print_menu():
    print("\n=== 株価取得ツール ===")
    print("1) 分類と銘柄コードを確認")
    print("2) 選択した分類の株価を取得（複数選択可）")
    print("3) 分類を新規作成")
    print("4) 分類に銘柄コードを追加")
    print("5) 分類から銘柄コードを削除")
    print("6) 直近の取得結果を Excel に出力（分類ごとにシート分け）")
    print("0) 終了")

def select_categories(cat_names: List[str]) -> List[str]:
    print("\n利用可能な分類：")
    for i, c in enumerate(cat_names, 1):
        print(f"{i}. {c}")
    raw = input("取得したい分類番号を入力（カンマ区切り、例: 1,3）、または Enter で全選択：").strip()
    if not raw:
        return cat_names
    idxs = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= len(cat_names):
            idxs.append(int(part)-1)
    picked = [cat_names[i] for i in idxs]
    if not picked:
        print("有効な選択がありません。すべての分類を選択します。")
        return cat_names
    return picked

def fetch_quotes(tickers: List[str], category: str) -> pd.DataFrame:
    if not tickers:
        return pd.DataFrame()

    tk = yf.Tickers(" ".join(tickers))
    rows = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for t in tickers:
        try:
            info = tk.tickers[t].fast_info
            row = {
                "分類": category,
                "銘柄コード": t,
                "取得日時": ts
            }
            # fast_info の全フィールドを保存
            for k in info.keys():
                try:
                    row[k] = info.get(k, None)
                except Exception:
                    row[k] = None

            # info（詳細情報）を追加
            try:
                full_info = tk.tickers[t].info
                if isinstance(full_info, dict):
                    for k, v in full_info.items():
                        if k not in row:
                            row[k] = v
                        else:
                            row[f"info_{k}"] = v
            except Exception:
                pass

            rows.append(row)

        except Exception as e:
            rows.append({
                "分類": category,
                "銘柄コード": t,
                "取得日時": ts,
                "エラー": str(e)
            })

    return pd.DataFrame(rows)

def export_to_csv(df: pd.DataFrame) -> str:
    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"quotes_{ts}.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"CSV を保存しました：{path}")
    return path

def export_to_excel_by_category(df: pd.DataFrame, path: str):
    if df.empty:
        print("エクスポートするデータがありません。")
        return
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for cat, g in df.groupby("分類"):
            g.sort_values(["分類", "銘柄コード"], inplace=True)
            g.to_excel(writer, sheet_name=str(cat)[:31], index=False)
    print(f"Excel に出力しました：{path}")

def main():
    print("""
    ========================================
         📊 StockShelf - 株式管理ツール
    ========================================
    """)

    categories = load_categories(CONFIG_FILE)
    last_df = pd.DataFrame()

    while True:
        print_menu()
        choice = input("操作を選択してください：").strip()

        if choice == "1":
            print("\n現在の分類設定：")
            for k, v in categories.items():
                print(f"- {k}: {', '.join(v) if v else '(空)'}")

        elif choice == "2":
            if not categories:
                print("分類がありません。先に追加してください。")
                continue
            cats = select_categories(list(categories.keys()))
            all_rows = []
            for c in cats:
                d = fetch_quotes(categories.get(c, []), c)
                if not d.empty:
                    all_rows.append(d)
            if all_rows:
                last_df = pd.concat(all_rows, ignore_index=True)
                csv_path = export_to_csv(last_df)
            else:
                print("データを取得できませんでした。分類内の銘柄コードを確認してください。")

        elif choice == "3":
            name = input("新しい分類名を入力：").strip()
            if name:
                if name in categories:
                    print("その分類は既に存在します。")
                else:
                    categories[name] = []
                    save_categories(CONFIG_FILE, categories)
                    print(f"分類を追加しました：{name}")

        elif choice == "4":
            name = input("銘柄を追加する分類名を入力：").strip()
            if name not in categories:
                print("分類が存在しません。")
                continue
            codes = input("追加する銘柄コードを入力（カンマ区切り、例：AAPL, 7203.T, BTC-USD）：").strip()
            items = [x.strip() for x in codes.split(",") if x.strip()]
            categories[name] = sorted(set(categories[name] + items))
            save_categories(CONFIG_FILE, categories)
            print(f"{name} を更新しました: {', '.join(categories[name])}")

        elif choice == "5":
            name = input("銘柄を削除する分類名を入力：").strip()
            if name not in categories:
                print("分類が存在しません。")
                continue
            print(f"現在の銘柄: {', '.join(categories[name])}")
            codes = input("削除する銘柄コードを入力（カンマ区切り）：").strip()
            items = [x.strip() for x in codes.split(",") if x.strip()]
            categories[name] = [x for x in categories[name] if x not in items]
            save_categories(CONFIG_FILE, categories)
            print(f"{name} を更新しました: {', '.join(categories[name]) if categories[name] else '(空)'}")

        elif choice == "6":
            if last_df.empty:
                print("直近の取得結果がありません。先に 2 でデータを取得してください。")
            else:
                ensure_dirs()
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                xlsx = os.path.join(OUTPUT_DIR, f"quotes_{ts}.xlsx")
                export_to_excel_by_category(last_df, xlsx)

        elif choice == "0":
            print("終了しました。")
            sys.exit(0)
        else:
            print("無効な選択です。もう一度入力してください。")

if __name__ == "__main__":
    main()


import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 0) Excel から読み込み  ―  (ソース = Excel.Workbook …)
#     * 1 行目も 2 行目もスキップし、3 行目をデータとして扱う
# --------------------------------------------------
wb_path = Path(r"path")          # ファイルパス
sheet   = "sheetname"            # シート名

raw = pd.read_excel(             # ヘッダーは使わず丸ごと読む
    wb_path,
    sheet_name=sheet,
    header=None,                 # ヘッダー行なし
    engine="openpyxl"
)

df = raw.iloc[2:].copy()         # = Table.Skip(..., 2)

# --------------------------------------------------
# 1) 先頭 1 行だけ残す  ―  Table.FirstN(...,1)
# --------------------------------------------------
df = df.iloc[:1]

# --------------------------------------------------
# 2) aa 列を追加 (常に 1)  ―  Table.AddColumn(...,"aa", each 1)
# --------------------------------------------------
df["aa"] = 1

# --------------------------------------------------
# 3) melt で縦持ちに変換
#     = Table.UnpivotOtherColumns({ "aa" }, "属性", "値")
# --------------------------------------------------
# 列名を「Column1」「Column2」…と付け直しておくと
# 後の `Column` 置換ステップが分かりやすい
df.columns = [f"Column{i+1}" if col != "aa" else "aa"
              for i, col in enumerate(df.columns)]

df = (
    df.melt(id_vars=["aa"],
            var_name="属性",
            value_name="値")
      .copy()
)

# --------------------------------------------------
# 4) カスタム列の追加と属性列の整形
# --------------------------------------------------
df["カスタム"] = df["属性"]                     # = Table.AddColumn(...,"カスタム", each [属性])
df["属性"]    = df["属性"].str.replace("Column", "", regex=False)  # 置換
df["属性"]    = df["属性"].astype("int64")       # 型変換

# --------------------------------------------------
# 5) 不要列削除・並び替え・値のフィルダウン
# --------------------------------------------------
df = df.drop(columns=["aa"])                     # = Table.RemoveColumns
df = df.sort_values("属性").reset_index(drop=True)  # = Table.Sort
df["値"] = df["値"].fillna(method="ffill")       # = Table.FillDown

# --------------------------------------------------
# 6) 文字列化 → 置換 → 日付型へ
# --------------------------------------------------
df["値"] = (df["値"].astype(str)
                     .str.replace("2024", "2025", regex=False)  # 1 回目
                     .str.replace("2023", "2024", regex=False)) # 2 回目

df["値"] = pd.to_datetime(df["値"], errors="coerce")            # to date

# --------------------------------------------------
# 7) エラー (NaT) 行削除  ―  Table.RemoveRowsWithErrors
# --------------------------------------------------
df = df.dropna(subset=["値"]).reset_index(drop=True)

#   * Table.Buffer に相当する操作は pandas では不要です
# --------------------------------------------------
print(df.head())                 # これが M の `削除されたエラーB` と同内容

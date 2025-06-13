import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------
# 1) ソースの読み込み
# --------------------------------------------------
wb_path   = Path(r"path")        # Excel ファイルのフルパス
sheet     = "sheetname"          # 取り込みたいシート名

# ヘッダー行はそのまま残し、データの 1 行目をスキップ (=Table.Skip)
df = pd.read_excel(
    wb_path,
    sheet_name=sheet,
    header=0,            # 1 行目をヘッダーとして読む
    engine="openpyxl"
).iloc[1:].reset_index(drop=True)

# --------------------------------------------------
# 2) 「Column2」と「Column3」を結合し、新列「結合済み」を作成
#    (Table.CombineColumns + TransformColumnTypes)
# --------------------------------------------------
df["Column3"]   = df["Column3"].astype(str)
df["結合済み"] = df["Column2"].astype(str) + "-" + df["Column3"]
df.drop(["Column2", "Column3"], axis=1, inplace=True)

# --------------------------------------------------
# 3) Unpivot (=Table.UnpivotOtherColumns)
#    指定列以外を縦持ちにして「属性」「値」に
# --------------------------------------------------
id_cols = ["結合済み", "Column4", "Column5",
           "Column6", "Column18", "Column19", "Column22"]

df = (
    df.melt(id_vars=id_cols, var_name="属性", value_name="値")
      .astype({"値": "string", "Column4": "string"})
)

# --------------------------------------------------
# 4) エラー行削除 (Table.RemoveRowsWithErrors)  
#    → pandas では欠損(NaN)を除去するのが近い
# --------------------------------------------------
df = df.dropna(subset=["値"])

# --------------------------------------------------
# 5) 各種フィルタリング
# --------------------------------------------------
df = df[~df["値"].str.startswith("2023", na=False)]          # 値が"2023..."ではない
df = df[df["値"].isin(["process1", "process2"])]                        # 値が"process1"または"process2"

df["属性"] = df["属性"].str.replace("Column", "", regex=False)

df = df[~df["結合済み"].str.startswith("Fe",  na=False)]
df = df[~df["結合済み"].str.endswith("-",      na=False)]
df = df[~df["結合済み"].str.contains(",",      na=False)]

# --------------------------------------------------
# 6) 属性列を整数化し、偶数化 (=Table.AddColumn 等)
# --------------------------------------------------
df["属性"]   = df["属性"].astype(int)
df["カスタム"] = np.where(df["属性"] % 2 == 1, df["属性"] - 1, df["属性"])
df["カスタム"] = "Column" + df["カスタム"].astype(str)

# 属性→カスタムへの置き換え
df = (
    df.drop(columns="属性")
      .rename(columns={"カスタム": "属性"})
)

# --------------------------------------------------
# 7) lot_number の 1 桁を 2 桁に統一 (Table.ReplaceValue)
# --------------------------------------------------
df["結合済み"] = (
    df["結合済み"]
      .str.replace("lot_number-1", "lot_number-01", regex=False)
      .str.replace("lot_number-2", "lot_number-02", regex=False)
)

# --------------------------------------------------
# 8) query1 との結合 (Table.NestedJoin → ExpandTableColumn)
#    ※ query1 は別途 DataFrame として読み込んでおく想定
# --------------------------------------------------
#  例: query1 = pd.read_excel("query1.xlsx").rename(columns={...})
query1 = ...  # ここで DataFrame を用意して下さい

df = (
    df.merge(
        query1[["カスタム", "値"]]
             .rename(columns={"カスタム": "属性", "値": "query2.値"}),
        on="属性",
        how="left"
    )
)

# --------------------------------------------------
# 9) 完成
# --------------------------------------------------
# df には M で得られていた #"xxx" と同じ内容が入っています
print(df.head())

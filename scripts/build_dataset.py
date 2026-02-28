import os
import hashlib
import pandas as pd
import numpy as np

RAW_PATH = "data_raw/kaggle/avazu_train.csv"
OUT_EVENTS = "data_processed/ad_events_sample.csv"
OUT_DAILY = "data_processed/campaign_daily.csv"

# ===== 可调参数（先小后大）=====
MAX_ROWS = 20000            # 先用 2 万行，保证文件小、可提交
DAYS_WINDOW = 5
SEED = 42

# 模拟参数（为了支持 CPA/ROAS 演示）
BASE_CPC = 0.20
CPC_STD = 0.05
CVR_BASE = 0.05
AOV_BASE = 30.0
AOV_STD = 8.0

def stable_hash_to_int(s: str, mod: int) -> int:
    h = hashlib.md5(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % mod

def parse_avazu_hour_to_timestamp(hour_str: str) -> pd.Timestamp:
    # hour: YYMMDDHH，例如 14102100 -> 2014-10-21 00:00:00
    s = str(hour_str)
    yy = int(s[0:2]); mm = int(s[2:4]); dd = int(s[4:6]); hh = int(s[6:8])
    return pd.Timestamp(year=2000+yy, month=mm, day=dd, hour=hh)

def main():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"找不到原始文件：{RAW_PATH}")

    rng = np.random.default_rng(SEED)

    # 只读必要列（快很多）
    keep_cols = {"click", "hour", "C1", "C2", "C3", "C14"}
    df = pd.read_csv(RAW_PATH, usecols=lambda c: c in keep_cols)

    df["timestamp"] = df["hour"].astype(str).apply(parse_avazu_hour_to_timestamp)
    df["date"] = df["timestamp"].dt.date.astype(str)

    unique_dates = sorted(df["date"].unique().tolist())
    chosen_dates = unique_dates[:DAYS_WINDOW] if len(unique_dates) >= DAYS_WINDOW else unique_dates
    df = df[df["date"].isin(chosen_dates)].copy()

    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, random_state=SEED).copy()

    def mk_campaign(row):
        key = f"{row.get('C1','X')}_{row.get('C2','X')}"
        return f"cmp_{stable_hash_to_int(key, 5000)}"

    def mk_creative(row):
        key = f"{row.get('C3','X')}_{row.get('C14','X')}"
        return f"cr_{stable_hash_to_int(key, 20000)}"

    def mk_audience(row):
        key = f"{row.get('C2','X')}_{row.get('C14','X')}"
        return f"aud_{stable_hash_to_int(key, 10000)}"

    df["campaign_id"] = df.apply(mk_campaign, axis=1)
    df["creative_id"] = df.apply(mk_creative, axis=1)
    df["audience_id"] = df.apply(mk_audience, axis=1)

    df["geo"] = df["audience_id"].apply(lambda x: ["US","UK","CA","AU","SG"][stable_hash_to_int(x, 5)])
    df["device"] = df["audience_id"].apply(lambda x: ["ios","android","web"][stable_hash_to_int(x, 3)])

    df["clicked"] = df["click"].astype(int)

    impression_cost = rng.normal(loc=0.002, scale=0.001, size=len(df)).clip(0, None)
    cpc = rng.normal(loc=BASE_CPC, scale=CPC_STD, size=len(df)).clip(0.01, None)
    df["cost"] = (impression_cost + df["clicked"] * cpc).round(4)

    out_events = df[[
        "timestamp","campaign_id","creative_id","audience_id","geo","device","clicked","cost"
    ]].copy()
    os.makedirs(os.path.dirname(OUT_EVENTS), exist_ok=True)
    out_events.to_csv(OUT_EVENTS, index=False)

    daily = out_events.copy()
    daily["date"] = pd.to_datetime(daily["timestamp"]).dt.date.astype(str)

    agg = daily.groupby(["date","campaign_id"], as_index=False).agg(
        impressions=("clicked","size"),
        clicks=("clicked","sum"),
        spend=("cost","sum"),
    )

    cvrs = rng.normal(loc=CVR_BASE, scale=0.01, size=len(agg)).clip(0.01, 0.3)
    agg["conversions"] = (agg["clicks"] * cvrs).round().astype(int)

    aov = rng.normal(loc=AOV_BASE, scale=AOV_STD, size=len(agg)).clip(5, None)
    agg["revenue"] = (agg["conversions"] * aov).round(2)
    agg["spend"] = agg["spend"].round(2)

    os.makedirs(os.path.dirname(OUT_DAILY), exist_ok=True)
    agg.to_csv(OUT_DAILY, index=False)

    print("✅ 生成完成：")
    print(f"- {OUT_EVENTS} (rows={len(out_events)})")
    print(f"- {OUT_DAILY} (rows={len(agg)})")

if __name__ == "__main__":
    main()

import os
import numpy as np
import pandas as pd

IN_PATH = "data_processed/campaign_daily.csv"
OUT_PATH = "data_processed/campaign_daily_anomaly.csv"

SEED = 42

# ===== 可控生成（按图：conversions / revenue）=====
BASE_CVR = 0.06
CVR_NOISE_STD = 0.01

AOV_BASE = 35.0
AOV_NOISE_STD = 6.0

# ===== 3 类异常注入强度 =====
CVR_DROP_RATIO = 0.45    # 质量变：CVR 下滑
CTR_DROP_RATIO = 0.35    # 上游掉：CTR 下滑
SPEND_SPIKE_RATIO = 0.70 # 浪费：spend 飙升但 revenue 不涨

def main():
    if not os.path.exists(IN_PATH):
        raise FileNotFoundError(f"找不到输入文件：{IN_PATH}")

    rng = np.random.default_rng(SEED)
    df = pd.read_csv(IN_PATH)

    required = {"date","campaign_id","impressions","clicks","spend"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"campaign_daily 缺少字段：{missing}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date","campaign_id"]).reset_index(drop=True)

    unique_dates = sorted(df["date"].dt.date.unique().tolist())
    if len(unique_dates) < 4:
        raise ValueError("日期太少，至少需要 4 天才能注入异常")

    # 选中间偏后一天作为异常开始日（让前后对比明显）
    start_date = pd.to_datetime(unique_dates[len(unique_dates)//2])

    # 选 3 个 campaign_id 作为“人群/素材/地域”的代理（对应图里的 3 个异常）
    campaigns = sorted(df["campaign_id"].unique().tolist())
    if len(campaigns) < 3:
        raise ValueError("campaign_id 数量太少（至少 3 个）")

    target_audience = campaigns[0]  # 人群代理
    target_creative = campaigns[1]  # 素材代理
    target_geo = campaigns[2]       # 地域代理

    # ===== 1) 可控生成 conversions / revenue =====
    cvr = rng.normal(loc=BASE_CVR, scale=CVR_NOISE_STD, size=len(df))
    cvr = np.clip(cvr, 0.005, 0.30)

    conv = df["clicks"].to_numpy() * cvr
    conv = conv + rng.normal(loc=0.0, scale=np.maximum(1.0, conv*0.05), size=len(df))
    conv = np.clip(np.round(conv), 0, None).astype(int)
    df["conversions"] = conv

    aov = rng.normal(loc=AOV_BASE, scale=AOV_NOISE_STD, size=len(df))
    aov = np.clip(aov, 5.0, None)

    rev = df["conversions"].to_numpy() * aov
    rev = rev + rng.normal(loc=0.0, scale=np.maximum(1.0, rev*0.05), size=len(df))
    rev = np.clip(np.round(rev, 2), 0, None)
    df["revenue"] = rev

    # ===== 2) 注入 3 类异常（从 start_date 起）=====
    # 异常1：某类人群 CVR 下滑（质量变）
    mask1 = (df["date"] >= start_date) & (df["campaign_id"] == target_audience)
    df.loc[mask1, "conversions"] = np.floor(df.loc[mask1, "conversions"] * (1 - CVR_DROP_RATIO)).astype(int)
    df.loc[mask1, "revenue"] = np.round(df.loc[mask1, "revenue"] * (1 - CVR_DROP_RATIO), 2)

    # 异常2：某素材 CTR 下滑（上游掉）=> clicks 下降（impressions 不变）
    mask2 = (df["date"] >= start_date) & (df["campaign_id"] == target_creative)
    df.loc[mask2, "clicks"] = np.floor(df.loc[mask2, "clicks"] * (1 - CTR_DROP_RATIO)).astype(int)
    df.loc[mask2, "conversions"] = np.floor(df.loc[mask2, "conversions"] * (1 - CTR_DROP_RATIO)).astype(int)
    df.loc[mask2, "revenue"] = np.round(df.loc[mask2, "revenue"] * (1 - CTR_DROP_RATIO), 2)

    # 异常3：某地域 spend 飙升但 revenue 不涨（浪费）
    mask3 = (df["date"] >= start_date) & (df["campaign_id"] == target_geo)
    df.loc[mask3, "spend"] = np.round(df.loc[mask3, "spend"] * (1 + SPEND_SPIKE_RATIO), 2)

    # ===== 3) 计算衍生指标（便于你验证 ROI 掉了）=====
    df["ctr"] = np.where(df["impressions"] > 0, df["clicks"] / df["impressions"], np.nan)
    df["cvr"] = np.where(df["clicks"] > 0, df["conversions"] / df["clicks"], np.nan)
    df["cpa"] = np.where(df["conversions"] > 0, df["spend"] / df["conversions"], np.nan)
    df["roas"] = np.where(df["spend"] > 0, df["revenue"] / df["spend"], np.nan)
    df["roi"] = np.where(df["spend"] > 0, (df["revenue"] - df["spend"]) / df["spend"], np.nan)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out = df.copy()
    out["date"] = out["date"].dt.date.astype(str)
    out.to_csv(OUT_PATH, index=False)

    print("✅ Day3 生成完成：")
    print(f"- 输出：{OUT_PATH} (rows={len(out)})")
    print("✅ 注入异常：")
    print(f"  1) CVR 下滑（质量变）：campaign_id={target_audience}，从 {start_date.date()} 起")
    print(f"  2) CTR 下滑（上游掉）：campaign_id={target_creative}，从 {start_date.date()} 起")
    print(f"  3) spend 飙升不增收（浪费）：campaign_id={target_geo}，从 {start_date.date()} 起")

if __name__ == "__main__":
    main()

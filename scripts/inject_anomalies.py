cat > scripts/inject_anomalies.py <<'EOF'
import os
import numpy as np
import pandas as pd

IN_PATH = "data_processed/campaign_daily.csv"
OUT_PATH = "data_processed/campaign_daily_anomaly.csv"

SEED = 42

# ===== 你可以调的全局参数 =====
BASE_CVR = 0.06          # 点击->转化基础率
CVR_NOISE_STD = 0.01     # CVR 噪声
AOV_BASE = 35.0          # 客单价
AOV_NOISE_STD = 6.0      # AOV 噪声

# ===== 异常注入参数（按图的 3 类）=====
ANOMALY_START_DATE = None   # 不写死，脚本会自动选中间日期
CVR_DROP_RATIO = 0.45       # CVR 下滑（质量变）：乘以 (1-0.45)=0.55
CTR_DROP_RATIO = 0.35       # CTR 下滑（上游掉）：点击乘以 (1-0.35)=0.65
SPEND_SPIKE_RATIO = 0.70    # spend 飙升（浪费）：spend 乘以 1.70

def main():
    if not os.path.exists(IN_PATH):
        raise FileNotFoundError(f"找不到输入文件：{IN_PATH}")

    rng = np.random.default_rng(SEED)
    df = pd.read_csv(IN_PATH)

    # 基础校验
    required = {"date","campaign_id","impressions","clicks","spend"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"campaign_daily 缺少字段：{missing}")

    # 日期排序
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date","campaign_id"]).reset_index(drop=True)

    # 选择异常开始日期：默认取时间序列中间偏后的一天
    unique_dates = sorted(df["date"].dt.date.unique().tolist())
    if len(unique_dates) < 4:
        raise ValueError("日期太少，无法注入异常（至少 4 天）")

    start_date = ANOMALY_START_DATE
    if start_date is None:
        start_date = unique_dates[len(unique_dates)//2]
    start_date = pd.to_datetime(start_date)

    # 选择 3 个目标（campaign / creative / geo 的代理维度）
    # 你现在的 campaign_daily 只有 campaign_id 维度，所以我们用“不同 campaign_id”来分别代表：
    # - 某类人群（audience proxy）
    # - 某素材（creative proxy）
    # - 某地域（geo proxy）
    campaigns = sorted(df["campaign_id"].unique().tolist())
    if len(campaigns) < 3:
        raise ValueError("campaign_id 数量太少（至少 3 个）")

    target_audience = campaigns[0]  # 用 campaign_id 代理“人群”
    target_creative = campaigns[1]  # 用 campaign_id 代理“素材”
    target_geo = campaigns[2]       # 用 campaign_id 代理“地域”

    # ===== 1) 先生成“可控”的 conversions/revenue =====
    # CVR：base + 噪声（每行）
    cvr = rng.normal(loc=BASE_CVR, scale=CVR_NOISE_STD, size=len(df))
    cvr = np.clip(cvr, 0.005, 0.3)

    # conversions = clicks * cvr + 噪声
    conv = (df["clicks"].to_numpy() * cvr)
    conv = conv + rng.normal(loc=0.0, scale=np.maximum(1.0, conv*0.05), size=len(df))
    conv = np.clip(np.round(conv), 0, None).astype(int)
    df["conversions"] = conv

    # AOV：base + 噪声（每行）
    aov = rng.normal(loc=AOV_BASE, scale=AOV_NOISE_STD, size=len(df))
    aov = np.clip(aov, 5.0, None)

    rev = df["conversions"].to_numpy() * aov
    rev = rev + rng.normal(loc=0.0, scale=np.maximum(1.0, rev*0.05), size=len(df))
    rev = np.clip(np.round(rev, 2), 0, None)
    df["revenue"] = rev

    # ===== 2) 注入 3 类异常（从 start_date 起生效）=====
    # 异常1：某类人群 CVR 下滑（质量变）
    mask1 = (df["date"] >= start_date) & (df["campaign_id"] == target_audience)
    df.loc[mask1, "conversions"] = np.floor(df.loc[mask1, "conversions"] * (1 - CVR_DROP_RATIO)).astype(int)
    # revenue 同步下降
    df.loc[mask1, "revenue"] = np.round(df.loc[mask1, "revenue"] * (1 - CVR_DROP_RATIO), 2)

    # 异常2：某素材 CTR 下滑（上游掉） -> clicks 下降（impressions 保持）
    mask2 = (df["date"] >= start_date) & (df["campaign_id"] == target_creative)
    df.loc[mask2, "clicks"] = np.floor(df.loc[mask2, "clicks"] * (1 - CTR_DROP_RATIO)).astype(int)
    # clicks 变了，conversions/revenue 也要按比例缩小（保持 CVR 大致不变）
    df.loc[mask2, "conversions"] = np.floor(df.loc[mask2, "conversions"] * (1 - CTR_DROP_RATIO)).astype(int)
    df.loc[mask2, "revenue"] = np.round(df.loc[mask2, "revenue"] * (1 - CTR_DROP_RATIO), 2)

    # 异常3：某地域 spend 飙升但 revenue 不涨（浪费） -> spend 上升，revenue 不变
    mask3 = (df["date"] >= start_date) & (df["campaign_id"] == target_geo)
    df.loc[mask3, "spend"] = np.round(df.loc[mask3, "spend"] * (1 + SPEND_SPIKE_RATIO), 2)
    # revenue 保持，形成 ROAS/ROI 下降

    # ===== 3) 计算衍生指标（方便你检查 ROI 掉了）=====
    df["impressions"] = df["impressions"].astype(int)
    df["clicks"] = df["clicks"].astype(int)
    df["spend"] = df["spend"].astype(float)

    df["ctr"] = np.where(df["impressions"] > 0, df["clicks"] / df["impressions"], np.nan)
    df["cvr"] = np.where(df["clicks"] > 0, df["conversions"] / df["clicks"], np.nan)
    df["cpa"] = np.where(df["conversions"] > 0, df["spend"] / df["conversions"], np.nan)
    df["roas"] = np.where(df["spend"] > 0, df["revenue"] / df["spend"], np.nan)
    df["roi"] = np.where(df["spend"] > 0, (df["revenue"] - df["spend"]) / df["spend"], np.nan)

    # 输出
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df_out = df.copy()
    df_out["date"] = df_out["date"].dt.date.astype(str)
    df_out.to_csv(OUT_PATH, index=False)

    print("✅ Day3 生成完成：")
    print(f"- 输出：{OUT_PATH} (rows={len(df_out)})")
    print("✅ 注入异常：")
    print(f"  1) CVR 下滑（质量变）：campaign_id={target_audience}，从 {start_date.date()} 起")
    print(f"  2) CTR 下滑（上游掉）：campaign_id={target_creative}，从 {start_date.date()} 起")
    print(f"  3) spend 飙升不增收（浪费）：campaign_id={target_geo}，从 {start_date.date()} 起")

if __name__ == "__main__":
    main()
EOF

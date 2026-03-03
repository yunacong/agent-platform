import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", message="Mean of empty slice")
from typing import Any, Dict, List, Optional

DATA_PATH = "data_processed/campaign_daily_anomaly.csv"

ALLOWED_GROUP_BY = {"date","campaign_id"}
ALLOWED_FILTERS = {"campaign_id"}

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df

def apply_date_range(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    s = pd.to_datetime(start)
    e = pd.to_datetime(end)
    return df[(df["date"] >= s) & (df["date"] <= e)].copy()

def apply_filters(df: pd.DataFrame, filters: Optional[Dict[str, Any]]) -> pd.DataFrame:
    if not filters:
        return df
    for k, v in filters.items():
        if k not in ALLOWED_FILTERS:
            raise ValueError(f"Unsupported filter: {k}")
        df = df[df[k] == v]
    return df

def query_metrics(metric: str, group_by: Optional[List[str]], filters: Optional[Dict[str, Any]], start: str, end: str):
    df = load_data()
    df = apply_date_range(df, start, end)
    df = apply_filters(df, filters)

    if group_by:
        for g in group_by:
            if g not in ALLOWED_GROUP_BY:
                raise ValueError(f"Unsupported group_by: {g}")
        agg_map = {metric: "sum"} if metric in ["impressions","clicks","spend","conversions","revenue"] else {metric: "mean"}
        out = df.groupby(group_by, as_index=False).agg(agg_map)
    else:
        # 不分组就返回汇总一行
        if metric in ["impressions","clicks","spend","conversions","revenue"]:
            val = float(df[metric].sum())
        else:
            val = float(np.nanmean(df[metric].to_numpy()))
        out = pd.DataFrame([{metric: val}])

    # date 转回字符串
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"]).dt.date.astype(str)

    return out.to_dict(orient="records")

def _window_split(df: pd.DataFrame, start_date: pd.Timestamp, baseline_days: int, compare_days: int):
    # baseline: start_date 前 baseline_days 天
    # compare: start_date 起 compare_days 天
    all_dates = sorted(df["date"].dt.date.unique().tolist())
    all_dates = [pd.to_datetime(d) for d in all_dates]
    if start_date not in all_dates:
        # 若 start_date 不在数据里，使用最接近的后一日
        all_dates_sorted = sorted(all_dates)
        start_date = next((d for d in all_dates_sorted if d >= start_date), all_dates_sorted[-1])

    idx = all_dates.index(start_date)
    b_start = max(0, idx - baseline_days)
    b_dates = all_dates[b_start:idx]
    c_dates = all_dates[idx: idx + compare_days]

    baseline = df[df["date"].isin(b_dates)]
    compare = df[df["date"].isin(c_dates)]
    return baseline, compare, [d.date().isoformat() for d in b_dates], [d.date().isoformat() for d in c_dates]

def detect_anomaly(metric: str, group_by: Optional[str], start: str, end: str, baseline_days: int, compare_days: int, threshold_pct: float):
    df = load_data()
    df = apply_date_range(df, start, end)

    # 用范围中间偏后一天作为 start_date（跟 Day3 逻辑一致）
    dates = sorted(df["date"].dt.date.unique().tolist())
    if len(dates) < 4:
        raise ValueError("Not enough dates to detect anomalies")
    start_date = pd.to_datetime(dates[len(dates)//2])

    results = []

    if group_by is None:
        baseline, compare, b_dates, c_dates = _window_split(df, start_date, baseline_days, compare_days)
        b = float(np.nanmean(baseline[metric])) if metric not in ["impressions","clicks","spend","conversions","revenue"] else float(baseline[metric].sum())
        c = float(np.nanmean(compare[metric])) if metric not in ["impressions","clicks","spend","conversions","revenue"] else float(compare[metric].sum())
        pct = None if b == 0 else (c - b) / b
        if pct is not None and abs(pct) >= threshold_pct:
            results.append({"key": "ALL", "baseline": b, "compare": c, "pct_change": pct, "baseline_dates": b_dates, "compare_dates": c_dates})
    else:
        if group_by not in ["campaign_id"]:
            raise ValueError("group_by only supports campaign_id for now")

        for key, g in df.groupby(group_by):
            baseline, compare, b_dates, c_dates = _window_split(g, start_date, baseline_days, compare_days)
            if len(baseline) == 0 or len(compare) == 0:
                continue
            b = float(np.nanmean(baseline[metric])) if metric not in ["impressions","clicks","spend","conversions","revenue"] else float(baseline[metric].sum())
            c = float(np.nanmean(compare[metric])) if metric not in ["impressions","clicks","spend","conversions","revenue"] else float(compare[metric].sum())
            pct = None if b == 0 else (c - b) / b
            if pct is not None and abs(pct) >= threshold_pct:
                results.append({"key": key, "baseline": b, "compare": c, "pct_change": pct, "baseline_dates": b_dates, "compare_dates": c_dates})

        # 按影响排序（变化幅度绝对值）
        results.sort(key=lambda x: abs(x["pct_change"]), reverse=True)

    return start_date.date().isoformat(), results

def slice_compare(metric: str, dim: str, b_start: str, b_end: str, c_start: str, c_end: str, top_k: int):
    if dim != "campaign_id":
        raise ValueError("dim only supports campaign_id for now")

    df = load_data()
    b = apply_date_range(df, b_start, b_end)
    c = apply_date_range(df, c_start, c_end)

    def total(frame: pd.DataFrame):
        if metric in ["impressions","clicks","spend","conversions","revenue"]:
            return float(frame[metric].sum())
        return float(np.nanmean(frame[metric].to_numpy()))

    b_total = total(b)
    c_total = total(c)

    # 分维度值
    if metric in ["impressions","clicks","spend","conversions","revenue"]:
        b_by = b.groupby(dim, as_index=False)[metric].sum().rename(columns={metric:"baseline"})
        c_by = c.groupby(dim, as_index=False)[metric].sum().rename(columns={metric:"compare"})
    else:
        b_by = b.groupby(dim, as_index=False)[metric].mean().rename(columns={metric:"baseline"})
        c_by = c.groupby(dim, as_index=False)[metric].mean().rename(columns={metric:"compare"})

    merged = b_by.merge(c_by, on=dim, how="outer").fillna(0.0)
    merged["delta"] = merged["compare"] - merged["baseline"]

    # 贡献度：看谁对整体变化贡献最大（按 delta 排序）
    merged["contribution"] = merged["delta"]
    merged = merged.sort_values("contribution")

    # 取 top_k 负贡献（导致下滑的）优先
    contrib_rows = merged.head(top_k).to_dict(orient="records")

    return {
        "baseline_summary": {"start": b_start, "end": b_end, metric: b_total},
        "compare_summary": {"start": c_start, "end": c_end, metric: c_total},
        "contributions": contrib_rows
    }

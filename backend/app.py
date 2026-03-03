from fastapi import FastAPI, HTTPException
from backend.models import (
    QueryMetricsRequest, QueryMetricsResponse,
    DetectAnomalyRequest, DetectAnomalyResponse,
    SliceCompareRequest, SliceCompareResponse
)
from backend.service import query_metrics, detect_anomaly, slice_compare

app = FastAPI(title="Agent Platform Tools API", version="0.1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query_metrics", response_model=QueryMetricsResponse)
def api_query_metrics(req: QueryMetricsRequest):
    try:
        rows = query_metrics(
            metric=req.metric,
            group_by=req.group_by,
            filters=req.filters,
            start=req.date_range.start,
            end=req.date_range.end,
        )
        return {"rows": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/detect_anomaly", response_model=DetectAnomalyResponse)
def api_detect_anomaly(req: DetectAnomalyRequest):
    try:
        start_date, anomalies = detect_anomaly(
            metric=req.metric,
            group_by=req.group_by,
            start=req.date_range.start,
            end=req.date_range.end,
            baseline_days=req.baseline_days,
            compare_days=req.compare_days,
            threshold_pct=req.threshold_pct,
        )
        return {"metric": req.metric, "start_date": start_date, "anomalies": anomalies}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/slice_compare", response_model=SliceCompareResponse)
def api_slice_compare(req: SliceCompareRequest):
    try:
        out = slice_compare(
            metric=req.metric,
            dim=req.dim,
            b_start=req.baseline_range.start,
            b_end=req.baseline_range.end,
            c_start=req.compare_range.start,
            c_end=req.compare_range.end,
            top_k=req.top_k,
        )
        return {"metric": req.metric, "dim": req.dim, **out}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

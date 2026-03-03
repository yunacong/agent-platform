from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal

MetricName = Literal["impressions","clicks","spend","conversions","revenue","ctr","cvr","cpa","roas","roi"]

class DateRange(BaseModel):
    start: str = Field(..., description="YYYY-MM-DD")
    end: str = Field(..., description="YYYY-MM-DD (inclusive)")

class QueryMetricsRequest(BaseModel):
    metric: MetricName
    group_by: Optional[List[str]] = Field(default=None, description="支持: date, campaign_id")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="例如 {campaign_id: 'cmp_1000'}")
    date_range: DateRange

class QueryMetricsResponse(BaseModel):
    rows: List[Dict[str, Any]]

class DetectAnomalyRequest(BaseModel):
    metric: MetricName
    group_by: Optional[str] = Field(default=None, description="支持: campaign_id（可选）")
    date_range: DateRange
    baseline_days: int = Field(default=2, description="基线窗口大小（天）")
    compare_days: int = Field(default=2, description="对比窗口大小（天）")
    threshold_pct: float = Field(default=0.2, description="触发阈值：变化百分比，例如 0.2=20%")

class DetectAnomalyResponse(BaseModel):
    metric: MetricName
    start_date: str
    anomalies: List[Dict[str, Any]]

class SliceCompareRequest(BaseModel):
    metric: MetricName
    dim: str = Field(..., description="支持: campaign_id")
    baseline_range: DateRange
    compare_range: DateRange
    top_k: int = 10

class SliceCompareResponse(BaseModel):
    metric: MetricName
    dim: str
    baseline_summary: Dict[str, Any]
    compare_summary: Dict[str, Any]
    contributions: List[Dict[str, Any]]

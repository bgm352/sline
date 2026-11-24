from dataclasses import dataclass
from typing import Tuple
import cv2
import numpy as np


@dataclass
class CenteringResult:
    left_right_ratio: Tuple[float, float]
    top_bottom_ratio: Tuple[float, float]
    passes_psa_10_front: bool
    passes_psa_9_front: bool
    verdict: str


def measure_centering_from_borders(
    left_px: float,
    right_px: float,
    top_px: float,
    bottom_px: float,
) -> CenteringResult:
    """Calculates L/R and T/B centering percentages and checks PSA 10 (55/45) & PSA 9 (60/40) gates."""
    lr_total = max(left_px + right_px, 1e-6)
    tb_total = max(top_px + bottom_px, 1e-6)

    l_pct = round((left_px / lr_total) * 100, 1)
    r_pct = round((right_px / lr_total) * 100, 1)
    t_pct = round((top_px / tb_total) * 100, 1)
    b_pct = round((bottom_px / tb_total) * 100, 1)

    max_lr = max(l_pct, r_pct)
    max_tb = max(t_pct, b_pct)

    passes_10 = max_lr <= 55.0 and max_tb <= 55.0
    passes_9 = max_lr <= 60.0 and max_tb <= 60.0

    if passes_10:
        verdict = "PSA 10 Centering Eligible (<= 55/45)"
    elif passes_9:
        verdict = "PSA 9 Centering Range (<= 60/40)"
    else:
        verdict = "Off-Center (> 60/40) — High risk for PSA 8 or lower"

    return CenteringResult(
        left_right_ratio=(l_pct, r_pct),
        top_bottom_ratio=(t_pct, b_pct),
        passes_psa_10_front=passes_10,
        passes_psa_9_front=passes_9,
        verdict=verdict,
    )


def estimate_borders_opencv(image_bytes: bytes) -> Tuple[float, float, float, float]:
    """
    Quick automated border estimator using edge detection.
    Returns (left_px, right_px, top_px, bottom_px) as a starting point for manual fine-tuning.
    """
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return (50.0, 50.0, 50.0, 50.0)

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)

    mid_y, mid_x = h // 2, w // 2
    row = edges[mid_y, :]
    col = edges[:, mid_x]

    nz_x = np.where(row > 0)[0]
    nz_y = np.where(col > 0)[0]

    left_px = float(nz_x[0]) if len(nz_x) > 1 else w * 0.08
    right_px = float(w - nz_x[-1]) if len(nz_x) > 1 else w * 0.08
    top_px = float(nz_y[0]) if len(nz_y) > 1 else h * 0.08
    bottom_px = float(h - nz_y[-1]) if len(nz_y) > 1 else h * 0.08

    return (max(left_px, 1.0), max(right_px, 1.0), max(top_px, 1.0), max(bottom_px, 1.0))

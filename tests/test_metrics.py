import pytest
import numpy as np
from demand_taxonomy.metrics import calculate_adi, calculate_cv2, get_behavior_segment

def test_calculate_adi():
    # Demand every period
    assert calculate_adi([10, 10, 10, 10]) == 1.0
    # Demand every 2nd period
    assert calculate_adi([10, 0, 10, 0]) == 2.0
    # No demand
    assert calculate_adi([0, 0, 0]) == float('inf')

def test_calculate_cv2():
    # Stable demand (CV2 = 0)
    assert calculate_cv2([10, 10, 10]) == 0.0
    # Variable demand
    # mean = 10, std = 0 -> CV2 = 0
    # let's try mean = 10, non-zero are [5, 15]
    # mean_nz = 10, std_nz = 5
    # CV2 = (5/10)^2 = 0.25
    assert calculate_cv2([5, 15, 0, 0]) == 0.25

def test_get_behavior_segment():
    # Stable: Low ADI (< 1.32), Low CV2 (< 0.49)
    assert get_behavior_segment(1.1, 0.2) == "STABLE"
    # Erratic: Low ADI, High CV2
    assert get_behavior_segment(1.1, 0.6) == "ERRATIC"
    # Intermittent: High ADI, Low CV2
    assert get_behavior_segment(2.0, 0.2) == "INTERMITTENT"
    # Lumpy: High ADI, High CV2
    assert get_behavior_segment(2.0, 0.6) == "LUMPY"

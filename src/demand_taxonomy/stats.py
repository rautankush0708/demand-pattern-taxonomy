import numpy as np

def mann_kendall_test(x):
    """
    Perform a simplified Mann-Kendall Trend Test.
    
    Args:
        x (list or np.array): Time series data.
        
    Returns:
        tuple: (slope, p_value_estimate)
        Note: p_value_estimate is a simplified approximation based on Z-score.
    """
    n = len(x)
    if n < 3:
        return 0.0, 1.0
        
    # Calculate S statistic
    s = 0
    for j in range(1, n):
        for i in range(j):
            diff = x[j] - x[i]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1
                
    # Calculate Variance
    # (Simplified: doesn't handle tied groups for this first version)
    var_s = (n * (n - 1) * (2 * n + 5)) / 18
    
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s == 0:
        z = 0
    else:
        z = (s + 1) / np.sqrt(var_s)
        
    # Approximation of p-value from Z-score (Standard Normal)
    # Using a simple approximation for the CDF of the normal distribution
    p_value = 2 * (1 - (0.5 * (1 + np.erf(np.abs(z) / np.sqrt(2)))))
    
    # Calculate Theil-Sen Slope (Median of all pairwise slopes)
    slopes = []
    for j in range(1, n):
        for i in range(j):
            if j != i:
                slopes.append((x[j] - x[i]) / (j - i))
    
    slope = np.median(slopes) if slopes else 0.0
    
    return slope, p_value

def detect_trend(demand_series, p_threshold=0.05):
    """
    Categorize trend based on Mann-Kendall results.
    
    Returns:
        str: GROWTH, DECLINE, or STABLE
    """
    slope, p = mann_kendall_test(demand_series)
    
    if p < p_threshold:
        if slope > 0:
            return "GROWTH"
        else:
            return "DECLINE"
    return "STABLE"

import numpy as np

def calculate_adi(demand_series):
    """
    Calculate the Average Demand Interval (ADI).
    
    Formula: Total Periods / Number of Non-Zero Demand Periods
    
    Args:
        demand_series (list or np.array): Time series of demand.
        
    Returns:
        float: The ADI value.
    """
    demand = np.array(demand_series)
    total_periods = len(demand)
    non_zero_periods = np.count_nonzero(demand)
    
    if non_zero_periods == 0:
        return float('inf')
        
    return total_periods / non_zero_periods

def calculate_cv2(demand_series):
    """
    Calculate the Squared Coefficient of Variation (CV²).
    
    Formula: (std_nz / mean_nz)^2
    
    Args:
        demand_series (list or np.array): Time series of demand.
        
    Returns:
        float: The CV² value.
    """
    demand = np.array(demand_series)
    non_zero_demand = demand[demand > 0]
    
    if len(non_zero_demand) == 0:
        return 0.0
        
    mean_nz = np.mean(non_zero_demand)
    std_nz = np.std(non_zero_demand)
    
    if mean_nz == 0:
        return 0.0
        
    return (std_nz / mean_nz) ** 2

def get_behavior_segment(adi, cv2, thresholds={'adi': 1.32, 'cv2': 0.49}):
    """
    Categorize SKU behavior based on ADI and CV².
    
    Args:
        adi (float): Calculated ADI.
        cv2 (float): Calculated CV².
        thresholds (dict): ADI and CV² thresholds (default to Weekly taxonomy standards).
        
    Returns:
        str: Segment name (STABLE, ERRATIC, INTERMITTENT, LUMPY)
    """
    is_regular = adi < thresholds['adi']
    is_smooth = cv2 < thresholds['cv2']
    
    if is_regular and is_smooth:
        return "STABLE"
    elif is_regular and not is_smooth:
        return "ERRATIC"
    elif not is_regular and is_smooth:
        return "INTERMITTENT"
    else:
        return "LUMPY"

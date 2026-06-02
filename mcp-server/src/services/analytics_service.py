from typing import Dict, Any, Optional

def calculate_variation(current: float, previous: float) -> Dict[str, Any]:
    if previous == 0:
        return {
            "variation_percentage": None,
            "direction": "undefined",
            "message": "Comparison base is zero"
        }
    
    variation = ((current - previous) / previous) * 100
    
    direction = "stable"
    if variation > 0.01:
        direction = "increase"
    elif variation < -0.01:
        direction = "decrease"
        
    return {
        "variation_percentage": round(variation, 2),
        "direction": direction
    }

#!/usr/bin/env python3
"""
Test script to directly test the PlanModel without going through API
"""
import json
import os
import sys
from datetime import datetime, timedelta

# Add the src directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Import the plan model
from ai.model.src.agents.plan_model import PlanModel

def main():
    # Sample input data with multiple locations
    sample_input = {
        "destination": "Đà Nẵng",
        "accommodations": [
            {
                "id": "hotel1", 
                "name": "Sala Danang Beach Hotel", 
                "price": 850000, 
                "description": "Khách sạn 4 sao với tầm nhìn ra biển",
                "location": "Bãi biển Mỹ Khê"
            }
        ],
        "places": [
            {
                "id": "place1", 
                "name": "Bãi biển Mỹ Khê", 
                "description": "Bãi biển cát trắng đẹp với nước biển trong xanh"
            },
            {
                "id": "place2", 
                "name": "Bà Nà Hills", 
                "description": "Khu nghỉ dưỡng trên núi với Cầu Vàng nổi tiếng"
            },
            {
                "id": "place3", 
                "name": "Ngũ Hành Sơn", 
                "description": "Danh thắng với các hang động đá vôi và chùa cổ"
            }
        ],
        "restaurants": [
            {
                "id": "rest1", 
                "name": "Nhà hàng Bé Mặn", 
                "description": "Nhà hàng hải sản địa phương nổi tiếng"
            },
            {
                "id": "rest2", 
                "name": "Quán Mít", 
                "description": "Quán ăn phục vụ các món Việt Nam truyền thống"
            }
        ]
    }

    # Use fixed specific dates for a 3-day trip
    meta = {
        "trip_name": "Kỳ nghỉ Đà Nẵng 3 ngày",
        "start_date": "2023-06-15",
        "end_date": "2023-06-18",
        "user_id": "user123",
        "note": "Hãy tạo lịch trình cụ thể cho 3 ngày đầy đủ từ 15/6 đến 18/6"
    }

    # Initialize the plan model with lower temperature for more consistency
    print("Initializing PlanModel...")
    planner = PlanModel(temperature=0.5)
    
    print("Generating travel plan...")
    print(f"Input data: Destination={sample_input['destination']}, Places={len(sample_input['places'])}, Restaurants={len(sample_input['restaurants'])}")
    print(f"Date range: {meta['start_date']} to {meta['end_date']}")
    
    # Generate the plan
    plan = planner.generate_plan(sample_input, **meta)
    
    # Print a summary of the plan
    print("\n=== Travel Plan Summary ===")
    print(f"Trip Name: {plan.get('trip_name', 'N/A')}")
    print(f"Destination: {plan.get('destination', 'N/A')}")
    print(f"Start Date: {plan.get('start_date', 'N/A')}")
    print(f"End Date: {plan.get('end_date', 'N/A')}")
    
    # Print plan by day summary
    days = plan.get('plan_by_day', [])
    print(f"\nTotal Days: {len(days)}")
    
    for i, day in enumerate(days):
        print(f"\nDay {i+1}: {day.get('day_title', '')}")
        print(f"Date: {day.get('date', 'N/A')}")
        segments = day.get('segments', [])
        
        print(f"Segments: {len(segments)}")
        for segment in segments:
            time_of_day = segment.get('time_of_day', '')
            activities = segment.get('activities', [])
            
            if activities:
                print(f"  {time_of_day.capitalize()} ({len(activities)} activities):")
                for activity in activities:
                    print(f"    - {activity.get('name', '')} ({activity.get('type', '')})")
    
    # Save the complete plan to a JSON file
    output_file = "test_plan_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"\nComplete plan saved to {output_file}")

if __name__ == "__main__":
    main() 
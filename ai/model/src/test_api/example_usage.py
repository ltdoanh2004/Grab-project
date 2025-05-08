#!/usr/bin/env python3
"""
Example script demonstrating how to use the PlanModel class
for generating travel plans with LangChain integration.
"""
import json
import os
from ai.model.src.agents.plan_agent import PlanModel

def print_plan_summary(plan):
    """Print a summary of the generated plan."""
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
        segments = day.get('segments', [])
        
        for segment in segments:
            time_of_day = segment.get('time_of_day', '')
            activities = segment.get('activities', [])
            
            if activities:
                print(f"  {time_of_day.capitalize()} ({len(activities)} activities):")
                for activity in activities:
                    print(f"    - {activity.get('name', '')} ({activity.get('type', '')})")

def save_plan_to_file(plan, filename="travel_plan.json"):
    """Save the plan to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"\nFull plan saved to {filename}")

def demo_basic_plan():
    """Demonstrate generating a basic travel plan."""
    print("\n=== Generating Basic Travel Plan ===")
    
    # Sample input data
    sample_input = {
        "accommodations": [
            {"id": "hotel1", "name": "Sala Danang Beach Hotel", "price": 850000, "description": "4-star hotel with sea view"}
        ],
        "places": [
            {"id": "place1", "name": "Bãi biển Mỹ Khê", "description": "Beautiful beach with white sand"},
            {"id": "place2", "name": "Bà Nà Hills", "description": "Mountain resort with Golden Bridge"}
        ],
        "restaurants": [
            {"id": "rest1", "name": "Nhà hàng Bé Mặn", "description": "Local seafood restaurant"},
            {"id": "rest2", "name": "Bamboo 2 Restaurant", "description": "Vietnamese cuisine"}
        ]
    }
    
    # Create planner and generate plan
    planner = PlanModel()
    plan = planner.generate_plan(
        sample_input,
        trip_name="Đà Nẵng Vacation",
        destination="Đà Nẵng",
        start_date="2023-10-15",
        end_date="2023-10-18"
    )
    
    # Print and save the plan
    print_plan_summary(plan)
    save_plan_to_file(plan, "basic_plan.json")

def demo_plan_with_tools():
    """Demonstrate generating a travel plan using tools."""
    print("\n=== Generating Travel Plan With Tools ===")
    
    # Sample input data
    sample_input = {
        "accommodations": [
            {"id": "hotel2", "name": "AVORA Hotel Danang", "price": 1200000, "description": "Luxury hotel in city center"}
        ],
        "places": [
            {"id": "place3", "name": "Marble Mountains", "description": "Cluster of five marble and limestone hills"},
            {"id": "place4", "name": "Dragon Bridge", "description": "Bridge that breathes fire on weekends"}
        ],
        "restaurants": [
            {"id": "rest3", "name": "Madame Lan Restaurant", "description": "Upscale Vietnamese dining"}
        ]
    }
    
    # Create planner and generate plan with tools
    planner = PlanModel()
    plan = planner.generate_plan_with_tools(
        sample_input,
        trip_name="Đà Nẵng Explorer",
        destination="Đà Nẵng",
        start_date="2023-11-10",
        end_date="2023-11-13"
    )
    
    # Print and save the plan
    print_plan_summary(plan)
    save_plan_to_file(plan, "plan_with_tools.json")

def demo_minimal_input():
    """Demonstrate generating a plan with minimal input."""
    print("\n=== Generating Plan With Minimal Input ===")
    
    # Minimal input
    minimal_input = {
        "destination": "Hội An",
        "accommodations": [],
        "places": [],
        "restaurants": []
    }
    
    # Create planner and generate plan
    planner = PlanModel()
    plan = planner.generate_plan(minimal_input)
    
    # Print and save the plan
    print_plan_summary(plan)
    save_plan_to_file(plan, "minimal_plan.json")

if __name__ == "__main__":
    # Ensure OPEN_API_KEY is set
    if not os.getenv("OPEN_API_KEY"):
        print("Warning: OPEN_API_KEY environment variable is not set.")
        print("Please set it before running this script.")
        exit(1)
        
    # Run demos
    demo_basic_plan()
    
    # Uncomment to run additional demos
    # demo_plan_with_tools()
    # demo_minimal_input() 
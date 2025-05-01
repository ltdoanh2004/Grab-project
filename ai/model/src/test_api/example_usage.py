#!/usr/bin/env python3
import json
from plan_model import PlanModel

def main():
    # Initialize the plan model
    model = PlanModel()
    
    # Example user input
    user_input = {
        "destination": "Tokyo, Japan",
        "budget": "$3000",
        "people": 2,
        "travel_time": "7 days",
        "use_langchain": True  # Set to True to use LangChain for processing
    }
    
    print("Generating travel plan...")
    result = model.handle_user_input(user_input)
    
    if result.get("status") == "success":
        plan = result.get("plan")
        print("\nTravel Plan Generated Successfully!")
        print(f"Destination: {user_input['destination']}")
        print(f"Budget: {user_input['budget']}")
        print(f"People: {user_input['people']}")
        print(f"Travel Time: {user_input['travel_time']}")
        
        # Print summary
        if "summary" in plan:
            print("\nSummary:")
            for key, value in plan["summary"].items():
                print(f"- {key}: {value}")
        
        # Print itinerary overview
        if "itinerary" in plan:
            print("\nItinerary Overview:")
            for day in plan["itinerary"]:
                print(f"Day {day.get('day')}: {len(day.get('activities', []))} activities")
        
        # Save the complete plan to a JSON file
        with open("travel_plan.json", "w") as f:
            json.dump(plan, f, indent=2)
        print("\nComplete plan saved to travel_plan.json")
    else:
        print("Error generating plan:")
        print(result.get("error", "Unknown error"))

if __name__ == "__main__":
    main() 
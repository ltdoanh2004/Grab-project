# Trip Planner

A web app that allows users to easily select and customize their tour itinerary based on personal preferences, using either predefined suggestions or AI-generated recommendations.

## Demo
[![](https://markdown-videos-api.jorgenkh.no/youtube/jjYC0ocranI)](https://youtu.be/jjYC0ocranI)

## Tech Stack

## Activity Diagram

![Untitled-2025-05-14-0903](https://github.com/user-attachments/assets/b4fda94b-f4eb-4a4f-a060-4f3a748d0726)

## Database schema

![mydb](https://github.com/user-attachments/assets/881a47bb-5361-4821-9d91-482ecbd3afcf)

## AI agent schema

![Agent Schema](images/agent.png)

### Agent Workflow Script

1. **User Input**: Users provide preferences (style, budget, session, etc.).
2. **Suggest Agent**: Receives user input, generates embeddings, and queries Pinecone (vector database) for relevant travel options.
3. **Pinecone**: Returns a list of IDs matching the user's preferences.
4. **Plan Agent**: Fetches detailed data from the travel database using the list of IDs, then creates a draft plan.
5. **Review Agent**: Reviews and edits the draft plan, searches for travel tips using Tavily (search tools), and finalizes the plan.
6. **User Review**: Users can view, comment, and request edits to the plan.
7. **Plan Agent (Edit)**: Incorporates user feedback, fetches additional activities if needed, and updates the plan.
8. **Final Plan**: The final plan is delivered to the user and stored for future reference.

**Key Components:**

- **Suggest Agent**: Embedding and initial recommendation
- **Plan Agent**: Data retrieval and plan creation/editing
- **Review Agent**: Plan review, enrichment, and finalization
- **Pinecone**: Vector database for fast similarity search
- **Tavily**: External search for travel tips and enrichment
- **Travel Database**: Source of detailed travel data
- **User Feedback Loop**: Continuous improvement via user comments and edits

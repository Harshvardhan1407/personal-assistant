from pydantic import BaseModel, Field

class chatbot_tools:
    class AddNumbersInput(BaseModel):
        """Schema for adding two numbers."""
        a: int = Field(..., description="First integer number")
        b: int = Field(..., description="Second integer number")


    class WeatherDetailsInput(BaseModel):
        """Schema for fetching weather details."""
        location: str = Field(..., description="City or location name")


    class RetrieveInformationInput(BaseModel):
        """Schema for retrieving RAG information."""
        user_input: str = Field(..., description="User's question for document retrieval")


    # 🔹 Step 3: Define Tool Functions
    def add_two_numbers(a: int, b: int) -> dict:
        """Adds two numbers and returns the sum."""
        return {"result": a + b}


    def weather_details(location: str) -> dict:
        """Fetches weather details for a given location."""
        return {"location": location, "temperature": 20}


    def retrieve_information(user_input: str) -> str:
        """Fetches relevant information using RAG."""
        return {"user_input": user_input}

    def general_query(user_input: str) -> str:
        """function for genral query."""
        return {"user_input": user_input}

    tools=[
        {
            "name": "add_two_numbers",
            "description": "Adds two numbers", 
            "parameters": AddNumbersInput.model_json_schema(), 
            "function": add_two_numbers
        },
        {
            "name": "weather_details", 
            "description": "Gets weather details for a location", 
            "parameters": WeatherDetailsInput.model_json_schema(), 
            "function": weather_details
            },
        {
            "name": "retrieve_information", 
            "description": "Retrieves information from RAG", 
            "parameters": RetrieveInformationInput.model_json_schema(), 
            "function": retrieve_information
            },
        {
            "name": "general_query",
            "description": "Handles general conversational queries and provides responses based on user input.",
            "parameters": RetrieveInformationInput.model_json_schema(), 
            "function": general_query
            },   
    ]
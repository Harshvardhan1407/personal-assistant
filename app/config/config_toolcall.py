from pydantic import BaseModel, Field

# 🔹 Define the chatbot_tools class
class chatbot_tools:
    # 🔹 Step 1: Define Pydantic Models for Input Validation
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

    # 🔹 Step 2: Define Tool Functions
    @staticmethod  # Use staticmethod to call these functions without creating an object
    def add_two_numbers(a: int, b: int) -> dict:
        """Adds two numbers and returns the sum."""
        return {"result": a + b}

    @staticmethod
    def weather_details(location: str) -> dict:
        """Fetches weather details for a given location."""
        return {"location": location, "temperature": 20}

    @staticmethod
    def retrieve_information(user_input: str) -> dict:
        """Fetches relevant information using RAG."""
        return {"user_input": user_input}

    @staticmethod
    def general_query(user_input: str) -> dict:
        """Function for general query."""
        return {"user_input": user_input}

    # 🔹 Step 3: Define the Tools List Inside the Class
    tools = [
        {
            "name": "add_two_numbers",
            "description": "Adds two numbers",
            "parameters": AddNumbersInput.model_json_schema(),
            "function": add_two_numbers  # No need for self since it's static
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

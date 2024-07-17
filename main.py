from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# from common import crawl , data_cleaning, ada_embedding
import numpy as np
from ast import literal_eval
import requests
import json
import re
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='chatbot.log', filemode='w', level=logging.INFO,format='%(asctime)s %(message)s')

class OpenAIBot:
    def __init__(self, engine):
        # Initialize conversation with a system message
        self.conversation = [{"role": "system", "content": "You are a helpful assistant."}]
        self.engine = engine

    def add_message(self, role, content):
        # Adds a message to the conversation.
        if content is not None:
            self.conversation.append({"role": role, "content": content})
            # print("conversation:", self.conversation)
        else:
            print(f"Attempted to add a message with null content for role {role}")
        # self.conversation.append({"role": role, "content": content})
    
    def json_response(self):
        return "these informations are classified, i can help you with track your electricity consumption ,monitor your consumption, recharge details of your prepaid meters and also compare your electricity bills over time"
    
    def consumer_details(self):
        try:
            """get consumer details"""
            url = os.getenv("login_api") 
            response = requests.get(url )
            if response.status_code == 200:
                response_data = response.json()
                logger.info('consumer details success')
                keys_to_fetch = ['consumer_name',"consumer_mobile_no","consumer_email_id","balance_amount",'last_recharge_time', 'last_coupon_number', 'last_coupon_amount','dg_reading', 'grid_reading',"grid_sanctioned_load","overload_grid","overload_dg"]
                data = {key: response_data['resource'][key] for key in keys_to_fetch}
                return data
        except Exception as e:
            logger.info("consumer details error:", e)

    def get_population(self,year):
        """get usa population"""
        url = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"
        response = requests.get(url )
    
        if response.status_code == 200:
            # print("Success:", response.json())
            logger.info("usa popluation data success")
            return response.json()
        else:
            logger.info("Error in api:", response.status_code, response.text)
    
    def daily_data(self):
        """ daily data"""
        try:
            url = os.getenv("daily_api")
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("daily data fetched")
                return response.json()
        except Exception as e:
            logger.info("error in daily data fetching",e)

    def monthly_data(self):
        """ monthly data"""
        try:
            url = os.getenv("monthly_api")
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("monthly data fetched")
                return response.json()
        except Exception as e:
            logger.info("error in monthly data fetching",e)

    def get_current_weather(self, location, unit="celcius"):
        """Get the current weather in a given location"""
        try:
            if "tokyo" in location.lower():
                return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
            elif "san francisco" in location.lower():
                return json.dumps({"location": "San Francisco", "temperature": "32", "unit": unit})
            elif "paris" in location.lower():
                return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
            else:
                return json.dumps({"location": location, "temperature": "unknown"})
        except Exception as e:
            logger.info("error in weather fetching",e)

    def format_currency_as_rupees(self,response):
        # Use regex to find and replace dollar amounts with rupees
        return re.sub(r'\$\s*([\d,]+(?:\.\d+)?)', r'₹\1', response)
    
    def power_cut(self):
        try:
            output = self.consumer_details()
            values = {}
            if float(output['balance_amount'])<0:
                values['balance'] = output['balance_amount']
            if output['overload_grid']=="y":
                values["overload_grid"] = output['overload_grid'],
            elif output['overload_dg']=="y":
                values["overload_dg"]= output['overload_dg']
            logger.info('power cut details success')
            return values
        except Exception as e:
            logger.info("error in power cut details",e)

    def get_cat_fact(self):
        url = "https://catfact.ninja/fact"
        response = requests.get(url )
        if response.status_code == 200:
            # print("Success:", response.json())
            logger.info("cat fact data sucess")
            return response.json()
        else:
            logger.info("Error in cat fact:", response.status_code, response.text)

    def generate_response(self, prompt):
        # Add user prompt to conversation
        self.add_message("user", prompt)
        tools = [
        {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},},
                "required": ["location"],},},},
                {
                    "type": "function",
                    "function": {
                        "name": "get_population",
                        "description": "Get the USA population",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            "required": ["year"]
                            },},},
                {
                    "type": "function",
                    "function": {
                        "name": "get_cat_fact",
                        "description": "Give me a cat fact",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
                {
                    "type": "function",
                    "function": {
                        "name": "consumer_details",
                        "description": "Fetches consumer details or grid_reading based on the request.",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
                 {
                    "type": "function",
                    "function": {
                        "name": "power_cut",
                        "description": "power cut or electricity outage or balance inquiry",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
                {
                    "type": "function",
                    "function": {
                        "name": "json_response",
                        "description": "give me json or api response ",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
                {
                    "type": "function",
                    "function": {
                        "name": "daily_data",
                        "description": "give me my daily data",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
                {
                    "type": "function",
                    "function": {
                        "name": "monthly_data",
                        "description": "give me this month data or monthly data",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
            ]

        try:
            # Make a request to the API using the chat-based endpoint with conversation context
            # print("done: 0")
            response = client.chat.completions.create( 
                model=self.engine, 
                messages=self.conversation,
                tools=tools,
                tool_choice="auto"  # auto is default, but we'll be explicit
            )
            response_message = response.choices[0].message
            # message = format_currency_as_rupees(response_message)
            # print("response_message:",response_message.content)
            # print("done: 1")
            self.add_message("assistant", response_message.content)
            # print(response_message)
            # Check if the model wanted to call a function
            # tool_calls = response_message.get('tool_calls', [])
            tool_calls = response_message.tool_calls
            if tool_calls:
                available_functions = {
                    "get_current_weather": self.get_current_weather,
                     "get_population": self.get_population,
                     "get_cat_fact": self.get_cat_fact,
                     "consumer_details":self.consumer_details,
                     "power_cut": self.power_cut,
                     "json_response": self.json_response,
                     "monthly_data":self.monthly_data,
                     "daily_data": self.daily_data,
                }  

                # Extend conversation with assistant's reply
                # print("done: 2")
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    if function_name == "get_current_weather":
                        function_response = function_to_call(
                            location=function_args.get("location"),
                            unit=function_args.get("unit")
                            )
                    elif function_name == "get_population":
                        function_response = function_to_call(
                            year=function_args.get("year")
                            )
                    else:
                        function_response = function_to_call()
                    
                    # print("done: 3")
                    # Ensure function response is not None
                    if function_response is not None:
                        # print(self.conversation)
                        self.conversation.append(
                            {   "role": "assistant",
                                "content": json.dumps({
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "response": function_response,
                                })
                            }
                        )            
                    else:
                        print(f"Function {function_name} returned None for arguments {function_args}")
                # print("done: 4")
                # Get a new response from the model where it can see the function response
                second_response = client.chat.completions.create( model=self.engine, messages=self.conversation)
                assistant_response = second_response.choices[0].message.content
                message = self.format_currency_as_rupees(assistant_response)
                self.add_message("assistant", message)
                return message

            # Return the initial response if no tool call was made
            return response_message.content
        except Exception as e:
            print(f'Error Generating Response: {e}')
            return None


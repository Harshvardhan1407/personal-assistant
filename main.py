from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# from common import crawl , data_cleaning, ada_embedding
import numpy as np
from ast import literal_eval
import requests
import json
import re
import logging
import config


logger = logging.getLogger(__name__)
logging.basicConfig(filename='chatbot.log', filemode='w', level=logging.INFO,format='%(asctime)s %(message)s')

class OpenAIBot:
    def __init__(self, engine):
        # Initialize conversation with a system message
        # self.conversation = [{"role": "system", "content": "You are a helpful assistant."}]
        self.conversation = [{
                "role": "system",
                "content": """
                You are an electric meter customer service assistant. Your role is to help users find details about their electric meter consumption, balance politely and competently.
                
                Follow these instructions to assist users:
                - parent company name is Radius.
                - Greet the user warmly.
                - Understand their query regarding consumption, balance, or personal information.
                - Retrieve and provide the requested information accurately.
                - Don't try to give generic response.
                - Assist with any other related queries or close the conversation politely.
                
                Ensure that details about tool call functions, IDs, or JSON responses are not shown to the user.  Instead, present the user with clear and helpful information in a natural language format. Always give money amount in rupee and if values are in negative shown them with negative sign and be direct with those values.
                If you don't have the infomation, tell the user to contact support or provider team.
                """
            }
            ]

        self.engine = engine

    def add_message(self, role, content):
        # Adds a message to the conversation.
        if content is not None:
            self.conversation.append({"role": role, "content": content})
            # print("conversation:", self.conversation)
        else:
            logger.info(f"Attempted to add a message with null content for role {role}")
        # self.conversation.append({"role": role, "content": content})
    
    def json_response(self):
        return "these informations are classified, i can help you with track your electricity consumption ,monitor your consumption, recharge details of your prepaid meters and also compare your electricity bills over time"
    
    def login_api(self):
        try:
            # url = os.getenv("login_api")
            url = config.login_api
            response = requests.get(url )
            if response.status_code == 200:
                return response.json()['resource']
            
            logger.info("login_api success")
        except Exception as e:
            logger.info("error fetching login api:",e)

    def consumer_details(self):
        try:
            data = self.login_api()
            keys_to_fetch = ['location_id',"flat_number",'consumer_name',"consumer_mobile_no","consumer_email_id","balance_amount"]#,"balance_amount",'last_recharge_time', 'last_coupon_number', 'last_coupon_amount','dg_reading', 'grid_reading',"grid_sanctioned_load","overload_grid","overload_dg"]
            output = {key: data[key] for key in keys_to_fetch}
            # Step 1: Add the new key with the value of the old key
            output["login_id"] = output["location_id"]
            del output["location_id"]
            logger.info("consumer_details success")
            return output
        
        except Exception as e:
            logger.info("error fetching consumer_details:",e)
    
    def notifiation(self):
        try:
            data = self.login_api()
            keys_to_fetch = ['notification_email', 'notification_sms', 'notification_ivrs', 'notification_app_load', 'notification_app_balance', 'low_bal_alert', 'notification_app_esource', 'notification_app_unit_consumption', 'alert_daily_consumption_grid', 'alert_daily_consumption_dg','power_cut_restore_notification', 'recharge_notification', 'last_reading_alert_notification']
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("notification data success")
            return output

        except Exception as e:
            logger.info("error fetching notification_details:",e)
    
    def balance_recharge(self):
        try:
            data  = self.login_api()
            keys_to_fetch = ['balance_amount', 'last_recharge_time', 'last_coupon_amount',]#'last_coupon_number'
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("balance_recharge data success")
            return output
        except Exception as e:
            logger.info("error fetching balance and recharge:",e)    
    
    def consumption(self):
        try:
            data  = self.login_api()
            keys_to_fetch = ['dg_reading', 'grid_reading', 'last_reading_updated', 'daily_dg_unit', 'daily_grid_unit', 'monthly_dg_unit', 'monthly_grid_unit', 'daily_dg_amount', 'daily_grid_amount', 'fix_charges_monthly', 'monthly_dg_amount', 'monthly_grid_amount', 'fix_charges','energy_source', 'last_reading_updated_dg',]
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("consumption data success")
            return output
        except Exception as e:
            logger.info("error fetching consumption details:",e)  

    def site_details(self):
        try:
            data  = self.login_api()
            keys_to_fetch = ['site_id', 'site_name', 'site_address', 'site_city', 'site_state', 'site_country', 'site_zipcode', 'site_supervisor_name',]
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("site_details data success")
            return output
        except Exception as e:
            logger.info("error fetching site details:",e)
    
    def costumer_support(self):
        try:
            data  = self.login_api()
            keys_to_fetch = ['site_supervisor_name', 'site_supervisor_contact_no', 'site_supervisor_email_id', 'site_support_concern_name', 'site_support_contact_no', 'site_support_email_id',]
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("costumer support data success")
            return output
        except Exception as e:
            logger.info("error fetching costumer support:",e)  

    # def consumer_details(self):
    #     try:
    #         """get consumer details"""
    #         url = os.getenv("login_api") 
    #         response = requests.get(url )
    #         if response.status_code == 200:
    #             response_data = response.json()
    #             logger.info('consumer details success')
    #             keys_to_fetch = ['consumer_name',"consumer_mobile_no","consumer_email_id","balance_amount",'last_recharge_time', 'last_coupon_number', 'last_coupon_amount','dg_reading', 'grid_reading',"grid_sanctioned_load","overload_grid","overload_dg"]
    #             data = {key: response_data['resource'][key] for key in keys_to_fetch}
    #             return data
    #     except Exception as e:
    #         logger.info("consumer details error:", e)

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
            # url = os.getenv("daily_api")
            url = config.daily_api
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("daily data fetched")
                return response.json()
        except Exception as e:
            logger.info("error in daily data fetching",e)

    def monthly_data(self):
        """ monthly data"""
        try:
            # url = os.getenv("monthly_api")
            url = config.monthly_api
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
            output = self.login_api()
            values = {}
            if float(output['balance_amount'])<0:
                values['balance'] = output['balance_amount']
            if output['overload_grid'] in ["y", "Y"]:
                values["overload_grid"] = output['overload_grid'],
            elif output['overload_dg'] in ["y", "Y"]:
                values["overload_dg"]= output['overload_dg']
            logger.info(values)
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
                        "description": "Fetches consumer details, grid_reading, balance based on the request.",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
# 1
                 {
                    "type": "function",
                    "function": {
                        "name": "notifiation",
                        "description": "what notification are enabled for me",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
# 2
                 {
                    "type": "function",
                    "function": {
                        "name": "balance_recharge",
                        "description": "give me my balance or recharge related query",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
# 3
                 {
                    "type": "function",
                    "function": {
                        "name": "consumption",
                        "description": "Retrieve detailed consumption information including current grid reading, generator and grid readings, daily and monthly units, amounts, fixed charges, and last updated timestamps.",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},
# 4
                 {
                    "type": "function",
                    "function": {
                        "name": "site_details",
                        "description": "what are my site details",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},

                 {
                    "type": "function",
                    "function": {
                        "name": "costumer_support",
                        "description": "give me my customer support details",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # No properties needed as it takes no parameters
                            },},},


                 {
                    "type": "function",
                    "function": {
                        "name": "power_cut",
                        "description": "power cut or electricity outage",
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
                        "description": "give me this day or  daily data",
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
                     "notifiation": self.notifiation,
                     "balance_recharge": self.balance_recharge,
                     "consumption": self.consumption,
                     "site_details": self.site_details,
                     "costumer_support":self.costumer_support,

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


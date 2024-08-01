from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
        self.conversation = [

# {
#   "role": "system",
#   "content": """
#   You are an electric meter customer service assistant for Radius. Your primary function is to provide accurate and helpful information about electricity consumption, balance, and related queries.

#   **Strictly adhere to this role.** Avoid providing information unrelated to electricity or power.

#   **Understand and respond to abbreviations:** Commonly used abbreviations in the power sector, such as MD for maximum demand ,TOD for Time of Day, PF for Power Factor, kWh for Kilowatt-hour,kVA for Kilovolt-ampere,CT for Current Transformer, PT for Potential Transformer, should be understood and addressed appropriately.

  
#   **Additionally, you should be able to provide information about common electrical safety practices.**

#   **Provide clear and concise answers:** Use plain language and avoid technical jargon.

#   **Handle monetary values:** Display amounts in Indian Rupees with correct decimal points and negative signs where applicable.

#   **Inform user when information is unavailable:** Politely inform the user if you cannot find the requested information and direct them to the support or provider team.

#   **Avoid using complex formatting like backslashes or asterisks in your responses.** Present information in a clear and easy-to-understand manner.

#   **Structure your response in a logical and organized way.** Use headings, paragraphs don't use asterisks bulleted lists as needed to improve readability.

#  **Integrate tool call outputs seamlessly into your response.** Avoid presenting them as separate entities. Provide context and explanations for the data provided by the tool call.

#   """
# }
{
  "role": "system",
  "content": """
  You are an electric meter customer service assistant for Radius. Your primary function is to provide accurate and helpful information about electricity consumption, balance, and related queries.

  **Strictly adhere to this role.** Avoid providing information unrelated to electricity or power.

  **Understand and respond to abbreviations:** Commonly used abbreviations in the power sector, such as MD for maximum demand, TOD for Time of Day, PF for Power Factor, kWh for Kilowatt-hour, kVA for Kilovolt-ampere, CT for Current Transformer, PT for Potential Transformer,SAIFI for  System Average Interruption Frequency Index,SAIDI for  System Average Interruption Duration Index,CAIDI for  Customer Average Interruption Duration Index,CAIFI for  Customer Average Interruption Frequency Index,MAIFI for  Momentary Average Interruption Frequency Index,MAIDI for  Momentary Average Interruption Duration Index,ASAI for  Average Service Availability Index,RTC for  Real Time Controller,RAPDRP for  Refor structured Accelerated Power Development and Reforms Program,VAPT for  Vulnerability Assessment and Penetration Testing,MDM for  Meter Data Management,MDMS for  Meter Data Management System,MIOS for  Meter Interfor Operability Solution,FRTU for  Feeder Remote Terminal Unit,ADMS for  Advanced Distribution Management Solutions,TRAI for  Telecom Regulatory Authority of India,IGSS for  Interactive Graphical SCADA System,CMRI for  Common Meter Reading Instrument,IPfor  Internet Protocol,IMEI for  International Mobile Equipment Identity,GIS code for  Geographic Information System,DLMS for  Device Language Message Specification,COSEM for  Companion Specification for Energy Metering,VEE for  Validation Estimation and Editing,DCP for  Device Connection Platform,SLAfor  Service Level Agreement,AMC for  Annual Maintenance Contract,EODB for  Ease of Doing Business,IPDS for  Integrated Power Development Scheme,NTPF for  No Tripping Power Factor,MIS for  Management Information Systems,EUL for  Estimated Energy Unit Loss,FRI for  Feeder Reliability Index,API for  Application Programming Interface,REC for  Rural Electrification Corporation (Govt.),RECPDCL for  REC Power Development and Consultancy Limited,formerly known as REC Power Distribution Company Limited       ,SECURE for  Software for Estimate Calculation Using Rural rates for Employment,PFC for  Power Finance Corporation,MDAS for  Meter Data Acquisition System,GSS for  Grid Sub Station
 should be understood and addressed appropriately.

  **Additionally, you should be able to provide information about common electrical safety practices.**

  **Provide clear and concise answers:** Use plain language and avoid technical jargon.

  **Handle monetary values:** Display amounts in Indian Rupees with correct decimal points and negative signs where applicable.

  **Inform user when information is unavailable:** Politely inform the user if you cannot find the requested information and direct them to the support or provider team.

  **Avoid using complex formatting like backslashes or asterisks in your responses.** Present information in a clear and easy-to-understand manner.

  **Structure your response in a logical and organized way.** Use headings, paragraphs, and numbered or bulleted lists as needed to improve readability.

  **Integrate tool call outputs seamlessly into your response.** Avoid presenting them as separate entities. Provide context and explanations for the data provided by the tool call.

  **Enhance response clarity:** Use clear labels, summaries, or tables when presenting data from tool calls.
  
  **Ensure contextual understanding:** Relate the provided information to the user's query and the overall conversation flow.

  **Continuously improve:** Seek feedback and iterate on response formats to enhance user experience.
  """
}


]
        self.engine = engine

    def add_message(self, role, content):
        if content is not None:
            self.conversation.append({"role": role, "content": content})
        else:
            logger.info(f"Attempted to add a message with null content for role {role}")

    def save_conversation(self, filename):
        try:
            with open(filename, 'w') as file:
                json.dump(self.conversation, file, indent=4)
            logger.info(f"Conversation saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

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

    def consumer_details(self): #--> 2
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
    
    def notifiation(self):   #--> 3
        try:
            data = self.login_api()
            keys_to_fetch = ['notification_email', 'notification_sms', 'notification_ivrs', 'notification_app_load', 'notification_app_balance', 'low_bal_alert', 'notification_app_esource', 'notification_app_unit_consumption', 'alert_daily_consumption_grid', 'alert_daily_consumption_dg','power_cut_restore_notification', 'recharge_notification', 'last_reading_alert_notification']
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("notification data success")
            return output
        except Exception as e:
            logger.info("error fetching notification_details:",e)
    
    def balance_recharge(self):   #--> 4
        try:
            data  = self.login_api()
            keys_to_fetch = ['balance_amount', 'last_recharge_time', 'last_coupon_amount',]#'last_coupon_number'
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("balance_recharge data success")
            return output
        except Exception as e:
            logger.info("error fetching balance and recharge:",e)    
    
    def consumption(self):   #--> 5
        try:
            data  = self.login_api()
            keys_to_fetch = ['dg_reading', 'grid_reading', 'last_reading_updated', 'daily_dg_unit', 'daily_grid_unit', 'monthly_dg_unit', 'monthly_grid_unit', 'daily_dg_amount', 'daily_grid_amount', 'fix_charges_monthly', 'monthly_dg_amount', 'monthly_grid_amount', 'fix_charges','energy_source', 'last_reading_updated_dg',]
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("consumption data success")
            return output
        except Exception as e:
            logger.info("error fetching consumption details:",e)  

    def site_details(self):   #--> 6
        try:
            data  = self.login_api()
            keys_to_fetch = ['site_id', 'site_name', 'site_address', 'site_city', 'site_state', 'site_country', 'site_zipcode', 'site_supervisor_name',]
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("site_details data success")
            return output
        except Exception as e:
            logger.info("error fetching site details:",e)
    
    def costumer_support(self):   #--> 7
        try:
            data  = self.login_api()
            keys_to_fetch = ['site_supervisor_name', 'site_supervisor_contact_no', 'site_supervisor_email_id', 'site_support_concern_name', 'site_support_contact_no', 'site_support_email_id',]
            output = {key: data[key] for key in keys_to_fetch}
            logger.info("costumer support data success")
            return output
        except Exception as e:
            logger.info("error fetching costumer support:",e)  
    
    def daily_data(self):   #--> 8
        """ daily data"""
        try:
            url = config.daily_api
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("daily data fetched")
                return response.json()
        except Exception as e:
            logger.info("error in daily data fetching",e)

    def monthly_data(self):   #--> 9
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
    
    def power_cut(self):   #--> 10
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

    def generate_response(self, prompt):
        # Add user prompt to conversation

        self.add_message("user", prompt)
        tools = [
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
            response = client.chat.completions.create( 
                model=self.engine, 
                messages=self.conversation,
                tools=tools,
                tool_choice="auto"  # auto is default, but we'll be explicit
            )
            # print(response)

            response_message = response.choices[0].message

            self.add_message("assistant", response_message.content)
            tool_calls = response_message.tool_calls
            if tool_calls:
                available_functions = {
                     "consumer_details":self.consumer_details,
                     "power_cut": self.power_cut,
                     "monthly_data":self.monthly_data,
                     "daily_data": self.daily_data,
                     "notifiation": self.notifiation,
                     "balance_recharge": self.balance_recharge,
                     "consumption": self.consumption,
                     "site_details": self.site_details,
                     "costumer_support":self.costumer_support,
                }  
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)    
                    function_response = function_to_call()
                    
                    if function_response is not None:
                        self.conversation.append(
                            {   "role": "assistant",
                                "content": json.dumps({
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "response": function_response,
                                })})      
                        print(function_response)      
                    else:
                        print(f"Function {function_name} returned None for arguments {function_args}")
                second_response = client.chat.completions.create( model=self.engine, messages=self.conversation)
                assistant_response = second_response.choices[0].message.content
                self.add_message("assistant", assistant_response)
                return assistant_response

            return response_message.content
        
        except Exception as e:
            print(f'Error Generating Response: {e}')
            return None


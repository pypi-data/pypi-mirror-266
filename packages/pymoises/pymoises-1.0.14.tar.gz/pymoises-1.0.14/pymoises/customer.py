import requests
import logging
import re

from .dto import (
    check_email_phone_input_schema,
    get_customer_output_schema,
    move_lead_output_schema, 
    create_lead_input_schema,
    create_customer_output_schema
)

def clean_strings(string):

    words = string.split()
    if len(words) >= 1:
        return re.sub(r'[^a-zA-Z0-9]', '', words[0])
    
    return re.sub(r'[^a-zA-Z0-9]', '', string)



class Customers:
    def check_customer_by_email_phone(request: check_email_phone_input_schema) -> get_customer_output_schema:
        """
        Check if exist a customer in moises whit the email and phone.

        Params:
            check_email_phone_input_schema : 
                email (string): lead's email
                phone (string): lead's phone

        Return:
            get_customer_output_schema:
                success (boolean): success function
                message (string): result of function
                payload (dict) -- OPTIONAL:
                    tpid (string): if customer exist return tpid
        """
        url = "http://webservicesnt.org:5050/check-if-exist-customer"

        payload = {}
        payload['email'] = request['email']
        payload['phone'] = request['phone']

        headers = {}
        headers['Content-Type'] = 'application/json'

        try:

            moisesResponse = requests.request("POST", url, headers=headers, json=payload)
            logging.warning('RESPONE CHECK IF EXIST IN MOISES %s' % (moisesResponse.text))
            moisesResponse = moisesResponse.json()

            if not moisesResponse['result'] == 1:
                respone : get_customer_output_schema = {}
                respone['success'] = False
                respone['message'] = "Customer exist"
                respone['payload'] = {}
                respone['payload']['tpid'] = moisesResponse['data'][0]['tpId']

                return respone

            respone : get_customer_output_schema = {}
            respone['success'] = True
            respone['message'] = "Customer not exist"
            respone['payload'] = {}
            return respone
    
        except Exception as Err:
            respone : get_customer_output_schema = {}
            respone['success'] = False
            respone['message'] = str(Err)
            respone['payload'] = {}

            return respone
        
    def get_info_by_tpid(tpid: str):
        """
        Get info of customer by tpid.

        Params:
            tpid (string) :  lead's tpid

        Return:
            get_customer_output_schema:
                success (boolean): success function
                message (string): result of function
                payload (dict) -- OPTIONAL:
                    tpid (string): if customer exist return tpid
        """
        url = "http://webservicesnt.org:5050/customer/info"

        payload = {}
        payload['tpid'] = tpid

        headers = {}
        headers['Content-Type'] = 'application/json'

        try:

            moisesResponse = requests.request("POST", url, headers=headers, json=payload)
            logging.warning('RESPONE GET INFO FROM CUSTOMER %s' % (moisesResponse.text))
            moisesResponse = moisesResponse.json()

            if not moisesResponse['result'] == 1:
                respone : get_customer_output_schema = {}
                respone['success'] = False
                respone['message'] = "Customer noit exist"
                respone['payload'] = {}

                return respone

            respone : get_customer_output_schema = {}
            respone['success'] = True
            respone['message'] = "Customer info"
            respone['payload'] = {}
            respone['payload']['tpid'] = moisesResponse['data']['tpId']
            respone['payload']['crmId'] = moisesResponse['data']['crmId']
            respone['payload']['firstName'] = clean_strings(moisesResponse['data']['firstName'])
            respone['payload']['lastName'] = clean_strings(moisesResponse['data']['lastName'])
            respone['payload']['phoneCode'] = moisesResponse['data']['phoneCode']
            respone['payload']['phoneNumber'] = moisesResponse['data']['phoneNumber']
            respone['payload']['country'] = moisesResponse['data']['country']
            respone['payload']['BussinessUnit'] = moisesResponse['data']['idCrmBusinessUnit']
            respone['payload']['email'] = moisesResponse['data']['email']


            return respone
    
        except Exception as Err:
            respone : get_customer_output_schema = {}
            respone['success'] = False
            respone['message'] = str(Err)
            respone['payload'] = {}

            return respone
   
    def move_lead_another_bussinesUnit(tpid: str, bussinesUnitName: str) -> move_lead_output_schema:
        """
        move a customer in moises to another bussinesUnit and change owner in crm-app.

        Params:
            tpid (string): lead's TPID
            bussinesUnitName (str): BussinesUnit to move
                Fxtrategy     : 8
                AscendingBull : 14
                Inverlion     : 15
                Noimarkets    : 16
                UBM Capital   : 17
                ALL Markets   : 18
                FxIntegral    : 19
                Profitbitz    : 20
                Solutraders   : 21
                BearInvester  : 22

        Return:
            move_lead_output_schema:
                success (boolean): success function
                message (string): result of function
                payload (dict) -- OPTIONAL:
                    tpid (string): if customer move correctly return tpid
                    crmId (string): if customer move correctly return crmId
                    idBusinessUnit (string): if customer move correctly return idBusinessUnit
        """
        url = "http://webservicesnt.org:5050/update/move-lead-crm"

        payload = {}
        payload['tpid'] = tpid
        payload['bussinesUnitName'] = bussinesUnitName

        headers = {}
        headers['Content-Type'] = 'application/json'

        try:

            moisesResponse = requests.request("POST", url, headers=headers, json=payload)
            logging.warning('MOVE LEAD IN MOISES %s' % (moisesResponse.text))
            moisesResponse = moisesResponse.json()

            if not moisesResponse['result'] == 1:
                respone : move_lead_output_schema = {}
                respone['success'] = False
                respone['message'] = "Customer not move"
                respone['payload'] = {}

                return respone

            respone : move_lead_output_schema = {}
            respone['success'] = True
            respone['message'] = "Customer move correctly"
            respone['payload'] = {}
            respone['payload']['tpid'] = tpid
            respone['payload']['crmId'] = moisesResponse['data']['crmId']
            respone['payload']['idBusinessUnit'] = moisesResponse['data']['idBussinesUnit']

            return respone
        
        except Exception as Err:
            respone : get_customer_output_schema = {}
            respone['success'] = False
            respone['message'] = str(Err)
            respone['payload'] = {}

            return respone
    
    def create_lead_affiliates(input: create_lead_input_schema) -> create_customer_output_schema:
        """
        create a lead from api affiliates in a internal Affiliate.

        Params:
            create_lead_input_schema: 
                firstName (str) : lead's name
                lastName (str) : lead's last name
                email (str) : lead's email
                password (str) :  lead's password
                phoneCode (int) : country phone code
                phoneNumber (str) : lead's phone number
                country (str) : lead's country
                    MX, PE, CL, BR, CR, PA

                page (str) : lead's page

                bussinesUnitName (str): lead's BussinesUnit
                    Fxtrategy     : 8
                    AscendingBull : 14
                    Inverlion     : 15
                    Noimarkets    : 16
                    UbmCapital    : 17
                    AllMarkets    : 18
                    FxIntegral    : 19
                    Profitbitz    : 20
                    Solutraders   : 21
                    BearInvester  : 22

        Return:
            create_customer_output_schema:
                success (boolean): success function
                message (string): result of function
                payload (dict) -- OPTIONAL:
                    id (string): if customer move correctly return UUID
                  
        """
        url = "https://webservicesnt.org:4455/customer/affiliate-api"

        payload = {}
        payload['firstName'] = input['firstName']
        payload['lastName'] = input['firstName']
        payload['email'] = input['email']
        payload['password'] = input['password']
        payload['phoneCode'] = int(input['phoneCode'])
        payload['phoneNumber'] = input['phoneNumber']
        payload['country'] = input['country']
        payload['page'] = input['page']
        payload['brand'] = input['bussinesUnitName']

        headers = {}
        headers['Content-Type'] = 'application/json'

        try:

            moisesResponse = requests.request("POST", url, headers=headers, json=payload)
            logging.warning('CREATE LEAD IN API AFFILIATES MOISES %s' % (moisesResponse.text))
            moisesResponse = moisesResponse.json()

            if not moisesResponse['result'] == 1:
                respone : create_customer_output_schema = {}
                respone['success'] = False
                respone['message'] = "Customer not create"
                respone['payload'] = {}

                return respone

            respone : create_customer_output_schema = {}
            respone['success'] = True
            respone['message'] = "Customer move correctly"
            respone['payload'] = {}
            respone['payload'] = moisesResponse['data']

            return respone
        
        except Exception as Err:
            respone : create_customer_output_schema = {}
            respone['success'] = False
            respone['message'] = str(Err)
            respone['payload'] = {}

            return respone

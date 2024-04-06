import requests
import logging

class BusinessUnit:
    def check_info_BU(id_business_unit: int):
        """
        Check info BU in moises by id.

        Params:
            id_business_unit (int): bu ids in moises  

        Return:
            success (boolean): success function
            message (string): result of function
            payload (dict) :
                name (string)


        """
        url = "http://webservicesnt.org:5050/get/bussinesUnit"

        payload = {}
        payload['idBussinessUnit'] = str(id_business_unit)

        headers = {}
        headers['Content-Type'] = 'application/json'

        try:

            moisesResponse = requests.request("POST", url, headers=headers, json=payload)
            logging.warning('RESPONE CHECK INFO BUSSINESS UNIT %s' % (moisesResponse.text))
            moisesResponse = moisesResponse.json()

            if not moisesResponse['result'] == 1:
                respone = {}
                respone['success'] = False
                respone['message'] = "BU not found"
                respone['payload'] = {}

                return respone

            respone = {}
            respone['success'] = True
            respone['message'] = "BU info correctly"
            respone['payload'] = {}
            respone['payload']['id'] = id_business_unit
            respone['payload']['name'] = str(moisesResponse['data']['name']).lower()
            return respone
    
        except Exception as Err:
            respone = {}
            respone['success'] = False
            respone['message'] = str(Err)
            respone['payload'] = {}

            return respone
import os
import requests
import json
from flask import Flask, flash, render_template, request
from datetime import datetime
from time import strftime

app = Flask(__name__)
app.secret_key = "hello"

ENV = 'QA'

http_proxy = "http://internet.ford.com:83"
https_proxy = "http://internet.ford.com:83"

proxyDict = {"http": http_proxy, "https": https_proxy}

if ENV == 'PROD':
    AZ_TKN_URL = 'https://login.microsoftonline.com/azureford.onmicrosoft.com/oauth2/v2.0/token'
    API_URL = 'https://api.pd01e.gcp.ford.com/itconnect'
    CLNT_ID = ''
    CLNT_SEC = ''
    SCOPE = ''

if ENV == 'QA':
    AZ_TKN_URL = 'https://login.microsoftonline.com/azureford.onmicrosoft.com/oauth2/v2.0/token'
    API_URL = 'https://api.qa01e.gcp.ford.com/itconnect'
    CLNT_ID = 'a10db1f0-ab44-4d32-ab19-b033533a29b2'
    CLNT_SEC = 'VyT8Q~39LnKoqKhvxf0G5uQ3iHfN9h1deOr1pbx8'
    SCOPE = '4baf82f3-cbec-4c28-9b7d-0166c43a8f86/.default'



def func(cdsid, ob_cdsid, ticktype, priority, title, application, Prod_Queue, detail, Issue_Type):
    print(ticktype)
    
    shrtDesc = title
    lngDesc = detail

    

    if not (ob_cdsid and not ob_cdsid.isspace()):
        ob_cdsid = cdsid

    product_lookup = {
        'Teamcenter': ['Teamcenter', 'TC-Teamcenter', 'Software', 'Application', 'Product Development'],
        'Data Factory': ['Data Factory', 'CATIAV5-CATIA V5', 'Software', 'Application', 'Global Data Insight & Analytics > Data Factory'],
    }

    categorization_lookup = {
        'Access Issue': ['Availability', 'Access'],
        'Outage': ['Service Availability', 'Application Availability'],
        'Data Issue': ['Service Data', 'Data Related'],
        'Performance Issue': ['Service Functionality', 'Performance'],
        'Storage Issue': ['Service Capacity', 'Insufficient Storage'],
        'Others': ['Service Functionality', 'General Error Message'],
    }

    if priority == 'Critical':
        Impct = "2-Significant/Large"
        Urgcy = "1-Critical"
    elif priority == 'High':
        Impct = "2-Significant/Large"
        Urgcy = "2-High"
    elif priority == 'Medium':
        Impct = "3-Moderate/Limited"
        Urgcy = "2-High"
    elif priority == 'Low':
        Impct = '4-Minor/Localized'
        Urgcy = '4-Low'

    Support_Organization = "Data Factory"
    Support_Group = Prod_Queue
    Sub_Application = application

    def GetToken(cId, cSecrt, scope, tkUrl):
        payload = 'grant_type=client_credentials&scope=' + scope + '&client_id=' + cId + '&client_secret=' + cSecrt + ''
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", tkUrl, headers=headers, proxies=proxyDict, data=payload)
        jsonResp = response.json()
        return jsonResp

    tkn_result = GetToken(CLNT_ID, CLNT_SEC, SCOPE, AZ_TKN_URL)
    api_token = tkn_result["access_token"]

    def Modify_Ticket(method, url, token, data_input):
        headers = {
            'authorization': "Bearer " + token,
            'content-type': "application/json"
        }
        jsn_data = json.dumps(data_input)
        response = requests.request(method, url, data=jsn_data, headers=headers)
        if response.status_code == 204:
            jsonRes = "empty"
        else:
            jsonRes = response.json()
        if response.status_code in [200, 201, 204]:
            status = True
        else:
            status = False
        return status, jsonRes

    def Query_people(method, url, token):
        headers = {
            'authorization': "Bearer " + token,
            'content-type': "application/json"
        }
        response = requests.request(method, url, headers=headers)
        jsonRes = response.json()
        if response.status_code in [200, 201]:
            status = True
        else:
            status = False
        return status, jsonRes

    people_result = []
    UserFullName = ''

    qpURL = API_URL + "/extensions/v1/people?q=('Remedy Login ID' = \"" + ob_cdsid + "\" AND 'Profile Status'=\"Enabled\")&fields=values(Remedy Login ID,Request ID,Full Name,First Name,Last Name,Site,Internet E-mail)"

    people_result = Query_people("GET", qpURL, api_token)
    json_str = str(people_result[1])

    if 'Full Name' in json_str:
        UserFullName = people_result[1]["entries"][0]["values"]["Full Name"]
       
        UserFirstName = people_result[1]["entries"][0]["values"]["First Name"]
        UserLastName = people_result[1]["entries"][0]["values"]["Last Name"]
        PersonId = people_result[1]["entries"][0]["values"]["Request ID"]
        print(PersonId)

    else:
        print("User Not Found")
        rtn_status = "userid \"" + ob_cdsid + "\" not found... enter correct cdsid..."
        return rtn_status

    submit_result = []
    ticket_no = ''
    rtn_status = ''


    lngDesc="Application Name: 53019-Data Factory(DF)\nSub Application Name: "+Sub_Application+"\nComments:  "+lngDesc

    if UserFullName and not UserFullName.isspace():
        if ticktype == 'INC':

            dt = {"values": {
                "Description": shrtDesc,
                "Detailed_Decription": lngDesc,
                "Impact": Impct,
                "Urgency": Urgcy,
                "Status": "Assigned",
                "Reported Source": "Direct Input",
                "Service_Type": "User Service Restoration",
                "Owner Group": Support_Group,
                "Owner Support Organization": Support_Organization,
                "Owner Support Company": "Ford Motor Company",
                "Manufacturer": "Ford Motor Company",
                "Assigned Group": Support_Group,
                "Assigned Support Organization": Support_Organization,
                "Assigned Support Company": "Ford Motor Company",
                "ServiceCI": "Application Support",
                "Categorization Tier 1": "Break/Fix",
                "Categorization Tier 2": "Service Functionality",
                "Categorization Tier 3": "General Error Message",
                "Corporate ID": cdsid,
                "Login_ID": ob_cdsid,
                "Direct Contact Last Name": "GDIA",
                "Direct Contact First Name": "F",
                "z1D_Action": "CREATE",
                "Product Name": "Data Factory",
                "Product Categorization Tier 1": "Software",
                "Product Categorization Tier 2": "Application",
                "Product Categorization Tier 3": "Global Data Insight & Analytics"
            }}
            URL = API_URL + '/incident/v1/incident'

        else:
            # Define template_id for WO ticket submission
            if ENV == 'PROD':
                # TEMPLATE_ID = 'IDGG2SHDDYPDFAQT6FP5QS76RXL7A0'
                proxy_person_id = 'PPL000000894050'  # Proxy account person id

            if ENV == 'QA':
                # TEMPLATE_ID = 'IDGDZT1RAAHLOAQT5CLLQS62XODYZQ'
                proxy_person_id = 'PPL000000894050'  # Proxy account person id

            

            dt = {
                "values": {
                    "Customer Person ID": ""+ PersonId.split("|")[0] +"",
                    "Requested By Person ID": proxy_person_id,
                    "Summary": shrtDesc,
                    "Detailed Description": lngDesc,
                    "Status": "Assigned",
                    "Product Cat Tier 1(2)": "Software",
                    "Product Cat Tier 2 (2)": "Application",
                    "Product Cat Tier 3 (2)": "Global Data Insight & Analytics",
                    "Product Name (2)": "Data Factory",
                    "Priority": "Low",
                    "Request Manager Company": "Ford Motor Company",
                    "Manager Support Organization": Support_Organization,
                    "Manager Support Group Name": Support_Group,
                    "Support Company": "Ford Motor Company",
                    "Support Organization": Support_Organization,
                    "Support Group Name": Support_Group,
                    "CI Name" : "Application Support",
                    "ReconciliationIdentity" : "OI-82D0A41AA84847F0AC4C253A73F0AB41",
                    "z1D_Action": "CREATE"
                }
            }
            URL = API_URL + '/workorder/v1/workorder'

        # Call function to submit WO ticket
        submit_result = Modify_Ticket("POST", URL, api_token, dt)
        print (submit_result[0])
        print (submit_result[1])

        if submit_result[0]:
            if ( ticktype == 'INC' ):
                EntryID=submit_result[1]["values"]["Incident Entry ID"]
                ticket_no=submit_result[1]["values"]["Incident Number"]
            else:
                EntryID=submit_result[1]["values"]["WorkOrder_ EntryID"]
                ticket_no=submit_result[1]["values"]["WorkOrder_Number"]
            rtn_status = "Submitted successfully, your ticket number is " + ticket_no
        else:
            rtn_status = "Error occurred while submitting the Work Order ticket"

    return rtn_status




@app.route("/")
def home():
    return render_template("index.html")

@app.route('/process', methods=['POST'])
def result():
    if request.method == 'POST':
        inputs = request.form
        userid = inputs.get('CDSID')
        OBH_UNAME = inputs.get('OBH_UNAME')
        application = inputs['DETAILS_LIST']
        ProdQueue = inputs['QUELIST']
        priority = inputs['Priority-radio-Btn']
        title = inputs['title_textbox']
        description = inputs['description_textbox']
        serviceType = inputs['Type-radio-Btn']

        print('=================== DETAILS ===================\nUserID: '+userid+' \nOnBehalf ID: '+OBH_UNAME+'\nServiceType: '+serviceType+' \nApplication: '+application+' \nQueue: '+ProdQueue+' \nPriority: '+priority+' \nTicket Title: '+title+' \nDescription: '+description+'\n===============================================')

    call_func = func(userid, OBH_UNAME, serviceType, priority, title, application, ProdQueue, description)
    flash(call_func)

    return render_template("index.html")


###############################################
#                Run app                      #
###############################################        
# if __name__ == '__main__':
#     app.run(debug=True)

# Enable for server deployment
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)


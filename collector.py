import requests

debugMode: bool = False

def requestRawData():
    if(debugMode):
        print("Data requested")
        return("Nova")
    else:
        url = "https://goboardapi.azurewebsites.net/api/FacilityCount/GetCountsByAccount"

        querystring = {"AccountAPIKey":"7938fc89-a15c-492d-9566-12c961bc1f27"}

        payload = ""
        headers = {"cookie": "ARRAffinity=8e5b8fa31cb09ead9afab497af65d34eed91ada4b22f18d258db2a324dcd2a9c; ARRAffinitySameSite=8e5b8fa31cb09ead9afab497af65d34eed91ada4b22f18d258db2a324dcd2a9c"}

        response = requests.get(url, data=payload, headers=headers, params=querystring)

        return response.json()
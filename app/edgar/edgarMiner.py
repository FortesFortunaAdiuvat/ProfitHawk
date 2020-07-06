# package used to execute HTTP POST request to the API
import json
import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import pygsheets
import datetime
import pandas as pd

# API Key
TOKEN = '317c04d61c5c3844449d220cd31f15641ade772114e359788ff3502ef6faddb1' # replace YOUR_API_KEY with the API key you got from sec-api.io after sign up
# API endpoint
API = "https://api.sec-api.io?token=" + TOKEN

# define the filter parameters you want to send to the API 
payload_10Q = {
  "query": { "query_string": { "query": "cik:320193 AND filedAt:{2016-01-01 TO 2016-12-31} AND formType:\"10-Q\"" } },
  "from": "0",
  "size": "10",
  "sort": [{ "filedAt": { "order": "desc" } }]
}

payload = {
  "query": { "query_string": { "query": "cik:* AND filedAt:{2020-06-25 TO 2020-06-27} AND formType:\"SC 13D\"" } },
  "from": "0",
  "size": "10",
  "sort": [{ "filedAt": { "order": "desc" } }]
}


# format your payload to JSON bytes
jsondata = json.dumps(payload)
jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes

headers = {'Content-Type': 'application/json; charset=utf-8', 'Content-Length': len(jsondataasbytes)}

# res1 = requests.post(url=API, headers=headers, json=jsondataasbytes)

# instantiate the request 
req = urllib.request.Request(API)

# set the correct HTTP header: Content-Type = application/json
req.add_header('Content-Type', 'application/json; charset=utf-8')
# set the correct length of your request
req.add_header('Content-Length', len(jsondataasbytes))

# send the request to the API
response = urllib.request.urlopen(req, jsondataasbytes)

# read the response 
res_body = response.read()
# transform the response into JSON
filings = json.loads(res_body.decode("utf-8"))

# print JSON 
print(filings)

with open('filingsResponse.json', 'w') as f:
    f.write(str(filings))


# print(f'requests')
# print(res1)
df = pd.DataFrame(columns=['ticker', 'companyName', 'entity1', 'entity2', 'sharesIssued', 'purchasePrice', 'filingDate', 'filingDetailLink'])
print(f"Records returned: {filings['total']['value']}")
gc = pygsheets.authorize() # must have client_secret.json
sh = gc.open('TimeMachine_1')
wks = sh.sheet1
wks.update_value('B5', 'test')
for company in filings['filings']:
    ticker = company['ticker']
    print(f"{company['ticker']}")
    companyName = company['companyName']
    print(f"{company['companyName']}")
    formType = company['formType']
    print(f"{company['formType']}")
    filedAt = company['filedAt']
    print(f"{company['filedAt']}")
    print(f"{company['accessionNo']}")
    accessionNo = company['accessionNo']

    print(f"{company['linkToTxt']}")
    linkToTxt = company['linkToTxt']

    print(f"The link to filing details are: {company['linkToFilingDetails']}\n")
    linkToFilingDetails = company['linkToFilingDetails']
    
    print(f"{company['entities'][0]['companyName']}")
    entity1 = company['entities'][0]['companyName']
    print(f"{company['entities'][1]['companyName']}")
    entity2 = company['entities'][1]['companyName']

    filingData = requests.get(url = linkToTxt)
    #print(f'{filingData.content}')

    soup = BeautifulSoup(filingData.content, 'html.parser')
    tdTags = soup.find_all('td')
    for tag in tdTags:
        #sharesBought = tag.find('Aggregate Amount Beneficially Owned by Each Reporting Person')
        sharesBought = re.search(r'aggregate amount beneficially owned by each reporting person', str(tag.text).lower())
        if sharesBought is not None:
            print(sharesBought.group())
            sharesNum = tag.find_all('p')
            try:
                print(sharesNum[2].text)
                sharesAmount = sharesNum[2].text
                purchasePrice = 0
                data = {'ticker': ticker, 'companyName': companyName, 'entity1':entity1, 'entity2': entity2, 'sharesIssued': sharesAmount, 'purchasePrice': purchasePrice, 'filingDate': filedAt, 'filingDetailLink': linkToFilingDetails}
                df = df.append(data)
                print(df)
            except:
                pass # edge case not caught by scraper: https://www.sec.gov/Archives/edgar/data/894627/000092189520001864/0000921895-20-001864.txt 

    print(df)
    print(f"_______________________")



    

    
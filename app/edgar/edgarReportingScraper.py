import sqlite3, requests, datetime, re
from lxml import html, etree
from bs4 import BeautifulSoup
import pandas as pd
import pygsheets


url = "https://www.sec.gov/cgi-bin/current?q1=0&q2=0&q3=SC+13D"

payload = {}
headers = {
  'Host': 'www.sec.gov',
  'Referer': 'https://www.sec.gov/edgar/searchedgar/currentevents.htm',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

response = requests.request("GET", url, headers=headers, data = payload)
print(response.status_code)
print(response.content.decode('utf-8'))
# print(response.text.encode('utf8'))

soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
# print(soup)

filings_table = soup.find('table')
# print(filings_table)

filings_list = str(filings_table).split('\n')

filing_df = pd.DataFrame(columns=['Company Name', 'Filing Detail Link'])
company_name_list = []
company_filing_detail_link_list = []
for filing_line in filings_list:
    filing_line = re.sub(' +',' ',filing_line) #https://stackoverflow.com/questions/37445285/how-to-best-replace-multiple-whitespaces-by-one-in-python/37445349;  https://stackoverflow.com/questions/2077897/substitute-multiple-whitespace-with-single-whitespace-in-python
    filing_line = filing_line.split(' ',6) # https://stackoverflow.com/questions/30636248/split-a-string-only-by-first-space-in-python/30636260    
    # print(filing_line)
    if len(filing_line) == 7 and filing_line[0] == '08-04-2020':
        print(filing_line[6]+': sec.gov'+filing_line[2].replace('href="','').replace('">SC',''))
        company_name_list.append(filing_line[6])
        filing_detail_link = filing_line[2].replace('href="','').replace('">SC','')
        company_filing_detail_link_list.append(filing_detail_link)

# pd.set_option('display.max_columns', 0)
filing_df['Company Name'] = company_name_list
filing_df['Filing Detail Link'] = company_filing_detail_link_list
print(filing_df)

#Full XPath: /html/body/div[4]/div[2]/div/table/tbody/tr[2]/td[3]/a
#XPath: //*[@id="formDiv"]/div/table/tbody/tr[2]/td[3]/a
filing_form_link_list = []
filing_df2 = pd.DataFrame(columns=['Company Name', 'Filing Form Link'])
for link in filing_df['Filing Detail Link']:
    # print('sec.gov'+link)
    full_link = 'https://sec.gov'+link
    #print(full_link)
    res = requests.get(url=full_link, headers=headers)
    #print(res.status_code)
    # print(response.content.decode('utf-8'))
    tree = html.fromstring(res.content.decode('utf-8'))
    root = etree.tostring(tree).decode('utf-8')
    soup2 = BeautifulSoup(root, 'html.parser')
    table2 = soup2.find('table')
    # print(table2)
    link_set2 = table2.find_all('a', href=True)
    #print(link_set2[0]['href'])
    filing_form_link_list.append('https://sec.gov'+link_set2[0]['href'])

filing_df2['Company Name'] = company_name_list
filing_df2['Filing Form Link'] = filing_form_link_list
print(filing_df2)

gc = pygsheets.authorize() # must have client_secret.json
sh = gc.open('TimeMachine_1')
wks = sh.sheet1
#wks.update_value('B5', 'test')
wks.set_dataframe(filing_df2, (1,1))

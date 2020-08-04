import sqlite3, requests, datetime, re
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

# print(response.text.encode('utf8'))

soup = BeautifulSoup(response.content, 'html.parser')
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
    if len(filing_line) == 7 and filing_line[0] == '08-03-2020':
        print(filing_line[6]+': sec.gov'+filing_line[2].replace('href="','').replace('">SC',''))
        company_name_list.append(filing_line[6])
        filing_detail_link = filing_line[2].replace('href="','').replace('">SC','')
        company_filing_detail_link_list.append(filing_detail_link)

# pd.set_option('display.max_columns', 0)
filing_df['Company Name'] = company_name_list
filing_df['Filing Detail Link'] = company_filing_detail_link_list
print(filing_df)

    

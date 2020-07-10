import sqlite3, requests, datetime, re, json, argparse, os, sys, six, pygsheets
from bs4 import BeautifulSoup
import pandas as pd
from pandas.tseries.offsets import BDay # A utility for handling business days: https://stackoverflow.com/questions/2224742/most-recent-previous-business-day-in-python
import numpy as np
import time
from prettytable import PrettyTable
import pyfiglet
from pyfiglet import figlet_format
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt, style_from_dict)
#from pyconfigstore import ConfigStore

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None

import camelot
 
style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})



############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################


class seekingAlphaMiner():
    #################################################
    #    #####  ####### #######    #     # ######   #
    #   #     # #          #       #     # #     #  #
    #   #       #          #       #     # #     #  #
    #    #####  #####      #       #     # ######   #
    #         # #          #       #     # #        #
    #   #     # #          #       #     # #        #
    #    #####  #######    #        #####  #        #
    #################################################
    def deleteDatabase(self):
        databaseName = self.getDatabaseName()
        if os.path.exists(databaseName):
            os.remove(databaseName)
        return

    def rotateLog(self):
        if os.path.exists('excel/seekingAlphaLog.csv'):
            os.rename('excel/seekingAlphaLog.csv', f'excel/seekingAlphaLog_{datetime.datetime.now()}.csv')
        if os.path.exists('err/errorLog.txt'):
            os.rename('err/errorLog.txt', f'err/errorLog_{datetime.datetime.now()}.txt')
        if os.path.exists('seekingAlpha.db'):
            os.rename('seekingAlpha.db',f'seekingAlpha_{datetime.datetime.now()}.db')
        return

    def ifNotExistsCreateDB(self):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        createBalanceSheetsTable = f'''CREATE TABLE IF NOT EXISTS balanceSheets (
            rowid INTEGER PRIMARY KEY, companyTicker TEXT, timeScale TEXT, date datetime, lineItemName TEXT, lineItemDesc TEXT, lineItemSectionGroup TEXT, rawValue INTEGER, yearOverYearGrowthValue INTEGER, percentageOfGroup INTEGER
        ); '''
        createCashFlowsTable = f'''CREATE TABLE IF NOT EXISTS cashFlows (
            rowid INTEGER PRIMARY KEY, companyTicker TEXT, timeScale TEXT, date datetime, lineItemName TEXT, lineItemDesc TEXT, lineItemSectionGroup TEXT, rawValue INTEGER, yearOverYearGrowthValue INTEGER
        ); '''
        createIncomeStatementsTable = f'''CREATE TABLE IF NOT EXISTS incomeStatements( 
            rowid INTEGER PRIMARY KEY, companyTicker TEXT, timeScale TEXT, date datetime, lineItemName TEXT, lineItemDesc TEXT, lineItemSectionGroup TEXT, rawValue INTEGER, yearOverYearGrowthValue INTEGER, percentageOfRevenue INTEGER
        ); '''
        createRealTimePricesTable = f'''CREATE TABLE IF NOT EXISTS priceAction (
            rowid INTEGER PRIMARY KEY, companyTicker TEXT, date datetime, open INTEGER, high INTEGER, low INTEGER, close INTEGER, previousClose INTEGER, low52Week INTEGER, high52Week INTEGER
        ); '''
        createStudyFutureCouponTable = f'''CREATE TABLE IF NOT EXISTS study_futureCoupon(
            rowid INTEGER PRIMARY KEY, companyTicker TEXT,  coupon INTEGER, growth INTEGER, sampleDate datetime
        ); '''
        createOverviewDataTable = f'''CREATE TABLE IF NOT EXISTS overviewData (
            rowid INTEGER PRIMARY KEY, companyTicker TEXT, sector TEXT, industry TEXT
        ); '''
        createTickersTable = f'''CREATE TABLE IF NOT EXISTS tickers (rowid INTEGER PRIMARY KEY, ticker TEXT); '''
        createOptionsDataTable = f'''CREATE TABLE IF NOT EXISTS optionsData (
            rowid INTEGER PRIMARY KEY, companyTicker TEXT, optionType TEXT, strikePrice INTEGER, inTheMoney TEXT, expirationDate datetime, askPrice INTEGER, askSize INTEGER,askTime datetime, askDate datetime, askDateTime datetime, bidPrice INTEGER, bidSize INTEGER, bidTime datetime, bidDate datetime, bidDateTime datetime, contractExchange TEXT, openInterest TEXT, openInterestDate datetime, openPrice INTEGER, high INTEGER, low INTEGER, close INTEGER, last INTEGER, lastPrice INTEGER, previousClose INTEGER, change INTEGER, percentChange INTEGER, volume INTEGER, delay INTEGER,time datetime, date datetime, dateTime datetime, year datetime, month datetime); '''
        createSecFilingsTable = f'''CREATE TABLE IF NOT EXISTS secFilings (rowid INTEGER PRIMARY KEY, companyTicker TEXT, filingID INTEGER, filingURI TEXT, filingFormName TEXT, filingDescription TEXT, filingDate datetime, filingPDF TEXT); '''
        createTickersTable = f'''CREATE TABLE IF NOT EXISTS tickers (rowid INTEGER PRIMARY KEY, ticker TEXT); '''
        cursor.execute(createBalanceSheetsTable)
        cursor.execute(createCashFlowsTable)
        cursor.execute(createIncomeStatementsTable)
        cursor.execute(createRealTimePricesTable)
        cursor.execute(createStudyFutureCouponTable)
        cursor.execute(createOverviewDataTable)
        cursor.execute(createOptionsDataTable)
        cursor.execute(createSecFilingsTable)

        sqliteConnection.commit()
        sqliteConnection.close()

        return

    def addTableIndexing(self):
        queryString = f'''CREATE INDEX IF NOT EXISTS tag_companyTicker on incomeStatements (companyTicker);
            CREATE INDEX IF NOT EXISTS tag_companyTicker2 on balanceSheets (companyTicker);
            CREATE INDEX IF NOT EXISTS tag_companyTicker3 on cashFlows (companyTicker); '''
        return

    def getSeekingAlphaProCookie(self):
        if os.path.exists('seekingAlphaProCookie.txt'):
            with open('seekingAlphaProCookie.txt', 'r') as f:
                seekingAlphaProCookie = f.readline()
            # print(seekingAlphaProCookie)
        else:
            seekingAlphaProCookie = ''
        return seekingAlphaProCookie 

    def getRequestHeaders(self,ticker):
        seekingAlphaProCookie = self.getSeekingAlphaProCookie()
        headers = { # Necessary or else requests are 403 Forbidden 
            'Referer': f'https://seekingalpha.com/symbol/{ticker}/balance-sheet',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'cookie': f'{seekingAlphaProCookie}'
            # 'cookie': 'machine_cookie=4731953277079; _gcl_au=1.1.1199554884.1584215784; _pxvid=e2354d36-662d-11ea-b255-0242ac12000c; h_px=1; portfolio_sort_type=a_z; has_paid_subscription=true; ever_pro=1; user_id=51399747; user_nick=; user_devices=1; u_voc=209; marketplace_author_slugs=; user_perm=; sapu=12; user_remember_token=b663c1290b28648465ba3a9318b2ba5e8c9035fc; user_cookie_key=vhepn; _igt=3eff2345-50a2-4b60-a8c4-39cd61c4c355; _ig=9df61b54-419a-4482-cdc5-03229a410f9c; _ga=GA1.2.2136682556.1587757982; _gid=GA1.2.584912144.1587757982; ga_clientid=2136682556.1587757982; __pnahc=0; __tbc=%7Bjzx%7DlCp-P5kTOqotpgFeypItnKS3A44UHT9sb1IJ3lxi9-tdsGRLenQpOSERaaj8bTeUNfdIs_-76qPyuNAwJKCo47DY3s-wYK4D6WUV902MnXUHRK2A0IQ6GtabSFotCECnUVgFAp6l8Mpn6PJS7yCpyA; __pat=-14400000; __pvi=%7B%22id%22%3A%22v-2020-04-24-13-53-04-540-XMRlyuZeOafKa7bz-bcf2d031d41cb6b433743ba653047c89%22%2C%22domain%22%3A%22.seekingalpha.com%22%2C%22time%22%3A1587757987298%7D; xbc=%7Bjzx%7DvCGphVlY9G4xxbXMbU8IuTNHJT8Yqbk_90HouEauVQaYv8bfeCicutcYPlBHwdzy1ZubkHNyv6fLEAD6-vDWEoAg9zPeinc0DHqVA8piSbx4R-DLnTT5L3pBjNj5xQKkYi-Jf5mLolR2HyrLdfZkSV3Ytksz2sJ95qmuyU4zL9PkrBZxm_xYO9jUpIbQyW2f_AIz6V5o4jfaAvpwM2_Yiv7eCg92K16Z4rOuGrbH9bNLMAJ0FFexg1wu-Mkhj1AoTG8hAhNgJGQp7GSaonPHI8AIFVrGkvP41Ki_RUI2ZI4AG_FThVhuJP0IL71oUyMF0SnHBlGobcIZ5e7MEvgRRffWX98O0pYApIiqxmqtQXdS6Zg77YBXUbQ6ipG9T64BY55zeAhJ8O0UVdNJJKec8PAm6GzbDAptjt-JnZJfx50; _pxff_axt=540; _pxff_wa=1,702; __adblocker=true; _px2=eyJ1IjoiZjljYjc3MDAtODY3OC0xMWVhLTg5OTItZWQwZjgwNzZhMzU0IiwidiI6ImUyMzU0ZDM2LTY2MmQtMTFlYS1iMjU1LTAyNDJhYzEyMDAwYyIsInQiOjE1ODc3NjY5NzMzNjIsImgiOiI0MzAwNmU0ZGFiZDA5Yzc3NWZlZjgxZmI1N2U4ZGE0ODYxMjBlZTc1MjkzNzQ4MzAyNTZhZDJhYzlkYjczZDI2In0=; _px=1UFk9dAcIQDjrYO2j89NyN584WxgNLDjvaT8/P0q9/xUzwEJkHlGaMhWqmkn6cea+RBEggbqLx6+y+NYK0B92w==:1000:Ok0hU+SBeflq6QESBQeZGfaK1WWmMyTqv8KuDNQIf8ivAQEFXfO7LptURzbEsnPbE+g77f1lHUckIGKHu6LaWa8t7OhjE38HxSJd+qEmDn4wZU3gRgziEWCLLVSq7sxcYKXj0uMOgpicXT5f5A/+s6Q7DQuZRDX00ftllKw6Ne0zdIYEv75z3TS0VelWOPCDsuJM1rfhn60UvBbw6nEbLKcRAeW7k4eyP4z9CeVi7IIBe0SjW//KSW9mwWTw12IvigKq1OHZO7mWg679nD/Y8w==; _pxde=ca77bdecb75957e177e3bf4c87ca8c1d5e2c32ef6b70926ffb9698baace9a54f:eyJ0aW1lc3RhbXAiOjE1ODc3NjY0OTE5NzIsImZfa2IiOjAsImZfdHlwZSI6InciLCJmX2lkIjoiMjE0NTMyNGYtZjRmZC00MGUyLTljZWQtMzJmZTdkMmU2MWJjIiwiZl9vcmlnaW4iOiJjdXN0b20ifQ==; gk_user_access=1*archived*1587766496; gk_user_access_sign=bd71b99f8e0161e0eae23c03a3ba0c446bcbdb82'
        }

        return headers


    def getDatabaseName(self):
        # databaseName = f'seekingAlpha_{datetime.datetime.now().strftime("%Y%m%d")}.db'
        databaseName = 'seekingAlpha2.db'
        return databaseName

    def setDatabaseName(self):
        databaseName = f'seekingAlpha_{datetime.datetime.now().strftime("%Y%m%d")}.db'
        return

    def log(self, string, color, font="slant", figlet=False):
        if colored:
            if not figlet:
                six.print_(colored(string, color))
            else:
                six.print_(colored(figlet_format(
                    string, font=font), color))
        else:
            six.print_(string)


    #     # ####### ######      #####   #####  ######     #    ######  ####### ######   #####  
    #  #  # #       #     #    #     # #     # #     #   # #   #     # #       #     # #     # 
    #  #  # #       #     #    #       #       #     #  #   #  #     # #       #     # #       
    #  #  # #####   ######      #####  #       ######  #     # ######  #####   ######   #####  
    #  #  # #       #     #          # #       #   #   ####### #       #       #   #         # 
    #  #  # #       #     #    #     # #     # #    #  #     # #       #       #    #  #     # 
     ## ##  ####### ######      #####   #####  #     # #     # #       ####### #     #  #####  

    def getCompanyOverviewData(self,ticker):
        url = f'https://seekingalpha.com/symbol/{ticker}/overview'
        headers = self.getRequestHeaders(ticker)
        overviewPage = requests.get(url=url, headers=headers)
        # print(overviewPage.status_code)
        # print(overviewPage.content)
        soup = BeautifulSoup(overviewPage.content, 'html.parser')
        # print(soup)
        # with open('overviewPage.html', 'w') as f:
        #     f.write(str(soup))
        scriptSections = soup.find('script', text=re.compile("window.SA = "))
        # print(scriptSections)
        # data = str(scriptSections)[str(scriptSections).find('window.SA = '):str(scriptSections).find('industryname')]
        try:
            sector = re.search(r'"sectorname":"[A-Za-z ]*"', str(scriptSections)).group()
            sector = sector.replace('\'','')
            sectorName = sector.split(sep=':')[1]

        except:
            sector = '"Not Found"'
            sectorName = '"Not Found"'
        # sector = str(sector)

        # sector = {sector}
        # print(sector)
        # print(sectorName)
        try:
            industry = re.search(r'"industryname":"[A-Za-z ]*"', str(scriptSections)).group()
            industry = industry.replace('\'', '')
            industryName = industry.split(sep=':')[1]
        except:
            industry = '"Not Found"'
            industryName = '"Not Found"'

        # industry = str(industry)
        # print(industryName)

        headers = self.getRequestHeaders(ticker)
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        overviewData_insertQuery = f'INSERT INTO overviewData (companyTicker, sector, industry) VALUES ("{ticker}", {sectorName}, {industryName});'
        cursor.execute(overviewData_insertQuery)
        sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()


            # dataSection = sec.find('A')
        # for sec in scriptSections:
        #     print(dataSection)
        return overviewPage.status_code

    ########################################################################
    #      #    ######  ###    #     # ### #     # ####### ######   #####   #
    #     # #   #     #  #     ##   ##  #  ##    # #       #     # #     #  #
    #    #   #  #     #  #     # # # #  #  # #   # #       #     # #        #
    #   #     # ######   #     #  #  #  #  #  #  # #####   ######   #####   #
    #   ####### #        #     #     #  #  #   # # #       #   #         #  #
    #   #     # #        #     #     #  #  #    ## #       #    #  #     #  #
    #   #     # #       ###    #     # ### #     # ####### #     #  #####   #
    ########################################################################
    def getBalanceSheetData(self,ticker):
        headers = self.getRequestHeaders(ticker)
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        balanceSheetAnnualURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=annual&statement_type=balance-sheet&order_type=latest_left&is_pro=True'
        balanceSheetQuarterlyURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=balance-sheet&order_type=latest_left&is_pro=True'
        balanceSheetRes = requests.get(url=balanceSheetAnnualURL, headers=headers)

        companyAnnualBalanceSheet = {}
        try:
            companyAnnualBalanceSheet = balanceSheetRes.json()
        except:
            companyAnnualBalanceSheet['data'] = ''
            pass

        if balanceSheetRes.status_code == 200 and len(companyAnnualBalanceSheet['data']) != 0:
            for datum in companyAnnualBalanceSheet['data']: # there is one list of objects per line item
                for item in datum:
                    for cell in item:
                        if cell['class'].startswith('left-label'):
                            lineItemName = cell['value']
                            lineItemDesc = cell['name']
                            lineItemSectionGroup = cell['sectionGroup']
                        if cell['class'].startswith('value'):
                            if cell['class'].startswith('value'):
                                if 'TTM' in cell['name']:
                                    timeScale = 'annual_TTM'
                                    date = datetime.datetime.now()
                                elif 'Last Report' in cell['name']:
                                    timeScale = 'annual_lastReport'
                                    date = datetime.datetime.now()
                                else:
                                    timeScale = 'annual'
                                    date = datetime.datetime.strptime(cell['name'], '%b %Y')
                            if 'raw_value' in cell.keys():
                                if '(' in cell['raw_value']:
                                    rawValue = round(format(-float(cell['raw_value'].strip('()').strip("'").replace(',','')), 'f'), 2)
                                else:
                                    rawValue = round(float(cell['raw_value'].replace(",","")),2)
                                    # print(rawValue)
                            else:
                                rawValue = np.nan
                            if 'yoy_value' in cell.keys():
                                if '(' in cell['yoy_value']:
                                    yoyValue = -float(cell['yoy_value'].strip('()').strip("%").replace(',',''))
                                elif '-' in cell['yoy_value']:
                                    yoyValue = np.nan
                                else:
                                    yoyValue = float(cell['yoy_value'].strip("%").replace(',',''))
                            else:
                                yoyValue = np.nan
                            if 'asset_percent' in cell.keys():
                                if '(' in cell['asset_percent']:
                                    percentageOfGroup = -float(cell['asset_percent'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['asset_percent'] or 'NM' in cell['asset_percent']:
                                    percentageOfGroup = np.nan
                                else:
                                    try: 
                                        percentageOfGroup = float(cell['asset_percent'].strip('%').replace(',',''))
                                    except:
                                        percentageOfGroup = np.nan
                            elif 'liability_percent' in cell.keys():
                                if '(' in cell['liability_percent']:
                                    percentageOfGroup = -float(cell['liability_percent'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['liability_percent'] or 'NM' in cell['liability_percent']:
                                    percentageOfGroup = np.nan
                                else:
                                    try:
                                        percentageOfGroup = float(cell['liability_percent'].strip('%').replace(',',''))
                                    except:
                                        percentageOfGroup = np.nan
                            else:
                                percentageOfGroup = np.nan
                            #print(f''' INSERT INTO balanceSheets (companyTicker, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}', '{date}', '{lineItemName}', '{lineItemDesc}', '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');''')
                            insertRecord_SQL = f''' INSERT INTO balanceSheets (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}','{timeScale}', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');'''
                            cursor.execute(insertRecord_SQL)
                            sqliteConnection.commit()

        #time.sleep(5)    
        balanceSheetQuarterlyRes = requests.get(url=balanceSheetQuarterlyURL, headers=headers)
        # print(balanceSheetQuarterlyRes.status_code)
        companyQuarterlyBalanceSheet = {}
        try:
            companyQuarterlyBalanceSheet = balanceSheetQuarterlyRes.json()
        except:
            companyQuarterlyBalanceSheet['data'] = ''
            pass
        date=''
        for datum in companyQuarterlyBalanceSheet['data']: # there is one list of objects per line item, # TODO: cutting off final list item, Supplimental Info is a different data model
            for item in datum:
                if balanceSheetQuarterlyRes.status_code == 200 and len(companyQuarterlyBalanceSheet['data']) != 0:
                    for cell in item:
                        if cell['class'].startswith('left-label'):
                            lineItemName = cell['value']
                            lineItemDesc = cell['name']
                            lineItemSectionGroup = cell['sectionGroup']
                        if cell['class'].startswith('value'):
                            if cell['class'].startswith('value'):
                                if 'TTM' in cell['name']:
                                    timeScale = 'quarterly_TTM'
                                    date = datetime.datetime.now()
                                elif 'Last Report' in cell['name']:
                                    timeScale = 'quarterly_lastReport'
                                    date = datetime.datetime.now()
                                else:
                                    timeScale = 'quarterly'
                                    date = datetime.datetime.strptime(cell['name'], '%b %Y')
                            if 'raw_value' in cell.keys():
                                if '(' in cell['raw_value']:
                                    rawValue = round(-float(cell['raw_value'].strip('()').replace(',','')),2)
                                else:
                                    rawValue = round(float(cell['raw_value'].replace(',','')),2)
                            else:
                                rawValue = np.nan
                            if 'yoy_value' in cell.keys():
                                if '(' in cell['yoy_value']:
                                    yoyValue = -float(cell['yoy_value'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['yoy_value'] or 'NM' in cell['yoy_value']:
                                    yoyValue = np.nan
                                else:
                                    yoyValue = float(cell['yoy_value'].strip('%').replace(',',''))
                            else:
                                yoyValue = np.nan
                            if 'asset_percent' in cell.keys():
                                if '(' in cell['asset_percent']:
                                    percentageOfGroup = -float(cell['asset_percent'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['asset_percent'] or '' in cell['asset_percent']:
                                    percentageOfGroup = np.nan 
                                else:
                                    percentageOfGroup = float(cell['asset_percent'].strip('%').replace(',',''))
                            elif 'liability_percent' in cell.keys():
                                if '(' in cell['liability_percent']:
                                    percentageOfGroup = -float(cell['liability_percent'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['liability_percent'] or '' in cell['liability_percent']:
                                    percentageOfGroup = np.nan
                                else:
                                    percentageOfGroup = float(cell['liability_percent'].strip('%').replace(',',''))
                            else:
                                percentageOfGroup = np.nan
                            #print(f''' INSERT INTO balanceSheets (companyTicker, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}', '{date}', '{lineItemName}', '{lineItemDesc}', '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');''')
                            insertRecord_SQL = f''' INSERT INTO balanceSheets (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}','{timeScale}', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');'''
                            cursor.execute(insertRecord_SQL)
                            sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()
        return

    def getCashFlowData(self,ticker):
        headers = self.getRequestHeaders(ticker)
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        cashFlowAnnualURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=cash-flow-statement&order_type=latest_left&is_pro=True'
        cashFlowQuarterlyURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=cash-flow-statement&order_type=latest_left&is_pro=True'
        cashFlowAnnualRes = requests.get(url=cashFlowAnnualURL, headers=headers)
        # print(cashFlowAnnualRes.status_code)
        companyAnnualCashFlow = {}
        try:
            companyAnnualCashFlow = cashFlowAnnualRes.json()
        except:
            companyAnnualCashFlow['data'] = ''
            pass
        date=''
        if cashFlowAnnualRes.status_code == 200 and len(companyAnnualCashFlow['data']) != 0:
            for datum in companyAnnualCashFlow['data']: # there is one list of objects per line item, # TODO: cutting off final list item, Supplimental Info is a different data model
                for item in datum:
                    for cell in item:
                        if cell['class'].startswith('left-label'):
                            lineItemName = cell['value']
                            lineItemDesc = cell['name']
                            lineItemSectionGroup = cell['sectionGroup']
                        if cell['class'].startswith('value'):
                            if cell['class'].startswith('value'):
                                if 'TTM' in cell['name']:
                                    timeScale = 'annual_TTM'
                                    date = datetime.datetime.now()
                                elif 'Last Report' in cell['name']:
                                    timeScale = 'annual_lastReport'
                                    date = datetime.datetime.now()
                                else:
                                    timeScale = 'annual'
                                    date = datetime.datetime.strptime(cell['name'], '%b %Y')
                            if 'raw_value' in cell.keys():
                                if '(' in cell['raw_value']:
                                    rawValue = round(-float(cell['raw_value'].strip('()').replace(',','')),2)
                                else:
                                    rawValue = round(float(cell['raw_value'].replace(',','')),2)
                            else:
                                rawValue = np.nan
                            if 'yoy_value' in cell.keys():
                                if '(' in cell['yoy_value']:
                                    yoyValue = -float(cell['yoy_value'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['yoy_value'] or '' in cell['yoy_value']:
                                    yoyValue = np.nan
                                else:
                                    yoyValue = float(cell['yoy_value'].strip('%').replace(',',''))
                            else:
                                yoyValue = np.nan
                            insertRecord_SQL = f''' INSERT INTO cashFlows (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue) VALUES ('{ticker}','{timeScale}', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}');'''
                            cursor.execute(insertRecord_SQL)
                            sqliteConnection.commit()
        #time.sleep(5)
        cashFlowQuarterlyRes = requests.get(url=cashFlowQuarterlyURL, headers=headers)
        # print(cashFlowQuarterlyRes.status_code)
        companyQuarterlyCashFlow = {}
        try:
            companyQuarterlyCashFlow = cashFlowQuarterlyRes.json()
        except:
            companyQuarterlyCashFlow['data'] = ''
            pass
        date=''
        if cashFlowQuarterlyRes.status_code == 200 and len(companyQuarterlyCashFlow['data']) != 0:
            for datum in companyQuarterlyCashFlow['data']: # there is one list of objects per line item, # TODO: cutting off final list item, Supplimental Info is a different data model
                for item in datum:
                    for cell in item:
                        if cell['class'].startswith('left-label'):
                            lineItemName = cell['value']
                            lineItemDesc = cell['name']
                            lineItemSectionGroup = cell['sectionGroup']
                        if cell['class'].startswith('value'):
                            if cell['class'].startswith('value'):
                                if 'TTM' in cell['name']:
                                    timeScale = 'quarterly_TTM'
                                    date = datetime.datetime.now()
                                elif 'Last Report' in cell['name']:
                                    timeScale = 'quarterly_lastReport'
                                    date = datetime.datetime.now()
                                else:
                                    timeScale = 'quarterly'
                                    date = datetime.datetime.strptime(cell['name'], '%b %Y')
                            if 'raw_value' in cell.keys():
                                if '(' in cell['raw_value']:
                                    rawValue = round(-float(cell['raw_value'].strip('()').replace(',','')),2)
                                else:
                                    rawValue = round(float(cell['raw_value'].replace(',','')),2)
                            else:
                                rawValue = np.NaN
                            if 'yoy_value' in cell.keys():
                                if '(' in cell['yoy_value']:
                                    yoyValue = -float(cell['yoy_value'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['yoy_value'] or 'NM' in cell['yoy_value']:
                                    yoyValue = np.nan
                                else:
                                    yoyValue = float(cell['yoy_value'].strip('%').replace(',',''))
                            else:
                                yoyValue = np.NaN
                            #print(f''' INSERT INTO balanceSheets (companyTicker, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}', '{date}', '{lineItemName}', '{lineItemDesc}', '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');''')
                            insertRecord_SQL = f''' INSERT INTO cashFlows (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue) VALUES ('{ticker}','{timeScale}', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}');'''
                            cursor.execute(insertRecord_SQL)
                            sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()
        return

    def getIncomeStatementData(self,ticker):
        headers = self.getRequestHeaders(ticker)
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        incomeStatementAnnualURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=annual&statement_type=income-statement&order_type=latest_left&is_pro=True'
        incomeStatementQuarterlyURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=income-statement&order_type=latest_left&is_pro=True'
        incomeStatementAnnualRes = requests.get(url=incomeStatementAnnualURL, headers=headers)
        # print(incomeStatementAnnualRes.status_code)
        companyAnnualIncomeStatement = {}
        try:
            companyAnnualIncomeStatement = incomeStatementAnnualRes.json()
        except:
            companyAnnualIncomeStatement['data'] = ''
            pass

        date=''
        if incomeStatementAnnualRes.status_code == 200 and len(companyAnnualIncomeStatement['data']) != 0:
            for datum in companyAnnualIncomeStatement['data']: # there is one list of objects per line item, # TODO: cutting off final list item, Supplimental Info is a different data model
                for item in datum:
                    for cell in item:
                        if cell['class'].startswith('left-label'):
                            lineItemName = cell['value']
                            lineItemDesc = cell['name']
                            lineItemSectionGroup = cell['sectionGroup']
                        if cell['class'].startswith('value'):
                            if cell['class'].startswith('value'):
                                if 'TTM' in cell['name']:
                                    timeScale = 'annual_TTM'
                                    date = datetime.datetime.now()
                                elif 'Last Report' in cell['name']:
                                    timeScale = 'annual_lastReport'
                                    date = datetime.datetime.now()
                                else:
                                    timeScale = 'annual'
                                    date = datetime.datetime.strptime(cell['name'], '%b %Y')
                            if 'raw_value' in cell.keys():
                                if '(' in cell['raw_value']:
                                    rawValue = format(-float(cell['raw_value'].strip('()').replace(',','')), 'f')
                                elif 'NM' in cell['raw_value']:
                                    rawValue = np.nan
                                else:
                                    rawValue = format(float(cell['raw_value'].replace(',','')),'f')
                            else:
                                rawValue = np.NaN
                            if 'yoy_value' in cell.keys():
                                if '(' in cell['yoy_value']:
                                    yoyValue = -float(cell['yoy_value'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['yoy_value'] or 'NM' in cell['yoy_value']:
                                    yoyValue = np.nan
                                else:
                                    yoyValue = float(cell['yoy_value'].strip('%').replace(',',''))
                            else:
                                yoyValue = np.NaN
                            if 'revenue_percent' in cell.keys():
                                if '(' in cell['revenue_percent']:
                                    percentageOfRevenue = -float(cell['revenue_percent'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['revenue_percent'] or 'nan' in cell['revenue_percent'] or '' in cell['revenue_percent']:
                                    percentageOfRevenue = np.nan
                                else:
                                    # print(percentageOfRevenue)
                                    percentageOfRevenue = float(cell['revenue_percent'].strip('%').replace(',',''))
                            else:
                                percentageOfRevenue = np.nan
                            # print(f''' INSERT INTO balanceSheets (companyTicker, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}', '{date}', '{lineItemName}', '{lineItemDesc}', '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');''')
                            insertRecord_SQL = f''' INSERT INTO incomeStatements (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfRevenue) VALUES ('{ticker}','{timeScale}', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfRevenue}');'''
                            cursor.execute(insertRecord_SQL)
                            sqliteConnection.commit()
        #time.sleep(5)
        incomeStatementQuarterlyRes = requests.get(url=incomeStatementQuarterlyURL, headers=headers)
        # print(incomeStatementQuarterlyRes.status_code)
        companyQuarterlyIncomeStatement = {}
        try:
            companyQuarterlyIncomeStatement = incomeStatementQuarterlyRes.json()
        except:
            companyQuarterlyIncomeStatement['data'] = ''
            pass
        date=''
        if incomeStatementQuarterlyRes.status_code == 200 and len(companyQuarterlyIncomeStatement['data']) != 0:
            for datum in companyQuarterlyIncomeStatement['data']: # there is one list of objects per line item, # TODO: cutting off final list item, Supplimental Info is a different data model
                for item in datum:
                    for cell in item:
                        if cell['class'].startswith('left-label'):
                            lineItemName = cell['value']
                            lineItemDesc = cell['name']
                            lineItemSectionGroup = cell['sectionGroup']
                        if cell['class'].startswith('value'):
                            if 'TTM' in cell['name']:
                                timeScale = 'quarterly_TTM'
                                date = datetime.datetime.now()
                            elif 'Last Report' in cell['name']:
                                timeScale = 'quarterly_lastReport'
                                date = datetime.datetime.now()
                            else:
                                timeScale = 'quarterly'
                                date = datetime.datetime.strptime(cell['name'], '%b %Y')
                            if 'raw_value' in cell.keys():
                                if '(' in cell['raw_value']:
                                    rawValue = round(-float(cell['raw_value'].strip('()').replace(',','')),2)
                                elif 'NM' in cell['raw_value']:
                                    rawValue = np.nan
                                else:
                                    rawValue = round(float(cell['raw_value'].replace(',','')),2)
                            else:
                                rawValue = np.NaN
                            if 'yoy_value' in cell.keys():
                                if '(' in cell['yoy_value']:
                                    yoyValue = -float(cell['yoy_value'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['yoy_value'] or 'NM' in cell['yoy_value']:
                                    yoyValue = np.nan
                                else:
                                    yoyValue = float(cell['yoy_value'].strip('%').replace(',',''))
                            else:
                                yoyValue = np.NaN
                            if 'revenue_percent' in cell.keys():
                                if '(' in cell['revenue_percent']:
                                    percentageOfRevenue = -float(cell['revenue_percent'].strip('()').strip('%').replace(',',''))
                                elif '-' in cell['revenue_percent'] or '' in cell['revenue_percent']:
                                    percentageOfRevenue = np.nan
                                else:
                                    percentageOfRevenue = float(cell['revenue_percent'].strip('%').replace(',',''))
                            else:
                                percentageOfRevenue = np.nan
                            #print(f''' INSERT INTO balanceSheets (companyTicker, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}', '{date}', '{lineItemName}', '{lineItemDesc}', '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');''')
                            insertRecord_SQL = f''' INSERT INTO incomeStatements (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfRevenue) VALUES ('{ticker}','{timeScale}', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfRevenue}');'''
                            cursor.execute(insertRecord_SQL)
                            sqliteConnection.commit()

        #time.sleep(60)
        cursor.close()
        sqliteConnection.close()
        return

    def getRatings(self, ticker):
        quantRatingBreakdownURL = f'https://seekingalpha.com/symbol/{ticker}/cresscap/categories_ratings?pro=false'
        headers = { # Necessary or else requests are 403 Forbidden 
            'Referer': f'https://seekingalpha.com/symbol/{ticker}/balance-sheet',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'cookie': 'machine_cookie=4731953277079; _gcl_au=1.1.1199554884.1584215784; _pxvid=e2354d36-662d-11ea-b255-0242ac12000c; h_px=1; portfolio_sort_type=a_z; has_paid_subscription=true; ever_pro=1; user_id=51399747; user_nick=; user_devices=1; u_voc=209; marketplace_author_slugs=; user_perm=; sapu=12; user_remember_token=b663c1290b28648465ba3a9318b2ba5e8c9035fc; user_cookie_key=vhepn; _igt=3eff2345-50a2-4b60-a8c4-39cd61c4c355; _ig=9df61b54-419a-4482-cdc5-03229a410f9c; _ga=GA1.2.2136682556.1587757982; _gid=GA1.2.584912144.1587757982; ga_clientid=2136682556.1587757982; __pnahc=0; __tbc=%7Bjzx%7DlCp-P5kTOqotpgFeypItnKS3A44UHT9sb1IJ3lxi9-tdsGRLenQpOSERaaj8bTeUNfdIs_-76qPyuNAwJKCo47DY3s-wYK4D6WUV902MnXUHRK2A0IQ6GtabSFotCECnUVgFAp6l8Mpn6PJS7yCpyA; __pat=-14400000; __pvi=%7B%22id%22%3A%22v-2020-04-24-13-53-04-540-XMRlyuZeOafKa7bz-bcf2d031d41cb6b433743ba653047c89%22%2C%22domain%22%3A%22.seekingalpha.com%22%2C%22time%22%3A1587757987298%7D; xbc=%7Bjzx%7DvCGphVlY9G4xxbXMbU8IuTNHJT8Yqbk_90HouEauVQaYv8bfeCicutcYPlBHwdzy1ZubkHNyv6fLEAD6-vDWEoAg9zPeinc0DHqVA8piSbx4R-DLnTT5L3pBjNj5xQKkYi-Jf5mLolR2HyrLdfZkSV3Ytksz2sJ95qmuyU4zL9PkrBZxm_xYO9jUpIbQyW2f_AIz6V5o4jfaAvpwM2_Yiv7eCg92K16Z4rOuGrbH9bNLMAJ0FFexg1wu-Mkhj1AoTG8hAhNgJGQp7GSaonPHI8AIFVrGkvP41Ki_RUI2ZI4AG_FThVhuJP0IL71oUyMF0SnHBlGobcIZ5e7MEvgRRffWX98O0pYApIiqxmqtQXdS6Zg77YBXUbQ6ipG9T64BY55zeAhJ8O0UVdNJJKec8PAm6GzbDAptjt-JnZJfx50; _pxff_axt=540; _pxff_wa=1,702; __adblocker=true; _px2=eyJ1IjoiZjljYjc3MDAtODY3OC0xMWVhLTg5OTItZWQwZjgwNzZhMzU0IiwidiI6ImUyMzU0ZDM2LTY2MmQtMTFlYS1iMjU1LTAyNDJhYzEyMDAwYyIsInQiOjE1ODc3NjY5NzMzNjIsImgiOiI0MzAwNmU0ZGFiZDA5Yzc3NWZlZjgxZmI1N2U4ZGE0ODYxMjBlZTc1MjkzNzQ4MzAyNTZhZDJhYzlkYjczZDI2In0=; _px=1UFk9dAcIQDjrYO2j89NyN584WxgNLDjvaT8/P0q9/xUzwEJkHlGaMhWqmkn6cea+RBEggbqLx6+y+NYK0B92w==:1000:Ok0hU+SBeflq6QESBQeZGfaK1WWmMyTqv8KuDNQIf8ivAQEFXfO7LptURzbEsnPbE+g77f1lHUckIGKHu6LaWa8t7OhjE38HxSJd+qEmDn4wZU3gRgziEWCLLVSq7sxcYKXj0uMOgpicXT5f5A/+s6Q7DQuZRDX00ftllKw6Ne0zdIYEv75z3TS0VelWOPCDsuJM1rfhn60UvBbw6nEbLKcRAeW7k4eyP4z9CeVi7IIBe0SjW//KSW9mwWTw12IvigKq1OHZO7mWg679nD/Y8w==; _pxde=ca77bdecb75957e177e3bf4c87ca8c1d5e2c32ef6b70926ffb9698baace9a54f:eyJ0aW1lc3RhbXAiOjE1ODc3NjY0OTE5NzIsImZfa2IiOjAsImZfdHlwZSI6InciLCJmX2lkIjoiMjE0NTMyNGYtZjRmZC00MGUyLTljZWQtMzJmZTdkMmU2MWJjIiwiZl9vcmlnaW4iOiJjdXN0b20ifQ==; gk_user_access=1*archived*1587766496; gk_user_access_sign=bd71b99f8e0161e0eae23c03a3ba0c446bcbdb82'
        }
        quantRatingBreakdownRes = requests.get(url=quantRatingBreakdownURL, headers=headers)
        print(quantRatingBreakdownRes.status_code)
        print(quantRatingBreakdownRes.content)

        sellSideRatingURL = f'https://seekingalpha.com/symbol/{ticker}/ratings/analysis_summary_data'
        sellSideAnalystRatingsRes = requests.get(url=sellSideRatingURL, headers=headers)

        return

    def getPriceActionData(self, ticker):
        headers = {
            'Referer': f'https://seekingalpha.com/symbol/{ticker}/balance-sheet',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'cookie': 'machine_cookie=4731953277079; _gcl_au=1.1.1199554884.1584215784; _pxvid=e2354d36-662d-11ea-b255-0242ac12000c; h_px=1; portfolio_sort_type=a_z; has_paid_subscription=true; ever_pro=1; user_id=51399747; user_nick=; user_devices=1; u_voc=209; marketplace_author_slugs=; user_perm=; sapu=12; user_remember_token=b663c1290b28648465ba3a9318b2ba5e8c9035fc; user_cookie_key=vhepn; _igt=3eff2345-50a2-4b60-a8c4-39cd61c4c355; _ig=9df61b54-419a-4482-cdc5-03229a410f9c; _ga=GA1.2.2136682556.1587757982; _gid=GA1.2.584912144.1587757982; ga_clientid=2136682556.1587757982; __pnahc=0; __tbc=%7Bjzx%7DlCp-P5kTOqotpgFeypItnKS3A44UHT9sb1IJ3lxi9-tdsGRLenQpOSERaaj8bTeUNfdIs_-76qPyuNAwJKCo47DY3s-wYK4D6WUV902MnXUHRK2A0IQ6GtabSFotCECnUVgFAp6l8Mpn6PJS7yCpyA; __pat=-14400000; __pvi=%7B%22id%22%3A%22v-2020-04-24-13-53-04-540-XMRlyuZeOafKa7bz-bcf2d031d41cb6b433743ba653047c89%22%2C%22domain%22%3A%22.seekingalpha.com%22%2C%22time%22%3A1587757987298%7D; xbc=%7Bjzx%7DvCGphVlY9G4xxbXMbU8IuTNHJT8Yqbk_90HouEauVQaYv8bfeCicutcYPlBHwdzy1ZubkHNyv6fLEAD6-vDWEoAg9zPeinc0DHqVA8piSbx4R-DLnTT5L3pBjNj5xQKkYi-Jf5mLolR2HyrLdfZkSV3Ytksz2sJ95qmuyU4zL9PkrBZxm_xYO9jUpIbQyW2f_AIz6V5o4jfaAvpwM2_Yiv7eCg92K16Z4rOuGrbH9bNLMAJ0FFexg1wu-Mkhj1AoTG8hAhNgJGQp7GSaonPHI8AIFVrGkvP41Ki_RUI2ZI4AG_FThVhuJP0IL71oUyMF0SnHBlGobcIZ5e7MEvgRRffWX98O0pYApIiqxmqtQXdS6Zg77YBXUbQ6ipG9T64BY55zeAhJ8O0UVdNJJKec8PAm6GzbDAptjt-JnZJfx50; _pxff_axt=540; _pxff_wa=1,702; __adblocker=true; _px2=eyJ1IjoiZjljYjc3MDAtODY3OC0xMWVhLTg5OTItZWQwZjgwNzZhMzU0IiwidiI6ImUyMzU0ZDM2LTY2MmQtMTFlYS1iMjU1LTAyNDJhYzEyMDAwYyIsInQiOjE1ODc3NjY5NzMzNjIsImgiOiI0MzAwNmU0ZGFiZDA5Yzc3NWZlZjgxZmI1N2U4ZGE0ODYxMjBlZTc1MjkzNzQ4MzAyNTZhZDJhYzlkYjczZDI2In0=; _px=1UFk9dAcIQDjrYO2j89NyN584WxgNLDjvaT8/P0q9/xUzwEJkHlGaMhWqmkn6cea+RBEggbqLx6+y+NYK0B92w==:1000:Ok0hU+SBeflq6QESBQeZGfaK1WWmMyTqv8KuDNQIf8ivAQEFXfO7LptURzbEsnPbE+g77f1lHUckIGKHu6LaWa8t7OhjE38HxSJd+qEmDn4wZU3gRgziEWCLLVSq7sxcYKXj0uMOgpicXT5f5A/+s6Q7DQuZRDX00ftllKw6Ne0zdIYEv75z3TS0VelWOPCDsuJM1rfhn60UvBbw6nEbLKcRAeW7k4eyP4z9CeVi7IIBe0SjW//KSW9mwWTw12IvigKq1OHZO7mWg679nD/Y8w==; _pxde=ca77bdecb75957e177e3bf4c87ca8c1d5e2c32ef6b70926ffb9698baace9a54f:eyJ0aW1lc3RhbXAiOjE1ODc3NjY0OTE5NzIsImZfa2IiOjAsImZfdHlwZSI6InciLCJmX2lkIjoiMjE0NTMyNGYtZjRmZC00MGUyLTljZWQtMzJmZTdkMmU2MWJjIiwiZl9vcmlnaW4iOiJjdXN0b20ifQ==; gk_user_access=1*archived*1587766496; gk_user_access_sign=bd71b99f8e0161e0eae23c03a3ba0c446bcbdb82'
        }

        realTimePriceDataURL = f'https://finance.api.seekingalpha.com/v2/real-time-prices?symbols%5B%5D={ticker}'
        companyRealTimePriceRes = requests.get(url=realTimePriceDataURL, headers=headers)
        # print(companyRealTimePriceRes.status_code)
        # print(companyRealTimePriceRes.content)
        companyRealTimePriceData = companyRealTimePriceRes.json()
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        for datum in companyRealTimePriceData['data']:
            # print(datum['attributes']['close'])
            lastClose = datum['attributes']['close']
            low52Week = datum['attributes']['low52Week']
            high52Week = datum['attributes']['high52Week']
            lastCloseDateTime = datum['attributes']['dateTime']
            low = datum['attributes']['low']
            openPrice = datum['attributes']['open']
            high = datum['attributes']['high']
            previousClose = datum['attributes']['previousClose']
            recordInsertQuery = f'INSERT INTO priceAction (companyTicker ,date, open , high , low , close, previousClose, low52Week, high52Week) VALUES ("{ticker}","{lastCloseDateTime}", {openPrice}, {high}, {low}, {lastClose}, {previousClose}, {low52Week}, {high52Week});'
            try:
                cursor.execute(recordInsertQuery)
            except:
                pass
            sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()
        return

    def getXigniteOptionsToken(self):
        url = f'https://seekingalpha.com/market_data/xignite_token'
        xigniteTokenData = requests.get(url)
        xigniteTokenInfo = json.loads(xigniteTokenData.content.decode('utf-8'))
        token = xigniteTokenInfo['_token']
        userid = xigniteTokenInfo['_token_userid']
        return token, userid

    def getOptionsData(self,ticker):
        # headers = getRequestHeaders(ticker)
        # databaseName = getDatabaseName()
        # sqliteConnection = sqlite3.connect(databaseName)
        # cursor = sqliteConnection.cursor()
        token, userid = self.getXigniteOptionsToken()
        #month=12; year=2020
        currentMonth = datetime.datetime.now().month
        currentYear = datetime.datetime.now().year
        stopYear = currentYear + 3
            
        while currentYear != stopYear:
            getEquityOptionsDataURL = f'''https://globaloptions.xignite.com/xglobaloptions.json/GetEquityOptionChain?IdentifierType=Symbol&Identifier={ticker}&Month={currentMonth}&Year={currentYear}&SymbologyType=&OptionExchange=&_callback=SA.Utils.SymbolData.clb15901181749410&_token={token}&_token_userid={userid}&_=1590118174801 '''
            equityOptionsChainData = requests.get(url=getEquityOptionsDataURL)
            # print(equityOptionsChainData.content)
            # print(equityOptionsChainData.status_code)
            optionsInfoString = equityOptionsChainData.content.decode('utf-8')
            optionsInfo = re.search(r'\{.*\}', str(optionsInfoString)).group()
            optionsInfo = json.loads(optionsInfo)
            # print(optionsInfo['Quote'])
            if optionsInfo['Quote'] is None:
                pass
                # print(f'{ticker} options data not found')
            elif optionsInfo['Quote']['Outcome'] == 'Success':
                databaseName = self.getDatabaseName()
                sqliteConnection = sqlite3.connect(databaseName)
                cursor = sqliteConnection.cursor()
                try:
                    for contract in optionsInfo['Expirations'][0]['Calls']:
                        strikePrice = contract['StrikePrice']
                        inTheMoney = contract['InTheMoney']
                        expirationDate = contract['ExpirationDate']
                        askPrice = contract['Ask']
                        askSize = contract['AskSize']
                        # askTime = datetime.datetime.strptime(contract['AskTime'], '%-I:%M:%S %p') #format H:M:S PM
                        askTime = contract['AskTime']
                        # askDate = datetime.datetime.strptime(contract['AskDate'], '%-m/%-d/%Y') #format M/D/YYYY  # datetime format code list # https://www.programiz.com/python-programming/datetime/strftime
                        askDate = contract['AskDate']
                        askDateTime = askDate +' '+ askTime
                        try:
                            askDateTime = datetime.datetime.strptime(askDateTime, '%m/%d/%Y %I:%M:%S %p')
                        except:
                            askDateTime = ''
                            print(f'askDateTime conversion error: {askDate} and {askTime}')
                        #print(f"{datetime.datetime.strptime(askDate, '%-I:%M:%S %p')} + {datetime.datetime.strptime(askTime, '%-m/%-d/%Y')}")
                        bidPrice = contract['Bid']
                        bidSize = contract['BidSize']
                        # bidTime = datetime.datetime.strptime(contract['BidTime'], '%-I:%M:%S %p')
                        bidTime = contract['BidTime']
                        # bidDate = datetime.datetime.strptime(contract['BidDate'], '%-m/%-d/%Y')
                        bidDate = contract['BidDate']
                        bidDateTime = bidDate +' '+ bidTime
                        try:
                            bidDateTime = datetime.datetime.strptime(bidDateTime, '%m/%d/%Y %I:%M:%S %p')
                        except:
                            bidDateTime = ''
                            print(f'bidDateTime conversion error: {bidDate} and {bidTime}')
                        contractExchange = contract['Exchange']
                        openInterest = contract['OpenInterest']
                        openInterestDate = contract['OpenInterestDate']
                        openPrice = contract['Open']
                        high = contract['High']
                        low = contract['Low']
                        close = contract['Close']
                        last = contract['Last']
                        lastPrice = contract['LastSize']
                        previousClose = contract['PreviousClose']
                        change = contract['Change']
                        percentChange = contract['PercentChange']
                        volume = contract['Volume']
                        delay = contract['Delay']
                        time = contract['Time']
                        date = contract['Date']
                        try:
                            dateTime = date + ' '+time
                        except:
                            dateTime = ''
                        try:
                            dateTime = datetime.datetime.strptime(dateTime, '%m/%d/%Y %I:%M:%S %p')
                        except:
                            dateTime = ''
                            print(f'dateTime conversion error: {date} and {time}')
                        year = contract['Year']
                        month = contract['Month']                    
                        # callOptionContractInsertQuery = f'''INSERT INTO optionsData (companyTicker, optionType, strikePrice, inTheMoney, expirationDate, askPrice, askSize, askTime, askDate, bidPrice, bidSize, bidTime, bidDate, contractExchange, openInterest, openInterestDate, openPrice, high, low, close, last, lastPrice, previousClose, change, percentChange, volume, delay, time, date, year, month) VALUES ('{ticker}','call', {strikePrice}, '{inTheMoney}', '{expirationDate}', '{askPrice}', '{askSize}', '{askTime}', '{askDate}', '{bidPrice}', '{bidSize}', '{bidTime}', '{bidDate}', '{contractExchange}', '{openInterest}', '{openInterestDate}', {openPrice}, {high}, {low}, {close}, {last}, {lastPrice}, {previousClose}, {change}, {percentChange}, {volume}, {delay}, '{time}', '{date}', '{year}', '{month}'); '''
                        callOptionContractInsertQuery = f'''INSERT INTO optionsData (companyTicker, optionType, strikePrice, inTheMoney, expirationDate, askPrice, askSize,askTime, askDate, askDateTime, bidPrice, bidSize,bidTime,bidDate, bidDateTime, contractExchange, openInterest, openInterestDate, openPrice, high, low, close, last, lastPrice, previousClose, change, percentChange, volume, delay,time,date, dateTime, year, month) VALUES ('{ticker}','call', {strikePrice}, '{inTheMoney}', '{expirationDate}', '{askPrice}', '{askSize}', '{askTime}', '{askDate}', '{askDateTime}', '{bidPrice}', '{bidSize}', '{bidTime}', '{bidDate}', '{bidDateTime}', '{contractExchange}', '{openInterest}', '{openInterestDate}', {openPrice}, {high}, {low}, {close}, {last}, {lastPrice}, {previousClose}, {change}, {percentChange}, {volume}, {delay},'{time}', '{date}', '{dateTime}', '{year}', '{month}'); '''
                        print(callOptionContractInsertQuery)
                        # print(callOptionContractInsertQuery)
                        cursor.execute(callOptionContractInsertQuery)
                        sqliteConnection.commit()
                except:
                    pass

                try:
                    for contract in optionsInfo['Expirations'][0]['Puts']:
                        strikePrice = contract['StrikePrice']
                        inTheMoney = contract['InTheMoney']
                        expirationDate = contract['ExpirationDate']
                        askPrice = contract['Ask']
                        askSize = contract['AskSize']
                        # askTime = datetime.datetime.strptime(contract['AskTime'],  '%-I:%M:%S %p') #format H:M:S PM
                        askTime = contract['AskTime']
                        # askDate = datetime.datetime.strptime(contract['AskDate'], '%-m/%-d/%Y') #format M/D/YYYY
                        askDate = contract['AskDate']
                        try:
                            askDateTime = datetime.datetime.strptime(askDateTime, '%m/%d/%Y %I:%M:%S %p')
                        except:
                            askDateTime = ''
                            print(f'askDateTime conversion error: {askDate} and {askTime}')
                        bidPrice = contract['Bid']
                        bidSize = contract['BidSize']
                        # bidTime = datetime.datetime.strptime(contract['BidTime'], '%-I:%M:%S %p')
                        bidTime = contract['BidTime']
                        # bidDate = datetime.datetime.strptime(contract['BidDate'], '%-m/%-d/%Y')
                        bidDate = contract['BidDate']
                        try:
                            bidDateTime = datetime.datetime.strptime(bidDateTime, '%m/%d/%Y %I:%M:%S %p')
                        except:
                            bidDateTime = ''
                            print(f'bidDateTime conversion error: {bidDate} and {bidTime}')
                        contractExchange = contract['Exchange']
                        openInterset = contract['OpenInterest']
                        openInterestDate = contract['OpenInterestDate']
                        openPrice = contract['Open']
                        high = contract['High']
                        low = contract['Low']
                        close = contract['Close']
                        last = contract['Last']
                        lastPrice = contract['LastSize']
                        previousClose = contract['PreviousClose']
                        change = contract['Change']
                        percentChange = contract['PercentChange']
                        volume = contract['Volume']
                        delay = contract['Delay']
                        time = contract['Time']
                        date = contract['Date']
                        try:
                            dateTime = date + ' '+time
                        except:
                            dateTime = ''
                        try:
                            dateTime = datetime.datetime.strptime(dateTime, '%m/%d/%Y %I:%M:%S %p')
                        except:
                            dateTime = ''
                            print(f'DateTime conversion error: {date} and {time}')
                        year = contract['Year']
                        month = contract['Month']                   
                        # putOptionContractInsertQuery = f'''INSERT INTO optionsData (companyTicker, optionType, strikePrice, inTheMoney, expirationDate, askPrice, askSize, askTime, askDate, bidPrice, bidSize, bidTime, bidDate, contractExchange, openInterest, openInterestDate, openPrice, high, low, close, last, lastPrice, previousClose, change, percentChange, volume, delay, time, date, year, month) VALUES ('{ticker}','put', {strikePrice}, '{inTheMoney}', '{expirationDate}', '{askPrice}', '{askSize}', '{askTime}', '{askDate}', '{bidPrice}', '{bidSize}', '{bidTime}', '{bidDate}', '{contractExchange}', '{openInterset}', '{openInterestDate}', {openPrice}, {high}, {low}, {close}, {last}, {lastPrice}, {previousClose}, {change}, {percentChange}, {volume}, {delay}, '{time}', '{date}', '{year}', '{month}'); '''
                        putOptionContractInsertQuery =  f'''INSERT INTO optionsData (companyTicker, optionType, strikePrice, inTheMoney, expirationDate, askPrice, askSize,askTime,askDate, askDateTime, bidPrice, bidSize,bidTime,bidDate, bidDateTime, contractExchange, openInterest, openInterestDate, openPrice, high, low, close, last, lastPrice, previousClose, change, percentChange, volume, delay,time,date, dateTime, year, month) VALUES ('{ticker}','put', {strikePrice}, '{inTheMoney}', '{expirationDate}', '{askPrice}', '{askSize}','{askTime}', '{askDate}', '{askDateTime}', '{bidPrice}', '{bidSize}','{bidTime}', '{bidDate}', '{bidDateTime}', '{contractExchange}', '{openInterest}', '{openInterestDate}', {openPrice}, {high}, {low}, {close}, {last}, {lastPrice}, {previousClose}, {change}, {percentChange}, {volume}, {delay},'{time}', '{date}', '{dateTime}', '{year}', '{month}'); '''
                        # print(putOptionContractInsertQuery)
                        cursor.execute(putOptionContractInsertQuery)
                        sqliteConnection.commit()
                except:
                    pass
                cursor.close()
                sqliteConnection.close()
            else:
                pass
                # print(f'{ticker} options data not found')
            if currentMonth == 12:
                currentMonth = 1
                currentYear += 1
            else:
                currentMonth += 1

        return

    def getStatementOfBeneficialOwnershipSEC(self, ticker):
        # looking for Form SC 13D
        headers = self.getRequestHeaders(ticker)
        url = f'https://seekingalpha.com/symbol/{ticker}/filings-load-more.json?filing_type=all&order_by=filed_at&dir=desc&page=1' #increase page number as response is paginated to get more data further back in time
        try:
            res = requests.get(url=url, headers=headers).json()
        except:
            res = 0
            pass
        # print(res)
        if res == 0:
            pass
        else:
            databaseName = self.getDatabaseName()
            sqliteConnection = sqlite3.connect(databaseName)
            cursor = sqliteConnection.cursor()
            # Find where "form_name" = "SC 13D" and get "uri" field
            for filing in res:
                #if filing['form_name'] == 'SC 13D' or filing['form_name'] == 'SC 13D/A':
                # print(filing)
                url2 = f'https://seekingalpha.com{filing["uri"]}'
                res2 = requests.get(url=url2, headers=headers)
                #print(res2.content)
                soup = BeautifulSoup(res2.content, 'html.parser')
                container = soup.find('a', {"class": "filing-pdf pull-right"}, href=True) # https://stackoverflow.com/questions/5815747/beautifulsoup-getting-href
                # print(container['href'])
                # Append uri to base site url "https://seekingalpha.com"
                #url3 = f'https://seekingalpha.com{container["href"]}'
                # Send this request and get uri for PDF of filing
                # filingPDF = requests.get(url=url3, headers=headers)
                # #print(filingPDF.content)
                # with open(f'{ticker}_SC 13D_{filing["id"]}.pdf', 'wb') as f: # https://stackoverflow.com/questions/34503412/download-and-save-pdf-file-with-python-requests-module
                #     f.write(filingPDF.content)
                rules = {"pages":{"1":{"table_areas":["98.15094339622641,418.63614593091285,490.7547169811321,159.78337081600446"],"columns": 'null'},"2":{"table_areas":["0,792,612,0.04522706479705311"],"columns":'null'},"3":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"4":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"5":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"6":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"7":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"8":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"9":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"10":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"11":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"12":{"table_areas":["29.830188679245282,749.659769126186,580.2452830188679,269.48305989815896"],"columns":'null'},"13":{"table_areas":["20.20754716981132,790.0754440511903,586.0188679245283,310.8610127975681"],"columns":'null'},"14":{"table_areas":["20.20754716981132,784.301776204761,587.9433962264151,358.9749115178113"],"columns":'null'},"15":{"table_areas":["20.20754716981132,773.7167184863076,588.9056603773585,312.7855687463778"],"columns":'null'},"16":{"table_areas":["20.20754716981132,785.2640541791659,588.9056603773585,605.3180729654564"],"columns":'null'},"17":{"table_areas":["350.2641509433962,736.1878774845179,491.7169811320755,297.3891211559"],"columns":'null'},"18":{"table_areas":["350.2641509433962,772.7544405119028,571.5849056603773,478.29738034401436"],"columns":'null'},"19":{"table_areas":["0,792,612,0.04522706479705311"],"columns":'null'},"20":{"table_areas":["20.20754716981132,773.7167184863076,588.9056603773585,393.61691859638637"],"columns":'null'},"21":{"table_areas":["20.20754716981132,773.7167184863076,588.9056603773585,436.9194274446052"],"columns":'null'},"22":{"table_areas":["0,792,612,0.04522706479705311"],"columns":'null'},"23":{"table_areas":["350.2641509433962,772.7544405119028,566.7735849056604,358.9749115178113"],"columns":'null'},"24":{"table_areas":["350.2641509433962,772.7544405119028,538.8679245283018,610.1294628374808"],"columns":'null'},"25":{"table_areas":["20.20754716981132,736.1878774845179,586.9811320754717,457.12726490710736"],"columns":'null'},"26":{"table_areas":["20.20754716981132,773.7167184863076,587.9433962264151,495.61838388330193"],"columns":'null'},"27":{"table_areas":["159.73584905660377,766.9807726654735,586.9811320754717,516.788499320209"],"columns":'null'},"28":{"table_areas":["20.20754716981132,779.4903863327368,587.9433962264151,539.8831707059256"],"columns":'null'},"29":{"table_areas":["20.20754716981132,764.093938742259,547.5283018867924,291.6154533094708"],"columns":'null'},"30":{"table_areas":["20.20754716981132,772.7544405119028,241.52830188679246,478.29738034401436"],"columns":'null'}},"flavor":"Stream","row_close_tol":2,"col_close_tol":0,"split_text":False,"flag_size":False}
                try:
                    filingDescription = filing["description"].replace("'", "")
                except:
                    filingDescription = ''
                
                try:
                    insertQuery = f''' INSERT INTO secFilings (companyTicker, filingID , filingURI , filingFormName , filingDescription , filingDate , filingPDF ) VALUES ('{ticker}', '{filing["id"]}', 'https://seekingalpha.com{filing["uri"]}', '{filing["form_name"]}', '{filingDescription}', "{datetime.datetime.strptime(filing["date"], '%m/%d/%Y')}", 'https://seekingalpha.com{container["href"]}')'''
                except:
                    pass
                #https://strftime.org/ for datetime format codes
                #print(insertQuery)
                try:
                    cursor.execute(insertQuery)
                    sqliteConnection.commit()
                except:
                    pass

            cursor.close()
            sqliteConnection.close()

        return

    #########################################################################################################
    #   ######     #    #######    #       #     #    #    #     # ######  #       ####### ######   #####   #
    #   #     #   # #      #      # #      #     #   # #   ##    # #     # #       #       #     # #     #  #
    #   #     #  #   #     #     #   #     #     #  #   #  # #   # #     # #       #       #     # #        #
    #   #     # #     #    #    #     #    ####### #     # #  #  # #     # #       #####   ######   #####   #
    #   #     # #######    #    #######    #     # ####### #   # # #     # #       #       #   #         #  #
    #   #     # #     #    #    #     #    #     # #     # #    ## #     # #       #       #    #  #     #  #
    #   ######  #     #    #    #     #    #     # #     # #     # ######  ####### ####### #     #  #####   #
    #########################################################################################################
    def getLastClosePrice(self,ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        lastClosePriceQuery = f'select close, MAX(date) as date from priceAction where companyTicker = "{ticker}" AND close != "nan"; '
        lastClosePriceData = cursor.execute(lastClosePriceQuery).fetchall()
        lastClosePrice = lastClosePriceData[0][0]
        lastCloseDate = lastClosePriceData[0][1]
        #print(f'Last Close Price: {lastClosePrice}')

        cursor.close()
        sqliteConnection.close()
        return lastClosePrice

    def getFirstBasicEarningsPerShare(self,ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        firstBasicEPS_query = f'select MIN(date) as date, rawValue as firstBasicEPS from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual" AND rawvalue != "nan"; '
        firstBasicEPSData = cursor.execute(firstBasicEPS_query).fetchall()
        firstBasicEPS = firstBasicEPSData[0][1]
        # print(f'first after-tax EPS: {firstBasicEPS}')
        cursor.close()
        sqliteConnection.close()
        return firstBasicEPS

    def getLastBasicEarningsPerShare(self,ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        lastBasicEarningsPerShareQuery = f'select rawValue as eps,MAX(date) as date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual" AND rawvalue != "nan";'
        lastBasicEarningsPerShareData = cursor.execute(lastBasicEarningsPerShareQuery).fetchall()
        lastBasicEarningsPerShare = lastBasicEarningsPerShareData[0][0]

        cursor.close()
        sqliteConnection.close()
        return lastBasicEarningsPerShare

    def getFirstEffectiveTaxRate(self, ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        firstTaxRateQuery = f'select rawValue as firstTaxRate,MIN(date) as date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Effective Tax Rate" and timeScale = "annual" AND rawvalue != "nan";'
        firstTaxRateData = cursor.execute(firstTaxRateQuery).fetchall()

        if 'None' in str(firstTaxRateData[0][0]):
            firstEffectiveTaxRate = 0
        else:
            firstEffectiveTaxRate = firstTaxRateData[0][0]

        cursor.close()
        sqliteConnection.close()
        return firstEffectiveTaxRate

    def getLastEffectiveTaxRate(self, ticker): 
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        effectiveTaxRateQuery = f'select rawvalue as effectiveTaxRate, MAX(date) from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Effective Tax Rate" and timeScale = "annual" ;'
        lastEffectiveTaxRateData = cursor.execute(effectiveTaxRateQuery).fetchall()

        if 'None' in str(lastEffectiveTaxRateData[0][0]) or 'nan' in str(lastEffectiveTaxRateData[0][0]):
            lastEffectiveTaxRate = 0
        else:
            lastEffectiveTaxRate = lastEffectiveTaxRateData[0][0]

        cursor.close()
        sqliteConnection.close()
        return lastEffectiveTaxRate

    def getLastDividendPerShare(self, ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        divPerShareQuery = f'select MAX(date), rawvalue as divPerShare from incomeStatements where lineitemname = "Dividend Per Share" and companyTicker = "{ticker}" and timeScale = "annual" AND rawvalue != "nan"; '
        lastDivPerShareData = cursor.execute(divPerShareQuery).fetchall()
        lastDivPerShare = lastDivPerShareData[0][1]
        if lastDivPerShare == None:
            lastDivPerShare = 0

        #print(f'last div per share query result: {lastDivPerShare}')
        #print(f'Last Div Per Share: {lastDivPerShare}')
        cursor.close()
        sqliteConnection.close()
        return lastDivPerShare

    def getAnnualIncomeStatementDateRange(self, ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()

        countDistinctAnnualTimeScaleDates = f'select count(distinct(date)) from incomeStatements where companyTicker = "{ticker}" and timeScale = "annual" AND rawvalue != "nan";'
        queryData = cursor.execute(countDistinctAnnualTimeScaleDates).fetchall()
        numberOfDates = queryData[0][0]

        cursor.close()
        sqliteConnection.close()
        return numberOfDates

    def getAnnualLatestTotalCash(self, ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        queryString = f"SELECT rawvalue, max(Date) FROM balanceSheets where lineitemname like 'Total Cash & ST Investments' and companyticker = '{ticker}' and timescale = 'annual';"
        queryData = cursor.execute(queryString).fetchall()

        totalCash = queryData[0][0]
        if 'None' in str(totalCash):
            queryString2 = f'SELECT rawvalue, max(Date) FROM balanceSheets where lineitemname like "Cash And Equivalents" and companyticker = "{ticker}" and timescale = "annual"; '
            queryData2 = cursor.execute(queryString2).fetchall()
            totalCash = queryData2[0][0]

        cursor.close()
        sqliteConnection.close()
        return totalCash

    def getAnnualLatestTotalAssets(self, ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        queryString = f"SELECT rawvalue, max(Date) FROM balanceSheets where lineitemname like 'Total Assets' and companyticker = '{ticker}' and timescale = 'annual'; "
        queryData = cursor.execute(queryString).fetchall()

        totalAssets = queryData[0][0]

        cursor.close()
        sqliteConnection.close()
        return totalAssets

    def getAnnualLatestTotalLiabilities(self, ticker):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        queryString = f"SELECT rawvalue, max(Date) FROM balanceSheets where lineitemname like 'Total Liabilities' and companyticker = '{ticker}' and timescale = 'annual'; "
        queryData = cursor.execute(queryString).fetchall()
        totalLiabilities = queryData[0][0]

        cursor.close()
        sqliteConnection.close()
        return totalLiabilities


    #########################################################################
    ######  ### ####### #     # #######  #####   #####     #       #######  #####  ###  #####  
    #     #  #       #  ##    # #       #     # #     #    #       #     # #     #  #  #     # 
    #     #  #      #   # #   # #       #       #          #       #     # #        #  #       
    ######   #     #    #  #  # #####    #####   #####     #       #     # #  ####  #  #       
    #     #  #    #     #   # # #             #       #    #       #     # #     #  #  #       
    #     #  #   #      #    ## #       #     # #     #    #       #     # #     #  #  #     # 
    ######  ### ####### #     # #######  #####   #####     ####### #######  #####  ###  #####  
    #########################################################################

    #https://www.journaldev.com/23365/python-string-to-datetime-strptime

    def calc_futureCoupon(self, ticker, debugFlag):
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        errorFlag = 0
        errorMsg = ''
        lastClosePrice = self.getLastClosePrice(ticker)
        if 'None' in str(lastClosePrice):
            print(f'Price not found for : {ticker}')
            errorFlag += 1
            errorMsg += f'Price not found for {ticker}\n'
        else:
            lastAfterTaxBasicEPS = self.getLastBasicEarningsPerShare(ticker)
            lastEffectiveTaxRate = self.getLastEffectiveTaxRate(ticker)
            if 'nan' in str(lastEffectiveTaxRate):
                lastEffectiveTaxRate = 0
            try:
                if '-' in str(lastAfterTaxBasicEPS):
                    lastAfterTaxBasicEPS = str(lastAfterTaxBasicEPS).strip('-')
                    if lastEffectiveTaxRate == 0:
                        lastBeforeTaxBasicEPS = -(float(lastAfterTaxBasicEPS))
                        # if debugFlag ==True:
                        #     print(f'lastBeforeTaxBasicEPS = -(float({lastAfterTaxBasicEPS}))')
                    else:
                        lastBeforeTaxBasicEPS = -(float(lastAfterTaxBasicEPS) / (1 - (lastEffectiveTaxRate/100)))
                else:
                    if lastEffectiveTaxRate == 0:
                        lastBeforeTaxBasicEPS = float(lastAfterTaxBasicEPS)
                    else:
                        lastBeforeTaxBasicEPS = float(lastAfterTaxBasicEPS) / (1 - (lastEffectiveTaxRate/100))
                # if debugFlag == True:
                    # print(f'Last Effective Tax Rate: {lastEffectiveTaxRate}\n')
                    # print(f'Last After Tax Basic EPS: {lastAfterTaxBasicEPS}\n')
            except:
                errorFlag += 1
                errorMsg += 'Error in last effective tax rate and last before tax EPS eq\n'
                # print('error in last before tax EPS eq')
                # if debugFlag == True:
                #     print(f'Last Effective Tax Rate: {lastEffectiveTaxRate}\n')
                #     print(f'Last After Tax Basic EPS: {lastAfterTaxBasicEPS}\n')
                #     print(f'Last Before Tax Basic EPS: {lastBeforeTaxBasicEPS}\n')



            # print(lastBeforeTaxBasicEPS)

            lastDivPerShare = self.getLastDividendPerShare(ticker)
            # if debugFlag == True:
            #     print(lastDivPerShare)
            try:
                lastDivYieldEquationString = f'({lastDivPerShare}/{lastClosePrice})*100'
            except:
                errorFlag += 1
                errorMsg += 'Last Div Yield eq error\n'
                # if debugFlag == True:
                #     print(f'Dividend Yield Equation: {lastDivYieldEquationString}')

            try:
                lastDivYield = (lastDivPerShare/lastClosePrice)*100
            except:
                lastDivYield = 0
                errorFlag += 1
                errorMsg += 'Error in Div Yield computation\n'
                # print('error in div yield eq')

            # if debugFlag == True:
            #     print(f'Last Div Yield: {lastDivYield}')

            try:
                couponEquationString = f'({lastBeforeTaxBasicEPS} / {lastClosePrice})*100) + {lastDivYield}'
            except:
                errorFlag += 1
                errorMsg += 'Coupon Eq error\n'

            # if debugFlag == True:
            #     print(f'Coupon Equation String: {couponEquationString}')

            # print(f'Coupon Equation: {couponEquationString}')
            try:
                coupon = round(((lastBeforeTaxBasicEPS / lastClosePrice)*100) + lastDivYield, 2)
            except:
                coupon = 0
                errorFlag += 1
                errorMsg += 'Coupon computation error\n'
                # print('error in coupon eq')

            firstAfterTaxBasicEPS = self.getFirstBasicEarningsPerShare(ticker)
            firstEffectiveTaxRate = self.getFirstEffectiveTaxRate(ticker)
            # print(f'First After-Tax Basic EPS: {firstAfterTaxBasicEPS}')

            try:
                if '-' in str(firstAfterTaxBasicEPS):
                    # print('yes')
                    # print(firstAfterTaxBasicEPS)
                    firstAfterTaxBasicEPS = str(firstAfterTaxBasicEPS).strip('-')
                    if firstEffectiveTaxRate == 0:
                        firstBeforeTaxBasicEPS = -(float(firstAfterTaxBasicEPS))
                    else:
                        firstBeforeTaxBasicEPS = -(float(firstAfterTaxBasicEPS) / (1 - (float(firstEffectiveTaxRate)/100)))
                else:
                    if firstEffectiveTaxRate == 0:
                        firstBeforeTaxBasicEPS = float(firstAfterTaxBasicEPS)
                    else:
                        firstBeforeTaxBasicEPS = float(firstAfterTaxBasicEPS) / (1 - (firstEffectiveTaxRate/100))
            except:
                errorFlag += 1
                errorMsg += 'Error in first effective tax rate and first before tax EPS eq\n'
                # print('error in first before tax EPS eq')

            numberOfDatesForTicker = self.getAnnualIncomeStatementDateRange(ticker)
            numberOfPeriods = float(numberOfDatesForTicker) - 1

            try:
                growthCalculationString = f'(({lastBeforeTaxBasicEPS}/{firstBeforeTaxBasicEPS})^(1/{numberOfPeriods})-1)*100'
                growth = round(((float(lastBeforeTaxBasicEPS)/float(firstBeforeTaxBasicEPS))**(1/numberOfPeriods)-1)*100, 2) # https://www.wikihow.com/Calculate-an-Annual-Percentage-Growth-Rate

                futureCoupon5yr = ''
                futureCoupon10yr = ''
                futureCoupon15yr = ''
                futureCoupon20yr = ''
                for i in range(1,21):
                    #next - last known eps + last known eps * growth
                    projectedEPS = lastBeforeTaxBasicEPS + (lastBeforeTaxBasicEPS*((growth/100)))
                    futureCoupon = (lastBeforeTaxBasicEPS + (lastBeforeTaxBasicEPS*((growth/100)))) / (lastClosePrice)
                    # print(f'in {i} year(s): ${projectedEPS[0]}\t {futureCoupon[0]*100}%')
                    lastBeforeTaxBasicEPS = projectedEPS
                    if i == 5:
                        futureCoupon5yr = round(futureCoupon*100, 2)
                    if i == 10:
                        futureCoupon10yr = round(futureCoupon*100 ,2)
                    if i == 15:
                        futureCoupon15yr = round(futureCoupon*100, 2)
                    if i == 20:
                        futureCoupon20yr = round(futureCoupon*100, 2)
            except:
                growth = 0
                errorFlag += 1
                errorMsg += 'Error in Growth Eq\n'
                # print('error in growth eq')

            totalCash = self.getAnnualLatestTotalCash(ticker)
            if 'None' in str(totalCash):
                totalCash = 0
                # print("found none cash")
            totalAssets = self.getAnnualLatestTotalAssets(ticker)
            totalLiabilities = self.getAnnualLatestTotalLiabilities(ticker)

            if 'None' in str(totalAssets) or 'None' in str(totalLiabilities):
                currentRatio = 0
            else:
               currentRatio = float(totalAssets)/float(totalLiabilities)
            #TODO: consistency printing out percentages and dollar amounts and displaying in screen output
            if debugFlag == True:
                try:
                    print(f'    Coupon: {coupon}%\n    Growth: {growth}%\n    Cash: ${totalCash}\n    Current Ratio: {currentRatio}%\n')
                    prettyTable = PrettyTable(["Ticker", "Last Close Price", 'Last After Tax EPS', 'Last Tax Rate', 'Last Before-Tax EPS', 'Last DivYield', 'coupon', 'First Before-Tax EPS', 'Growth', 'In 5yrs', 'In 10yrs', 'In 15yrs', 'In 20yrs' ])
                    prettyTable.add_row([f'{ticker}',f'${lastClosePrice}',f'{round(lastAfterTaxBasicEPS,2)}',f'{round(lastEffectiveTaxRate,2)}',f'{round(lastBeforeTaxBasicEPS,2)}', f'{round(lastDivYield,2)}%', f'{round(coupon,2)}%', f'{round(firstBeforeTaxBasicEPS,2)}', f'{round(growth,2)}%', futureCoupon5yr, futureCoupon10yr, futureCoupon15yr, futureCoupon20yr])
                    print(prettyTable)
                    print(f'Dividend Equation: {lastDivYieldEquationString} == (lastDivPerShare/lastClosePrice)*100')
                    print(f'Coupon Equation: {couponEquationString} == (lastBeforeTaxBasicEPS / lastClosePrice)*100) + lastDivYield')
                    print(f'Growth Equation: {growthCalculationString} == ((lastBeforeTaxBasicEPS/firstBeforeTaxBasicEPS)^(1/numberOfPeriods)-1)*100')
                    print(f'Total Cash: {totalCash}')
                    print(f'Current Ratio: {currentRatio}')
                    print(f'{ticker},,,{round(lastDivYield,2)},{round(coupon,2)},{round(growth,2)},{totalCash},{currentRatio},{futureCoupon5yr},{futureCoupon10yr},{futureCoupon15yr},{futureCoupon20yr}\n')
                except:
                    errorFlag += 1
                    errorMsg += 'Error printing debug info\n'
                    # print("debug output")
            else:
                print(f'{ticker}:\n    Coupon: {coupon}%\n    Growth: {growth}%\n    Cash: ${totalCash}\n    Current Ratio: {currentRatio}%\n')




            try:
                # print(f'Printing Excel...')
                # print(f'''{ticker},,,{divYield},{coupon},{totalCash},{currentRatio}\n''')
                with open('excel/seekingAlphaLog.csv', 'a') as f: #TODO: update output: symbol,,,DivYield, Coupon, Growth, Cash, Current Ratio
                    f.write(f'''{ticker},,,{lastDivYield},{coupon},{growth},{totalCash},{currentRatio}\n''')
                    # pass

                # print(f'{ticker}:\n  Coupon: {round(coupon,2)}%\t\n  Growth: {round(growth,2)}%\t\n    Cash: ${totalCash}\t\n    CR: {currentRatio}\n')
                with open('screenOutputLog.txt', 'a') as f:
                    f.write(f'{ticker}:\n  Coupon: {round(coupon,2)}%\t\n  Growth: {round(growth,2)}%\t\n   Cash: ${totalCash}\t\n    CR: {currentRatio}\n')
            except:
                errorFlag += 1
                errorMsg += 'Error in logging to file\n'
                print('log output')

        if errorFlag > 0:
            # print(f'**{ticker}**error {errorFlag}')
            # totalErrorCount += 1
            with open('err/errorLog.txt', 'a') as f:
                f.write(f'**{ticker}**error {errorFlag}\n{errorMsg}')
        else:
            try:
                futureCouponDataInsertQuery = f'INSERT INTO study_futureCoupon (companyTicker, coupon, growth, sampleDate) VALUES("{ticker}", {coupon}, {growth}, "{datetime.datetime.now()}")'       
                cursor.execute(futureCouponDataInsertQuery)
                sqliteConnection.commit()
                # totalSuccessCount += 1
            except:
                # totalErrorCount += 1
                errorFlag += 1
                errorMsg += 'Error inserting to study_futureCoupon'   
                # print(errorMsg)
        cursor.close()
        sqliteConnection.close()
        return #prettyTable

    def calculateProjectedROI(self, ticker):
        sqliteConnection = sqlite3.connect('seekingAlpha.db')
        cursor = sqliteConnection.cursor()
        companyLastClosePriceQuery = f'select close from priceAction where companyTicker = "{ticker}";' 
        companyBasicEarningsPerShareQuery = f'select rawvalue,date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual";'
        netIncomeQuery = f'select rawvalue,date from incomeStatements where companyTicker = "{ticker}" and lineItemName = "Net Income" and timeScale = "annual";'
        effectiveTaxRateQuery = f'select rawvalue, date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Effective Tax Rate" and timeScale = "annual";'
        price = pd.read_sql(companyLastClosePriceQuery, sqliteConnection)
        print(f'Price: {price}')
        # basicEarningsPerShare = pd.read_sql(companyBasicEarningsPerShareQuery, sqliteConnection)
        # print(basicEarningsPerShare)
        # divPerShare = pd.read_sql(divPerShareQuery, sqliteConnection)
        # print(divPerShare)
        # couponRate_df = pd.DataFrame(columns=['date','basicEPS', 'divPerShare', 'couponRate'])
        # temp_df = pd.merge(basicEarningsPerShare, divPerShare, on='date')
        # print(temp_df)
        # for row in temp_df['rawValue_x']:
        #     temp_df['rawValue_x'][row] = format(temp_df['rawValue_x'][row], 'f') 
        # temp_df['rawValue_x'] = (temp_df['rawValue_x'] != '').astype(float)
        # temp_df['rawValue_y'] = (temp_df['rawValue_y'] != '').astype(float)

        #for value in temp_df['rawValue_x']: print(float(value))
        # for value in temp_df['rawValue_y']: temp_df['rawValue_y'] = float(value)
        taxRateQuery = f'select rawValue as taxRate,MAX(date) as date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Effective Tax Rate" and timeScale = "annual";'
        taxRate_df = pd.read_sql(taxRateQuery, sqliteConnection)
        epsQuery = f'select rawValue as eps,MAX(date) as date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual";'
        eps_df = pd.read_sql(epsQuery, sqliteConnection)
        # print(f'final after tax EPS {eps_df["eps"]}')
        # netIncomeQuery = f'select rawvalue as netIncome,MAX(date) as date from incomeStatements where companyTicker = "{ticker}" and lineItemName = "Net Income" and timeScale = "annual"'
        # netIncome_df = pd.read_sql(netIncomeQuery, sqliteConnection)
        divPerShareQuery = f'select MAX(distinct(date)), rawvalue as divPerShare from incomeStatements where lineitemname = "Dividend Per Share" and companyTicker = "{ticker}" and timeScale = "annual" and date like "Dec%"'
        divPerShare_df = pd.read_sql(divPerShareQuery,sqliteConnection)
        # print(f'Div per share: {divPerShare_df["divPerShare"][9]}')
        divYield = (divPerShare_df['divPerShare']/price['close'])*100
        # print(f'divYield: {divYield[0]}')
        # print(f'Final Tax Rate: {taxRate_df["taxRate"]}')
        #After tax / 1 - effective tax rate
        # preTaxEPS = eps_df['eps'] + (eps_df['eps']*(taxRate_df['taxRate']/100))
        preTaxEPS = (eps_df['eps'])/(1-(taxRate_df['taxRate']/100))
        print(f'preTaxEPS: {preTaxEPS}')
        # print(f'PreTax EPS: {eps_df['eps']} + ({eps_df['eps']}*({taxRate_df['taxRate']}/100))')
        print(eps_df['eps'])
        print(taxRate_df['taxRate'])
        # print(preTaxEPS)
        # print(price['close'])

        # EXR pays 3.93% a year on  $91.6 => $3.59 / share
        # 
        divPerShareVar = '' # In the case that the company does not pay
        if divPerShare_df["divPerShare"][0] == 'None':
            divPerShareVar = 0
        else:
            divPerShareVar = divPerShare_df["divPerShare"][0]
        print(f'coupon = ({preTaxEPS[0]}/{price["close"][0]})*100 + ({divPerShareVar}/{price["close"][0]})*100')
        coupon = ((preTaxEPS[0]/price['close'][0])*100)+divYield # add divYield and print equation explanation
        print(f'coupon = {coupon[0]}%')

        epsRateQuery = f'select distinct(date), rawValue as eps from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual" order by date DESC;'
        epsRate_df = pd.read_sql(epsRateQuery, sqliteConnection)
        # print(epsRate_df)
        epsRate_df = epsRate_df[0:10]
        # epsRate_df['preTaxEPS'] = epsRate_df.apply(epsRate_df['eps'])
        # print(epsRate_df)
        # finalEPS = epsRate_df['eps'][0]
        finalEPS_query = f'select MAX(date), rawValue as eps from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual" and date like "Dec%";'
        #finalEPS_df = pd.read_sql(finalEPS_query,sqliteConnection)
        finalEPS = preTaxEPS
        #startEPS = epsRate_df['eps'][9]
        startEPS_query = f'select MIN(date), rawValue as eps from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual" and date like "Dec%";'
        startEPS_df = pd.read_sql(startEPS_query,sqliteConnection)
        startTaxRateQuery = f'select rawValue as taxRate,MIN(date) as date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Effective Tax Rate" and timeScale = "annual" and date like "Dec%";'
        startTaxRate_df = pd.read_sql(startTaxRateQuery, sqliteConnection)
        # print(f'Starting Tax Rate: {startTaxRate_df["taxRate"]}')
        print(f'initial after tax EPS: {startEPS_df["eps"]}')
        # startEPS = startEPS_df['eps'] + (startEPS_df['eps']*(startTaxRate_df['taxRate']/100))
        startEPS = (startEPS_df['eps']/(1-(startTaxRate_df['taxRate']/100) ))
        # print(f'start pre-tax EPS: {startEPS}')

        # print(f'growth = (({finalEPS[0]}/{startEPS[0]}^(1/10-1)*100')
        growth = ((finalEPS/startEPS)**(1/9)-1)*100
        # print(f'growth = {growth[0]}%')

        projectedPrice = price['close'][0]
        projectedEPS = projectedPrice * (coupon/100)

        futureCoupon5yr = ''
        futureCoupon10yr = ''
        futureCoupon15yr = ''
        futureCoupon20yr = ''
        for i in range(1,21):
            #next - last known eps + last known eps * growth
            projectedEPS = finalEPS + (finalEPS*((growth/100)))
            futureCoupon = (finalEPS + (finalEPS*((growth/100)))) / (price['close'][0])
            # print(f'in {i} year(s): ${projectedEPS[0]}\t {futureCoupon[0]*100}%')
            finalEPS = projectedEPS
            if i == 5:
                futureCoupon5yr = round(futureCoupon[0]*100, 2)
            if i == 10:
                futureCoupon10yr = round(futureCoupon[0]*100 ,2)
            if i == 15:
                futureCoupon15yr = round(futureCoupon[0]*100, 2)
            if i == 20:
                futureCoupon20yr = round(futureCoupon[0]*100, 2)


        print(f'{ticker},,,,,,{round(coupon[0],2)},{round(growth[0],2)},{futureCoupon5yr},{futureCoupon10yr},{futureCoupon15yr},{futureCoupon20yr}')


        # epsRate_df['annualGrowth'] = np.rate()
        # coupon = Latest EPS/Price + divYield; divYield = divPerShare/Price
        #numpy.rate() #TODO: https://www.geeksforgeeks.org/numpy-rate-in-python/
        # temp_df['couponRate'] = temp_df.apply(lambda row: (float(row.rawValue_x)/float(price['close'])) + (float(row.rawValue_y)/float(price['close'])), axis=1)
        # EPS pre-tax = Basic EPS +(basic EPS * effective tax rate) ,last year EPS Pre-tax / stock price to get relevant coupon rate, then add div yield
        # EPS growth % = annual rate of change of EPS pre-tax
        # print(temp_df)

        cursor.close()
        sqliteConnection.close()
        return

    def mineSecFilingsData(self, ticker):
        headers = { 
            'Referer': f'https://seekingalpha.com/symbol/{ticker}/balance-sheet',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
        }
        databaseName = self.getDatabaseName()
        sqliteConnection = sqlite3.connect(databaseName)
        cursor = sqliteConnection.cursor()
        filingPDFQuery = f'''SELECT filingID, filingFormName, filingPDF from secFilings WHERE companyTicker = '{ticker}' AND filingFormName LIKE 'SC 13D%'; '''
        filingPDFLink = pd.read_sql_query(filingPDFQuery, sqliteConnection)
        print(filingPDFLink['filingPDF'][0])
        #fileName = f'''{ticker}_{filingFormName['filingFormName'][0]}_{filingFormName['filingID'][0]}.pdf '''
        res = requests.get(url=filingPDFLink['filingPDF'][0], headers=headers)
        with open(f'{ticker}_{filingPDFLink["filingFormName"][0]}_{filingPDFLink["filingID"][0]}.pdf', 'wb') as f:
            f.write(res.content)
        
        print(ticker)
        tables = camelot.read_pdf(f'{ticker}_{filingPDFLink["filingFormName"][0]}_{filingPDFLink["filingID"][0]}.pdf', pages="3-end", flavor='lattice')
        for t in tables:
            # print(t.parsing_report)
            t_df = t.df
            #pd.set_option('display.max_rows', len(t_df))
            sharesBeneficiallyOwned = t_df[1][10]
            classRepresentationPercent = t_df[1][12]
            print(sharesBeneficiallyOwned)
            print(classRepresentationPercent)

        tables2 = camelot.read_pdf(f'{ticker}_{filingPDFLink["filingFormName"][0]}_{filingPDFLink["filingID"][0]}.pdf', pages="all", flavor='stream')
        for t in tables2:
            # print(t.parsing_report)
            t_df = t.df
            # print(t_df)
            try:
                print(t_df[0][16])
                print(t_df[0][17])
            except:
                pass

        
        cursor.close()
        sqliteConnection.close()
        return
    
    def gsheets_companyRevenue(self,ticker):
        # https://github.com/nithinmurali/pygsheets
        # link to ProfitHawk GSheets project: https://docs.google.com/spreadsheets/d/1YF3RnTjXGeLtoyG4z78bUirf3qPskkJKY9SQ8GPqTQo/edit?usp=sharing (must be added to project to link to work)
        # query = f'''select * from incomeStatements where companyTicker = '{ticker}' and lineitemsectiongroup = 'revenue'; '''
        gc = pygsheets.authorize() # must have client_secret.json from console.google.com
        sh = gc.open('ProfitHawk')
        wks = sh.sheet1

        wks.update_value('B5', f"{ticker}")
        b2 = wks.cell('B2')
        b2.formula = '=SPARKLINE(GOOGLEFINANCE(B5,"price",TODAY()-B4,TODAY(),"daily"),{"charttype","line";"linewidth",2;"color","#5f88cc"})'
        # my_nparray = np.random.randint(10, size=(3, 4))

        # update the sheet with array
        #wks.update_values('A2', my_nparray.tolist())


        return

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################


######  #     # #     #    ####### ### #     # ####### 
#     # #     # ##    #       #     #  ##   ## #       
#     # #     # # #   #       #     #  # # # # #       
######  #     # #  #  #       #     #  #  #  # #####   
#   #   #     # #   # #       #     #  #     # #       
#    #  #     # #    ##       #     #  #     # #       
#     #  #####  #     #       #    ### #     # ####### 

def executeTickerList(minerObj, tickerList, debugBool):
    for ticker in tickerList:
        # minerObj.getIncomeStatementData(ticker)
        # minerObj.getBalanceSheetData(ticker)
        # minerObj.getCashFlowData(ticker)
        # minerObj.getPriceActionData(ticker)
        # minerObj.getCompanyOverviewData(ticker)
        # minerObj.getOptionsData(ticker)
        # minerObj.calc_futureCoupon(ticker, debugFlag=debugBool)
        minerObj.getStatementOfBeneficialOwnershipSEC(ticker)

    return

def readFromTextFile(minerObj, fileList, debugBool):
    if len(sys.argv) == []: # TODO: with command line arguments, this condition is no longer needed
        for file in ['symbols_nyse.txt', 'symbols_nasdaq.txt', 'symbols_amex.txt']:
            tickerList = []
            tickerStr = ''
            with open(file, 'r') as f:
                for item in f:
                    # print(item.split())
                    tickerList = item.split()
            #print(tickerList)
            for ticker in tickerList:
                if '$' in ticker or '^' in ticker or '~' in ticker:
                    print(ticker)
                else:
                    # print(ticker)
                    # minerObj.getBalanceSheetData(ticker)
                    # minerObj.getCashFlowData(ticker)
                    # minerObj.getIncomeStatementData(ticker)
                    # minerObj.getPriceActionData(ticker)
                    # minerObj.calc_futureCoupon(ticker, debugFlag=debugBool)
                    minerObj.getStatementOfBeneficialOwnershipSEC(ticker)
    else:
        fileCounter = 1
        for file in fileList:
            tickerList = []
            tickerStr = ''
            counter = 1
            with open(file, 'r') as f:
                for item in f:
                    # print(item.split())
                    tickerList = item.split()
            #print(tickerList)
            for ticker in tickerList:
                if '$' in ticker or '^' in ticker or '~' in ticker:
                    print(ticker)
                else:
                    print(f'{ticker}\t\t\tFile: {fileCounter} [{counter}/{len(tickerList)}]')
                    # minerObj.getBalanceSheetData(ticker)
                    # minerObj.getCashFlowData(ticker)
                    # minerObj.getIncomeStatementData(ticker)
                    # minerObj.getPriceActionData(ticker)
                    # minerObj.getCompanyOverviewData(ticker)
                    # minerObj.calc_futureCoupon(ticker, debugFlag=debugBool)
                    minerObj.getOptionsData(ticker)
                    minerObj.getStatementOfBeneficialOwnershipSEC(ticker)

                    counter += 1
            
            fileCounter += 1

def readFromCSV():
    tickerList_df = pd.read_csv('NYSE.csv', sep=',')
    #print(tickerList_df['Symbol'])
    for ticker in tickerList_df['Symbol']:
        if '$' in ticker or '^' in ticker or '~' in ticker:
            print(ticker)
        else:
            # print(ticker)
            getIncomeStatementData(ticker)
            getPriceActionData(ticker)
            calc_futureCoupon(ticker)
    return

def executeWorkaround(minerObj):
    #minerObj.gsheets_companyRevenue('SCHW')
    minerObj.getOptionsData('SCHW')
    print('Workaround done.')
    return

def findFilingsSEC(minerObj):
    minerObj.ifNotExistsCreateDB()
    #minerObj.getStatementOfBeneficialOwnershipSEC('SCON')
    minerObj.mineSecFilingsData('SCON')
    return

# @click.group()
# @click.pass_context()
def main(minerObj):
    # parser = argparse.ArgumentParser(description=f'{log("Profit Hawk", color="red", figlet=True)}')
    parser = argparse.ArgumentParser(description=f'SA Miner CLI')
    
    
    tickerList = []; fileList = ''; debugFlag = ''; # TODO: What is metavar property used for in argparse?
    parser.add_argument('-d', '--debug',action='store_true', help='Signal True Dubug Flag for detailed output and logging')
    parser.add_argument('-t', '--ticker',action='store',type=str,metavar=tickerList, nargs='+', help='Provide 1 to * space delimited tickers') # + indicates 1 to many arguments; https://stackoverflow.com/questions/20165843/argparse-how-to-handle-variable-number-of-arguments-nargs
    #parser.add_argument('-f', '--file', type=str, nargs=1, metavar=fileList, default=None,help='Provide 1 to * space delimited filenames with tickers')
    parser.add_argument('-f', '--file',action='store',type=str,nargs='+', help='Provide 1 to * space delimited files, containing space delimited tickers')
    #parser.add_argument('-d', '--debug', type=str, nargs=1, metavar=debugFlag, default=True, help='Signal to print debug detail info to screen and logfile')
    parser.add_argument('-o', '--options', action='store_true', help='')
    parser.add_argument('-w', '--workaround', action='store_true', help='')
    parser.add_argument('-u', '--update', action='store_true', help='')
    parser.add_argument('-s', '--sec', action='store_true', help='')


    args = parser.parse_args()

    debugBool = False
    if args.debug:
        # print('debug')
        debugBool = True
    
    if args.file:
        # print('file')
        readFromTextFile(minerObj, args.file, debugBool)
    elif args.ticker:
        # print('ticker')
        executeTickerList(minerObj, args.ticker, debugBool)
    elif args.sec:
        findFilingsSEC(minerObj)
    elif args.workaround:
        executeWorkaround(minerObj)
    else:
        print('Nothing')

    


    return

# @main.command()
# @click.pass_context()
# def loadDatabase(ctx):
#     print("I'm a beautiful CLI ✨")
#     return



#TODO: https://codeburst.io/building-beautiful-command-line-interfaces-with-python-26c7e1bb54df
if __name__ == '__main__':   
    #log("Profit Hawk", color="red", figlet=True)
    #deleteDatabase()
    #TODO: Class together all API miner commands, so flask server can keep database updated without doing a complete pull every time
    sam1 = seekingAlphaMiner()
    sam1.rotateLog()
    sam1.ifNotExistsCreateDB()
    # rotateLog()
    # ifNotExistsCreateDB()
    
    
    # #readFromCommandLine()
    # #readFromCSV()
    # readFromTextFile(debugBool=True)
    #calculateProjectedROI('AB')

    main(sam1)
    # print(f'Tickers successfully processed: {totalSuccessCount}')
    # print(f'Tickers exited with error: {totalErrorCount}')
            
        
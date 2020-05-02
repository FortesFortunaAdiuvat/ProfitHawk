import sqlite3, requests, datetime, re, json, argparse, os, sys, six
import pandas as pd
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
 
style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})

#################################################
#    #####  ####### #######    #     # ######   #
#   #     # #          #       #     # #     #  #
#   #       #          #       #     # #     #  #
#    #####  #####      #       #     # ######   #
#         # #          #       #     # #        #
#   #     # #          #       #     # #        #
#    #####  #######    #        #####  #        #
#################################################
def deleteDatabase():
    databaseName = getDatabaseName()
    if os.path.exists(databaseName):
        os.remove(databaseName)
    return

def rotateLog():
    if os.path.exists('excel/seekingAlphaLog.csv'):
        os.rename('excel/seekingAlphaLog.csv', f'excel/seekingAlphaLog_{datetime.datetime.now()}.csv')
    return

def ifNotExistsCreateDB():
    databaseName = getDatabaseName()
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
        rowid INTEGER PRIMARY KEY, companyTicker TEXT, coupon INTEGER, growth INTEGER, sampleDate datetime
    ); '''
    cursor.execute(createBalanceSheetsTable)
    cursor.execute(createCashFlowsTable)
    cursor.execute(createIncomeStatementsTable)
    cursor.execute(createRealTimePricesTable)
    cursor.execute(createStudyFutureCouponTable)

    sqliteConnection.commit()
    sqliteConnection.close()

    return

def getSeekingAlphaProCookie():
    if os.path.exists('seekingAlphaProCookie.txt'):
        with open('seekingAlphaProCookie.txt', 'r') as f:
            seekingAlphaProCookie = f.readline()
        # print(seekingAlphaProCookie)
    else:
        seekingAlphaProCookie = ''
    return seekingAlphaProCookie

def getRequestHeaders(ticker):
    seekingAlphaProCookie = getSeekingAlphaProCookie()
    headers = { # Necessary or else requests are 403 Forbidden 
        'Referer': f'https://seekingalpha.com/symbol/{ticker}/balance-sheet',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
        'cookie': f'{seekingAlphaProCookie}'
        #'cookie': 'machine_cookie=4731953277079; _gcl_au=1.1.1199554884.1584215784; _pxvid=e2354d36-662d-11ea-b255-0242ac12000c; h_px=1; portfolio_sort_type=a_z; has_paid_subscription=true; ever_pro=1; user_id=51399747; user_nick=; user_devices=1; u_voc=209; marketplace_author_slugs=; user_perm=; sapu=12; user_remember_token=b663c1290b28648465ba3a9318b2ba5e8c9035fc; user_cookie_key=vhepn; _igt=3eff2345-50a2-4b60-a8c4-39cd61c4c355; _ig=9df61b54-419a-4482-cdc5-03229a410f9c; _ga=GA1.2.2136682556.1587757982; _gid=GA1.2.584912144.1587757982; ga_clientid=2136682556.1587757982; __pnahc=0; __tbc=%7Bjzx%7DlCp-P5kTOqotpgFeypItnKS3A44UHT9sb1IJ3lxi9-tdsGRLenQpOSERaaj8bTeUNfdIs_-76qPyuNAwJKCo47DY3s-wYK4D6WUV902MnXUHRK2A0IQ6GtabSFotCECnUVgFAp6l8Mpn6PJS7yCpyA; __pat=-14400000; __pvi=%7B%22id%22%3A%22v-2020-04-24-13-53-04-540-XMRlyuZeOafKa7bz-bcf2d031d41cb6b433743ba653047c89%22%2C%22domain%22%3A%22.seekingalpha.com%22%2C%22time%22%3A1587757987298%7D; xbc=%7Bjzx%7DvCGphVlY9G4xxbXMbU8IuTNHJT8Yqbk_90HouEauVQaYv8bfeCicutcYPlBHwdzy1ZubkHNyv6fLEAD6-vDWEoAg9zPeinc0DHqVA8piSbx4R-DLnTT5L3pBjNj5xQKkYi-Jf5mLolR2HyrLdfZkSV3Ytksz2sJ95qmuyU4zL9PkrBZxm_xYO9jUpIbQyW2f_AIz6V5o4jfaAvpwM2_Yiv7eCg92K16Z4rOuGrbH9bNLMAJ0FFexg1wu-Mkhj1AoTG8hAhNgJGQp7GSaonPHI8AIFVrGkvP41Ki_RUI2ZI4AG_FThVhuJP0IL71oUyMF0SnHBlGobcIZ5e7MEvgRRffWX98O0pYApIiqxmqtQXdS6Zg77YBXUbQ6ipG9T64BY55zeAhJ8O0UVdNJJKec8PAm6GzbDAptjt-JnZJfx50; _pxff_axt=540; _pxff_wa=1,702; __adblocker=true; _px2=eyJ1IjoiZjljYjc3MDAtODY3OC0xMWVhLTg5OTItZWQwZjgwNzZhMzU0IiwidiI6ImUyMzU0ZDM2LTY2MmQtMTFlYS1iMjU1LTAyNDJhYzEyMDAwYyIsInQiOjE1ODc3NjY5NzMzNjIsImgiOiI0MzAwNmU0ZGFiZDA5Yzc3NWZlZjgxZmI1N2U4ZGE0ODYxMjBlZTc1MjkzNzQ4MzAyNTZhZDJhYzlkYjczZDI2In0=; _px=1UFk9dAcIQDjrYO2j89NyN584WxgNLDjvaT8/P0q9/xUzwEJkHlGaMhWqmkn6cea+RBEggbqLx6+y+NYK0B92w==:1000:Ok0hU+SBeflq6QESBQeZGfaK1WWmMyTqv8KuDNQIf8ivAQEFXfO7LptURzbEsnPbE+g77f1lHUckIGKHu6LaWa8t7OhjE38HxSJd+qEmDn4wZU3gRgziEWCLLVSq7sxcYKXj0uMOgpicXT5f5A/+s6Q7DQuZRDX00ftllKw6Ne0zdIYEv75z3TS0VelWOPCDsuJM1rfhn60UvBbw6nEbLKcRAeW7k4eyP4z9CeVi7IIBe0SjW//KSW9mwWTw12IvigKq1OHZO7mWg679nD/Y8w==; _pxde=ca77bdecb75957e177e3bf4c87ca8c1d5e2c32ef6b70926ffb9698baace9a54f:eyJ0aW1lc3RhbXAiOjE1ODc3NjY0OTE5NzIsImZfa2IiOjAsImZfdHlwZSI6InciLCJmX2lkIjoiMjE0NTMyNGYtZjRmZC00MGUyLTljZWQtMzJmZTdkMmU2MWJjIiwiZl9vcmlnaW4iOiJjdXN0b20ifQ==; gk_user_access=1*archived*1587766496; gk_user_access_sign=bd71b99f8e0161e0eae23c03a3ba0c446bcbdb82'
    }

    return headers

def getDatabaseName():
    databaseName = 'seekingAlpha_20200501.db'
    return databaseName

def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(
                string, font=font), color))
    else:
        six.print_(string)



########################################################################
#      #    ######  ###    #     # ### #     # ####### ######   #####   #
#     # #   #     #  #     ##   ##  #  ##    # #       #     # #     #  #
#    #   #  #     #  #     # # # #  #  # #   # #       #     # #        #
#   #     # ######   #     #  #  #  #  #  #  # #####   ######   #####   #
#   ####### #        #     #     #  #  #   # # #       #   #         #  #
#   #     # #        #     #     #  #  #    ## #       #    #  #     #  #
#   #     # #       ###    #     # ### #     # ####### #     #  #####   #
########################################################################
def getBalanceSheetData(ticker):
    headers = getRequestHeaders(ticker)
    databaseName = getDatabaseName()
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
        for datum in companyAnnualBalanceSheet['data']: # there is one list of objects per line item, # TODO: cutting off final list item, Supplimental Info is a different data model
            for item in datum:
                for cell in item:
                    if cell['class'].startswith('left-label'):
                        lineItemName = cell['value']
                        lineItemDesc = cell['name']
                        lineItemSectionGroup = cell['sectionGroup']
                    if cell['class'].startswith('value'):
                        if 'Last Report' in cell['name'] or 'TTM' in cell['name']:
                            date = datetime.datetime.now()
                        else:
                            date = datetime.datetime.strptime(cell['name'], '%b %Y').strftime('%b %Y') # captures date in 'Dec 2019' format
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
                        insertRecord_SQL = f''' INSERT INTO balanceSheets (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}','annual', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');'''
                        cursor.execute(insertRecord_SQL)
                        sqliteConnection.commit()

    #time.sleep(5)    
    balanceSheetQuarterlyRes = requests.get(url=balanceSheetQuarterlyURL, headers=headers)
    print(balanceSheetQuarterlyRes.status_code)
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
                        if 'Last Report' in cell['name'] or 'TTM' in cell['name']:
                            date = datetime.datetime.now()
                        else:
                            date = datetime.datetime.strptime(cell['name'], '%b %Y').strftime('%b %Y')
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
                        insertRecord_SQL = f''' INSERT INTO balanceSheets (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}','quarterly', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');'''
                        cursor.execute(insertRecord_SQL)
                        sqliteConnection.commit()
    
    cursor.close()
    sqliteConnection.close()
    return

def getCashFlowData(ticker):
    headers = getRequestHeaders(ticker)
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()

    cashFlowAnnualURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=cash-flow-statement&order_type=latest_left&is_pro=True'
    cashFlowQuarterlyURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=cash-flow-statement&order_type=latest_left&is_pro=True'
    cashFlowAnnualRes = requests.get(url=cashFlowAnnualURL, headers=headers)
    print(cashFlowAnnualRes.status_code)
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
                        if 'Last Report' in cell['name'] or 'TTM' in cell['name']:
                            date = datetime.datetime.now()
                        else:
                            date = datetime.datetime.strptime(cell['name'], '%b %Y').strftime('%b %Y')
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
                        insertRecord_SQL = f''' INSERT INTO cashFlows (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue) VALUES ('{ticker}','annual', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}');'''
                        cursor.execute(insertRecord_SQL)
                        sqliteConnection.commit()
    #time.sleep(5)
    cashFlowQuarterlyRes = requests.get(url=cashFlowQuarterlyURL, headers=headers)
    print(cashFlowQuarterlyRes.status_code)
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
                        if 'Last Report' in cell['name'] or 'TTM' in cell['name']:
                            date = datetime.datetime.now()
                        else:
                            date = datetime.datetime.strptime(cell['name'], '%b %Y').strftime('%b %Y')
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
                            elif '-' in cell['yoy_value'] or '' in cell['yoy_value']:
                                yoyValue = np.nan
                            else:
                                yoyValue = float(cell['yoy_value'].strip('%').replace(',',''))
                        else:
                            yoyValue = np.NaN
                        #print(f''' INSERT INTO balanceSheets (companyTicker, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue, percentageOfGroup) VALUES ('{ticker}', '{date}', '{lineItemName}', '{lineItemDesc}', '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}', '{percentageOfGroup}');''')
                        insertRecord_SQL = f''' INSERT INTO cashFlows (companyTicker, timeScale, date, lineItemName, lineItemDesc, lineItemSectionGroup, rawValue, yearOverYearGrowthValue) VALUES ('{ticker}','quarterly', '{date}', '{lineItemName}', "{lineItemDesc}", '{lineItemSectionGroup}', '{rawValue}', '{yoyValue}');'''
                        cursor.execute(insertRecord_SQL)
                        sqliteConnection.commit()

    cursor.close()
    sqliteConnection.close()
    return

def getIncomeStatementData(ticker):
    headers = getRequestHeaders(ticker)
    databaseName = getDatabaseName()
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
                            elif '-' in cell['yoy_value'] or '' in cell['yoy_value']:
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
                                print(percentageOfRevenue)
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
                                rawValue = round(format(-float(cell['raw_value'].strip('()').replace(',','')),'f'),2)
                            elif 'NM' in cell['raw_value'] or '' in cell['raw_value']:
                                rawValue = np.nan
                            else:
                                rawValue = round(format(float(cell['raw_value'].replace(',','')),'f'),2)
                        else:
                            rawValue = np.NaN
                        if 'yoy_value' in cell.keys():
                            if '(' in cell['yoy_value']:
                                yoyValue = -float(cell['yoy_value'].strip('()').strip('%').replace(',',''))
                            elif '-' in cell['yoy_value'] or '' in cell['yoy_value']:
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

def getRatings(ticker):
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

def getPriceActionData(ticker):
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
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    for datum in companyRealTimePriceData['data']:
        # print(datum['attributes']['close'])
        lastClose = datum['attributes']['close']
        low52Week = datum['attributes']['low52Week']
        high52Week = datum['attributes']['high52Week']
        lastCloseDateTime = datum['attributes']['dateTime']
        low = datum['attributes']['low']
        open = datum['attributes']['open']
        high = datum['attributes']['high']
        previousClose = datum['attributes']['previousClose']
        recordInsertQuery = f'INSERT INTO priceAction (companyTicker ,date, open , high , low , close, previousClose, low52Week, high52Week) VALUES ("{ticker}","{lastCloseDateTime}", {open}, {high}, {low}, {lastClose}, {previousClose}, {low52Week}, {high52Week});'
        try:
            cursor.execute(recordInsertQuery)
        except:
            pass
        sqliteConnection.commit()

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
def getLastClosePrice(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    lastClosePriceQuery = f'select close, MAX(date) as date from priceAction where companyTicker = "{ticker}"'
    lastClosePriceData = cursor.execute(lastClosePriceQuery).fetchall()
    lastClosePrice = lastClosePriceData[0][0]
    lastCloseDate = lastClosePriceData[0][1]
    #print(f'Last Close Price: {lastClosePrice}')

    cursor.close()
    sqliteConnection.close()
    return lastClosePrice

def getFirstBasicEarningsPerShare(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    
    firstBasicEPS_query = f'select MIN(date) as date, rawValue as firstBasicEPS from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual";'
    firstBasicEPSData = cursor.execute(firstBasicEPS_query).fetchall()
    firstBasicEPS = firstBasicEPSData[0][1]
    # print(f'first after-tax EPS: {firstBasicEPS}')
    cursor.close()
    sqliteConnection.close()
    return firstBasicEPS

def getLastBasicEarningsPerShare(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    lastBasicEarningsPerShareQuery = f'select rawValue as eps,MAX(date) as date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Basic EPS" and timeScale = "annual";'
    lastBasicEarningsPerShareData = cursor.execute(lastBasicEarningsPerShareQuery).fetchall()
    lastBasicEarningsPerShare = lastBasicEarningsPerShareData[0][0]

    cursor.close()
    sqliteConnection.close()
    return lastBasicEarningsPerShare

def getFirstEffectiveTaxRate(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    
    firstTaxRateQuery = f'select rawValue as firstTaxRate,MIN(date) as date from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Effective Tax Rate" and timeScale = "annual";'
    firstTaxRateData = cursor.execute(firstTaxRateQuery).fetchall()
    
    if 'None' in str(firstTaxRateData[0][0]):
        firstEffectiveTaxRate = 0
    else:
        firstEffectiveTaxRate = firstTaxRateData[0][0]
    
    cursor.close()
    sqliteConnection.close()
    return firstEffectiveTaxRate

def getLastEffectiveTaxRate(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()

    effectiveTaxRateQuery = f'select rawvalue as effectiveTaxRate, MAX(date) from incomeStatements where companyTicker = "{ticker}" and lineitemname = "Effective Tax Rate" and timeScale = "annual";'
    lastEffectiveTaxRateData = cursor.execute(effectiveTaxRateQuery).fetchall()
    
    if 'None' in str(lastEffectiveTaxRateData[0][0]):
        lastEffectiveTaxRate = 0
    else:
        lastEffectiveTaxRate = lastEffectiveTaxRateData[0][0]

    cursor.close()
    sqliteConnection.close()
    return lastEffectiveTaxRate

def getLastDividendPerShare(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    divPerShareQuery = f'select MAX(date), rawvalue as divPerShare from incomeStatements where lineitemname = "Dividend Per Share" and companyTicker = "{ticker}" and timeScale = "annual"; '
    lastDivPerShareData = cursor.execute(divPerShareQuery).fetchall()
    lastDivPerShare = lastDivPerShareData[0][1]
    if lastDivPerShare == None:
        lastDivPerShare = 0

    #print(f'last div per share query result: {lastDivPerShare}')
    #print(f'Last Div Per Share: {lastDivPerShare}')
    cursor.close()
    sqliteConnection.close()
    return lastDivPerShare

def getAnnualIncomeStatementDateRange(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    
    countDistinctAnnualTimeScaleDates = f'select count(distinct(date)) from incomeStatements where companyTicker = "{ticker}" and timeScale = "annual";'
    queryData = cursor.execute(countDistinctAnnualTimeScaleDates).fetchall()
    numberOfDates = queryData[0][0]
    
    cursor.close()
    sqliteConnection.close()
    return numberOfDates

#########################################################################
######  ### ####### #     # #######  #####   #####     #       #######  #####  ###  #####  
#     #  #       #  ##    # #       #     # #     #    #       #     # #     #  #  #     # 
#     #  #      #   # #   # #       #       #          #       #     # #        #  #       
######   #     #    #  #  # #####    #####   #####     #       #     # #  ####  #  #       
#     #  #    #     #   # # #             #       #    #       #     # #     #  #  #       
#     #  #   #      #    ## #       #     # #     #    #       #     # #     #  #  #     # 
######  ### ####### #     # #######  #####   #####     ####### #######  #####  ###  #####  
#########################################################################

def calc_futureCoupon(ticker):
    databaseName = getDatabaseName()
    sqliteConnection = sqlite3.connect(databaseName)
    cursor = sqliteConnection.cursor()
    errorFlag = 0
    lastClosePrice = getLastClosePrice(ticker)
    if 'None' in str(lastClosePrice):
        print(f'Price not found for : {ticker}')
    else:
        lastAfterTaxBasicEPS = getLastBasicEarningsPerShare(ticker)
        lastEffectiveTaxRate = getLastEffectiveTaxRate(ticker)
        if 'nan' in str(lastEffectiveTaxRate):
            lastEffectiveTaxRate = 0
        # print(lastEffectiveTaxRate)
        # print(lastAfterTaxBasicEPS)
        try:
            if '-' in str(lastAfterTaxBasicEPS):
                lastAfterTaxBasicEPS = str(lastAfterTaxBasicEPS).strip('-')
                if lastEffectiveTaxRate == 0:
                    lastBeforeTaxBasicEPS = -(float(lastAfterTaxBasicEPS))
                else:
                    lastBeforeTaxBasicEPS = -(float(lastAfterTaxBasicEPS) / (1 - (lastEffectiveTaxRate/100)))
            else:
                if lastEffectiveTaxRate == 0:
                    lastBeforeTaxBasicEPS = float(lastAfterTaxBasicEPS)
                else:
                    lastBeforeTaxBasicEPS = float(lastAfterTaxBasicEPS) / (1 - (lastEffectiveTaxRate/100))
        except:
            errorFlag += 1
        
        # print(lastBeforeTaxBasicEPS)
        
        lastDivPerShare = getLastDividendPerShare(ticker)
        # print(lastDivPerShare)
        try:
            lastDivYieldEquationString = f'({lastDivPerShare}/{lastClosePrice})*100'
        except:
            errorFlag += 1
        # print(f'Dividend Yield Equation: {lastDivYieldEquationString}')
        
        try:
            lastDivYield = (lastDivPerShare/lastClosePrice)*100
        except:
            lastDivYield = 0
            errorFlag += 1

        try:
            couponEquationString = f'({lastBeforeTaxBasicEPS} / {lastClosePrice})*100) + {lastDivYield}'
        except:
            errorFlag += 1
        
        # print(f'Coupon Equation: {couponEquationString}')
        try:
            coupon = round(((lastBeforeTaxBasicEPS / lastClosePrice)*100) + lastDivYield, 2)
        except:
            coupon = 0
            errorFlag += 1

        firstAfterTaxBasicEPS = getFirstBasicEarningsPerShare(ticker)
        firstEffectiveTaxRate = getFirstEffectiveTaxRate(ticker)
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

        numberOfDatesForTicker = getAnnualIncomeStatementDateRange(ticker)
        numberOfPeriods = float(numberOfDatesForTicker) - 1
        
        try:
            growthCalculationString = f'(({lastBeforeTaxBasicEPS}/{firstBeforeTaxBasicEPS})^(1/{numberOfPeriods})-1)*100'
            growth = round(((float(lastBeforeTaxBasicEPS)/float(firstBeforeTaxBasicEPS))**(1/numberOfPeriods)-1)*100, 2) # TODO: need to dynamically calculate period in exponent

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

        #TODO: consistency printing out percentages and dollar amounts and displaying in screen output
        prettyTable = PrettyTable(["Ticker", "Last Close Price", 'Last After Tax EPS', 'Last Tax Rate', 'Last Before-Tax EPS', 'Last DivYield', 'coupon', 'First Before-Tax EPS', 'Growth', 'In 5yrs', 'In 10yrs', 'In 15yrs', 'In 20yrs' ])
        prettyTable.add_row([f'{ticker}',f'${lastClosePrice}',f'{round(lastAfterTaxBasicEPS,2)}',f'{round(lastEffectiveTaxRate,2)}',f'{round(lastBeforeTaxBasicEPS,2)}', f'{round(lastDivYield,2)}%', f'{round(coupon,2)}%', f'{round(firstBeforeTaxBasicEPS,2)}', f'{round(growth,2)}%', futureCoupon5yr, futureCoupon10yr, futureCoupon15yr, futureCoupon20yr])
        print(prettyTable)
        print(couponEquationString)
        print(growthCalculationString)
        #print(f'{ticker},,,,,,{round(coupon,2)},{round(growth,2)},{futureCoupon5yr},{futureCoupon10yr},{futureCoupon15yr},{futureCoupon20yr}')
        try:
            with open('seekingAlphaLog.csv', 'a') as f:
                f.write(f'{ticker},,,,,,{round(coupon,2)},{round(growth,2)},{futureCoupon5yr},{futureCoupon10yr},{futureCoupon15yr},{futureCoupon20yr}\n')

            print(f'{ticker}:\n  Coupon: {round(coupon,2)}%\t\n  Growth: {round(growth,2)}%\t\n')
        except:
            errorFlag += 1

    if errorFlag > 0:
        print(f'**{ticker}**error {errorFlag}')
    else:
        try:
            futureCouponDataInsertQuery = f'INSERT INTO study_futureCoupon (companyTicker, coupon, growth, sampleDate) VALUES("{ticker}", {coupon}, {growth}, "{datetime.datetime.now()}")'       
            cursor.execute(futureCouponDataInsertQuery)
        except:
            pass   
    cursor.close()
    sqliteConnection.close()
    return #prettyTable

def calculateProjectedROI(ticker):
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



# @click.group()
# @click.pass_context()
# def main(ctx):

#     return

# @main.command()
# @click.pass_context()
# def loadDatabase(ctx):
#     print("I'm a beautiful CLI ✨")
#     return


#ifNotExistsCreateDB()
#getCompanyFinancialData('SCHW')
#getRatings('SCHW')
# def start():
#     main(obj={})

if __name__ == '__main__':   
    #print(len(sys.argv))
    ifNotExistsCreateDB()
    def readFromCommandLine():
        for ticker in sys.argv[1:]:
            # print(ticker)
            #getCompanyFinancialData(ticker)
            getIncomeStatementData(ticker)
            getPriceActionData(ticker)
            #calculateProjectedROI(ticker)
            #getLastClosePrice(ticker)
            calc_futureCoupon(ticker)

        return
    
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

    def readFromTextFile():
        for file in sys.argv[1:]:
            tickerList = []
            tickerStr = ''
            with open(file, 'r') as f:
                for item in f:
                    # print(item.split())
                    tickerList = item.split()
            print(tickerList)
            for ticker in tickerList:
                if '$' in ticker or '^' in ticker or '~' in ticker:
                    print(ticker)
                else:
                    # print(ticker)
                    getIncomeStatementData(ticker)
                    getPriceActionData(ticker)
                    calc_futureCoupon(ticker)

    # getRealTimePrices('SCHW')
    #readFromTextFile()
    #getCompanyFinancialData('SCHW')
    # calculateProjectedROI('SCHW')
    #log("Profit Hawk", color="red", figlet=True)
    deleteDatabase()
    rotateLog()
    ifNotExistsCreateDB()
    readFromCommandLine()
    #readFromCSV()
    #readFromTextFile()
    #calculateProjectedROI('AB')

            
        
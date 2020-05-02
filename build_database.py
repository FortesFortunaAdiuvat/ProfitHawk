import os
from datetime import datetime
from config import db
from models import Person, Note

import sqlite3, requests

# Data to initialize database with
PEOPLE = [
    {
        "fname": "Doug",
        "lname": "Farrell",
        "notes": [
            ("Cool, a mini-blogging application!", "2019-01-06 22:17:54"),
            ("This could be useful", "2019-01-08 22:17:54"),
            ("Well, sort of useful", "2019-03-06 22:17:54"),
        ],
    },
    {
        "fname": "Kent",
        "lname": "Brockman",
        "notes": [
            (
                "I'm going to make really profound observations",
                "2019-01-07 22:17:54",
            ),
            (
                "Maybe they'll be more obvious than I thought",
                "2019-02-06 22:17:54",
            ),
        ],
    },
    {
        "fname": "Bunny",
        "lname": "Easter",
        "notes": [
            ("Has anyone seen my Easter eggs?", "2019-01-07 22:47:54"),
            ("I'm really late delivering these!", "2019-04-06 22:17:54"),
        ],
    },
]

# Delete database file if it exists currently
if os.path.exists("people.db"):
    os.remove("people.db")

# Create the database
db.create_all()

# iterate over the PEOPLE structure and populate the database
for person in PEOPLE:
    p = Person(lname=person.get("lname"), fname=person.get("fname"))

    # Add the notes for the person
    for note in person.get("notes"):
        content, timestamp = note
        p.notes.append(
            Note(
                content=content,
                timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
            )
        )
    db.session.add(p)

db.session.commit()


def ifNotCreateDB():
    sqliteConnection = sqlite3.connect('seekingAlpha.DB')
    cursor = sqliteConnection.cursor()

    createBankingSheetsTable = f'''CREATE TABLE IF NOT EXISTS balanceSheets (
        rowid INTEGER PRIMARY KEY, companyTicker TEXT, lineItemName TEXT, lineItemSectionGroup TEXT, absoluteDateValues TEXT, yearOverYearGrowthValue TEXT, percentOfAssetsOverLiabilities TEXT
    ); '''
    createCashFlowsTable = f'''CREATE TABLE IF NOT EXISTS cashFlows (
        rowid INTEGER PRIMARY KEY, companyTicker TEXT, lineItemName TEXT, lineItemSectionGroup TEXT, absoluteDateValues TEXT, yearOverYearGrowthValue TEXT, percentOfAssetsOverLiabilities TEXT
    ); '''
    createIncomeStatementsTable = f'''CREATE TABLE IF NOT EXISTS incomeStatements( 
        rowid INTEGER PRIMARY KEY, companyTicker TEXT, lineItemName TEXT, lineItemSectionGroup TEXT, absoluteDateValues TEXT, yearOverYearGrowthValue TEXT, percentOfAssetsOverLiabilities TEXT
    ); '''

def loadSeekingAlphaDB(ticker):
    headers = { # Necessary or else requests are 403 Forbidden 
        'Referer': f'https://seekingalpha.com/symbol/{ticker}/balance-sheet',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*'
    }
    #sqliteConnection = sqlite3.connect('seekingAlpha.db')
    balanceSheetAnnualURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=annual&statement_type=balance-sheet&order_type=latest_left&is_pro=True'
    balanceSheetQuarterlyURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=balance-sheet&order_type=latest_left&is_pro=True'
    
    cashFlowAnnualURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=cash-flow-statement&order_type=latest_left&is_pro=True'
    cashFlowQuarterlyURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=cash-flow-statement&order_type=latest_left&is_pro=True'

    incomeStatementAnnualURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=annual&statement_type=income-statement&order_type=latest_left&is_pro=True'
    incomeStatementQuarterlyURL = f'https://seekingalpha.com/symbol/{ticker}/financials-data?period_type=quarterly&statement_type=income-statement&order_type=latest_left&is_pro=True'
    
    balanceSheetRes = requests.get(url=balanceSheetAnnualURL, headers=headers)
    print(balanceSheetRes.status_code)
    companyAnnualBalanceSheet = balanceSheetRes.json()
    for datum in companyAnnualBalanceSheet['data']:
        print(datum[0][0]['name'])
        print(datum[0][0]['value'])
        print(datum[0][0]['sectionGroup'])
        print(datum[0][0]['chartId'])

        print(datum[0][1]['name'])
        print(datum[0][1]['value'])
        #print(datum[0][1]['raw_value'])
        # print(datum[0][1]['yoy_value'])
        print(datum[0][1]['class'])
        # print(datum[0][1]['asset_percent'])

        print(datum[0][2]['name'])
        print(datum[0][2]['value'])
        print(datum[0][2]['raw_value'])
        print(datum[0][2]['yoy_value'])
        print(datum[0][2]['class'])
        # print(datum[0][2]['asset_percent'])


        print(datum[0][3]['name'])
        print(datum[0][3]['value'])
        print(datum[0][3]['raw_value'])
        print(datum[0][3]['yoy_value'])
        print(datum[0][3]['class'])
        # print(datum[0][3]['asset_percent'])


        print(datum[0][4]['name'])
        print(datum[0][4]['value'])
        print(datum[0][4]['raw_value'])
        print(datum[0][4]['yoy_value'])
        print(datum[0][4]['class'])
        # print(datum[0][4]['asset_percent'])


        print(datum[0][5]['name'])
        print(datum[0][5]['value'])
        print(datum[0][5]['raw_value'])
        print(datum[0][5]['yoy_value'])
        print(datum[0][5]['class'])
        # print(datum[0][5]['asset_percent'])


        print(datum[0][6]['name'])
        print(datum[0][6]['value'])
        print(datum[0][6]['raw_value'])
        print(datum[0][6]['yoy_value'])
        print(datum[0][6]['class'])
        # print(datum[0][6]['asset_percent'])

    
    balanceSheetQuarterlyRes = requests.get(url=balanceSheetQuarterlyURL, headers=headers)
    print(balanceSheetQuarterlyRes.status_code)
    companyQuarterlyBalanceSheet = balanceSheetQuarterlyRes.json()
    

    cashFlowAnnualRes = requests.get(url=cashFlowAnnualURL, headers=headers)
    print(cashFlowAnnualRes.status_code)
    companyAnnualCashFlow = cashFlowAnnualRes.json()

    cashFlowQuarterlyRes = requests.get(url=cashFlowQuarterlyURL, headers=headers)
    print(cashFlowQuarterlyRes.status_code)
    companyQuarterlyCashFlow = cashFlowQuarterlyRes.json()

    incomeStatementAnnualRes = requests.get(url=incomeStatementAnnualURL, headers=headers)
    print(incomeStatementAnnualRes.status_code)
    companyAnnualIncomeStatement = incomeStatementAnnualRes.json()

    incomeStatementQuarterlyRes = requests.get(url=incomeStatementQuarterlyURL, headers=headers)
    print(incomeStatementQuarterlyRes.status_code)
    companyQuarterlyIncomeStatement = incomeStatementQuarterlyRes.json()

    
    return

loadSeekingAlphaDB('SCHW')

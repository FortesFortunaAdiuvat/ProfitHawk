## Seeking Alpha Module

### Please run `python seekingAlphaMiner.py --help` for CLI options
 - Use `--file` followed by a space delimited list of files containing space delimited ticker symbols
 - Use `--ticker` to provide a space delimited list of ticker symbols directly on command line
 - Give `--debug` flag to show enhanced output

### General Info
 - Database name used is by today's date in format YYYYMMDD. Subsequent runs in same day utilize the same database.
 - Excel CSV files are in the excel folder
 - Error logs are in the err folder
 - Create a seekingAlphaProCookie.txt file in this dir with your Machine Cookie from Browser for Pro Data)

### Database Schema Info
 - Company Financial Fundamental data is split into balanceSheets, incomeStatements, cashFlow tables
 - Coupon and Growth data is stored in study_futureCoupon table
 - Company stock info is in priceAction table

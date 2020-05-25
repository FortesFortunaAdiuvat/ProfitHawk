select 
distinct  main.sector,main.industry, main.companyticker, main.Profit_Margin,main.Retained_Income,Current_Ratio,
main.rawvalue_1, main.rawvalue_2,
--(main.rawvalue_1+ main.rawvalue_2+main.rawvalue_2) / 1000000 Total,
main.rawvalue_1 + - (main.rawvalue_2) Expenses


from (

select  distinct  o.sector,o.industry, a.companyticker, 
round((cast(a.rawvalue as float)/ cast(b.rawvalue as float) ) *100,2) Profit_Margin,
round((cast(c.rawvalue as float)/ cast(b.rawvalue as float) ) *100,2) Retained_Income,
round((CAST(b1.rawvalue AS FLOAT) / 1000000) / (CAST(b2.rawvalue AS FLOAT) / 1000000 ),2) Current_Ratio,

case  when (a.lineitemname = 'Selling General & Admin Expenses' and a.timescale = 'annual_TTM') then a.rawvalue else '' end rawvalue_1,
--case when (a.lineitemname = 'Net Interest Expenses' or a.timescale = 'annual_TTM') then b.rawvalue else '' end rawvalue_2,
 -- case when (a.lineitemname = 'Depreciation & Amortization' or a.timescale = 'annual_TTM') then b.rawvalue else '' end rawvalue_3
from incomeStatements a, incomeStatements b, incomeStatements c,overviewData O ,
balancesheets b1,   balancesheets b2 
where a.companyticker = b.companyticker and a.companyticker = c.companyticker 
and b1.companyticker = b2.companyticker
and a.companyticker = b1.companyticker
and  a.companyticker = O.companyticker and
a.lineitemname = 'Gross Profit' and a.timescale = 'annual_TTM'
and b.lineitemname = 'Total Revenues' and b.timescale = 'annual_TTM'
and c.lineitemname = 'Net Income' and c.timescale = 'annual_TTM'
and b1.lineitemname = 'Total Current Assets' and b1.timescale = 'annual_lastReport'
and b2.lineitemname = 'Total Current Liabilities' and b2.timescale = 'annual_lastReport'
) Main

--SGA Selling General & Admin Expenses + Net Interest Expenses
--R&D Expenses ,Property Expenses Other, Operating Expenses,Provision For Loan Losses,Total Interest Expense
--Depreciation & Amortization
----Depreciation & Amortization, Total
--If you find D&A on Income Statement - use it
--otherwise
--look at Cash Flow and try to find
--"Depreciation & Amortization, Total"
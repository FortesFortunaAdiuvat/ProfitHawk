-- SQLite


CREATE TABLE _vars(companyTicker);
INSERT INTO _vars(companyTicker) VALUES ('T');


select A.date, 
      A.rawvalue/ 1000000 as Revenues, 
      B.rawvalue/ 1000000 as GrossProfit, 
      C.rawvalue/ 1000000 as NetIncome ,
      D.rawvalue/ 1000000 as RevCO,
      E.rawvalue/ 1000000 as _ExSGA,
      F.rawvalue/ 1000000 as _ExDA,
      G.rawvalue/ 1000000 as _ExNI,
      H.rawvalue/ 1000000 as _ExRnD,
      BS_A.rawvalue/ 1000000 as Cash,
      BS_B.rawvalue/ 1000000 as CA,
      BS_C.rawvalue/ 1000000 as CL,
      BS_D.rawvalue/ 1000000 as TA,
      BS_E.rawvalue/ 1000000 as TL,
      BS_F.rawvalue/ 1000000 as RetainedEarnings
    from incomeStatements as A
inner JOIN incomeStatements as B
 on A.date = B.date
inner JOIN incomeStatements as C
 On A.date = C.date
inner JOIN incomeStatements as D 
 On A.date = D.date
inner JOIN incomeStatements as E
 On A.date = E.date
inner JOIN incomeStatements as F
 On A.date = F.date
inner JOIN incomeStatements as G
 On A.date = G.date
inner JOIN incomeStatements as H
 On A.date = H.date
 inner join balanceSheets as BS_A
on A.date = BS_A.date
 inner join balanceSheets as BS_B
on A.date = BS_B.date
 inner join balanceSheets as BS_C
on A.date = BS_C.date
 inner join balanceSheets as BS_D
on A.date = BS_D.date
 inner join balanceSheets as BS_E
on A.date = BS_E.date
 inner join balanceSheets as BS_F
on A.date = BS_F.date
    where A.companyticker = (select companyticker from _vars) and A.lineitemname = 'Revenues' and A.timescale = "annual"
    and B.companyticker = (SELECT companyticker from _vars)   and B.lineitemname = 'Gross Profit' and B.timescale = "annual"
    and C.companyticker =  (SELECT companyticker from _vars)  and C.lineitemname = "Net Income to Company" and C.timescale = "annual"
    and D.companyticker = (SELECT companyticker from _vars)   and D.lineitemname = "Earnings From Continuing Operations" and D.timescale = "annual"
    and E.companyticker = (SELECT companyticker from _vars)   and E.lineitemname = "Selling General & Admin Expenses" and E.timescale = "annual"
    and F.companyticker = (SELECT companyticker from _vars)   and F.lineitemname = "Depreciation & Amortization" and F.timescale = "annual"
    and G.companyticker = (SELECT companyticker from _vars)   and G.lineitemname = "Interest Expense" and G.timescale = "annual"
    --and H.companyticker = (SELECT companyticker from _vars)   and H.lineitemname = "R&D Expenses" and H.timescale = "annual"
  and BS_A.companyticker = (SELECT companyticker from _vars) and BS_A.lineitemname = "Cash And Equivalents" and BS_A.timescale="annual"
  and BS_B.companyticker = (SELECT companyticker from _vars) and BS_B.lineitemname = "Total Current Assets" and BS_B.timescale="annual"
  and BS_C.companyticker = (SELECT companyticker from _vars) and BS_C.lineitemname = "Total Current Liabilities" and BS_C.timescale="annual"
     and BS_D.companyticker = (SELECT companyticker from _vars) and BS_D.lineitemname = "Total Assets" and BS_D.timescale="annual"
  and BS_E.companyticker = (SELECT companyticker from _vars) and BS_E.lineitemname = "Total Liabilities" and BS_E.timescale="annual"
  and BS_F.companyticker = (SELECT companyticker from _vars) and BS_F.lineitemname = "Retained Earnings" and BS_F.timescale="annual"
order by A.Date Asc;


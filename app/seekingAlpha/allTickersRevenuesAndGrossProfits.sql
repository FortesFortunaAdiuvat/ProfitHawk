-- SQLite
SELECT DISTINCT main.date, main.Revenues, main.GrossProfit from
(
SELECT a.companyTicker, a.date, a.rawvalue AS 'Revenues', a.lineitemname, b.rawvalue AS 'GrossProfit', b.lineitemname
FROM incomeStatements a, incomeStatements b
WHERE a.date = b.date and a.companyticker = b.companyTicker 
AND a.lineitemname = 'Revenues' and b.lineitemname = 'Gross Profit'
AND a.timescale = 'annual' AND b.timescale = 'annual'
) main
DROP TABLE IF EXISTS _vars;
CREATE TABLE _vars(companyTicker);
INSERT INTO _vars(companyTicker) VALUES ('INTC');

SELECT a.date,
	CASE WHEN (a.rawvalue is null or a.rawvalue = '') then 0 ELSE a.rawvalue END GrossProfit,
    CASE WHEN (b.rawvalue is null or b.rawvalue = '') then 0 else b.rawvalue end NetIncome,
    case when (c.rawvalue is null or c.rawvalue = '') then 0 else c.rawvalue end RevCO,
    case when (d.rawvalue is null or d.rawvalue = '') then 0 else d.rawvalue end _ExSGA,
    case when (e.rawvalue is null or e.rawvalue = '') then 0 else e.rawvalue end _ExDA,
    case when (f.rawvalue is null or f.rawvalue = '') then 0 else f.rawvalue end _ExNI,
    case when (g.rawvalue is null or g.rawvalue = '') then 0 else g.rawvalue end Cash,
    case when (h.rawvalue is null or h.rawvalue = '') then 0 else h.rawvalue end _ExRnD,
    Case when (bs_a.rawvalue is null or bs_a.rawvalue ='')  then 0 else bs_a.rawvalue end Cash,
    CASE WHEN (bs_b.rawvalue is null or bs_b.rawvalue = '') then 0 else bs_b.rawvalue END CA,
    case when (bs_c.rawvalue is null or bs_c.rawvalue = '') then 0 else bs_c.rawvalue end CL,
    Case when (bs_d.rawvalue is null or bs_d.rawvalue ='')  then 0 else bs_d.rawvalue end TA,
    case when (bs_e.rawvalue is null or bs_e.rawvalue = '') then 0 else bs_e.rawvalue end TL,
    case when (bs_f.rawvalue is null or bs_f.rawvalue = '') then 0 else bs_f.rawvalue end RetainedEarnings
FROM _vars
LEFT JOIN incomeStatements a ON a.companyticker = _vars.companyticker AND a.lineitemname = 'Revenues' AND a.timescale = 'annual'
LEFT JOIN incomeStatements b on b.date = a.date and b.companyticker = _vars.companyticker and b.lineitemname = 'Gross Profit' and b.timescale = 'annual'
left join incomeStatements c on c.date = a.date and c.companyticker = _vars.companyticker and c.lineitemname = 'Net Income to Company' and c.timescale = 'annual'
left join incomeStatements d on d.date = a.date and d.companyticker = _vars.companyticker and d.lineitemname = 'Earnings From Continuing Operations' and d.timescale = 'annual'
left join incomeStatements e on e.date = a.date and e.companyticker = _vars.companyticker and e.lineitemname = 'Selling General & Admin Expenses' and e.timescale = 'annual'
left JOIN incomeStatements f on f.date = a.date and f.companyticker = _vars.companyticker and f.lineitemname = 'Depreciation & Amortization' and f.timescale = 'annual'
left join incomeStatements g on g.date = a.date and g.companyticker = _vars.companyticker and g.lineitemname = 'Net Interest Expenses' and g.timescale = 'annual'
LEFT JOIN incomeStatements h ON h.date = a.date AND h.companyticker = _vars.companyticker AND h.lineitemname = 'R&D Expenses' and h.timescale = 'annual'
LEFT JOIN balanceSheets bs_a ON bs_a.date = a.date AND bs_a.companyticker = _vars.companyticker AND bs_a.lineitemname = 'Cash And Equivalents' AND bs_a.timescale = 'annual'
left join balanceSheets bs_b on bs_b.date = a.date and bs_b.companyticker = _vars.companyticker and bs_b.lineitemname = 'Total Current Assets' and bs_b.timescale = 'annual'
left join balanceSheets bs_c on bs_c.date = a.date and bs_c.companyticker = _vars.companyticker and bs_c.lineitemname = 'Total Current Liabilities' and bs_c.timescale = 'annual'
LEFT JOIN balanceSheets bs_d ON bs_d.date = a.date AND bs_d.companyticker = _vars.companyticker AND bs_d.lineitemname = 'Total Assets' AND bs_d.timescale = 'annual'
left join balanceSheets bs_e on bs_e.date = a.date and bs_e.companyticker = _vars.companyticker and bs_e.lineitemname = 'Total Liabilities' and bs_e.timescale = 'annual'
left join balanceSheets bs_f on bs_f.date = a.date and bs_f.companyticker = _vars.companyticker and bs_f.lineitemname = 'Retained Earnings' and bs_f.timescale = 'annual';

DROP TABLE _vars
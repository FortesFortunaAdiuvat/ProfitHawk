import camelot, requests
import pandas as pd

def extractFilingTables(ticker):
    # looking for Form SC 13D
    headers = { 
        'Referer': f'https://seekingalpha.com/symbol/{ticker}/balance-sheet',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
    }
    url = f'https://seekingalpha.com/filings/pdf/14257148.pdf' 
    res = requests.get(url=url, headers=headers)
    # print(res)
    with open(f'{ticker}_SC 13D.pdf', 'wb') as f: # https://stackoverflow.com/questions/34503412/download-and-save-pdf-file-with-python-requests-module
        f.write(res.content)
    tables = camelot.read_pdf(f'{ticker}_SC 13D.pdf', pages="3-end", flavor='lattice')
    for t in tables:
        print(t.parsing_report)
        t_df = t.df
        pd.set_option('display.max_rows', len(t_df))
        print(t_df)
    return

extractFilingTables('SCON')
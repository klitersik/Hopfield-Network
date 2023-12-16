import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
from supabase import create_client, Client

months_dict = {
    'sty': '01', 'lut': '02', 'mar': '03', 'kwi': '04', 'maj': '05', 'cze': '06',
    'lip': '07', 'sie': '08', 'wrz': '09', 'paź': '10', 'lis': '11', 'gru': '12'
}

button_x_Path = '/html/body/div/div[2]/div[1]/div[2]/div[2]/button[1]'
table_x_Path = "/html/body/table[1]/tbody/tr[2]/td[2]/table/tbody/tr/td/table/tbody/tr/td/table[5]/tbody/tr/td/table/tbody/tr[2]/td[1]/table[2]/tbody"

url: str = "https://iqcvodlrxlihqexxwpiv.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlxY3ZvZGxyeGxpaHFleHh3cGl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDA1NzI3MTgsImV4cCI6MjAxNjE0ODcxOH0.syaMQHi6l0_G-PBXM5VdXgd3jc-vjHzTMxJ92r2RimU"
supabase: Client = create_client(url, key)

data_rows = []

def konwersja_daty(row):
    day, month = row['Data'].split()  # Podzielenie na dzień i skrót miesiąca
    month_number = months_dict[month]  # Znalezienie numeru miesiąca
    year = 2023  # Możesz dodać rok zgodnie z potrzebą
    return datetime.strptime(f"{day} {month_number} {year}", "%d %m %Y")  # Tworzenie pełnej daty

def konwersja_wartosci(row):
    value = row['Wolumen'][:-1]  # Wybierz wartość bez ostatniej litery
    if row['Wolumen'].endswith('m'):
        return float(value) * 1000000  # Pomnożenie dla 'm'
    elif row['Wolumen'].endswith('k'):
        return float(value) * 1000  # Pomnożenie dla 'k'
    else:
        return value   # Zwrócenie wartości bez zmiany
    
async def main():
    browser = await launch(autoClose=False,headless=True,options={'args': ['--no-sandbox']})
    page = await browser.newPage()
    for i in range(1,45):
        print("Analizowana strona:",i)
        await page.goto(f'https://stooq.pl/t/?i=516&v=0&l={i}&o=5')
        await page.waitFor(3000)

        button = await page.xpath(button_x_Path)
        if button:
            await page.waitFor(2000)
            await button[0].click()
            await page.waitFor(5000)
            await page.reload()
            await page.waitFor(8000)

        await page.waitFor(3000)

        table = await page.waitForXPath(table_x_Path)
        html_code = await page.evaluate('(element) => element.outerHTML', table)

        soup = BeautifulSoup(html_code, 'html.parser')

        relevant_tr_tags = soup.find_all('tr', id=lambda x: x and x.startswith('r_') and x.split('_')[1].isdigit() and 0 <= int(x.split('_')[1]) <= 99)
        
        for tr_tag in relevant_tr_tags:
            td_tags = tr_tag.find_all('td')
            row = []    
            for td_tag in td_tags:
                row.append(td_tag.text.strip())
            
            data_rows.append(row)

    df = pd.DataFrame(data_rows, columns=["Symbol", "Nazwa", "Kurs", "Zmiana%", "Zmiana", "Wolumen", "Data", "idk"])
    df = df.drop(columns=["idk","Nazwa","Zmiana%", "Zmiana"])

    print(df)
    
    df['Data'].replace('', np.nan, inplace=True)
    df = df.dropna(how='any', axis=0)
    df.dropna(subset=['Data'], inplace=True)
    df["Data"] = "15 gru"
    df['Data'] = df.apply(konwersja_daty, axis=1)
    df['Data'] = df['Data'].astype(str)

    df['Wolumen'] = df.apply(konwersja_wartosci, axis=1)
    df['Wolumen'] = pd.to_numeric(df['Wolumen'], errors='coerce').fillna(0).astype(int)

    df = df.drop_duplicates()
    chunk_size = 100
    
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]

        records = []

        for index, row in chunk.iterrows():
            record = {
                "symbol": row['Symbol'],
                "Kurs": row['Kurs'],
                "Wolumen": row['Wolumen'],
                "Data": row['Data']
            }
            records.append(record)

        data, count = supabase.table('indeksy').insert(records).execute()
    
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())

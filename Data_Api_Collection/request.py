import requests
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

def get_data(date_str: str, page_no: int = 1):
    url = os.getenv("API_KEY")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "date": date_str,
        "pageNo": str(page_no)
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        json_data = response.json()

        if json_data.get("errorCodes") == ["0"]:
            domestic_list = json_data.get("DomesticDetails", [])
            if domestic_list:
                df = pd.DataFrame(domestic_list)
                return df
            else:
                print(f"⚠️ No data found for {date_str}, page {page_no}")
                return pd.DataFrame()
        else:
            print("❌ API returned errorCodes:", json_data.get("errorCodes"))
            return pd.DataFrame()
    else:
        print("❌ HTTP error:", response.status_code)
        return pd.DataFrame()
df = get_data("2018-03", 1)
print(df.head())

import requests
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

def get_data(date_str: str, page_no: int):
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
        error_codes = json_data.get("errorCodes", [])

        if error_codes == ["0"]:
            domestic_list = json_data.get("DomesticDetails", [])
            if domestic_list:
                df = pd.DataFrame(domestic_list)
                keep_columns = ['month', 'year', 'destinationProvinceNameEn', 'originProvinceNameEn',
                            'visitPurposeEn', 'trips', 'spendSAR', 'nights']
                df = df[keep_columns]
                return df, "0"
            else:
                return pd.DataFrame(), "0"  
        elif error_codes:
            return pd.DataFrame(), error_codes[0]
        else:
            return pd.DataFrame(), "unknown"
    else:
        return pd.DataFrame(), str(response.status_code)

    
print(get_data("2024-01", 1))  # Example usage for testing



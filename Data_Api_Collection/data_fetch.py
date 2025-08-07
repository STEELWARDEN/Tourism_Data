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
    


def get_data_temp_single(latitude: float, longitude: float,time: int):
        api_key = os.getenv("API_KEY_TEMP")
        url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={time}&units=metric&appid={api_key}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                temp = data["data"][0]["temp"]
        else:
            raise Exception(f"Error fetching temperature data: {response.status_code}") 
        return temp, "200"

def get_data_temp_bulk(latitude: float, longitude: float, start_time: int, end_time: int,province: str):
    url = os.getenv("API_KEY_BULK")
    params = {
        "start": start_time,
        "end": end_time,
        "latitude": latitude,
        "longitude": longitude,
        "parameters": "T2M",  # Temperature at 2 meters
        "community": "AG",
        "format": "JSON"
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(response)
    print(data)

    if "properties" not in data or "parameter" not in data["properties"]:
        print(f"No temperature data for {province}")
        return pd.DataFrame()

    temp_data = data["properties"]["parameter"]["T2M"]

    df = pd.DataFrame({
        "date": temp_data.keys(),
        "temp": temp_data.values(),
        "province": province
    })

    df["year"] = df["date"].str[:4].astype(int)
    df["month"] = df["date"].str[4:].astype(int)
    df = df.drop(columns=["date"])

    return df






      

        




    



import data_fetch as gd
import pandas as pd
from datetime import datetime
import time



temp_data = "C:\\Users\\Mohammed\\Desktop\\Machine learning project for Tourism Data\\Data\\Temp_Province_data.csv"
tourist_data = "C:\\Users\\Mohammed\\Desktop\\Machine learning project for Tourism Data\\Data\\Tourism_data.csv"
tourist_temp_data = "C:\\Users\\Mohammed\\Desktop\\Machine learning project for Tourism Data\\Data\\tourism_with_temps.csv"




 


def init_data_tourist():
  year = 2018
  month = 1
  column_names = ['month', 'year', 'destinationProvinceNameEn', 
                 'originProvinceNameEn', 'visitPurposeEn', 
                 'trips', 'spendSAR', 'nights']
  df = pd.DataFrame(columns=column_names)
  df.to_csv(tourist_data, index=False)
  

  while not (year == 2025 and month == 8):
      date_str = f"{year}-{month:02d}"
      page_no = 1

      while True:
          df_response, status = gd.get_data(date_str, page_no)
          if status == "0":
                      df_response.to_csv(tourist_data, mode='a', header=False, index=False)
                      page_no += 1
                      print(df_response)
          elif status == "104" or status == "101":
               break
          elif status == "102":
               break
          else:
               raise Exception(f"Error fetching data: {status}")

      month += 1
      if month > 12:
          month = 1
          year += 1


def init_temperature_data():
     province_records = {"Jazan":(16.8894, 42.5706),"Riyadh":(24.7136, 46.6753),"Madinah":(24.4672, 39.6024),"Eastren":(23.5681, 50.6794),"Makkah":(21.4241, 39.8173),
                            "Tabuk":(28.3835, 36.5662),"Hail":(27.5114, 41.7208),"Northern Borders":(30.0799, 42.8638),"Alqassim":(26.2078, 43.4837),
                            "Albaha":(18.2465, 42.5117),"Najran":(17.5656, 44.2289),"Aseer":(19.0969, 42.8638),"Jouf":(29.8874, 39.3206),}
     
     column_names = ['month', 'year', 'province', 'temp']
     df = pd.DataFrame(columns=column_names)
     df.to_csv(temp_data, index=False)

     
     start_date_year = 2018
     end_date_year = 2023
    

     for key in province_records:
           latitude, longitude = province_records[key]
           df_response = gd.get_data_temp_bulk(latitude,longitude,start_date_year,end_date_year,key)
           if not df_response.empty:
                    df_response = df_response[['month', 'year', 'province', 'temp']] 
                    df_response.to_csv(temp_data, mode='a', header=False, index=False)
           else:
                raise Exception(f"Error fetching temperature data for {key}, {df_response}")

def merge_data():
     tourist_df = pd.read_csv(tourist_data)
     temp_df = pd.read_csv(temp_data)

     tourist_df['year'] = tourist_df['year'].astype(int)
     temp_df['year'] = temp_df['year'].astype(int)
     tourist_df['month'] = tourist_df['month'].astype(int)
     temp_df['month'] = temp_df['month'].astype(int)


     origin_temp = temp_df.rename(columns={'province': 'originProvinceNameEn', 'temp': 'origin_temp'})
     tourist_df = tourist_df.merge(origin_temp, on=['originProvinceNameEn', 'year', 'month'], how='left')

     destination_temp = temp_df.rename(columns={'province': 'destinationProvinceNameEn', 'temp': 'destination_temp'})
     tourist_df = tourist_df.merge(destination_temp, on=['destinationProvinceNameEn', 'year', 'month'], how='left')

     tourist_df.to_csv(tourist_temp_data, index=False)



merge_data()







          

                    
               
                    
                         
                    
                
           
     
           


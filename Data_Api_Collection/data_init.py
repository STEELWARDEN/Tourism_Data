import data_fetch as gd
import pandas as pd



temp_data = "C:\\Users\\Mohammed\\Desktop\\Machine learning project for Tourism Data\\Data\\Temp_Province_data.csv"
tourist_data = "C:\\Users\\Mohammed\\Desktop\\Machine learning project for Tourism Data\\Data\\Tourism_data.csv"



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


init_data_tourist()
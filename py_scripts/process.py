import numpy as np
import pandas as pd


# process raw data (as data) and output the processed data
def process_data(data):
    # copy data
    data = data.copy()

    # transform DATE to string
    data["DATE"] = data["DATE"].apply(lambda d: str(d)[:10])

    # Add new col "crop year" for wheat calender 
    data["crop_year"] = data["DATE"].apply(classify_date)

    # remove ****-02-29 from crop years

    # select index
    arr_date_to_remove = [f"{year}-02-29" for year in range(1981, 2020 + 1)]
    index_to_drop = data[data["DATE"].isin(arr_date_to_remove)].index

    data.drop(index_to_drop, inplace=True)

    # remove crop years 1981, 2021 as they are not complete
    # remove also not classified

    # select index
    index_to_drop = data[data["crop_year"].isin(["1981", "2021", "not classified"])].index

    data.drop(index_to_drop, inplace=True)

    # create col of days
    # for each crop year

    val_counts = data["crop_year"].value_counts()

    nb_years = len(val_counts)
    nb_days = val_counts[0]

    # create a list of days 
    # in my case 1 --> nb_days
    li_days = [i + 1 for i in range(nb_days)]

    # create the complet col to be added 
    # data frame
    # concatenation of the li of days
    complet_li_days = []
    for i in range(nb_years):
        complet_li_days += li_days

    data["day"] = complet_li_days

    # create avg col
    data["GDD"] = (data["T2M_MAX"] + data["T2M_MIN"]) / 2

    # create cumulative columns
    for col in ["GDD", "PRECTOT", "WS2M", "RH2M"]:
        data[f"cumulative_{col}"] = create_cumsum(data, col)

    return data


# function to classify crop years
# d as a string
def classify_date(d):
  d = pd.Timestamp(d)
  # wheat calendar
  START_DATE = "-10-15"
  END_DATE = "-07-10"

  prev_year = str(d.year - 1)
  current_year = str(d.year)
  next_year = str(d.year + 1)

  to_date = pd.Timestamp
  if to_date(current_year + START_DATE) <= d <= to_date(next_year + END_DATE):
    return next_year

  if to_date(prev_year + START_DATE) <= d <= to_date(current_year + END_DATE):
    return current_year
  
  return "not classified"


# to create cumulative sum of crop years
def create_cumsum(data, col_name):
    # cumsum for a single year
    create_cum_for_year = lambda crop_year_, col_name_: data[data["crop_year"] == crop_year_][col_name_].copy().cumsum()
    
    # repeat the same procedure for all crop years
    arr_li_cum_prec = []
    for crop_year in data["crop_year"].value_counts().sort_index().index:
        arr_li_cum_prec.append(create_cum_for_year(crop_year, col_name))

    return pd.concat(arr_li_cum_prec, ignore_index=True).values
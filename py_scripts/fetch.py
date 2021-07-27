import requests
import pandas as pd


class LocationWeather:
  def __init__(self, lat, lon, start_date="19810101", end_date="20210131"):

    # to call API
    URL = "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?"+\
    "&request=execute&identifier=SinglePoint&"+\
    "parameters=PRECTOT,WS2M,RH2M,T2MDEW,T2M_MAX,T2M_MIN,ALLSKY_SFC_SW_DWN,T2M&"+\
    f"startDate={start_date}&endDate={end_date}&userCommunity=AG&"+\
    f"tempAverage=DAILY&outputList=CSV&lat={lat}&lon={lon}&user=DAV"

    # network request
    self.res = requests.get(URL).json()

    # build weather data frame
    # dict
    self.weather_dict = {}
    res_reduced = self.res["features"][0]["properties"]['parameter']

    # date col
    # all dic obj are { "date": val }
    translate_to_date = LocationWeather.translate_to_date
    self.weather_dict["DATE"] = [translate_to_date(d) for d in res_reduced["PRECTOT"].keys()]

    # build weather col
    for key in res_reduced:
      self.weather_dict[key] = list(res_reduced[key].values())

    # final data frame object
    self.weather_data_frame = pd.DataFrame(self.weather_dict)
    return

  @staticmethod
  # transform date year_month_day --> date object
  # date of 20200114 --> 2020-01-14
  def translate_to_date(s_date):

    # split string
    year = int(s_date[0:4])
    month = int(s_date[4:6])
    day = int(s_date[6:])

    return pd.Timestamp(year=year, month=month, day=day)
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 13:42:33 2023

@author: xiaom
"""

import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import scipy.stats as st


ev_vehicle = pd.read_csv("C:/Users/xiaom/OneDrive/Desktop/Github Folder/Electric-Vehicle-EDA/Electric_Vehicle_Population_Data.csv")

ev_vehicle.columns

ev_vehicle.duplicated().sum()
#Overall no Duplicates in the Electric Vehicle Dataset

#Checking if the EV dataset have any missing values(for each variable)
ev_vehicle.isna().sum()

ev_vehicle[ev_vehicle['County'].isna()]

ev_vehicle[ev_vehicle['Vehicle Location'].isna()]

cnt_legis_district = ev_vehicle['Legislative District'].value_counts() \
                                  .reset_index() \
                                  .rename(columns = {'index':'Legislative District', 
                                                     'Legislative District': 'N'})

#Subsetted out whole dataset to only vehicles registered to the state of Washington
ev_subset = ev_vehicle.loc[ev_vehicle["State"] == "WA", ["County", "City", "Model Year", "Make", 
                                                      "Model", "Electric Vehicle Type", 
                                                      "Clean Alternative Fuel Vehicle (CAFV) Eligibility", 
                                                     "Electric Range", 'Base MSRP']] \
          .rename(columns = {'Electric Vehicle Type': 'EV_Type', 
                             "Clean Alternative Fuel Vehicle (CAFV) Eligibility": "CAFV", 
                             "Electric Range": "Electric_Range", 
                             'Base MSRP':"Base MSRP", 
                             "Model Year": "Model_Year"}).copy()

ev_subset.info()

# Count of registered EV by county and city
city_county_count = ev_subset[["County", "City"]] \
    .value_counts() \
    .reset_index() \
    .rename(columns = {0:"N"}) \
    .sort_values(by = "N", ascending = False)

#Count of registered EV by County
county_count = ev_subset["County"] \
    .value_counts(normalize = True) \
    .reset_index() \
    .rename(columns = {"index": "County",
                       "County": "N"})

# Subsetting for the top 10 counties w/ EV
top_ten_county = county_count.head(10).copy()
'''
Q1. which county + city have the most EV? Amongst top 10 - Which EV (Model + Make + Model Year) is most popular?
Q2. How does those EV (from q1) compare the ones that did not make to the list?
Q3. Is there a difference in preference EV state between top EV states and non ev states?
Limitations of the exploratory data analysis
'''
'''
Seems like the top ten counties accounts for about 91% of the total EV ownership in the State of Washington (2020 Census). Amongst the 
all counties, Kings county accounts for about 51% of the EV owernship. Based on this finding, we need to if the count of EV differs between 
county? (Potential intermediate questions - what are the most popular in the top 10 states? ) 
'''

car_variable = ['County','Model_Year', 'Make', 'Model', 'EV_Type', 'CAFV', 'Electric_Range', 'Base MSRP']
#Looking at the EV only associated w/ the top 10 county
car_detail_df = ev_subset.loc[ev_subset["County"].isin(top_ten_county["County"]), car_variable].copy()


# Count of EV car make by county (numerator)
cars_count_by_county = car_detail_df.groupby(by = ["County", "Make", "Model"], as_index = False)["County"].agg(["count"]) \
             .reset_index() \
             .sort_values(by = ["County", "count"], ascending = False)

# Count of all ev by county (Denominator)
total_ev_top_10 = cars_count_by_county.groupby(by = "County", as_index = False)["count"] \
                    .agg(["sum"]) \
                    .reset_index() \
                    .rename(columns = {"sum":"Total"}) \
                    .drop_duplicates(subset = "County").copy()

#Getting the top ev per each county
top_cars_by_county = (cars_count_by_county.drop_duplicates(subset = ["County"], keep = "first")
                                         .sort_values(by = "count", ascending = False)
                                         .reset_index(drop = True)
                                         .copy())

#Joining numerator dataset w/ denominator dataset to get the % of the most popular EV accounts for each county
county_car_join = (top_cars_by_county.merge(total_ev_top_10, how = "left", 
                        left_on = "County", 
                        right_on = "County", 
                        suffixes = ["_l", "_r"], 
                        validate = "one_to_one", 
                        indicator = True))

county_car_join["Rate"] = county_car_join["count"] /  county_car_join["Total"]
print(county_car_join)


#Seems like Tesla-Model Y accounts for a sizeable percentage of each of the top 10 EV counties in the state of Washington, (not accounting for model year and other factors. Surprisingly, Whatcomm County favors Nissan-Leaf more than Tesla EV (Nissan is the top 3rd preferred brand of EV in Washington). Other than this - no new interesting fact since Tesla is the main producer of EV after all. 
                                                                                                                           
car_specs = ev_subset[['County',  'Make', #'Model',
                       'EV_Type', 'CAFV', 'Electric_Range', 'Base MSRP']]


car_specs.head()


(car_specs.groupby(by = "Make", as_index = False)[["Electric_Range","Base MSRP"]] \
         .agg("mean") \
         .sort_values(by = "Electric_Range", ascending = False))


car_specs.groupby(by = ["Make", 'EV_Type'], as_index = False)['EV_Type'].agg(["count"]).reset_index().sort_values(by = "Make")


(car_specs["Make"].value_counts(ascending = False, normalize = True)
                 .reset_index()
                 .rename(columns = {'index': "Car Make", "Make":"Pct"}))
#Tesla represent 44% of the registered EVs in the State of Washington.
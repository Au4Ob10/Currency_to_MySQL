import subprocess
import sys
import pymysql
import csv
import datetime
from bs4 import BeautifulSoup
import requests 
import re
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter


#Code for commodities adapted from their respective pages on macrotrends.com: https://www.macrotrends.net/



def Commod_Prices(siteName,listName):

    data = requests.get(siteName)
    results = BeautifulSoup(data.text, "html.parser")

    Commod_Prices = results.find("tbody").findAll("tr")

    curr_idx = 0

    avg_price = 0

    #Calculate average price per Bushel for entire year range

    for i in Commod_Prices[0:23]:
        listName.append(i.findAll("td")[1].string)

        listName[curr_idx] = listName[curr_idx].strip("$")
        listName[curr_idx] = listName[curr_idx].replace(",","")
        
        avg_price += float(listName[curr_idx])

        listName[curr_idx] = f"{float(listName[curr_idx]):.2f}"
        listName[curr_idx] = "$" + str(listName[curr_idx])
        curr_idx += 1

    avg_price /= len(listName)
    avg_crop_prices.append("$" + str(f"{avg_price:.2f}"))


silv_url = "https://www.macrotrends.net/1470/historical-silver-prices-100-year-chart"
gold_url = "https://www.macrotrends.net/1333/historical-gold-prices-100-year-chart"
corn_url = "https://www.macrotrends.net/2532/corn-prices-historical-chart-data"
wheat_url = "https://www.macrotrends.net/2534/wheat-prices-historical-chart-data"
soybean_url = "https://www.macrotrends.net/2531/soybean-prices-historical-chart-data"


silver_prices_list = []
gold_prices_list = []
corn_prices_list = []
wheat_prices_list = []
soybean_prices_list = []
avg_crop_prices = []
    

Commod_Prices(corn_url,corn_prices_list)
Commod_Prices(wheat_url,wheat_prices_list)
Commod_Prices(soybean_url,soybean_prices_list)




try:
        conn = pymysql.connect(
        user="username",
        password="password",
        host="hostIP",
        port=3306,
        database="database_name"
    )
except pymysql.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()





# In this function call specify: starting row, ending row, starting col, ending col, name of appended list.
years = []



#Function to create my gold and silver tables. Column 1 is predefined as "year" since all my tables use it.


def yearlyChangeTable (tableName,col_2_Name,listName):
    list_idx = 0

    if listName == gold_prices_list or listName == silver_prices_list :

        cur.execute(f"CREATE TABLE {tableName} (Year int, {col_2_Name} varchar(10));")

    for i in years:
        cur.execute(f"INSERT INTO {tableName} (Year,{col_2_Name}) VALUES (%s,%s)", (str(i),listName[list_idx]))
        list_idx += 1
#     conn.commit()

yearlyChangeTable('Gold_Prices_Lab_5','Gold_Price_Per_Ounce',gold_prices_list)
yearlyChangeTable('Silver_Prices_Lab_5','Silver_Price_Per_Ounce',silver_prices_list)

#Function to populate mysql table with average closing price from 2000 to 2022.

def averagesTable_data(tableName,listName,col_2_Name,avg_price_idx):  

    list_idx = 0

    cur.execute(f"CREATE TABLE {tableName} (Year int, {col_2_Name} varchar(20),Average varchar (20),Above_or_Below varchar(20));")

    for i in years:
        
        if avg_crop_prices[avg_price_idx]  > listName[list_idx]:
            above_below = "Below_Average"

        elif avg_crop_prices[avg_price_idx]  < listName[list_idx]:
            above_below = "Above_Average"
        
        else: 
            above_below = "At_Average"

        cur.execute(f"INSERT INTO {tableName} (Year,{col_2_Name},Average,Above_or_Below) VALUES (%s,%s,%s,%s)", (str(i),listName[list_idx],avg_crop_prices[avg_price_idx],above_below))

        list_idx += 1

    conn.commit()

# Crop prices are measured in bushels.  For corn there are 56 lbs/bushel, whereas wheat and soybeans are 60 lbs/bushel.

averagesTable_data('Corn_Prices_Lab_5',corn_prices_list,'Corn_Price_Per_Bushel',0)

averagesTable_data('Wheat_Prices_Lab_5',corn_prices_list,'Wheat_Price_Per_Bushel',1)







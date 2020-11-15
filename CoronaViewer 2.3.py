#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 14:42:35 2020
@author: Lars Idema

Dashboard tool showing the development of corona in a selected country in graphs.
Four graphs are shown:
    - country
    - comparison country
    - list of countries sorted by e.g. number of cases
    - list of countries sorted by e.g. number of cases per million inhabitants
You can make a selection on number of cases, number of casualties etc.
The data is derived from "Our World in Data"

"""

# In[1]:


import pandas as pd
pd.set_option('display.max_rows', 10)
pd.options.display.max_rows

# Corona data from Our World in Data
# https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-codebook.csv
#
# iso_code, continent, location, date, total_cases, new_cases, new_cases_smoothed, total_deaths, new_deaths,
# new_deaths_smoothed, total_cases_per_million, new_cases_per_million, new_cases_smoothed_per_million, 
# total_deaths_per_million, new_deaths_per_million, new_deaths_smoothed_per_million, icu_patients, 
# icu_patients_per_million, hosp_patients, hosp_patients_per_million, weekly_icu_admissions, 
# weekly_icu_admissions_per_million, weekly_hosp_admissions, weekly_hosp_admissions_per_million, 
# total_tests, new_tests, new_tests_smoothed, total_tests_per_thousand, new_tests_per_thousand, 
# new_tests_smoothed_per_thousand, tests_per_case, positive_rate, tests_units, 
# stringency_index, population, population_density, median_age, aged_65_older, aged_70_older, 
# gdp_per_capita, extreme_poverty, cardiovasc_death_rate, diabetes_prevalence, 
# female_smokers, male_smokers, handwashing_facilities, hospital_beds_per_thousand, life_expectancy, human_development_index
#
cdata = pd.read_csv("https://github.com/owid/covid-19-data/raw/master/public/data/owid-covid-data.csv", index_col = "location")
#cdata.head()

# Add date numbers and country names as columns
cdata['date_num'] = cdata.groupby(['location']).cumcount()+1; cdata
cdata['country'] = cdata.index; cdata
cdata = cdata.drop('International')
cdata = cdata.drop('World')


# Drop small countries
small_countries = cdata[cdata["population"] < 1e6]
small_countries = list(set(list(small_countries.index.values)))
cdata = cdata.drop(small_countries)

import numpy as np
import matplotlib.pyplot as plt
country = "Netherlands"
nc = cdata.loc[[country], ["date", "date_num","new_cases"]]
ax1=nc.plot("date_num","new_cases", title=country, logy=True, color='orange', marker='.')


# In[2]:


# only select top countries
# first select last row of every country
cdata_last = cdata.groupby(["location"]).agg(lambda x: x.iloc[-1])
## print(cdata_last)

cdata_toplast = cdata_last[cdata_last["new_deaths"] > 250]
#cdata_toplast = cdata_toplast.drop('World')
cdata_toplast = cdata_toplast.sort_values(by=['new_deaths'], ascending=False)
#print(cdata_toplast)
# then only select countries with high values, also drop 'world' entry

# remove data from original dataset
top_countries = pd.Series(cdata_toplast.index.values, name='top10')
print("Top countries new deaths per day:\n",  top_countries)

#select data with only top countries 
cdata_top = cdata[cdata['country'].isin(top_countries)]

import seaborn as sns
sns.set()
g=sns.pairplot(x_vars=["date_num"], y_vars=["new_deaths"], data=cdata_top, hue="country", height=7, diag_kind = 'kde',
             plot_kws = {'alpha': 0.6, 's': 100, 'edgecolor': 'k'})
g.set(xlim=(60, None))


# In[3]:


mode1 = "new_cases"
mode = mode1

country = "Netherlands"
data1 = cdata.loc[[country], ["date", "date_num", mode]]
dates1 = data1["date_num"].values
values1 = data1[mode].values
values1[values1 == 0] = 0.1

country2 = "Germany"
data2 = cdata.loc[[country2], ["date", "date_num", mode]]
dates2 = data2["date_num"].values
values2 = data2[mode].values
values2[values2 == 0] = 0.1


# In[4]:


import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from numpy import isnan
from datetime import datetime
#import numpy as np

now = datetime.now() # current date and time
date_time = now.strftime("%d-%m-%Y")
print("date and time:",date_time)

root= tk.Tk()
# start full screen
root.attributes('-fullscreen', True)

label1 = tk.Label(root, text='CORONA DASHBOARD '+date_time)
label1.config(font=('Arial', 20))
label1.grid(row = 0, column = 0, sticky = "W", pady = 2, columnspan = 3) 

#canvas1.create_window(250, 50, window=label1)

def smoothdata(x, window_len=7, window='hanning'):
    #window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
    if window_len<3: return x
    s = np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat': w = np.ones(window_len,'d') #moving average
    else: w = eval('np.'+window+'(window_len)')
    y = np.convolve(w/w.sum(),s,mode='same')
    return y[window_len:-window_len+1]


def check_cmbo():
    global data1
    global data2
    global dates1
    global dates2
    global values1
    global values2
    global country1
    global country2
    global linlog
    global info1
    global info2
    global title1
    global title2
    global title3
    global title4
    global country1_str
    global country2_str
        
    country1 = combo1.get();
    country2 = combo5.get();
    mode1 = combo2.get() #cases/deaths
    mode2 = combo6.get() #abs/rel
    panel1 = combo7.get()
    topbot = combo8.get()
    
    if mode2 == "per million":
        mode = mode1+"_per_million"
    else: # "absolute"
        mode = mode1
    select = mode

    if topbot == "bottom countries":
        panel1_asc = True
    else: # "Top countries"
        panel1_asc = False
  
    data1 = cdata.loc[[country1], ["date", "date_num", select]]
    data2 = cdata.loc[[country2], ["date", "date_num", select]]
 
    # tests_units, stringency_index, population, population_density, median_age,
    # aged_65_older, aged_70_older, gdp_per_capita, extreme_poverty, 
    # cardiovasc_death_rate, diabetes_prevalence, female_smokers, male_smokers,
    # handwashing_facilities, hospital_beds_per_thousand, life_expectancy, human_development_index    
    
    country1_info = {
        "population": cdata.loc[country1].iloc[-5][34]/1e6,
        "density   ": cdata.loc[country1].iloc[-5][35],
        "life_exp  ": cdata.loc[country1].iloc[-5][47],
    }
    country2_info = {
        "population": cdata.loc[country2].iloc[-5][34]/1e6,
        "density   ": cdata.loc[country2].iloc[-5][35],
        "life_exp  ": cdata.loc[country2].iloc[-5][47],
    }

    # convert to string
    country1_str = ""
    for key in country1_info:
        print(country1_info[key])
        if isnan(country1_info[key]): country1_info[key] = 0        
        country1_str = country1_str + str(key) + ' ' + str(round(country1_info[key],1)) + '\n'
    country2_str = ""
    for key in country2_info:
        if isnan(country2_info[key]): country2_info[key] = 0        
        country2_str = country2_str + str(key) + ' ' + str(round(country2_info[key],1)) + '\n'
    
    # Data for panel 1
    # "corona", "population", "population_density", "gdp_per_capita", "human_development_index"
    # "ascending", "descending"
    if panel1 == "corona":
#        cdata_toplast = cdata_toplast[cdata_toplast["population"] > 1e6] # skip small countries
        cdata_panel = cdata_last[cdata_last["population"] > 1e6] # skip small countries
        info1 = cdata_panel.sort_values(by=[mode1], ascending=panel1_asc)[mode1]
#        info1 = cdata_toplast.sort_values(by=[mode1], ascending=panel1_asc)[mode1]
        info1 = info1[0:15]

    else:
        cdata_panel = cdata_last[cdata_last["population"] > 1e6] # skip small countries
        #cdata_panel = cdata_panel.drop('World')
        info1 = cdata_panel.sort_values(by=[panel1], ascending=panel1_asc)[panel1]
        info1 = info1[0:15]
    
    # Data per million
    printdata = cdata[cdata[select] > 1].pivot(index='country', columns='date_num', values=mode1+"_per_million")
    #prevent log of zero
    printdata[printdata<0.1] = 0.1
    # Fill in NaN's...
    printdata[printdata.isnull()] = 0.1
    #new death data is irregular, smoothen it 
    smooth = 7 #smoothen factor
    roll_window = printdata.T.rolling(window=smooth)
    rolldata = roll_window.mean()
    rolldata = rolldata.T
    weekcases = rolldata[rolldata.columns[-1]]
    #sort on last entries - highest on top
    info2 = weekcases.sort_values(axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last')[:15]

    period = combo4.get()
    if period=="all":
        dates1 = data1["date_num"].values
        values1 = data1[mode].values
        dates2 = data2["date_num"].values
        values2 = data2[mode].values
    elif period=="month": 
        dates1 = data1["date_num"].values[-30:]
        values1 = data1[mode].values[-30:]
        dates2 = data2["date_num"].values[-30:]
        values2 = data2[mode].values[-30:]
    elif period=="3 months": 
        dates1 = data1["date_num"].values[-90:]
        values1 = data1[mode].values[-90:]
        dates2 = data2["date_num"].values[-90:]
        values2 = data2[mode].values[-90:]
    values1[values1 == 0] = 0.1
    values2[values2 == 0] = 0.1
    
    lilo =combo3.get(); #lin or log plot
    if   (lilo == "lin") or (lilo == "smooth lin"): linlog = "lin"
    elif (lilo == "log") or (lilo == "smooth log"): linlog = "log"
    if   (lilo == "smooth lin" ) or (lilo == "smooth log" ):
        values1 = smoothdata(values1, 7) #window length = 7
        values2 = smoothdata(values2, 7)
    
    title1 = mode1 + " " + mode2 + " in " + country1
    title2 = mode1 + " " + mode2 + " in " + country2
    title3 = "Highest " + mode1 + " in the world"
    title4 = "Highest " + mode1 + " in the world, per million people"


def create_charts():
    global graph_active
    global country1
    global country2
    global country1_str
    global country2_str
    global mode1
    global mode2
    
    
    check_cmbo()
    
    # plot country of interest
    figure1 = Figure(figsize=(7, 3.5), dpi=100) #, frameon=False
    subplot1 = figure1.add_subplot(111)
    subplot1.plot(dates1, values1, marker='.', markerfacecolor='red')
    subplot1.set_title(title1)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    subplot1.text(0.05, 0.95, country1_str, transform=subplot1.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)
    if linlog == "log": 
        subplot1.set_yscale('log')
    else:
        subplot1.set_yscale('linear')
    figure1.set_tight_layout(True)
    plot1 = FigureCanvasTkAgg(figure1, root)
    plot1.draw()
    plot1.get_tk_widget().grid(row = 4, column = 0, pady = 2, columnspan = 3)

    # plot 2nd country of interest
    figure2 = Figure(figsize=(7, 3.5), dpi=100) #, frameon=False
    subplot2 = figure2.add_subplot(111)
    subplot2.plot(dates2, values2, marker='.', markerfacecolor='red')
    subplot2.set_title(title2)
    subplot2.text(0.05, 0.95, country2_str, transform=subplot2.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)
    subplot2.set_xlabel('days since first outbreak')
    if linlog == "log":  
        subplot2.set_yscale('log')
    else:
        subplot2.set_yscale('linear')
    figure2.set_tight_layout(True)
    plot2 = FigureCanvasTkAgg(figure2, root)  # A tk.DrawingArea.
    plot2.draw()
    plot2.get_tk_widget().grid(row = 5, column = 0, pady = 2, columnspan = 3)    
    
    # plot highest countries    
    figure3 = Figure(figsize=(7, 3.5), dpi=100) 
    subplot3 = figure3.add_subplot(111) 
    xAxis = info1.index 
    yAxis =  info1.values 
    subplot3.bar(xAxis,yAxis, color = 'lightsteelblue')
    subplot3.tick_params(labelrotation=45)
    subplot3.set_title(title3)
    subplot3.tick_params(axis='x', labelsize=10)
    figure3.subplots_adjust(bottom=0.3) # or whatever
    figure3.set_tight_layout(True)
    plot3 = FigureCanvasTkAgg(figure3, root)  # A tk.DrawingArea.
    plot3.draw()
    plot3.get_tk_widget().grid(row = 4, column = 4, pady = 2)    
    
    # plot highest countries    
    figure4 = Figure(figsize=(7, 3.5), dpi=100) 
    subplot4 = figure4.add_subplot(111) 
    xAxis = info2.index 
    yAxis = info2.values 
    subplot4.bar(xAxis,yAxis, color = 'lightsteelblue')
    subplot4.tick_params(labelrotation=45)
    subplot4.set_title(title4)
    subplot4.tick_params(axis='x', labelsize=10)
    figure4.subplots_adjust(bottom=0.3) # or whatever
    figure4.set_tight_layout(True)
    plot4 = FigureCanvasTkAgg(figure4, root)  # A tk.DrawingArea.
    plot4.draw()
    plot4.get_tk_widget().grid(row = 5, column = 4, pady = 2)    
    
    
# Set up the buttons
combo1 = ttk.Combobox(root)
combo1['values']= ("Netherlands", "Germany", "Belgium", "France", "Italy", "Spain", "United States", "World") #, "Top-5", "World", "Select"
combo1.current(0) #set the selected item
combo1.grid(row = 1, column = 0, pady = 2)

combo2 = ttk.Combobox(root)
combo2['values']= ("new_deaths", "new_deaths_smoothed",
                   "total_deaths", "icu_patients",
                   "new_cases", "new_cases_smoothed",
                   "total_cases", "total_cases_smoothed"
#                   ,"new_tests", "new_tests_smoothed", "positive_rate"
                  )

combo2.current(5) #set the selected item
combo2.grid(row = 1, column = 1, pady = 2) 
# iso_code, continent, location, date, total_cases, new_cases, new_cases_smoothed, total_deaths, new_deaths,
# new_deaths_smoothed, total_cases_per_million, new_cases_per_million, new_cases_smoothed_per_million, 
# total_deaths_per_million, new_deaths_per_million, new_deaths_smoothed_per_million, icu_patients, 
# icu_patients_per_million, hosp_patients, hosp_patients_per_million, weekly_icu_admissions, 
# weekly_icu_admissions_per_million, weekly_hosp_admissions, weekly_hosp_admissions_per_million, 
# total_tests, new_tests, new_tests_smoothed, total_tests_per_thousand, new_tests_per_thousand, 
# new_tests_smoothed_per_thousand, tests_per_case, positive_rate, tests_units, 
# stringency_index, population, population_density, median_age, aged_65_older, aged_70_older, 
# gdp_per_capita, extreme_poverty, cardiovasc_death_rate, diabetes_prevalence, 
# female_smokers, male_smokers, handwashing_facilities, hospital_beds_per_thousand, life_expectancy, human_development_index

combo6 = ttk.Combobox(root)
combo6['values']= ("absolute", "per million")
combo6.current(1) #set the selected item
combo6.grid(row = 1, column = 2, pady = 2) 

combo5 = ttk.Combobox(root)
combo5['values']= ("Netherlands", "Germany", "Belgium", "France", "Italy", "Spain", "United States") #, "Top-5", "World", "Select"
combo5.current(1) #set the selected item
combo5.grid(row = 2, column = 0, pady = 2) 

combo3 = ttk.Combobox(root)
combo3['values']= ("lin", "log", "smooth lin", "smooth log")
combo3.current(0) #set the selected item
combo3.grid(row = 2, column = 1, pady = 2) 

combo4 = ttk.Combobox(root)
combo4['values']= ("all", "month", "3 months")
combo4.current(2) #set the selected item
combo4.grid(row = 2, column = 2, pady = 2) 

button1 = tk.Button (root, text=' Create Charts ',command=create_charts, bg='palegreen2', font=('Arial', 11, 'bold')) 
button1.grid(row = 1, column = 3, pady = 2, rowspan=2) 

button3 = tk.Button (root, text='Exit', command=root.destroy, bg='lightsteelblue2', font=('Arial', 11, 'bold'))
button3.grid(row = 5, column = 3, pady = 2, rowspan=2) 

combo7 = ttk.Combobox(root)
combo7['values']= ("corona", "population", "population_density", "gdp_per_capita", "human_development_index", 
                   "male_smokers", "female_smokers", "aged_65_older", "aged_70_older", "extreme_poverty",
                   "cardiovasc_death_rate", "diabetes_prevalence", "life_expectancy")

combo7.current(0) #set the selected item
combo7.grid(row = 1, column = 4, pady = 2) 

combo8 = ttk.Combobox(root)
combo8['values']= ("top countries", "bottom countries")
combo8.current(0) #set the selected item
combo8.grid(row = 2, column = 4, pady = 2) 


button1.invoke()


# Main loop
root.mainloop()


# In[ ]:





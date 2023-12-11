# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CGzvmieDVU0fJ-nFAdxxsmoQh_EfqYPI
"""

import pandas as pd
import streamlit as st
import numpy as np
import requests
from datetime import date, datetime, timedelta
import sqlite_utils
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from PIL import Image

# EXTRACT THE SITES IN TOWER HAMLETS
#api is link between between us and database
req = requests.get("https://api.erg.ic.ac.uk/AirQuality/Information/MonitoringSiteSpecies/GroupName=towerhamlets/Json") #requests gets the info from the api
js = req.json() #json is like a python dictionary
sites = js['Sites']['Site'] #turns dictionary into list

#creating NO2 hourly table


EndDate = date.today() + timedelta(days = 1)
EndWeekDate = EndDate
StartWeekDate = EndDate - timedelta(weeks = 2)
StartDate = StartWeekDate - timedelta(days = 1)

while StartWeekDate > StartDate :
        for el in sites:
            def convert(list):
                list['@Value'] = float(list['@Value'])
                list['@Site'] = el['@SiteName']
                return list
            url = f'https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode={el["@SiteCode"]}/SpeciesCode=NO2/StartDate={StartWeekDate.strftime("%d %b %Y")}/EndDate={EndWeekDate.strftime("%d %b %Y")}/Json'
            print(url)
            req = requests.get(url, headers={'Connection':'close'}) #closes connection to the api
            print(req)
            j = req.json()
            # CLEAN SITES WITH NO DATA OR ZERO VALUE OR NOT NO2 (ONLY MEASURE AVAILABLE AT ALL SITES)
            filtered = [a for a in j['RawAQData']['Data'] if a['@Value'] != '' and a['@Value'] != '0' ] #removes zero and missing values
            if len(filtered) != 0:
                filtered = map(convert, filtered)
                filteredList = list(filtered)
                df= pd.DataFrame(filteredList)
                #db['NO2_hourly'].upsert_all(filteredList,pk=('@MeasurementDateGMT', '@Site')) #combo of update and insert, updates record if it already exists if not creates it
        EndWeekDate = StartWeekDate
        StartWeekDate = EndWeekDate - timedelta(weeks = 2)

#creating O3 hourly table

EndDate = date.today() + timedelta(days = 1)
EndWeekDate = EndDate
StartWeekDate = EndDate - timedelta(weeks = 6)
StartDate = StartWeekDate - timedelta(days = 1)

while StartWeekDate > StartDate :
        for el in sites:
            def convert(list):
                list['@Value'] = float(list['@Value'])
                list['@Site'] = el['@SiteName']
                return list
            url = f'https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode={el["@SiteCode"]}/SpeciesCode=O3/StartDate={StartWeekDate.strftime("%d %b %Y")}/EndDate={EndWeekDate.strftime("%d %b %Y")}/Json'
            print(url)
            req = requests.get(url, headers={'Connection':'close'}) #closes connection to the api
            print(req)
            j = req.json()
            # CLEAN SITES WITH NO DATA OR ZERO VALUE OR NOT NO2 (ONLY MEASURE AVAILABLE AT ALL SITES)
            filtered = [a for a in j['RawAQData']['Data'] if a['@Value'] != '' and a['@Value'] != '0' ] #removes zero and missing values 
            if len(filtered) != 0:
                filtered = map(convert, filtered)
                filteredList = list(filtered)
                #db['O3_hourly'].upsert_all(filteredList,pk=('@MeasurementDateGMT', '@Site')) #combo of update and insert, updates record if it already exists if not creates it 
        EndWeekDate = StartWeekDate
        StartWeekDate = EndWeekDate - timedelta(weeks = 6)

#set up streamlit page 

st.set_page_config(layout = "wide")
st.title("Air quality dashboard")
st.write('''This is a dashboard displaying air quality data in Tower Hamlets.
 This information has been obtained from the Environmental Research Group of Kings College
London (http://www.erg.kcl.ac.uk), using data from the London Air Quality Network
(http://www.londonair.org.uk). This information is licensed under the terms of the Open
Government Licence. 
  ''')

st_autorefresh(interval=30*60*1000, key="api_update") #set to autorefresh every 30 mins

def get_image(path:str)->Image:
    image = Image.open(path)
    return image

image = get_image("logo.PNG") # path of the file
st.sidebar.image(image, use_column_width=True)
st.sidebar.header(":black[Filter your data]")

pollutant= st.sidebar.selectbox('Choose a pollutant', options= ('NO2', 'Ozone'))

#%%

#Make NO2 page

if pollutant == 'NO2':
    st.subheader('Nitrogen dioxide (NO2)')
    st.write('''Nitrogen dioxide (NO2) is a gas that is mainly produced during the combustion of fossil fuels, along with nitric oxide (NO).
    Short-term exposure to concentrations of NO2 can cause inflammation of the airways and increase susceptibility to respiratory infections and to allergens. 
    NO2 can also exacerbate the symptoms of those already suffering from lung or heart conditions, and cause changes to the environment such as soil chemistry.''')
    
    st.write('''The Air Quality Standards Regulations 2010 require that the annual mean concentration of NO2 must not exceed 40 µg/m3 and that there should be no more than 18
    exceedances of the hourly mean limit value (concentrations above 200 µg/m3) in a single year.''')

    fig.update_layout(
        title={
            'text': 'Line plot showing hourly NO2 measurements from active sensors in Tower Hamlets','xanchor': 'left',
            'yanchor': 'top','x':0.05,'y':0.98},
        xaxis_title='Measurement Date',
        yaxis_title='NO<sub>2</sub> Concentration (µg/m<sup>3</sup>)',
        legend_title_text= '', 
        font=dict(size= 17)
    )
    
    fig.update_xaxes(title_font=dict(size=22), tickfont=dict(size=18))
    fig.update_yaxes(title_font=dict(size=22), tickfont=dict(size=18))
    
    #print("plotly express hovertemplate:", fig.data[0].hovertemplate)
    
    fig.update_traces(hovertemplate='<b>Measurement time (GMT) = </b>%{x}<br><b>Value = </b>%{y}<extra></extra>')
    
    fig.update_layout(hoverlabel = dict(
                    font_size = 16))
    
    fig.add_hline(y=40,line_dash='dot')
    
    #fig.add_annotation(x=20,y=40, text='Maximum target concentration', showarrow=False,yshift=10)
    
    fig.show()
    
    st.plotly_chart(fig, theme=None)

#make ozone page

if pollutant == 'Ozone':
    st.subheader('Ozone (O3)')
    st.write('''Ozone (O3) is a gas which is damaging to human health and can trigger inflammation of the respiratory tract, eyes, nose and throat as well as asthma attacks. 
    In addition, ozone can have adverse effects on the environment through oxidative damage to vegetation including crops.''')
    
    st.write('''The Air Quality Standards Regulations 2010 set the target that the 8-hour mean concentrations of O3 should not exceed 100 µg/m3 more than 10 times per year.''')

    fig.update_layout(
        title={
            'text': 'Line plot showing hourly O3 measurements from active sensors in Tower Hamlets',
            'xanchor': 'left',
            'yanchor': 'top',
            'x': 0.05,
            'y': 0.98
        },
        xaxis_title='Measurement Date',
        yaxis_title='O<sub>3</sub> Concentration (µg/m<sup>3</sup>)',
        legend_title_text='',
        font=dict(size=17)
    )

    fig.update_xaxes(title_font=dict(size=22), tickfont=dict(size=18))
    fig.update_yaxes(title_font=dict(size=22), tickfont=dict(size=18))

    #print("plotly express hovertemplate:", fig.data[0].hovertemplate)

    fig.update_traces(hovertemplate='<b>Measurement time (GMT) = </b>%{x}<br><b>Value = </b>%{y}<extra></extra>')

    fig.update_layout(hoverlabel = dict(
                font_size = 16))

    #fig.add_hline(y=40,line_dash='dot')

    #fig.add_annotation(x=20,y=40, text='Maximum target concentration', showarrow=False,yshift=10)

    fig.show()

    st.plotly_chart(fig, theme=None)    

    st.write(''' There are currently no active O3 sensors in Tower Hamlets with the most recent measurement of O3 being on 24/2 
                            at Blackwall
        ''')

# DRAFT
# df.head()

# #set up streamlit page

# st.set_page_config(layout = "wide")

# st.title("Air quality dashboard")
# st.write('''This is a dashboard displaying air quality data in Tower Hamlets.
#  This information has been obtained from the Environmental Research Group of Kings College
# London (http://www.erg.kcl.ac.uk), using data from the London Air Quality Network
# (http://www.londonair.org.uk). This information is licensed under the terms of the Open
# Government Licence.
#   ''')

# st_autorefresh(interval=30*60*1000, key="api_update") #set to autorefresh every 30 mins

# st.subheader('Nitrogen dioxide (NO2)')
# st.write('''Nitrogen dioxide (NO2) is a gas that is mainly produced during the combustion of fossil fuels, along with nitric oxide (NO).
#      Short-term exposure to concentrations of NO2 can cause inflammation of the airways and increase susceptibility to respiratory infections and to allergens.
#      NO2 can also exacerbate the symptoms of those already suffering from lung or heart conditions, and cause changes to the environment such as soil chemistry.''')

# st.write('''The Air Quality Standards Regulations 2010 require that the annual mean concentration of NO2 must not exceed 40 µg/m3 and that there should be no more than 18
#      exceedances of the hourly mean limit value (concentrations above 200 µg/m3) in a single year.''')

# fig = px.line(df, x= '@MeasurementDateGMT', y= '@Value', color='@Site',width=1200, height= 700)

# fig.update_layout(title={
#             'text': 'Line plot showing hourly NO2 measurements from active sensors in Tower Hamlets','xanchor': 'left',
#             'yanchor': 'top','x':0.05,'y':0.98},
#                             xaxis_title='Measurement Date',
#                             yaxis_title='NO<sub>2</sub> Concentration (µg/m<sup>3</sup>)',
#                             #legend=dict(orientation="h", entrywidth=250,
#                             #yanchor="bottom", y=1.02, xanchor="right", x=1),
#                             legend_title_text= '', font=dict(size= 17)
#                             )

# fig.update_xaxes(title_font=dict(size=22), tickfont=dict(size=18))
# fig.update_yaxes(title_font=dict(size=22), tickfont=dict(size=18))

# fig.update_traces(hovertemplate='<b>Measurement time (GMT) = </b>%{x}<br><b>Value = </b>%{y}<extra></extra>')

# fig.update_layout(hoverlabel = dict(
#                 font_size = 16))

# fig.add_hline(y=40,line_dash='dot')

#             #fig.add_annotation(x=20,y=40, text='Maximum target concentration', showarrow=False,yshift=10)

# fig.show()

# st.plotly_chart(fig, theme=None)

# def get_image(path:str)->Image:
#     image = Image.open(path)
#     return image

# image = get_image("LBTH_banner.PNG") # path of the file
# st.image(image)

import pandas as pd
import numpy as np
import requests
import streamlit as st
import datetime
import json
import base64
import plotly
import plotly.express as px
from tabulate import tabulate
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt

st.markdown("<h1 style='text-align: center; color: #2f54eb;'>Preludd ML Challenge</h1>", unsafe_allow_html=True)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


lottie_url = "https://assets5.lottiefiles.com/packages/lf20_yzoqyyqf.json"
# lottie_json = load_lottieurl(lottie_url)
# st_lottie(lottie_json, height=320)


"""
Aggregated data for individual dates chosen are shown below
"""

# Load dataset
df = pd.read_csv("sample.csv")


cols = df.columns

df["date1"] = pd.to_datetime(df["date"])
df["date1"] = df['date1'].dt.strftime('%m-%d-%Y')

df['time1'] = pd.to_datetime(df['time'],format= '%H:%M:%S').dt.time
df['hour'] = pd.to_datetime(df['time'],format= '%H:%M:%S').dt.hour


st.sidebar.header('Please select required filters')
manu = st.sidebar.multiselect('Select', df["manufacturer"].unique())
date = st.sidebar.date_input('start date', [datetime.date(2019,11,6), datetime.date(2019,11,10)])
start_time = st.sidebar.time_input('Start Time', datetime.time(12,15))
end_time = st.sidebar.time_input('End Time', datetime.time(16,30))

agg = pd.DataFrame()


if st.sidebar.button('Show Data'):
    df_new = df[(df["manufacturer"].isin(manu))
                    & (df["date1"] >= date[0].strftime('%d-%m-%Y'))
                    & (df["date1"] <= date[1].strftime('%d-%m-%Y'))
                    & (df['time1'] >= start_time)
                    & (df['time1'] <= end_time)]

    mccs = str(list(df_new["mcc"].unique())).strip('[]')

    agg["transaction_count"] = df_new.groupby(['date1'])['transaction_count'].first()
    agg["debits_amount"] = df_new.groupby(['date1'])['debits_amount'].first()
    agg["credits_amount"] = df_new.groupby(['date1'])['credits_amount'].first()
    agg["debits_reversal_amount"] = df_new.groupby(['date1'])['debits_reversal_amount'].first()
    agg["debits_number"] = df_new.groupby(['date1'])['debits_number'].first()
    agg["credits_number"] = df_new.groupby(['date1'])['credits_number'].first()
    agg["debits_reversal_number"] = df_new.groupby(['date1'])['debits_reversal_number'].first()
    agg["non_completed_number"] = df_new.groupby(['date1'])['non_completed_number'].first()

    categories = ["Total number of Transactions: ", "Total amount: ", "Total debit amount: ", "Total credit amount: ",
                  "Total debit-reversal amount: ", "Total number of debit transactions: ",
                  "Total number of credit transactions: ", "Total number of debit-reversal transactions: ",
                  "Total number of non-completed transactions: "]
    values = [agg["transaction_count"].sum(), df_new["amount"].sum(), agg["debits_amount"].sum(), agg["credits_amount"].sum(),
              agg["debits_reversal_amount"].sum(), agg["debits_number"].sum(), agg["credits_number"].sum(),
              agg["debits_reversal_number"].sum(), agg["non_completed_number"].sum()]


    tables = pd.DataFrame(
        {
            "Categories": categories,
            "Values": values
        }
    )
    tables.set_index('Categories', inplace=True)

    """
    ### Summary of transaction details for the selected input details.
    """

    st.markdown(tabulate(tables, tablefmt="pipe", headers="keys"), unsafe_allow_html=True)
    st.write("The MCCs included are ", mccs, ".")

    """
    ### Summary of transaction details for the selected input details in individual date level.
    """
    st.dataframe(agg)

    """
    # Dataframe:
    ### The dataframe after applying all the filters is as follows.
    """

    st.dataframe(df_new)

    csv = df_new.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">Download Data as CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

    hour_data = pd.DataFrame()
    hour_data["transaction_count"] = df_new.groupby(["hour"])["transaction_count"].sum()
    fig1 = px.line(hour_data, x=hour_data.index, y="transaction_count", title='Transaction Count over hours in selected dates', template="simple_white")


    st.plotly_chart(fig1)

else:
    st.write("Please choose the filters and click 'Show data'")



# CricAnalytics – Interactive Cricket Dashboard

**Live demo:** [https://cricanalytics-tee2bs8wtajpvy4evjahwv.streamlit.app/](https://cricanalytics-tee2bs8wtajpvy4evjahwv.streamlit.app/)

## Project Overview

CricAnalytics is an end-to-end data analytics project that transforms IPL ball-by-ball data into an interactive dashboard. It showcases real-world data engineering and visualization techniques.

## Key Features

- **Batter Analysis** – Runs, strike rate, dot ball percentage, boundaries (4s/6s), filter by opposition
- **Bowler Analysis** – Wickets, economy rate, dot balls bowled
- **Match Progression** – Total runs by over (selectable innings)
- **Team Filter** – Analyse performance of any IPL team

## Tools

- **Data processing:** Python, Pandas
- **Visualisation:** Plotly
- **Dashboard:** Streamlit
- **Deployment:** Streamlit Cloud
- **Version control:** GitHub

## What is Demonstrated

- Merging multiple datasets 
- Calculating cricket-specific metrics 
- Building an interactive web app with zero frontend experience
- Deploying a live data product

## How to Run Locally

```bash
git clone https://github.com/abrarhsnt/CricAnalytics.git
cd CricAnalytics
pip install -r requirements.txt
streamlit run app.py

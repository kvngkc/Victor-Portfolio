# Bellabeat Smart Device Analysis
**Google Data Analytics Capstone — Case Study 2**

> *How can a wellness company play it smart?*

---

## Overview

This project analyses publicly available Fitbit tracker data to surface consumer behaviour insights for **Bellabeat** — a health-focused smart device company targeting women. The goal is to identify usage patterns in activity, sleep, and weight tracking that can sharpen Bellabeat's marketing strategy for new user acquisition.

The dataset covers **35 Fitbit users** across **March–May 2016**, sourced from two Kaggle export periods and combined into a single clean dataset.

---

## Project Structure

```
Case Study 2/
├── archive/                     # Raw Fitbit CSV exports (two collection periods)
├── processed_data/
│   ├── daily_merged.csv         # Cleaned daily activity + sleep + weight (1,373 rows)
│   ├── daily_engineered.csv     # Feature-engineered daily dataset (activity/sleep tiers)
│   ├── hourly_merged.csv        # Cleaned hourly steps, calories & intensities (46,008 rows)
│   └── hourly_engineered.csv    # Hourly dataset with derived time columns
├── data_processing.py           # ETL pipeline — cleans and merges raw CSVs
├── bellabeat_analysis.ipynb     # Jupyter analysis notebook (Analyse phase)
├── app.py                       # Streamlit interactive dashboard
└── Case Study 2 (...).pdf       # Original case study brief
```

---

## How to Run

### 1. Process the raw data
```bash
python data_processing.py
```
Reads from `archive/`, deduplicates, merges daily and hourly tables, and writes to `processed_data/`.

### 2. Run the analysis notebook
Open `bellabeat_analysis.ipynb` in Jupyter and run all cells. This performs feature engineering (activity tiers, sleep tiers, wear consistency) and exports the engineered CSVs used by the dashboard.

### 3. Launch the dashboard
```bash
streamlit run app.py
```
Opens an interactive Streamlit app with four tabs: User Engagement, Sleep & Health Correlation, Hourly Rhythms, and Marketing Recommendations.

---

## Key Findings

| Insight | Detail |
|---|---|
| **Low step counts** | Average daily steps: 7,247 — below the 10,000 active threshold |
| **Sedentary majority** | 36% of tracked days fall in the sedentary (<5k steps) tier |
| **Sleep deficit** | Most users fail to meet the NSF 7–9 hour recommendation |
| **Sedentary–sleep link** | Strong negative correlation (−0.53) between sedentary minutes and sleep duration |
| **Peak activity** | 12–2 PM lunch spike and 5–7 PM post-work peak are the highest activity windows |
| **Weekend shift** | Users sleep +28 mins longer on weekends while step count slightly dips |
| **Low weight tracking** | Only 13 of 35 users logged weight; 90%+ of entries were typed manually |

---

## Dependencies

```
pandas
numpy
plotly
streamlit
jupyter
```

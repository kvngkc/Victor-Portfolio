import os
import pandas as pd
import numpy as np

# Define input paths
p1_dir = "archive/mturkfitbit_export_3.12.16-4.11.16/Fitabase Data 3.12.16-4.11.16"
p2_dir = "archive/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16"
output_dir = "processed_data"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def to_snake_case(df):
    """Convert dataframe columns to snake_case."""
    df.columns = (
        df.columns.str.replace(r'(?<!^)(?=[A-Z])', '_', regex=True)
        .str.lower()
        .str.replace('__', '_')
    )
    return df

print("=== STARTING DATA CLEANING & MERGING PIPELINE ===")

# ==========================================
# 1. PROCESS DAILY ACTIVITY
# ==========================================
print("\n[1/5] Processing Daily Activity...")
da1 = pd.read_csv(os.path.join(p1_dir, "dailyActivity_merged.csv"))
da2 = pd.read_csv(os.path.join(p2_dir, "dailyActivity_merged.csv"))

# Concatenate P1 and P2
da_combined = pd.concat([da1, da2], ignore_index=True)
da_combined = to_snake_case(da_combined)

# Rename date column and format it
da_combined = da_combined.rename(columns={'activity_date': 'date'})
da_combined['date'] = pd.to_datetime(da_combined['date'], format='%m/%d/%Y').dt.date

# Remove duplicates
dup_count = da_combined.duplicated(subset=['id', 'date']).sum()
if dup_count > 0:
    print(f"  Removing {dup_count} duplicate rows from daily activity...")
    da_combined = da_combined.drop_duplicates(subset=['id', 'date'])

print(f"  Total daily activity rows: {len(da_combined)} (Unique IDs: {da_combined['id'].nunique()})")


# ==========================================
# 2. PROCESS SLEEP
# ==========================================
print("\n[2/5] Processing Daily Sleep...")

# Load P2 sleep day (official daily data)
sleep2_official = pd.read_csv(os.path.join(p2_dir, "sleepDay_merged.csv"))
sleep2_official = to_snake_case(sleep2_official)
sleep2_official = sleep2_official.rename(columns={'sleep_day': 'date'})
# Format date (strip time portion since sleepDay is always 12:00:00 AM)
sleep2_official['date'] = pd.to_datetime(sleep2_official['date'], format='%m/%d/%Y %I:%M:%S %p').dt.date

# Generate P1 daily sleep from minuteSleep_merged.csv
print("  Generating March-April daily sleep from minute sleep records...")
min_sleep1 = pd.read_csv(os.path.join(p1_dir, "minuteSleep_merged.csv"))
min_sleep1 = to_snake_case(min_sleep1)
min_sleep1['datetime'] = pd.to_datetime(min_sleep1['date'], format='%m/%d/%Y %I:%M:%S %p')

# Group by log_id to find wake up time and sleep metrics
log_summary = min_sleep1.groupby(['id', 'log_id']).agg(
    wakeup_time=('datetime', 'max'),
    total_minutes_in_bed=('value', 'count'),
    minutes_asleep=('value', lambda x: (x == 1).sum())
).reset_index()

# Set sleep date based on wake up date
log_summary['date'] = log_summary['wakeup_time'].dt.date

# Aggregate logs by id and date (to handle multiple sleeps on the same day)
sleep1_computed = log_summary.groupby(['id', 'date']).agg(
    total_sleep_records=('log_id', 'count'),
    total_minutes_asleep=('minutes_asleep', 'sum'),
    total_time_in_bed=('total_minutes_in_bed', 'sum')
).reset_index()

# Combine P1 and P2 sleep datasets
sleep_combined = pd.concat([sleep1_computed, sleep2_official], ignore_index=True)

# Remove duplicate records
dup_sleep = sleep_combined.duplicated(subset=['id', 'date']).sum()
if dup_sleep > 0:
    print(f"  Removing {dup_sleep} duplicate rows from daily sleep...")
    sleep_combined = sleep_combined.drop_duplicates(subset=['id', 'date'])

print(f"  Total daily sleep rows: {len(sleep_combined)} (Unique IDs: {sleep_combined['id'].nunique()})")


# ==========================================
# 3. PROCESS WEIGHT LOGS
# ==========================================
print("\n[3/5] Processing Weight Logs...")
w1 = pd.read_csv(os.path.join(p1_dir, "weightLogInfo_merged.csv"))
w2 = pd.read_csv(os.path.join(p2_dir, "weightLogInfo_merged.csv"))

w_combined = pd.concat([w1, w2], ignore_index=True)
w_combined = to_snake_case(w_combined)
w_combined = w_combined.rename(columns={'date': 'date_time'})
# Convert date_time and extract date portion
w_combined['date_time'] = pd.to_datetime(w_combined['date_time'], format='%m/%d/%Y %I:%M:%S %p')
w_combined['date'] = w_combined['date_time'].dt.date

# Deduplicate by keeping the first log if multiple exist on the same day
w_combined = w_combined.sort_values(by=['id', 'date_time'])
dup_w = w_combined.duplicated(subset=['id', 'date']).sum()
if dup_w > 0:
    print(f"  Removing {dup_w} duplicate/subsequent logs per day from weight...")
    w_combined = w_combined.drop_duplicates(subset=['id', 'date'], keep='first')

# Drop unused columns
w_combined = w_combined.drop(columns=['date_time', 'log_id'])

print(f"  Total daily weight rows: {len(w_combined)} (Unique IDs: {w_combined['id'].nunique()})")


# ==========================================
# 4. MERGE DAILY DATASETS (MAXIMIZE SAMPLE SIZES)
# ==========================================
print("\n[4/5] Merging Daily Data...")
# Use LEFT join to keep all daily activity rows (highest user coverage)
daily_merged = pd.merge(da_combined, sleep_combined, on=['id', 'date'], how='left')
daily_merged = pd.merge(daily_merged, w_combined, on=['id', 'date'], how='left')

# Format date column back to string for easier sharing/loading
daily_merged['date'] = daily_merged['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

print(f"  Merged Daily shape: {daily_merged.shape}")
print(f"  Missing values check:")
print(f"    Sleep data missing: {daily_merged['total_minutes_asleep'].isna().sum()} rows")
print(f"    Weight data missing: {daily_merged['weight_kg'].isna().sum()} rows")

# Save merged daily data
daily_out_path = os.path.join(output_dir, "daily_merged.csv")
daily_merged.to_csv(daily_out_path, index=False)
print(f"  Saved Daily dataset to: {daily_out_path}")


# ==========================================
# 5. PROCESS HOURLY METRICS
# ==========================================
print("\n[5/5] Processing Hourly Metrics (Steps, Calories, Intensities)...")
# Load and concat Steps
hs1 = pd.read_csv(os.path.join(p1_dir, "hourlySteps_merged.csv"))
hs2 = pd.read_csv(os.path.join(p2_dir, "hourlySteps_merged.csv"))
hs_combined = pd.concat([hs1, hs2], ignore_index=True)
hs_combined = to_snake_case(hs_combined)

# Load and concat Calories
hc1 = pd.read_csv(os.path.join(p1_dir, "hourlyCalories_merged.csv"))
hc2 = pd.read_csv(os.path.join(p2_dir, "hourlyCalories_merged.csv"))
hc_combined = pd.concat([hc1, hc2], ignore_index=True)
hc_combined = to_snake_case(hc_combined)

# Load and concat Intensities
hi1 = pd.read_csv(os.path.join(p1_dir, "hourlyIntensities_merged.csv"))
hi2 = pd.read_csv(os.path.join(p2_dir, "hourlyIntensities_merged.csv"))
hi_combined = pd.concat([hi1, hi2], ignore_index=True)
hi_combined = to_snake_case(hi_combined)

# Merge Hourly data
hourly_merged = pd.merge(hs_combined, hc_combined, on=['id', 'activity_hour'], how='inner')
hourly_merged = pd.merge(hourly_merged, hi_combined, on=['id', 'activity_hour'], how='inner')

# Parse datetime
hourly_merged['activity_hour'] = pd.to_datetime(hourly_merged['activity_hour'], format='%m/%d/%Y %I:%M:%S %p')
# Format as ISO string
hourly_merged['activity_hour'] = hourly_merged['activity_hour'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Deduplicate
dup_h = hourly_merged.duplicated(subset=['id', 'activity_hour']).sum()
if dup_h > 0:
    print(f"  Removing {dup_h} duplicate rows from hourly activity...")
    hourly_merged = hourly_merged.drop_duplicates(subset=['id', 'activity_hour'])

print(f"  Hourly shape: {hourly_merged.shape} (Unique IDs: {hourly_merged['id'].nunique()})")

# Save merged hourly data
hourly_out_path = os.path.join(output_dir, "hourly_merged.csv")
hourly_merged.to_csv(hourly_out_path, index=False)
print(f"  Saved Hourly dataset to: {hourly_out_path}")

print("\n=== PIPELINE SUCCESSFULLY COMPLETED ===")

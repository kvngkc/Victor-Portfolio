# Project Change-Log: Cyclistic Q1 2026 Data Analysis

This document tracks all operations, changes, and cleaning procedures applied to the Cyclistic Q1 2026 bike-share dataset in chronological order.

---

### [2026-06-13] Step 1: Project Initialization & Notebook Setup
* **Action:** Restructured the Jupyter Notebook [case_study_1.ipynb](file:///C:/Users/KC/Projects/Case%20Study%201/case_study_1.ipynb).
* **Rationale:** Created a clean environment with Markdown annotations explaining the analytical framework.
* **Libraries:** Configured automatic imports and validation for `pandas`, `glob`, and `os`.

### [2026-06-13] Step 2: Data Merging & Datetime Formatting
* **Action:** Combined the monthly data from the `cyclistic_2026_q1_data` directory.
  * *Included Files:* January, February, March, and April 2026 CSV datasets.
* **Transformations:**
  * Read each CSV file into Pandas.
  * Standardized the text-based datetime columns (`started_at` and `ended_at`) by casting them into Pandas `datetime64` objects.
  * Concatenated all DataFrames together into a unified set using `pd.concat` (resetting the index to maintain a single continuous sequence).
* **Output:** Saved the comprehensive dataset to `cyclistic_2026_q1_merged.csv`.

### [2026-06-13] Step 3: Pre-Cleaning Data Audit
* **Action:** Wrote an audit suite in the notebook to inspect the merged dataset.
* **Checks Conducted:**
  * Calculated duplicate `ride_id` rows.
  * Counted missing (`NaN`) values for all columns.
  * Audited datetime logic by calculating trip duration (in seconds) and checking for negative values, zero values, trips < 1 minute, and trips > 24 hours.
  * Audited station name strings for test/maintenance keywords (e.g. "test", "temp", "maintenance", "hq", "base").
  * Inspected unique category labels for spelling or capitalization discrepancies.

### [2026-06-13] Step 4: Data Cleaning Operations
* **Action:** Implemented data cleaning cells to sanitize the dataset.
* **Transformations Applied:**
  * **Duplicate Removal:** Dropped rows with duplicated `ride_id` values to ensure uniqueness.
  * **Categorical Alignment:** Cleaned strings in `rideable_type` and `member_casual` by stripping leading/trailing whitespace and converting all letters to lowercase.
  * **Station Name Formatting:** Stripped leading/trailing whitespace from `start_station_name` and `end_station_name`.
  * **Test Data Filtering:** Removed any ride records associated with test, temporary, or maintenance stations (any name matching `test|temp|maintenance|hq|base`).
  * **Trip Duration Filtering:** Restricted trip durations to at least 1 minute (60 seconds) and at most 24 hours (86,400 seconds). This removed accidental starts, docking errors, and potential lost/stolen bikes.
  * **Coordinates Validation:** Dropped rows missing start/end latitude or longitude coordinates.
  * **Missing Station Imputation:** Rather than dropping rows with missing station names (common for electric bikes which can lock anywhere on-street), labeled them as `"On-Street (Dockless)"` and set IDs to `"DOCKLESS"`. This keeps representation for electric bike rides.
  * **Sorting:** Sorted the final cleaned dataset chronologically by `started_at` to facilitate time-series analysis.
* **Output:** Saved the final clean dataset as `cyclistic_2026_q1_clean.csv`.

### [2026-06-13] Step 5: Post-Cleaning Validation
* **Action:** Added code cell validation to verify cleanup results.
* **Checks Conducted:**
  * Verified that final dataset duplicates in `ride_id` is exactly `0`.
  * Verified coordinate null counts are exactly `0`.
  * Verified station name null counts are exactly `0`.
  * Verified minimum trip duration is >= 60 seconds and maximum is <= 24 hours.
  * Outputted a sample preview of the final dataset to verify correct formatting.

### [2026-06-13] Step 6: Calculated Columns Added (Ride Length & Day of Week)
* **Action:** Appended code cells to compute ride durations and trip start days.
* **Transformations Applied:**
  * **Ride Length Calculation:** Subtracted `started_at` from `ended_at` and converted the time difference to minutes as a float (`ride_length`).
  * **Day of Week Extraction:** Extracted the name of the day of the week (Monday to Sunday) from `started_at` (`day_of_week`).
* **Output:** Saved the updated dataset back to `cyclistic_2026_q1_clean.csv`.

### [2026-06-13] Step 7: Sorted Clean Dataset by Ride Length
* **Action:** Appended code cell to sort the cleaned dataset.
* **Transformations Applied:**
  * **Sorting:** Sorted the entire dataset by `ride_length` in ascending order (from shortest rides to longest rides). This makes it easier to analyze trip length distributions.
* **Output:** Overwrote `cyclistic_2026_q1_clean.csv` with the sorted rows.

### [2026-06-13] Step 8: Descriptive Analysis & Pivot Tables
* **Action:** Appended code cells to conduct descriptive analysis.
* **Transformations Applied:**
  * **Group Comparison:** Grouped the cleaned dataset by `member_casual` to calculate the mean, median, minimum, and maximum of `ride_length`.
  * **Weekly Profiles:** Created pivot tables organizing both average ride duration and total ride count by user type and day of the week (chronologically ordered from Monday to Sunday).
* **Output:** Printed tables of descriptive statistics directly inside the Jupyter Notebook.

### [2026-06-13] Step 9 Visualizations: Descriptive Charts
* **Action:** Added a visualization cell (`step9-viz-code`) to plot three charts from the Step 9 descriptive analysis.
* **Charts Added:**
  * **Chart 1 — Average & Median Ride Length Comparison:** Grouped bar chart (`sns.barplot`) comparing mean and median `ride_length` (minutes) for members vs. casual users.
  * **Chart 2 — Weekly Ride Duration Profile:** Line chart (`plt.plot`) showing average ride duration by day of the week (Mon–Sun) for each user type, with markers and a dashed grid.
  * **Chart 3 — Weekly Ride Counts:** Grouped bar chart (`sns.barplot`) showing the total number of rides per day of the week for each user type.
* **Bug Fixed:** Corrected `import matplotlib as plt` → `import matplotlib.pyplot as plt`. The incorrect alias caused `plt.figure()` to raise a `NameError` in this cell and all downstream cells. *(Fixed 2026-06-13)*

### [2026-06-13] Step 10 — Insight 1: Bike Type Preferences
* **Action:** Added code cell (`insight1-code`) to analyze rideable type preferences by user segment.
* **Method:**
  * Grouped `df_clean` by `['member_casual', 'rideable_type']` and counted rides per combination using `.size().unstack(fill_value=0)`.
  * Calculated each bike type's share as a percentage of that user type's total rides.
  * Plotted a stacked 100% bar chart (classic bike vs. electric bike) for members and casual users.
* **Note:** Previously erroring (`NameError: name 'plt' is not defined`) due to the incorrect import alias in the Step 9 viz cell. Resolved by fixing that import. *(Fixed 2026-06-13)*

### [2026-06-13] Step 10 — Insight 2: Hourly Usage Patterns (Rush Hour vs. Leisure Peak)
* **Action:** Added code cell (`insight2-code`) to plot ride frequency by hour of day.
* **Method:**
  * Extracted the start hour from `started_at` into a new column `hour` using `.dt.hour`.
  * Grouped by `['member_casual', 'hour']` and counted rides, then unstacked into a wide pivot table.
  * Plotted a line chart (hours 0–23 on x-axis) with one line per user type to reveal commuter vs. leisure peak patterns.
* **Bug Fixed:** Added explicit `pd.to_datetime(df_clean['started_at'])` conversion at the top of the cell to ensure `.dt.hour` works regardless of whether `df_clean` was loaded from CSV (as a string column) by a prior cell. *(Fixed 2026-06-13)*

### [2026-06-13] Step 10 — Insight 3: Round Trip Behavior
* **Action:** Added code cell (`insight3-code`) to measure the rate of round trips per user type.
* **Method:**
  * Filtered out all dockless (`"On-Street (Dockless)"`) rides to focus on station-to-station trips.
  * Created a boolean column `is_round_trip` (True when `start_station_name == end_station_name`).
  * Calculated the percentage of round trips per user type using `.value_counts(normalize=True)`.
  * Plotted a bar chart showing the round-trip percentage for members vs. casual users.

### [2026-06-13] Step 10 — Insight 4: Ride Distance & Speed (Haversine)
* **Action:** Added code cell (`insight4-code`) to estimate straight-line displacement and average riding speed.
* **Method:**
  * Implemented a `haversine_dist()` function to calculate the great-circle distance (km) between start and end GPS coordinates.
  * Added `distance_km` column to `df_clean`.
  * Derived `speed_kmh` as `distance_km / (ride_length / 60)` (converting minutes to hours).
  * Plotted side-by-side bar charts: mean distance (km) and mean speed (km/h) for members vs. casual users.

### [2026-06-13] Step 10 — Insight 5: Top 5 Routes Profile
* **Action:** Added code cell (`insight5-code`) to identify the most-ridden station-to-station routes per user type.
* **Method:**
  * Filtered out dockless rides to retain only named-station trips.
  * Constructed a `route` string column as `"<start_station_name> to <end_station_name>"`.
  * For each user type (member, casual), found the top 5 routes by ride count using `.value_counts().head(5)`.
  * Plotted two horizontal bar charts (stacked vertically) showing the top 5 routes and their ride volumes for each user group.

---

### [2026-06-13] Bug Fixes & Full Verification Run
* **Action:** Fixed two bugs identified during Step 9 / Step 10 development and re-ran all affected cells to confirm successful execution.
* **Fixes Applied:**
  * **`step9-viz-code`:** Changed `import matplotlib as plt` to `import matplotlib.pyplot as plt`. This was the root cause of `NameError: name 'plt' is not defined` in the Step 9 viz cell and Insight 1.
  * **`insight2-code`:** Added `df_clean['started_at'] = pd.to_datetime(df_clean['started_at'])` before the `.dt.hour` extraction to guard against `started_at` being a raw string when loaded from CSV by a prior cell.
* **Verification:** All six previously unrun/erroring cells now execute successfully:
  * `step9-viz-code` — 3 descriptive charts rendered.
  * `insight1-code` — Bike type preference stacked bar chart rendered.
  * `insight2-code` — Hourly ride distribution line chart rendered.
  * `insight3-code` — Round trip behavior bar chart rendered.
  * `insight4-code` — Distance & speed side-by-side bar charts rendered.
  * `insight5-code` — Top 5 routes horizontal bar charts rendered.

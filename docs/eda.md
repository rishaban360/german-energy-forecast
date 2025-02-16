# Exploratory Data Analysis (EDA)

### Introduction

This analysis explores the German energy load forecasting system's performance, focusing on patterns, accuracy, and potential areas for improvement. We analyze high-frequency load data (15-minute intervals) to understand both the underlying demand patterns and forecast quality.

First step is to load the data and check the basic information and quality.

```python
print("=== Actual Load Data ===")
print(f"Total data points: {len(actual_load)}")
print(f"Time range: {actual_load.index.min()} to {actual_load.index.max()}")
print("\nDataset Shape:", actual_load.shape)
print(f"Time frequency: {actual_load.index.to_series().diff().mode()[0]}")
print(f"Missing values: {actual_load.isnull().sum()}")
print(f"Duplicate timestamps: {actual_load.index.duplicated().sum()}\n")
```

```
Output:
=== Actual Load Data ===
Total data points: 69972
Time range: 2023-02-14 12:00:00+01:00 to 2025-02-13 10:45:00+01:00

Dataset Shape: (69972,)
Time frequency: 0 days 00:15:00
Missing values: 0
Duplicate timestamps: 0
```

!!! note "Data Quality"

      This initial assessment suggests the dataset is well-maintained and suitable for detailed time series analysis. The absence of missing values and duplicates means we can proceed with analysis without needing extensive data cleaning or imputation.

Now let's understand the load patterns and forecast accuracy

## Understand Data Distribution

### Load Distribution

![Load Distribution](../assets/images/eda/histogram_hour_load.png)

!!! info "**Load Distribution**"

      - Mean Load: 52,789 MW (shown by the red dashed line)

- X-axis: Shows the load values in Megawatts (MW), ranging from about 35,000 MW to 75,000 MW
- Y-axis: Shows the frequency (how often each load value occurs)

!!! note "Key insights"

      The distribution is **bimodal (two peaks)**:

      - First peak around 45,000-50,000 MW
      - Second peak around 55,000-60,000 MW

      This likely represents:

      - Lower peak: Typical nighttime/weekend loads
      - Higher peak: Typical working hours/weekday loads

Bimodal distribution is common in electricity demand patterns due to:

- Residential and commercial usage
- Industrial operations
- Seasonal variations
- Day-of-week effects

Let us check the distribution of load by day and night as well as by weekday and weekend.

![Load Distribution by Day and Night](../assets/images/eda/weekend_vs_weekday_densityplot.png)

!!! note "Key Insights"

      - The bimodal pattern is primarily driven by day/night differences
      - Weekday/weekend differences add another layer of variation:
        - Weekdays have higher overall demand
        - Weekends have more consistent (less variable) demand
      - For forecasting, this suggests:
        - Time of day is the primary factor
        - Day of week is a secondary but important factor
        - Need to account for both patterns in the model

### Daily Load Profile

![Daily Pattern](../assets/images/eda/load_hourly_distribution.png)

This box plot shows electricity load patterns across 24 hours of the day in Germany.

Each box shows the load distribution for that hour:

- Box: 25th to 75th percentile
- Whiskers: Min/max values
- Middle line: Median load

!!! note "Key Insights"

      - Lowest demand: Early morning (3-5 AM) ~40-45k MW
      - Peak demand: Evening hours (18-20) ~60-65k MW
      - Business hours (8-18): Consistently high demand ~55-60k MW

      This pattern reflects typical daily electricity consumption with morning ramp-up, sustained business hours, and evening peak before night decline.

### Statistical summary by hour

![Statistical summary by hour](../assets/images/eda/statistical_summary_by_hour.png)

This statistical summary plot shows three key metrics of electricity load across 24 hours:

- Mean (green line): Average load for each hour
- Median (blue line): Middle value of load for each hour
- Mean + Standard Deviation (red dashed line): Shows variability

Daily pattern shows,

| Time Period | Pattern           | Load Range       |
| ----------- | ----------------- | ---------------- |
| 4-5 AM      | Lowest point      | ~42-45k MW       |
| 5-9 AM      | Morning ramp      | Sharp increase   |
| 10-12 AM    | Peak              | ~60k MW          |
| 12-18       | Afternoon plateau | Slight decline   |
| 19-20       | Evening peak      | Small bump       |
| After 20:00 | Night decline     | Gradual decrease |

The gap between mean and mean+std (red dashed line) indicates load variability at each hour, which is larger during business hours than at night.

### Weekly Load Pattern

![Weekly Pattern](../assets/images/eda/weekly_pattern.png)

The weekly load pattern shows distinct characteristics across different days:

!!! info "Load Ranges"

      - Weekday Range: ~35,000 MW to ~70,000 MW
      - Weekend Range: ~30,000 MW to ~65,000 MW
      - Consistent minimum loads across all days
      - Different maximum loads between weekdays and weekends

This weekly pattern suggests the need for:

- Separate modeling approaches for weekdays and weekends
- Special attention to Monday transitions
- Different load expectations for weekend operations
- Consideration of day-of-week in forecast models

## Anomaly Detection in Load Data

### Extreme Load Values Analysis

We identify extreme values using statistical methods and visualize them to understand their patterns and potential causes.

```python title="Extreme Loads Analysis"
extreme_analysis = analyze_extreme_loads(load_forecast_df)
```

```
output:

Extreme Load Analysis:
High threshold (99th percentile): 71649 MW
Low threshold (1st percentile): 35037 MW
Number of extreme high loads: 700
Number of extreme low loads: 700

```

![Extreme Loads](../assets/images/eda/extreme_loads.png)

!!! note "Key Insights"

      - Extreme high loads occur primarily in winter months (visible spikes in Jan 2024)
      - Extreme low loads cluster in summer months (Jul-Aug 2023, 2024)

      Seasonal pattern is clearly visible with:

      - Higher demand in winter
      - Lower demand in summer
      - More volatility during transition periods

This pattern suggests strong seasonal and weather-related influences on electricity demand.

### Holiday Impact Analysis

Analyzing how holidays affect load patterns and identifying anomalous holiday periods.

```python
# Code for holiday analysis
holiday_analysis = analyze_holiday_impact(load_forecast_df)
```

```
Output:

Holiday Impact Analysis:
Number of holidays: 1728

Average load on holidays: 43314 MW
Average load on normal days: 52918 MW
Difference: 9604 MW

```

![Holiday Impact](../assets/images/eda/holiday_impact_load.png)

## Temperature-Load Relationship Analysis

### Purpose

Investigated how temperature affects electricity load in Germany, focusing on daily and weekly patterns to identify key relationships and anomalies.

### Method

- Analyzed 17,509 hourly observations
- Examined correlations across different time periods
- Visualized load patterns across:

      - Hours (daily cycles)
      - Days (weekly patterns)
      - Temperature ranges
      - Temperature-load correlations

![Temperature-Load Anamoly](../assets/images/eda/Temperature_load_anamoly.png)

Here are the key insights from this Load vs Temperature scatter plot:

a. Distribution Pattern:

- Forms a distinctive fan shape
- Higher load variability at lower temperatures
- Converging pattern at higher temperatures

b. Time-of-Day Effect (shown by colors):

- Purple/dark (night hours): Lower loads (30-40k MW)
- Green/yellow (day hours): Higher loads (50-70k MW)
- Clear separation between day/night consumption

c. Temperature Range:

- Narrow band: 16-20°C
- Most concentrated around 18°C
- Load varies significantly (30-70k MW) even within this narrow temperature range

d. Load-Temperature Relationship:

- No strong linear relationship
- Higher loads possible at all temperatures
- Time of day appears more influential than temperature
- Suggests temperature alone is insufficient for load prediction

e. Clustering:

- Dense central cluster around 17.5-18.5°C
- Sparse points at temperature extremes
- Shows typical operating conditions

**Key Findings**

**Time Patterns**

- Peak loads: ~60,000 MW at 10 AM
- Lowest loads: ~42,000 MW at 3 AM
- Weekdays average 55,000 MW
- Weekends drop to 44,000-47,000 MW

**Temperature Impact**

- Overall negative correlation (-0.266)
- Colder temperatures → Higher loads
- Correlation varies by hour:
  - Morning: Strong negative (-0.4)
  - Afternoon: Positive (0.3)
  - Shows clear daily cycle

**Business Implications**

- Load prediction needs both temperature and time factors
- Weekend/weekday difference: ~10,000 MW
- Temperature effect varies significantly by time of day

### Temperature Analysis Results:

![Temperature-Load Relationship](../assets/images/eda/temperature_load_relationships.png)

Data Overview

- N = 17,509 observations
- Complete dataset: No missing values
- Temperature range: T ∈ [15.93°C, 20.32°C]
- Load range: L ∈ [28,031 MW, 76,582 MW]

### Statistical Relationships

1. Correlation Analysis

- Global correlations:
  - Pearson (r) = -0.266
  - Spearman (ρ) = -0.288
- Hourly correlations (rₕ):
  ```
  r₂ = 0.390  (2 AM)
  r₁ = 0.374  (1 AM)
  r₀ = 0.369  (12 AM)
  ```

2. Load Distribution by Temperature (μ ± σ)

```
T ≤ 17.51°C: L = 54,845 ± 7,594 MW  (n=3507)
17.51°C < T ≤ 17.90°C: L = 55,351 ± 8,875 MW  (n=3506)
17.90°C < T ≤ 18.18°C: L = 53,721 ± 8,971 MW  (n=3506)
18.18°C < T ≤ 18.48°C: L = 52,377 ± 9,297 MW  (n=3501)
T > 18.48°C: L = 47,316 ± 8,763 MW  (n=3489)
```

3. Peak Load Analysis

Daily peaks (MW):

```
L₁₀ₕᵣ = 59,874 ± 7,312
L₉ₕᵣ = 59,537 ± 7,507
L₁₁ₕᵣ = 59,402 ± 7,608
```

4. Weekly Pattern

```
Weekdays: L̄ᵥᵥ ≈ 55,375 MW
Weekend: L̄ᵥₑ ≈ 46,082 MW
ΔL = L̄ᵥᵥ - L̄ᵥₑ ≈ 9,293 MW
```

5. Temperature Quartile Effects

```
Q₂₅: ΔL = -2,968 MW  (T = 17.51°C)
Q₅₀: ΔL = -4,334 MW  (T = 17.90°C)
Q₇₅: ΔL = -6,294 MW  (T = 18.48°C)
```

!!! note "Key Findings"

      - Temperature-Load relationship varies significantly by hour (r ∈ [-0.4, 0.3])
      - Weekly cycle dominates load patterns (ΔL ≈ 9.3 GW)
      - Daily peaks occur consistently at 10:00 (L̄ ≈ 60 GW)
      - Lower temperatures correlate with higher loads (negative correlation)

## Forecast Performance Analysis

### Accuracy Overview

![Actual vs Forecast](../assets/images/eda/scatter.png)

!!! info "Scatter plot insights"

      - **Strong correlation** between actual and forecast
      - Systematic underestimation at peak loads
      - Better accuracy at lower demand levels
      - Most points within ±2000 MW of perfect prediction

### Error Analysis

![Error Analysis](../assets/images/eda/error_analysis.png)

!!! info "Error patterns"

      - Mean Absolute Error: ~1000 MW
      - Larger errors during rapid load changes
      - Systematic underestimation during peaks
      - Best accuracy during stable periods

## Conclusion: Load Pattern Analysis for Feature Engineering

The analysis of Germany's electricity consumption data revealed several interesting patterns that help explain how and when people use electricity. The data shows that electricity usage follows predictable daily and weekly rhythms - much like our own routines. During weekdays, consumption peaks around 10 AM when businesses are in full swing, while early morning hours (around 3 AM) see the lowest usage. Weekends tell a different story, with significantly lower consumption (about 9,300 MW less) as many businesses are closed.

What surprised me most was that last week's electricity usage is actually better at predicting today's usage than yesterday's data or even the temperature. Speaking of temperature, its relationship with electricity usage isn't as straightforward as I initially thought - it matters more during certain times of the day than others. Holidays also have a clear impact, showing patterns similar to weekends.

These insights helped me identify which features would be most valuable for building a forecasting model. Instead of just using temperature and recent usage data, I learned that incorporating time-based patterns (especially weekly cycles) and special calendar days (like holidays) would be crucial for accurate predictions.

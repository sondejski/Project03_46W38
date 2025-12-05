Project 3 – Wind Resource Assessment (Horns Rev)

This is my assignment for wind resource analysis using ERA5 data.  
The goal is to load wind data from several NetCDF files and calculate different wind characteristics at a chosen location inside the Horns Rev area.

I tried to keep the code as simple and readable as possible.

---

## What the project does

- Loads and merges multiple ERA5 NetCDF files (1997–2008)
- Computes wind speed and wind direction from u- and v-components
- Interpolates wind data to a chosen location (inside the data grid)
- Computes wind speed at different heights using the power-law profile
- Fits a Weibull distribution to wind speed time series
- Plots:
  - wind speed distribution (histogram + Weibull fit)
  - wind rose diagram
- Calculates AEP (Annual Energy Production) for:
  - NREL 5 MW turbine  
  - NREL 15 MW turbine  
- Allows analysis for selected years (default 1997–2008)

---

Classes Implemented
WindResourceModel
(located in src/wind_resource.py)

This is the main class of the project.
It stores the list of NetCDF files and provides functions to analyse the wind data.

Key methods:

load_data() → loads and merges all NetCDF files

subset_years() → selects a range of years

get_time_series_at_location() → interpolates to a chosen lat/lon

power_law_profile() → estimates wind at any height

fit_weibull() → finds Weibull scale and shape

plot_speed_distribution() → histogram + Weibull

plot_wind_rose() → wind rose diagram

compute_aep() → calculates AEP for a turbine

<img width="1121" height="154" alt="image" src="https://github.com/user-attachments/assets/0b14bb4e-2cc9-4cc7-85a7-7e76a8b25e72" /># Project 3 – Wind Resource Assessment (Horns Rev)

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

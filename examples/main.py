import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.wind_resource import WindResourceModel


def main():
    # Paths (adjust if your structure is different)
    nc_files = [
        os.path.join("inputs", "1997-1999.nc"),
        os.path.join("inputs", "2000-2002.nc"),
        os.path.join("inputs", "2003-2005.nc"),
        os.path.join("inputs", "2006-2008.nc"),
    ]

    model = WindResourceModel(nc_files)
    model.load_data()

    # Example site inside the box (approx Horns Rev 1)
    lat = 55.55
    lon = 7.90

    # 1) Compute wind speed / direction at 10 m and 100 m
    ts_10m = model.get_time_series_at_location(lat, lon, height=10)
    ts_100m = model.get_time_series_at_location(lat, lon, height=100)

    print("10 m time series:", ts_10m)
    print("100 m time series:", ts_100m)

    # 2) Power law example: speed at 90 m (hub height 5 MW)
    speed_90m = model.get_speed_at_height_power_law(
        lat=lat, lon=lon, z_target=90.0, ref_height=100
    )
    print("Example speed at 90 m:", speed_90m)

    # 3) Weibull fit and histogram at 100 m
    speeds_100m = ts_100m["speed"].values
    model.plot_speed_distribution(
        speeds_100m,
        title="Wind speed distribution at 100 m",
        show=True,
    )

    # 4) Wind rose at 100 m
    dirs_100m = ts_100m["direction"].values
    model.plot_wind_rose(
        dirs_100m,
        title="Wind rose at 100 m",
        show=True,
    )

    # 5) AEP for NREL 5 MW (hub height 90 m) for year 2000
    power_curve_5mw = os.path.join("inputs", "NREL_Reference_5MW_126.csv")
    aep_5mw_2000 = model.compute_aep(
        lat=lat,
        lon=lon,
        hub_height=90.0,
        power_curve_csv=power_curve_5mw,
        year=2000,
    )
    print(f"AEP NREL 5 MW (year 2000) = {aep_5mw_2000:.1f} MWh")

    # 6) AEP for NREL 15 MW (hub height 150 m) for year 2000
    power_curve_15mw = os.path.join("inputs", "NREL_Reference_15MW_240.csv")
    aep_15mw_2000 = model.compute_aep(
        lat=lat,
        lon=lon,
        hub_height=150.0,
        power_curve_csv=power_curve_15mw,
        year=2000,
    )
    print(f"AEP NREL 15 MW (year 2000) = {aep_15mw_2000:.1f} MWh")


if __name__ == "__main__":
    main()

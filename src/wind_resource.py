import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import gamma


class WindResourceModel:
    """
    Simple class for wind resource assessment.
    """

    def __init__(self, nc_files):
        """
        nc_files: list of paths to NetCDF files.
        """
        self.nc_files = nc_files
        self.ds = None

    # -------------------------
    # Data loading
    # -------------------------

    def load_data(self):
        """
        Load and merge all NetCDF files along time dimension.
        """
        datasets = []
        for path in self.nc_files:
            ds = xr.open_dataset(path, engine="netcdf4")
            datasets.append(ds)
        self.ds = xr.concat(datasets, dim="time").sortby("time")
        return self.ds

    def _ensure_data_loaded(self):
        if self.ds is None:
            self.load_data()

    def subset_years(self, start_year=1997, end_year=2008):
        """
        Select data between start_year and end_year.
        """
        self._ensure_data_loaded()
        start = f"{start_year}-01-01"
        end = f"{end_year}-12-31"
        return self.ds.sel(time=slice(start, end))

    # -------------------------
    # Wind speed and direction
    # -------------------------

    @staticmethod
    def _uv_to_speed_dir(u, v):
        """
        Convert u, v to wind speed and direction (deg).
        """
        speed = np.sqrt(u ** 2 + v ** 2)
        direction = (np.degrees(np.arctan2(-u, -v)) + 360.0) % 360.0
        return speed, direction

    def get_speed_direction_at_height(
        self,
        height=10,
        start_year=1997,
        end_year=2008,
    ):
        """
        Wind speed and direction for whole grid at given height.
        """
        ds_sel = self.subset_years(start_year, end_year)
        u = ds_sel[f"u{height}"]
        v = ds_sel[f"v{height}"]
        speed, direction = self._uv_to_speed_dir(u, v)
        out = xr.Dataset(
            {
                "speed": speed,
                "direction": direction,
            },
            coords=ds_sel.coords,
        )
        return out

    def get_time_series_at_location(
        self,
        lat,
        lon,
        height=10,
        start_year=1997,
        end_year=2008,
    ):
        """
        Time series at one location using interpolation.
        """
        ds_sel = self.subset_years(start_year, end_year)
        u = ds_sel[f"u{height}"].interp(latitude=lat, longitude=lon)
        v = ds_sel[f"v{height}"].interp(latitude=lat, longitude=lon)
        speed, direction = self._uv_to_speed_dir(u, v)
        return xr.Dataset({"speed": speed, "direction": direction})

    # -------------------------
    # Power law vertical profile
    # -------------------------

    @staticmethod
    def power_law_profile(speed_ref, z_ref, z_target, alpha=0.14):
        """
        Power law profile: V(z) = V_ref * (z/z_ref)^alpha.
        """
        factor = (z_target / z_ref) ** alpha
        return speed_ref * factor

    def get_speed_at_height_power_law(
        self,
        lat,
        lon,
        z_target,
        ref_height=100,
        alpha=0.14,
        start_year=1997,
        end_year=2008,
    ):
        """
        Wind speed at z_target using power law.
        """
        ts_ref = self.get_time_series_at_location(
            lat=lat,
            lon=lon,
            height=ref_height,
            start_year=start_year,
            end_year=end_year,
        )
        speed_target = self.power_law_profile(
            ts_ref["speed"], z_ref=ref_height, z_target=z_target, alpha=alpha
        )
        return speed_target

    # -------------------------
    # Weibull fitting
    # -------------------------

    @staticmethod
    def fit_weibull(speeds):
        """
        Fit Weibull distribution (method of moments).
        Returns (A, k).
        """
        arr = np.asarray(speeds)
        arr = arr[~np.isnan(arr)]
        if arr.size == 0:
            return np.nan, np.nan
        mean = arr.mean()
        std = arr.std()
        if mean == 0:
            return np.nan, np.nan
        k = (std / mean) ** -1.086
        A = mean / gamma(1.0 + 1.0 / k)
        return A, k

    @staticmethod
    def weibull_pdf(v, A, k):
        v = np.asarray(v)
        pdf = (k / A) * (v / A) ** (k - 1) * np.exp(-(v / A) ** k)
        return pdf

    def fit_weibull_at_location(
        self,
        lat,
        lon,
        height=100,
        start_year=1997,
        end_year=2008,
    ):
        """
        Fit Weibull at given location and height.
        """
        ts = self.get_time_series_at_location(
            lat=lat,
            lon=lon,
            height=height,
            start_year=start_year,
            end_year=end_year,
        )
        speeds = ts["speed"].values
        return self.fit_weibull(speeds)

    def plot_speed_distribution(
        self,
        speeds,
        bins=30,
        title="Wind speed distribution",
        show=True,
        ax=None,
    ):
        """
        Plot histogram and fitted Weibull curve.
        """
        A, k = self.fit_weibull(speeds)
        if ax is None:
            fig, ax = plt.subplots()
        arr = np.asarray(speeds)
        arr = arr[~np.isnan(arr)]
        ax.hist(arr, bins=bins, density=True, alpha=0.6, label="data")
        if not np.isnan(A) and not np.isnan(k):
            v_plot = np.linspace(0.0, arr.max(), 100)
            pdf = self.weibull_pdf(v_plot, A, k)
            ax.plot(v_plot, pdf, label=f"Weibull (A={A:.2f}, k={k:.2f})")
        ax.set_xlabel("Wind speed [m/s]")
        ax.set_ylabel("Probability density")
        ax.set_title(title)
        ax.legend()
        if show:
            plt.show()
        return A, k

    def plot_speed_distribution_at_location(
        self,
        lat,
        lon,
        height=100,
        start_year=1997,
        end_year=2008,
        bins=30,
        title=None,
        show=True,
        ax=None,
    ):
        """
        Plot wind speed distribution at given location and height.
        """
        ts = self.get_time_series_at_location(
            lat=lat,
            lon=lon,
            height=height,
            start_year=start_year,
            end_year=end_year,
        )
        speeds = ts["speed"].values
        if title is None:
            title = f"Wind speed distribution at {height} m"
        return self.plot_speed_distribution(
            speeds=speeds,
            bins=bins,
            title=title,
            show=show,
            ax=ax,
        )

    # -------------------------
    # Wind rose
    # -------------------------

    def plot_wind_rose(
        self,
        directions_deg,
        n_sectors=16,
        title="Wind rose",
        show=True,
        ax=None,
    ):
        """
        Plot simple wind rose.
        """
        dirs = np.asarray(directions_deg)
        dirs = dirs[~np.isnan(dirs)]
        theta = np.deg2rad(dirs)
        sector_edges = np.linspace(0.0, 2.0 * np.pi, n_sectors + 1)
        counts, _ = np.histogram(theta, bins=sector_edges)
        frequencies = counts / counts.sum()
        theta_centers = (sector_edges[:-1] + sector_edges[1:]) / 2.0
        if ax is None:
            ax = plt.subplot(111, polar=True)
        width = 2.0 * np.pi / n_sectors
        ax.bar(theta_centers, frequencies, width=width, align="center", alpha=0.7)
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_title(title)
        if show:
            plt.show()

    def plot_wind_rose_at_location(
        self,
        lat,
        lon,
        height=100,
        start_year=1997,
        end_year=2008,
        n_sectors=16,
        title=None,
        show=True,
        ax=None,
    ):
        """
        Plot wind rose at given location and height.
        """
        ts = self.get_time_series_at_location(
            lat=lat,
            lon=lon,
            height=height,
            start_year=start_year,
            end_year=end_year,
        )
        dirs = ts["direction"].values
        if title is None:
            title = f"Wind rose at {height} m"
        self.plot_wind_rose(
            directions_deg=dirs,
            n_sectors=n_sectors,
            title=title,
            show=show,
            ax=ax,
        )

    # -------------------------
    # Turbine power and AEP
    # -------------------------

    @staticmethod
    def load_power_curve(csv_path):
        """
        Load power curve CSV.
        """
        df = pd.read_csv(csv_path)
        ws_col = [c for c in df.columns if "Wind Speed" in c][0]
        power_col = [c for c in df.columns if "Power" in c][0]
        ws = df[ws_col].values.astype(float)
        power = df[power_col].values.astype(float)
        return ws, power

    @staticmethod
    def interpolate_power(ws_values, ws_curve, power_curve):
        """
        Interpolate turbine power for given wind speeds.
        """
        return np.interp(ws_values, ws_curve, power_curve, left=0.0, right=0.0)

    def compute_aep(
        self,
        lat,
        lon,
        hub_height,
        power_curve_csv,
        year,
        alpha=0.14,
    ):
        """
        Compute AEP [MWh] for one turbine and one year.
        """
        ref_height = 100 if hub_height > 50 else 10
        speed_hub = self.get_speed_at_height_power_law(
            lat=lat,
            lon=lon,
            z_target=hub_height,
            ref_height=ref_height,
            alpha=alpha,
            start_year=year,
            end_year=year,
        )
        ws_curve, power_curve = self.load_power_curve(power_curve_csv)
        power_ts_kw = self.interpolate_power(speed_hub.values, ws_curve, power_curve)
        total_energy_kwh = np.sum(power_ts_kw)
        aep_mwh = total_energy_kwh / 1000.0
        return aep_mwh
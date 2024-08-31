import os
import streamlit as st
from skyfield.api import Topos, load, EarthSatellite
import requests
import pandas as pd
import numpy as np
from datetime import datetime

def get_cardinal_direction(azimuth_degrees):
    """
    Converts azimuth degrees to cardinal direction.
    """
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    index = int((azimuth_degrees + 22.5) // 45)
    return directions[index % 8]

def compute_ephemeris(satellite_url, latitude, longitude, start_date_utc, start_time, end_time, custom_tle=None):
    """
    Computes the ephemeris for the satellite.
    """
    try:
        ts = load.timescale()
        year, month, day = map(int, start_date_utc.split('-'))
        observer = Topos(latitude, longitude)
        start_hour, start_minute = start_time.hour, start_time.minute
        end_hour, end_minute = end_time.hour, end_time.minute
        start_datetime = datetime(year, month, day, start_hour, start_minute)
        end_datetime = datetime(year, month, day, end_hour, end_minute)
        total_minutes = int((end_datetime - start_datetime).total_seconds() // 60)
        times = ts.utc(year, month, day, [start_hour] * total_minutes, np.arange(start_minute, start_minute + total_minutes))

        # Fetch TLE data for custom satellite or use predefined URL
        if custom_tle:
            satellites = [EarthSatellite(custom_tle[1], custom_tle[2], custom_tle[0], ts)]
        else:
            r = requests.get(satellite_url)
            with open('satellite_data.txt', 'wb') as f:
                f.write(r.content)
            satellites = load.tle_file('satellite_data.txt')

        # Prepare the ephemeris data
        ephemeris_data = []
        for satellite in satellites:
            difference = satellite - observer
            for ti in times:
                topocentric = difference.at(ti)
                ra, dec, distance = topocentric.radec()
                alt, az, distance = topocentric.altaz()

                if alt.degrees > 0:  # Check if the satellite is above the horizon
                    azimuth_degrees = az.degrees
                    cardinal_direction = get_cardinal_direction(azimuth_degrees)
                    ephemeris_data.append({
                        "Date (UTC)": ti.utc_strftime('%Y-%m-%d %H:%M:%S'),
                        "R.A.": str(ra),
                        "Dec": str(dec),
                        "Altitude": f"{alt.degrees:.2f}°",
                        "Azimuth": f"{azimuth_degrees:.2f}° ({cardinal_direction})"
                    })

        # Convert ephemeris data to DataFrame for display
        ephemeris_df = pd.DataFrame(ephemeris_data)
        if not custom_tle:
            os.remove('satellite_data.txt')
        return ephemeris_df
    except Exception as e:
        st.error(f"Error computing ephemeris: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame on error

def fetch_custom_tle(satellite_name_or_id):
    """
    Fetches TLE data for a custom satellite by name or NORAD ID.
    """
    try:
        if satellite_name_or_id.isdigit():
            celestrak_url = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={satellite_name_or_id}'
        else:
            celestrak_url = f'https://celestrak.org/NORAD/elements/gp.php?NAME={satellite_name_or_id}&FORMAT=TLE'

        with st.spinner("Fetching TLE data..."):
            response = requests.get(celestrak_url)

        if response.status_code == 200 and len(response.text.splitlines()) >= 2:
            lines = response.text.splitlines()
            st.success("TLE data fetched successfully!")
            st.text(f"Name: {lines[0].strip()}\nTLE Line 1: {lines[1].strip()}\nTLE Line 2: {lines[2].strip()}")
            return lines[0].strip(), lines[1].strip(), lines[2].strip()  # Name, TLE line 1, TLE line 2
        else:
            st.error("TLE data could not be fetched. Please check the satellite name or NORAD ID.")
            return None
    except Exception as e:
        st.error(f"Error fetching TLE data: {str(e)}")
        return None

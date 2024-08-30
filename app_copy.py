import os
import streamlit as st
from skyfield.api import Topos, load, EarthSatellite
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import numpy as np
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# Function to convert azimuth degrees to cardinal direction
def get_cardinal_direction(azimuth_degrees):
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    index = int((azimuth_degrees + 22.5) // 45)
    return directions[index % 8]

# Function to get timezone in an abbreviated format
def get_abbreviated_timezone(timezone_str, dt):
    try:
        tz = pytz.timezone(timezone_str)
        return dt.astimezone(tz).tzname()
    except Exception as e:
        st.error(f"Error converting timezone: {str(e)}")
        return timezone_str  # Return the original string if conversion fails

# Generalized function to compute satellite ephemeris
def compute_ephemeris(satellite_url, latitude, longitude, start_date_utc, start_time, end_time, custom_tle=None):
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
            st.write("Using custom TLE data for satellite computation.")
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
                    # Convert Angle objects to string representations and add cardinal direction
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

# Fetch TLE data for custom satellite by name or NORAD ID
def fetch_custom_tle(satellite_name_or_id):
    try:
        # Correct URL formats for NORAD ID and satellite name
        if satellite_name_or_id.isdigit():
            # Fetch TLE by NORAD ID
            celestrak_url = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={satellite_name_or_id}'
        else:
            # Fetch TLE by satellite name
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

# Streamlit app
def main():
    st.title("Satellites Ephemeris Calculator")

    # Dropdown for satellite category selection
    satellite_categories = {
        'Starlink Generation 1': 'https://celestrak.org/NORAD/elements/supplemental/sup-gp.php?FILE=starlink&FORMAT=tle',
        'Starlink Generation 2': 'https://celestrak.org/NORAD/elements/supplemental/sup-gp.php?FILE=starlink&FORMAT=tle&VERSION=2',
        'OneWeb': 'https://celestrak.org/NORAD/elements/supplemental/sup-gp.php?FILE=oneweb&FORMAT=tle',
        'Kuiper': 'https://celestrak.org/NORAD/elements/supplemental/sup-gp.php?FILE=kuiper&FORMAT=tle',
        'Custom Satellite': None
    }
    satellite_type = st.selectbox("Select or Search Satellite", list(satellite_categories.keys()))

    custom_tle = None
    satellite_url = satellite_categories[satellite_type]

    # If custom satellite is selected, ask for satellite name or NORAD ID
    if satellite_type == 'Custom Satellite':
        satellite_name_or_id = st.text_input("Enter Satellite Name or NORAD ID:")
        if satellite_name_or_id:
            custom_tle = fetch_custom_tle(satellite_name_or_id)

    # Detect user's local time zone
    local_timezone = datetime.now().astimezone().tzinfo

    # Coordinates and time input
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            use_address = st.checkbox("Use Address to Set Location", value=False)
            if use_address:
                address = st.text_input("Enter Your Address:")
                if address:
                    # Add User-Agent to Nominatim geocoder
                    geolocator = Nominatim(user_agent="satellite-observation-app")
                    try:
                        location = geolocator.geocode(address, timeout=10)
                        if location:
                            latitude = location.latitude
                            longitude = location.longitude
                        else:
                            st.write("Could not find the location. Please enter a valid address.")
                    except Exception as e:
                        st.error(f"Error fetching location data: {str(e)}")
            else:
                st.write("Select your location on the map:")
                default_location = [37.7749, -122.4194]
                map_display = folium.Map(location=default_location, zoom_start=2)
                folium.Marker(default_location, tooltip="Default Location").add_to(map_display)
                map_data = st_folium(map_display, width=350, height=300)
                if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
                    latitude = map_data['last_clicked']['lat']
                    longitude = map_data['last_clicked']['lng']

        with col2:
            latitude = st.text_input("Latitude:", value=str(latitude) if 'latitude' in locals() else "")
            longitude = st.text_input("Longitude:", value=str(longitude) if 'longitude' in locals() else "")

            # Determine time zone from GPS coordinates
            if latitude and longitude:
                try:
                    tf = TimezoneFinder()
                    timezone_str = tf.timezone_at(lng=float(longitude), lat=float(latitude))
                    timezone = pytz.timezone(timezone_str)
                    # Display abbreviated timezone
                    current_time = datetime.now()
                    timezone_abbr = get_abbreviated_timezone(timezone_str, current_time)
                    st.write(f"Detected Time Zone: {timezone_str} ({timezone_abbr})")
                except Exception as e:
                    st.error(f"Error determining timezone: {str(e)}")
                    timezone = local_timezone
            else:
                timezone = local_timezone
                timezone_abbr = timezone.tzname(datetime.now())
                st.write(f"Using local time zone: {timezone} ({timezone_abbr})")

            start_date_local = st.date_input("Start Date (Local Time):")
            start_time_local = st.time_input("Start Time (Local Time):")
            end_time_local = st.time_input("End Time (Local Time):")

            # Convert local time to UTC
            start_datetime_local = datetime.combine(start_date_local, start_time_local)
            end_datetime_local = datetime.combine(start_date_local, end_time_local)
            start_datetime_utc = start_datetime_local.astimezone(pytz.utc)
            end_datetime_utc = end_datetime_local.astimezone(pytz.utc)

            st.write(f"Start Time in UTC: {start_datetime_utc.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"End Time in UTC: {end_datetime_utc.strftime('%Y-%m-%d %H:%M:%S')}")

            # Compute button
            compute_button = st.button("Compute Satellite Positions")

    # Align the table with the button
    if compute_button:
        if latitude and longitude and start_date_local:
            ephemeris_df = compute_ephemeris(
                satellite_url, float(latitude), float(longitude),
                start_datetime_utc.strftime('%Y-%m-%d'),
                start_datetime_utc.time(), end_datetime_utc.time(),
                custom_tle
            )
            if not ephemeris_df.empty:
                # Display the dataframe with use_container_width to match the app width
                st.dataframe(ephemeris_df, use_container_width=True)
            else:
                st.write("No visible satellites found for the specified time and location.")
        else:
            st.write("Please fill in all fields (latitude, longitude, and observation time).")

if __name__ == "__main__":
    main()

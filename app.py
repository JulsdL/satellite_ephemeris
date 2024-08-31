import os
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

from utils.satellite_utils import compute_ephemeris, fetch_custom_tle
from utils.timezone_utils import get_abbreviated_timezone

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

    # Coordinates and time input - Default to mobile-friendly single-column layout
    use_address = st.checkbox("Use Address to Set Location", value=False)
    if use_address:
        address = st.text_input("Enter Your Address:")
        if address:
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
        # Use an empty container to manage the map rendering
        map_placeholder = st.empty()
        with map_placeholder:
            default_location = [37.7749, -122.4194]
            map_display = folium.Map(location=default_location, zoom_start=2)
            folium.Marker(default_location, tooltip="Default Location").add_to(map_display)
            map_data = st_folium(map_display, width=350, height=300)
            if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
                latitude = map_data['last_clicked']['lat']
                longitude = map_data['last_clicked']['lng']

    # Latitude and Longitude input fields
    latitude = st.text_input("Latitude:", value=str(latitude) if 'latitude' in locals() else "")
    longitude = st.text_input("Longitude:", value=str(longitude) if 'longitude' in locals() else "")

    # Determine time zone from GPS coordinates
    if latitude and longitude:
        try:
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lng=float(longitude), lat=float(latitude))
            timezone = pytz.timezone(timezone_str)
            current_time = datetime.now()
            timezone_abbr = get_abbreviated_timezone(timezone_str, current_time)
            st.write(f"Detected Time Zone: {timezone_str} ({timezone_abbr})")
        except Exception as e:
            st.error(f"Error determining timezone: {str(e)}")
            timezone = local_timezone
    else:
        timezone = local_timezone
        timezone_str = str(timezone)
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

    compute_button = st.button("Compute Satellite Positions")

    # Align the table with the button
    if compute_button:
        if latitude and longitude and start_date_local:
            ephemeris_df = compute_ephemeris(
                satellite_url, float(latitude), float(longitude),
                start_datetime_utc.strftime('%Y-%m-%d'),
                start_datetime_utc.time(), end_datetime_utc.time(),
                timezone_str,  # Pass the timezone string to the function
                custom_tle
            )
            if not ephemeris_df.empty:
                st.dataframe(ephemeris_df, use_container_width=True)
            else:
                st.write("No visible satellites found for the specified time and location.")
        else:
            st.write("Please fill in all fields (latitude, longitude, and observation time).")

if __name__ == "__main__":
    main()

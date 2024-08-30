import streamlit as st
import pytz

def get_abbreviated_timezone(timezone_str, dt):
    """
    Converts the timezone string to an abbreviated format.
    """
    try:
        tz = pytz.timezone(timezone_str)
        return dt.astimezone(tz).tzname()
    except Exception as e:
        st.error(f"Error converting timezone: {str(e)}")
        return timezone_str  # Return the original string if conversion fails

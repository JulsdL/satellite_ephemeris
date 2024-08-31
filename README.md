---
title: Satellite Ephemeris Calculator
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: "1.24.1"
app_file: app.py
pinned: false
---

# 🌌 Satellite Ephemeris Calculator with Streamlit

Welcome to the **Satellite Ephemeris Calculator**! This application empowers users to track and observe satellites in real time from any location on Earth. It's perfect for astronomy enthusiasts, satellite observers, and anyone curious about the night sky.

## [![Streamlit App](https://img.shields.io/badge/Streamlit-Online-green?style=for-the-badge)]

## 🚀 Features

- **Real-time Satellite Tracking:** Track satellites from various constellations like Starlink, OneWeb, and Kuiper.
- **Custom Satellite Search:** Enter specific satellite names or NORAD IDs to fetch their position.
- **Location Flexibility:** Enter your location manually, use your address, or click on the map to set your coordinates.
- **Time Zone Detection:** Automatically detects and displays your local time zone, with the flexibility to compute positions for different locations.
- **Beautiful and Responsive UI:** Designed with Streamlit for an interactive and user-friendly experience.

## 🌍 How It Works

1. **Select or Search a Satellite**: Choose from pre-defined satellite constellations or enter a custom satellite name/NORAD ID.
2. **Set Your Location**:
   - Use your address
   - Select a location on the map
   - Enter latitude and longitude manually
3. **Choose Observation Time**: Enter your observation window in local time.
4. **Compute Satellite Positions**: Click the button, and the app will display visible satellites with their respective coordinates.

## 🛠️ Installation

To run the app locally, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/satellite-ephemeris-calculator.git
   cd satellite-ephemeris-calculator
   ```

2. **Install the Requirements**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## 🧩 Project Structure

````plaintext
.
├── app.py                      # Main application file
├── utils
│   ├── satellite_utils.py      # Satellite-related utility functions
│   ├── timezone_utils.py       # Timezone conversion utilities
├── requirements.txt            # Python dependencies
├── README.md                   # Project README
└── .gitignore                  # Git ignore file

## 🔍 Dependencies

The app uses the following Python libraries:

    Streamlit: For creating the web application interface.
    Skyfield: For computing satellite positions and ephemeris.
    Geopy: To handle geocoding for address-based location input.
    Folium: For interactive maps.
    TimezoneFinder: For detecting time zones based on geographic coordinates.
    Pandas, NumPy, Requests, and others for data handling and HTTP requests.

install these with:

```bash
pip install -r requirements.txt
````

## 🌠 Usage

    Launch the App: Run the app using Streamlit and open it in your browser.
    Select a Satellite: Choose from the dropdown or enter a custom satellite.
    Set Your Location: Use the map, enter an address, or provide coordinates.
    Enter Time Range: Input the local time window for observation.
    Compute: Click the button to compute satellite positions and view the results!

## 🌟 Acknowledgements

Special thanks to:

    -Unistellar for inspiring the satellite observation campaign.
    -Franck Marchis for the ephemeris calculation code.
    -The developers of all the amazing open-source libraries used in this project.

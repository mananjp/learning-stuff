from tkinter import *
from PIL import Image, ImageTk
import requests
import json

# Initialize the Tkinter root window
root = Tk()
root.title("Weather")

# Set the icon of the window (ensure the image file exists)
try:
    root.iconphoto(True, ImageTk.PhotoImage(
        Image.open('D:/git/learning-stuff/image_view/logo.png').resize((32, 32), Image.Resampling.LANCZOS)))
except FileNotFoundError:
    print("Icon file not found, skipping setting icon.")

# Define the API key and base URL for WeatherAPI
api_key = "de91bf433e654941b0d161342243011"  # Replace with your actual API key

# Create Entry widget for city input
c = Entry(root)
c.grid(row=0, column=1, padx=10, pady=10)

# Create labels for displaying the weather data
weather_label = Label(root, text="Weather: ")
weather_label.grid(row=1, column=0, padx=10, pady=5)

temp_label = Label(root, text="Temperature: ")
temp_label.grid(row=2, column=0, padx=10, pady=5)

aqi_label = Label(root, text="AQI (PM2.5): ")
aqi_label.grid(row=3, column=0, padx=10, pady=5)

# Labels for forecast
forecast_label = Label(root, text="3-Day Forecast:")
forecast_label.grid(row=5, column=0, padx=10, pady=5)

forecast_day_1_label = Label(root, text="")
forecast_day_1_label.grid(row=6, column=0, padx=10, pady=5)

forecast_day_2_label = Label(root, text="")
forecast_day_2_label.grid(row=7, column=0, padx=10, pady=5)

forecast_day_3_label = Label(root, text="")
forecast_day_3_label.grid(row=8, column=0, padx=10, pady=5)

# Function to calculate AQI from PM2.5 using standard AQI categories and return the corresponding color
def calculate_aqi(pm2_5):
    if pm2_5 <= 12:
        return 50, "Good", "green"
    elif 12.1 <= pm2_5 <= 35.4:
        return 100, "Moderate", "yellow"
    elif 35.5 <= pm2_5 <= 55.4:
        return 150, "Unhealthy for Sensitive Groups", "orange"
    elif 55.5 <= pm2_5 <= 150.4:
        return 200, "Unhealthy", "red"
    elif 150.5 <= pm2_5 <= 250.4:
        return 300, "Very Unhealthy", "purple"
    else:
        return 400, "Hazardous", "brown"

# Function to fetch and update weather data and forecast
def submit():
    city = c.get()  # Get the city name from the Entry widget

    # Construct the API URL for current weather and forecast
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3&aqi=yes"

    try:
        # Try to fetch the weather data
        api_req = requests.get(url)

        # Check if the request was successful (status code 200)
        if api_req.status_code == 200:
            api = api_req.json()

            # Check if the 'current' data exists
            if "current" not in api:
                weather_label.config(text="Error: Invalid city name")
                temp_label.config(text="")
                aqi_label.config(text="")
                forecast_day_1_label.config(text="")
                forecast_day_2_label.config(text="")
                forecast_day_3_label.config(text="")
                return

            # Extract current weather details
            weather_description = api["current"]["condition"]["text"]
            temperature_celsius = api["current"]["temp_c"]
            pm2_5 = api["current"]["air_quality"].get("pm2_5", None)  # Using .get() to handle missing values

            # Handle missing or None values for AQI or PM2.5
            if pm2_5 is None:
                aqi = "N/A"
                aqi_level = "N/A"
                color = "white"  # Default color if AQI is not available
            else:
                aqi, aqi_level, color = calculate_aqi(pm2_5)

            # Update the current weather labels
            weather_label.config(text=f"Weather: {weather_description}")
            temp_label.config(text=f"Temperature: {temperature_celsius}°C")
            aqi_label.config(text=f"AQI (PM2.5): {aqi} ({aqi_level})")

            # Change the background color based on the AQI level
            root.config(bg=color)

            # Extract 3-day forecast details
            forecast = api["forecast"]["forecastday"]

            # Update the 3-day forecast labels
            forecast_day_1_label.config(text=f"Day 1: {forecast[0]['date']} - {forecast[0]['day']['condition']['text']} - {forecast[0]['day']['avgtemp_c']}°C")
            forecast_day_2_label.config(text=f"Day 2: {forecast[1]['date']} - {forecast[1]['day']['condition']['text']} - {forecast[1]['day']['avgtemp_c']}°C")
            forecast_day_3_label.config(text=f"Day 3: {forecast[2]['date']} - {forecast[2]['day']['condition']['text']} - {forecast[2]['day']['avgtemp_c']}°C")

        else:
            # Handle error if the API call fails
            weather_label.config(text=f"Error: Unable to fetch weather data. Status code {api_req.status_code}")
            temp_label.config(text="")
            aqi_label.config(text="")
            forecast_day_1_label.config(text="")
            forecast_day_2_label.config(text="")
            forecast_day_3_label.config(text="")
            print(f"Error fetching weather data: Status code {api_req.status_code}. Please check your API key and try again.")

    except Exception as e:
        # Handle exception if the request fails
        weather_label.config(text=f"Error: {e}")
        temp_label.config(text="")
        aqi_label.config(text="")
        forecast_day_1_label.config(text="")
        forecast_day_2_label.config(text="")
        forecast_day_3_label.config(text="")
        print(f"Error: {e}")

# Create the Submit button
submit_btn = Button(root, text="Submit", command=submit)
submit_btn.grid(row=0, column=2, padx=10, pady=10)

# Create the city label and position it in the grid
city_label = Label(root, text="City: ")
city_label.grid(row=0, column=0, padx=10, pady=10)

# Create the quit button
quit_btn = Button(root, text="Quit", command=root.quit)
quit_btn.grid(row=1, column=2, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()

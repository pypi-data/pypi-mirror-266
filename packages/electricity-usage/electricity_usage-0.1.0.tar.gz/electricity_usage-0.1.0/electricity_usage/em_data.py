import requests
import os

# This method utilizes the zone and API_KEY to retrieve information from the electricity maps API.
def get_power_data(zone, API_KEY):
    url = f"https://api.electricitymap.org/v3/power-breakdown/latest?zone={zone}"
    headers = {
        "auth-token": API_KEY
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200: 
        response_data = response.json()
        power_production_total = response_data.get('powerProductionTotal')
        power_consumption_total = response_data.get('powerConsumptionTotal')
        return power_production_total, power_consumption_total
    else:
        print(f"Error: {response.status_code}")
        print("Electricity Maps isn't responding. Please check your authentication token.")
        return None, None

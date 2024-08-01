import requests
from datetime import datetime
import os

# Your personal data. Used by Nutritionix to calculate calories.
GENDER = "male"
WEIGHT_KG = 84
HEIGHT_CM = 180
AGE = 32

# Nutritionix APP ID and API Key. Actual values are stored as environment variables.
APP_ID = os.getenv("ENV_NIX_APP_ID")
API_KEY = os.getenv("ENV_NIX_API_KEY")

exercise_endpoint = "https://trackapi.nutritionix.com/v2/natural/exercise"

def get_exercise_data(exercise_text):
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": API_KEY,
    }

    parameters = {
        "query": exercise_text,
        "gender": GENDER,
        "weight_kg": WEIGHT_KG,
        "height_cm": HEIGHT_CM,
        "age": AGE
    }

    try:
        response = requests.post(exercise_endpoint, json=parameters, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def log_to_sheet(data):
    today_date = datetime.now().strftime("%d/%m/%Y")
    now_time = datetime.now().strftime("%X")
    
    sheet_endpoint = os.getenv("ENV_SHEETY_ENDPOINT")
    GOOGLE_SHEET_NAME = "workout"

    for exercise in data["exercises"]:
        sheet_inputs = {
            GOOGLE_SHEET_NAME: {
                "date": today_date,
                "time": now_time,
                "exercise": exercise["name"].title(),
                "duration": exercise["duration_min"],
                "calories": exercise["nf_calories"]
            }
        }

        try:
            sheet_response = requests.post(
                sheet_endpoint,
                json=sheet_inputs,
                auth=(
                    os.getenv("ENV_SHEETY_USERNAME"),
                    os.getenv("ENV_SHEETY_PASSWORD"),
                )
            )
            sheet_response.raise_for_status()
            print(f"Sheety Response: \n {sheet_response.text}")
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")

def get_past_logs():
    sheet_endpoint = os.getenv("ENV_SHEETY_ENDPOINT")
    try:
        sheet_response = requests.get(
            sheet_endpoint,
            auth=(
                os.getenv("ENV_SHEETY_USERNAME"),
                os.getenv("ENV_SHEETY_PASSWORD"),
            )
        )
        sheet_response.raise_for_status()
        logs = sheet_response.json()
        print(f"Past Exercise Logs: \n {logs}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def main():
    while True:
        print("1. Log new exercise")
        print("2. View past exercise logs")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            exercise_text = input("Tell me which exercises you did: ")
            exercise_data = get_exercise_data(exercise_text)
            if exercise_data:
                log_to_sheet(exercise_data)
        elif choice == "2":
            get_past_logs()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


import requests
import random
from itertools import permutations
import numpy as np 
#Google Places API key
API_KEY = '' # add Google Places API key

def fetch_data_for_place(place):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"tourist attractions in {place}",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        activities = [{"name": result["name"], "place_id": result["place_id"]} for result in results]
        categorized_activities = {
            "morning": activities[:5],
            "afternoon": activities[5:10],
            "evening": activities[10:15]
        }
        return categorized_activities
    else:
        print("Error fetching data from the API:", response.status_code)
        return None
def fetch_distance_matrix(origins, destinations):
    endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    origins = [f"place_id:{place_id}" for place_id in origins]
    destinations = [f"place_id:{place_id}" for place_id in destinations]
    
    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "key": API_KEY
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        results = response.json()
        if results.get("status") == "OK":
            rows = results.get("rows", [])
            distance_matrix = []
            for row in rows:
                distances = [element["distance"]["value"] for element in row["elements"] if element["status"] == "OK"]
                distance_matrix.append(distances)
            return np.array(distance_matrix)
        else:
            print(f"API returned an error: {results.get('status')}")
            return None
    else:
        print(f"Error fetching distance matrix data from the API: {response.status_code}")
        print(f"Response content: {response.text}")
        return None
    
def prioritize_activities(data, interests):

    prioritized_data = {}
    for time_of_day, activities in data.items():
        prioritized_data[time_of_day] = random.sample(activities, len(activities))  # Randomly shuffle activities
    return prioritized_data

def create_itinerary(data, days):
    """
    Generate a draft itinerary.
    """
    itinerary = {}
    for day in range(1, days + 1):
        itinerary[f"Day {day}"] = {
            "Morning": data["morning"][day % len(data["morning"])],
            "Afternoon": data["afternoon"][day % len(data["afternoon"])],
            "Evening": data["evening"][day % len(data["evening"])]
        }
    return itinerary

def tsp_optimization(locations, distance_matrix):
    n = len(locations)
    min_distance = float('inf')
    optimal_route = None

    for route in permutations(range(n)):
        current_distance = sum(distance_matrix[route[i]][route[i + 1]] for i in range(n - 1))
        current_distance += distance_matrix[route[-1]][route[0]]  # Return to starting point
        
        if current_distance < min_distance:
            min_distance = current_distance
            optimal_route = route

    return optimal_route, min_distance

def reorder_activities(data, optimal_route):
    reordered_data = {}
    all_activities = [item for sublist in data.values() for item in sublist]
    
    if optimal_route is None:
        return data
    
    optimal_activities = [all_activities[i] for i in optimal_route]
    
    reordered_data['morning'] = optimal_activities[:5]
    reordered_data['afternoon'] = optimal_activities[5:10]
    reordered_data['evening'] = optimal_activities[10:15]
    
    return reordered_data

def get_user_feedback(itinerary):
    print("\nPlease rate each activity from 1 (dislike) to 5 (love):")
    feedback = {}
    for day, activities in itinerary.items():
        for time, activity in activities.items():
            while True:
                try:
                    rating = int(input(f"{day} - {time} - {activity['name']}: "))
                    if 1 <= rating <= 5:
                        feedback[(day, time)] = rating
                        break
                    else:
                        print("Please enter a number between 1 and 5.")
                except ValueError:
                    print("Please enter a valid number.")
    return feedback

def adjust_itinerary(itinerary, feedback, data):
    all_activities = [item for sublist in data.values() for item in sublist]
    unused_activities = [activity for activity in all_activities if activity['name'] not in [act for day in itinerary.values() for act in day.values()]]
    
    for (day, time), rating in feedback.items():
        if rating <= 2:  # If the user dislikes the activity
            if unused_activities:
                new_activity = unused_activities.pop(0)
                itinerary[day][time] = new_activity['name']
                print(f"Replaced {itinerary[day][time]} with {new_activity['name']} for {day} - {time}")
            else:
                print(f"No more alternative activities available to replace {itinerary[day][time]} for {day} - {time}")
    
    return itinerary

def fetch_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_address,opening_hours,price_level",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json().get("result", {})
        return {
            "name": result.get("name"),
            "rating": result.get("rating"),
            "address": result.get("formatted_address"),
            "opening_hours": result.get("opening_hours", {}).get("weekday_text"),
            "price_level": result.get("price_level")
        }
    else:
        print(f"Error fetching place details: {response.status_code}")
        return None
    
def display_activity_details(activity):
    print(f"  Name: {activity['name']}")
    print(f"  Rating: {activity['rating']}")
    print(f"  Address: {activity['address']}")
    print(f"  Price Level: {'$' * activity['price_level'] if activity['price_level'] else 'N/A'}")
    if activity['opening_hours']:
            print("  Opening Hours:")
            for hours in activity['opening_hours']:
                print(f"    {hours}")
    print()



def main():
    place = input("Enter a place: ")
    days = int(input("Enter number of days: "))
    interests = input("Enter interests (comma-separated): ").split(',')

    data = fetch_data_for_place(place)
    
    if not data:
        print(f"No data found for {place}. Please provide a different place.")
        return

    places = [activity["name"] for category in data.values() for activity in category]
    place_ids = [activity["place_id"] for category in data.values() for activity in category]

    distance_matrix = fetch_distance_matrix(place_ids, place_ids)
    
    if distance_matrix is None:
        print("Failed to fetch distance matrix data. Proceeding without optimization.")
        reordered_data = data
    else:
        optimal_route, _ = tsp_optimization(places, distance_matrix)
        reordered_data = reorder_activities(data, optimal_route)

    prioritized_data = prioritize_activities(reordered_data, interests)

    itinerary = create_itinerary(prioritized_data, days)

    while True:
        print(f"\nItinerary for {place}:\n")
        for day, activities in itinerary.items():
            print(f"{day}:")
            for time_of_day, activity in activities.items():
                print(f"  {time_of_day}: {activity['name']}")
            print()
        
        feedback = get_user_feedback(itinerary)
        itinerary = adjust_itinerary(itinerary, feedback, data)
        
        continue_feedback = input("Would you like to provide more feedback? (yes/no): ").lower()
        if continue_feedback != 'yes':
            break

    print("\nFinal Itinerary:")
    for day, activities in itinerary.items():
        print(f"{day}:")
        for time_of_day, activity in activities.items():
            print(f"  {time_of_day}: {activity}")
        print()

if __name__ == "__main__":
    main()
    
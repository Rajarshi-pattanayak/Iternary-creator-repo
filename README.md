# Travel Itinerary Generator

## Overview
This Python script generates personalized travel itineraries using the Google Places API. It fetches tourist attractions for a specified location, optimizes the route, and allows users to customize their itinerary based on their preferences.

## Features
- Fetch tourist attractions for a given location
- Categorize activities into morning, afternoon, and evening slots
- Optimize the route using the Traveling Salesman Problem (TSP) algorithm
- Generate a draft itinerary based on the number of days specified
- Allow user feedback and itinerary adjustment
- Display detailed information about each activity

## Requirements
- Python 3.x
- `requests` library
- `numpy` library
- Google Places API key

## Installation
1. Clone this repository or download the `places.py` file.
2. Install the required libraries:
   ```
   pip install requests numpy
   ```
3. Obtain a Google Places API key from the [Google Cloud Console](https://console.cloud.google.com/).
4. Replace the `API_KEY` variable in the script with your actual API key.

## Usage
1. Run the script:
   ```
   python places.py
   ```
2. Follow the prompts to enter:
   - The place you want to visit
   - Number of days for your trip
   - Your interests (comma-separated)
3. Review the generated itinerary
4. Provide feedback on each activity (rate from 1 to 5)
5. Choose to continue providing feedback or finalize the itinerary

## Functions
- `fetch_data_for_place(place)`: Fetches tourist attractions for the given place
- `fetch_distance_matrix(origins, destinations)`: Retrieves distance matrix for optimizing the route
- `prioritize_activities(data, interests)`: Prioritizes activities based on user interests
- `create_itinerary(data, days)`: Generates a draft itinerary
- `tsp_optimization(locations, distance_matrix)`: Optimizes the route using TSP algorithm
- `reorder_activities(data, optimal_route)`: Reorders activities based on the optimized route
- `get_user_feedback(itinerary)`: Collects user feedback on the itinerary
- `adjust_itinerary(itinerary, feedback, data)`: Adjusts the itinerary based on user feedback
- `fetch_place_details(place_id)`: Retrieves detailed information about a place
- `display_activity_details(activity)`: Displays detailed information about an activity

## Note
This script uses the Google Places API, which may incur costs depending on your usage. Make sure to review the [Google Places API pricing](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing) before extensive use.

## Contributing
Feel free to fork this repository and submit pull requests with improvements or bug fixes.

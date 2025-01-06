import re
import os
from flask import Flask, request, jsonify
import pandas as pd
import random
from flask_cors import CORS
from word2number import w2n

app = Flask(__name__)
CORS(app)

datasets_path = "d:/Dataset/"

pagination_state = {}

def load_city_data(city_name):
    """Loads the Excel file for a given city."""
    city_file = os.path.join(datasets_path, f"{city_name.lower().replace(' ', '_')}.xlsx")
    
    if os.path.exists(city_file):
        data = pd.read_excel(city_file)
        data.columns = data.columns.str.lower()
        return data
    else:
        return None
    
def load_accommodation_data(city_name):
    city_file = os.path.join(datasets_path, f"{city_name.lower().replace(' ', '_')}.xlsx")
    
    if os.path.exists(city_file):
        data = pd.read_excel(city_file, sheet_name="Sheet2")
        data.columns = data.columns.str.lower()
        return data
    else:
        return None

def load_foods_data(city_name):
    city_file = os.path.join(datasets_path, f"{city_name.lower().replace(' ', '_')}.xlsx")
    
    if os.path.exists(city_file):
        data = pd.read_excel(city_file, sheet_name="Sheet3")
        data.columns = data.columns.str.lower()
        return data
    else:
        return None

def extract_number(query, default=5):
    """Extract number from the query or use default."""
    numbers = re.findall(r'\b\d+\b', query)
    if numbers:
        return int(numbers[0])
    try:
        return w2n.word_to_num(query)
    except ValueError:
        return default

def extract_city(query):
    """Extracts the city name from the user's query."""
    city_keywords = ["san pedro", "binan", "cabuyao", "calamba", "sta rosa", "los baños", "victoria", "bay", "kalayaan", "santa cruz", "pagsanjan"]
    for city in city_keywords:
        if city in query.lower():
            return city
    return None


#Locations________________________________________________________________________________________________
def extract_location(query, city_name):
    """Extracts location name from the user's query based on the available locations in the dataset."""
    data = load_city_data(city_name)
    if data is not None:
        location_keywords = data['location'].unique() 
        for location in location_keywords:
            if location.lower() in query.lower():
                return location
    return None

def show_hours_for_location(user_id, location_name, city_name):
    """Returns the operating hours for a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"The operating hours for {location_name} in {city_name} are:<br>"
    for _, row in location_data.iterrows():
        response += (
            f"Location: {row['location']}<br>"
            f"Operating Hours: {row['opening']}AM - {row['closing']}PM<br><br>"
        )
    return response

def show_activities_for_location(user_id, location_name, city_name):
    """Returns the activities available at a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"Here are the activities you can do at {location_name} in {city_name}:<br>"
    for _, row in location_data.iterrows():
        response += f"* {row['to_do_activies']}<br>"

    return response

def show_locations(user_id, query, city_name):
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find any locations for this city."

    locations = data['location'].unique()
    random.shuffle(locations)
    num_results = extract_number(query)

    start_index = pagination_state[user_id]['locations']
    locations_to_show = locations[start_index:start_index + num_results]

    pagination_state[user_id]['locations'] += num_results

    response = f"Here are some locations and attractions in {city_name}:<br>"
    for loc in locations_to_show:
        response += f"* {loc}<br>"

    if pagination_state[user_id]['locations'] < len(locations):
        response += "<br>Would you like to see more?"
    else:
        response += "<br>No more locations to show."
    return response

def show_best_locations(user_id, query, city_name):
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find the best locations for this city."

    start_index = pagination_state[user_id]['best_locations']
    sorted_data = data.sort_values(by='rating', ascending=False)
    
    num_results = extract_number(query)

    best_locations = sorted_data[['location', 'rating', 'entrance_fee', 'to_do_activies']].iloc[start_index:start_index + num_results]

    pagination_state[user_id]['best_locations'] += num_results

    response = f"Here are the best locations in {city_name} based on ratings:<br>"
    for _, row in best_locations.iterrows():
        response += (
            f"Location: {row['location']}<br>"
            f"Rating: {row['rating']}<br>"
            f"Entrance Fee: {row['entrance_fee']}<br>"
            f"Activities: {row['to_do_activies']}<br><br>"
        )

    if pagination_state[user_id]['best_locations'] < len(sorted_data):
        response += "<br>Would you like to see more?"
    else:
        response += "<br>No more best locations to show."
    return response

def show_description_for_location(user_id, location_name, city_name):
    """Returns the description of a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"The {location_name} in {city_name}:<br>"
    for _, row in location_data.iterrows():
        response += f"{row['description']}<br>"
    
    return response

def show_rating_for_location(user_id, location_name, city_name):
    """Returns the rating of a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"The rating for {location_name} in {city_name} is:<br>"
    for _, row in location_data.iterrows():
        response += f"Rating: {row['rating']}<br>"

    return response

def show_best_season_for_location(user_id, location_name, city_name):
    """Returns the best season to visit a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"The best season to visit {location_name} in {city_name} is:<br>"
    for _, row in location_data.iterrows():
        response += f"Best Season: {row['best_season']}<br>"
        response += f"Reason: {row['best_season_why']}<br>"

    return response

def show_best_date_for_location(user_id, location_name, city_name):
    """Returns the best date to visit a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"The best date to visit {location_name} in {city_name} is:<br>"
    for _, row in location_data.iterrows():
        # Assuming the column is 'best_date'
        response += f"Best Date: {row['best_date']}<br>"

    return response

def show_best_season_why_for_location(user_id, location_name, city_name):
    """Returns why the best season is considered the best for a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"Here's why {location_name} in {city_name} should be visited in that season:<br>"
    for _, row in location_data.iterrows():
        # Assuming the column is 'Best_Season_Why'
        response += f"Reason:{row['best_season_why']}<br>"

    return response

def show_available_dates_for_location(user_id, location_name, city_name):
    """Returns the available dates for a specific location in a city."""
    data = load_city_data(city_name)
    if data is None:
        return "Sorry, I couldn't find information for this city."

    location_data = data[data['location'].str.contains(location_name, case=False, na=False)]
    
    if location_data.empty:
        return f"Sorry, I couldn't find any information for {location_name} in {city_name}."

    response = f"The available dates for {location_name} in {city_name} are:<br>"
    for _, row in location_data.iterrows():
        # Assuming the column is 'available_date'
        response += f"Available Date: {row['available_days']}<br>"

    return response

#Accommodations________________________________________________________________________________
def show_accommodations(user_id, city_name):
    """Returns a list of accommodations available in a specific city, paginated 5 at a time."""
    data = load_accommodation_data(city_name)
    if data is None:
        return "Sorry, I couldn't find accommodation information for this city."

    accommodations = data[['name', 'description', 'nearest_attraction', 'type_of_accomodation', 'level_of_accomodation', 'phone_number', 'rating', 'price_range', 'one-day_rate', '12-hours_rate','6-hours_rate']]

    if accommodations.empty:
        return f"Sorry, no accommodations were found in {city_name}."

    # Get the current start index from pagination state (default to 0 if not set)
    start_index = pagination_state[user_id].get('accommodations', 0)

    # Show the next 5 accommodations
    accommodations_to_show = accommodations.iloc[start_index:start_index + 4]

    # Update the index for next request
    pagination_state[user_id]['accommodations'] = start_index + 5

    # Format the response
    response = f"Here are some accommodations available in {city_name}:<br>"
    for _, row in accommodations_to_show.iterrows():
        response += (
            f"<b>{row['name']}</b><br>"
            f"Description: {row['description']}<br>"
            f"Price Range: {row['price_range']}<br>"
            f"One-Day Rate: {row['one-day_rate']}<br>"
            f"Twelve Hours Rate: {row['12-hours_rate']}<br>"
            f"Six Hours Rate: {row['6-hours_rate']}<br>"
            f"Nearest Attraction: {row['nearest_attraction']}<br>"
            f"Type: {row['type_of_accomodation']}<br>"
            f"Level: {row['level_of_accomodation']}<br>"
            f"Phone Number: {row['phone_number']}<br>"
            f"Rating: {row['rating']}<br><br>"  
        )
    response += "<br>For more detail try searching the name and calling the phone number provided<br>"

    # Check if there are more accommodations to show
    if pagination_state[user_id]['accommodations'] < len(accommodations):
        response += "<br>Would you like to see more?"
    else:
        response += "<br>No more accommodations to show."

    pagination_state[user_id]['user_intent'] = 'best_accommodation'  # Keep track of user intent
    pagination_state[user_id]['showing_more'] = True  # Track if user wants to see more

    return response

def show_best_accommodation(user_id, city_name):
    """Returns the best-rated accommodation in a city."""
    # Load the accommodation data for the city
    data = load_accommodation_data(city_name)
    
    if data is None:
        return f"Sorry, I couldn't find accommodation information for {city_name}."
    
    # Sort accommodations by rating in descending order
    sorted_data = data.sort_values(by='rating', ascending=False)
    
    # Get the first accommodation (pagination state starts at 0)
    start_index = pagination_state[user_id].get('accommodations', 0)  # Default to 0 if not found
    
    accommodations_to_show = sorted_data.iloc[start_index:start_index + 1]  # Show one accommodation at a time

    # Update the pagination state to the next accommodation
    pagination_state[user_id]['accommodations'] = start_index + 1
    
    # If no accommodation is found, return a message
    if accommodations_to_show.empty:
        return "No more accommodations to show."
    
    # Get the best accommodation to display
    best_accommodation = accommodations_to_show.iloc[0]
    
    # Return details of the best accommodation
    response = f"The best accommodation in {city_name} is:<br>"
    response += (
        f"<b>{best_accommodation['name']}</b><br>"
        f"Description: {best_accommodation['description']}<br>"
        f"Price Range: {best_accommodation['price_range']}<br>"
        f"One-Day Rate: {best_accommodation['one-day_rate']}<br>"
        f"Twelve Hours Rate: {best_accommodation['12-hours_rate']}<br>"
        f"Six Hours Rate: {best_accommodation['6-hours_rate']}<br>"
        f"Nearest Attraction: {best_accommodation['nearest_attraction']}<br>"
        f"Type: {best_accommodation['type_of_accomodation']}<br>"
        f"Level: {best_accommodation['level_of_accomodation']}<br>"
        f"Phone Number: {best_accommodation['phone_number']}<br>"
        f"Rating: {best_accommodation['rating']}<br><br>"
        )
    
    response += "<br>For more detail try searching the name and calling the phone number provided<br>"
    
    # Ask if the user would like more information
    response += "<br>Would you like to know more about this place or other accommodations?"
    
    # Keep track of user intent and if they want to see more accommodations
    pagination_state[user_id]['user_intent'] = 'best_accommodation'
    pagination_state[user_id]['showing_more'] = True
    return response

def show_cheapest_accommodation(user_id, city_name):
    """Returns the cheapest accommodation in a city."""
    # Load the accommodation data for the city
    data = load_accommodation_data(city_name)
    
    if data is None:
        return f"Sorry, I couldn't find accommodation information for {city_name}."
    
    # Extract the minimum price from the price range for sorting
    def extract_min_price(price_range):
        try:
            # Split the range (e.g., '₱500-₱1,000') and get the lower value
            min_price = price_range.split('-')[0].replace('₱', '').replace(',', '').strip()
            return int(min_price)
        except (ValueError, AttributeError):
            return float('inf')  # Default to a very high value if parsing fails

    # Add a new column for the extracted minimum price
    data['min_price'] = data['price_range'].apply(extract_min_price)

    # Sort accommodations by the extracted minimum price in ascending order
    cheapest_accommodation = data.sort_values(by='min_price', ascending=True)

    # Ensure the pagination starts from the first accommodation
    if user_id not in pagination_state:
        pagination_state[user_id] = {'accommodations': 0}  # Initialize to 0 on first request

    start_index = pagination_state[user_id].get('accommodations', 0)  # Get the current index for pagination

    # Show the accommodation at the current start_index
    accommodation_to_show = cheapest_accommodation.iloc[start_index:start_index + 1]

    # Update the index for the next request (increment by 1 for next accommodation)
    pagination_state[user_id]['accommodations'] = start_index + 1

    # Prepare the response with details of the current cheapest accommodation
    response = f"Here is the cheapest accommodation in {city_name}:<br>"
    for _, row in accommodation_to_show.iterrows():
        response += (
            f"<b>{row['name']}</b><br>"
            f"Description: {row['description']}<br>"
            f"Price Range: {row['price_range']}<br>"
            f"One-Day Rate: {row['one-day_rate']}<br>"
            f"Twelve Hours Rate: {row['12-hours_rate']}<br>"
            f"Six Hours Rate: {row['6-hours_rate']}<br>"
            f"Nearest Attraction: {row['nearest_attraction']}<br>"
            f"Type: {row['type_of_accomodation']}<br>"
            f"Level: {row['level_of_accomodation']}<br>"
            f"Phone Number: {row['phone_number']}<br>"
            f"Rating: {row['rating']}<br><br>"
        )
    response += "<br>For more detail try searching the name and calling the phone number provided<br>"

    # Check if there are more accommodations to show
    if pagination_state[user_id]['accommodations'] < len(cheapest_accommodation):
        response += "<br>Would you like to see more accommodations?"
    else:
        response += "<br>No more accommodations to show."

    return response

def show_most_expensive_accommodation(user_id, city_name):
    """Returns the most expensive accommodation in a city."""
    # Load the accommodation data for the city
    data = load_accommodation_data(city_name)
    
    if data is None:
        return f"Sorry, I couldn't find accommodation information for {city_name}."

    # Convert price range to numeric for sorting
    def extract_max_price(price_range):
        try:
            # Split the range (e.g., '₱700-₱1,500') and get the upper value
            max_price = price_range.split('-')[-1].replace('₱', '').replace(',', '').strip()
            return int(max_price)
        except (ValueError, AttributeError):
            return 0  # Default to 0 if parsing fails

    # Add a new column for the extracted maximum price
    data['max_price'] = data['price_range'].apply(extract_max_price)

    # Sort accommodations by the extracted maximum price in descending order
    most_expensive_accommodation = data.sort_values(by='max_price', ascending=False)

    # Initialize pagination state if needed
    if user_id not in pagination_state:
        pagination_state[user_id] = {'accommodations': 0}  # Initialize to 0 on first request

    # Get the current index for pagination
    start_index = pagination_state[user_id].get('accommodations', 0)

    # Show the accommodation at the current start_index
    accommodation_to_show = most_expensive_accommodation.iloc[start_index:start_index + 1]

    # Update the index for the next request (increment by 1 for next accommodation)
    pagination_state[user_id]['accommodations'] = start_index + 1

    # Prepare the response with details of the current most expensive accommodation
    response = f"Here is the most expensive accommodation in {city_name}:<br>"
    for _, row in accommodation_to_show.iterrows():
        response += (
            f"<b>{row['name']}</b><br>"
            f"Description: {row['description']}<br>"
            f"Price Range: {row['price_range']}<br>"
            f"One-Day Rate: {row['one-day_rate']}<br>"
            f"Twelve Hours Rate: {row['12-hours_rate']}<br>"
            f"Six Hours Rate: {row['6-hours_rate']}<br>"
            f"Nearest Attraction: {row['nearest_attraction']}<br>"
            f"Type: {row['type_of_accomodation']}<br>"
            f"Level: {row['level_of_accomodation']}<br>"
            f"Phone Number: {row['phone_number']}<br>"
            f"Rating: {row['rating']}<br><br>"
        )
    response += "<br>For more detail try searching the name and calling the phone number provided<br>"
    # Check if there are more accommodations to show
    if pagination_state[user_id]['accommodations'] < len(most_expensive_accommodation):
        response += "<br>Would you like to see more accommodations?"
    else:
        response += "<br>No more accommodations to show."

    return response

def convert_price_to_numeric(price_range):
    if isinstance(price_range, str):

        price_range = price_range.replace('$', '').split('-')
        if len(price_range) == 2:
            return float(price_range[0])
        else:
            return float(price_range[0])
    return 0
#Foods_________________________________________________________________________________________________________
def show_famous_food(user_id, city_name):
    """Returns a random famous food in a given city."""
    # Load food data for the city
    data = load_foods_data(city_name)
    
    if data is None:
        return f"Sorry, I couldn't find any food information for {city_name}."

    # Shuffle the dataset to randomize the order
    data = data.sample(frac=1).reset_index(drop=True)

    # Ensure pagination state for food queries
    if user_id not in pagination_state:
        pagination_state[user_id] = {'foods': 0}  # Initialize pagination state

    start_index = pagination_state[user_id].get('foods', 0)

    # Display one food item per response
    if start_index >= len(data):
        return "No more famous foods to show. Would you like to start over?"

    food_to_show = data.iloc[start_index:start_index + 5]

    # Update pagination state
    pagination_state[user_id]['foods'] = start_index + 5

    # Prepare response
    response = f"Here is a famous food in {city_name}:<br>"
    for _, row in food_to_show.iterrows():
        response += (
            f"<b>{row['name']}</b><br>"
            f"Description: {row['description']}<br>"
            f"Price Range: {row['price_range']}<br>"
            f"Type of Food: {row['type']}<br><br>"
        )

    # Check if more food items are available
    if pagination_state[user_id]['foods'] < len(data):
        response += "<br>Would you like to see more famous foods?"
    else:
        response += "<br>No more famous foods to show."

    return response

def show_food_locations(user_id, city_name, query):
    """Returns places where the given food can be bought in the given city."""
    # Load food data for the city
    food_data = load_foods_data(city_name)

    if food_data is None:
        return f"Sorry, I couldn't find any food information for {city_name}."

    # Try to match food name in the query itself (without extracting it manually)
    # You can assume that the user asks for food directly, e.g., "Where can I buy Adobo in Manila?"
    food_name = query.split("where can i buy")[1].split("in")[0].strip()  # Extract food name using string splitting
    
    # Search for the food in the dataset
    food_data_filtered = food_data[food_data['name'].str.contains(food_name, case=False, na=False)]

    if food_data_filtered.empty:
        return f"Sorry, I couldn't find {food_name} in {city_name}. Maybe you can try another food item?"

    # Display locations selling the food
    response = f"Here are places in {city_name} where you can buy {food_name}:<br>"
    for _, row in food_data_filtered.iterrows():
        response += (
            f"<b>{row['name']}</b><br>"
            f"You Can Buy It In: {row['where_to_buy']}<br>"
            f"Price Range: {row['price_range']}<br>"
        )

    return response

def show_food_type(user_id, city_name, query):
    """Returns the type of a given food in the specified city."""
    # Load food data for the city
    food_data = load_foods_data(city_name)

    if food_data is None:
        return f"Sorry, I couldn't find any food information for {city_name}."

    # Try to match food name in the query itself (e.g., "What type of food is Adobo in Manila?")
    food_name = query.split("what type of food is")[1].split("in")[0].strip()  # Extract food name using string splitting

    # Search for the food in the dataset
    food_data_filtered = food_data[food_data['name'].str.contains(food_name, case=False, na=False)]

    if food_data_filtered.empty:
        return f"Sorry, I couldn't find {food_name} in {city_name}. Maybe you can try another food item?"

    # Display the type of food
    response = f"The type of food {food_name} is in {city_name} is:<br>"
    for _, row in food_data_filtered.iterrows():
        response += f"Type: {row['type']}<br>"

    return response


def chatbot_response(query, user_id):
    query = query.lower()

    if user_id not in pagination_state:
        pagination_state[user_id] = {
            'locations': 0, 'best_locations': 0, 'hours': 0, 'last_location_request': None, 'user_intent': None, 'city_name': None
        }

    city_name = extract_city(query)
    if city_name is None:
        return "Sorry, I couldn't determine the city you're asking about. Please include the city in your question(in (City)...)"
    
    if "famous food" in query or "local food" in query or "what to eat" in query or "foods" in query:
        # Set the user intent to 'famous_food'
        pagination_state[user_id]['user_intent'] = 'famous_food'
        pagination_state[user_id]['city_name'] = city_name
        # Show famous food in the city
        return show_famous_food(user_id, city_name)

    elif "where can i buy" in query or "where to buy" in query:
        # Pass the query to show_food_locations to extract the food name from it
        return show_food_locations(user_id, city_name, query)

    elif "what type of food" in query or "type of food" in query:
        # Pass the query to show_food_type to extract the food name from it
        return show_food_type(user_id, city_name, query)

    #Accommodations_____________________________________________________________________________
    if "best accommodation" in query or "best hotel" in query:
        # Set the user intent to 'best_accommodation'
        pagination_state[user_id]['user_intent'] = 'best_accommodation'
        pagination_state[user_id]['city_name'] = city_name
        # Return the best-rated accommodation in the city
        return show_best_accommodation(user_id, city_name)
    
    if "cheapest hotel" in query or "cheapest accommodation" in query:
        pagination_state[user_id]['user_intent'] = 'cheapest_accommodation'
        pagination_state[user_id]['city_name'] = city_name
        return show_cheapest_accommodation(user_id, city_name)
    
    if "most expensive hotel" in query or "most expensive accommodation" in query:
        # Set the user intent to 'most_expensive_accommodation'
        pagination_state[user_id]['user_intent'] = 'most_expensive_accommodation'
        pagination_state[user_id]['city_name'] = city_name
        # Show the most expensive accommodation in the city
        return show_most_expensive_accommodation(user_id, city_name)
    
    if "accommodation" in query or "where to stay" in query or "hotel" in query:
        # Set the user intent to 'accommodations'
        pagination_state[user_id]['user_intent'] = 'accommodations'
        pagination_state[user_id]['city_name'] = city_name
        # Show accommodations in the city
        return show_accommodations(user_id, city_name)
    
    #Locations___________________________________________________________________________________________________________
    if "available date" in query or "when is" in query or "is it open" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_available_dates_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."
    
    if "why the best season" in query or "why is this the best season" in query or "why visit in this season" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_best_season_why_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."
    
    if "best date" in query or "ideal date" in query or "when to visit" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_best_date_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."
    
    if "best season" in query or "best time to visit" in query or "when to visit" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_best_season_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."
    
    if "rating" in query or "rate" in query or "what is the rating" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_rating_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."

    if "what is" in query or "tell me about" in query or "description of" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_description_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."

    if "activity" in query or "activities" in query or "what can i do" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_activities_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."

    if "location" in query or "attraction" in query:
        if "best location" in query or "best locations" in query or "rating" in query:
            pagination_state[user_id]['user_intent'] = 'best_locations'
            pagination_state[user_id]['city_name'] = city_name
            return show_best_locations(user_id, query, city_name)
        else:
            pagination_state[user_id]['user_intent'] = 'locations'
            pagination_state[user_id]['city_name'] = city_name
            return show_locations(user_id, query, city_name)

    elif "operating hours" in query or "opening hours" in query or "operating time" in query or "opening time" in query:
        location_name = extract_location(query, city_name)
        if location_name:
            return show_hours_for_location(user_id, location_name, city_name)
        else:
            return "Sorry, I couldn't identify the location you're asking about. Please provide a clear location name."

    else:
        return "Sorry, I didn't quite get that. Please ask about something you want to know about the place."

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    user_id = request.json.get('user_id')  # Unique identifier for each user session
    if user_query and user_id:
        user_query_lower = user_query.lower()

        if "no" in user_query_lower:
            # Reset pagination and user intent when user says "no"
            pagination_state[user_id]['user_intent'] = None
            pagination_state[user_id]['locations'] = 0
            pagination_state[user_id]['best_locations'] = 0
            pagination_state[user_id]['accommodations'] = 0
            pagination_state[user_id]['hours'] = 0
            pagination_state[user_id]['city_name'] = None  # Clear city info
            return jsonify({'response': "Okay, I won't show more results. Let me know if you need anything else."})

        if "yes" in user_query_lower:
            if pagination_state[user_id]['user_intent'] is None:
                return jsonify({'response': "Please ask about locations, best locations, or accommodations first before requesting more."})

            city_name = pagination_state[user_id]['city_name']
            if pagination_state[user_id]['user_intent'] == 'accommodations':
                response = show_accommodations(user_id, city_name)
            elif pagination_state[user_id]['user_intent'] == 'best_accommodation':
                response = show_best_accommodation(user_id, city_name)
            elif pagination_state[user_id]['user_intent'] == 'locations':
                response = show_locations(user_id, user_query, city_name)
            elif pagination_state[user_id]['user_intent'] == 'best_locations':
                response = show_best_locations(user_id, user_query, city_name)
            elif pagination_state[user_id]['user_intent'] == 'cheapest_accommodation':
                response = show_cheapest_accommodation(user_id, city_name)
            elif pagination_state[user_id]['user_intent'] == 'most_expensive_accommodation':
                response = show_most_expensive_accommodation(user_id, city_name)
            elif pagination_state[user_id]['user_intent'] == 'famous_food':
                response = show_famous_food(user_id, city_name)

            return jsonify({'response': response})

        # Default handling for queries
        response = chatbot_response(user_query, user_id)
        return jsonify({'response': response})

    return jsonify({'response': "Please send a valid query."})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

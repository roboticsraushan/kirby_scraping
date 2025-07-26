# Configuration file for Kirby Service Center Scraper

# Different parameter sets for different use cases

# Parameter Set 1: Major US Cities (Quick Test)
MAJOR_CITIES_CONFIG = {
    "locations": [
        "New York, NY",
        "Los Angeles, CA", 
        "Chicago, IL",
        "Houston, TX",
        "Phoenix, AZ",
        "Philadelphia, PA",
        "San Antonio, TX",
        "San Diego, CA",
        "Dallas, TX",
        "San Jose, CA"
    ],
    "search_radius": "50",  # 50 miles
    "max_results": "25",
    "description": "Major US Cities - Quick Test"
}

# Parameter Set 2: Top 50 Major US Cities (Population Based)
TOP_50_CITIES_CONFIG = {
    "locations": [
        "New York City, NY",
        "Los Angeles, CA",
        "Chicago, IL",
        "Houston, TX",
        "Phoenix, AZ",
        "Philadelphia, PA",
        "San Antonio, TX",
        "San Diego, CA",
        "Dallas, TX",
        "Jacksonville, FL",
        "Fort Worth, TX",
        "Austin, TX",
        "San Jose, CA",
        "Charlotte, NC",
        "Columbus, OH",
        "Indianapolis, IN",
        "San Francisco, CA",
        "Seattle, WA",
        "Denver, CO",
        "Oklahoma City, OK",
        "Nashville, TN",
        "Washington, DC",
        "El Paso, TX",
        "Las Vegas, NV",
        "Boston, MA",
        "Detroit, MI",
        "Portland, OR",
        "Louisville, KY",
        "Memphis, TN",
        "Baltimore, MD",
        "Albuquerque, NM",
        "Milwaukee, WI",
        "Tucson, AZ",
        "Fresno, CA",
        "Sacramento, CA",
        "Atlanta, GA",
        "Mesa, AZ",
        "Kansas City, MO",
        "Colorado Springs, CO",
        "Raleigh, NC",
        "Omaha, NE",
        "Miami, FL",
        "Virginia Beach, VA",
        "Long Beach, CA",
        "Oakland, CA",
        "Minneapolis, MN",
        "Bakersfield, CA",
        "Tulsa, OK",
        "Tampa, FL",
        "Arlington, TX"
    ],
    "search_radius": "75",  # 75 miles
    "max_results": "50",
    "description": "Top 50 Major US Cities - Population Based"
}

# Parameter Set 3: All 50 US States (Complete Coverage)
ALL_50_STATES_CONFIG = {
    "locations": [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming"
    ],
    "search_radius": "100",  # 100 miles
    "max_results": "50",
    "description": "All 50 US States - Complete Coverage"
}

# Parameter Set 4: All US States (Comprehensive) - Legacy version
ALL_STATES_CONFIG = {
    "locations": [
        "Alaska", "Texas", "California", "Montana", "New Mexico",
        "Arizona", "Nevada", "Colorado", "Oregon", "Wyoming",
        "Michigan", "Minnesota", "Utah", "Idaho", "Kansas",
        "Nebraska", "South Dakota", "Washington", "North Dakota", "Oklahoma",
        "Missouri", "Florida", "Wisconsin", "Georgia", "Illinois",
        "Iowa", "New York", "North Carolina", "Arkansas", "Alabama",
        "Louisiana", "Mississippi", "Pennsylvania", "Ohio", "Virginia",
        "Tennessee", "Kentucky", "Indiana", "Maine", "South Carolina",
        "West Virginia", "Maryland", "Hawaii", "Massachusetts", "Vermont",
        "New Hampshire", "New Jersey", "Connecticut"
    ],
    "search_radius": "100",  # 100 miles
    "max_results": "50",
    "description": "All US States - Comprehensive Search (Legacy)"
}

# Parameter Set 5: Robotics Hub Cities (Focused)
ROBOTICS_HUBS_CONFIG = {
    "locations": [
        "San Francisco, CA",
        "Seattle, WA", 
        "Boston, MA",
        "Austin, TX",
        "Pittsburgh, PA",
        "Atlanta, GA",
        "Denver, CO",
        "Portland, OR",
        "San Diego, CA",
        "Cambridge, MA"
    ],
    "search_radius": "75",  # 75 miles
    "max_results": "75",
    "description": "Robotics Hub Cities - Focused Search"
}

# Parameter Set 6: High Population States (Dense Coverage)
HIGH_POPULATION_CONFIG = {
    "locations": [
        "California", "Texas", "Florida", "New York", "Pennsylvania",
        "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan",
        "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts",
        "Tennessee", "Indiana", "Missouri", "Maryland", "Colorado"
    ],
    "search_radius": "200",  # 200 miles
    "max_results": "100",
    "description": "High Population States - Dense Coverage"
}

# Parameter Set 7: Custom Locations (User Defined)
CUSTOM_CONFIG = {
    "locations": [
        # Add your custom locations here
        "Houston, TX",
        "Dallas, TX", 
        "Austin, TX",
        "San Antonio, TX"
    ],
    "search_radius": "50",  # 50 miles
    "max_results": "25",
    "description": "Custom Locations - User Defined"
}

# Available search radius options
SEARCH_RADIUS_OPTIONS = {
    "10": "10 mi",
    "25": "25 mi", 
    "50": "50 mi",
    "75": "75 mi",
    "100": "100 mi",
    "200": "200 mi",
    "500": "500 mi"
}

# Available max results options
MAX_RESULTS_OPTIONS = {
    "25": "25",
    "50": "50",
    "75": "75", 
    "100": "100"
}

# Default configuration
DEFAULT_CONFIG = MAJOR_CITIES_CONFIG

# Function to get configuration by name
def get_config(config_name):
    """Get configuration by name"""
    configs = {
        "major_cities": MAJOR_CITIES_CONFIG,
        "top_50_cities": TOP_50_CITIES_CONFIG,
        "all_50_states": ALL_50_STATES_CONFIG,
        "all_states": ALL_STATES_CONFIG,
        "robotics_hubs": ROBOTICS_HUBS_CONFIG,
        "high_population": HIGH_POPULATION_CONFIG,
        "custom": CUSTOM_CONFIG
    }
    return configs.get(config_name, DEFAULT_CONFIG)

# Function to list available configurations
def list_configs():
    """List all available configurations"""
    configs = {
        "major_cities": MAJOR_CITIES_CONFIG,
        "top_50_cities": TOP_50_CITIES_CONFIG,
        "all_50_states": ALL_50_STATES_CONFIG,
        "all_states": ALL_STATES_CONFIG,
        "robotics_hubs": ROBOTICS_HUBS_CONFIG,
        "high_population": HIGH_POPULATION_CONFIG,
        "custom": CUSTOM_CONFIG
    }
    
    print("Available configurations:")
    for name, config in configs.items():
        print(f"  {name}: {config['description']}")
        print(f"    Locations: {len(config['locations'])}")
        print(f"    Radius: {config['search_radius']} miles")
        print(f"    Max Results: {config['max_results']}")
        print() 
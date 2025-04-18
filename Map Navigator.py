import heapq
import folium
from datetime import datetime, time
from geopy.distance import geodesic
import json
from typing import Dict, List, Tuple, Optional
import math
import heapq
import folium
from datetime import datetime, time, timedelta
from geopy.distance import geodesic
import json
from typing import Dict, List, Tuple, Optional
import math
from enum import Enum
from dataclasses import dataclass
import pandas as pd
import numpy as np

class EnhancedMapNavigator:
    def __init__(self):
        self.graph = {}
        self.locations = {}  # Store (latitude, longitude) of each location
        self.location_metadata = {}  # Store additional info about locations
        self.traffic_patterns = {}  # Store time-based traffic patterns
        self.road_types = {}  # Store road type information

    def add_location(self, location: str, latitude: float, longitude: float, 
                    location_type: str = "general", description: str = None):
        """
        Adds a location with its coordinates and metadata.
        
        Args:
            location: Name of the location
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            location_type: Type of location (e.g., landmark, shopping, restaurant)
            description: Additional description of the location
        """
        if location not in self.graph:
            self.graph[location] = []
            self.locations[location] = (latitude, longitude)
            self.location_metadata[location] = {
                "type": location_type,
                "description": description
            }

    def add_road(self, location1: str, location2: str, distance: float, 
                base_traffic_factor: float, road_type: str = "street"):
        """
        Adds a road between two locations with enhanced metadata.
        
        Args:
            location1: First location name
            location2: Second location name
            distance: Distance in kilometers
            base_traffic_factor: Base traffic congestion factor
            road_type: Type of road (highway, street, avenue)
        """
        road_id = f"{location1}-{location2}"
        self.road_types[road_id] = road_type
        
        # Add bidirectional roads
        self.graph[location1].append((location2, distance, base_traffic_factor))
        self.graph[location2].append((location1, distance, base_traffic_factor))

    def add_traffic_pattern(self, location1: str, location2: str, 
                          time_patterns: Dict[str, float]):
        """
        Adds time-based traffic patterns for a road.
        
        Args:
            location1: First location name
            location2: Second location name
            time_patterns: Dictionary mapping time ranges to traffic multipliers
        """
        road_id = f"{location1}-{location2}"
        self.traffic_patterns[road_id] = time_patterns
        reverse_road_id = f"{location2}-{location1}"
        self.traffic_patterns[reverse_road_id] = time_patterns

    def get_traffic_multiplier(self, location1: str, location2: str, 
                             current_time: datetime) -> float:
        """
        Gets the traffic multiplier for a specific time on a road.
        
        Args:
            location1: Starting location
            location2: Ending location
            current_time: Current datetime
        
        Returns:
            Traffic multiplier for the specified time
        """
        road_id = f"{location1}-{location2}"
        if road_id not in self.traffic_patterns:
            return 1.0

        current_hour = current_time.hour
        patterns = self.traffic_patterns[road_id]
        
        # Define time ranges and their corresponding multipliers
        for time_range, multiplier in patterns.items():
            start_hour, end_hour = map(int, time_range.split('-'))
            if start_hour <= current_hour < end_hour:
                return multiplier
        
        return 1.0

    def dijkstra(self, start: str, end: str, 
                current_time: datetime = None) -> Tuple[List[str], float]:
        """
        Enhanced Dijkstra's algorithm considering time-based traffic patterns.
        
        Args:
            start: Starting location
            end: Destination location
            current_time: Current datetime for traffic calculation
        
        Returns:
            Tuple containing the path and total cost
        """
        if current_time is None:
            current_time = datetime.now()

        pq = [(0, start)]
        distances = {location: float('inf') for location in self.graph}
        distances[start] = 0
        previous_nodes = {location: None for location in self.graph}
        
        while pq:
            current_distance, current_location = heapq.heappop(pq)

            if current_location == end:
                break

            if current_distance > distances[current_location]:
                continue

            for neighbor, distance, base_traffic in self.graph[current_location]:
                # Get time-based traffic multiplier
                traffic_multiplier = self.get_traffic_multiplier(
                    current_location, neighbor, current_time
                )
                
                # Calculate total traffic factor
                total_traffic_factor = base_traffic * traffic_multiplier
                
                # Consider road type in travel cost calculation
                road_id = f"{current_location}-{neighbor}"
                road_type_multiplier = self.get_road_type_multiplier(
                    self.road_types.get(road_id, "street")
                )
                
                travel_cost = distance * total_traffic_factor * road_type_multiplier
                new_distance = current_distance + travel_cost

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_location
                    heapq.heappush(pq, (new_distance, neighbor))

        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.insert(0, current)
            current = previous_nodes[current]

        return path, distances[end]

    def get_road_type_multiplier(self, road_type: str) -> float:
        """
        Returns a multiplier based on road type.
        
        Args:
            road_type: Type of road
        
        Returns:
            Multiplier for the road type
        """
        multipliers = {
            "highway": 0.8,  # Highways are faster
            "street": 1.0,   # Normal streets
            "avenue": 0.9,   # Avenues are somewhat faster than streets
            "local": 1.2     # Local roads are slower
        }
        return multipliers.get(road_type, 1.0)

    def visualize_route(self, start: str, end: str, path: List[str], 
                       show_traffic: bool = True) -> None:
        """
        Enhanced visualization with traffic information and location metadata.
        
        Args:
            start: Starting location
            end: Destination location
            path: List of locations in the path
            show_traffic: Whether to show traffic information
        """
        # Create base map
        start_lat, start_lon = self.locations[start]
        m = folium.Map(location=[start_lat, start_lon], zoom_start=12)

        # Add locations with enhanced tooltips
        for location, (lat, lon) in self.locations.items():
            metadata = self.location_metadata[location]
            popup_text = f"""
                <b>{location}</b><br>
                Type: {metadata['type']}<br>
                {metadata['description'] if metadata['description'] else ''}
            """
            color = 'red' if location in [start, end] else 'blue'
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color)
            ).add_to(m)

        # Plot the path with traffic information
        if len(path) > 1:
            for i in range(len(path) - 1):
                loc1, loc2 = path[i], path[i+1]
                lat1, lon1 = self.locations[loc1]
                lat2, lon2 = self.locations[loc2]
                
                # Get current traffic information
                current_time = datetime.now()
                traffic_multiplier = self.get_traffic_multiplier(loc1, loc2, current_time)
                
                # Color code based on traffic
                if show_traffic:
                    color = self.get_traffic_color(traffic_multiplier)
                else:
                    color = "blue"

                # Add the road segment
                folium.PolyLine(
                    [(lat1, lon1), (lat2, lon2)],
                    color=color,
                    weight=4,
                    opacity=0.8,
                    popup=f"Traffic Factor: {traffic_multiplier:.2f}"
                ).add_to(m)

        # Save the map
        m.save("enhanced_route_map.html")
        print("Enhanced map saved as 'enhanced_route_map.html'")

    def get_traffic_color(self, traffic_multiplier: float) -> str:
        """
        Returns a color based on traffic conditions.
        
        Args:
            traffic_multiplier: Traffic multiplier value
        
        Returns:
            Color code for the traffic condition
        """
        if traffic_multiplier <= 1.0:
            return "green"
        elif traffic_multiplier <= 1.5:
            return "yellow"
        else:
            return "red"

    def save_to_json(self, filename: str) -> None:
        """
        Saves the current map data to a JSON file.
        
        Args:
            filename: Name of the file to save to
        """
        data = {
            "locations": self.locations,
            "location_metadata": self.location_metadata,
            "traffic_patterns": self.traffic_patterns,
            "road_types": self.road_types,
            "graph": {k: [(n, d, t) for n, d, t in v] 
                     for k, v in self.graph.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_from_json(self, filename: str) -> None:
        """
        Loads map data from a JSON file.
        
        Args:
            filename: Name of the file to load from
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.locations = data["locations"]
        self.location_metadata = data["location_metadata"]
        self.traffic_patterns = data["traffic_patterns"]
        self.road_types = data["road_types"]
        self.graph = {k: [(n, d, t) for n, d, t in v] 
                     for k, v in data["graph"].items()}

# Example usage
def main():
    # Create navigator instance
    navigator = EnhancedMapNavigator()

    # Add locations with metadata
    locations_data = [
        ("Connaught Place", 28.6277, 77.2208, "commercial", "Central business district"),
        ("Karol Bagh", 28.6460, 77.2054, "shopping", "Popular shopping area"),
        ("Chandni Chowk", 28.6500, 77.2300, "historical", "Historic market area"),
        ("India Gate", 28.6129, 77.2295, "landmark", "War memorial"),
        ("Saket", 28.5245, 77.1947, "residential", "Modern residential area"),
        ("Red Fort", 28.6562, 77.2410, "historical", "Historic fort complex"),
        ("Lajpat Nagar", 28.5638, 77.2341, "shopping", "Popular market area"),
        ("Nehru Place", 28.5523, 77.2597, "commercial", "IT hub"),
        ("Hauz Khas", 28.5494, 77.2001, "entertainment", "Cultural hub"),
        ("Dwarka", 28.5823, 77.0500, "residential", "Suburban area"),
        ("Vasant Kunj", 28.5200, 77.1500, "residential", "Upscale residential area"),
        ("Greater Kailash", 28.5439, 77.2467, "residential", "Premium residential area")
    ]

    for loc in locations_data:
        navigator.add_location(*loc)

    # Add roads with different types
    roads_data = [
        ("Connaught Place", "Karol Bagh", 5, 1.2, "avenue"),
        ("Karol Bagh", "Chandni Chowk", 3, 1.5, "street"),
        ("Chandni Chowk", "India Gate", 4, 1.1, "avenue"),
        ("India Gate", "Saket", 8, 1.3, "highway"),
        ("Saket", "Connaught Place", 10, 1.0, "highway"),
        ("Karol Bagh", "Saket", 7, 1.4, "street"),
        ("Red Fort", "Chandni Chowk", 1, 1.2, "street"),
        ("Lajpat Nagar", "Nehru Place", 5, 1.5, "avenue"),
        ("Hauz Khas", "Saket", 4, 1.2, "street"),
        ("Dwarka", "Vasant Kunj", 12, 1.1, "highway"),
        ("Vasant Kunj", "Greater Kailash", 9, 1.3, "avenue"),
        ("Greater Kailash", "Nehru Place", 3, 1.2, "street")
    ]

    for road in roads_data:
        navigator.add_road(*road)

    # Add time-based traffic patterns
    traffic_patterns = {
        "8-10": 2.0,    # Morning rush hour
        "10-16": 1.2,   # Daytime
        "16-19": 1.8,   # Evening rush hour
        "19-22": 1.3,   # Evening
        "22-8": 1.0     # Night
    }

    # Apply traffic patterns to major roads
    major_routes = [
        ("Connaught Place", "Karol Bagh"),
        ("India Gate", "Saket"),
        ("Dwarka", "Vasant Kunj"),
        ("Lajpat Nagar", "Nehru Place")
    ]

    for route in major_routes:
        navigator.add_traffic_pattern(*route, traffic_patterns)

    return navigator

if __name__ == "__main__":
    navigator = main()
    
    # Display available locations
    print("Available locations:")
    for location in sorted(navigator.locations.keys()):
        metadata = navigator.location_metadata[location]
        print(f"- {location} ({metadata['type']}): {metadata['description']}")

    # Get user input
    start = input("\nEnter starting location: ")
    end = input("Enter destination: ")

    if start in navigator.locations and end in navigator.locations:
        # Find and display route
        current_time = datetime.now()
        path, cost = navigator.dijkstra(start, end, current_time)
        
        print("\nRoute Details:")
        print(f"Time: {current_time.strftime('%H:%M')}")
        print(f"Path: {' → '.join(path)}")
        print(f"Total cost (including traffic): {cost:.2f} units")
        
        # Visualize route
        navigator.visualize_route(start, end, path)
        
        # Save map data
        navigator.save_to_json("delhi_map_data.json")
    else:
        print("Invalid location(s). Please try again.")

class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

@dataclass
class TimeWindow:
    start_time: time
    end_time: time
    traffic_multiplier: float
    day_of_week: List[DayOfWeek]

class LocationSchedule:
    def __init__(self):
        self.operating_hours: Dict[DayOfWeek, List[Tuple[time, time]]] = {}
        self.peak_hours: List[TimeWindow] = []
        self.special_events: List[Tuple[datetime, datetime, str]] = []

class EnhancedMapNavigator:
    def __init__(self):
        self.graph = {}
        self.locations = {}
        self.location_metadata = {}
        self.traffic_patterns = {}
        self.road_types = {}
        self.location_schedules = {}
        self.route_history = []
        self.speed_limits = {}
        self.construction_zones = {}
        self.weather_impacts = {}

    def add_location(self, location: str, latitude: float, longitude: float, 
                    location_type: str = "general", description: str = None,
                    schedule: LocationSchedule = None):
        """
        Adds a location with its coordinates, metadata, and operating schedule.
        """
        if location not in self.graph:
            self.graph[location] = []
            self.locations[location] = (latitude, longitude)
            self.location_metadata[location] = {
                "type": location_type,
                "description": description
            }
            self.location_schedules[location] = schedule or LocationSchedule()

    def set_operating_hours(self, location: str, day: DayOfWeek, 
                          hours: List[Tuple[time, time]]):
        """
        Sets operating hours for a location on a specific day.
        """
        if location in self.location_schedules:
            self.location_schedules[location].operating_hours[day] = hours

    def add_peak_hours(self, location: str, peak_window: TimeWindow):
        """
        Adds peak hours information for a location.
        """
        if location in self.location_schedules:
            self.location_schedules[location].peak_hours.append(peak_window)

    def add_special_event(self, location: str, start: datetime, end: datetime, 
                         event_name: str):
        """
        Adds a special event for a location.
        """
        if location in self.location_schedules:
            self.location_schedules[location].special_events.append(
                (start, end, event_name)
            )

    def add_road(self, location1: str, location2: str, distance: float, 
                base_traffic_factor: float, road_type: str = "street",
                speed_limit: float = None):
        """
        Adds a road with speed limit information.
        """
        road_id = f"{location1}-{location2}"
        self.road_types[road_id] = road_type
        if speed_limit:
            self.speed_limits[road_id] = speed_limit
        
        self.graph[location1].append((location2, distance, base_traffic_factor))
        self.graph[location2].append((location1, distance, base_traffic_factor))

    def add_construction_zone(self, location1: str, location2: str, 
                            start_date: datetime, end_date: datetime,
                            delay_factor: float):
        """
        Adds construction zone information for a road segment.
        """
        road_id = f"{location1}-{location2}"
        self.construction_zones[road_id] = {
            "start_date": start_date,
            "end_date": end_date,
            "delay_factor": delay_factor
        }

    def add_weather_impact(self, date: datetime, impact_factor: float,
                         weather_type: str):
        """
        Adds weather impact information for a specific date.
        """
        self.weather_impacts[date.date()] = {
            "impact_factor": impact_factor,
            "weather_type": weather_type
        }

    def calculate_eta(self, start: str, end: str, 
                     departure_time: datetime) -> timedelta:
        """
        Calculates estimated time of arrival considering all factors.
        """
        path, cost = self.dijkstra(start, end, departure_time)
        if not path:
            return None

        total_time = timedelta()
        current_time = departure_time

        for i in range(len(path) - 1):
            current = path[i]
            next_location = path[i + 1]
            
            # Get base travel time
            road_id = f"{current}-{next_location}"
            distance = next(
                (d for n, d, _ in self.graph[current] if n == next_location),
                None
            )
            
            if distance is None:
                continue

            speed = self.speed_limits.get(road_id, 50)  # Default 50 km/h
            base_time = distance / speed * 60  # Convert to minutes

            # Apply various factors
            traffic_factor = self.get_traffic_multiplier(
                current, next_location, current_time
            )
            
            # Check for construction
            construction_factor = 1.0
            if road_id in self.construction_zones:
                construction = self.construction_zones[road_id]
                if (construction["start_date"] <= current_time <= 
                    construction["end_date"]):
                    construction_factor = construction["delay_factor"]

            # Check for weather
            weather_factor = 1.0
            if current_time.date() in self.weather_impacts:
                weather = self.weather_impacts[current_time.date()]
                weather_factor = weather["impact_factor"]

            # Calculate segment time
            segment_time = (base_time * traffic_factor * construction_factor * 
                          weather_factor)
            total_time += timedelta(minutes=segment_time)
            current_time += timedelta(minutes=segment_time)

        return total_time

    def is_location_open(self, location: str, 
                        check_time: datetime) -> Tuple[bool, str]:
        """
        Checks if a location is open at a specific time.
        """
        if location not in self.location_schedules:
            return True, "No schedule information available"

        schedule = self.location_schedules[location]
        day = DayOfWeek(check_time.weekday())

        # Check operating hours
        if day in schedule.operating_hours:
            for start, end in schedule.operating_hours[day]:
                if start <= check_time.time() <= end:
                    break
            else:
                return False, "Outside operating hours"

        # Check special events
        for event_start, event_end, event_name in schedule.special_events:
            if event_start <= check_time <= event_end:
                return False, f"Closed for special event: {event_name}"

        return True, "Open"

    def get_optimal_departure_time(self, start: str, end: str, 
                                 target_arrival: datetime,
                                 search_window_hours: int = 3) -> datetime:
        """
        Finds the optimal departure time to reach the destination by target time.
        """
        best_departure = None
        min_total_time = timedelta(hours=24)
        
        # Search within the window before target arrival
        for minutes in range(search_window_hours * 60):
            test_time = target_arrival - timedelta(minutes=minutes)
            travel_time = self.calculate_eta(start, end, test_time)
            
            if travel_time is None:
                continue
                
            arrival_time = test_time + travel_time
            
            # Check if this gets us there on time
            if arrival_time <= target_arrival:
                if travel_time < min_total_time:
                    min_total_time = travel_time
                    best_departure = test_time

        return best_departure

    def generate_timing_report(self, start: str, end: str, 
                             departure_time: datetime) -> Dict:
        """
        Generates a detailed timing report for a route.
        """
        path, cost = self.dijkstra(start, end, departure_time)
        if not path:
            return None

        report = {
            "departure_time": departure_time,
            "total_distance": 0,
            "total_time": timedelta(),
            "segments": [],
            "factors_considered": {
                "traffic": [],
                "construction": [],
                "weather": [],
                "special_events": []
            }
        }

        current_time = departure_time

        for i in range(len(path) - 1):
            current = path[i]
            next_location = path[i + 1]
            
            segment = {
                "from": current,
                "to": next_location,
                "start_time": current_time,
                "factors": {}
            }

            # Calculate segment details
            road_id = f"{current}-{next_location}"
            distance = next(
                (d for n, d, _ in self.graph[current] if n == next_location),
                None
            )
            
            if distance is None:
                continue

            speed = self.speed_limits.get(road_id, 50)
            base_time = distance / speed * 60

            # Apply and record factors
            traffic_factor = self.get_traffic_multiplier(
                current, next_location, current_time
            )
            segment["factors"]["traffic"] = traffic_factor

            if road_id in self.construction_zones:
                construction = self.construction_zones[road_id]
                if (construction["start_date"] <= current_time <= 
                    construction["end_date"]):
                    segment["factors"]["construction"] = (
                        construction["delay_factor"]
                    )

            if current_time.date() in self.weather_impacts:
                weather = self.weather_impacts[current_time.date()]
                segment["factors"]["weather"] = weather["impact_factor"]

            # Calculate final segment time
            total_factor = (
                traffic_factor * 
                segment["factors"].get("construction", 1.0) * 
                segment["factors"].get("weather", 1.0)
            )
            segment_time = base_time * total_factor
            
            segment["duration"] = timedelta(minutes=segment_time)
            segment["distance"] = distance
            segment["end_time"] = current_time + segment["duration"]

            report["segments"].append(segment)
            report["total_distance"] += distance
            report["total_time"] += segment["duration"]
            current_time = segment["end_time"]

        report["arrival_time"] = current_time
        return report

def main():
    # Create navigator instance
    navigator = EnhancedMapNavigator()

    # Add locations with operating hours
    locations_data = [
        ("Connaught Place", 28.6277, 77.2208, "commercial", 
         "Central business district"),
        ("Karol Bagh", 28.6460, 77.2054, "shopping", "Popular shopping area"),
        ("Chandni Chowk", 28.6500, 77.2300, "historical", "Historic market area"),
        # ... (previous locations)
    ]

    for loc_data in locations_data:
        navigator.add_location(*loc_data)
        
        # Add sample operating hours
        schedule = LocationSchedule()
        for day in DayOfWeek:
            if day in [DayOfWeek.SUNDAY]:
                # Different hours for Sunday
                hours = [(time(10, 0), time(20, 0))]
            else:
                # Regular hours
                hours = [(time(9, 0), time(21, 0))]
            navigator.set_operating_hours(loc_data[0], day, hours)

    # Add roads with speed limits
    roads_data = [
        ("Connaught Place", "Karol Bagh", 5, 1.2, "avenue", 40),
        ("Karol Bagh", "Chandni Chowk", 3, 1.5, "street", 30),
        # ... (previous roads)
    ]

    for road in roads_data:
        navigator.add_road(*road)

    # Add construction zones
    navigator.add_construction_zone(
        "Connaught Place", 
        "Karol Bagh",
        datetime(2024, 12, 1),
        datetime(2024, 12, 31),
        1.5
    )

    # Add weather impacts
    navigator.add_weather_impact(
        datetime(2024, 12, 20),
        1.3,
        "Heavy Rain"
    )

    return navigator

if __name__ == "__main__":
    navigator = main()
    
    print("Delhi Navigation System")
    print("=" * 50)
    print("\nAvailable locations:")
    for location in sorted(navigator.locations.keys()):
        metadata = navigator.location_metadata[location]
        print(f"- {location} ({metadata['type']}): {metadata['description']}")

    start = input("\nEnter starting location: ")
    end = input("Enter destination: ")
    
    # Get timing preferences
    print("\nTiming Options:")
    print("1. Depart now")
    print("2. Arrive by specific time")
    timing_choice = input("Choose option (1/2): ")

    current_time = datetime.now()
    
    if timing_choice == "1":
        departure_time = current_time
    else:
        hour = int(input("Enter arrival hour (0-23): "))
        minute = int(input("Enter arrival minute (0-59): "))
        target_arrival = datetime.combine(
            current_time.date(), 
            time(hour, minute)
        )
        departure_time = navigator.get_optimal_departure_time(
            start, end, target_arrival
        )

    if start in navigator.locations and end in navigator.locations:
        # Generate and display timing report
        report = navigator.generate_timing_report(start, end, departure_time)
        
        if report:
            print("\nRoute Timing Report")
            print("=" * 50)
            print(f"Departure: {report['departure_time'].strftime('%H:%M')}")
            print(f"Arrival: {report['arrival_time'].strftime('%H:%M')}")
            print(f"Total Distance: {report['total_distance']:.1f} km")
            print(f"Total Time: {report['total_time']}")
            
            print("\nSegment Details:")
            for segment in report["segments"]:
                print(f"\n{segment['from']} → {segment['to']}")
                print(f"Distance: {segment['distance']:.1f} km")
                print(f"Duration: {segment['duration']}")
                print("Factors:")
                for factor, value in segment['factors'].items():
                    print(f"  - {factor}: {value:.2f}x")

            # Visualize route
            navigator.visualize_route(start, end, 
                                   [seg['from'] for seg in report['segments']] + 
                                   [report['segments'][-1]['to']])
        else:
            print("Could not calculate route.")
    else:
        print

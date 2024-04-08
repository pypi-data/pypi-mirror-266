import re
from typing import Any, Optional

def __get_entity(pattern: str, string: str) -> Optional[str]:
    r = re.search(pattern, string)
    return r.group() if r is not None else None

def extract_date_time(content: str, instructions: list, prompt_engine: Any) -> dict:
    """Extract time information from return value of function call extract_date_time

    Args:
        content (str): return value from extract_date_time fucntion call

    Returns:
        dict: start time, end time, and current time
    """
    start_time = r"(?<=start time:\s)\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.*(?=Ext)"
    end_time = r"(?<=end time:\s)\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.*(?=Ext)"
    current_time = r"(?<=Current time:\s)\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"

    return {
        'name': 'extract_date_time',
        'parameters': {
            'start_time': __get_entity(start_time, content),
            'end_time': __get_entity(end_time, content),
            'current_time': __get_entity(current_time, content),
        },
        'role': 'function',
    }

def extract_coordinates(content: str, instructions: list, prompt_engine: Any) -> dict:
    """
    Extract latitude and longitude information from return value of function call extract_coordinatess

    Args:
        content (str): return value from extract_coordinates fucntion call

    Returns:
        dict: latitude and longitude
    """

    latitude = r"(?<=latitude:\s)-?\d{1,3}\.\d{1,6}"
    longitude = r"(?<=longitude:\s)-?\d{1,3}\.\d{1,6}"

    return {
        'name': 'extract_coordinates',
        'parameters': {
            'latitude': __get_entity(latitude, content),
            'longitude': __get_entity(longitude, content),
        },
        'role': 'function',
    }

def get_movie_theaters(content: str, instructions: list, prompt_engine: Any) -> dict:
    """
    Get list of movie theaters given coordinates

    Args:
        content (str): return value from get_movie_theaters fucntion call

    Returns:
        dict:
            reference_number,
            popular_theaters,
            recent_visited_theaters,
            user_preferred_theaters,
            requested_location_based_theaters
    """

    reference_number = r"(?<=reference number:\s)ref_\d+"
    popular_theaters = r"(?<=Popular theaters:\s).*"
    recent_visited_theaters = r"(?<=Recently visited theaters:\s).*"
    user_preferred_theaters = r"(?<=User-preferred theaters:\s).*"
    requested_location_based_theaters = r"(?<=Requested location-based theaters:\s).*"

    return {
        'name': 'get_movie_theaters',
        'parameters': {
            'reference_number': __get_entity(reference_number, content),
            'popular_theaters': __get_entity(popular_theaters, content),
            'popular_theaters': __get_entity(popular_theaters, content),
            'user_preferred_theaters': __get_entity(user_preferred_theaters, content),
            'requested_location_based_theaters': __get_entity(requested_location_based_theaters, content),
        },
        'role': 'function',
    }

def get_movie_titles(content: str, instructions: list, prompt_engine: Any) -> dict:
    """
    Get list of movie titles given coordinates

    Args:
        content (str): return value from get_movie_titles fucntion call

    Returns:
        dict:
            reference_number,
            movie_titles,
    """

    reference_number = r"(?<=reference number:\s)ref_\d+"
    movie_titles = r'(?:(?<=reference number:\sref_\d{3}\)\s)|(?<=reference number:\sref_\d{4}\)\s)).*'

    return {
        'name': 'get_movie_titles',
        'parameters': {
            'reference_number': __get_entity(reference_number, content),
            'movie_titles': __get_entity(movie_titles, content),
        },
        'role': 'function',
    }

def get_movie_schedules(content: str, instructions: list, prompt_engine: Any) -> dict:
    """
    Get list of movie schedules given coordinates

    Args:
        content (str): return value from get_movie_schedules fucntion call

    Returns:
        dict:
            reference_number,
            movie_schedules,
    """

    reference_number = r"(?<=reference number:\s)ref_\d+"
    movie_title = r'(?<=-\sScreening\sschedule\sof\s").*(?=" movie\sin)'
    movie_theater = r'(?<=movie\sin\s").*(?=" theater:)'
    movie_schedules = r'(?<=" theater:).*'

    return {
        'name': 'get_movie_schedules',
        'parameters': {
            'reference_number': __get_entity(reference_number, content),
            'movie_title': __get_entity(movie_title, content),
            'movie_theater': __get_entity(movie_theater, content),
            'movie_schedules': __get_entity(movie_schedules, content),
        },
        'role': 'function',
    }

def book_movie_tickets(content: str, instructions: list, prompt_engine: Any) -> dict:
    return {
        'name': 'book_movie_tickets',
        'parameters': {},
        'role': 'function',
    }

def search_movie_information(content: str, instructions: list, prompt_engine: Any) -> dict:
    movie_title = r"(?<='title':\s).*(?=\s)"
    movie_snippet = r"(?<=snippet:\s).*"

    content_list = content.split('\n')
    movies = []
    for i in range(1, len(content_list), 2):
        title = __get_entity(movie_title, content_list[i])
        snippet = __get_entity(movie_snippet, content_list[i + 1])
        movies.append({'title': title, 'snippet': snippet})

    return {
        'name': 'search_movie_information',
        'parameters': movies,
        'role': 'function',
    }

def search_benefit_for_booking_movie(content: str, instructions: list, prompt_engine: Any) -> dict:
    return {
        'name': 'search_benefit_for_booking_movie',
        'parameters': {
            'benefit': content,
        },
        'role': 'function',
    }

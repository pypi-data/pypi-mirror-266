import json
import os
from datetime import date, datetime, time, timedelta
from dotenv import load_dotenv
from url_remote.environment_name_enum import EnvironmentName
from urllib.parse import urlparse

from .mini_logger import MiniLogger as logger

load_dotenv()


def timedelta_to_time_format(time_delta: timedelta) -> str:
    """
    Convert a timedelta to a time format in HH:MM:SS.

    Parameters:
        time_delta (datetime.timedelta): The timedelta to be converted.

    Returns:
        str: A string in HH:MM:SS format representing the time duration.

    Example:
        Usage of timedelta_to_time_format:

        >>> from datetime import timedelta
        >>> duration = timedelta(hours=2, minutes=30, seconds=45)
        >>> formatted_time = timedelta_to_time_format(duration)
        >>> print(formatted_time)
        "02:30:45"
    """
    TIMEDELTA_TO_TIME_FORMAT_METHOD_NAME = "timedelta_to_time_format"
    logger.start(TIMEDELTA_TO_TIME_FORMAT_METHOD_NAME, object={'time_delta': time_delta})

    # Calculate the total seconds and convert to HH:MM:SS format
    total_seconds = int(time_delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format as "HH:MM:SS"
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    logger.end(TIMEDELTA_TO_TIME_FORMAT_METHOD_NAME,
               object={'formatted_time': formatted_time})
    return formatted_time


def is_valid_time_range(time_range: tuple) -> bool:
    """
    Validate that the time range is in the format 'HH:MM:SS'.
    """
    IS_VALID_TIME_RANGE_METHOD_NAME = "is_valid_time_range"
    logger.start(IS_VALID_TIME_RANGE_METHOD_NAME, object={
        "time_range": time_range.__str__()})
    if len(time_range) != 2:
        logger.end(IS_VALID_TIME_RANGE_METHOD_NAME, object={
            "is_valid_time_range_result": False, "reason": "len(time_range) != 2"})
        return False

    for time_obj in time_range:
        if not isinstance(time_obj, time):
            logger.end(IS_VALID_TIME_RANGE_METHOD_NAME, object={
                "is_valid_time_range_result": False, "reason": "time_range contains non-time objects"})
            return False
        time_str = time_obj.strftime('%H:%M:%S')
        if time_obj.strftime('%H:%M:%S') != time_str:
            logger.end(IS_VALID_TIME_RANGE_METHOD_NAME, object={
                "is_valid_time_range_result": False, "reason": "time_range contains invalid time format"})
            return False

    logger.end(IS_VALID_TIME_RANGE_METHOD_NAME, object={
        "is_valid_time_range_result": True})
    return True


def validate_url(url):
    if url is not None or url != "":
        parsed_url = urlparse(url)
        return parsed_url.scheme and parsed_url.netloc
    return True


def is_valid_date_range(date_range: tuple) -> bool:
    """
    Validate that the date range is in the format 'YYYY-MM-DD'.
    """
    IS_VALID_DATE_RANGE_METHOD_NAME = "is_valid_date_range"
    logger.start(IS_VALID_DATE_RANGE_METHOD_NAME, object={
        "date_range": date_range.__str__()})
    if len(date_range) != 2:
        logger.end(IS_VALID_DATE_RANGE_METHOD_NAME, object={
            "is_valid_date_range_result": False, "reason": "len(date_range) != 2"})
        return False

    for date_obj in date_range:
        if not isinstance(date_obj, date):
            logger.end(IS_VALID_DATE_RANGE_METHOD_NAME, object={
                "is_valid_date_range_result": False, "reason": "date_range contains non-date objects"})
            return False
    logger.end(IS_VALID_DATE_RANGE_METHOD_NAME, object={
        "is_valid_date_range_result": True})
    return True


def is_valid_datetime_range(datetime_range: tuple) -> bool:
    """
    Validate that the datetime range is in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    IS_VALID_DATETIME_RANGE_METHOD_NAME = "is_valid_datetime_range"
    logger.start(IS_VALID_DATETIME_RANGE_METHOD_NAME, object={
        "datetime_range": datetime_range.__str__()})
    if len(datetime_range) != 2:
        logger.end(IS_VALID_DATETIME_RANGE_METHOD_NAME, object={
            "is_valid_datetime_range_result": False, "reason": "len(datetime_range) != 2"})
        return False

    for datetime_obj in datetime_range:
        if not isinstance(datetime_obj, datetime):
            logger.end(IS_VALID_DATETIME_RANGE_METHOD_NAME, object={
                "is_valid_datetime_range_result": False, "reason": "datetime_range contains non-datetime objects"})
            return False
    logger.end(IS_VALID_DATETIME_RANGE_METHOD_NAME, object={
        "is_valid_datetime_range_result": True})
    return True


def is_list_of_dicts(obj):
    """
    Check if an object is a list of dictionaries.

    Parameters:
        obj (object): The object to be checked.

    Returns:
        bool: True if the object is a list of dictionaries, False otherwise.

    Example:
        Usage of is_list_of_dicts:

        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> result = is_list_of_dicts(data)
        >>> print(result)
        True

        >>> data = [1, 2, 3]
        >>> result = is_list_of_dicts(data)
        >>> print(result)
        False
    """
    IS_LIST_OF_DICTS_FUNCTION_NAME = "is_list_of_dicts"
    logger.start(IS_LIST_OF_DICTS_FUNCTION_NAME, object={"obj": obj})
    try:
        if not isinstance(obj, list):
            is_list_of_dicts_result = False
            logger.end(IS_LIST_OF_DICTS_FUNCTION_NAME, object={
                "is_list_of_dicts_result": is_list_of_dicts_result})
            return is_list_of_dicts_result
        for item in obj:
            if not isinstance(item, dict):
                is_list_of_dicts_result = False
                logger.end(IS_LIST_OF_DICTS_FUNCTION_NAME, object={
                    "is_list_of_dicts_result": is_list_of_dicts_result})
                return is_list_of_dicts_result
        is_list_of_dicts_result = True
        logger.end(IS_LIST_OF_DICTS_FUNCTION_NAME, object={
            "is_list_of_dicts_result": is_list_of_dicts_result})
        return is_list_of_dicts_result
    except Exception as exception:
        logger.exception(IS_LIST_OF_DICTS_FUNCTION_NAME, exception)
        logger.end(IS_LIST_OF_DICTS_FUNCTION_NAME)
        raise


def is_time_in_time_range(check_time: time, time_range: tuple) -> bool:
    """
    Check if the given time is within the specified time range.

    Parameters:
        check_time (str): The time to check in 'HH:MM:SS' format.
        time_range (tuple): A tuple containing start and end times in 'HH:MM:SS' format.

    Returns:
        bool: True if the check_time is within the time range, False otherwise.
    """
    IS_TIME_IN_TIME_RANGE_METHOD_NAME = "is_time_in_time_range"
    logger.start(IS_TIME_IN_TIME_RANGE_METHOD_NAME, object={
        "check_time": check_time.__str__(), "time_range": time_range.__str__()})
    if not is_valid_time_range(time_range) or not isinstance(check_time, time):
        logger.end(IS_TIME_IN_TIME_RANGE_METHOD_NAME, object={
            "is_time_in_time_range_result": False})
        return False
    start_time, end_time = time_range
    logger.end(IS_TIME_IN_TIME_RANGE_METHOD_NAME, object={
        "is_time_in_time_range_result": start_time <= check_time <= end_time})
    return start_time <= check_time <= end_time


def is_date_in_date_range(check_date: date, date_range: tuple) -> bool:
    """
    Check if the given date is within the specified date range.

    Parameters:
        check_date (str): The date to check in 'YYYY-MM-DD' format.
        date_range (tuple): A tuple containing start and end dates in 'YYYY-MM-DD' format.

    Returns:
        bool: True if the check_date is within the date range, False otherwise.
    """
    IS_DATE_IN_DATE_RANGE_METHOD_NAME = "is_date_in_date_range"
    logger.start(IS_DATE_IN_DATE_RANGE_METHOD_NAME, object={
        "check_date": check_date.__str__(), "date_range": date_range.__str__()})
    if not is_valid_date_range(date_range) or not isinstance(check_date, date):
        logger.end(IS_DATE_IN_DATE_RANGE_METHOD_NAME, object={
            "is_date_in_date_range_result": False})
        return False

    start_date, end_date = date_range
    logger.end(IS_DATE_IN_DATE_RANGE_METHOD_NAME, object={
        "is_date_in_date_range_result": start_date <= check_date <= end_date})
    return start_date <= check_date <= end_date


def is_datetime_in_datetime_range(check_datetime: datetime, datetime_range: tuple) -> bool:
    """
    Check if the given datetime is within the specified datetime range.

    Parameters:
        check_datetime (str): The datetime to check in 'YYYY-MM-DD HH:MM:SS' format.
        datetime_range (tuple): A tuple containing start and end datetimes in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        bool: True if the check_datetime is within the datetime range, False otherwise.
    """
    IS_DATETIME_IN_DATETIME_RANGE_METHOD_NAME = "is_datetime_in_datetime_range"
    logger.start(IS_DATETIME_IN_DATETIME_RANGE_METHOD_NAME)
    if not is_valid_datetime_range(datetime_range) or not isinstance(check_datetime, datetime):
        logger.end(IS_DATETIME_IN_DATETIME_RANGE_METHOD_NAME, object={
            "is_valid_datetime_range": False})
        return False

    start_datetime, end_datetime = datetime_range
    is_datetime_in_datetime_range_result = start_datetime <= check_datetime <= end_datetime
    logger.end(IS_DATETIME_IN_DATETIME_RANGE_METHOD_NAME, object={
        "is_datetime_in_datetime_range_result": is_datetime_in_datetime_range_result})
    return is_datetime_in_datetime_range_result


# TODO Align those methods with typescript-sdk https://github.com/circles-zone/typescript-sdk-remote-typescript-package/blob/dev/typescript-sdk/src/utils/index.ts  # noqa501
# TODO Take those three functions to a separate file http_response.py
# TODO Shall we create also createInternalServerErrorHttpResponse(), createOkHttpResponse() like we have in TypeScript?

# Former name was create_http_headers()
def create_authorization_http_headers(user_jwt: str):
    http_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {user_jwt}',
    }
    return http_headers


def create_return_http_headers():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }


# https://google.github.io/styleguide/jsoncstyleguide.xml?showone=Property_Name_Format#Property_Name_Format
def create_http_body(body):
    # TODO console.warning() if the body is not a valid camelCase JSON
    # https://stackoverflow.com/questions/17156078/converting-identifier-naming-between-camelcase-and-underscores-during-json-seria
    return json.dumps(body)


def get_brand_name():
    return our_get_env("BRAND_NAME")


def get_environment_name():
    environment_name = our_get_env("ENVIRONMENT_NAME")
    EnvironmentName(environment_name)  # if invalid, raises ValueError: x is not a valid EnvironmentName
    return environment_name


def our_get_env(key: str, default: str = None, raise_if_not_found: bool = True) -> str:
    result = os.getenv(key, default)
    if raise_if_not_found and result is None:
        raise Exception(f"Environment variable {key} not found")
    return result


def get_sql_hostname() -> str:
    return our_get_env("RDS_HOSTNAME")


def get_sql_username() -> str:
    return our_get_env("RDS_USERNAME")


def get_sql_password() -> str:
    return our_get_env("RDS_PASSWORD")


def remove_digits(text: str) -> str:
    return ''.join([i for i in text if not i.isdigit()])

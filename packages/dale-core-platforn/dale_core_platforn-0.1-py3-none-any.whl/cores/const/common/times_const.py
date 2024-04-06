from ..__const import Const


class TimeConst(Const):
    """
        %Y: Year with century as a four-digit number (e.g., 2023).
        %y: Year without century as a zero-padded two-digit number (e.g., 23).
        %m: Month as a zero-padded two-digit number (e.g., 06).
        %d: Day of the month as a zero-padded two-digit number (e.g., 27).
        %H: Hour in 24-hour format as a zero-padded two-digit number (e.g., 15).
        %I: Hour in 12-hour format as a zero-padded two-digit number (e.g., 03).
        %M: Minute as a zero-padded two-digit number (e.g., 30).
        %S: Second as a zero-padded two-digit number (e.g., 45).
        %p: AM/PM designation (applicable with %I for 12-hour format).
        %A: Full weekday name (e.g., Monday).
        %a: Abbreviated weekday name (e.g., Mon).
        %B: Full month name (e.g., June).
        %b: Abbreviated month name (e.g., Jun)
        %w: Weekday as a decimal number, where Sunday is 0 and Saturday is 6.
        %U: Week number of the year as a zero-padded decimal number, with Sunday as the first day of the week (e.g., 00-53).
        %W: Week number of the year as a zero-padded decimal number, with Monday as the first day of the week (e.g., 00-53).
        %j: Day of the year as a zero-padded decimal number (e.g., 001-365).
        %x: Locale's date representation (e.g., 06/27/2023).
        %X: Locale's time representation (e.g., 15:30:45).
        %Z: Time zone name (e.g., UTC, EST, PST).
        %%: A literal '%' character.
        %c: Locale's appropriate date and time representation.
        %D: Equivalent to %m/%d/%y (e.g., 06/27/23).
        %F: Equivalent to %Y-%m-%d (e.g., 2023-06-27).
        %e: Day of the month as a decimal number, with a leading space for single-digit days (e.g., ' 1', '15').
        %j: Day of the year as a decimal number, padded with zeros (e.g., '001', '365').
    """
    class Format:
        FORMAT_DD_MM_YY_12_HOUR = '%d/%m/%y %I:%M %p'  # dd/mm/yy 00:00 AM/PM
        FORMAT_DD_MM_YY_DD_Z = '%Y-%m-%dT%H:%M:%S.%f%z'
        FORMAT_DD_MM_YY_DD_Z_2 = '%Y-%m-%dT%H:%M:%S%z'
        FORMAT_DD_MM_YY_S_F = '%Y-%m-%d %H:%M:%S.%f'
        FORMAT_DD_MM_YY = '%d/%m/%y'  # dd/mm/yy
        FORMAT_DD_MM_YYYY = '%d/%m/%Y'  # dd/mm/yyyy
        FORMAT_DD_MM_YYYY_H_M_S_FILE = '%d_%m_%Y_%H_%M_%S'  # dd_mm_yyyy_H_M_S
        FORMAT_D_B_Y = '%d %B %Y'  # 20 Aug 2023
        FORMAT_D_B_FULL_Y = '%d %B %Y'  # 01 August 2023
        FORMAT_D_B = '%d %B'  # Mar 20
        FORMAT_B_D_Y = '%B %d, %Y'  # August 20, 2023
        FORMAT_B_Y = '%d %b %Y'  # Mar 2023

        FORMAT_12_HOUR = '%I:%M %p'
        FORMAT_12_HOUR_WITHOUT_ZERO = '%-I:%M %p'
        FORMAT_24_HOUR = '%H:%M:%S'

    class Timeout:
        TIMEOUT_2 = 2
        TIMEOUT_10 = 10
        TIMEOUT_15 = 15
        TIMEOUT_30 = 30
        TIMEOUT_60 = 60
        TIMEOUT_60000MS = 60000

    class TimePattern:
        YEAR_YEAR_PATTERN = r'^\d{4} – \d{4}$'
        MONTH_YEAR_PATTERN = r"\b\w{3,}\b \d{4}"

    class Retry:
        DEFAULT = 3

    class Month:
        names = {
            'January': 'Jan',
            'February': 'Feb',
            'March': 'Mar',
            'April': 'Apr',
            'May': 'May',
            'June': 'Jun',
            'July': 'Jul',
            'August': 'Aug',
            'September': 'Sep',
            'October': 'Oct',
            'November': 'Nov',
            'December': 'Dec'
        }

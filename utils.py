import time
def prep_loc(num):
    return "{:04}".format(str(num))

def pad(value, width=2, char=' '):
    return "{:>{char}{width}}".format(str(value), char=char, width=width)

def days_in_month(year, month):
    """Calculate days in month for given year and month"""
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif month == 2:
        # Simplified leap year check (CircuitPython doesn't have calendar module)
        if year % 4 == 0:
            return 29
        return 28
    return 30

def struct_time(year, month, day, hour, minute, second):
    """Create a time.struct_time object"""
    return time.struct_time((
        year, month, day,  # tm_year, tm_mon, tm_mday
        hour, minute, second,  # tm_hour, tm_min, tm_sec
        0, 0, 0,  # tm_wday, tm_yday, tm_isdst
        0  # tm_gmtoff
    ))

def get_clock_text(ntp):
    utc_struct = ntp.datetime
    
    # Convert to PST manually
    pst_hour = (utc_struct.tm_hour - 7) % 24
    pst_day = utc_struct.tm_mday
    
    # Handle date transition
    if pst_hour >= 24:
        pst_hour -= 24
        if utc_struct.tm_mon == 1 and utc_struct.tm_mday == 1:
            pst_day = 31
            pst_month = 12
            pst_year = utc_struct.tm_year - 1
        elif utc_struct.tm_mday == 1:
            pst_day = days_in_month(utc_struct.tm_year, utc_struct.tm_mon - 1)
            pst_month = utc_struct.tm_mon - 1
            pst_year = utc_struct.tm_year
        else:
            pst_day -= 1
            pst_month = utc_struct.tm_mon
            pst_year = utc_struct.tm_year
            
        # Update global date
        ntp.datetime = struct_time(pst_year, pst_month, pst_day,
                                 pst_hour, utc_struct.tm_min, 
                                 utc_struct.tm_sec)
    
    # Determine AM/PM
    period = "AM" if pst_hour < 12 else "PM"
    display_hour = pst_hour if pst_hour != 0 else 12
    display_hour = display_hour - 12 if display_hour > 12 else display_hour
    
    # Format the time
    return f"{pad(display_hour)}:{pad(utc_struct.tm_min, char='0')} {period}"

def get_date_text(ntp):
    utc_struct = ntp.datetime
    
    # Convert to PST manually
    pst_hour = (utc_struct.tm_hour - 7) % 24
    pst_day = utc_struct.tm_mday
    pst_year = utc_struct.tm_year

    
    # Handle date transition
    if pst_hour >= 24:
        pst_hour -= 24
        if utc_struct.tm_mon == 1 and utc_struct.tm_mday == 1:
            pst_day = 31
            pst_month = 12
            pst_year = utc_struct.tm_year - 1
        elif utc_struct.tm_mday == 1:
            pst_day = days_in_month(utc_struct.tm_year, utc_struct.tm_mon - 1)
            pst_month = utc_struct.tm_mon - 1
            pst_year = utc_struct.tm_year
        else:
            pst_day -= 1
            pst_month = utc_struct.tm_mon
            pst_year = utc_struct.tm_year
            
        # Update global date
        ntp.datetime = struct_time(pst_year, pst_month, pst_day,
                                 pst_hour, utc_struct.tm_min, 
                                 utc_struct.tm_sec)
    
    return f"{pad(utc_struct.tm_mon, char='0')}/{pad(pst_day, char='0')}/{str(pst_year)}"
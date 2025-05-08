import time
def prep_loc(num):
    return "{:04}".format(str(num))

def pad(value, width=2, char=' '):
    return "{:>{char}{width}}".format(str(value), char=char, width=width)

def get_clock_text(ntp):
    utc_struct = ntp.datetime
    
    # Convert to PST manually
    pst_hour = utc_struct.tm_hour
    pst_day = utc_struct.tm_mday
    
    # Determine AM/PM
    period = "AM" if pst_hour < 12 else "PM"
    display_hour = pst_hour if pst_hour != 0 else 12
    display_hour = display_hour - 12 if display_hour > 12 else display_hour
    
    # Format the time
    return f"{pad(display_hour)}:{pad(utc_struct.tm_min, char='0')} {period}"

def get_date_text(ntp):
    utc_struct = ntp.datetime
    
    pst_day = utc_struct.tm_mday
    pst_year = utc_struct.tm_year

    return f"{pad(utc_struct.tm_mon, char='0')}/{pad(pst_day, char='0')}/{str(pst_year)}"
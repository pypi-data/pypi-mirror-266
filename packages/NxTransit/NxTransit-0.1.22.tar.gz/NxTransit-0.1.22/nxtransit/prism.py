# BETA
def calculate_accessibility_indices(source, travel_times, time_window, opening_hours, T_min):
    # Initialize the RSTP and CUMRT values
    RSTP = set()
    CUMRT = 0
    
    # Unpack time window and opening hours
    t_o, t_n = time_window
    t_s, t_e = opening_hours
    
    # Iterate through each opportunity to calculate accessibility
    for op, times in travel_times.items():
        # Unpack travel times to and from the opportunity
        C_j_op, C_op_j = times
        
        # Calculate the time interval during which the individual can be at the opportunity
        available_start = max(t_o + C_j_op, t_s)  # No earlier than the opening time and travel time
        available_end = min(t_n - C_op_j, t_e)    # No later than the closing time and travel time
        
        # Check if the opportunity is accessible (the individual can stay for T_min)
        if available_start + T_min <= available_end:
            RSTP.add((op, available_start))
            CUMRT += available_end - available_start - T_min
    
    return RSTP, CUMRT

# Example usage:
# Assume we have a dictionary of travel times to ('to_op') and from ('from_op') each opportunity 'op'.
# Each entry in the dictionary is a tuple (C_j_op, C_op_j).
travel_times_to_and_from_opportunities = {
    'op1': (3600, 3600),  # 1 hour to and 1 hour from opportunity 1
    'op2': (1800, 1800),  # 30 minutes to and 30 minutes from opportunity 2
    # ... other opportunities
}

# Time window in which the individual is willing to engage in activities (e.g., 8:00 AM to 8:00 PM)
individual_time_window = (28800, 72000)  # (8 AM, 8 PM in seconds since midnight)

# Opening hours for all opportunities (from 10,000 seconds to 70,000 seconds since midnight)
opportunities_opening_hours = (10000, 70000)

# Minimum time required to spend at each opportunity
minimum_time_at_opportunity = 1800  # 30 minutes in seconds

# Calculate the indices
rstp, cumrt = calculate_accessibility_indices(
    source='source_node',
    travel_times=travel_times_to_and_from_opportunities,
    time_window=individual_time_window,
    opening_hours=opportunities_opening_hours,
    T_min=minimum_time_at_opportunity
)

print("RSTP:", rstp)
print("CUMRT:", cumrt)



def calculate_latest_departure_times(source, travel_times, time_window, opening_hours, T_min):
    # Initialize the RSTP set for the latest departure times
    RSTP_latest_departure = {}

    # Unpack the individual's available time window and the opening hours for opportunities
    t_o, t_n = time_window
    t_s, t_e = opening_hours

    # Iterate through each opportunity to calculate the latest departure time
    for op, times in travel_times.items():
        # Unpack travel times to and from the opportunity
        C_j_op, C_op_j = times
        
        # Calculate the latest possible departure time from the opportunity
        # This time must allow the individual to return to the starting point before t_n
        # and must be after the opportunity has opened (after t_s) and after the minimum stay T_min
        latest_possible_departure = min(t_e, t_n - C_op_j) - T_min
        
        # If the latest possible departure time is after the opening time plus travel time, it's valid
        if latest_possible_departure >= (t_s + C_j_op):
            RSTP_latest_departure[op] = latest_possible_departure

    return RSTP_latest_departure

# Example usage:
# Assuming travel_times_to_and_from_opportunities, individual_time_window,
# opportunities_opening_hours, and minimum_time_at_opportunity are defined as before

# Calculate the latest departure times
rstp_latest_departures = calculate_latest_departure_times(
    source='source_node',
    travel_times=travel_times_to_and_from_opportunities,
    time_window=individual_time_window,
    opening_hours=opportunities_opening_hours,
    T_min=minimum_time_at_opportunity
)

print("RSTP Latest Departure Times:", rstp_latest_departures)


def calculate_accessibility(source, travel_times, time_window, opening_hours, T_min):
    # Initialize the result set for RSTP information
    RSTP_info = set()

    # Initialize a variable for the total CUMRT
    total_CUMRT = 0

    # Unpack the individual's available time window and the opening hours for opportunities
    t_o, t_n = time_window
    t_s, t_e = opening_hours

    # Iterate through each opportunity to calculate accessibility information
    for op, times in travel_times.items():
        # Unpack travel times to and from the opportunity
        C_j_op, C_op_j = times
        
        # Calculate the earliest arrival and the latest departure times
        earliest_arrival = max(t_o + C_j_op, t_s)
        latest_departure = min(t_e, t_n - C_op_j) - T_min

        # Calculate the cumulative reliable time (CUMRT) for this opportunity
        if earliest_arrival <= latest_departure:
            cum_time = latest_departure - earliest_arrival
            total_CUMRT += cum_time
            # Add to the RSTP set if the opportunity is accessible
            RSTP_info.add((op, earliest_arrival, latest_departure, cum_time))
        else:
            # If not accessible, cum_time is set to 0
            cum_time = 0

    return RSTP_info, total_CUMRT

# Example usage:
# Assuming travel_times_to_and_from_opportunities, individual_time_window,
# opportunities_opening_hours, and minimum_time_at_opportunity are defined as before

# Calculate the RSTP information and total CUMRT
rstp_info, total_cumrt = calculate_accessibility(
    source='source_node',
    travel_times=travel_times_to_and_from_opportunities,
    time_window=individual_time_window,
    opening_hours=opportunities_opening_hours,
    T_min=minimum_time_at_opportunity
)

print("RSTP Information (Opportunity, Earliest Arrival, Latest Departure, CUM Time):", rstp_info)
print("Total CUMRT:", total_cumrt)
import time
import threading

# Initialize the sequence number and the last timestamp
_sequence_number = 0
_last_timestamp = 0
_lock = threading.Lock()

def generate_sequence_number():
    """
    Generates a unique sequence number for use as a primary key.
    
    The sequence number is a combination of the current timestamp (in seconds) 
    and a counter for the current second, ensuring uniqueness.
    
    :return: A unique sequence number.
    """
    global _sequence_number, _last_timestamp
    
    with _lock:  # Ensure thread safety
        current_timestamp = int(time.time())
        
        if current_timestamp == _last_timestamp:
            # If within the same second, increment the sequence number
            _sequence_number += 1
        else:
            # Reset the sequence number for a new second
            _sequence_number = 1
            _last_timestamp = current_timestamp
        
        # Combine the timestamp and sequence number (optional, but useful for readability)
        # If you prefer a single, incrementing number without the timestamp, remove the current_timestamp part
        unique_id = (current_timestamp * 1000) + _sequence_number  # *1000 to make room for the sequence number
        
        return unique_id

# Example usage
if __name__ == "__main__":
    # Call the function
    print("Calling generate_sequence_number: ")
    for _ in range(5):
        print(generate_sequence_number())


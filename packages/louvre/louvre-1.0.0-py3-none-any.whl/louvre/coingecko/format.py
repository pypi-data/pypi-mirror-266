import pandas as pd


def convert_historical_data_to_dataframe(data):
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['Timestamp', 'Value'])
    
    # Convert the 'Timestamp' column from milliseconds since the Unix epoch to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    
    return df
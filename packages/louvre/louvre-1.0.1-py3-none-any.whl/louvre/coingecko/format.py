import pandas as pd


def convert_historical_data_to_dataframe(data):
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['time', 'value'])
    
    # Convert the 'Timestamp' column from milliseconds since the Unix epoch to datetime
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index("time")
    
    return df["value"]
import pandas as pd
import csv

def string_in_file(file_path, string_to_search):
    with open(file_path, 'r') as file:
        return string_to_search in file.read()

def filter_csv_columns(csv_file_path, headers_to_include):
    filtered_csv_file_path = 'filtered_' + csv_file_path.split('/')[-1]

    with open(csv_file_path, 'r') as source_file:
        csv_reader = csv.reader(source_file)
        headers = next(csv_reader)
        
        # Determine indices of headers to include
        header_indices = [i for i, h in enumerate(headers) if h in headers_to_include]
        
        # Open new file in write mode to save filtered data
        with open(filtered_csv_file_path, 'w', newline='') as target_file:
            csv_writer = csv.writer(target_file)
            
            # Write headers of columns to include
            csv_writer.writerow([headers[i] for i in header_indices])
            
            # Write rows, only including the specified columns
            for row in csv_reader:
                csv_writer.writerow([row[i] for i in header_indices])


def search_headers_in_file(csv_file_path, file_path):
    # just read first row of csv file 
    df = pd.read_csv(csv_file_path, nrows=1)
    headers = df.columns.tolist()
    results = {header: string_in_file(file_path, header) for header in headers}
    return results

if __name__ == "__main__":
    csv_file_path = '/home/john/topics/minimum_wage/etl/transformed/df_mw_first.csv'
    #file_path = '/home/john/topics/minimum_wage/analysis/avg_wages_by_cat.R'
    file_path = '/home/john/topics/minimum_wage/analysis/utilities_outcome_experimental_plots.R'
    x = search_headers_in_file(csv_file_path, file_path)
    used_columns = [k for k, v in x.items() if v]
    filter_csv_columns(csv_file_path, used_columns)
    

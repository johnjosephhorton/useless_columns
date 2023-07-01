import re 
import os 
import csv
from collections.abc import Sequence

def column_names(csv_file_path):
    with open(csv_file_path, 'r') as source_file:
        csv_reader = csv.reader(source_file)
        headers = next(csv_reader)
    return headers

class AnalyticFile:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        with open(self.path, 'r') as f:
            self.txt = f.read()

        self.csv_files = self.get_csv_files()
        self.used_columns_dict = self.get_used_columns()

    def string_in_file(self, string_to_search):
        return string_to_search in self.txt
    
    def get_csv_files(self):
        csv_files = list(set(re.findall(r'read\.csv\(\s*\"(.*?).csv\"', self.txt, re.DOTALL)))
        return csv_files
    
    def csv_file_paths(self):
        return [os.path.normpath(os.path.join(os.path.dirname(self.path), f + ".csv")) for f in self.csv_files]
    
    def get_used_columns(self):
        used_dict = dict({})
        for csv_file in self.csv_file_paths():
            headers = column_names(csv_file)
            results = {header: self.string_in_file(header) for header in headers}
            used_dict[csv_file] = [k for k, v in results.items() if v]
        return used_dict
    
    def __repr__(self):
        return f"AnalyticFile({self.name})"
    
class AnalyticsFiles(Sequence):
    def __init__(self, directory):
        self._data = []
        for analytic_file in os.listdir(directory):
            if analytic_file.endswith(".R"):
                self._data.append(AnalyticFile(os.path.join(directory, analytic_file)))
        
        self.combined_used_columns = self.get_combined_used_columns()
        self.data_to_files = self.get_data_to_files()

    def __getitem__(self, index):
        return self._data[index]
    
    def __len__(self):
        return len(self._data)
    
    def get_data_to_files(self):
        d = dict({})
        for analytic_file in self._data:
            for csv_file in analytic_file.csv_files:
                if csv_file in d:
                    d[csv_file].append(analytic_file.name)
                else:
                    d[csv_file] = [analytic_file.name]
        return d
    
    def get_combined_used_columns(self):
        "For each analytic file, get the columns used in each CSV and combined"
        used_columns_dict = dict({})
        for analytic_file in self._data:
            used_columns_dict.update(analytic_file.used_columns_dict)
        return used_columns_dict

if __name__ == "__main__":
    a = AnalyticFile('/home/john/topics/minimum_wage/analysis/utilities_outcome_experimental_plots.R')
    print(a.get_csv_files())
    print(a.csv_file_paths())
    print(a.get_used_columns())

    A = AnalyticsFiles('/home/john/topics/minimum_wage/analysis')
    print(A.combined_used_columns)
    print(A.data_to_files)
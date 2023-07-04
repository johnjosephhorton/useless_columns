import re 
import os 
import csv
import tempfile
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

    def string_in_file(self, string_to_search):
        "Does this string appear anywhere in the file?"
        return string_to_search in self.txt
    
    @property
    def csv_files(self, paths = ["/home/john/topics/minimum_wage/etl/transformed/","/home/john/topics/minimum_wage/computed_objects/"]):
        #_csv_files = list(set(re.findall(r'read\.csv\(\s*\"(.*?).csv\"', self.txt, re.DOTALL)))
        #_csv_files = list(set(re.findall(r'read\.csv\(\s*\"(.*?).csv\"', self.txt)))
        csv_files = []
        _csv_files = set(re.findall(r'GetData\("(.+)"\)', self.txt))
        for csv_file in _csv_files:
            for path in paths: 
                full_path = os.path.normpath(os.path.join(path, csv_file))
                print(full_path)
                if os.path.isfile(full_path):
                    csv_files.append(full_path)
                    break
        return csv_files
    
    @property
    def used_columns_dict(self):
        used_dict = dict({})
        for csv_file in self.csv_files:
            headers = column_names(csv_file)
            results = {header: self.string_in_file(header) for header in headers}
            used_dict[csv_file] = {k for k, v in results.items() if v}
        return used_dict

    def __repr__(self):
        return f"AnalyticFile({self.name})"
    
class AnalyticsFiles(Sequence):
    def __init__(self, directory):
        self._data = []
        for analytic_file in os.listdir(directory):
            if analytic_file.endswith(".R"):
                self._data.append(AnalyticFile(os.path.join(directory, analytic_file)))
        
        self.used_columns_dict = self.get_combined_used_columns()
        self.data_to_files = self.get_data_to_files()

        # gets one list of all csv files used 
        #self.csv_files = []
        #[self.csv_files.extend(analytic_file.csv_files) for analytic_file in self._data]
        self.csv_files = list(self.used_columns_dict.keys())

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
        agg_used_columns_dict = dict({})
        for analytic_file in self._data:
            for csv_file, used_columns in analytic_file.used_columns_dict.items():
                if csv_file in agg_used_columns_dict:
                    [agg_used_columns_dict[csv_file].add(k) for k in used_columns]
                else:
                    agg_used_columns_dict[csv_file] = used_columns
        return agg_used_columns_dict
    
    def write_filtered_csv_files(self, output_directory = "/tmp/mw_rep"):
        if output_directory is None:
            tempdir = tempfile.TemporaryDirectory()
            output_directory = tempdir.name

        print(f"Writing filtered CSV files to {output_directory}")

        for csv_file in self.csv_files:
            print(f"Writing: {csv_file}")
            headers = self.used_columns_dict[csv_file]
            with open(csv_file, 'r') as source_file:
                csv_reader = csv.reader(source_file)
                old_headers = next(csv_reader)
                d = dict(zip(old_headers, range(len(old_headers))))
                with open(os.path.join(output_directory, os.path.basename(csv_file)), 'w') as dest_file:
                    csv_writer = csv.writer(dest_file)
                    csv_writer.writerow(headers)
                    for row in csv_reader:
                        csv_writer.writerow([row[d[header]] for header in headers])
            print(f"\tWent from {len(old_headers)} to {len(headers)} columns")


if __name__ == "__main__":
    a = AnalyticFile('/home/john/topics/minimum_wage/analysis/utilities_outcome_experimental_plots.R')
    #print(a.get_csv_files())
    #print(a.csv_file_paths())
    #print(a.get_used_columns())

    A = AnalyticsFiles('/home/john/topics/minimum_wage/analysis')
    a = A[18]
    #print(A.used_columns_dict)
    #print(A.combined_used_columns)
    #print(A.data_to_files)

    A.write_filtered_csv_files()
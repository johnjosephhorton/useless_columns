import jinja2 
import subprocess

from jinja2 import Environment, FileSystemLoader
import datetime
from find_r_packages import get_all_used_packages, get_installed_packages, get_r_files, keyify, create_docker_section, get_r_version

from AnalyticFile import AnalyticsFiles

notice_about_replication = """
The platform used as the empirical context chooses to remain anonymous.
To...
"""



    #print(a.get_csv_files())
    #print(a.csv_file_paths())
    #print(a.get_used_columns())

A = AnalyticsFiles('/home/john/topics/minimum_wage/analysis')

path = "/home/john/topics/minimum_wage/analysis"
r_files = get_r_files("/home/john/topics/minimum_wage/analysis")
used_packages = get_all_used_packages(r_files)
installed_packages = keyify(get_installed_packages())

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('replication_template.md')

A = AnalyticsFiles('/home/john/topics/minimum_wage/analysis')

variables = dict({})
variables["analytic_file_names"] = A.file_names()
variables["notice_about_replication"] = notice_about_replication
variables["r_version"] = get_r_version()
variables["project_name"] = "Price Floors and Employer Preferences: Evidence from a Minimum Wage Experiment"
variables["date"] = datetime.date.today().strftime("%B %d, %Y")
variables["datasets"] = A.data_files()
variables["used_packages"] = used_packages
variables["docker_section"] = create_docker_section(used_packages, installed_packages, include_version = True)
rendered_template = template.render(variables)

with open('rendered_template.md', 'w') as f:
    f.write(rendered_template)

subprocess.call(["pandoc", "-o", "replication.pdf", "rendered_template.md"])

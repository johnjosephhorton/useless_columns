import os 
import subprocess
import json 

def get_r_version():
    try:
        result = subprocess.run(['R', '--version'], capture_output=True, text=True)
        output_lines = result.stdout.splitlines()
        version_line = output_lines[0].strip()
        version = version_line.split()[2]
        return version
    except (FileNotFoundError, IndexError):
        return None


def get_r_files(path, depth = 1):
    "get all the R files in the passed-to path; doesn't go deeper than depth 1"
    r_files = []
    for file in os.listdir(path):
            if file.endswith(".R"):
                 r_files.append(os.path.join(path, file))
    return r_files  

def cleanup(library_line):
    "gets rid of whitespace and library( and require( and ) and stuff"
    return library_line.lstrip().rstrip().replace("library(", "").replace("require(", "").replace(")", "").replace('"', '')

def get_libraries(r_file):
    "get all the libraries that are loaded in the passed-to R file"
    libraries = []
    with open(r_file) as f:
        for line in f:
            if line.lstrip().startswith("library(") or line.lstrip().startswith("require("):
                libraries.append(cleanup(line))
    return libraries

def get_all_used_packages(r_files):
    "get all the packages used in the passed-to R files"
    all_packages = []
    for r_file in r_files:
        all_packages.extend(get_libraries(r_file))
    return sorted(list(set(all_packages)), key = str.lower)

def package_details(package):
    # using subprocess, get the details of the passed-to package
    r_cmd = f"""
    desc <- packageDescription("{package}")
    desc_list <- unclass(desc)
    desc_json <- jsonlite::toJSON(desc_list, pretty = TRUE)
    cat(desc_json)
    """
    result = subprocess.run(["Rscript", "-e", r_cmd], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_installed_packages():
    # using subprocess, get all the installed packages on the system 
    r_cmd = """
    installed.packages.df <- as.data.frame(installed.packages())
    json_str <- jsonlite::toJSON(installed.packages.df, dataframe = "rows", pretty = TRUE)
    cat(json_str)
    """
    result = subprocess.run(["Rscript", "-e", r_cmd], capture_output=True, text=True)
    installed_packages_list = json.loads(result.stdout)
    for package in installed_packages_list:
        details = package_details(package["Package"])
        for key in details:
            if key not in package:
                package[key] = details[key]
    return installed_packages_list

def keyify(list_of_packages):
    # the packages are a list of dictionaries; this turns into a dictionary of dictionaries
    return {package["Package"]: package for package in list_of_packages}

def create_docker_line(package, repo = 'http://cran.us.r-project.org', version = None):
    # create the docker line for the passed-to package
    # if version is None, then the latest version if installed
    # if the package as a "Repository" key, then it's on CRAN; otheriwse assumed GitHub
    details = package_details(package)
    if 'Repository' in details: # indicates it's on CRAN
        if version:
            return f"RUN Rscript -e \"remotes::install_version('{package}', version = '{version}', repos = '{repo}')\""
        else:
            return f"RUN Rscript -e \"install.packages('{package}', repos='{repo}')\""
    else:
        # assuming on GitHub
        github_user = details["RemoteUsername"][0]
        install_line = f"{github_user}/{package}"
        return f"RUN Rscript -e \"remotes::install_github('{install_line}')\""

def create_docker_section(used_packages, installed_packages, include_version = True):
    "create the docker section of the Dockerfile"
    docker_section = []
    for package_name in used_packages:
        package = installed_packages[package_name]
        if include_version: 
            docker_section.append(create_docker_line(package_name, version = package["Version"]))
        else:
            docker_section.append(create_docker_line(package_name))
    return "\n".join(docker_section)
    
if __name__ == "__main__":
    path = "/home/john/topics/minimum_wage/analysis"
    r_files = get_r_files("/home/john/topics/minimum_wage/analysis")
    used_packages = get_all_used_packages(r_files)
    installed_packages = keyify(get_installed_packages())
    print(create_docker_section(used_packages, installed_packages, include_version = True))

    print(create_docker_section(used_packages, installed_packages, include_version = False))



# Overview
{{project_name }}

# Replication 

{{ notice_about_replication }}

{{ date }}

# Code 

```
/writeup
/analysis
/data
```

# Analytic files 

{% for file_name in analytic_file_names %}
1. {{ file_name }}
{% endfor %}

# Datasets used

{% for dataset in datasets %}
1. {{dataset}}
{% endfor %}

# R version 

{{ r_version }}

# R packages

{% for package in used_packages %}
1. {{package}}
{% endfor %}

```
{{docker_section}}
```

# Instructions for replication 



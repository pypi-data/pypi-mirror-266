from collections import Counter
from datetime import datetime

from vijil.evaluations.options import PROBES_DIMENSIONS_MAPPING

def format_datetime(datetime_str):
    """Format datetime from API response."""
    if datetime_str:
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y/%m/%d %H:%M")
        except ValueError:
            return datetime_str
    else:
        return datetime_str

def find_job_by_task_id(job_list, target_task_id):
    for job in job_list:
        if job.get('id') == target_task_id:
            return job
    return None 

def generate_default_job_name(username, model_hub, model_name):
    current_date = datetime.now().strftime("%m%d%Y")
    current_timestamp = datetime.now().strftime("%H%M%S")
    job_name = '_'.join([username, model_hub, model_name, current_date, current_timestamp]).replace(" ", "")
    return job_name

def get_dimensions_from_probe_groups(probe_groups):
    # Cleaning up empty strings here
    probe_groups = [i for i in probe_groups if i]
    
    mapped_dimensions = []
    
    for group in probe_groups:
        for dimension, probes in PROBES_DIMENSIONS_MAPPING.items():
            dimension = dimension.capitalize()
            if group in probes and dimension not in mapped_dimensions:
                mapped_dimensions.append(dimension)
                continue
    
    return sorted(mapped_dimensions)

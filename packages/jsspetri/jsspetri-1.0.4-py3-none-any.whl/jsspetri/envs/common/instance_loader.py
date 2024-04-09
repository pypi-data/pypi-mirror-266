import os
import pandas as pd

def load_instance_raw(instance_id):
    """
    Load raw instance data from a file.

    Parameters:
        instance_id (str): The identifier of the instance to load.

    Returns:
        pandas.DataFrame: The raw instance data.
        tuple: A tuple containing the number of jobs, number of machines, and number of features.
    """
    instance_path = os.path.join(os.path.dirname(__file__), "instances", instance_id)
    data = []
    try:
        with open(instance_path, 'r') as file:
            for line in file:
                elements = line.strip().split()
                data.append(elements)
           # print(f"Instance '{instance_id}' is loaded.")
    except FileNotFoundError:
        print(f"The file '{instance_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    raw_instance = pd.DataFrame(data)
    n_job, n_machine = tuple(raw_instance.iloc[0].dropna().astype(int))
    n_features = int((raw_instance.shape[1] - (n_machine * 2)) / n_machine) + 1
    raw_instance = raw_instance.drop(0).apply(pd.to_numeric, errors='coerce')
    
    max_bound=raw_instance.max().max()
    return raw_instance, (n_job, n_machine, n_features,max_bound)

def load_instance(instance_id):
    """
    Load instance data from a file and organize it into a structured format.

    Parameters:
        instance_id (str): The identifier of the instance to load.

    Returns:
        list: A list containing dictionaries representing the operation sequence for each job.
        tuple: A tuple containing the number of jobs, number of machines, and number of features.
    """
    raw_instance, (n_job, n_machine, n_features ,max_bound) = load_instance_raw(instance_id)
    instance = []
    for job_index in range(raw_instance.shape[0]):   
        job = {}
        for op_index in range(0, raw_instance.shape[1], n_features + 1):
            key = raw_instance.iloc[job_index, op_index]
            values = list(raw_instance.iloc[job_index, op_index + 1: op_index + n_features + 1]) 
            job[key] = values      
        instance.append(job)
           
    return instance, (n_job, n_machine, n_features ,max_bound)

# %% Test
if __name__ == "__main__":
    
     instance,size = load_instance("ta01X1")
     n_job, n_machine, n_features ,max_bound=size
     print(n_job, n_machine, n_features ,max_bound)
     
   
    





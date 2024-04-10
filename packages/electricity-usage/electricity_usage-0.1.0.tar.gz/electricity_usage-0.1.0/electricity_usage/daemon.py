import json
import threading
import os
import subprocess
import datetime
import pytimeparse
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from electricity_usage import job
from electricity_usage import em_data


class Daemon:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, em_API_key, area, input_dir):
        if not hasattr(self, 'initialized'):
            self.jobs = []  # List to store jobs
            self.lock = threading.Lock()
            self.initialized = True
            self.next_job_id = 1  # Added variable for job ID
            self.stop_event = threading.Event()  # Event for stopping the Daemon thread
            self.em_API_key = em_API_key
            self.area = area
            self.input_dir = input_dir

            # Watchdog Setup
            self.event_handler = CustomFileSystemEventHandler(self)
            self.observer = Observer()
            self.observer.schedule(self.event_handler, path=input_dir, recursive=False) #recursive
            self.observer.start()


    # The run method runs as a daemon process, checking run conditions and executing command lines 
    def run(self):
        while not self.stop_event.is_set():
            #print("Daemon is running...")
            
            power_production, power_consumption = em_data.get_power_data(self.area, self.em_API_key)
            #print(power_production, power_consumption)

            # Execute command line when power is available
            if power_production is not None and power_consumption is not None:
                if power_consumption < power_production:
                    # Run processes
                    with self.lock:
                        for job_instance in self.jobs:
                            commandline = job_instance.commandline
                            job_id = job_instance.job_id
                            print(f"Executing commandline for Job {job_id}: {commandline}")
                            # Execute the command line
                            subprocess.run(commandline, shell=True, check=True)
                            # Remove the job from the list self.jobs so it's not executed again
                            self.jobs.remove(job_instance)

            # Execute command line to meet the deadline
            with self.lock:
                for job_instance in self.jobs:  
                    # Check if latest_starting_point is less than or equal to the current time
                    if job_instance.latest_starting_point <= datetime.datetime.now():
                        commandline = job_instance.commandline
                        job_id = job_instance.job_id
                        print(f"Executing commandline for Job {job_id}: {commandline}")
                        # Execute the command line
                        subprocess.run(commandline, shell=True, check=True)
                        # Remove the job from the list self.jobs so it's not executed again
                        self.jobs.remove(job_instance)

            # time.sleep(900)
            self.stop_event.wait(timeout=10)

        self.observer.stop()  # End Observer thread
        self.observer.join()  # Wait until the Observer thread ends
        #print("Daemon Terminated")



    # the stop method terminates the run method by setting a stop_event and performs directory cleanup 
    def stop(self):
        self.stop_event.set()  # Set Stop Event to end the Daemon thread
        try:
            # Check if the folder exists
            if os.path.exists(self.input_dir):
                shutil.rmtree(self.input_dir) #deletes the directory and all its contents recursively
                #print("All files in the folder have been deleted successfully.")
                
            else:
                print(f"The folder {self.input_dir} does not exist.")
        except Exception as e:
            print(f"Error deleting files: {str(e)}")



    # the process_json_file method uses data to create jobs
    def process_json_file(self, file_path):
        #print("Daemon process_json_file method executed")
        try:
            with open(file_path, 'r') as file:
                params = json.load(file)
        
            # Read parameters
            #estimate = float(params.get('estimate'))
            estimate = params.get('estimate') 
            deadline = datetime.datetime.strptime(params.get('deadline'), "%Y-%m-%d %H:%M:%S")
            commandline = params.get('commandline')

            if estimate and deadline and commandline:
                with self.lock:
                    latest_starting_point = deadline - datetime.timedelta(seconds=pytimeparse.parse(estimate))

                    # Increment job_id before use to ensure it's consecutive
                    job_id = self.next_job_id
                    self.next_job_id = self.next_job_id+1
                    new_job=f"job{job_id}" # Jobs are named as follows: job1, job2, ...
                    new_job = job.Job(job_id, estimate, deadline, latest_starting_point, commandline)
                    self.jobs.append(new_job) # Add the job to the jobs list
                    #print(f"Job {job_id} added.")
                    
        except Exception as e:
            print("Something went wrong. Please check your input Parameters (estimate, deadline, commandline)")
    


# the CustomFileSystemEventHandler is used for process communication
# It uses the watchdog library to register new files in the input directory,
# on registered daemon methods are executed 
class CustomFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, daemon_instance):
        super().__init__()
        self.daemon_instance = daemon_instance

    def on_created(self, event):
        if event.is_directory:
            #print("Event recognized")
            return
        elif event.event_type == 'created':
            if event.src_path.endswith('.json'): # Call Daemon's process_json_file method
                #print(f"New JSON file detected: {event.src_path}")
                self.daemon_instance.process_json_file(event.src_path)     
            elif event.src_path.endswith('txt'): # Call Daemon's stop method
                #print("Stop token file detected. Stopping daemon.")
                self.daemon_instance.stop() 

import datetime

# This class serves as a data structure for storing job parameters.
class Job:
    def __init__(self, job_id, estimate, deadline, latest_starting_point, commandline):
        self.job_id = job_id
        self.estimate = estimate
        self.deadline = deadline
        self.latest_starting_point = latest_starting_point 
        self.commandline = commandline


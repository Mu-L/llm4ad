# Module Name: JSSPEvaluation
# Last Revision: 2025/2/16
# Description: Evaluates the Job Shop Scheduling Problem (JSSP).
#              Given a set of jobs and machines, the goal is to schedule jobs on machines
#              in a way that minimizes the total makespan (completion time of all jobs).
#              This module is part of the LLM4AD project (https://github.com/Optima-CityU/llm4ad).
#
# Parameters:
#    - timeout_seconds: Maximum allowed time (in seconds) for the evaluation process: int (default: 20).
#    - n_instance: Number of problem instances to generate: int (default: 16).
#    - n_jobs: Number of jobs to schedule: int (default: 10).
#    - n_machines: Number of machines available: int (default: 5).
# 
# References:
#   - Fei Liu, Rui Zhang, Zhuoliang Xie, Rui Sun, Kai Li, Xi Lin, Zhenkun Wang, 
#       Zhichao Lu, and Qingfu Zhang, "LLM4AD: A Platform for Algorithm Design 
#       with Large Language Model," arXiv preprint arXiv:2412.17287 (2024).
#
# ------------------------------- Copyright --------------------------------
# Copyright (c) 2025 Optima Group.
# 
# Permission is granted to use the LLM4AD platform for research purposes. 
# All publications, software, or other works that utilize this platform 
# or any part of its codebase must acknowledge the use of "LLM4AD" and 
# cite the following reference:
# 
# Fei Liu, Rui Zhang, Zhuoliang Xie, Rui Sun, Kai Li, Xi Lin, Zhenkun Wang, 
# Zhichao Lu, and Qingfu Zhang, "LLM4AD: A Platform for Algorithm Design 
# with Large Language Model," arXiv preprint arXiv:2412.17287 (2024).
# 
# For inquiries regarding commercial use or licensing, please contact 
# http://www.llm4ad.com/contact.html
# --------------------------------------------------------------------------


from __future__ import annotations
from typing import Any, List, Tuple, Callable
import numpy as np
import matplotlib.pyplot as plt

from llm4ad.base import Evaluation
from llm4ad.task.optimization.jssp_construct.get_instance import GetData
from llm4ad.task.optimization.jssp_construct.template import template_program, task_description

__all__ = ['JSSPEvaluation']

class JSSPEvaluation(Evaluation):
    """Evaluator for Job Shop Scheduling Problem."""

    def __init__(self, 
                 timeout_seconds=20,
                 n_instance = 16,
                 n_jobs = 50,
                 n_machines = 10,
                 **kwargs):
        """
        Args:
            None
        Raises:
            AttributeError: If the data key does not exist.
            FileNotFoundError: If the specified data file is not found.
        """
        super().__init__(
            template_program=template_program,
            task_description=task_description,
            use_numba_accelerate=False,
            timeout_seconds=timeout_seconds
        )

        self.n_instance = n_instance
        self.n_jobs = n_jobs
        self.n_machines = n_machines
        getData = GetData(self.n_instance, self.n_jobs, self.n_machines)
        self._datasets = getData.generate_instances()

    def evaluate_program(self, program_str: str, callable_func: Callable) -> Any | None:
        return self.evaluate(callable_func)


    def plot_solution(self, schedule: List[List[Tuple[int, int, int]]], n_jobs: int, n_machines: int):
        """
        Plots the schedule as a Gantt chart.

        Args:
            schedule: The schedule generated by select_next_operation.
            n_jobs: Number of jobs.
            n_machines: Number of machines.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create a color map for the jobs
        colors = plt.cm.get_cmap('tab10', n_jobs)

        # Iterate over each job and its operations
        for job_idx, operations in enumerate(schedule):
            for operation in operations:
                machine, start_time, end_time = operation
                # Plot the operation as a horizontal bar with a specific color
                ax.barh(machine, end_time - start_time, left=start_time, 
                        color=colors(job_idx), label=f'Job {job_idx}')

        # Customize the plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_yticks(range(n_machines))
        ax.set_yticklabels([f'Machine {i}' for i in range(n_machines)])
        ax.set_title('Scheduling Gantt Chart')

        # Add a legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))  # Remove duplicate labels
        ax.legend(by_label.values(), by_label.keys(), title="Jobs", bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.show()

    def schedule_jobs(self, processing_times, n_jobs, n_machines,eva):
        """
        Schedule jobs on machines using a greedy constructive heuristic.

        Args:
            processing_times: A list of lists representing the processing times of each job on each machine.
            n_jobs: Number of jobs.
            n_machines: Number of machines.

        Returns:
            The makespan, which is the total time required to complete all jobs.
        """
        # Initialize the current status of each machine and job
        machine_status = [0] * n_machines  # Time each machine is available
        job_status = [0] * n_jobs  # Time each job is available
        operation_sequence = [[] for _ in range(n_jobs)]  # Sequence of operations for each job

        # Initialize the list of all operations
        all_operations = []
        for job_id in range(n_jobs):
            for machine_id in range(n_machines):
                all_operations.append((job_id, machine_id, processing_times[job_id][machine_id]))

        # Schedule operations until all are completed
        while all_operations:
            # Determine feasible operations
            feasible_operations = []
            for operation in all_operations:
                job_id, machine_id, processing_time = operation
                if job_status[job_id] <= machine_status[machine_id]:
                    feasible_operations.append(operation)

            if len(feasible_operations)==0:
                next_operation = all_operations[0]
            else:
                # Determine the next operation to schedule
                next_operation = eva({'machine_status': machine_status, 'job_status': job_status}, feasible_operations)

            # Schedule the next operation
            job_id, machine_id, processing_time = next_operation
            start_time = max(job_status[job_id], machine_status[machine_id])
            end_time = start_time + processing_time
            machine_status[machine_id] = end_time
            job_status[job_id] = end_time
            operation_sequence[job_id].append((machine_id, start_time, end_time))

            # Remove the scheduled operation from the list of all operations
            all_operations.remove(next_operation)

        # Calculate the makespan (total time required to complete all jobs)
        makespan = max(job_status)
        return makespan, operation_sequence

    def evaluate(self, eva: Callable) -> float:
        """
        Evaluate the constructive heuristic for JSSP.
        
        Args:
            instance_data: List of tuples containing the processing times, number of jobs, and number of machines.
            n_ins: Number of instances to evaluate.
            n_jobs: Number of jobs.
            n_machines: Number of machines.
            eva: The constructive heuristic function to evaluate.
        
        Returns:
            The average makespan across all instances.
        """
        makespans = []
        
        for instance in self._datasets[:self.n_instance]:
            processing_times, n1, n2 = instance
            makespan,solution  = self.schedule_jobs(processing_times, n1, n2,eva)
            makespans.append(makespan)
        
        average_makespan = np.mean(makespans)
        return -average_makespan  # Negative because we want to minimize the makespan

if __name__ == '__main__':


    def determine_next_operation(current_status, feasible_operations):
        """
        Determine the next operation to schedule based on a greedy heuristic.

        Args:
            current_status: A dictionary representing the current status of each machine and job.
            feasible_operations: A list of feasible operations that can be scheduled next.

        Returns:
            The next operation to schedule, represented as a tuple (job_id, machine_id, processing_time).
        """
        # Simple greedy heuristic: choose the operation with the shortest processing time
        next_operation = min(feasible_operations, key=lambda x: x[2])
        return next_operation


    tsp = JSSPEvaluation()
    makespan = tsp.evaluate_program('_',determine_next_operation)
    print(makespan)
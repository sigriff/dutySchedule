"""
This module implements a linear programming model using the PuLP library for solving
the problem of assigning employees to duties and shifts  within a rotation period
with the objective function of maximising employee satisfaction.

Example usage:
Follow the 4 steps below.

1. Set up the basic parameters for the problem.  This involves providing lists of employees, duties, shfts and rotations,
as well as providing an initial dictionary of bids

e.g.
problem_name = "Sample Problem"
employees = ["Samuel_Brown","Noah_Chen","Belissica_Gellor"]
duties = ["Machine_Operation","Mail_Sorting","Scanning_and_Bar_Coding"]
shifts = ["Early","Late","Night"]
rotations = ["Week_1","Week_2","Week_3"]
bids = {("Samuel_Brown","Machine_Operation","Early"): 1.0,
        ("Samuel_Brown","Machine_Operation","Late"): 1.0,
        ("Samuel_Brown","Mail_Sorting","Night") : 1.0,
        ("Noah_Chen","Machine_Operation","Early"): 1.0,
        ("Noah_Chen","Mail_Sorting","Late"): 1.0,
        ("Noah_Chen","Mail_Sorting","Night") : 1.0,
        ("Belissica_Gellor","Machine_Operation","Early"): 1.0,
        ("Belissica_Gellor","Scanning_and_Bar_Coding","Late"): 1.0,
        ("Belissica_Gellor","Machine_Operation","Night") : 1.0
       }
sched = Scheduler(problem_name, employees, duties, shifts, rotations, bids)

2. Complete a bid dictionary and validate its entries.
sched.completeBids()

3. Set up the scheduling problem

sched.setupProblem()

4. Solve the problem
sched.solveProblem()

Author: Simon Griffiths
Date: 24-Nov-2023
Version: 1.0.0
"""
import pulp
import pandas as pd
from itertools import product

class Scheduler(object):
    """ 
    This class is the problem solver for the duty schedule project.  Its purpose is to
    wrap the PuLP API with methods specific to the Royal Mail scheduling problem 
    """
    def __init__(self, problem_name: str, employees: list, duties: list, shifts: list, rotations: list, bids: dict):
        """
        Class constructor.  This intialises the variables used for solving the linear regression problem.
        """
        # Initialise the decision variables and constraint variables for the problem
        #self.rotation_name = rotation_name
        self.employees = employees
        self.duties = duties
        self.shifts = shifts
        self.rotations = rotations
        self.bids = bids

        self.prob = None
        self.problem_name = problem_name
        self.allocations = {}

    def cleanAllocations(self):
        """
        Strips all the unecessary data from the allocations dictionary.  Then updates the bids
        variable in the allocations by comparing the allocations with the original bids 
        """
        # Create a dataframe from the allocations dictionary
        fields = []
        parsed_data = []
        for key, value in self.allocations.items():
            fields = key.split(",_")
            fields.append(value)
            parsed_data.append(fields)
        allocdf = pd.DataFrame(parsed_data, columns=["Employee", "Duty", "Shift", "Week", "Bid"])

        # Create a dataframe for the bids dictionary (but do not include no-bids)
        parsed_data = []
        for key, value in self.bids.items():
            if value > 0.0: # Ignore no-bids
                employee, duty, shift = key  # Unpack the tuple key
                parsed_data.append([employee, duty, shift, value])
        bidsdf = pd.DataFrame(parsed_data, columns=["Employee", "Duty", "Shift", "Bid"])

        # Clean the allocations data
        allocdf["Employee"] = allocdf["Employee"].str.strip("Allocation_\\(")
        allocdf["Employee"] = allocdf["Employee"].str.strip("'")
        allocdf["Employee"] = allocdf["Employee"].str.replace("_", " ")
        allocdf["Duty"] = allocdf["Duty"].str.strip("'")
        allocdf["Duty"] = allocdf["Duty"].str.replace("_", " ")
        allocdf["Shift"] = allocdf["Shift"].str.strip("'")
        allocdf["Week"] = allocdf["Week"].str.strip("')")
        allocdf["Week"] = allocdf["Week"].str.replace("_", " ")

        # Cleanse the bids data so values match with the allocations dataframe
        bidsdf["Employee"] = bidsdf["Employee"].str.replace("-"," ")
        bidsdf["Employee"] = bidsdf["Employee"].str.strip("'")
        bidsdf["Duty"] = bidsdf["Duty"].str.replace("-"," ")
        bidsdf["Duty"] = bidsdf["Duty"].str.strip("'")
        bidsdf["Shift"] = bidsdf["Shift"].str.strip("'")

        # The current values are allocations, not bids.  Set them all to 0.0
        # in preparation for the next step
        allocdf["Bid"] = 0.0

        # Compare the allocations to the original bids and update the allocaions-bid column
        # with an indicator of whether or not the employee made a bid for that allocation
        for row in bidsdf.itertuples():

            # find all corresponding allocations and update the bid value
            allocdf.loc[(allocdf["Employee"] == row.Employee) &
                        (allocdf["Duty"] == row.Duty )&
                        (allocdf["Shift"] == row.Shift ), "Bid"] = row.Bid

        # now put the cleansed allocations dictionary back together from the dataframe
        self.allocations = {(row["Employee"], row["Duty"], row["Shift"], row["Week"]): row["Bid"] for index, row in allocdf.iterrows()}

        #allocdf.to_csv("clean_allocations.csv", index=False)

    def completeBids(self):
        """
        The Objective Function needs a complete set of validated bids including "no-bids".
        Validations include: The employees, duties and shifts in the bids dictionary exist
        in the database; Each employee has provided at least 3 bids; and Each employee has
        provided at least one bid for each shift
        """
        # Check the validity of existing bids by checking the employee, duty and shift values are correct
        for (employee, duty, shift) in self.bids.keys():
            if employee not in self.employees or duty not in self.duties or shift not in self.shifts:
                raise ValueError(f"Bid contains invalid keys: {employee}, {duty}, {shift}")

        # Count the number of bid each employee has provided (total bids and bids per shift)
        bid_counts = {employee: 0 for employee in self.employees}
        early_bid_counts = {employee: 0 for employee in self.employees}
        late_bid_counts = {employee: 0 for employee in self.employees}
        night_bid_counts = {employee: 0 for employee in self.employees}
        for (employee, duty, shift) in self.bids.keys():
            bid_counts[employee] += 1
            if shift == "Early":
                early_bid_counts[employee] += 1
            if shift == "Late":
                late_bid_counts[employee] += 1
            if shift == "Night":
                night_bid_counts[employee] += 1
 
        # Check that each employee has provided at least 3 bids and at leat 1 early, 1 late and 1 night bid
        employees_with_not_enough_bids = [employee for employee, count in bid_counts.items() if count < 3]
        employees_missing_early_bid = [employee for employee, count in early_bid_counts.items() if count < 1]
        employees_missing_late_bid = [employee for employee, count in late_bid_counts.items() if count < 1]
        employees_missing_night_bid = [employee for employee, count in night_bid_counts.items() if count < 1]
        employees_with_incorrect_bids = {}

        if employees_with_not_enough_bids:
            employees_with_incorrect_bids["Employees with less than 3 bids"] = employees_with_not_enough_bids
        if employees_missing_early_bid:
            employees_with_incorrect_bids["Employees without an Early bid"] = employees_missing_early_bid
        if employees_missing_late_bid:
            employees_with_incorrect_bids["Employees without a Late bid"] = employees_missing_late_bid
        if employees_missing_night_bid:
            employees_with_incorrect_bids["Employees without a Night bid"] = employees_missing_night_bid

        if employees_with_incorrect_bids:
            raise ValueError(f"Employees with incorrect bids: {employees_with_incorrect_bids}")

        # Complete the bids with missing no-bids
        all_combinations = product(self.employees, self.duties, self.shifts)
        for combination in all_combinations:
            if combination not in self.bids:
                self.bids[combination] = 0.0        

    def setUpProblem(self):
        """
        This method uses the PuLP library to build the optimisation problem.  The problem
        is a scheduling challenge of allocating employees to duties in shifts over a 3 week
        rotation period.  Employees make bids for their preferred duty in a shift.

        The objective function is to maximise satisfaction where satisfaction is the sum of
        allocations x bids for all employees. (An allocation is a binary variable 1 if the
        employees has been allocated to a shift-duty and 0 if not). A bid is a score for a
        combination of an employee's requested shift and duty.
        
        There are several constraints to the problem:
        1. For each employee and rotation exactly one shift and duty combination must be allocated
        2. Over a 3 week rotation, an employee must be assigned exactly on early duty, one late
           duty and one night duty
        3. Within a single week, each shift and duty combination may have only one employee
           allocated to it
        """
        
       # Decision Variables
        allocations = pulp.LpVariable.dicts("Allocation", ((e, d, sh, r)
            for e in self.employees 
            for d in self.duties
            for sh in self.shifts
            for r in self.rotations),
            cat="Binary")

        # Create the linear optimisation problem
        self.prob = pulp.LpProblem(self.problem_name, pulp.LpMaximize)

        # Objective Function
        self.prob += pulp.lpSum(self.bids[(e, d, sh)] * allocations[(e, d, sh, r)] 
                        for e in self.employees
                        for d in self.duties
                        for sh in self.shifts
                        for r in self.rotations)

        ## Constraints

        # Each employee must be allocated exactly one duty and shift combination per rotation week
        for e in self.employees:
            for r in self.rotations:
                constraint = pulp.LpConstraint(
                    e=pulp.lpSum(allocations[(e, d, sh, r)] for d in self.duties for sh in self.shifts),
                    sense=pulp.LpConstraintEQ,
                    rhs=1,
                    name=f"employee_{e}_rotation_{r}_constraint" 
                )
                self.prob.addConstraint(constraint)
                
        # ALTERNATIVE EXAMPLE OF ADDING A CONSTRAINT
        #for e in self.employees:
        #    for r in self.rotations:
        #        self.prob += pulp.lpSum(allocations[(e, d, sh, r)] for d in self.duties
        #                                                           for sh in self.shifts) == 1

        # Each employee must be assigned one early, late, and night duty over the rotation period
        for e in self.employees:
            for sh in self.shifts:
                constraint = pulp.LpConstraint(
                    e=pulp.lpSum(allocations[(e, d, sh, r)] for d in self.duties for r in self.rotations),
                    sense=pulp.LpConstraintEQ,
                    rhs=1,
                    name=f"employee_{e}_shift_{sh}_constraint"
                )
                self.prob.addConstraint(constraint)

        # Each duty, shift, and rotation combination may have only one employee allocated
        for d in self.duties:
            for sh in self.shifts:
                for r in self.rotations:
                    constraint = pulp.LpConstraint(
                        e=pulp.lpSum(allocations[(e, d, sh, r)] for e in self.employees),
                        sense=pulp.LpConstraintLE,
                        rhs=1,
                        name=f"duty_{d}_shift_{sh}_rotation_{r}_constraint"
                    )
                    self.prob.addConstraint(constraint)

    def solveProblem(self):
        """
        Check a problem has been set up and solve it.
        """
        if self.prob is not None:
            self.prob.solve()

        # Create a dictionary of the allocations
        for v in self.prob.variables():
            if v.varValue > 0:
                self.allocations[v.name] = v.varValue

if __name__ == "__main__":
    print("This is the Scheduler module")
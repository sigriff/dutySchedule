"""
This is the main scheduling program.

Author: Simon Griffiths
Date: 29-Nov-2023
"""
from src.database.scheduleDb import DbUtility
import pandas as pd
#import os
from src.app.scheduler import Scheduler
from src.app.visualiser import BidPreferenceAnalysis
from src.app.visualiser import EmployeeAllocations
import random

def createAllocations(dbutil: DbUtility, bids: dict) -> dict:
    """
    Takes in a dictionary of bids, reads employees, duties, shifts and rotations
    from the database and creates allocations using the scheduler
    """
    # Get lists of Employee, Duty, Shift and Rotation objects.  Replace any spaces with '-'
    # as it makes the results of the allocations easier to read
    try:
        employees = dbutil.readEmployeesAsFlatList(separator="-")
        duties = dbutil.readDutiesAsFlatList(separator="-")
        shifts = dbutil.readShiftsAsFlatList(separator="-")
        weeks = dbutil.readRotationWeeksAsFlatList(separator="-")
    except Exception as e:
        print(f"\nAn error occurred reading from the dictionary\n{e}\n")
        return {} # just return an empty dictionary

    # Replace any spaces in the bids to match the lists above
    updated_bids = {}
    for key, value in bids.items():
        updated_key = tuple(element.replace(' ', '-') for element in key)
        updated_bids[updated_key] = value
    
    # randomise the order of the employees.  This is so that multiple
    # runs of the scheduler will produce different allocations using
    # the same bids (if there are different options)
    random.shuffle(employees)
    
    # create a scheduler, complete the bids dictionary with no-bids,
    # set up the scheduling problem and solve it
    try:
        sched = Scheduler("SampleAllocations", employees, duties, shifts, weeks, updated_bids)
        sched.completeBids()
        sched.setUpProblem()
        sched.solveProblem()
    except Exception as e:
        print(f"\nAn error occurred during scheduling\n{e}\n")
        return {} # just return an empty dictionary

    # clean up the allocations data
    sched.cleanAllocations()

    #print(f"\n\nallocations =\n{sched.allocations}")

    return sched.allocations

def createRandomBids(dbutil: DbUtility) -> None:
    """
    Create a sample of random bids and offer the user a choice of saving it to a csv, or ignoring it
    """
    # Create an instance of DBUtility and return a dictionary of randomised bids
    try:
        bids = dbutil.createRandomBids()
    except Exception as e:
        print(f"\nAn error occurred creating bids, please check the employees, duties and shifts data in the database schema {schema}\n{e}\n")
        return

    if len(bids) < 1:
        print(f"\nNo bids were created, please check the employees, duties and shifts data in the database schema {schema}\n")
        return

    # Pretty print the bids to the CLI, using max length variables to neaten up the print
    max_name_length = max(len(employee) for employee, duty, shift in bids.keys())
    max_duty_length = max(len(duty) for employee, duty, shift in bids.keys())
    for key in bids:
        employee, duty, shift = key
        print(f"{employee:<{max_name_length}} {duty:<{max_duty_length}} {shift}")
    print(f"\nBids count = {len(bids)}\n")
    
    # ask the user if they want to accept or modify these bids
    sub_prompt = (
        "Choose from the following: (default 2. Ignore bids)\n"
        "1. Download bids to csv\n"
        "2. Ignore bids\n"
        ">>>"
    )
    try:
        sub_option = int(input(sub_prompt))
    except:
        print("\nBids ignored\n")
        return

    # Sub Option 1 - Download bids to csv
    if sub_option == 1:
        dbutil.saveBidsDictAsCsv(bids)
        print("\nBids saved to .\data\\bids.csv\n")

    else:
        print("\nBids ignored\n")
        return

def main(option, schema) -> None:
    """
    Handle options from the CLI
    """
    # Create an instance of the Scheduler Db Utility
    try:
        dbutil = DbUtility(schema)
    except Exception as e:
        print(f"\nThere was an error connecting to the database:\n{e}\n")
        return

    # Create a random sample of bids and provide the option
    # to save them as a csv
    if option == 1:
        createRandomBids(dbutil)

    # Upload bids, create allocations and save them as a csv
    elif option == 2:
        bids = dbutil.readBidsDictFromCsv()
        allocations = createAllocations(dbutil, bids)
        if len(allocations) > 0: # Only save if there are allocations
            dbutil.saveAllocationsDictAsCsv(allocations)

    # Show Bid Preference Analysis
    elif option == 3:
        allocations = dbutil.readAllocationsDictFromCsv()
        bpa = BidPreferenceAnalysis(allocations)
        bpa.createVisualisation()

    # Show Show Employee Allocations
    elif option == 4:
        allocations = dbutil.readAllocationsDictFromCsv()
        duties = dbutil.readDutiesAsFlatList()
        shifts = dbutil.readShiftsAsFlatList()
        weeks = dbutil.readRotationWeeksAsFlatList()
        ea = EmployeeAllocations(allocations=allocations, duties=duties, shifts=shifts, weeks=weeks)
        ea.createVisualisation()

    # Database Admin Functions
    elif option == 5:
        print("\nPlease run module ..\src\database\scheduleDb.py and follow the instruction in the CLI\n")

if __name__ =="__main__":
    """
    Command Line Interface (CLI)
    """
    # set the database schema
    schema = input("Enter a schema name (default: rm_scheduling): ")
    if schema in (None, ""):
        schema = "rm_scheduling"
    print(f"Schema set to: {schema}\n")

    # create a prompt for the CLI
    prompt = (
        "Choose from the following:\n"
        "1. Create a random sample of bids\n"
        "2. Create allocations\n"
        "3. Show Bid Preference Analysis\n"
        "4. Show Employee Allocations\n"
        "5. Perform Database Admin Functions\n"
        "6. Exit\n"
        ">>>"
    )

    # Present the CLI options to the user
    while True:
        try:
            option = int(input(prompt))
        except:
            print("Invalid option chosen. Exiting...\n")
            break

        if option in (1, 2, 3, 4, 5):
            main(option, schema)
        else:
            print("Exiting...\n")
            break

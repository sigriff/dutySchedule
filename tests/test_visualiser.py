"""
Unit tests for the Visualiser module

Example usage python -m unittest tests/test_visualiser.py
Author: Simon Griffiths
Date: 04-Dec-2023
Version: 1.0.0
"""
import unittest
from src.app.visualiser import BidPreferenceAnalysis
from src.app.visualiser import EmployeeAllocations

class UnitTestVisualiser(unittest.TestCase):
    """
    Unit tests to validate the classes and methods of the visualiser module
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.  Initialises test data for the unit tests
        """
        super().__init__(*args, **kwargs)

        # Test set of allocation dictionary data
        self.test_allocations = {
("10 Ann Michele van der Sar", "Handling Oversized Mail", "Early", "Week 2"):1.0,
("10 Ann Michele van der Sar", "Handling Oversized Mail", "Night", "Week 3"):1.0,
("10 Ann Michele van der Sar", "Problem Resolution", "Late", "Week 1"):0.0,
("11 Ava Patel", "Cleaning and maintenance", "Late", "Week 2"):0.0,
("11 Ava Patel", "Handling Oversized Mail", "Early", "Week 3"):0.0,
("11 Ava Patel", "Handling Specialised Items", "Night", "Week 1"):1.0,
("12 Kimble Rand", "Handling Specialised Items", "Late", "Week 1"):1.0,
("12 Kimble Rand", "Quality Control Checks", "Early", "Week 3"):1.0,
("12 Kimble Rand", "Scanning and Bar Coding", "Night", "Week 2"):0.0,
("13 Aiden Martin", "Housekeeping", "Night", "Week 2"):0.0,
("13 Aiden Martin", "Inventory Management", "Late", "Week 1"):0.0,
("13 Aiden Martin", "Mail Sorting", "Early", "Week 3"):0.0,
("14 Alexander Muller", "Handling Specialised Items", "Early", "Week 2"):1.0,
("14 Alexander Muller", "Handling Specialised Items", "Late", "Week 3"):0.0,
("14 Alexander Muller", "Housekeeping", "Night", "Week 1"):1.0,
("15 Ethan Smith", "Data Entry", "Late", "Week 3"):1.0,
("15 Ethan Smith", "Loading and Unloading", "Early", "Week 2"):0.0,
("15 Ethan Smith", "Mail Sorting", "Night", "Week 1"):0.0,
("16 Emily Smith", "Handling Oversized Mail", "Early", "Week 1"):1.0,
("16 Emily Smith", "Inventory Management", "Late", "Week 3"):1.0,
("16 Emily Smith", "Safety Compliance", "Night", "Week 2"):1.0,
("17 Muhammad Ali", "Coordination with Transportation", "Early", "Week 1"):0.0,
("17 Muhammad Ali", "Package Inspection", "Night", "Week 3"):1.0,
("17 Muhammad Ali", "Safety Compliance", "Late", "Week 2"):0.0,
("18 Sophie Johnson", "Customer Service", "Late", "Week 2"):0.0,
("18 Sophie Johnson", "Loading and Unloading", "Early", "Week 1"):1.0,
("18 Sophie Johnson", "Machine Operation", "Night", "Week 3"):1.0,
("19 Rajesh Patel", "Cleaning and maintenance", "Late", "Week 3"):1.0,
("19 Rajesh Patel", "Package Inspection", "Early", "Week 2"):1.0,
("19 Rajesh Patel", "Scanning and Bar Coding", "Night", "Week 1"):1.0,
("1 Samuel Brown", "Data Entry", "Early", "Week 1"):0.0,
("1 Samuel Brown", "Handling Oversized Mail", "Night", "Week 2"):1.0,
("1 Samuel Brown", "Package Inspection", "Late", "Week 3"):0.0,
("20 Olivia Brown", "Handling Oversized Mail", "Night", "Week 1"):1.0,
("20 Olivia Brown", "Problem Resolution", "Late", "Week 3"):0.0,
("20 Olivia Brown", "Safety Compliance", "Early", "Week 2"):1.0}

        # Test set of duty list data
        self.test_duties = ["Bagging and Bundling", "Coordination with Transportation", "Safety Compliance", "Customer Service", "Inventory Management", "Machine Operation", "Quality Control Checks", 
                            "Record Keeping", "Data Entry", "Housekeeping", "Loading and Unloading", "Mail Sorting", "Scanning and Bar Coding", "Cleaning and maintenance", "Handling Oversized Mail", 
                            "Handling Specialised Items", "Package Inspection", "Labeling", "Problem Resolution"]
        self.test_duties.sort()

        self.test_shifts= ["Early", "Late", "Night"]

        self.Test_weeks = ["Week 1", "Week 2", "Week 3"]

    def test_BidPreferenceAnalysis(self):
        """
        
        """
        bpa = BidPreferenceAnalysis(allocations = self.test_allocations)
        bpa.createVisualisation()

    def test_EmployeeAllocations(self):
        """
        """
        ea = EmployeeAllocations(allocations = self.test_allocations, duties = self.test_duties, shifts = self.test_shifts, weeks = self.Test_weeks)
        ea.createVisualisation()
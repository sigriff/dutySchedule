"""
Unit tests for the scheduler module

Example usage python -m unittest tests/test_scheduler.py
Author: Simon Griffiths
Date: 24-Nov-2023
Version: 1.0.0
"""
import unittest
from src.app.scheduler import Scheduler
import pandas as pd

class UnitTestScheduler(unittest.TestCase):
    """
    Unit tests to validate the methods of the Scheduler class
    """
    def setUp(self) -> None:
        """
        Setup the test data for each unit test
        """

        # Set up some test data
        self.problem_name = "Unit Test Scheduler"
        self.employees = ["01 Samuel Brown","02 Noah Chen","03 Olivia Dubois", "04 Belissica Gellor", "05 Max Ivanov", "06 Zoe Jones", "07 Emma Nguyen", "08 Mia Rossi", "09 Carlos Garcia"]
        self.duties = ["Machine Operation","Mail Sorting","Scanning and Bar Coding"]
        self.shifts = ["Early","Late","Night"]
        self.rotations = ["Week 1", "Week 2", "Week 3"]
        self.bids = {("01 Samuel Brown", "Machine Operation", "Early"): 1.0,
                     ("01 Samuel Brown", "Scanning and Bar Coding", "Late"): 1.0,
                     ("01 Samuel Brown", "Mail Sorting", "Night") : 1.0,
                     ("02 Noah Chen", "Machine Operation", "Early"): 1.0,
                     ("02 Noah Chen", "Scanning and Bar Coding", "Late"): 1.0,
                     ("02 Noah Chen", "Mail Sorting", "Night") : 1.0,
                     ("03 Olivia Dubois", "Machine Operation", "Early"): 1.0,
                     ("03 Olivia Dubois", "Scanning and Bar Coding", "Late"): 1.0,
                     ("03 Olivia Dubois", "Mail Sorting", "Night") : 1.0,
                     ("04 Belissica Gellor", "Machine Operation", "Early"): 1.0,
                     ("04 Belissica Gellor", "Scanning and Bar Coding", "Late"): 1.0,
                     ("04 Belissica Gellor", "Mail Sorting", "Night") : 1.0,
                     ("05 Max Ivanov", "Machine Operation", "Early"): 1.0,
                     ("05 Max Ivanov", "Scanning and Bar Coding", "Late"): 1.0,
                     ("05 Max Ivanov", "Mail Sorting", "Night") : 1.0,
                     ("06 Zoe Jones", "Machine Operation", "Early"): 1.0,
                     ("06 Zoe Jones", "Scanning and Bar Coding", "Late"): 1.0,
                     ("06 Zoe Jones", "Mail Sorting", "Night") : 1.0,
                     ("07 Emma Nguyen", "Machine Operation", "Early"): 1.0,
                     ("07 Emma Nguyen", "Scanning and Bar Coding", "Late"): 1.0,
                     ("07 Emma Nguyen", "Mail Sorting", "Night") : 1.0,
                     ("08 Mia Rossi", "Machine Operation", "Early"): 1.0,
                     ("08 Mia Rossi", "Scanning and Bar Coding", "Late"): 1.0,
                     ("08 Mia Rossi", "Mail Sorting", "Night") : 1.0,
                     ("09 Carlos Garcia", "Machine Operation", "Early"): 1.0,
                     ("09 Carlos Garcia", "Scanning and Bar Coding", "Late"): 1.0,
                     ("09 Carlos Garcia", "Mail Sorting", "Night") : 1.0
                    }
        
        #Allocations result should be this:
        #Employee,Duty,Shift,Week,Bid
        #01 Samuel Brown,Machine Operation,Early,Week 2,1.0
        #01 Samuel Brown,Machine Operation,Night,Week 1,0.0
        #01 Samuel Brown,Scanning and Bar Coding,Late,Week 3,1.0
        #02 Noah Chen,Mail Sorting,Late,Week 3,0.0
        #02 Noah Chen,Scanning and Bar Coding,Early,Week 2,0.0
        #02 Noah Chen,Scanning and Bar Coding,Night,Week 1,0.0
        #03 Olivia Dubois,Machine Operation,Early,Week 1,1.0
        #03 Olivia Dubois,Machine Operation,Late,Week 2,0.0
        #03 Olivia Dubois,Mail Sorting,Night,Week 3,1.0
        #04 Belissica Gellor,Machine Operation,Late,Week 1,0.0
        #04 Belissica Gellor,Mail Sorting,Early,Week 3,0.0
        #04 Belissica Gellor,Mail Sorting,Night,Week 2,1.0
        #05 Max Ivanov,Machine Operation,Early,Week 3,1.0
        #05 Max Ivanov,Mail Sorting,Late,Week 2,0.0
        #05 Max Ivanov,Mail Sorting,Night,Week 1,1.0
        #06 Zoe Jones,Mail Sorting,Early,Week 1,0.0
        #06 Zoe Jones,Scanning and Bar Coding,Late,Week 2,1.0
        #06 Zoe Jones,Scanning and Bar Coding,Night,Week 3,0.0
        #07 Emma Nguyen,Machine Operation,Late,Week 3,0.0
        #07 Emma Nguyen,Scanning and Bar Coding,Early,Week 1,0.0
        #07 Emma Nguyen,Scanning and Bar Coding,Night,Week 2,0.0
        #08 Mia Rossi,Machine Operation,Night,Week 2,0.0
        #08 Mia Rossi,Scanning and Bar Coding,Early,Week 3,0.0
        #08 Mia Rossi,Scanning and Bar Coding,Late,Week 1,1.0
        #09 Carlos Garcia,Machine Operation,Night,Week 3,0.0
        #09 Carlos Garcia,Mail Sorting,Early,Week 2,0.0
        #09 Carlos Garcia,Mail Sorting,Late,Week 1,0.0
    
    def test_initialisation(self):
        """
        Tests for the correct instantiation of a Scheduler object
        """
        # Create an instance of the scheduler and pass it valid inputs
        sched = Scheduler(self.problem_name, self.employees, self.duties, self.shifts, self.rotations, self.bids)

        # Assert that the data inputs have been correctly set up
        self.assertEqual(sched.employees, self.employees, "The employees lists should match")
        self.assertEqual(sched.duties, self.duties, "The duties lists should match")
        self.assertEqual(sched.shifts, self.shifts, "The shifts lists should match")
        self.assertEqual(sched.rotations, self.rotations, "The rotations lists should match")
        self.assertEqual(sched.bids, self.bids, "The bids dictionaries should match")
        self.assertEqual(sched.problem_name, self.problem_name, f"The problem name should be '{self.problem_name}'")

    def test_completeBids(self):
        """
        Test for checking the Bids
        """
        # Create an instance of the scheduler and pass it valid inputs
        sched = Scheduler(self.problem_name, self.employees, self.duties, self.shifts, self.rotations, self.bids)

        # Complete the bids (this is the method being tested)
        try:
            sched.completeBids()
        except ValueError as e:
            self.assertNotIsInstance(e, ValueError) # Test for errors thrown by the method

        # Assert the correct number of bids has been created
        self.assertEqual(len(sched.bids), 81, f"The number of bids should be 81")

    def test_completeBids_error(self):
        """
        Test the ValueError is raised
        """
        # Remove an early, late and night duty to test the ValueError is raised (each employee should have 3 bids)
        del self.bids[("09 Carlos Garcia", "Machine Operation", "Early")]
        del self.bids[("08 Mia Rossi", "Scanning and Bar Coding", "Late")]
        del self.bids[("07 Emma Nguyen", "Mail Sorting", "Night")]

        # Create an instance of the scheduler and pass it valid inputs
        sched = Scheduler(self.problem_name, self.employees, self.duties, self.shifts, self.rotations, self.bids)

        # Complete the bids (this is the method being tested) and assert the ValueError is rasied
        with self.assertRaises(ValueError):
            sched.completeBids()

        # Assert no new bids are created 
        self.assertEqual(len(self.bids), 24, f"The number of bids should be 24")

    def test_SetUpAndSolveProblem_and_cleanAllocations(self):
        """
        Tests the allocations dictionary is correctly cleaned after the problem has been solved.  Also tests that the constraints have been respected.
        """
        # Create an instance of the scheduler and solve it
        sched = Scheduler(self.problem_name, self.employees, self.duties, self.shifts, self.rotations, self.bids)
        sched.completeBids()

        # Set up and solve the problem, then clean the allocations (these are the methods being tested)
        sched.setUpProblem()
        sched.solveProblem()
        sched.cleanAllocations()

        # Test the allocations have been compiled into the correct dictionary format
        # First unpack the tuple of the first tuple key
        first_item = list(sched.allocations.items())[0]
        key, value = first_item
        employee, duty, shift, week = key
        # Test each element of the tuple key
        self.assertEqual(employee, "01 Samuel Brown", "Unexpected Employee")
        self.assertEqual(duty, "Machine Operation", "Unexpected Duty")
        self.assertEqual(shift, "Early", "Unexpected Shift")
        self.assertEqual(week, "Week 2", "Unexpected Week")
        self.assertGreater(value, 0.0, "An allocation value should have been assigned")

        # Test no-bids have been handled
        second_item = list(sched.allocations.items())[1]
        key, value = second_item
        employee, duty, shift, week = key
        self.assertEqual(employee, "01 Samuel Brown", "Unexpected Employee")
        self.assertEqual(duty, "Machine Operation", "Unexpected Duty")
        self.assertEqual(shift, "Night", "Unexpected Shift")
        self.assertEqual(week, "Week 1", "Unexpected Week")
        self.assertEqual(value, 0.0, "An no-bid allocation should have been assigned")

        # Test the number of allocations is correct
        self.assertAlmostEqual(len(sched.allocations), 27, delta=1, msg="The number of allocations should be 27")

        # Create a dataframe of allocations in order to count the allocations and prove the constraints have been respected
        # Do this by iterating the dictionary and unpacking the tuple key and allocation value into dataframe columns
        allocsdf = pd.DataFrame([(emp, duty, shift, rotation, alloc) for (emp, duty, shift, rotation), alloc in sched.allocations.items()],
                            columns=["Employee", "Duty", "Shift", "Rotation", "Bidded"])

        # Test the constraint - Each employee must be allocated exactly one duty and shift combination per rotation
        allocation_counts = allocsdf.groupby(["Employee", "Rotation"]).size().reset_index(name="Count")
        violations = allocation_counts[allocation_counts["Count"] != 1]
        self.assertEqual(len(violations), 0, msg=f"There are employees with more than 1 allocation per rotation {violations}")

        # Test the constraint - Each employee must be assigned one early, late, and night duty over the rotation period
        allocation_counts = allocsdf.groupby(["Employee", "Shift"]).size().reset_index(name="Count")
        violations = allocation_counts[allocation_counts["Count"] < 1]
        self.assertEqual(len(violations), 0, msg=f"There are employees not allocated to each shift {violations}")

        # Test the constraint that - Each duty, shift, and rotation combination may have only one employee allocated
        allocation_counts = allocsdf.groupby(["Duty", "Shift", "Rotation"]).size().reset_index(name="Count")
        violations = allocation_counts[allocation_counts["Count"] < 1]
        self.assertEqual(len(violations), 0, msg=f"There are duty shifts that have been allocated to more than one employee {violations}")

if __name__ == "__main__":
    unittest.main()


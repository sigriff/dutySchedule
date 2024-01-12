"""
Unit tests for the scheduleDb module.  The tests in this module
can both setup and destroy the database, so this module uses
mocking to avoid impacting the database.

Example usage python -m unittest tests/test_scheduleDb.py

Author: Simon Griffiths
Date: 24-Nov-2023
Version: 1.0.0
"""
import unittest
from unittest.mock import MagicMock, patch
from src.database.scheduleDb import DbUtility, SchemaDoesNotExistException, Duty, Employee, RotationWeek, Shift
from typing import Optional
from src.database.scheduleDb import TableDoesNotExistException
import pandas as pd

class UnitTestScheduleDb(unittest.TestCase):
    """
    Unit tests to validate the methods of the ScheduleDb class.
    """
    _schemaName = "test_rm_scheduling"
    _dbutil: Optional[DbUtility] = None

    def setUp(self) -> None:
        """
        Instantiate DbUtility for all the tests to use (apart from the class initialisation tests)
        """
        self._dbutil = self.create_test_dbutil()

    def create_test_dbutil(self) -> DbUtility:
        """
        Create an instance of DBUtility
        """
        # Mock environment variables
        with patch("src.database.scheduleDb.os.getenv") as mock_getenv:
            mock_getenv.side_effect = ["SQL_USER", "SQL_KEY"]

            # Mock the creation of the database engine
            with patch("src.database.scheduleDb.db.create_engine") as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine

                # Mock the checkSchema and createSchema methods
                with patch("src.database.scheduleDb.DbUtility.checkSchema") as mock_checkSchema:
                    with patch("src.database.scheduleDb.DbUtility.createSchema") as mock_createSchema:
                        # Create the DbUtility instance
                        l_dbutil = DbUtility(self._schemaName) 
        
        return l_dbutil

    @patch("src.database.scheduleDb.os.getenv")
    @patch("src.database.scheduleDb.db.create_engine")
    @patch("src.database.scheduleDb.DbUtility.checkSchema")
    def test_initialisation(self, mock_checkSchema, mock_create_engine, mock_getenv):
        """
        Tests for the correct instantiation of a DBUtility object.  In this scenario
        the schema already exists
        """
        # Setup
        mock_getenv.side_effect = ["SQL_USER", "SQL_KEY"]
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
     
        # Test the instantiation of DBUtility
        l_dbutil = DbUtility(self._schemaName)
     
        # Assert the dbutility instantiated
        self.assertIsNotNone(l_dbutil)
     
        # Assert that each external entity in the flow was called create
        mock_getenv.assert_any_call("SQL_USER")
        mock_getenv.assert_any_call("SQL_KEY")
        mock_checkSchema.assert_called()
        mock_create_engine.assert_called()
        self.assertEqual(l_dbutil.schemaName, self._schemaName)

    @patch("src.database.scheduleDb.os.getenv")
    @patch("src.database.scheduleDb.db.create_engine")
    @patch("src.database.scheduleDb.DbUtility.checkSchema")
    @patch("src.database.scheduleDb.DbUtility.createSchema")
    def test_initialisation_no_schema(self, mock_createSchema, mock_checkSchema, mock_create_engine, mock_getenv):
        """
        Tests for the correct instantiation of a DBUtility object.  In this scenario
        the schema does not already exist
        """
        # Setup
        mock_getenv.side_effect = ["SQL_USER", "SQL_KEY"]
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
    
        # Mock the checkSchema method to raise SchemaDoesNotExistException
        mock_checkSchema.side_effect = SchemaDoesNotExistException(self._schemaName, "")
    
        # Test the instantiation of DBUtility
        l_dbutil = DbUtility(self._schemaName)
    
        # Assertions - check that create schema is called
        mock_createSchema.assert_called_once()

    def test_dropSchema(self):
        """
        Test the schema drops and tables are deleted with the correct SQL
        """
        # Mock the connect method of the engine
        mock_connection = MagicMock()
        self._dbutil.engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Call the dropSchema method
        self._dbutil.dropSchema()

        # Assert the correct SQL command was executed
        actual_sql = str(mock_connection.execute.call_args[0][0]) # Get the SQL from the TextClause
        self.assertEqual(actual_sql, f"DROP DATABASE IF EXISTS {self._schemaName}")
        
    @patch("src.database.scheduleDb.db.inspect")
    @patch("src.database.scheduleDb.pd.read_csv")
    @patch("src.database.scheduleDb.os.path.join")
    @patch("src.database.scheduleDb.os.path.dirname")
    @patch("src.database.scheduleDb.pd.DataFrame.to_sql")
    def test_populateSampleData_success(self, mock_to_sql, mock_dirname, mock_join, mock_read_csv, mock_inspect):
        """
        Test the database interaction and csv file reading.  In this test, the tables exist in the database
        """
        # Setup Mocks
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ["employee"]
        mock_inspect.return_value = mock_inspector
        mock_read_csv.return_value = MagicMock() # Mock the returned dataframe
        mock_dirname.return_value = "mocked_dir"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        # Call the method to test
        self._dbutil.populateSampleData()

        # Assertions to ensure all tables were checked and data was uploaded
        self.assertEqual(mock_read_csv.call_count, 4)

    @patch("src.database.scheduleDb.db.inspect")
    def test_populateSampleData_no_table(self, mock_inspect):
        """
        Test the assertion when tables do not exist
        """
        # Setup mocks
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = []  # No tables exist
        mock_inspect.return_value = mock_inspector

        # Assert that TableDoesNotExistException is raised
        with self.assertRaises(TableDoesNotExistException):
            self._dbutil.populateSampleData()

    @patch("src.database.scheduleDb.DbUtility.readEmployeesAsList")
    @patch("src.database.scheduleDb.DbUtility.readDutiesAsFlatList")
    @patch("src.database.scheduleDb.DbUtility.readShiftsAsFlatList")
    def test_createRandomBids(self, mock_shifts_list, mock_duties_list, mock_employees_list):
        """
        Test the creation of a random sample of bids
        """
        # Setup mocks
        mock_employees = []
        employee = Employee()
        employee.employee_id = 1
        employee.first_name = "John"
        employee.last_name = "Smith"
        mock_employees.append(employee)
        employee = Employee()
        employee.employee_id = 2
        employee.first_name = "Billy Bob"
        employee.last_name = "Thornton Smythe"
        mock_employees.append(employee)
        mock_employees_list.return_value = mock_employees
        mock_duties_list.return_value = ["Duty 1", "Duty 2", "Duty 3", "Duty 4", "Duty 5", "Duty 6"]
        mock_shifts_list.return_value = ["Early", "Late", "Night"]

        # Call the createRandomBids method
        random_bids_1 = self._dbutil.createRandomBids()

        # Assert 6 bids have been created
        self.assertEqual(len(random_bids_1), 6, f"The number of bids should be 6")

        # Assert each employee has 1 early, 1 late and 1 night duty
        df = pd.DataFrame(random_bids_1.keys(), columns=["Employee", "Duty", "Shift"])
        employee_df = df[df["Employee"] == "1 John Smith"]
        shift_counts = employee_df["Shift"].value_counts()
        self.assertEqual(1, shift_counts.get("Early"), "John Smith should have 1 Early shift")
        self.assertEqual(1, shift_counts.get("Late"), "John Smith should have 1 Late shift")
        self.assertEqual(1, shift_counts.get("Night"), "John Smith should have 1 Night shift")
        employee_df = df[df["Employee"] == "2 Billy Bob Thornton Smythe"]
        shift_counts = employee_df["Shift"].value_counts()
        self.assertEqual(1, shift_counts.get("Early"), "Billy Bob should have 1 Early shift")
        self.assertEqual(1, shift_counts.get("Late"), "Billy Bob should have 1 Late shift")
        self.assertEqual(1, shift_counts.get("Night"), "Billy Bob should have 1 Night shift")

        # Call the createRandomBids method a second time
        random_bids_2 = self._dbutil.createRandomBids()

        # Assert the results are different from the first time.  On a very few occasions the results
        # could legitimately be the same and show as a test failure.  If this happens simply re-run
        # the unit test
        self.assertNotEqual(random_bids_1, random_bids_2, "The bids should be different as they are randomised")

    @patch("src.database.scheduleDb.pd.read_csv")
    def test_readAllocationsDictFromCsv(self, mock_read_csv):
        """
        Tests the csv read of allocations is correctly converted to a dictionary
        """
        # Create a mock dataframe
        data = {"employee": ["Alice", "Bob"],
                "duty": ["Duty1", "Duty2"],
                "shift": ["Morning", "Evening"],
                "week": ["Week 1", "Week 2"],
                "bid": [True, False]}
        mock_df = pd.DataFrame(data)

        # Create a mock return from the method
        expected_allocations = {
            ('Alice', 'Duty1', 'Morning', "Week 1"): 1,
            ('Bob', 'Duty2', 'Evening', "Week 2"): 0
        }

        # Setup mocks
        mock_read_csv.return_value = mock_df

        # Call the method to test
        allocations = self._dbutil.readAllocationsDictFromCsv()

        # Assertion to ensure the dataframe and dictionary are the same
        self.assertEqual(expected_allocations, allocations)

    @patch("src.database.scheduleDb.pd.read_csv")
    def test_readBidsDictFromCsv(self, mock_read_csv):
        """
        Tests the csv read of bids is correctly converted to a dictionary
        """
        # Create a mock dataframe
        data = {"employee": ["Alice", "Bob"],
                "duty": ["Duty1", "Duty2"],
                "shift": ["Morning", "Evening"],
                "bid": [True, True]}
        mock_df = pd.DataFrame(data)

        # Create a mock return from the method
        expected_bids = {
            ('Alice', 'Duty1', 'Morning'): 1,
            ('Bob', 'Duty2', 'Evening'): 1
        }

        # Setup mocks
        mock_read_csv.return_value = mock_df

        # Call the method to test
        bids = self._dbutil.readBidsDictFromCsv()

        # Assertion to ensure the dataframe and dictionary are the same
        self.assertEqual(expected_bids, bids)

    @patch("src.database.scheduleDb.DbUtility.readDutiesAsList")
    def test_readDutiesAsFlatList(self, mock_readDutiesAsList):
        """
        Test the conversion of a list of Duty objects to a flat list
        """
        # Create a mock object list
        mock_duties = []
        duty = Duty()
        duty.duty_id = 1
        duty.duty_name = "Duty 1"
        duty.duty_description = "Duty 1 Description"
        mock_duties.append(duty)
        duty = Duty()
        duty.duty_id = 2
        duty.duty_name = "Duty 2"
        duty.duty_description = "Duty 2 Description"
        mock_duties.append(duty)
        expected_flat_list = ["Duty_1","Duty_2"]

        # Create the mocks
        mock_readDutiesAsList.return_value = mock_duties

        # Call the method to test
        flat_list = self._dbutil.readDutiesAsFlatList("_")

        # Assertion to check the flat list is returned with "_"
        self.assertEqual(expected_flat_list, flat_list)

    @patch("src.database.scheduleDb.DbUtility.readEmployeesAsList")
    def test_readEmployeesAsFlatList(self, mock_readEmployeesAsList):
        """
        Test the conversion of a list of Employee objects to a flat list
        """
        # Create a mock object list
        mock_employees = []
        employee = Employee()
        employee.employee_id = 1
        employee.first_name = "John"
        employee.last_name = "Smith"
        mock_employees.append(employee)
        employee = Employee()
        employee.employee_id = 2
        employee.first_name = "Billy Bob"
        employee.last_name = "Thornton Smythe"
        mock_employees.append(employee)
        expected_flat_list = ["1_John_Smith","2_Billy_Bob_Thornton_Smythe"]

        # Create the mocks
        mock_readEmployeesAsList.return_value = mock_employees

        # Call the method to test
        flat_list = self._dbutil.readEmployeesAsFlatList("_")

        # Assertion to check the flat list is returned with "_"
        self.assertEqual(expected_flat_list, flat_list)

    @patch("src.database.scheduleDb.DbUtility.readRotationWeeksAsList")
    def test_readRotationWeeksAsFlatList(self, mock_readRotationWeeksAsList):
        """
        Test the conversion of a list of RotationWeeks objects to a flat list
        """
        # Create a mock object list
        mock_rotationweeks = []
        week = RotationWeek()
        week.week = "Week 1"
        mock_rotationweeks.append(week)
        week = RotationWeek()
        week.week = "Week 2"
        mock_rotationweeks.append(week)
        week = RotationWeek()
        week.week = "Week 3"
        mock_rotationweeks.append(week)
        expected_flat_list = ["Week_1","Week_2","Week_3"]

        # Create the mocks
        mock_readRotationWeeksAsList.return_value = mock_rotationweeks

        # Call the method to test
        flat_list = self._dbutil.readRotationWeeksAsFlatList("_")

        # Assertion to check the flat list is returned with "_"
        self.assertEqual(expected_flat_list, flat_list)

    @patch("src.database.scheduleDb.DbUtility.readShiftsAsList")
    def test_readShiftsAsList(self, mock_readShiftsAsList):
        """
        Test the conversion of a list of Shift objects to a flat list
        """
        # Create a mock object list
        mock_shifts = []
        shift = Shift()
        shift.shift = "Early"
        mock_shifts.append(shift)
        shift = Shift()
        shift.shift = "Late"
        mock_shifts.append(shift)
        shift = Shift()
        shift.shift = "Night"
        mock_shifts.append(shift)
        expected_flat_list = ["Early","Late","Night"]

        # Create the mocks
        mock_readShiftsAsList.return_value = mock_shifts

        # Call the method to test
        flat_list = self._dbutil.readShiftsAsFlatList()

        # Assertion to check the flat list is returned
        self.assertEqual(expected_flat_list, flat_list)

if __name__ == "__main__":
    unittest.main()
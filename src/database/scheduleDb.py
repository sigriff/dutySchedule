"""
This module provides the constructs for the creation and operation of the Schedule database. Only MySQL is currently supported.
There are four sections in this module:

Section 1 - Declarative code
Contains declarative mapping which defines the Python Object Model and the Database Metadata which describes the
underlying SQL tables.  Contained in this section are the individual mapped classes of Duty, Employee, Rotation Week 
and Shift.  These mapped classes refer to singular database tables within the schedule schema.

Section 2 - Database Utility Class
Contains methods to create the database, schema and tables as well as destroy them.  Provides methods to populate the database
tables with data taken from CSV files located in the /data folder.  Provides methods to read data from the tables and convert
it into lists.  Provides methods to save to and read from the Bids and Allocations CSV files also located in the /data folder.
Provides methods to convert the data read from the CSVs into dictionaries.

Section 3 - User-defined Exceptions
Contains for user-defined error classes thrown for specific scenarios that could occur in the Database Utility code.

Section 4 - Command Line Interface
Contains interactive CLI code to allow a user to name and set up the database schema, populate the database tables with data,
print the contents of the database tables and also to destroy the database schema and all content.


Example usage:
To create the schema
myVar = DbUtility(schemaName="mySchema")
myVar->setupSchemaTables()

To drop the schema
myVar = DbUtility(schemaName="mySchema")
myVar->dropSchema()

To load the test data
myVar = DbUtility(schemaName="mySchema")
myVar->populateTestData()

Alternatively you can use the CLI by running python -m rmScheduleDeclaration

Author: Simon Griffiths
Date: 20-Nov-2023
Version: 1.0.0
"""
import os
from typing import List
import sqlalchemy as db
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker
from enum import Enum
import pandas as pd
import random
from dotenv import load_dotenv

"""
Section 1 - Declarative code
"""
class Base(DeclarativeBase):
    """
    A Base class for each of the individual mapped classes to inherit from.
    """
    pass

class Duty(Base):
    """
    Declaration for the mapped Duty table
    """
    # Declaration of the table name.
    __tablename__ = "duty"

    # Declaration of the table columns.
    duty_id: Mapped[int] = mapped_column(primary_key=True)
    duty_name: Mapped[str] = mapped_column(String(50))
    duty_description: Mapped[str] = mapped_column(String(150))

    def __repr__(self) -> str:
        """
        For debugging - return the self values using their repr() functions
        """
        return f"Duty(duty_id={self.duty_id!r}, duty_name={self.duty_name!r}, duty_description={self.duty_description!r})"

class Employee(Base):
    """
    Declaration for the mapped Employee table
    """
    # Declaration of the table name.
    __tablename__ = "employee"

    # Declaration of the table columns.
    employee_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        """
        For debugging - return the self values using their repr() functions
        """
        return f"Employee(employee_id={self.employee_id!r}, first_name={self.first_name!r}, last_name={self.last_name!r})"

class RotationWeek(Base):
    """
    Declaration for the mapped RotationWeek table
    """
    # Declaration of the table name.
    __tablename__ = "rotationweek"

    # Declaration of the table columns.
    week: Mapped[str] = mapped_column(String(6), primary_key=True)

    def __repr__(self) -> str:
        """
        For debugging - return the self values using their repr() functions
        """
        return f"RotationWeek(week={self.week!r})"

class Shift(Base):
    """
    Declaration for the mapped Shift table
    """
    # Declaration of the table name.
    __tablename__ = "shift"

    # Declaration of the table columns.
    shift: Mapped[str] = mapped_column(String(6), primary_key=True)

    def __repr__(self) -> str:
        """
        For debugging - return the self values using their repr() functions
        """
        return f"Shift(shift={self.shift!r})"

"""
Section 2 - Database Utility Class
"""
class DbUtility(object):
    """
    This database utility is used to manage the Schedule database.  It provides methods to create and drop a schema as well as create
    tables and populate them with data from CSV files. A method is also provided to clean data out of tables.  Methods are provided
    to read data from the tables lists. Utility methods are also provided to save the Bids and Allocations CSVs aswell as reading from
    these CSVs into dictionaries.  A special method is provided to randomly create Bids is also provided to assist testing.
    """
    
    def __init__(self,schemaName="rm_scheduling") -> None:
        """
        This constructs the Utility class.  It performs the following operations:
        1. Sets an attribute to hold the schema name for the database.
        2. Retrieves the SQL user and password from local environment variables for engine connection.
        3. Creates the engine for connections to the database and connection pooling and connects to the SQL server.
        4. Checks the schema exists and if it does not throws an error so that the schema can be created.
        5. (OPTIONALLY) Creates the schema.
        6. Recreates the engine and connects to the specified shcema.
        7. Retrieves the database meta data
        """

        # set the schema name for the database
        self.schemaName = schemaName

        # get the env variables which hold the SQL user and password
        load_dotenv()
        sql_user = os.getenv("SQL_USER")
        sql_key = os.getenv("SQL_KEY")

        if sql_user == None or sql_key == None:
            raise SqlUserOrKeyException([sql_user, None],"") # Do not pass the key into the message as it would be visible

        # get engine object using pymysql driver for mysql.  First connect to the SQL server and check the scehame exists
        # if the schema doesn't exist, create it.  Finally connect to the schema
        try:
            self.engine = db.create_engine(f"mysql+pymysql://{sql_user}:{sql_key}@localhost/")
            self.checkSchema()
        except SchemaDoesNotExistException:
            self.createSchema()
        finally:
            self.engine = db.create_engine(f"mysql+pymysql://{sql_user}:{sql_key}@localhost/{self.schemaName}")

        # get meta data object
        self.meta_data = db.MetaData()

    def checkSchema(self) -> None:
        """
        This method checks if the schema in self.schemaName exists.  If it doesn't it throws an error.
        """
        with self.engine.connect() as conn: # create a connection to the database
            query = text(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :schema")
            result = conn.execute(query, {"schema": self.schemaName})
            if result.fetchone() is None:
                raise SchemaDoesNotExistException(self.schemaName, "")

    def createRandomBids(self) -> dict:
        """
        Create random bids for each employee
        """
        # Start by retrieving the employees and duties
        employees = self.readEmployeesAsList()
        duties = self.readDutiesAsFlatList()
        shifts = self.readShiftsAsFlatList()
        bids = {}

        # For each employee get a random selection of 3 duties, one for each shift and
        # build a dictionary of employee bids
        for employee in employees:
            random_bids = [(random.choice(duties), shift) for shift in shifts]
            emp_bids = {(f"{employee.employee_id} {employee.first_name} {employee.last_name}", duty, shift):1.0 for duty, shift in random_bids}
            bids.update(emp_bids)

        return bids

    def createSchema(self) -> None:
        """
        This method takes the schema name from the self.schemaName variable and tries to create the database schema.
        """
        with self.engine.connect() as conn:  # create a connection to the database
            conn.execute(text(f'CREATE SCHEMA {self.schemaName}'))
           
    def dropSchema(self) -> None:
        """
        This method takes the schema name from the self.schemaName variable and deletes it from the database.
        WARNING! It will delete all tables and data from the schema as well.
        """
        with self.engine.connect() as conn:  # create a connection to the database
            conn.execute(text(f"DROP DATABASE IF EXISTS {self.schemaName}")) # drop the schema if it exists
            #Base.metadata.drop_all(self.engine) # This only drops the tables and not the schema so not using it

    def setupSchemaTables(self) -> None:
        """
        This method creates the database tables and relationships for the schema as declared by this module.
        The create_all method only creates tables and relationships if they do not already exist.
        """
        # Create all tables in the database which are defined by the Base's subclasses
        Base.metadata.create_all(self.engine)

    def populateSampleData(self) -> None:
        """
        This method checks that the various tables of the schema exist before populating them with sample data.
        It is IMPORTANT that the uploaded csv matches the structure of the table.
        """

        # First check that the employee table exists. If it DOES NOT then exit this method as the <dataFrame>.to_sql()
        # method used will create the table and we don't want this to happen. Doing so from this method could result in
        # referential integrity errors with other as yet uncreated tables so it is best to exit this method and ask the
        # user to first create the schema and setup empty tables before populating data
        inspector = db.inspect(self.engine)
        if Employee.__tablename__ not in inspector.get_table_names():
            raise TableDoesNotExistException(Employee.__tablename__, "")

        try:

            # get the path relative to this module
            module_dir = os.path.dirname(__file__)

            # Upload the duties and append them to the duty table 
            dutdf = pd.read_csv(os.path.join(module_dir, "..\\..\\data\\duties.csv"))
            dutdf.to_sql(Duty.__tablename__, con=self.engine, if_exists="append", index=False)

            # Upload the employees and append them to the employee table
            empdf = pd.read_csv(os.path.join(module_dir, "..\\..\\data\\employees.csv"))
            empdf.to_sql(Employee.__tablename__, con=self.engine, if_exists="append", index=False)

            # Upload the rotation weeks and append them to the rotation weeks table.
            rotwdf = pd.read_csv(os.path.join(module_dir, "..\\..\\data\\rotationweeks.csv"))
            rotwdf.to_sql(RotationWeek.__tablename__, con=self.engine, if_exists="append", index=False)

            # Upload the shifts and append them to the shifts table.
            shidf = pd.read_csv(os.path.join(module_dir, "..\\..\\data\\shifts.csv"))
            shidf.to_sql(Shift.__tablename__, con=self.engine, if_exists="append", index=False)

            print("All data uploaded ok\n")

        except IntegrityError as e: # This error is most likely to happen if the appends above are for exisitng keys
            print("The tables already contain data\n")

        except Exception as e:
            print(f"A general error occurred: {e}") # could be a csv format doesn't match the db table

    def readAllocationsDictFromCsv(self) -> dict:
        """
        Uploads the allocations csv and converts it to a dictionary
        """
        # Get the path relative to this module and read the bids csv to a dataframe
        current_dir = os.path.dirname(os.path.abspath(__file__))
        module_dir = os.path.join(current_dir, '..', '..')
        df = pd.read_csv(os.path.join(module_dir, "data", "allocations.csv"))

        # Convert the dataframe to a dictionary
        # The key is a tuple of (employee, duty, shift, week),
        # and the value is whether or not the employee bid for this allocation
        allocations = {(row['employee'], row['duty'], row['shift'], row['week']): row['bid'] for index, row in df.iterrows()}

        return allocations

    def readBidsDictFromCsv(self) -> dict:
        """
        Uploads the bids csv and converts it to a dictionary
        """
        # Get the path relative to this module and read the bids csv to a dataframe
        current_dir = os.path.dirname(os.path.abspath(__file__))
        module_dir = os.path.join(current_dir, '..', '..')
        df = pd.read_csv(os.path.join(module_dir, "data", "bids.csv"))

        # Convert the dataframe to a dictionary
        # The key is a tuple of (employee, duty, shift), and the value is bid
        bids = {(row['employee'], row['duty'], row['shift']): row['bid'] for index, row in df.iterrows()}

        return bids

    def readDutiesAsList(self) -> List[Duty]:
        """
        Reads all duties from the 'duty' table and returns them as a list of Duty objects.
        """
        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Query all duties
        duties = session.query(Duty).all()

        # Close the session
        session.close()

        return duties

    def readDutiesAsFlatList(self, separator=" ") -> list:
        """
        Reads all Duty objects from the 'duty' table and returns them as a flattened list
        of strings
        """
        duty_objects = self.readDutiesAsList()

        flat_list = [duty.duty_name.replace(' ', separator) for duty in duty_objects]

        return flat_list

    def readEmployeesAsList(self) -> List[Employee]:
        """
        Reads all employees from the 'employee' table and returns them as a list of Employee objects
        """
        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Query all employees
        employees = session.query(Employee).all()

        # Close the session
        session.close()

        return employees
    
    def readEmployeesAsFlatList(self, separator=" ") -> list:
        """
        Reads all Employee objects from the 'employee' table and returns them as a flattened list
        of strings
        """
        employee_objects = self.readEmployeesAsList()

        flat_list = [separator.join([str(empl.employee_id), empl.first_name, empl.last_name]).replace(' ', separator)
                        for empl in employee_objects]
        
        return flat_list

    def readRotationWeeksAsList(self) -> List[RotationWeek]:
        """
        Reads all weeks from the 'rotationweek' table and returns them as a list of RotationWeek objects
        """
        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Query all rotations
        weeks = session.query(RotationWeek).all()

        # Close the session
        session.close()

        return weeks

    def readRotationWeeksAsFlatList(self, separator=" ") -> list:
        """
        Reads all Rotation Week objects from the 'rotationweek' table and returns them as a flattened list
        of strings
        """
        week_objects = self.readRotationWeeksAsList()

        flat_list = [week.week.replace(' ', separator) for week in week_objects]

        return flat_list

    def readShiftsAsList(self) -> List[Shift]:
        """
        Reads all shifts from the 'shifts' table and returns them as a list of Shift objects
        """
        # Create a session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Query all rotations
        shifts = session.query(Shift).all()

        # Close the session
        session.close()

        return shifts

    def readShiftsAsFlatList(self, separator=" ") -> list:
        """
        Reads all Shift objects from the 'shift' table and returns them as a flattened list
        of strings
        """
        shift_objects = self.readShiftsAsList()

        flat_list = [shift.shift.replace(' ', separator) for shift in shift_objects]

        return flat_list

    def saveAllocationsDictAsCsv(self, allocations: dict) -> None:
        """
        Download the allocations dictionary to a csv
        """
        # Convert the dictionary to a pandas DataFrame
        df = pd.DataFrame([(key[0], key[1], key[2], key[3], value) for key, value in allocations.items()],
                          columns=['employee', 'duty', 'shift', 'week', 'bid'])

        # Get the path relative to this module and then save the DataFrame to a csv
        current_dir = os.path.dirname(os.path.abspath(__file__))
        module_dir = os.path.join(current_dir, '..', '..')
        df.to_csv(os.path.join(module_dir, "data", "allocations.csv"), index=False)

    def saveBidsDictAsCsv(self, bids: dict) -> None:
        """
        Download the bids dictionary to a csv
        """
        # Convert the dictionary to a pandas DataFrame
        df = pd.DataFrame([(key[0], key[1], key[2], value) for key, value in bids.items()],
                          columns=['employee', 'duty', 'shift', 'bid'])

        # get the path relative to this module and then save the DataFrame to a csv
        current_dir = os.path.dirname(os.path.abspath(__file__))
        module_dir = os.path.join(current_dir, '..', '..')
        df.to_csv(os.path.join(module_dir, "data", "bids.csv"), index=False)


"""
Section 3 - User-defined Exceptions
"""
class SchemaDoesNotExistException(Exception): # User-defined Exception
    """
    This exception is thrown when connecting to a database schema that does not exist.
    """
    def __init__(self, exception_parameter, exception_message) -> None:
        super().__init__(exception_parameter, "A schema with this name does not exist")

class SqlUserOrKeyException(Exception): # User-defined Exception
    """
    This exception is thrown if the SQL User or Key cannot be retrieved for the Db connection.
    """
    def __init__(self, exception_parameter, exception_message) -> None:
        super().__init__(exception_parameter, "SQL_USER or SQL_KEY environment variables not found")

class TableAlreadyPopulatedException(Exception): # User-defined Exception
    """
    This exception is thrown when trying to add sample data to a table that already has entries
    """
    def __init__(self, exception_parameter, exception_message) -> None:
        super().__init__(exception_parameter, "The tables already contain data")

class TableDoesNotExistException(Exception): # User-defined Exception
    """
    This exception is thrown when trying to populate a table that does not exist.
    """
    def __init__(self, exception_parameter, exception_message) -> None:
        super().__init__(exception_parameter, "A table with this name does not exist")


"""
Section 4 - Command Line Interface

The user is requested to enter a schema name, if left blank the default is "rm_scheduling".  After this the user is prompted
for various choices, to drop an existing schema, to create a new schema and tables, to populate the tables with data from
like-named CSV files in the /data folder, to print tables content or to exit.
"""
def default_schema() -> str:
    """
    Returns a default database schema name
    """
    return "rm_scheduling"

def main(option, schema) -> None:
    """
    Handle the CLI options entered by the user
    """
    print(f"\nsqlalchemy.__version__ = {db.__version__}")
    
    # set the database schema (for situations where the CLI is bypassed)
    if schema in (None, ""):
        schema = default_schema()
        print(f"Schema set to: {schema}\n")

    # create an instance of the DbUtility class to handle the connection
    try:
        dbutil = DbUtility(schema)
    except Exception as e:
        print(f"\nThere was an error connecting to the database:\n{e}\n")
        return
    
    match option:
        case 1: # Drop the schema
            print("Drop schema (WARNING: This deletes tables and data as well)\n")
            dbutil.dropSchema()
            print(f"Schema {schema} and all its tables dropped.\n")

        case 2: # Create the schema and database
            print("Create schema and setup the tables\n")
            dbutil.setupSchemaTables()
            print(f"Schema {schema} declaratively created with all its tables.\n")

        case 3: # Populate the tables with sample data
            print("Populate the tables with test data\n")
            try:
                dbutil.populateSampleData()
            except TableDoesNotExistException:
                print("The tables you are trying to populate to not exist. Please first create the schema (Option 2)\n")
                print()
            except IntegrityError:
                pass

        case 4: # Read the all the tables and print their contents
            try:
                # Read the data from the db
                duties = dbutil.readDutiesAsList()
                if len(duties) == 0: # handle no data in the tables (just checking the Duty table is enough)
                    print("\nThe Duty table is empty. Please upload sample date (Option 3) before trying again\n")
                    return
                employees = dbutil.readEmployeesAsList()
                rotationweeks = dbutil.readRotationWeeksAsList()
                shifts = dbutil.readShiftsAsList()

            except ProgrammingError as e:
                print(f"\nOne or more of the tables do not exist. Please create the schema and tables (Option 2) and then upload sample data (Option 3), before trying again.\n")
                return
            
            print("\nDuty table contents:")
            for duty in duties:
                print(duty.duty_id, duty.duty_name, duty.duty_description)

            print("\nEmployee table contents:")
            for employee in employees:
                print(employee.employee_id, employee.first_name, employee.last_name)

            print("\nRotationWeek table contents:")
            for week in rotationweeks:
                print(week.week)

            print("\nShift table contents:")
            for shift in shifts:
                print(shift.shift)

            print()

if __name__ == "__main__":

    # set the database schema
    schema = input("Enter a schema name (default if left blank: rm_scheduling): ")
    if schema in (None, ""):
        schema = default_schema()
    print(f"Schema set to: {schema}\n")

    # create a prompt for the CLI
    prompt = (
        "Choose from the following:\n"
        "1. Drop schema (WARNING: This deletes tables and data as well)\n"
        "2. Create schema and setup the tables\n"
        "3. Upload csv data to the database\n"
        "4. Read tables and print\n"
        "5. Exit\n"
        ">>>"
    )

    # Present the CLI options to the user
    while True:
        try:
            option = int(input(prompt))
        except:
            print("Invalid option chosen. Exiting...\n")
            break

        if option in (1, 2, 3, 4):
            main(option, schema)
        else:
            print("Exiting...\n")
            break
        
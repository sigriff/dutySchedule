# Project Name

DutySchedule
Simon Griffiths 11-Dec-2023

## Description

The DutySchedule project is an implementation of a scheduling solution to solve the allocation of duties to employees in Royal Mail's sorting offices.  The projects reads in bids for duties in shifts and with an objective function of 'maximising satisfaction', where satisfaction is measured by an allocated bid, allocates duties to employees within shifts over a three week rotation period.  To do this an optimisation problem is set up using linear programming and solved using the PuLP library.  Several constraints are also respected: an employee can only be allocated a single duty and shift in any single week of the rotation; each employee must be allocated a duty in each shift over the rotation; and within a shift a duty can only be allocated to one employee.  The bokeh library is used to present two visualisations of the solution.  One which shows the allocations of employees to duties and shifts within the rotation and the second which shows a view of how employees have has their bid preferences satisfied.

## Requirements

- Python 3.11.5
- MySQL 8.2 Community Edition
- Important python libraries:
    - PuLP https://coin-or.github.io/pulp/
    - Bokeh https://docs.bokeh.org/en/latest/index.html
    - SQLAlchemy https://www.sqlalchemy.org/
    - Pandas https://pandas.pydata.org/docs/
- The full list of python libraries can be found in requirements.txt
- The project was developed using an Anaconda Virtual Environment available here https://www.anaconda.com/
- This project has only been tested on Windows 11 Enterprise

## Installation

 1. Download and install MySQL Community Server 8.2.x https://www.mysql.com/downloads/
 2. Download and install MySQL Workbench
 3. If necessary start the MySQL service. In windows use services.msc and start the mySQL82 service
 4. Open the MySQL Workbench and create a DB Admin account and password for mySQL. Open the project .env file and save the DB Account and password there. e.g.
 SQL_USER="The Admin account"
 SQL_KEY="The Admin password"
 5. Ensure all python dependencies in requirements.txt are installed in your virtual environment
 6. Create the database schema and populate the tables:
    - In the terminal run module ../src/database/scheduleDb.py
    - Press Enter to accept the default schema rm_scheduling
    - Enter 2 - "Create schema and setup the tables"
    - Enter 3 - "Upload csv data to the database" - NOTE that this uses the duties.csv, employees.csv, rotationweeks.csv and shifts. csv files located in the ../data folder
    - Enter 4 - "Read tables  and print" to verify the tables contents

## How to use the project

 1. In the terminal run program main.py
 2. Press Enter to accept the default schema rm_scheduling
 3. Enter 1 - "Create a random sample of bids". This generates and prints randomised bids.
 4. Enter 1 - "Download bids to csv". This creates a ../data/bids.csv. Feel free to look at its contents, it will be the same as the printed list.
 5. Alternatively you can create your own bids.csv and save it in the same place. The only rules to follow are that each employee must make a bid for one early, one late and one night duty.
 6. Enter 2 - "Create allocations". This runs the Scheduler and creates allocations. These are stored in ../data/allocations.csv
 7. To see how employees were allocated their bids, Enter 3 - "Show Bid Preference Analysis". This shows a stacked bar chart for each employee showing which bids were successfully allocated
 8. To see the Duty Schedule, Enter 4 - "Show Employee Allocations". This shows the duty and shift allocations to employees over the rotation period

"""
This module handles the visualisations for the duty schedule application.  It requires that
the scheduling application has been run and that allocations have been created.

Two visualisations are handled, a 'Bid Preference Analysis' shows which employees were allocated
their bid preferences and an 'Employee Allocations' analysis which shows visually which
employees have been allocated to which duties and shifts over the rotation period.  It also
shows whether or not the employee made a bid for the allocation.

Example usage:
1. Create an instance of the visualisation, providing allocations data
bpa = BidPreferenceAnalysis(allocations)

2. Call the visualisation
bpa.createVisualisation()

Author: Simon Griffiths
Date: 08-Dec-2023
Version: 1.0.0
"""
import pandas as pd
import numpy as np
import random

from bokeh.io import show, output_notebook
from bokeh.plotting import figure, show
from bokeh.transform import dodge, factor_cmap
from bokeh.models import ColumnDataSource

from bokeh.palettes import HighContrast3
from bokeh.models import HoverTool
from bokeh.models import FactorRange
from bokeh.palettes import Viridis3

class VisualiserBase():
    """
    A base class for the visualisations to inherit from
    """
    def __init__(self, **kwargs) -> None:
        """
        Constructor.  This creates instance attributes for
        the visualisations.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def createVisualisation(self) -> None:
        """
        Base method for subclasses.  This method creates a dataframe of allocations
        and sorts the employees into the correct order for the visualisations
        """
        print(f"\nRunning {self.reportname}\n")

        # Create a baseline DataFrame from allocations dictionary
        # Each tuple in the keys of the dictionary is unpacked and becomes a row in the DataFrame
        data = [(*key, value) for key, value in self.allocations.items()]
        self.allocdf = pd.DataFrame(data, columns=["Employee", "Duty", "Shift", "Week", "Bid"])

        # Pad employee columns with a leading zero - this makes axis sorting easier
        self.allocdf["Employee"] = [f"0{employee}" if employee[1] == " " else employee for employee in self.allocdf["Employee"]]

        # Sort by employee number for the visualisations
        self.allocdf.sort_values(by='Employee', ascending=True, inplace=True)
        self.allocdf.reset_index(drop=True, inplace=True)

class BidPreferenceAnalysis(VisualiserBase):
    """
    Class to handle the bid preference analysis visualisation.
    """
    def __init__(self, allocations, **kwargs) -> None:
        """
        Constructor.  Sets up the report name and the data to be used
        by the visualisation
        """
        super().__init__(reportname="Bid Preference Analysis", allocations=allocations, **kwargs)

    def createVisualisation(self) -> None:
        """
        Create a visualisation for Bid Preference Analysis.  This is based
        on a stacked column.

        The allocations data must be reformatted into the following format:

        data = {'Employee'  : ['01 Samuel Brown', '02 Noah Chen', '04 Belissica Gellor'],
                'Early'     : [1.0, 0.0, 1.0],
                'Late'      : [1.0, 1.0, 1.0],
                'Night'     : [0.0, 1.0, 1.0]
                }
        """
        super().createVisualisation()

        # Data source for the visualisation
        shifts = ["Early","Late","Night"]

        # Pivot the allocations into a format suitable for stacked columns
        data = self.allocdf.pivot_table(index='Employee', columns='Shift', values='Bid', fill_value='0.0')

        # Reset index to make 'Employee' a column again
        data.reset_index(inplace=True)

        # Name the columns
        data.columns = ['Employee', 'Early', 'Late', 'Night']

        # Tooltips
        tooltips = [
            ("Employee", "@Employee"),
            ("Shift", "$name"),
            ("Bid", "@$name")
        ]

        # Create the plot
        p = figure(x_range=self.allocdf['Employee'].unique(), width=1000, height=450, title="Bid Preference Analysis",
                   toolbar_location=None, tools="hover", tooltips=tooltips)

        # Create the stacked columns
        p.vbar_stack(shifts, x='Employee', width=0.6, color=HighContrast3, source=data, legend_label=shifts)

        p.xaxis.major_label_orientation = "vertical"
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"

        show(p)

class EmployeeAllocations(VisualiserBase):
    """
    Class to handle the bid preference analysis visualisation
    """
    def __init__(self, allocations, duties, shifts, weeks, **kwargs):
        """
        Constructor.  Sets up the report name and the data to be used
        by the visualisation
        """
        super().__init__(reportname="Employee Allocations", allocations=allocations, duties=duties, shifts=shifts, weeks=weeks, **kwargs)

    def createVisualisation(self) -> None:
        """
        Create a visualisation for Employee Allocations.  This is based on a categorical chart using rectangular glyphs and
        leans on the bokeh periodic table example.  https://docs.bokeh.org/en/latest/docs/examples/topics/categorical/periodic.html
        """
        super().createVisualisation()

        # Create a list of rotations for the x axis (the y axis will be duties)
        rotations = [" ".join([week, shift]) for week in self.weeks for shift in self.shifts]

        # Create y coordinates for duties and x coordinates for rotations.
        yduties = {duty: (i + 0.6) for i, duty in enumerate(self.duties)}
        xrotations = {rotation: (i + 0.5) for i, rotation in enumerate(rotations)}

        # Add new columns to the dataframe for x,y coordinates and employee initials
        self.allocdf['Rotation'] = self.allocdf['Week'] + " " + self.allocdf['Shift']
        self.allocdf['X-Rotation'] = self.allocdf['Rotation'].map(xrotations)
        self.allocdf['Y-Duty'] = self.allocdf['Duty'].map(yduties)
        self.allocdf['Initials'] = self.allocdf['Employee'].apply(self.extract_initials)

        # Amend the Bid column to say 'Bid'where the employee has bid for the allocation
        self.allocdf['BidStr'] = np.where(self.allocdf['Bid'] == 0.0, "", "Bid")

       # Colour Map 
        cmap = {
            "Week 1 Early"          : "#87CEFA",
            "Week 1 Late"           : "#00BFFF",
            "Week 1 Night"          : "#191970",
            "Week 2 Early"          : "#A8E4A0",
            "Week 2 Late"           : "#21D5A5",
            "Week 2 Night"          : "#2F4F4F",
            "Week 3 Early"          : "#EEAB7E",
            "Week 3 Late"           : "#E2742A",
            "Week 3 Night"          : "#8B4513"
        }

        # Tooltips for hover over
        TOOLTIPS = [
            ("Name", "@Employee"),
            ("Duty", "@Duty"),
            ("Shift"    , "@Shift"),
            ("Bid", "@Bid"),
        ]

        # Create a new figure for plotting
        p = figure(title="Employee Allocations", width=1000, height=450,
                x_range=rotations, y_range=self.duties,
                tools="hover", toolbar_location=None, tooltips=TOOLTIPS)

        # Create the rectangles (0.95, 0.95)
        r = p.rect("X-Rotation", "Y-Duty", 0.95, 0.95, source=self.allocdf, fill_alpha=0.6, legend_field="Rotation",
                    color=factor_cmap('Rotation', palette=list(cmap.values()), factors=list(cmap.keys())))

        # Create a dictionary for the text elements that will appear on the visualisation
        text_props = dict(source=self.allocdf, text_align="left", text_baseline="middle", text_font_size="11px")

        # Set the Texts for the rectangles along with their x,y coordinates
        p.text(x=dodge("X-Rotation", -0.4, range=p.x_range), y="Y-Duty", text="Initials", **text_props)
        p.text(x=dodge("X-Rotation", 0.25, range=p.x_range), y="Y-Duty", text="BidStr", text_font_style="bold", **text_props)

        # Other rectangle settings
        p.outline_line_color = None
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_standoff = 0
        p.legend.visible = False
        p.hover.renderers = [r] # only hover element boxes

        # Show the visualisation
        show(p)

    def extract_initials(self, name) -> str:
        """
        Method to extract initials from the Employee column of the
        dataframe.
        """
        parts = name.split()

        # Extract the first letter of each part and convert to uppercase
        initials = ''.join([part[0].upper() for part in parts if part.isalpha()])

        # Include the employee number in the initials string
        return parts[0] + "-" + initials

"""
Command Line Interface
"""
def main(option, schema) -> None:
    # Get data
    try:
        dbutil = DbUtility(schema)
        allocations = dbutil.readAllocationsDictFromCsv()
        duties = dbutil.readDutiesAsFlatList()
        #employees = dbutil.readEmployeesAsFlatList()
        shifts = dbutil.readShiftsAsFlatList()
        weeks = dbutil.readRotationWeeksAsFlatList()
    except Exception as e:
        print(f"\nThere was an error connecting to the database:\n{e}\n")
        return

    if option == 1: # Bid preference analysis
        vis = BidPreferenceAnalysis(allocations=allocations)
    elif option == 2: # Employee Allocations
        vis = EmployeeAllocations(allocations=allocations, duties=duties, shifts=shifts, weeks=weeks)

    vis.createVisualisation()

"""
Commnd Line Interface
"""
if __name__ == "__main__":
    # These imports change the python path at runtime.  This is specifically so that the
    # DbUtility can be used in the CLI only as it is not needed when Visualiser classes
    # are called from another program
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.database.scheduleDb import DbUtility
    
    # set the database schema
    schema = input("Enter a schema name (default: rm_scheduling): ")
    if schema in (None, ""):
        schema = "rm_scheduling"
    print(f"Schema set to: {schema}\n")

    # create a prompt for the CLI
    prompt = (
        "Choose from the following:\n"
        "1. Bid Preference Analysis\n"
        "2. Employee Allocations\n"
        "3. Exit\n"
        ">>>"
    )

    # Present the CLI options to the user
    while True:
        try:
            option = int(input(prompt))
        except:
            print("Invalid option chosen. Exiting...\n")
            break

        if option in (1, 2):
            main(option, schema)
        else:
            print("Exiting...\n")
            break
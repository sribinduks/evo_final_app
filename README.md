# _DS 3500 TA Evolutionary Framework Dashboard_

## _Instructions_
### 1. Run sorting.py
### 2. Run app.py
### 3. Click the web link to display the dashboard

## _Dash Features_
### - Displays a tradeoff curve for five objective functions: "over-assignment", "unwilling", "unpreferred", "conflict", and "overallocation"
### - Scatterplot displays five objective functions and the index in a hover display
### - Constraint sliders appear on the side and can be adjusted
### - User can set the time limit that evo runs
### - User can input an index number to generate a corresponding solution as a table of TA assignments
### - TA assigment table can be exported as an Excel file

## _Notes_
### - When user hovers over the index number, it can change over time due to the solution's evolution. The user can either wait till the program stops running at default time (1200 seconds) or add in a time limit to force the program to stop
### - The user can only input one time limit per run of evo

## _Warnings_
### The dashboard may display the errors: "list data out of range" and "pickle data truncated" but dash runs regardless

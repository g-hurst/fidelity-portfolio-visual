# fidelity-portfolio-visual

## Usage
To use this tool, a csv from a Fidelity portfolio must first be exported. This can be done by hitting the button in the picture below when looking at the **All Accounts** fiew in Fidelity. 

![Fildelity Export CSV Button](./images/fidelity_export_button.png)

Create a folder in the project named `portfolio_exports` in the project directory, and save the csv export with the default name that fidelity gives it. To spot check, the naming format that fidelity follows the format of `Portfolio_Positions_<MMM-DD-YYYY>.csv`. Proper formatting of the file name is critical for the program to run. 

The main code for this project is in [chart.py](./chart.py).
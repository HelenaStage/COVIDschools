# COVIDschools
Data and code required to reproduce findings pertaining to COVID-19 related school interventions

--- School closure ---



Analysis of school closure is a two step process. First, we use approximate Bayesian computation to produce 1000 posterior parameterisations of an SEIR compartmental epidemic model, before using a sample of these posteriors as covariates in a Negative Binomial latent Gaussian Process machine learning model. The functions used to construct and fit the SEIR model are stored in `mechanisitic_model.py`, and `pygom_abc.py`, and called upon by the notebooks `regional_ABC_fitting.ipynb` and `national_ABC_fitting.ipynb`. The model construciton and fitting process both rely on the PyGOM package for python. Outputs of the ABC fitting process have been included in this repository as some users have had difficulty using the PyGOM package. Users are also encouraged to use the provided case/hospitalisation data to fit ABC posteriors using their own methods.


## Generating ABC covariates


ABC posteriors are generated in the notebooks `regional_ABC_fitting.ipynb` (for german states) and `national_ABC_fitting.ipynb` (for Denmark, Sweden and Norway). Both these notebook require PyGOM to be installed to run properly. The notebooks should be run once for each naiton/state being investigated. Running these notebooks will produce files used as inputs to the GP model named `GP_input_data\{metric}_{region}.csv` (used to store observed data), and `GP_input_data\posteriors_{metric}_{region}.csv` (used to store the ABC posteriors), where `{metric}` refers to the value being observed (e.g. `new_cases` or `new_hosps`) and `region` refers to the abbreviated nation/state. For example running the notebok for confirmed cases in Berlin will produce files called `new_cases_DE_BE.csv` and `posteriors_new_cases_DE_BE.csv`. All intermediate files created in this process have been included in this repository. 


## Negative Binomial Latent Gaussian Process Regression


The GP model is fitted using notebook `CIM_NegBinom_GP.ipynb`. This notebook relies on the previously generated files, and uses the python package PyMC3. The region/nation being analysed should be stated in call three, using the variable `region`. For German states use, e.g. `DE_BE` for Berlin or `DE_NW` for North Rhine-Westphalia, and for nations use e.g. `NO` for Norway or `DK` for Denmark. The metric should be either `new_cases` for case data (used for German states and Sweden) or `new_hosps` (used for Norway and Denmark). Running this notebook for each state/nation will produce `.dictionary` files detailing the NegBinom GP model output, along with an image showing the modelled unintervened trajectory. 

### Package dependancies for school closure analysis:
- Numpy
- Pandas
- Matplotlib
- PyGOM
- PyMC3

For installation instructions for PyGOM please see https://github.com/PublicHealthEngland/pygom. 

The following file names include the data for school closure (including date accessed as numbers may since have changed):
- Denmark (accessed 20/06/2020): DK_data.csv
- Norway (accessed 02/06/2020): NO_data.csv
- Sweden (accessed 05/06/2020): SE_data.csv
- Germany: DE_reg_data_new.csv

Data from studied German states were obtained daily (with a day's delay). These files also include the projected trajectories resulting from the Gaussian Process forecast:
- Baden-Württemberg: Baden_results.csv
- Bavaria: Bavaria_results.csv
- Berlin: Berlin_results.csv
- Hesse: Hesse_results.csv
- Lower Saxony: LSaxony_results.csv
- North Rhine-Westphalia: NRW_results.csv
- Rhineland-Palatinate: Rhineland_results.csv

The script ConstGrowthRates.r will produce the pre- and post-response growth rates for each state.

--- School reopening ---

The following file names include the data for school reopening (including date accessed as numbers may since have changed):
- Denmark (hospital admissions, accessed 13/06/2020): denmark_data.csv
- Denmark (confirmed cases, accessed 13/06/2020): denmark_cases.csv
- Norway (accessed 13/06/2020): norway_data.csv
- Germany (hospital admissions, accessed 09/07/2020): germany_data_hosp.csv
- Germany (confirmed cases among staff and students, accessed 09/07/2020): germany_data_raw.csv

The script InstGrowthRates.r will produce the instantaneous growth rates for each data stream of interest, and this should be run first. For each data set of interest, the following Python scripts will overlay the instantaneous growth rates with the dates of key interventions:
- Danish daily hospital admissions: denmark.py
- Danish daily confirmed cases: denmark-cases.py
- Norwegian daily confirmed cases: norway.py
- German daily hospital admissions: germany_hosp.py
- German daily confirmed cases among staff and students: germany.py

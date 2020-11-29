# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 16:12:51 2020

@author: Joseph.Shingleton
"""
"""
This acts as a holder for a bunch of functions related to building and fitting
a mechanisitic model to the available data. 
"""
import numpy as np
import pandas as pd
from datetime import date
import pygom_abc as pgabc
from scipy.integrate import odeint
from scipy.optimize import minimize
from matplotlib import pyplot as plt
from pygom import Transition, TransitionType, DeterministicOde
from pygom.loss import NegBinomLoss, SquareLoss, PoissonLoss

#### Epidemic model ####

def prepare_ODE_model_data(df, fit_to='cases', N_to_fit= 25):
    """gets the required data to fit. Currently gets the first N deaths in the
    series which are none zero. 
    args:
        df: dataframe from which to pull data
        fit_to: column heading for fitting
        N_to_fit: number of none zero cases to fit
    returns:
        fit_data: list of data to fit to
        fit_end_point: index for end of fitting data
    """
    new_index = np.linspace(0, len(df), len(df) + 1)
    new_index = [int(x) for x in new_index]
    
    df = df.reset_index(drop=True)     
    
    fit_end_point =  N_to_fit

    fit_data = df[fit_to].values[:N_to_fit]
    
    return fit_data, fit_end_point

def ODE_model(N0):
    """This more complicated model can be used to fit for detected cases and hospitalisations (essentially the same thing).
    compartments are currently gamma distributed (shape=2). Will want to consider shape=3 distributions also. 
    args:
        N0: Population
    returns:
        model: a pygom ODEmodel object
    """
    states = ['S',  # susceptible
              'E0',
              'E1',# incubating
              'E2',
              'I',  # infectious (mild symptoms)
              'Id',  # infectious detected
              'Iu',  # infectious undetected
              'Id_cum', #Storing cummulative infections
              'R',]  # Removed (recoveries + fatalities)

    parameters = ['beta',   # infectivity of symptomatic cases
                  'alpha0',
                  'alpha1', 
                  'alpha2',# incubation period (time between being infected and developing symptoms)
                  'gamma', # hospitalisation
                  'kappa',
                  'delta1',
                  'delta2', # proportion of hospitalised/detected cases
                  'N0']     # population


    transitions = [Transition(origin='S', destination='E0', equation='beta*S*(I+Iu+Id)/(N0)',
                                  transition_type=TransitionType.T), # transmission from symptomatic cases 
                       Transition(origin='E0', destination='E1', equation='E0/alpha0',
                                  transition_type=TransitionType.T),
                       Transition(origin='E1', destination='E2', equation='E1/alpha1',
                                  transition_type=TransitionType.T), # latent to mild symptoms
                       Transition(origin='E2', destination='I', equation='E2/alpha2',
                                  transition_type=TransitionType.T), # latent to mild symptoms
                       Transition(origin='I', destination='Id', equation='kappa*I/gamma',
                                  transition_type=TransitionType.T), # mild symptoms to severe symptoms/hospitalisation         
                       Transition(origin='I', destination='Iu', equation='(1-kappa)*I/gamma',
                                  transition_type=TransitionType.T),  # mild symptoms to undetected
                       Transition(origin='Id', destination='R', equation='Id/delta1', 
                                  transition_type=TransitionType.T),
                       Transition(origin='Iu', destination='R', equation='Iu/delta2',
                                  transition_type=TransitionType.T)]
    
    births =           Transition(origin='Id_cum', equation='kappa*I/gamma',
                                  transition_type=TransitionType.B)


    model = DeterministicOde(states, parameters, transition=transitions, birth_death=births)
    model.parameters = {'beta':1.3, 
                        'alpha0':2.1,
                        'alpha1':2,
                        'alpha2':1.1,
                        'gamma': 7,
                        'kappa':0.1,
                        'delta1':14,
                        'delta2':14,
                        'N0':N0} 
    return model


def data_model(model, data, fit_to, times, weights, k, N0):

    """Sets up the model for fitting via approximate bayesian computation (ABC)
    args:
        model: determinisitic modle with dummy paramreter values (ODE object)
        data: data with which to fit the model (numpy array)
        times: time period over which to fit the model (numpy array)
        N0: population
    returns:
        model: abc_model object, not yet fitted.
    """
    print(type(data[0]))
    fit_to_dict = {'cases':'Id_cum', 'hospitalisations':'Id_cum', 'ICU':'Id_cum', 'new_hosps':'Id', 'new_cases':'Id'}
    
    fit_state = fit_to_dict[fit_to]

    E0_0 = 0
    E1_0 = 0
    E2_0 = 0
    I_0 = 0
    Id_0 = 0
    Iu_0 = 0
    Id_cum_0 = data[0]    
    R_0 = 0
    S_0 = N0 - (E0_0+E1_0+E2_0+I_0+Id_0+Iu_0+R_0)
    x_0 = [S_0, E0_0, E1_0,E2_0, I_0, Id_0, Iu_0, Id_cum_0, R_0]

    x_0 = [float(x) for x in x_0]
    initial_guess = [1.3, 7, 0.1, 14, 14]
    boxBounds = [(0,3), (0,5), (0,1), (0,21),(0,21),
                 (Id_cum_0/4,Id_cum_0*4),(Id_cum_0/4,Id_cum_0*4),(Id_cum_0/4,Id_cum_0*4),
                 (Id_cum_0/4,Id_cum_0*4),(Id_cum_0/4,Id_cum_0*4), (Id_cum_0/4,Id_cum_0)]
    print('BOX BOUNDS: {}'.format(boxBounds))
    # Need to seperate (x0, t0, w0, k0) from (xi, ti, wi, ki) for i!=0
    t_0 = times[0]
    t_i = times[1:]
    x_i = data[1:]
    k_i = k[1:]
    if weights is not None:
        w_i = weights[1:]
    else:
        w_i = None
    if k is not None:
        k_i = k[1:]
    else:
        k_i = None
    
    if fit_to == 'new_hosps':
        
        try:
            print('Using NegBinom loss')
            modelobj = NegBinomLoss(initial_guess, 
                               model, 
                               x_0, 
                               times[0], 
                               t_i, 
                               x_i, 
                               [fit_state],
                               w_i, 
                               k=k_i,
                               target_param=['beta','gamma', 'kappa', 'delta1', 'delta2'], 
                               target_state=['E0', 'E1','E2','I','Iu', 'Id'])
        except NameError:
            print('Using square loss')
            # Use SquareLoss if Pygom distribution is not updated with NegBinom (dev distribution is as of 20/06)
            modelobj = SquareLoss(initial_guess, 
                                  model, 
                                  x_0, 
                                  times[0], 
                                  t_i, 
                                  x_i, 
                                  [fit_state],
                                  target_param=['beta','gamma', 'kappa', 'delta1', 'delta2'], 
                                  target_state=['E0'])
    else:
        try:
            modelobj = NegBinomLoss(initial_guess, 
                               model, 
                               x_0, 
                               times[0], 
                               t_i, 
                               x_i, 
                               [fit_state],
                               w_i,
                               k=k_i,
                               target_param=['beta','gamma', 'kappa', 'delta1', 'delta2'], 
                               target_state=['E0', 'E1','E2','I','Iu', 'Id'])
            print('Using NegBinomLoss')
        except NameError:
            print('NegBinomLoss not available on this verssion of Pygom. Using SquareLoss')
            # Use SquareLoss if Pygom distribution is not updated with NegBinom (dev distribution is as of 20/06)
            modelobj = SquareLoss(initial_guess, 
                                  model, 
                                  x_0, 
                                  times[0], 
                                  t_i, 
                                  x_i, 
                                  [fit_state],
                                  w_i,
                                  target_param=['beta','gamma', 'kappa', 'delta1', 'delta2'], 
                                  target_state=['E0'])
    model = pgabc.ABC(modelobj, 
                      boxBounds, 
                      log10scale=[0,0,0,0,0,0,0,0,0,0,0], 
                      constraint=(N0,'S'))

    return model

### ABC fitting functions ###
def run_ABC_model(abc_model, ode_model, fit_end_point, sim_end_point, N0, generations=10):
    """takes an prepared ABC type model, calculates posteriors, and generates 
    a median simulation based on those posteriors, as well as 0.05 and 0.95 
    percentiles
    args:
        abc_model: a prepared abc type model
        ode_model: the mechnaistic model on which abc_model was generated
        fit_end_point: point at which fit data stops (int)
        sim_end_point: last time point to simulate to (int)
        N0: population
    returns:
        abc_model: fitted to data
        prediciton = [median, 0.05, 0.95]
        """
    abc_model.get_posterior_sample(N=1000,
                               tol=np.inf, 
                               G=generations, 
                               q=0.5, 
                               progress=True)    
    
    return abc_model


def fit_ODE_model(full_data, fit_data, fit_to, fit_end_point, weights, k, N0, generations):
    """runs the model base don the fitting data and returns simulated data, as
    well as th efitted model
    args:
        full_data: whole dataset from which fit data was extracted
        fit_to: column heading for fit_data
        fit_end_point: index for end of fitting data
        N0: population
        generations: number of ABC fitting generations
    return:
        ode_model: pygom ode model object
        fitted_model: abc_model object
    """
    sim_end_point = len(full_data)
    fit_times = np.linspace(0, fit_end_point-1, fit_end_point)
    ode_model = ODE_model(N0)
    abc_model = data_model(ode_model, fit_data, fit_to, fit_times, weights, k, N0)
    
    fitted_model = run_ABC_model(abc_model,
                                 ode_model,
                                 fit_end_point,
                                 sim_end_point, N0, generations)
    
    return ode_model, fitted_model



    

              
                   

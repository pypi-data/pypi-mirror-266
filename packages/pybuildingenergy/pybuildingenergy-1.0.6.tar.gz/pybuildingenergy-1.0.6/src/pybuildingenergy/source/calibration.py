from pybuildingenergy.data.building_archetype import Buildings_from_dictionary
from pybuildingenergy.source.utils import ISO52016
from pybuildingenergy.source.functions import ePlus_shape_data
import pandas as pd
import numpy as np
from pyswarms.single.global_best import GlobalBestPSO
import math

# ADD BEST-TESTs
new_bui = {
    # BUILDING FEATURE
    'building_type': 'BestTest600', # building type
    'periods': 2024, # year of construction 
    'latitude': 39.76,
    'longitude': -104.86, 
    'volume' : 129.6, # in m3
    'exposed_perimeter': 28, # perimeter in m
    'slab_on_ground': 48, # Area slab on ground in m2
    'wall_thickness' :  0.087, # in m
    'coldest_month': 1, 
    'a_use': 48,
    'surface_envelope': 48+48+21.6+21.6+12+16.2+16.2,
    'surface_envelope_model': 48+48+21.6+21.6+12+16.2+16.2,
    'annual_mean_internal_temperature': None,
    'annual_mean_external_temperature': None,
    # SYSTEMS 
    'side': 4.8,
    "heating_mode": True,
    "cooling_mode": True,
    'heating_setpoint': 20, # in °c
    'cooling_setpoint': 27, # in °c
    'heating_setback':20, # in °c
    'cooling_setback':27, # in °c
    'power_heating_max':1000000, # in W
    'power_cooling_max':-1000000, # in W
    # INTERNAL GAINS and VENTILATION LOSSES
    'air_change_rate_base_value':1.35 , # in m3/h*m2 = 0.018m3/s
    'air_change_rate_extra':0.0, # in m3/h*m2
    'internal_gains_base_value':4.1667, # in W/m2 =200W/48m2
    'internal_gains_extra':0, # in W/m2
    # THERMAL BRIDGES
    'thermal_bridge_heat' : 0.0, # in W/m
    # FEATURES OF FAACDE ELEMENTS:
    'thermal_resistance_floor': 0.039, 
    'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W"],dtype=object), 
    'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'SV'],dtype=object),
    'solar_abs_elements': np.array([0.6,0.6,0.6,0.6,0.0,0.6,0.0], dtype=object),
    'area_elements': [21.6, 9.6, 16.2,16.2, 48, 48, 12 ],
    'transmittance_U_elements' : [0.514, 0.514, 0.514, 0.514, 0.04, 0.318, 3],
    'thermal_resistance_R_elements' : [0, 0, 0, 0, 25.374, 0,0],
    # 'thermal_capacity_elements' : [14534, 14534,14534,14534, 19500, 89990, 0],
    'thermal_capacity_elements' : [19500, 14534,14534,14534, 19500, 18619, 0],
    # 'g_factor_windows' : [0]*6 +[0.86156],
    'g_factor_windows' : [0]*6 +[0.71],
    'heat_convective_elements_internal': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
    'heat_radiative_elements_internal': np.array([5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13],dtype=object),
    'heat_convective_elements_external': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
    'heat_radiative_elements_external': np.array([4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14],dtype=object),
    'sky_factor_elements': np.array([0.50, 0.50, 0.50, 0.50, 0.00, 1.00, 0.50], dtype=object), 
    'occ_level_wd':np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
    'occ_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
    'comf_level_wd': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
    'comf_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
    "construction_class": "class_i",
    # WEATHER FILE
    "weather_source": 'epw',
    "tmy_filename": "tmy_39.783_-104.892_2005_2015.csv",
    "location": None,
    # OPTIMIZATION
    'baseline_hci': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
    'baseline_hce': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
}

# CREATE Building object



def ISO52016_calibration_objective_function_monthly_heating_PSO(x, building_dict, 
                                                                real_months_values:np.array, 
                                                                weather_type,
                                                                path_weather_file_,
                                                                energy_cons_kWh_m2_rend):
                                                              
    '''
    Objective function oh the PSO optimization:
    The objectvie function refers to the heating consumption of the building. 
    it minimze the adjusted root mean sqaure deviation of the real value and the simulated ones:
    
    Parameters
    ----------
    inputs: inputs to be used by the bep_calc to calculate the energy need of the building usin the ISO 52016
    real_months_values: 12 values of real energy consumption of building in np.array
    bui_type: could be: schoolor other 
    tmy_data: weather data 
    
    Return 
    ------
    Value of the cost function 
    '''
    inputs_for_simulation = building_dict.copy()
    # copy of the original inputs to be used for the calculation of the nergy consumption 
    new_input_hci = (x.T[0].reshape(-1,1)* inputs_for_simulation['baseline_hci'])[0]
    new_input_hce = (x.T[1].reshape(-1,1)* inputs_for_simulation['baseline_hce'])[0]

    # new values of heat transfer coefficient internal and external
    inputs_for_simulation['heat_convective_elements_internal'] = new_input_hci
    inputs_for_simulation['heat_convective_elements_external'] = new_input_hce

    # Bilding simulation using the ISO 52016
    building_object_new = Buildings_from_dictionary(inputs_for_simulation)
    print(building_object_new.__getattribute__('heat_convective_elements_external'))
    hourly_results, annual_results_df = ISO52016().Temperature_and_Energy_needs_calculation(building_object_new, weather_source=weather_type, path_weather_file=path_weather_file_) 
    
    # from hourly values to montly values
    
    ISO52016_monthly_cooling_in_kWh_per_sqm = hourly_results['Q_C'].resample('ME').sum() / (1e3 * inputs_for_simulation['a_use'])
    print(ISO52016_monthly_cooling_in_kWh_per_sqm)
    #OBJECTIVE FUNCTION: adjusted root mean sqaure deviation      
    months = list(range(0,5)) + list(range(9,12))
    # real_months_values = np.array(energy_cons_kWh_m2_rend)[months]
    # real_months_values = np.array(energy_cons_kWh_m2_rend)
    # sim_data = ISO52016_monthly_heating_in_kWh_per_sqm.to_numpy()[months]
    sim_data = ISO52016_monthly_cooling_in_kWh_per_sqm.to_numpy()
    # n= len(months)
    n=12
    obj_funct = math.sqrt(sum((real_months_values-sim_data)**2)/(n-1))   
    print(obj_funct)
    # n=12         
    # obj_funct = math.sqrt(sum((real_months_values - ISO52016_monthly_heating_in_kWh_per_sqm.to_numpy())**2)/(n-1))
    return obj_funct


def PSO_optimizer(energy_cons_kWh_m2_rend, building_object:object, path_weather_file_:str, weather_type:str, 
                  monitored_monthly_data:np.array, number_iter:int, ftol_iter:float,
                  acceptable_cost_fc_value=1.0, ftol_PSO=0.5, ):
    '''
    Optimization process using the Partical Swarm Optimization. 
    The GlobalBestPSO has been modified adding a filter the stop the research if the value 
    of the cost function is lower than a desired value
    
    Parameters
    ----------
    inputs: inputs to be used by the bep_calc 
        to calculate the energy need of the building usin the ISO 52016
    real_months_values: 12 values of real 
        energy consumption of building in np.array
    tmy_data: weather data    
    bui_type: could be 'school' or other
    monitored_monthly_data: 12 values of real energy consumption 
        of building in np.array
    number_iter: number of maximum iteration 
    ftol_PSO: relative error in objective_func(best_pos) 
        acceptable for convergence. Default is :code: 0.3
    ftol_iter: number of iterations over which 
        the relative error in objective_func(best_pos) is acceptable for convergence.    
    acceptable_cost_fc_value: value of the cost function considered acceptable by the user (default is 1 [kWh/m2])
    
    '''
    
    options = {'c1': 0.5, 'c2': 0.3, 'w':0.9}
    bounds = (np.array([0.2,0.9]), np.array([0.5,2]))
    # bounds = (np.array([0.2,0.2]), np.array([10,10]))
    
    
    optimizer = GlobalBestPSO(n_particles=5, dimensions=2, options=options, bounds=bounds, 
                          ftol=ftol_PSO, ftol_iter=ftol_iter)

    # building_dict = building_object.__dict__
    cost, pos = optimizer.optimize(ISO52016_calibration_objective_function_monthly_heating_PSO, 
                                iters= number_iter,
                                # accept_bestcost_value= acceptable_cost_fc_value, 
                                building_dict=  building_object.__dict__, 
                                real_months_values= monitored_monthly_data,
                                weather_type= weather_type ,
                                path_weather_file_ = path_weather_file_,
                                energy_cons_kWh_m2_rend = energy_cons_kWh_m2_rend)
    return cost, pos 

path_epls_file = "/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/MODERATE/pyBuildingEnergy/pybuildingenergy/examples/energyPlus_data/Case600_V22.1.0out_Athens.csv"
path_weather_file_ = "/Users/dantonucci/Library/CloudStorage/OneDrive-ScientificNetworkSouthTyrol/MODERATE/pyBuildingEnergy/pybuildingenergy/examples/weatherdata/2020_Athens.epw"
def run_calibration(path_epls_file):

    building_object = Buildings_from_dictionary(new_bui)
    hourly_results, annual_results_df = ISO52016().Temperature_and_Energy_needs_calculation(building_object, weather_source='epw', path_weather_file=path_weather_file_) 
    ISO52016_monthly_heating_in_kWh_per_sqm = hourly_results['Q_H'].resample('ME').sum() / (1e3 * building_object.__getattribute__('a_use'))
    ISO52016_monthly_cooling_in_kWh_per_sqm = hourly_results['Q_C'].resample('ME').sum() / (1e3 * building_object.__getattribute__('a_use'))

    dir_energy_plus = path_epls_file
    eplus_data = ePlus_shape_data( pd.read_csv(dir_energy_plus), building_object.__getattribute__('a_use'))
    EnergyPlus_monthly_heating_in_kWh_per_sqm = eplus_data[0]
    EnergyPlus_monthly_cooling_in_kWh_per_sqm = eplus_data[1]
    ep_monthly_T_op = eplus_data[2]
    index = ISO52016_monthly_heating_in_kWh_per_sqm.index
    # df_ep_monthly = pd.DataFrame(index=index, data={'Q_H EnergyPlus' : EnergyPlus_monthly_heating_in_kWh_per_sqm, 'Q_C EnergyPlus' : EnergyPlus_monthly_cooling_in_kWh_per_sqm, 'T_op EnergyPlus' : ep_monthly_T_op})
    df_ep_monthly = pd.DataFrame(index=index, data={'Q_H EnergyPlus' : EnergyPlus_monthly_heating_in_kWh_per_sqm, 'Q_C EnergyPlus' : EnergyPlus_monthly_cooling_in_kWh_per_sqm})
    
    cost, options = PSO_optimizer(
        energy_cons_kWh_m2_rend = ISO52016_monthly_cooling_in_kWh_per_sqm.values.tolist(), 
        building_object= building_object,
        path_weather_file_=path_weather_file_,
        weather_type="epw",
        monitored_monthly_data = df_ep_monthly['Q_C EnergyPlus'].values.tolist(),
        number_iter=50,
        ftol_iter=50,
        acceptable_cost_fc_value=1.5, 
        ftol_PSO=1.5
    )
    print(cost)

    return cost, options

results = run_calibration(path_epls_file)
    # 
# # # REAL DATA
# energy_cons_GJ = [48.97, 40.25, 38.66, 20.11, 18.8, 0.6, 0, 0, 1.13, 28.89, 33.7, 46.63]
# energy_cons_kWh = list(map(lambda x: round(x * 277.778,2), energy_cons_GJ))
# energy_cons_kWh_m2 = list(map(lambda x: round(x/421.3,2), energy_cons_kWh))

# energy_cons_kWh_m2_rend = list(map(lambda x: round(x * 0.95 * 0.95 * 0.9 * 0.9,2), energy_cons_kWh_m2))
# energy_cons_kWh_m2_rend

# # # CALIBRATION 
# # #%% PSO CALIBRATION
# monitored_monthly_data = np.array(energy_cons_kWh_m2_rend)
# bui_type = "school"
# year_weather = 2015
# cost, options = PSO_optimizer(energy_cons_kWh_m2_rend, inputs, tmy_data, bui_type, year_weather, monitored_monthly_data, 
#                             number_iter=50, ftol_iter=50,
#                             acceptable_cost_fc_value=1.5, ftol_PSO=1.5)


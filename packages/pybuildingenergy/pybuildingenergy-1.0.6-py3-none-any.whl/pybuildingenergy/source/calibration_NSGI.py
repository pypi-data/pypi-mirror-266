
from pybuildingenergy.data.building_archetype import Buildings_from_dictionary
from pybuildingenergy.source.utils import ISO52016
from pybuildingenergy.source.functions import ePlus_shape_data
import pandas as pd
import numpy as np
import math

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
from pymoo.optimize import minimize

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



class MyProblem(ElementwiseProblem):

    def __init__(self, building_dict, energy_cons_kWh_m2_rend, real_months_values, weather_type, path_weather_file_):
        self.building_dict = building_dict, 
        self.energy_cons_kWh_m2_rend = energy_cons_kWh_m2_rend, 
        self.real_months_values= real_months_values,
        self.weather_type= weather_type,
        self.path_weather_file_= path_weather_file_
        super().__init__(
            n_var=2,
            n_obj=1,
            n_ieq_constr=2,
            xl=np.array([-2,-2]),
            xu=np.array([2,2]),              
            
            )

    def _evaluate(self, x, out, *args, **kwargs):

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
        inputs_for_simulation = self.building_dict[0]
        # copy of the original inputs to be used for the calculation of the nergy consumption 
        new_input_hci = (x[0].reshape(-1,1)* inputs_for_simulation['baseline_hci'])[0]
        new_input_hce = (x[1].reshape(-1,1)* inputs_for_simulation['baseline_hce'])[0]

        # new values of heat transfer coefficient internal and external
        inputs_for_simulation['heat_convective_elements_internal'] = new_input_hci
        inputs_for_simulation['heat_convective_elements_external'] = new_input_hce

        # Bilding simulation using the ISO 52016
        building_object_new = Buildings_from_dictionary(inputs_for_simulation)
        print(building_object_new.__getattribute__('heat_convective_elements_external'))
        print(building_object_new.__getattribute__('power_cooling_max'))
        hourly_results, annual_results_df = ISO52016().Temperature_and_Energy_needs_calculation(building_object_new, weather_source='epw', path_weather_file=self.path_weather_file_) 
        
        # from hourly values to monthly values
        
        ISO52016_monthly_heating_in_kWh_per_sqm = hourly_results['Q_H'].resample('ME').sum() / (1e3 * inputs_for_simulation['a_use'])
        ISO52016_monthly_cooling_in_kWh_per_sqm = hourly_results['Q_C'].resample('ME').sum() / (1e3 * inputs_for_simulation['a_use'])
        print(ISO52016_monthly_heating_in_kWh_per_sqm)
        #OBJECTIVE FUNCTION: adjusted root mean sqaure deviation      
        # months = list(range(0,5)) + list(range(9,12))
        # months = 12
        # real_months_values = np.array(self.energy_cons_kWh_m2_rend)
        sim_data = ISO52016_monthly_heating_in_kWh_per_sqm.to_numpy()
        # n= len(months)
        n=12
        obj_funct = math.sqrt(sum((self.real_months_values-sim_data)**2)/(n-1))   
        print(obj_funct)
        # n=12         
        # obj_funct = math.sqrt(sum((real_months_values - ISO52016_monthly_heating_in_kWh_per_sqm.to_numpy())**2)/(n-1))
        out["F"] = [obj_funct]

       
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
    
    problem = MyProblem(
        building_dict=  building_object.__dict__, 
        real_months_values=  df_ep_monthly['Q_C EnergyPlus'].values.tolist(),
        weather_type= "epw",
        path_weather_file_ = path_weather_file_,
        energy_cons_kWh_m2_rend = ISO52016_monthly_cooling_in_kWh_per_sqm.values.tolist()
    )

    algorithm = NSGA2(
        pop_size=40,
        n_offsprings=10,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )

    termination = get_termination("n_gen", 40)


    res = minimize(problem,
                algorithm,
                termination,
                seed=1,
                save_history=True,
                verbose=True)

    X = res.X
    F = res.F

run_calibration(path_epls_file)
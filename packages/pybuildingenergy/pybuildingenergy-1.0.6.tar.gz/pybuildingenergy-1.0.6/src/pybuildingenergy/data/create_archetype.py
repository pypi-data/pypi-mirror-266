# __author__ = "Daniele Antonucci, Ulrich Filippi Oberagger, Olga Somova"
# __credits__ = ["Daniele Antonucci", "Ulrich FIlippi Oberagger", "Olga Somova"]
# __license__ = "MIT"
# __version__ = "0.1"
# __maintainer__ = "Daniele Antonucci"

# '''

# # Acutal limitation
# Vedere test area edificio e area del solaio controterra differenti 
# # Italy:
# - tasso di ventilazione fissato a 0.3  h-1
# - considerato solo edifici tipo zona climatica media (E)

# '''

# import sys
# import os
# import pickle
# ###
# sys.path.append("/".join(os.path.realpath(__file__).split("/")[0:-2]))
# ####

# import numpy as np
# # from pybuildingenergy.data.profiles import profile_residential_1
# from profiles import profile_residential_1
# # from pybuildingenergy.src.functions import Perimeter_from_area, Area_roof, Internal_gains, Power_heating_system



# def Power_heating_system(bui_volume, bui_class):
#     """
#     Approssimative calculation of generator power, according to the following formula:
#     p = Voume[m3] * energy needs[kW/m3]

#     :param bui_class: could be:
#         * *'old'*: No or very low insulated building
#         * *'new'*: very well insulated building
#         * *'average'*:medium insulated building

#     :return heat_power: power of generator [W]
#     """
#     if bui_class == "old":
#         p = bui_volume * 0.12
#     elif bui_class == "gold":
#         p = bui_volume * 0.03
#     else:
#         p = bui_volume * 0.05

#     return p * 1000

# def Internal_gains(bui_type: str, area: float):
#     """
#     Calculation of internal gains according to the building typology

#     :param bui_type: type of building. Possible choice: residential, office, commercial
#     :param area: gross area of the building

#     :return: int_gains: value of internal gains in W/m2

#     .. note::
#         Only for residential building the data is avaialble.
#         The result is a sum of contribution given by equipments, people heat and lights
#     """
#     if bui_type == "residential":
#         int_gains = (120 + 100 + 2000 + 800 + 5 + 4 * 100) / area + 5 * 5

#     else:
#         int_gains = 5
#     return int_gains


# def Perimeter_from_area(area, side):
#     """
#     Perimeter from area assuming 10m of side

#     :param area: gross surface area of the slab on ground floor in [m]
#     :param side: side of a rectangular shape of the building
#     """
#     base = area / side
#     perimeter = 2 * (base + side)
#     return perimeter

# def Area_roof(leng_small, leng_roof):
#     """
#     Calculation of the roof area. According to the following formula:

#     formula = ((length_small*cos(28)+0.5*cos(28))*(length_roof+(0.5*2)))*2

#     **where**:

#     cos(28°) = 0.88

#     .. note:: 
#         The calculation assumes that the building has a rectangular floor plan.

#     :param leng_small: small length of roof side in [m]
#     :param leng_roof: length of roof side in [m]

#     """
#     Area = 2 * ((leng_small * 0.88) + (0.5 * 0.88)) * (leng_roof + (0.5 * 2))
#     return Area
# # ================================================================================================
# #                           COMPONENTS ARCHETYPE            
# # ================================================================================================

# # @Italy
# # WALL
# code_wall = ['wall01', 'wall02', 'wall03']
# description_wall = ['Masonry with lists of stones and bricks (40cm)', 'solid brick masonry', 'hollow brick masonry']
# thickness_wall = [0.40, 0.38, 0.40]
# heat_capacity_wall= [665658, 523248, 319500]
# U_wall= [ 1.61, 1.48, 1.26]
# R_wall= [1/value for value in U_wall]

# # ROOF 
# code_roof = ['roof01','roof02']
# description_roof = ['Pitched roof with wood structure and planking', 'Pitched roof with brick-concrete slab']
# thickness_roof = [0.34, 0.34]
# heat_capacity_roof= [278856, 390606]
# U_roof= [1.8, 2.2]
# R_roof= [1/value for value in U_roof]

# #FLOOR
# code_floor= ['floor01','floor02']
# description_floor = ['Concrete floor on soil', 'floor with reinforced brick-concreate slab, low insulation']
# thickness_floor = [0.27, 0.34]
# heat_capacity_floor= [463800, 448050]
# U_floor= [2.0, 0.98]
# R_floor= [1/value for value in U_floor]

# # WINDOW
# code_window = ['window01','window02']
# description_window = ['Single glass, methal frame without thermal break','single glasss wood frame']
# U_window = [5.7, 4.9]
# R_window = [1/value for value in U_window]
# g_window = [0.85, 0.85]

# # ========================================================================================================================
# #                                       INPUTS: SINGLE FAMILY HOUSE
# # ========================================================================================================================

# periods = ['before 1900', '1901-1920','1921-1945','1946-1960','1961-1875','1976-1990','1991-2005','2006-today']
# bui_types = ['single_family_house']*len(periods)
# wall_class = ['class_d', 'class_d','class_d', 'class_d', 'class_d','class_d','class_ie', 'class_e']
# nation = ['Italy']*len(periods)
# area = [139, 115, 116, 162, 156, 199, 172, 174]
# window_area = [17.4, 14.4, 14.5, 20.3, 19.5, 24.9, 21.5, 21.8] # 1/8 della superificie
# volume = [533,448,455,583,679,725,605,607]
# coldest_month = [1]*len(periods)
# S_V = [0.77, 0.82, 0.81, 0.75, 0.73, 0.72, 0.73, 0.72]
# S_envelope = [S*volume for S,volume in zip(S_V, volume)]
# number_of_floor = [2,2,2,2,2,2,2,2]
# height = [round(volume_i/(area_i/number_of_floor_i),2) for volume_i, area_i, number_of_floor_i in zip(volume, area, number_of_floor)]
# bui_height=[x / (y/z) for x, y,z in zip(volume, area, number_of_floor)]
# base= [(value/number_of_floor)/10 for value,number_of_floor in zip(area,number_of_floor)]
# perimeter =[Perimeter_from_area(value, 10/2) for value in area]
# area_north = [round(10 * heights,2) for heights in bui_height]
# area_south = area_north
# area_west = [round(bases * heights,2) for bases,heights in zip(base,bui_height)]
# area_east = area_west
# area_roof = [round(Area_roof(10, leng_roof)/2,2) for leng_roof in base]
# heating_mode = [True]*len(periods)
# cooling_mode = [True]*len(periods)
# heating_setpoint = [20]*len(periods)
# heating_setback = [10]*len(periods)
# cooling_setpoint = [26]*len(periods)
# cooling_setback = [26]*len(periods)
# thermal_bridge_heat  =[10]*len(periods)
# w_code = ['wall01','wall01','wall02','wall02','wall03','wall01','wall01','wall01']
# r_code = ['roof01','roof01','roof01','roof02','roof02','roof01','roof01','roof01']
# win_code= ['window01','window01','window02','window02','window02','window02','window02','window02']
# f_code = ['floor01','floor01','floor01','floor01','floor01','floor01','floor01','floor01']
# building_category_const = ['old','old','old','old','old','old','medium','medium']
# air_change_rate_base_value = [0.08,0.14,0.14, 0.1, 0.1, 0.1, 0.1,0.1]
# power_cooling = 10000
# # GLOBAL INPUTS
# typology_elements = np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W", "W", "W", "W"],dtype=object)
# orientation_elements =  np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'NV', 'SV', 'EV', 'WV'],dtype=object)
# solar_abs_elements =  np.array([1.0,1.0,1.0,1.0,0.0,1.0,0.6,0.6,0.6,0.6], dtype=object)
# heat_convective_elements_internal= np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50, 2.50, 2.50, 2.50], dtype=object)
# heat_radiative_elements_internal= np.array([5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13],dtype=object)
# heat_convective_elements_external= np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object)
# heat_radiative_elements_external= np.array([4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14],dtype=object)
# sky_factor_elements= np.array([0.50, 0.50, 0.50, 0.50, 0.00, 1.00, 0.50, 0.50, 0.50, 0.50], dtype=object)
# baseline_hci= np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50, 2.50, 2.50, 2.50], dtype=object)
# baseline_hce= np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object)


# profile_residential_1 = {
#     'code': 'profile01',
#     'type': 'residential',
#     'profile_workdays_internal_gains': np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
#     1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
#     'profile_weekend_internal_gains': np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
#     1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
#     'profile_workdays_ventilation': np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
#     1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
#     'profile_weekend_ventilation': np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
#     1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
# }

# heating_installed = [True]*len(periods)
# cooling_installed = [False]*len(periods)

# buis_dict = []
# for i,value in enumerate(bui_types):
#     bui = {
#         # BUILDING FEATURE
#         'nation':nation[i],
#         'building_type': bui_types[i], # building type
#         'periods': periods[i], # year of construction 
#         'latitude': None,
#         'longitude': None, 
#         'volume' : volume[i], # in m3
#         'exposed_perimeter': perimeter[i], # perimeter in m
#         'slab_on_ground': area[i]/number_of_floor[i], # Area slab on ground in m2
#         'wall_thickness' :  thickness_wall[code_wall.index(w_code[i])], # in m
#         'coldest_month': coldest_month[i], 
#         'a_use': area[i],
#         'surface_envelope': area_north[i]+ area_south[i] + area_east[i]+ area_west[i] + area[i] + area_roof[i],
#         'surface_envelope_model': S_envelope[i],
#         'S_V': S_V[i],
#         'annual_mean_internal_temperature': None,
#         'annual_mean_external_temperature': None,
#         # SYSTEMS 
#         'side': base[i],
#         "heating_mode": heating_mode[i],
#         "cooling_mode": cooling_mode[i],
#         'heating_setpoint': heating_setpoint[i], # in °c
#         'cooling_setpoint': cooling_setpoint[i], # in °c
#         'heating_setback':heating_setback[i], # in °c
#         'cooling_setback':cooling_setback[i], # in °c
#         'power_heating_max':Power_heating_system(volume[i], building_category_const[i]), # in W
#         'power_cooling_max':-10000, # in W
#         # INTERNAL GAINS and VENTILATION LOSSES
#         'air_change_rate_base_value':air_change_rate_base_value[i] , # in m3/h*m2
#         'air_change_rate_extra':0.0, # in m3/h*m2
#         'internal_gains_base_value':Internal_gains('residential', area[i]), # in W/m2
#         'internal_gains_extra':0, # in W/m2
#         # THERMAL BRIDGES
#         'thermal_bridge_heat' : thermal_bridge_heat[i], # in W/m
#         # FEATURES OF FACADE ELEMENTS:
#         'thermal_resistance_floor': R_floor[code_floor.index(f_code[i])], 
#         'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W", "W", "W", "W"],dtype=object), 
#         'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'NV', 'SV', 'EV', 'WV'],dtype=object),
#         'solar_abs_elements': np.array([0.6,0.6,0.6,0.6,0.0,0.6,0.0, 0.0, 0.0, 0.0], dtype=object),
#         'area_elements': list((area_north[i], area_south[i], 
#                 area_east[i],area_west[i],
#                 area[i]/2, area_roof[i], 
#                 round(0.1*window_area[i],2),round(0.3*window_area[i],2),
#                 round(0.3*window_area[i],2),round(0.3*window_area[i],2))
#         ), # Area of each facade elements ,
#         'transmittance_U_elements' : [U_wall[code_wall.index(w_code[i])]]*4+ [U_floor[code_floor.index(f_code[i])]] + [U_roof[code_roof.index(r_code[i])]] +[U_window[code_window.index(win_code[i])]]*4,
#         'thermal_resistance_R_elements' : [R_wall[code_wall.index(w_code[i])]]*4+ [R_floor[code_floor.index(f_code[i])]] + [R_roof[code_roof.index(r_code[i])]] +[R_window[code_window.index(win_code[i])]]*4,
#         'thermal_capacity_elements' : [heat_capacity_wall[code_wall.index(w_code[i])]]*4+ [heat_capacity_floor[code_floor.index(f_code[i])]] + [heat_capacity_roof[code_roof.index(r_code[i])]] +[0]*4,
#         'g_factor_windows' : [0]*6 +[g_window[code_window.index(win_code[i])]]*4,   
#         'heat_convective_elements_internal': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50, 2.50, 2.50, 2.50], dtype=object),
#         'heat_radiative_elements_internal': np.array([5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13],dtype=object),
#         'heat_convective_elements_external': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
#         'heat_radiative_elements_external': np.array([4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14],dtype=object),
#         'sky_factor_elements': np.array([0.50, 0.50, 0.50, 0.50, 0.00, 1.00, 0.50, 0.50, 0.50, 0.50], dtype=object), 
#         'occ_level_wd': profile_residential_1['profile_workdays_internal_gains'],
#         'occ_level_we': profile_residential_1['profile_weekend_internal_gains'],
#         'comf_level_wd': profile_residential_1['profile_workdays_ventilation'],
#         'comf_level_we': profile_residential_1['profile_weekend_ventilation'],
#         "construction_class": wall_class[i],
#         # WEATHER FILE
#         "weather_source": 'pvgis',
#         "tmy_filename": None,
#         "location": None,
#     }
#     buis_dict.append(bui)

# '''
# IWG5 SFH 
# _ Internal Gains (W/m2): 
#     # ELECTRIC EQUIPMENT
#     4.44666236343168 for Residential_Electric Equipment 1
#     4.44666236343168 for Residential_Electric Equipment 2
#     # LIGHTS 
#     10 for Residential_c9625ab5_SFH0
#     10 for Residential_c9625ab5_SFH1

# _ Flow rate (W/m2)
#     0.000747126436781609 for Residential_c9625ab5_SFH0
#     0.000526175249302814 for Residential_c9625ab5_SFH1 Flow Rate per Exterior Surface Area {m3/s-m2}

# Schedule:
# Residential_Setpoint_HtgSetp Schedule_Sunday,  !- Name
#     Temperature,             !- Schedule Type Limits Name
#     No,                      !- Interpolate to Timestep
#     07:00,                   !- Time 1 {hh:mm}
#     18,                      !- Value Until Time 1
#     20:00,                   !- Time 2 {hh:mm}
#     20,                      !- Value Until Time 2
#     24:00,                   !- Time 3 {hh:mm}
#     18;                      !- Value Until Time 3

# '''

# # iwg5_single_family_house = {
# #     'building_type': 'iwg5_SFH',
# #     'periods':2024,
# #     'latitude': 39.76,
# #     'longitude': -104.86,
# #     'volume': 192.4+140.4, 
# #     'slab_on_ground': 52,
# #     'wall_thickness':  , # in m
# #     'coldest_month': 1, 
# #     'a_use': ,
# #     'surface_envelope': ,
# #     'surface_envelope_model': ,
# #     'annual_mean_internal_temperature': None,
# #     'annual_mean_external_temperature': None,
# #     # SYSTEMS 
# #     'side': 4.8,
# #     "heating_mode": True,
# #     "cooling_mode": True,
# #     'heating_setpoint': 20, # in °c
# #     'cooling_setpoint': 27, # in °c
# #     'heating_setback':20, # in °c
# #     'cooling_setback':27, # in °c
# #     'power_heating_max':1000000, # in W
# #     'power_cooling_max':-1000000, # in W
# #     # INTERNAL GAINS and VENTILATION LOSSES
# #     'air_change_rate_base_value':0.000747126436781609 , # in m3/h*m2 = 0.018m3/s
# #     'air_change_rate_extra':0.0, # in m3/h*m2
# #     'internal_gains_base_value':14.44666236343168, # in W/m2 =10 W/m2 Lights + 4.44.. int 
# #     'internal_gains_extra':0, # in W/m2
# #     # THERMAL BRIDGES
# #     'thermal_bridge_heat' : 0.0, # in W/m
# #     # FEATURES OF FAACDE ELEMENTS:
# #     'thermal_resistance_floor': 0.039, 
# #     'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W"],dtype=object), 
# #     'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'SV'],dtype=object),
# #     'solar_abs_elements': np.array([0.6,0.6,0.6,0.6,0.0,0.6,0.0], dtype=object),
# #     'area_elements': [21.6, 9.6, 16.2,16.2, 48, 48, 12 ],
# #     'transmittance_U_elements' : [0.514, 0.514, 0.514, 0.514, 0.04, 0.318, 3],
# #     'thermal_resistance_R_elements' : [0, 0, 0, 0, 25.374, 0,0],
# #     # 'thermal_capacity_elements' : [14534, 14534,14534,14534, 19500, 89990, 0],
# #     'thermal_capacity_elements' : [19500, 14534,14534,14534, 19500, 18619, 0],
# #     # 'g_factor_windows' : [0]*6 +[0.86156],
# #     'g_factor_windows' : [0]*6 +[0.71],
# #     'heat_convective_elements_internal': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
# #     'heat_radiative_elements_internal': np.array([5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13],dtype=object),
# #     'heat_convective_elements_external': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
# #     'heat_radiative_elements_external': np.array([4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14],dtype=object),
# #     'sky_factor_elements': np.array([0.50, 0.50, 0.50, 0.50, 0.00, 1.00, 0.50], dtype=object), 
# #     'occ_level_wd':np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
# #     'occ_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
# #     'comf_level_wd': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
# #     'comf_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
# #     "construction_class": "class_i",
# #     # WEATHER FILE
# #     "weather_source": 'epw',
# #     "tmy_filename": "tmy_39.783_-104.892_2005_2015.csv",
# #     "location": None,
# #     # OPTIMIZATION
# #     'baseline_hci': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
# #     'baseline_hce': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
# # }

# bt_1A = {
#     # BUILDING FEATURE
#     'building_type': 'Example1A', # building type
#     'periods': 2024, # year of construction 
#     'latitude': 39.76,
#     'longitude': -104.86, 
#     'volume' : 129.6, # in m3
#     'exposed_perimeter': 28, # perimeter in m
#     'slab_on_ground': 48, # Area slab on ground in m2
#     'wall_thickness' :  0.087, # in m
#     'coldest_month': 1, 
#     'a_use': 48,
#     'surface_envelope': 48+48+21.6+21.6+12+16.2+16.2,
#     'surface_envelope_model': 48+48+21.6+21.6+12+16.2+16.2,
#     'annual_mean_internal_temperature': None,
#     'annual_mean_external_temperature': None,
#     # SYSTEMS 
#     'side': 4.8,
#     "heating_mode": True,
#     "cooling_mode": True,
#     'heating_setpoint': 20, # in °c
#     'cooling_setpoint': 27, # in °c
#     'heating_setback':20, # in °c
#     'cooling_setback':27, # in °c
#     'power_heating_max':1000000, # in W
#     'power_cooling_max':-1000000, # in W
#     # INTERNAL GAINS and VENTILATION LOSSES
#     'air_change_rate_base_value':1.35 , # in m3/h*m2 = 0.018m3/s
#     'air_change_rate_extra':0.0, # in m3/h*m2
#     'internal_gains_base_value':4.1667, # in W/m2 =200W/48m2
#     'internal_gains_extra':0, # in W/m2
#     # THERMAL BRIDGES
#     'thermal_bridge_heat' : 0.0, # in W/m
#     # FEATURES OF FAACDE ELEMENTS:
#     'thermal_resistance_floor': 0.039, 
#     'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W"],dtype=object), 
#     'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'SV'],dtype=object),
#     'solar_abs_elements': np.array([0.6,0.6,0.6,0.6,0.0,0.6,0.0], dtype=object),
#     'area_elements': [21.6, 9.6, 16.2,16.2, 48, 48, 12 ],
#     'transmittance_U_elements' : [0.514, 0.514, 0.514, 0.514, 0.04, 0.318, 3],
#     'thermal_resistance_R_elements' : [0, 0, 0, 0, 25.374, 0,0],
#     # 'thermal_capacity_elements' : [14534, 14534,14534,14534, 19500, 89990, 0],
#     'thermal_capacity_elements' : [19500, 14534,14534,14534, 19500, 18619, 0],
#     # 'g_factor_windows' : [0]*6 +[0.86156],
#     'g_factor_windows' : [0]*6 +[0.71],
#     'heat_convective_elements_internal': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
#     'heat_radiative_elements_internal': np.array([5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13],dtype=object),
#     'heat_convective_elements_external': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
#     'heat_radiative_elements_external': np.array([4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14],dtype=object),
#     'sky_factor_elements': np.array([0.50, 0.50, 0.50, 0.50, 0.00, 1.00, 0.50], dtype=object), 
#     'occ_level_wd':np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     'occ_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     'comf_level_wd': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     'comf_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     "construction_class": "class_i",
#     # WEATHER FILE
#     "weather_source": 'epw',
#     "tmy_filename": "tmy_39.783_-104.892_2005_2015.csv",
#     "location": None,
#     # OPTIMIZATION
#     'baseline_hci': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
#     'baseline_hce': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
# }


# # ADD BEST-TESTs
# bt_600 = {
#     # BUILDING FEATURE
#     'building_type': 'BestTest600', # building type
#     'periods': 2024, # year of construction 
#     'latitude': 39.76,
#     'longitude': -104.86, 
#     'volume' : 129.6, # in m3
#     'exposed_perimeter': 28, # perimeter in m
#     'slab_on_ground': 48, # Area slab on ground in m2
#     'wall_thickness' :  0.087, # in m
#     'coldest_month': 1, 
#     'a_use': 48,
#     'surface_envelope': 48+48+21.6+21.6+12+16.2+16.2,
#     'surface_envelope_model': 48+48+21.6+21.6+12+16.2+16.2,
#     'annual_mean_internal_temperature': None,
#     'annual_mean_external_temperature': None,
#     # SYSTEMS 
#     'side': 4.8,
#     "heating_mode": True,
#     "cooling_mode": True,
#     'heating_setpoint': 20, # in °c
#     'cooling_setpoint': 27, # in °c
#     'heating_setback':20, # in °c
#     'cooling_setback':27, # in °c
#     'power_heating_max':1000000, # in W
#     'power_cooling_max':-1000000, # in W
#     # INTERNAL GAINS and VENTILATION LOSSES
#     'air_change_rate_base_value':1.35 , # in m3/h*m2 = 0.018m3/s
#     'air_change_rate_extra':0.0, # in m3/h*m2
#     'internal_gains_base_value':4.1667, # in W/m2 =200W/48m2
#     'internal_gains_extra':0, # in W/m2
#     # THERMAL BRIDGES
#     'thermal_bridge_heat' : 0.0, # in W/m
#     # FEATURES OF FAACDE ELEMENTS:
#     'thermal_resistance_floor': 0.039, 
#     'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W"],dtype=object), 
#     'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'SV'],dtype=object),
#     'solar_abs_elements': np.array([0.6,0.6,0.6,0.6,0.0,0.6,0.0], dtype=object),
#     'area_elements': [21.6, 9.6, 16.2,16.2, 48, 48, 12 ],
#     'transmittance_U_elements' : [0.514, 0.514, 0.514, 0.514, 0.04, 0.318, 3],
#     'thermal_resistance_R_elements' : [0, 0, 0, 0, 25.374, 0,0],
#     # 'thermal_capacity_elements' : [14534, 14534,14534,14534, 19500, 89990, 0],
#     'thermal_capacity_elements' : [19500, 14534,14534,14534, 19500, 18619, 0],
#     # 'g_factor_windows' : [0]*6 +[0.86156],
#     'g_factor_windows' : [0]*6 +[0.71],
#     'heat_convective_elements_internal': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
#     'heat_radiative_elements_internal': np.array([5.13, 5.13, 5.13, 5.13, 5.13, 5.13, 5.13],dtype=object),
#     'heat_convective_elements_external': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
#     'heat_radiative_elements_external': np.array([4.14, 4.14, 4.14, 4.14, 4.14, 4.14, 4.14],dtype=object),
#     'sky_factor_elements': np.array([0.50, 0.50, 0.50, 0.50, 0.00, 1.00, 0.50], dtype=object), 
#     'occ_level_wd':np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     'occ_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     'comf_level_wd': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     'comf_level_we': np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], dtype=object),
#     "construction_class": "class_i",
#     # WEATHER FILE
#     "weather_source": 'epw',
#     "tmy_filename": "tmy_39.783_-104.892_2005_2015.csv",
#     "location": None,
#     # OPTIMIZATION
#     'baseline_hci': np.array([2.50, 2.50, 2.50, 2.50, 0.70, 5.00, 2.50], dtype=object),
#     'baseline_hce': np.array([20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],dtype=object),
# }
# buis_dict.append(bt_600)

# #  CREATE PICKLE FILE 
# # Specify the path to the pickle file
# pickle_file_path = 'archetypes.pickle'

# # Write data to the pickle file
# with open(pickle_file_path, 'wb') as f:
#     pickle.dump(buis_dict, f)


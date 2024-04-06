"""This module contains a Wind turbine."""

import math
from copy import deepcopy

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ...model.generator import Generator
from ...util.air_density_at_height import (
    AIR_DENSITY_KG_PER_M3,
    barometric,
    ideal_gas,
)
from ...util.temperature_at_height import linear_gradient
from ...util.wind_at_height import hellman, logarithmic_profile
from .config import WindPowerPlantConfig
from .inputs import WindPowerPlantInputs
from .state import WindPowerPlantState


class WindPowerPlant(Generator):
    """Simulation model of a windturbine plant.

    The code for the corrections and power output is heavily inspired
    by the windpowerlib::

        https://github.com/wind-python/windpowerlib

    """

    def __init__(self, params, inits):
        self.config: WindPowerPlantConfig = WindPowerPlantConfig(params)
        self.state: WindPowerPlantState = WindPowerPlantState(inits)
        self.inputs: WindPowerPlantInputs = WindPowerPlantInputs()

    def step(self):
        """Perform a simulation step."""
        next_state = deepcopy(self.state)
        self._check_inputs(next_state)

        # First step: wind speed at hub height using hellmann or
        # logarithmic profile
        if self.config.wind_profile == "hellmann":
            next_state.wind_hub_v_m_per_s = hellman(
                self.inputs.wind_v_m_per_s,
                self.config.wind_height_m,
                self.config.hub_height_m,
            )

        elif self.config.wind_profile == "logarithmic":
            next_state.wind_hub_v_m_per_s = logarithmic_profile(
                self.inputs.wind_v_m_per_s,
                self.config.wind_height_m,
                self.config.hub_height_m,
            )

        # Second step: temperature at hub height using linear gradient
        # need T and P  at hub height
        if self.config.temperature_profile == "linear_gradient":
            next_state.t_air_hub_deg_kelvin = linear_gradient(
                self.inputs.t_air_deg_kelvin,
                self.config.temperature_height_m,
                self.config.hub_height_m,
            )
        else:
            next_state.t_air_hub_deg_kelvin = self.inputs.t_air_deg_kelvin

        # Third step: air density at hub height using temperature at
        # hub height. Two different profiles available: barometric or
        # ideal_gas

        if self.config.air_density_profile == "barometric":
            next_state.air_density_hub_kg_per_m3 = barometric(
                self.inputs.air_pressure_hpa,
                next_state.t_air_hub_deg_kelvin,
                self.config.pressure_height_m,
                self.config.hub_height_m,
            )
            wind_speed_corrected = self.wind_curve_correction(
                next_state.air_density_hub_kg_per_m3
            )

        elif self.config.air_density_profile == "ideal_gas":
            next_state.air_density_hub_kg_per_m3 = ideal_gas(
                self.inputs.air_pressure_hpa,
                next_state.t_air_hub_deg_kelvin,
                self.config.pressure_height_m,
                self.config.hub_height_m,
            )
            wind_speed_corrected = self.wind_curve_correction(
                next_state.air_density_hub_kg_per_m3
            )
        else:
            # No air density correction; use default value
            next_state.air_density_hub_kg_per_m3 = AIR_DENSITY_KG_PER_M3
            wind_speed_corrected = self.config.wind_speeds_m_per_s

        # Last step: power output with either power_curve or
        # power_coefficient method
        if self.config.method == "power_curve":
            next_state.p_kw = self.power_curve_output(
                next_state.wind_hub_v_m_per_s, wind_speed_corrected
            )
        elif self.config.method == "power_coefficient":
            next_state.p_kw = self.power_coefficient_output(
                next_state.air_density_hub_kg_per_m3,
                next_state.wind_hub_v_m_per_s,
            )
        # if self.config.use_air_density_correction:
        #     # using air density correction we calculate automaticaly the pressure  at  hub height so we have 2 cases barometric  or ideal gas
        #     # self.config.air_density the value before  correction
        #     if self.config.air_density_correction_profile == "barometric":
        #         next_state.air_density_kg_per_m3 = self.barometric(
        #             next_state.t_air_hub_deg_celsius
        #         )
        #         if self.config.method == "power_curve":
        #             next_state.p_kw = np.interp(
        #                 next_state.wind_hub_v_m_per_s,
        #                 self.power_curve_correction(
        #                     next_state.air_density_kg_per_m3,
        #                 ),
        #                 self.config.power_curve["value"].values,
        #                 left=0,
        #                 right=0,
        #             )

        #         elif self.config.method == "power_coefficient":
        #             next_state.p_kw = self.power_coefficient_output(
        #                 next_state.air_density_kg_per_m3, next_state.wind_hub_v_m_per_s
        #             )

        #     elif self.config.air_density_correction_profile == "ideal_gas":
        #         next_state.air_density_kg_per_m3 = self.ideal_gas(next_state.t_air_hub_deg_celsius)
        #         if self.config.method == "power_curve":
        #             next_state.p_kw = np.interp(
        #                 next_state.wind_hub_v_m_per_s,
        #                 self.power_curve_correction(
        #                     next_state.air_density_kg_per_m3,
        #                 ),
        #                 self.config.power_curve["value"].values,
        #                 left=0,
        #                 right=0,
        #             )

        #         elif self.config.method == "power_coefficient":
        #             next_state.p_kw = self.power_coefficient_output(
        #                 next_state.air_density_kg_per_m3, next_state.wind_hub_v_m_per_s
        #             )

        #     # caculate the air density at hub height
        #     # then call the power curve correction using temperature and pressre at hub height

        #     # no air density correction

        # else:
        #     next_state.air_density_kg_per_m3 = (
        #         self.config.air_density
        #     )  # take the default value of air density
        #     if self.config.method == "power_curve":
        #         next_state.p_kw = np.interp(
        #             next_state.wind_hub_v_m_per_s,
        #             self.config.power_curve["wind_speed"],
        #             self.config.power_curve["value"],
        #             left=0,
        #             right=0,
        #         )

        #     elif self.config.method == "power_coefficient":
        #         next_state.p_kw = self.power_coefficient_output(
        #             next_state.air_density_kg_per_m3, next_state.wind_hub_v_m_per_s
        #         )

        # # last step the choice of power output  methed
        # # 2 cases power curve  or power coefficient

        # # only to see if the conditions works

        # if self.config.method == "power_curve":
        #     next_state.p_kw = self.power_curve_correction(
        #         next_state.wind_hub_v_m_per_s,
        #     )
        #     print(f"method is : {str(self.config.method):$^44}")

        # elif self.config.method == "power_coefficient":
        #     print(f"method is : {str(self.config.method):$^44}")

        # print(power_curve_correction(  self.config.air_density, self.config.power_curve["wind_speed"] ))
        # Scale to step size

        # the power output

        # next_state.p_kw *= self.inputs.step_size / 3600

        self.state = next_state
        self.inputs.reset()

    ############################################################################
    ############ Class methods are used in specific situations     #############
    # ##########################################################################

    def wind_curve_correction(
        self, density: float, density0: float = AIR_DENSITY_KG_PER_M3
    ):
        """Power curve at hub height

        Air density initial is set to the default value 1.225
        The correction is displayed in the new values of power_curve_wind_speeds
        """
        interpolation = np.interp(
            self.config.wind_speeds_m_per_s,
            [7.5, 12.5],
            [1 / 3, 2 / 3],
        )
        power_curve_correction = (
            np.array(density0 / density).reshape(-1, 1) ** interpolation
        ) * self.config.wind_speeds_m_per_s

        return power_curve_correction[0]

    # def atmospheric_pressure(self, h, P0=101325, h0=0):
    #     """Calculate the pressure at hub height starting from sea level
    #     pressure P0.

    #     P0=1013.25   Standard sea level pressure (Pa)

    #     """

    #     M = 0.029  # Molar mass of air in kg/mol
    #     g = 9.81  # Acceleration due to gravity in m/s^2
    #     R = 8.314  # Universal gas constant in J/(mol·K)
    #     T0 = 288.15  # Standard temperature at sea level in K

    #     # Calculate the temperature at altitude h using the standard lapse rate
    #     lapse_rate = -0.0065  # K/m
    #     T = T0 + lapse_rate * h

    #     # Calculate atmospheric pressure using the barometric formula
    #     P = P0 * math.exp(-M * g * (h - h0) / (R * T))

    #     return P

    # def linear_gradient(
    #     self, temperature: float, gradient: float = -0.0065
    # ) -> float:
    #     """Calculate temperature at hub height.

    #     Using air temperature at data height to calculate the
    #     temperature at hub height. Linear temperature gradient model is
    #     used. Uses hub height of wind turbine in m from the config.

    #     Parameters
    #     ----------
    #     temperature: float
    #         Air temperature in Kelvin
    #     gradient: float (optional)
    #         Temperature gradient of -6.5 K/km (-0.0065 K/m)

    #     """
    #     return temperature + gradient * (
    #         self.config.hub_height - self.config.temperature_height
    #     )

    # def barometric(self, next_state.t_air_hub_deg_celsius):
    #     """
    #     the barometric height equation to
    #     calculate the air density at hub height using pressure and Temperature at hub height
    #     R is the specific gas constant for dry air (around 287.05 J/(kg·K)).
    #     Pressure gradient of -1/8 hPa/m   ASSUMPTION
    #      1.225   # rho
    #      pressure:  Air pressure in Pa.
    #      pressure_height : Height in m for which the parameter `pressure` applies. the  same for  temperature_height
    #      pressure_height: hub height of wind turbine in m.
    #      next_state.t_air_hub_deg_celsius : Air temperature at hub height in K
    #     """

    #     #

    #     # pressure_height = temperature_height
    #     # pressure = self.atmospheric_pressure(
    #     #      pressure
    #     # )
    #     # pressure_height = self.atmospheric_pressure(hub_height )
    #     #   next_state.t_air_hub_deg_celsius = self.linear_gradient(
    #     #      temperature, self.config.temperature_height, self.config.hub_height
    #     #  )

    #     return (
    #         self.pressure_correction(self.inputs.air_pressure_hpa)
    #         * 1.225
    #         * 288.15
    #         / (101330 * next_state.t_air_hub_deg_celsius)
    #     )

    # def ideal_gas(self, next_state.t_air_hub_deg_celsius):
    #     """
    #     ideal gas
    #     the barometric height equation to
    #     calculate the air density at hub height using pressure and Temperature at hub height
    #     gas constant of dry air (287.058 J/(kg*K))
    #     return air density at hub height
    #     """
    #     return self.pressure_correction(self.inputs.air_pressure_hpa) / (
    #         287.058 * next_state.t_air_hub_deg_celsius
    #     )

    # def pressure_correction(self, pressure: float) -> float:
    #     """calculate the air pressure at hub height.

    #     At altitude h.
    #     """

    #     return (
    #         pressure * 100
    #         - (self.config.hub_height - self.config.pressure_height) * 1 / 8
    #     ) * 100

    # def logarithmic_profile(
    #     self,
    #     wind_speed: float,
    #     roughness_length: float = 0.15,
    #     obstacle_height: float = 0.0,
    # ) -> float:
    #     """Logarithmic wind profile.

    #     Calculate the wind speed at altitude h using logarithmic profile
    #     """

    #     return (
    #         wind_speed
    #         * np.log(
    #             (self.config.hub_height - 0.7 * obstacle_height)
    #             / roughness_length
    #         )
    #         / np.log(
    #             (self.config.wind_speed_height - 0.7 * obstacle_height)
    #             / roughness_length
    #         )
    #     )

    # def hellman(
    #     self, wind_speed: float, hellman_exponent: float = 1 / 7
    # ) -> float:
    #     """Wind profile using the Hellman law.

    #     Calculate the wind speed at altitude h using hellmann formula.
    #     """

    #     return (
    #         wind_speed
    #         * (self.config.hub_height / self.config.temperature_height)
    #         ** hellman_exponent
    #     )

    def power_curve_output(
        self,
        wind_speed,
        power_curve,
    ):
        """
        Calculation of the power curve value for a given wind speed by
        interpolation of power curve values dictionary.
        the only value required is the wind speed at hub  height
         wind_hub  = method(logarithmic_profile or hellmann profile)

        """

        power_output = np.interp(
            wind_speed,
            power_curve,
            self.config.power_curve_w,
            left=0,
            right=0,
        )
        return power_output / 1000  # to kW

    def power_coefficient_output(self, air_density, wind_speed):
        """
        calculate the poweroutput using  power coffecient method
        method that requires the following parameters: rotor diameter,  density
        which means it offers more versatile parameters to play with
        """
        # Use of the interpolated power_coefficient  to determine the output power

        power_coefficient_inter = np.interp(
            wind_speed,
            self.config.wind_speeds_m_per_s,
            self.config.power_coefficient,
            left=0,
            right=0,
        )

        return (
            1
            / 8
            * air_density
            * self.config.rotor_diameter**2
            * np.pi
            * np.power(wind_speed, 3)
            * power_coefficient_inter
        ) / 1000  # to kW

    def _check_inputs(self, nstate):
        pass

    #
    #

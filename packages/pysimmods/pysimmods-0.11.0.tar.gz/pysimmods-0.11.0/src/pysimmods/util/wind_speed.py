import numpy as np
import pandas as pd
import math
from pysimmods.generator.turbinesim.config import TurbineConfig


def logarithmic_profile(
    wind_speed,
    wind_speed_height,
    hub_height,
    roughness_length=0.15,
    obstacle_height=0.0,
):
    return (
        wind_speed
        * np.log((hub_height - 0.7 * obstacle_height) / roughness_length)
        / np.log(
            (wind_speed_height - 0.7 * obstacle_height) / roughness_length
        )
    )


# the other method Hellme
def hellman(
    wind_speed,
    wind_speed_height,
    hub_height,
    hellman_exponent=1 / 7,
):
    return wind_speed * (hub_height / wind_speed_height) ** hellman_exponent


# Calculate the pressure at altitude h using the barometric formula
def atmospheric_pressure(h, P0=101325):  # p0 in  1013.25 hPa-->Pa
    M = 0.029  # Molar mass of air in kg/mol
    g = 9.81  # Acceleration due to gravity in m/s^2
    R = 8.314  # Universal gas constant in J/(mol·K)
    T0 = 288.15  # Standard temperature at sea level in K

    # Calculate the temperature at altitude h using the standard lapse rate
    lapse_rate = -0.0065  # K/m
    T = T0 + lapse_rate * h

    # Calculate atmospheric pressure using the barometric formula
    P = P0 * math.exp(-M * g * h / (R * T))

    return P


def pressure_at_altitude(altitude_meters, sea_level_pressure_pa=101325.0):
    # Constants for the barometric equation
    L = 0.0065  # Temperature lapse rate (Kelvin per meter)
    T0 = 288.15  # Standard temperature at sea level (Kelvin)
    R = 287.05  # Specific gas constant for dry air (Joules per kilogram per Kelvin)
    g = 9.80665  # Acceleration due to gravity (meters per second squared)

    # Calculate temperature at the given altitude
    temperature_kelvin = T0 - L * altitude_meters

    # Calculate pressure at the given altitude
    pressure_pa = sea_level_pressure_pa * (1 - (L * altitude_meters) / T0) ** (
        g / (R * L)
    )

    return pressure_pa


# Example usage:
altitude = 1000  # Altitude in meters
pressure = pressure_at_altitude(altitude)
print(f"Pressure at {altitude} meters: {pressure} Pa")

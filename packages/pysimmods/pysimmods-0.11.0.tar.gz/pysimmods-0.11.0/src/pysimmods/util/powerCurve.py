def power_curve_correction(density, power_curve_wind_speeds):
    power_curve_correction = (
        (1.225 / density).reshape(-1, 1)
        ** np.interp(power_curve_wind_speeds, [7.5, 12.5], [1 / 3, 2 / 3])
    ) * power_curve_wind_speeds

    return power_curve_correction[0]

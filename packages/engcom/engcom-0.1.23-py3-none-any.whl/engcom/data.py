"""Module that generates data sets"""
import numpy as np


def step_response(
    time=None,
    ntime=101,
    maxtime=10,
    noisy=True,
    system_order=2,
    damping_ratio=0.5,
    natural_freq=1,
    time_constant=1,
):
    """Returns simulated step response data through time"""
    # Time
    if not time:
        time = np.linspace(0, maxtime, ntime)
    elif type(time) != np.ndarray:
        time = np.array(time)
    # Response Definition
    if system_order > 2:
        raise (ValueError("Paremeter system_order must be < 3."))
    if system_order == 1:
        def response(t):
            return np.exp(-t / time_constant)
    elif system_order == 2:
        l1 = (
            -damping_ratio * natural_freq
            + natural_freq * np.emath.sqrt(damping_ratio**2 - 1)
        )
        l2 = (
            -damping_ratio * natural_freq
            - natural_freq * np.emath.sqrt(damping_ratio**2 - 1)
        )
        def response(t):
            return (
                1
                / natural_freq**2
                * (
                    1
                    - 1
                    / (l2 - l1)
                    * (l2 * np.exp(l1 * t) - l1 * np.exp(l2 * t))
                )
            )

    # Response and Noise
    y = np.real(response(time))
    u = np.ones(y.shape)
    if noisy:
        std = 0.01 * max(y)
        y = y + std * np.random.standard_normal(y.shape)
    return {
        "time": time,
        "input": u,
        "output": y
    }

def policy_adoption():
    """Returns predicted probability data for policy adoption 
    vs percent of group in favor of policy. 
    Groups: average citizens and economic elites
    
    From Martin Gilens and Benjamin I. Page article
    Testing Theories of American Politics: Elites, Interest Groups, and Average Citizens
    http://dx.doi.org/10.1017/S1537592714001595
    Values read visually from Figure 1
    """
    percent_favoring_policy_change = np.array(range(10,110,10))
    predicted_prob_of_adoption_average = np.array([0.3, 0.3, 0.31, 0.31, 0.31, 0.31, 0.31, 0.32, 0.32, 0.33])
    predicted_prob_of_adoption_elite = np.array([0.01, 0.13, 0.2, 0.25, 0.3, 0.33, 0.37, 0.42, 0.48, 0.6])
    return {
        "percent_favoring_policy": percent_favoring_policy_change,
        "adoption_average": predicted_prob_of_adoption_average,
        "adoption_elite": predicted_prob_of_adoption_elite,
    }
    
def ideal_gas(
    V=None,
    T=None,
    n=1, 
    R=8.3145,
    noisy=True,
):
    """Returns ideal gas law data (Pressure vs Volume and Pressure)"""
    def pressure(V, n=1, R=8.3145, T=273.15):
        """Ideal gas law"""
        return n * R * T / V
    if V is None:
        V = np.linspace(1, 2, 11)
    elif type(V) == int:
        V = np.linspace(1, 2, V)
    elif type(V) == range:
        V = np.array(V)
    V = np.reshape(V, (len(V), 1))
    if T is None:
        T = np.linspace(273.15, 573.15, 4)
    elif type(T) == int:
        T = np.linspace(273.15, 573.15, T)
    elif type(T) == range:
        T = np.array(T)
    T = np.reshape(T, (1, len(T)))
    P = pressure(V, T)
    if noisy:
        if type(noisy) == int or type(noisy) == float:
            std = noisy * (np.max(P) - np.min(P))  # Standard deviation is scaled by noisy
        else:
            std = 0.01 * (np.max(P) - np.min(P))
        P = P + std * np.random.standard_normal(P.shape)
    return {
        "volume": V,
        "temperature": T,
        "pressure": P,
    }

def movie_ratings_binned():
    """The author's movie rating frequencies for 89 movies, 
    in 10 bins of size 1 from 0-10
    """
    rating_freq = np.array([0, 1, 6, 6, 18, 18, 20, 13, 5, 2])
    labels = []
    for i in range(0, len(rating_freq)):
        labels.append(f"{i}–{i+1}")
    return {
        "rating_freq": rating_freq,
        "labels": labels,
    }


def thermal_conductivity(category=None, paired=True):
    """Thermal conductivity in W/(m K) at 293 K and 100 kPa
    
    Source: Carvill, James. 1994. Mechanical Engineer's Data Handbook. 
    11th edition.
    """
    data_all = {
        "Metals": {
            "Aluminium": 239,
            "Antimony": 18,
            "Brass (60/40)": 96,
            "Cadmium": 92,
            "Chromium": 67,
            "Cobalt": 69,
            "Constantan": 22,
            "Copper": 386,
            "Gold": 310,
            "Inconel": 15,
            "Iron, cast": 55,
            "Iron, pure": 80,
            "Lead": 35,
            "Magnesium": 151,
            "Molybdenum": 143,
            "Monel": 26,
            "Nickel": 92,
            "Platinum": 67,
            "Silver": 419,
            "Steel, mild": 50,
            "Steel, stainless": 25,
            "Tin": 67,
            "Tungsten": 172,
            "Uranium": 28,
            "Zinc": 113,
        },
        "Liquids": {
            "Benzene": 0.16,
            "Carbon tetrachloride": 0.11,
            "Ethanol (ethyl alcohol)": 0.18,
            "Ether": 0.14,
            "Glycerine": 0.29,
            "Kerosene": 0.15,
            "Mercury": 8.80,
            "Methanol(methyl alcohol)": 0.21,
            "Oil, machine ": 0.15,
            "Oil, transformer": 0.13,
            "Water": 0.58,
        },
        "Gases": {
            "Air": 0.024,
            "Ammonia": 0.022,
            "Argon": 0.016,
            "Carbon dioxide": 0.015,
            "Carbon monoxide": 0.023,
            "Helium": 0.142,
            "Hydrogen": 0.168,
            "Methane": 0.030,
            "Nitrogen": 0.024,
            "Oxygen": 0.024,
            "Water vapour": 0.016,
        },
        "Plastics": {
            "Acrylic (Perspex)": 0.20,
            "Epoxy": 0.17,
            "Epoxy glass fibre": 0.23,
            "Nylon 6": 0.25,
            "Polyethylene, low density": 0.33,
            "Polyethylene, high density": 0.50,
            "PTFE": 0.25,
            "PVC": 0.19,
        },
        "Refrigerants at critical temperature": {
            "Ammonia (132.4 C)": 0.049,
            "Ethyl chloride (187.2 C)": 0.095,
            "Freon 12 (112 C)": 0.076,
            "Freon 22 (97 C)": 0.10,
            "Sulphur dioxide (157.2 C)": 0.0087,
        },
        "Insulators": {
            "Asbestos cloth": 0.13,
            "Balsa wood (average)": 0.048,
            "Calcium silicate": 0.05,
            "Compressed straw slab": 0.09,
            "Corkboard": 0.04,
            "Cotton wool": 0.029,
            "Diatomaceous earth": 0.06,
            "Diatomite": 0.12,
            "Expanded polystyrene": (0.03, 0.04),
        },
        "Miscellaneous:": {
            "Felt": 0.04,
            "Glass fibre quilt": 0.043,
            "Glass wool quilt": 0.040,
            "Hardboard": 0.13,
            "Kapok": 0.034,
            "Magnesia": 0.07,
            "Mineral wool quilt": 0.04,
            "Plywood": 0.13,
            "Polyurethane foam": 0.03,
            "Rock wool": 0.045,
            "Rubber, natural": 0.130,
            "Sawdust": 0.06,
            "Slag wool": 0.042,
            "Urea formaldehyde": 0.040,
            "Wood": (0.13, 0.17),
            "Wood wool slab": (0.10, .15),
        }
    }
    if category is not None:
        data = data_all[category]
        if not paired:
            d_pairs = np.array(list(data.items())).T
            data = {
                "labels": d_pairs[0].tolist(),
                "conductivity": np.array(d_pairs[1].copy(), dtype=float),
            }
    else:
        data = data_all
    return data


def game_of_life_starts(key: str) -> list:
    """Returns a list with a Conway's Game of Life starting state (alive: 1, dead: 0)"""
    starts = {
        "gosper_glider": [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        ]
    }
    return starts[key]
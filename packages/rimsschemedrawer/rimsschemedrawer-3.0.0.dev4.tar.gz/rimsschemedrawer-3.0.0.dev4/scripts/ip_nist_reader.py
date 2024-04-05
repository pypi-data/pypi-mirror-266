"""Create json file with all ionization potentials.

Elemental data read from the NIST database, which can be found here:
https://physics.nist.gov/PhysRefData/ASD/levels_form.html

2024-02-29: Currently, the following elements have no IP data associated with them:
    - Mt
    - Ds
    - Rg
    - Cn
    - Nh
    - Fl
    - Mc
    - Lv
    - Ts
    - Og
"""

import json

import requests


def get_url(ele: str) -> str:
    """Get URL for csv file from NIST.

    :param ele: String of element, e.g., Mg

    :return: URL to get csv file from NIST.
    """
    url = (
        f"https://physics.nist.gov/cgi-bin/ASD/energy1.pl?de=0&spectrum={ele}+"
        f"I&units=0&format=2&output=0&page_size=15&multiplet_ordered=0&conf_out"
        f"=on&term_out=on&level_out=on&unc_out=1&j_out=on&lande_out=on&perc_out"
        f"=on&biblio=on&temp=&submit=Retrieve+Data"
    )
    return url


def get_ip(ele: str) -> float:
    """Get ionization potential from NIST.

    :param ele: String of element, e.g., Mg

    :return: Ionization potential in eV.
    """
    data = requests.get(get_url(ele)).text
    data = data.split("\n")

    # find limit line in data
    limit_found = False
    for it, line in enumerate(data):
        if "Limit" in line:
            idx = it
            limit_found = True
            break

    if not limit_found:
        try:
            return manual_ips[ele]
        except KeyError:
            print(f"Could not find limit for {ele}")
            return None

    line = data[idx].replace('"', "").replace("=", "").split(",")
    # print(line)
    ip = line[4]
    if ip == "[" or ip == "":
        ip = line[5]  # we got a best guess value in []
    return float(ip)


manual_ips = {}

elements = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Ds",
    "Rg",
    "Cn",
    "Nh",
    "Fl",
    "Mc",
    "Lv",
    "Ts",
    "Og",
]

ele_ips = {}

for ele in elements:
    print(f"{ele} is up")
    ele_ips[ele] = get_ip(ele)

with open("ip_nist.json", "w") as fout:
    json.dump(ele_ips, fout, indent=4)

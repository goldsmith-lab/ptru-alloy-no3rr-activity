# -*- coding: utf-8 -*-
"""
Interface to MKMCXX microkinetics modelling software (https://www.mkmcxx.nl/).
Provides interfaces for writing input files, calling MKMCXX, and reading the
output.
"""

import os
import re
import subprocess
import pandas as pd
import glob
import natsort
import warnings


class Compound:
    """
    Represents a chemical compound in MKMCXX.

    Parameters
    ----------
    name : str
        A unique string identifying the compound. The convention to use unstarred
        chemical symbols for non-surface species (e.g., CO, H2) and starred symbols
        for surface-adsorbed species (CO*, H*), although whether the program treats
        the species as surface-adsorbed is always controlled by the attribute
        `is_site`
    is_site : bool
        True if the species is a surface-adsorbed species and false if it is a free
        species.
    start_conc : float
        The initial concentration of this species, in units of TODO: SPECIFY!
    tdrc : bool, optional
        Whether to include species in the total degree of rate control (TDRC)
        analysis. This has an effect only if TDRC is turned on in the settings.
    """

    def __init__(self, name: str, is_site: bool, start_conc: float, tdrc: bool = False):
        """Set up attributes"""

        self.name = name
        self.is_site = is_site
        self.start_conc = start_conc
        self.tdrc = tdrc

    def __repr__(self):
        return (
            f"Compound({self.name}, is_site={self.is_site}, "
            f"start_conc={self.start_conc}, tdrc={self.tdrc})"
        )

    def __str__(self):
        return f"{self.name}; {int(self.is_site)}; {self.start_conc}; {int(self.tdrc)}"


class Reaction:
    """Represents a chemical reaction in MKMCXX

    Parameters
    ----------
    reactants : dict
        A dictionary of the form {compound: quantity}, where compound is a
        `Compound` object representing a chemical reactant and `quantity` is
        the stoichiometric coefficient in front of that compound. The
        stoichiometry coefficients must be positive. E.g., for the reaction
        {CO} + 2{*} => {C*} + {O*}, this parameter would be {Compound("CO",
        ...): 1, Compound("*", ...): 2)}.
    products : dict
        A dictionary of the form {compound: quantity}, where compound is a
        `Compound` object representing a chemical product and `quantity` is the
        stoichiometric coefficient in front of that compound. The stoichiometry
        coefficients must be positive. E.g., for the reaction {CO} + 2{*} =>
        {C*} + {O*}, this parameter would be {Compound("C*", ...): 1,
        Compound("O*", ...): 1)}.
    """

    def __init__(self, reactants: dict, products: dict):
        self.reactants = reactants
        self.products = products

    def _unwrap_dict(self, dict):
        """Write out a reactant or product dictionary.
        Assumes that dictionary is of valid format."""

        result = " + ".join([f"{quantity}{{{c.name}}}" for c, quantity in dict.items()])

        return result

    def get_rxn_string(self):
        """
        String representation of the reaction alone. Useful for generating
        dictionary keys.
        """

        return (
            f"{self._unwrap_dict(self.reactants)} => "
            f"{self._unwrap_dict(self.products)}"
        )


class HKReaction(Reaction):
    """Represents a chemical reaction in MKMCXX

    Parameters
    ----------
    reactants : dict
        A dictionary of the form {compound: quantity}, where compound is a
        `Compound` object representing a chemical reactant and `quantity` is
        the stoichiometric coefficient in front of that compound. The
        stoichiometry coefficients must be positive. E.g., for the reaction
        {CO} + 2{*} => {C*} + {O*}, this parameter would be {Compound("CO",
        ...): 1, Compound("*", ...): 2)}.
    products : dict
        A dictionary of the form {compound: quantity}, where compound is a
        `Compound` object representing a chemical product and `quantity` is the
        stoichiometric coefficient in front of that compound. The stoichiometry
        coefficients must be positive. E.g., for the reaction {CO} + 2{*} =>
        {C*} + {O*}, this parameter would be {Compound("C*", ...): 1,
        Compound("O*", ...): 1)}.
    m2 : float
        [description]
    amu : float
        [description]
    K : float
        [description]
    sigma : float
        [description]
    sticking : float
        [description]
    jmol : float
        [description]
    do_drc : bool, optional
        True if any DRC or TDRC analyses performed should include this
        reaction. By default, False.
    """

    def __init__(
        self,
        reactants: dict,
        products: dict,
        m2: float,
        amu: float,
        K: float,
        sigma: float,
        sticking: float,
        jmol: float,
        do_drc: bool = False,
    ):

        # Store reactants and products
        super(HKReaction, self).__init__(reactants, products)

        # Store other parameters
        self.m2 = m2
        self.amu = amu
        self.K = K
        self.sigma = sigma
        self.sticking = sticking
        self.jmol = jmol
        self.do_drc = do_drc

    def __repr__(self):
        return (
            f"HKReaction({self._unwrap_dict(self.reactants)} "
            f"=> {self._unwrap_dict(self.products)}, "
            f"m2 = {self.m2:.3E}, "
            f"amu = {self.amu:.3E}, "
            f"K = {self.K:.3E}, "
            f"sigma = {self.sigma:.3E}, "
            f"sticking = {self.sticking:.3E}, "
            f"jmol = {self.jmol:.3E}, "
            f"do_drc = {self.do_drc})"
        )

    def __str__(self):
        return (
            f"HK; {self._unwrap_dict(self.reactants)} => "
            f"{self._unwrap_dict(self.products)}; "
            f"{self.m2}; {self.amu}; {self.K}; "
            f"{self.sigma}; {self.sticking}; "
            f"{self.jmol}; {int(self.do_drc)}"
        )


class ARReaction(Reaction):
    """Represents a chemical reaction in MKMCXX

    Parameters
    ----------
    reactants : dict
        A dictionary of the form {compound: quantity}, where compound is a
        `Compound` object representing a chemical reactant and `quantity` is
        the stoichiometric coefficient in front of that compound. The
        stoichiometry coefficients must be positive. E.g., for the reaction
        {CO} + 2{*} => {C*} + {O*}, this parameter would be {Compound("CO",
        ...): 1, Compound("*", ...): 2)}.
    products : dict
        A dictionary of the form {compound: quantity}, where compound is a
        `Compound` object representing a chemical product and `quantity` is the
        stoichiometric coefficient in front of that compound. The stoichiometry
        coefficients must be positive. E.g., for the reaction {CO} + 2{*} =>
        {C*} + {O*}, this parameter would be {Compound("C*", ...): 1,
        Compound("O*", ...): 1)}.
    vf : float
        Forward reaction velocity (e.g., forward pre-exponential factor)
    vb : float
        Backward reaction velocity (e.g., backward pre-exponential factor)
    Eaf : float
        Forward reaction activation energy
    Eab : float
        Backward reaction activation energy
    do_drc : bool, optional
        True if any DRC or TDRC analyses performed should include this
        reaction. By default, False.
    """

    def __init__(
        self,
        reactants: dict,
        products: dict,
        vf: float,
        vb: float,
        Eaf: float,
        Eab: float,
        do_drc: bool = False,
    ):

        # Store reactants and products
        super(ARReaction, self).__init__(reactants, products)

        # Store other parameters
        self.vf = vf
        self.vb = vb
        self.Eaf = Eaf
        self.Eab = Eab
        self.do_drc = do_drc

    def __repr__(self):
        return (
            f"ARReaction({self._unwrap_dict(self.reactants)} "
            f"=> {self._unwrap_dict(self.products)}, "
            f"vf = {self.vf:.3E}, "
            f"vb = {self.vb:.3E}, "
            f"Eaf = {self.Eaf:.3E}, "
            f"Eab = {self.Eab:.3E}, "
            f"do_drc = {self.do_drc})"
        )

    def __str__(self):
        return (
            f"AR; {self._unwrap_dict(self.reactants)} "
            f"=> {self._unwrap_dict(self.products)}; "
            f"{self.vf:.3E}; {self.vb:.3E}; {self.Eaf:.3E}; "
            f"{self.Eab:.3E}; {int(self.do_drc)}"
        )


class MicrokineticSimulation:
    """Base class for writing out a microkinetics simulation

    Parameters
    ----------
    reactions : list
        A list of ARReaction or HRReaction objects which will be included in the
        simulation
    settings : dict
        Settings for the simulation. By default, this dictionary is {"type":
        "sequencerun", "pressure": 1.0, "usetimestamp": false, "abstol": 1e-12,
        "reltol": 1e-12}
    runs : list
        If settings["type"] is "sequencerun", then `runs` specifies the different
        temperature scenarios to perform. `runs` should be a list of the form
        [{"temp": (temperature in K), "time": (max time in seconds)}, ...]
    directory: str, optional
        The directory where simulation input and output data should be stored.
        By default, the current working directory.
    restart : bool
        Whether to restart from previous simulation results. If True, then
        directory must be specified.
    run_directory: str, optional
        Name of the subdirectory where actual sequence run results are stored,
        by default "run". If this name is different (e.g., "SEQUENCERUN_*"),
        then specify that name here.
    """

    def __init__(
        self,
        reactions: list,
        settings: dict = None,
        runs: list = None,
        directory: str = None,
        restart=False,
        run_directory: str = "run",
    ):

        if restart and directory:
            raise NotImplementedError("Haven't implemented restart capabilities yet.")
        else:

            # Import reactions
            self.reactions = reactions

            # Process the reactants and products in each reaction to get the list
            # of unique compounds.
            compounds = []
            compounds.extend(
                [compound for r in reactions for compound, _ in r.reactants.items()]
            )
            compounds.extend(
                [compound for r in reactions for compound, _ in r.products.items()]
            )

            compounds = list(set(compounds))
            self.compounds = compounds

            # Apply default settings and update with any user arguments
            default_settings = {
                "type": "sequencerun",
                "usetimestamp": False,
                "abstol": 1e-12,
                "reltol": 1e-12,
            }

            if settings:
                default_settings.update(settings)

            self.settings = default_settings

            # If sequencerun type was specified, then require the user to input
            # sequence run information.

            if self.settings["type"] == "sequencerun":
                if not runs:
                    raise Exception(
                        "Detected a sequence run setup but no "
                        "runs were specified. You must specify runs."
                    )

                if not isinstance(runs, list):
                    raise Exception(
                        """You must specify a list of runs "
                        "of the format {"temp": temp, "time": time}."""
                    )

                self.runs = runs

            # Set up directory information
            if directory:
                self.directory = directory
            else:
                self.directory = os.getcwd()

            self.run_directory = run_directory

    def __repr__(self):
        string = ""

        string += "MicrokineticSimulation(\n"
        string += f"    Compounds:"

        for compound in self.compounds:
            string += f"\n        {compound.__repr__()}"

        string += f"\n\n    Reactions:"

        for reaction in self.reactions:
            string += f"\n        {reaction.__repr__()}"

        string += f"\n\n    Settings:\n"

        string += self.settings.__repr__()

        string += "\n)"

        return string

    def _print_setting(self, key, val):
        """Easy way to correctly print out a setting key for the input file"""

        if isinstance(val, str):
            return f"{key.upper()} = {val.upper()}"
        elif isinstance(val, float):
            return f"{key.upper()} = {val}"
        elif isinstance(val, bool):
            return f"{key.upper()} = {int(val)}"
        elif isinstance(val, list) and all([isinstance(s, str) for s in val]):
            # Probably a list of Compounds. Render them as such
            compound_str = ", ".join([f"{{{s}}}" for s in val])
            return f"{key.upper()} = {compound_str}"
        else:
            return f"{key.upper()} = {str(val)}"

    def __str__(self):

        result = ""

        # Write out the MKMCXX input in the correct format.
        result += "# MKMCXX input file generated by Samueldy Atomistic Utils"

        # Compounds section
        result += "\n&compounds"
        result += "\n# Name; is_site; start_conc; tdrc"
        for compound in self.compounds:
            result += "\n" + str(compound)

        result += "\n\n&reactions"
        # Don't let the user duplicate reactions.
        for reaction in set(self.reactions):
            if isinstance(reaction, HKReaction):
                result += (
                    "\n\n# Type; Reaction; area (m^2); amu; K; sigma; sticking; J/mol"
                )
            elif isinstance(reaction, ARReaction):
                result += "\n\n# Type; Reaction; vf; vb; Eaf; Eab"
            result += "\n" + str(reaction)

        if self.settings:
            # Don't want to print absolute and relative tolerances in the
            # settings section.
            settings_to_print = self.settings.copy()
            for k in ["abstol", "reltol"]:
                settings_to_print.pop(k)

            result += "\n\n&settings"
            for key, val in settings_to_print.items():
                result += f"\n{self._print_setting(key, val)}"

        # result +=  runs, if any
        if self.runs:
            result += "\n\n&runs"
            result += "\n# Temp; Time; AbsTol; RelTol"
            for run in self.runs:
                result += (
                    f"""\n{run["temp"]}; {run["time"]}; """
                    f"""{self.settings["abstol"]}; {self.settings["reltol"]}"""
                )

        # EOF
        result += "\n# End of input file."

        return result

    def write_input_files(self):
        """Write input file"""

        # Create target directory if it does not exist.
        if not os.path.exists(self.directory):
            os.makedirs(self.directory, exist_ok=True)

        with open(os.path.join(self.directory, "input.mkm"), "w", newline="\n") as f:
            f.write(self.__str__())

    def run(self, args: list = ["mkmcxx", "-i", "input.mkm"]):
        """Actually run the simulation

        Parameters
        ----------
        args : list, optional
            The list of command arguments to be passed to `subprocess.run`, by
            default ["mkmcxx", "-i", "input.mkm"]. Change this if you need to
            run a different command instead.

        Returns
        -------
        int
            The return code of the MKMCXX call
        bytes
            Captured standard output from the run
        bytes
            Captured standard error from the run
        """

        # Ensure input file is written.
        self.write_input_files()

        # Change to target directory
        curr_dir = os.getcwd()
        os.chdir(self.directory)

        try:
            # Call MKMCXX. Assumes that MKMCXX is on your path.
            p = subprocess.run(args=args, capture_output=True)

        finally:
            # Make sure to change back to the old working directory!!
            os.chdir(curr_dir)

        return p.returncode, p.stdout, p.stderr

    def read_results(self):
        """
        Read results from a previous calculation. The `run_directory` class
        variable must correspond to the actual run folder, or this will fail.
        """

        try:
            return {
                "range_results": self._read_range_results(),
                "temperature_results": self._read_temperature_run_results(),
                "drc_results": self._read_drc_results(),
            }
        except (FileNotFoundError, OSError):
            raise RuntimeError(
                "Cannot locate results. Please ensure that all results "
                "are present and that the `directory` and "
                "`run_directory` parameters are correctly set."
            )

    def _read_and_trim_df(self, fname, **kwargs) -> pd.DataFrame:
        """
        Wrapper around Pandas DataFrame reader so that we can take care of the
        issues with column names having too much whitespace around them.

        Parameters
        ----------
        fname : filepath or buffer
            Any valid string path, path object, or file-like object that can be
            passed to `pd.read_csv()`.

        Returns
        -------
        pd.DataFrame
            Dataframe where the column names have whitespace trimmed from the
            left and right sides.
        """

        df = pd.read_csv(fname, **kwargs)
        out_df = df.copy()
        columns = list(df.columns)
        columns = [c.strip() for c in columns]
        out_df.columns = columns

        return out_df

    def _read_range_results(self):
        """Read the data in the `range` directory
        """

        data_directory = os.path.join(self.directory, self.run_directory, "range")

        range_results = {
            os.path.basename(fname).split(".")[0]: self._read_and_trim_df(
                fname, sep="\t"
            )
            for fname in glob.glob(os.path.join(data_directory, "*.dat"))
        }

        return range_results

    def _read_drc_results(self):
        """
        Small plugin to read steady-state DRC results. Assumes that the results
        are in a folder called self.run_directory, not a time-stamped folder.
        """

        data_directory = os.path.join(
            self.directory, self.run_directory, "range", "drc"
        )

        try:
            drc_results = {
                os.path.basename(fname)
                .split(".")[0]: self._read_and_trim_df(fname, sep="\t")
                .transpose()
                for fname in glob.glob(os.path.join(data_directory, "*.dat"))
            }
        except (FileNotFoundError, OSError):
            warnings.warn(
                "Could not find DRC results files. "
                "Perhaps you didn't ask for them to be calculated?"
            )

        return drc_results

    def _read_temperature_run_results(self):
        """
        Read results for each of the temperature runs specified in the run
        folder.
        """

        data_directory = os.path.join(self.directory, self.run_directory)

        # Loop through and get just the "100K", "200K", etc. directories.
        dirs_to_process = [
            os.path.basename(dname)
            for dname in natsort.natsorted(
                glob.glob(os.path.join(data_directory, "*K"))
            )
        ]

        # For each directory, read in the coverage and derivative tables as
        # data frames.

        temperature_run_results = {
            folder: {
                "coverage": self._read_and_trim_df(
                    os.path.join(data_directory, folder, "coverage.dat"), sep="\t"
                ),
                "derivative": self._read_and_trim_df(
                    os.path.join(data_directory, folder, "derivatives.dat"), sep="\t"
                ),
            }
            for folder in dirs_to_process
        }

        return temperature_run_results


# Utilities for parsing reactions (maybe make into a class later?)


def parse_atom_str(atom_str: str, compounds: dict):
    """
    Turn a MKMCXX string of reactants or products into a dictionary
    representation. Useful for reconstruction MKMCXX simulations from Python.

    Parameters
    ----------
    atom_str : str
        The string representing either the reactants or products of a reaction,
        in the form "a{A} + b{B} + ...", where a and b are integer
        stoichiometry coefficients and A and B are symbols of chemical species.
    compounds : dict
        A dictionary of the form {symbol: Compound(symbol), ...}, where symbol
        is the symbol for a chemical species found in atom_str and
        Compound(symbol) is the corresponding Compound object. The dictionary
        compounds must have entries for every species symbol that occurs in
        atom_str.

    Returns
    -------
    dict
        A dictionary of the form {Compound(symbol_A): stoich_A,
        Compound(symbol_B): stoich_B}, where Compound(symbol_A) is the Compound
        object representing species A, and stoich_A is the
        corresponding stoichiometric coefficient as read from atom_str.
        (Similarly for B).

    Raises
    ------
    RuntimeError
        Raises a RuntimeError if the atom_str is malformed or otherwise cannot
        be parsed.
    """
    # Parse reactant or product strings
    spec_list = {}
    for single_atom_str in atom_str:
        z = atom_parser.match(single_atom_str)
        if z:
            spec = z.groupdict()
            spec_list.update(
                {compounds[spec["symbol"]]: int(spec["coeff"]) if spec["coeff"] else 1}
            )
        else:
            raise RuntimeError("Could not parse atom symbol.")
    return spec_list


atom_parser = re.compile(r"(?P<coeff>\d+[ ]?)?\{(?P<symbol>.*?)\}")


def parse_rxn_stoichiometry(input_str: str, compounds: dict) -> dict:
    """
    Parse a reaction line from MKMCXX input. Creates an `ARReaction` or
    `HKReaction` object from a single line of input from the reactions section
    of a MKMCXX input or input log file.

    Parameters
    ----------
    input_str : str
        The input string representing the reaction in MKMCXX format. Should be
        of the format "rxn_type; rxn_string; <other parameters>; ..." where
        rxn_type is either "AR" or "HK", rxn_string is a string of the format
        "reactants_str => products_str" (where both reactants_str and
        products_str conform to the format of atom_str as defined in the
        `parse_atom_str` function), and other relevant parameters as defined in
        the MKMCXX manual for Arrhenius and Hertz-Knudsen reactions
    compounds : dict
        A dictionary of the form {symbol: Compound(symbol), ...}, where symbol
        is the symbol for a chemical species found in atom_str and
        Compound(symbol) is the corresponding Compound object. The dictionary
        compounds must have entries for every species symbol that occurs in
        atom_str.

    Returns
    -------
    dict
        A dictionary of the form {Compound(symbol_A): stoich_A,
        Compound(symbol_B): stoich_B}, where Compound(symbol_A) is the Compound
        object representing reactant species A, and stoich_A is the
        corresponding stoichiometric coefficient as read from atom_str.
        (Similarly for B).
    dict
        A dictionary of the form {Compound(symbol_A): stoich_A,
        Compound(symbol_B): stoich_B}, where Compound(symbol_A) is the Compound
        object representing product species A, and stoich_A is the
        corresponding stoichiometric coefficient as read from atom_str.
        (Similarly for B).
    """

    # Separate reactants and products
    reactant_str, product_str = input_str.split("=>")

    # Separate reactant and products into individual species
    reactant_atom_str = [s.strip() for s in reactant_str.split("+")]
    product_atom_str = [s.strip() for s in product_str.split("+")]

    # Parse reactant and product strings
    reactant_specs = parse_atom_str(reactant_atom_str, compounds)
    product_specs = parse_atom_str(product_atom_str, compounds)

    return reactant_specs, product_specs


def parse_rxn_string(entire_rxn_str: str, compounds: dict):
    """
    Parse a complete reaction string from an MKMCXX file into a `Reaction`
    object.

    Parameters
    ----------
    entire_rxn_str : str
        The formatted reaction string from the `&reactions` section of the
        input file, formatted as specified in the MKMCXX manual.
    compounds : dict
        A dictionary of the form {symbol: Compound(symbol), ...}, where symbol
        is the symbol for a chemical species found in atom_str and
        Compound(symbol) is the corresponding Compound object. The dictionary
        compounds must have entries for every species symbol that occurs in
        atom_str.

    Returns
    -------
    ARReaction or HKReaction
        The reaction object representing the supplied entire_rxn_string.

    Raises
    ------
    RuntimeError
        Raised if the reaction type is not either "AR" or "HK".
    """

    # Split up the reaction string by semicolon
    rxn_string_pieces = [s.strip() for s in entire_rxn_str.split(";")]

    # Parse the reactants and products
    reactant_dict, product_dict = parse_rxn_stoichiometry(
        rxn_string_pieces[1], compounds=compounds
    )

    # Create a AR or HK reaction based on the first key
    if rxn_string_pieces[0].lower() == "hk":
        # Detected a Hertz-Knudsen reaction. Read appropriate parameters
        args = {
            "m2": float(rxn_string_pieces[2]),
            "amu": float(rxn_string_pieces[3]),
            "K": float(rxn_string_pieces[4]),
            "sigma": float(rxn_string_pieces[5]),
            "sticking": float(rxn_string_pieces[6]),
            "jmol": float(rxn_string_pieces[7]),
        }

        # If a DRC parameter is specified, add it as well.
        try:
            do_drc = True if int(rxn_string_pieces[8]) == 1 else False
        except (IndexError, ValueError):
            do_drc = False

        args.update({"do_drc": do_drc})

        # Create the reaction
        return HKReaction(reactants=reactant_dict, products=product_dict, **args)

    elif rxn_string_pieces[0].lower() == "ar":
        # Detected an Arrhenius reaction. Read appropriate parameters
        args = {
            "vf": float(rxn_string_pieces[2]),
            "vb": float(rxn_string_pieces[3]),
            "Eaf": float(rxn_string_pieces[4]),
            "Eab": float(rxn_string_pieces[5]),
        }

        # If a DRC parameter is specified, add it as well.
        try:
            do_drc = True if int(rxn_string_pieces[6]) == 1 else False
        except (IndexError, ValueError):
            do_drc = False

        args.update({"do_drc": do_drc})

        # Create the reaction
        return ARReaction(reactants=reactant_dict, products=product_dict, **args)

    else:
        raise RuntimeError(
            f"Reaction type '{rxn_string_pieces[0]}' is not a valid type. "
            f"Ensure that the first field is either 'HK' or 'AR'."
        )

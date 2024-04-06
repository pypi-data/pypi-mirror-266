from fave_measurement_point.formants import FormantArray, Slice
from fave_measurement_point.processor import parse_expression
import yaml
from pathlib import Path

class Heuristic():
    """A measurement heuristic class

    Args:
        heuristic_path (Path | str, optional): 
            Path to the heurstic yaml file. Defaults to None.
        heuristic_dict (dict, optional): 
            A heuristic dictionary. Defaults to None.
    
    Attributes:
        heuristic (str): 
            The name of the measurement point
            heuristics
        default (str):
            The default landmark expression to use
        specifics (list[Specific]):
            A list of specific measurement point landmarks.
    """

    def __init__(
            self, 
            heuristic_path: Path | str = None, 
            heuristic_dict: dict = None
        ):
        if heuristic_path:
            self.heuristic_dict = self.read_heuristic(heuristic_path)
        elif heuristic_dict:
            self.heuristic_dict = heuristic_dict
        else:
            self.heuristic_dict = {
                "heuristic": "default",
                "default": {"prop_time" : "1/3"},
                "specifics": []
            }
        
        self.heuristic = self.heuristic_dict["heuristic"]
        self.default = self.heuristic_dict["default"]
        self.specifics = [
            Specific(specific)
            for specific in self.heuristic_dict["specifics"]
            ]

    def __repr__(self):
        out = f"{self.heuristic} measurement point heuristic. "\
              f"default: {self.default}; "\
              f"{len(self.specifics)} specifics."
        return out

    def apply_heuristic(
            self, 
            label:str, 
            formants: FormantArray
        ) -> Slice:
        """Applies the heuristic to a FormantArray, and
        returns the appropriate slice.

        Args:
            label (str):
                The label of the formant track. This is 
                matched against the labels in the specifics.
            formants (FormantArray):
                The formants to evaluate against.

        Returns:
            (Slice): The formant slice at the designated landmark
        """
        rules = [
            specific
            for specific in self.specifics
            if label == specific.label
        ]

        if len(rules) == 1:
            rule = rules[0].kwarg
            rule = {
                k: parse_expression(rule[k], formants)
                for k in rule
            }
            return formants.get_slice_at(**rule)
        
        rule = {k: parse_expression(self.default[k], formants) for k in self.default}
        return formants.get_slice_at(**rule)


    def read_heuristic(self, heuristic_path: Path | str):
        if type(heuristic_path) is str:
            heuristic_path = Path(heuristic_path)
        
        with heuristic_path.open('r') as f:
            heuristic_dict = yaml.safe_load(f)

        return heuristic_dict
    

class Specific():
    def __init__(self, specific: dict):
        """A specific measurement point heuristic

        Args:
            specific (dict):
                A dictionary with a label and a 
                measurement point landmark

        Attributes:
            label (str): 
                The label for the specific measurement pint
            kwarg (dict):
                The kwargs to be passed to FormantArray.get_slice_at()
        """
        self.label = specific["label"]
        self.kwarg = {
            k: specific[k]
            for k in specific
            if k != "label"
        }
    
    def __repr__(self):
        out = f"{self.label}: {self.kwarg}"
        return out
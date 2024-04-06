import numpy as np
from nptyping import NDArray

from dataclasses import dataclass, field

@dataclass
class Point():
    """A single point

    Args:
        value (float):
            Formant value
        time (float):
            Time of point
        rel_time (float):
            Relative time of point
        prop_time (float):
            Proportional time of point
        index (int):
            Index of point
    """
    value: float
    time: float
    rel_time: float
    prop_time: float
    index: int

@dataclass
class Slice():
    """A slice across formants

    Args:
        formants (np.array): 
            The formant values
        time (float):
            The time of the slice
        rel_time (float):
            The relative time of the slice
        prop_time (float):
            The proportional time of the slice
        index:
            The index of the slice
    
    Attributes:
        f[1,2,3,...] (float):
            Specific formant values at the slice.
    """
    formants: NDArray
    time: float
    rel_time: float
    prop_time: float
    index: int

    def __post_init__(self):
        for i in range(self.formants.size):
            this_point = Point(
                self.formants[i],
                self.time,
                self.rel_time,
                self.prop_time,
                self.index
            )
            setattr(self, f"f{i+1}", this_point)

@dataclass
class Formant():
    """A single formant
    Args:
        track (np.array):
            The formant track values
        time (np.array|None):
            The time domain of the formant track. Optional

    Attributes:
        time (np.array):
            The time domain.
        rel_time (np.array):
            The relative time of the formant
        prop_time (np.array):
            The proportional time of the formant
        shape (tuple):
            The shape of the formant
        max (Point):
            A Point for the formant maximum
        min (Point):
            A Point for the formant minimum
    """
    track: NDArray
    time: NDArray = field(default_factory=lambda x: np.array([]))

    def __post_init__(self):
        if self.time.size == 0:
            idx_time = np.arange(self.track.size)
            self.time = idx_time/idx_time.max()
        
        self.rel_time = self.time - self.time.min()
        self.prop_time = self.rel_time / self.rel_time.max()
    
    def __repr__(self):
       return f"Formant(min: {self.min.value:.0f}, max: {self.max.value:.0f}, dur: {self.rel_time.max():.3f})"
        
    @property
    def shape(self):
        return self.track.shape
    
    @property
    def max(self):
        max_idx = self.track.argmax()
        max_value = self.track[max_idx]
        max_time = self.time[max_idx]
        max_rel_time = self.rel_time[max_idx]
        max_prop_time = self.prop_time[max_idx]
        return Point(max_value, max_time, max_rel_time, max_prop_time, max_idx)
    
    @property
    def min(self):
        min_idx = self.track.argmin()
        min_value = self.track[min_idx]
        min_time = self.time[min_idx]
        min_rel_time = self.rel_time[min_idx]
        min_prop_time = self.prop_time[min_idx]
        return Point(min_value, min_time, min_rel_time, min_prop_time, min_idx)
    
@dataclass
class FormantArray():
    """A representation of multiple formant tracks

    Args:
        array (np.array):
            An array of formant tracks
        time (np.array|None):
            The time domain of the formant tracks. Optional.
    
    Attributes:
        rel_time:
            The relative time domain
        prop_time:
            The proportional time domain
        f[1, 2, 3, ...] (np.array):
            Specific formant tracks.

    """
    array: NDArray
    time: NDArray = field(default_factory=lambda x: np.array([]))

    def __post_init__(self):
        if self.time.size == 0:
            idx_time = np.arange(self.array.shape[1])
            self.time = idx_time/idx_time.max()
        
        assert self.time.size == self.array.shape[1], \
            "The number of formant samples should match "\
            "the number of time points"

        self.rel_time = self.time - self.time.min()
        self.prop_time = self.rel_time / self.rel_time.max()

        for i in range(self.array.shape[0]):
            setattr(
                self,
                f"f{i+1}",
                Formant(self.array[i,:], self.time)
            )

    def __repr__(self):
        out = ""
        for i in range(self.array.shape[0]):
            formant_name = f"f{i+1}"
            formant = getattr(self, formant_name)
            out += f"{formant_name} = {formant.__repr__()}; "
        return out


    def get_slice_at(
            self,
            time: float = None,
            rel_time: float = None,
            prop_time: float = None
    ) -> Slice:
        """Get a formant slice at some time point.

        One, and only one, of the time arguments 
        (`time`, `rel_time`, `prop_time`) must be specified.

        Args:
            time (float, optional): 
                The absolute time of the slice. Defaults to None.
            rel_time (float, optional): 
                The relative time of the slice. Defaults to None.
            prop_time (float, optional): 
                The proportional time of the slice. Defaults to None.

        Returns:
            (Slice):
                A formant slice at the specified time.
        """
        passed = [
            x is not None
            for x in [time, rel_time, prop_time]
        ]
        if not any(passed):
            raise ValueError("One time parameter must be defined.")
        
        defined = [x for x in passed if x]
        if len(defined) > 1:
            raise ValueError("Only one time parameter can be defined.")
        
        if time is not None:
            closest_idx = np.abs(self.time - time).argmin()
        
        if rel_time is not None:
            closest_idx = np.abs(self.rel_time - rel_time).argmin()
        
        if prop_time is not None:
            closest_idx = np.abs(self.prop_time - prop_time).argmin()
        
        return Slice(
            formants = self.array[:, closest_idx],
            time = self.time[closest_idx],
            rel_time = self.rel_time[closest_idx],
            prop_time = self.prop_time[closest_idx],
            index = closest_idx
        )
"""
Lissajous Animation Simulation

This module provides classes for simulating Lissajous curves and generating animations
based on various parameters and configurations.

Classes:
- GenericLissajou: Simulates a generic Lissajous curve animation.
- VaryingAmplitudeLissajou: Simulates a Lissajous curve with varying amplitude.
- SinusoidalAmplitudeLissajou: Simulates a Lissajous curve with a sinusoidal variation in amplitude.
- FixedRatioLissajou: Simulates a Lissajous curve with a fixed ratio of amplitudes.
- EllipticLissajou: Simulates a Lissajous ellipse animation.
- CircularLissajou: Simulates a Lissajous circle animation.

Usage:
Each class provides a method 'show()' to display the animation. Instantiate the desired
class object and call 'show()' to view the animation.

Example:
    # Simulate and display a Lissajous ellipse animation
    animation = EllipticLissajou()
    animation.show()
"""

import numpy as np

from .anim import ParametricAnimation


class GenericLissajou(ParametricAnimation):
    """
    A class for simulating Lissajous curves.

    Parameters:
        a (float): The parameter controlling the x-coordinate.
        b (float): The parameter controlling the y-coordinate.
        delta (float): The phase difference between the two sine functions.
        range (float): The range of the parameter 't' for the simulation. A higher range will put more points on each frame
        nb_points (int): The number of points to generate within the range.

    Usage:
        ```python
        # example 1
        animation = GenericLissajou()
        animation.show()
        # exmple2: change lissajou parameters
        animation = GenericLissajou(a=3, b=2, delta=np.pi / 2)
        # example2: change the visualization params
        animation = GenericLissajou(
            a=1, b=2, delta=np.pi / 2, range=50, nb_points=100000
        )
        animation.max_frames = 10000
        animation.show()
        ```
    """

    def __init__(self, a=5, b=4, delta=np.pi / 2, range=20, nb_points=10000):
        super().__init__()
        self.a = a
        self.b = b
        self.delta = delta
        self.t2 = np.linspace(0, range, nb_points)

    def _before_each_iteration(self, t):
        self.a += 1 / 1000
        pass

    def _fx(self, t):
        return np.sin(self.a * self.t2 + self.delta)

    def _fy(self, t):
        return np.sin(self.b * self.t2)


class VaryingAmplitudeLissajou(GenericLissajou):
    """
    A class for simulating Lissajous curves with varying ratios and sinusoidal 'b'.

    Usage:
        animation = VaryingAmplitudeLissajou()
        animation.show()

    Note:
        - The parameter 'a' is fixed.
        - The parameter 'delta' is fixed at pi/2.
        - The parameter 'b' follows a sinusoidal function, resulting in dancing curves.
    """

    def _before_each_iteration(self, t):
        self.a = 3
        self.delta = np.pi / 2
        self.b = np.cos(t / 100) * self.a

    def _set_params(self, **kwargs):
        kwargs["speed"] = kwargs.get("speed") or 1000 / 3
        super()._set_params(**kwargs)


class SinusoidalAmplitudeLissajou(GenericLissajou):
    """
    A class for simulating Lissajous curves with a constant sinusoidal effect on 'b'.

    Usage:
        animation = SinusoidalAmplitudeLissajou()
        animation.show()

    Note:
        - The parameter 'a' is fixed.
        - The parameter 'delta' is fixed at pi/2.
        - The parameter 'b' varies with cosine of time for interesting effects.
    """

    def _before_each_iteration(self, t):
        self.a = 3
        self.delta = np.pi / 2
        self.b = np.cos(t / 500) * self.a

    def _set_params(self, **kwargs):
        kwargs["max_frames"] = kwargs.get("max_frames") or 1555
        super()._set_params(**kwargs)


class FixedRatioLissajou(GenericLissajou):
    """
    A class for simulating closed Lissajous curves with fixed ratio 'b/a'.

    Parameters:
        a (float): The parameter controlling the x-coordinate.
        delta (float): The phase difference between the two sine functions.
        range (float): The range of the parameter 't' for the simulation.
        nb_points (int): The number of points to generate within the range.
        ratio (float): The fixed ratio between 'b' and 'a'.

    Usage:
        animation = FixedRatioLissajou()
        animation.show()

    Note:
        - The ratio 'b/a' is kept constant to produce closed curves.
    """

    def __init__(self, a=5, delta=np.pi / 10, range=20, nb_points=10000, ratio=5):
        super().__init__(a=a, b=None, delta=delta, range=range, nb_points=nb_points)
        self.ratio = ratio

    def _before_each_iteration(self, t):
        self.a += 1 / 1000
        self.b = self.ratio * self.a


class EllipticLissajou(FixedRatioLissajou):
    """
    A class for simulating Lissajous ellipses.

    Usage:
        animation = EllipticLissajou()
        animation.show()

    Note:
        - The ratio 'b/a' is kept constant to produce ellipses.
    """

    def __init__(self, a=5, delta=np.pi / 10, range=20, nb_points=10000):
        ratio = 1
        super().__init__(a, delta, range, nb_points, ratio=ratio)


class CircularLissajou(EllipticLissajou):
    """
    A class for simulating Lissajous circles.

    Usage:
        animation = CircularLissajou()
        animation.show()

    Note:
        - The ratio 'b/a' is kept constant to produce circles.
        - The phase difference 'delta' is set to pi/2 to produce circles.
    """

    def __init__(self, a=5, range=20, nb_points=10000):
        delta = np.pi / 2
        super().__init__(a, delta=delta, range=range, nb_points=nb_points)


if __name__ == "__main__":
    liss = SinusoidalAmplitudeLissajou()
    liss.show()

# [Lissajou Animation Framework](https://github.com/Hermann-web/lissajou)

## Description

The Lissajou Animation Framework is a Python module designed for creating diverse animations using matplotlib. It offers a structured approach to building animations, including parametric animations and 3D parametric animations. While the module includes demonstrations of [Lissajou curves](https://en.wikipedia.org/wiki/Lissajous_curve), its primary focus is on providing a framework for general animation creation.

## Installation

You can install the Lissajou Animation Framework using pip:

```bash
pip install lissajou
```

## Usage

To create animations using the framework, you can utilize the provided classes and methods. Here's a basic example to get you started:

```python
from lissajou.anim import GenericLissajou

# Create a GenericLissajou object
animation = GenericLissajou()
animation.show()
```

## Classes and Features

The framework includes the following main classes:

- `BaseAnimation`: An abstract base class for creating animations with setup steps and frame updates.
- `ImageAnimation`: A subclass of `BaseAnimation` for creating animations with image data.
- `ParametricAnimation`: A subclass of `BaseAnimation` for creating parametric 2D animations.
- `ThreeDimensionalParametricAnimation`: A subclass of `ParametricAnimation` for creating parametric 3D animations.

## Showcase

Some Lissajou patterns support have been added to the module. You will find implementations of these animations in the module `lissajou.lissajou` so you can import them, and use with your custom parameters.

For example

```python
from lissajou.lissajou import SinusoidalAmplitudeLissajou
liss = SinusoidalAmplitudeLissajou(a=6, delta=np.pi / 6, range=18, nb_points=18000)
liss.show()
```

Here are some examples showcasing different types of Lissajou animations:

- Generic Lissajou Curve
- Lissajou Curve with Varying Amplitude
- Lissajou Curve with Sinusoidal Amplitude
- Lissajou Curve with Fixed Ratio
- Lissajou Ellipse Animation
- Lissajou Circle Animation

Usage examples an be tested in the file [examples/lissajou_examples.py](./examples/lissajou_examples.py)

## Custom Animation Examples

The framework allows for creating custom animations beyond the included examples. Here are some demonstrations:

### Image Animation

This example demonstrates creating an animation with image data.

```python
class ImageAnimationExample(ImageAnimation):
    """
    A subclass of ImageAnimation for creating animations with sinusoidal image data.

    This class generates sinusoidal image data and updates the animation view with
    the computed sine values for each frame.
    """

    def __init__(self, n):
        """
        Initializes the SinusoidalImageAnimation object with sinusoidal image data.
        """
        self.x = np.random.binomial(1, 0.3, size=(n, n))  # Generate random binary image
        super().__init__()  # Call the superclass constructor to set up the animation

    def _set_params(self, **kwargs):
        """
        Sets the parameters for the animation, including the shape of the image.
        """
        kwargs["shape"] = (
            self.x.shape
        )  # Set the shape parameter based on the generated image
        return super()._set_params(
            **kwargs
        )  # Call the superclass method to set parameters

    def _before_each_iteration(self, t):
        """
        Hook method called before each frame iteration.
        """
        pass  # No pre-iteration setup is needed for this subclass

    def _img_fct(self, t):
        """
        Computes the image values for each frame using sine function.
        """
        return np.sin(t * self.x)  # Compute sine values for the current frame


if __name__ == "__main__":
    print("Example 1: ImageAnimationExample")
    liss = ImageAnimationExample(100)
    liss.show()
```

### 3D Sinusoidal Parametric Animation

This example demonstrates creating a 2D or 3D animation using parametric equations with sine functions.

```python

class ThreeDsinusoidalParametricAnimation(ThreeDimensionalParametricAnimation):
    """
    A subclass of ThreeDimensionalParametricAnimation for creating 3D sinusoidal parametric animations.

    This class generates parametric data for x, y, and z coordinates using sinusoidal functions.
    """

    def __init__(self, n):
        """
        Initializes the ThreeDsinusoidalParametricAnimation object.
        """
        self.n = n
        super().__init__()  # Call the superclass constructor to set up the animation

    def _before_each_iteration(self, t):
        """
        Hook method called before each frame iteration.
        """
        self.tx = np.linspace(-np.pi, np.pi, self.n)  # Generate x values for each frame

    def _fx(self, t):
        """
        Computes the x-coordinate values for each frame using a sinusoidal function.
        """
        return np.sin(t * self.tx)  # Generate x values based on the sine of tx

    def _fy(self, t):
        """
        Computes the y-coordinate values for each frame using a sinusoidal function.
        """
        return np.cos(t * self.tx)  # Generate y values based on the cosine of tx

    def _fz(self, t):
        """
        Computes the z-coordinate values for each frame using a hyperbolic tangent function.
        """
        return np.tanh(
            t * self.tx
        )  # Generate z values based on the hyperbolic tangent of tx

if __name__ == "__main__":
    print("Example 2: ThreeDsinusoidalParametricAnimation")
    liss = ThreeDsinusoidalParametricAnimation(100)
    liss.show(x_range=(-1, 1), y_range=(-1, 1), z_range=(-1, 1))
```

You can also implement a 2D animation in a similar fashion, by using the `ParametricAnimation` abstract class.

These are just a few examples of how to create custom animations using the Lissajou Animation Framework. Feel free to explore the provided classes and experiment with your own animation ideas!

## Contributing

If you wish to contribute to the Lissajou Animation Framework, feel free to report issues or submit pull requests on the project's repository.

## License

This project is distributed under the MIT License.

This updated README now includes explanations and code examples for custom animation implementations, allowing users to explore the framework's capabilities further.

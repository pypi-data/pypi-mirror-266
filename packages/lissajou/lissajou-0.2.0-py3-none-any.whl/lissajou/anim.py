"""
File: animation_framework.py
Author: Hermann Agossou

Description:
    This file contains a framework for creating animations using matplotlib.
    It defines abstract base classes and subclasses for creating various types
    of animations, including parametric animations and 3D parametric animations.
"""

from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class BaseAnimation(metaclass=ABCMeta):
    """
    An abstract base class designed to simplify the creation of animations using matplotlib.

    This class defines a framework for creating animations by specifying setup steps,
    frame updates, and parameters. Subclasses should provide implementations for abstract
    methods to define specific animation behaviors.
    """

    max_frames = 100  # Default maximum number of frames
    speed = 1000 / 30  # Default frame interval in milliseconds (33.33ms for 30 FPS)

    def __init__(self):
        """
        Constructor for the BaseAnimation class.
        """
        pass  # Currently, there's no initialization required. Can be extended by subclasses.

    def setup(self, **kwargs):
        """
        Sets up the animation with specified parameters.

        This method initializes the animation by configuring parameters, setting up the figure and axes,
        and initializing the animation itself.

        Keyword Args:
            **kwargs: Arbitrary keyword arguments for animation parameters.
        """
        return self.__setup__(**kwargs)

    def __setup__(self, **kwargs):
        """
        Private method for initial setup of the animation. It configures parameters,
        sets up the figure and axes, and initializes the animation.

        Keyword Args:
            **kwargs: Arbitrary keyword arguments for animation parameters.
        """
        if hasattr(self, "anim") and self.anim is not None:
            return
        self._set_params(**kwargs)  # Set any provided parameters
        fig, self.ax = self.__set_axes__()  # Setup figure and axes
        self._before_all_iterations()  # Perform any setup before animation starts
        self.__animate__(t=0)  # Initialize the animation with the first frame
        # Create the animation object using FuncAnimation
        self.anim = FuncAnimation(
            fig,
            self.__animate__,
            frames=self.max_frames,
            interval=self.speed,
            blit=True,
        )

    def show(self, **kwargs):
        """
        Sets up the animation and displays it.

        Accepts various keyword arguments to customize animation parameters before display.
        """
        self.__setup__(**kwargs)  # Perform initial setup with any provided parameters
        plt.show()  # Display the animation

    def save(self, file_path: Union[str, Path], **kwargs):
        """
        Saves the animation to a file based on the file extension.

        Args:
            file_path (str): The path where the animation will be saved.
            **kwargs: Additional keyword arguments passed to the animation writer.

        Supported file formats:
            - Images: png, jpeg, jpg, tiff
            - Animated Images: gif
            - HTML: html, htm
            - Video: mp4

        For formats requiring external dependencies (e.g., ffmpeg), ensure the corresponding
        dependencies are installed in the system.

        If the specified format is unsupported, the function attempts to save the animation
        using the specified format anyway.

        Note: Some formats may require specific writers (e.g., 'pillow' for GIFs, 'ffmpeg' for videos).
        If a writer is not explicitly provided, default writers are used based on the file extension.

        Examples:
            anim.save('animation.mp4')  # Save as MP4 video with default parameters.
            anim.save('animation.gif', writer='pillow', fps=20)  # Save as GIF with custom parameters.
        """
        img_formats = ("png", "jpeg", "jpg", "tiff")
        animated_image_formats = ("gif",)
        video_formats = ("mp4",)
        html_formats = ("html", "htm")
        supported_formats = (
            img_formats + animated_image_formats + video_formats + html_formats
        )

        frame_formats = img_formats

        # Use pathlib to infer file format from the file extension
        file_path = Path(file_path)
        format = file_path.suffix[1:].lower()  # Remove the dot from the extension

        # Ensure directory exists if saving frame formats
        if format in frame_formats:
            file_path.parent.mkdir(exist_ok=True)
        else:
            assert file_path.parent.exists()
            file_path = file_path.absolute()
        file_path = str(file_path)

        # Perform initial setup with any provided parameters
        self.__setup__()

        # Save the animation based on the specified format
        if format in img_formats:
            # Save as image using imagemagick writer
            self.anim.save(
                file_path, writer=kwargs.pop("writer", "imagemagick"), **kwargs
            )
        elif format in animated_image_formats:
            # Save as GIF using pillow writer
            self.anim.save(
                file_path,
                writer=kwargs.pop("writer", "pillow"),
                fps=kwargs.pop("fps", 30),
                **kwargs,
            )
        elif format in video_formats:
            # Save as video using ffmpeg writer
            self.anim.save(
                file_path,
                writer=kwargs.pop("writer", "ffmpeg"),
                fps=kwargs.pop("fps", 30),
                **kwargs,
            )
        elif format in html_formats:
            # Save as HTML using html writer
            self.anim.save(file_path, writer=kwargs.pop("writer", "html"), **kwargs)
        else:
            # Unsupported format, attempt to save anyway
            print(
                f"Unsupported format={format}. Supported formats: {', '.join(supported_formats)}. Trying to save anyway"
            )
            self.anim.save(file_path, writer=kwargs.pop("writer"), **kwargs)

        print(f"Saved animation to {file_path}")

    @abstractmethod
    def _set_params(self, max_frames: int = None, speed: float = None):
        """
        Abstract method for setting animation parameters.

        Subclasses should implement this method to update animation-specific parameters.

        Args:
            max_frames (int, optional): The maximum number of frames for the animation.
            speed (float, optional): The time interval between frames in milliseconds.
        """
        if max_frames is not None:
            self.max_frames = max_frames
        if speed is not None:
            self.speed = speed

    @abstractmethod
    def __set_axes__(self):
        """
        Abstract method for setting up the axes of the figure.

        Subclasses must implement this method to define the axes setup.

        Returns:
            A tuple containing the figure and axes objects.
        """
        pass

    def _before_all_iterations(self):
        """
        Hook method called before the animation starts.

        Subclasses can override this method to perform any necessary setup before
        the animation iterations begin. By default, this method does nothing.
        """
        pass

    def __animate__(self, t):
        """
        Private method to update the animation at each frame.

        Args:
            t (int): The current frame number.

        Returns:
            A tuple containing the elements to update for the current frame.
        """
        print(f"\rt={t:^3}/{self.max_frames}", end="\r")  # Progress output
        self._before_each_iteration(t)  # Hook for tasks before each frame is processed
        # Initialize or update view data depending on whether it's the first frame
        if self.__is_first_it__(t):
            self.view = self.__initialize_view_data__(t, self.ax)
        else:
            self.view = self.__reset_view_data__(t, self.view)
        return (self.view,)

    @abstractmethod
    def _before_each_iteration(self, t):
        """
        Abstract method called before each frame is processed.

        Args:
            t (int): The current frame number.
        """
        pass  # Implementation required in subclass for per-frame setup or updates

    def __is_first_it__(self, t):
        """
        Check if the current frame is the first one.

        Args:
            t (int): The current frame number.

        Returns:
            bool: True if this is the first frame, False otherwise.
        """
        if hasattr(self, "_is_first_iteration"):
            return False
        self._is_first_iteration = True
        return True

    @abstractmethod
    def __initialize_view_data__(self, t, ax):
        """
        Abstract method to initialize the view data for the first frame of the animation.

        Args:
            t (int): The current frame number.
            ax (matplotlib.axes.Axes): The axes object for the animation.

        Returns:
            Initial view data for the animation. This can be matplotlib artists or any data structure
            that represents the initial state of the animated elements.
        """
        pass  # Must be implemented in subclass to define how to initialize the animation's view

    @abstractmethod
    def __reset_view_data__(self, t, view):
        """
        Abstract method to update the view data for each subsequent frame after the first.

        This method should update the state of the animated elements based on the current frame number.

        Args:
            t (int): The current frame number.
            view: The view data from the previous frame, to be updated for the current frame.

        Returns:
            Updated view data for the current frame. This is typically the same object(s) as `view`,
            but updated to reflect the new frame's state.
        """
        pass  # Must be implemented in subclass to define how to update the view for each frame


class ImageAnimation(BaseAnimation):
    """
    A subclass of BaseAnimation designed for creating animations with image data.

    This class initializes animation view data with random binary images and allows for
    updating the view data using a custom image function '_img_fct' for each frame.
    """

    width: int = None  # Width of the image
    height: int = None  # Height of the image

    def _set_params(self, shape: Tuple[int], **kwargs):
        """
        Sets the parameters for the animation, including the shape of the image.

        Args:
            shape (Tuple[int]): The shape (height, width) of the image.
        """
        super()._set_params(
            **kwargs
        )  # Call the base class method to handle common parameters
        assert shape is not None, "shape not set"
        assert np.asarray(shape).shape == (2,)  # Ensure shape is a two-element tuple
        self.height, self.width = shape
        assert isinstance(self.height, int) and isinstance(self.width, int)

    def __set_axes__(self):
        """
        Sets up the figure and axes for the animation.

        Returns:
            A tuple (fig, ax) with the matplotlib figure and axes objects.
        """
        fig, ax = plt.subplots()
        return fig, ax

    def __initialize_view_data__(self, t, ax):
        """
        Initializes the view data for the animation with random binary images.

        Args:
            t (int): The current frame number (not used in this method).
            ax (matplotlib.axes.Axes): The axes object for the animation.

        Returns:
            The initial view data for the animation, represented as an image.
        """
        # Generate a random binary image with the specified shape
        x = np.random.binomial(1, 0.3, size=(self.height, self.width))
        view = ax.imshow(x, cmap=plt.cm.gray)  # Display the image on the axes
        return view

    def __reset_view_data__(self, t, view):
        """
        Updates the view data for each frame of the animation with computed image values.

        Args:
            t (int): The current frame number.
            view: The view data from the previous frame (image object).

        Returns:
            The updated view data for the current frame.
        """
        view.set_array(self.__get_img_vals__(t))  # Update the image array
        return view

    def __get_img_vals__(self, t) -> np.ndarray:
        """
        Computes the image values for the current frame using a custom image function.

        Args:
            t (int): The current frame number.

        Returns:
            Computed image values as a NumPy array.
        """
        im = self._img_fct(t=t)  # Call the custom image function to get image values
        assert isinstance(im, np.ndarray)
        assert im.shape == (
            self.height,
            self.width,
        )  # Ensure image shape matches specified shape
        return im

    @abstractmethod
    def _img_fct(self, t) -> np.ndarray:
        """
        Abstract method to compute image values for each frame of the animation.

        Args:
            t (int): The current frame number.

        Returns:
            Computed image values as a NumPy array.
        """
        pass  # Must be implemented in subclass to define how image values are computed


class ParametricAnimation(BaseAnimation, metaclass=ABCMeta):
    """
    A subclass of BaseAnimation designed for creating parametric animations.

    This class introduces x and y ranges for the plot and requires the definition
    of parametric functions `_fx` and `_fy` to compute the x and y coordinates of
    the plot for each frame based on a parameter `t`.
    """

    x_range = None  # Optional x-axis range for the plot
    y_range = None  # Optional y-axis range for the plot

    def _set_params(
        self,
        x_range: Union[np.ndarray, List[float]] = None,
        y_range: Union[np.ndarray, List[float]] = None,
        **kwargs,
    ):
        """
        Sets the parameters for the animation, including the x and y ranges.

        Args:
            x_range (Union[np.ndarray, List[float]], optional): The range of the x-axis as [min, max].
            y_range (Union[np.ndarray, List[float]], optional): The range of the y-axis as [min, max].
        """
        super()._set_params(
            **kwargs
        )  # Call the base class method to handle common parameters
        if x_range is not None:
            assert np.asarray(x_range).shape == (
                2,
            )  # Ensure x_range is a two-element structure
            self.x_range = x_range
        if y_range is not None:
            assert np.asarray(y_range).shape == (
                2,
            )  # Ensure y_range is a two-element structure
            self.y_range = y_range

    def __set_axes__(self):
        """
        Sets up the figure and axes for the animation with optional x and y ranges.

        Returns:
            A tuple (fig, ax) with the matplotlib figure and axes objects.
        """
        fig, ax = plt.subplots()
        if self.x_range is not None:
            ax.set_xlim(self.x_range)  # Set the x-axis range if specified
        if self.y_range is not None:
            ax.set_ylim(self.y_range)  # Set the y-axis range if specified
        return fig, ax

    def __initialize_view_data__(self, t, ax):
        """
        Initializes the view data for the animation based on the parametric functions.

        Args:
            t (int): The current frame number.
            ax (matplotlib.axes.Axes): The axes object for the animation.

        Returns:
            The initial view data for the animation.
        """
        # Plot the initial data points based on the parametric functions
        (view,) = ax.plot(self._fx(t), self._fy(t))
        return view

    def __reset_view_data__(self, t, view):
        """
        Updates the view data for each frame.

        Args:
            t (int): The current frame number.
            view: The view data from the previous frame.

        Returns:
            The updated view data for the current frame.
        """
        # Update the data points for the current frame
        view.set_xdata(self._fx(t))
        view.set_ydata(self._fy(t))
        return view

    @abstractmethod
    def _fx(self, t):
        """
        Abstract method to compute the x-coordinate based on the parameter t.

        Args:
            t (int): The current frame number or time parameter.

        Returns:
            The x-coordinate for the plot at time t.
        """
        pass  # Must be implemented in subclass

    @abstractmethod
    def _fy(self, t):
        """
        Abstract method to compute the y-coordinate based on the parameter t.

        Args:
            t (int): The current frame number or time parameter.

        Returns:
            The y-coordinate for the plot at time t.
        """
        pass  # Must be implemented in subclass


class ThreeDimensionalParametricAnimation(ParametricAnimation, metaclass=ABCMeta):
    """
    A subclass of ParametricAnimation for creating 3D parametric animations.

    This class adds a third dimension to the animations, allowing for the creation of
    dynamic 3D visualizations. It introduces a z-axis range and requires the definition
    of a function `_fz` to compute the z-coordinate for each frame.
    """

    z_range = None  # Optional z-axis range for the plot

    def _set_params(self, z_range: Union[np.ndarray, List[float]] = None, **kwargs):
        """
        Sets the parameters for the animation, including the z range, in addition to
        the base class parameters.

        Args:
            z_range (Union[np.ndarray, List[float]], optional): The range of the z-axis as [min, max].
        """
        super()._set_params(
            **kwargs
        )  # Call the superclass method to handle x_range, y_range, and other params
        if z_range is not None:
            assert np.asarray(z_range).shape == (
                2,
            )  # Ensure z_range is a two-element structure
            self.z_range = z_range

    def __set_axes__(self):
        """
        Sets up the figure and axes for the 3D animation with optional x, y, and z ranges.

        Returns:
            A tuple (fig, ax) with the matplotlib figure and 3D axes objects.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")  # Create a 3D subplot
        if self.x_range is not None:
            ax.set_xlim(self.x_range)  # Set the x-axis range if specified
        if self.y_range is not None:
            ax.set_ylim(self.y_range)  # Set the y-axis range if specified
        if self.z_range is not None:
            ax.set_zlim(self.z_range)  # Set the z-axis range if specified
        return fig, ax

    def __initialize_view_data__(self, t, ax):
        """
        Initializes the view data for the 3D animation based on the parametric functions.

        Args:
            t (int): The current frame number.
            ax (matplotlib.axes._subplots.Axes3DSubplot): The 3D axes object for the animation.


        Returns:
            The initial view data for the 3D animation.
        """
        # Plot the initial data points based on the parametric functions
        (view,) = ax.plot(self._fx(t), self._fy(t), self._fz(t))
        return view

    def __reset_view_data__(self, t, view):
        """
        Updates the view data for each frame of the 3D animation.

        Args:
            t (int): The current frame number.
            view: The view data from the previous frame.

        Returns:
            The updated view data for the current frame.
        """
        # Update the data points for the current frame
        view.set_xdata(self._fx(t))
        view.set_ydata(self._fy(t))
        view.set_3d_properties(self._fz(t))  # Set the z-coordinate
        return view

    @abstractmethod
    def _fz(self, t):
        """
        Abstract method to compute the z-coordinate based on the parameter t.

        Args:
            t (int): The current frame number or time parameter.

        Returns:
            The z-coordinate for the plot at time t.
        """
        pass  # Must be implemented in subclass

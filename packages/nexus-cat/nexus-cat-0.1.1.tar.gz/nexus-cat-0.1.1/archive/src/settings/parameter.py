class Parameter:
    """
    The Parameter class represents a parameter with a name and a value.

    Attributes:
    - name: Name of the parameter.
    - value: Value associated with the parameter.

    Methods:
    - __init__(self, name, value): Initializes a Parameter object with a name and value.
    - get_name(self): Returns the name of the parameter.
    - get_value(self): Returns the value associated with the parameter.
    - set_value(self, new_value): Sets a new value for the parameter.
    """

    def __init__(self, name, value):
        """
        Initializes a Parameter object with a name and value.

        Parameters:
        - name: Name of the parameter.
        - value: Value associated with the parameter.
        """
        self.name = name
        self.value = value

    def get_name(self):
        """Returns the name of the parameter."""
        return self.name

    def get_value(self):
        """Returns the value associated with the parameter."""
        return self.value

    def set_value(self, new_value):
        """
        Sets a new value for the parameter.

        Parameters:
        - new_value: The new value to be set for the parameter.
        """
        self.value = new_value

import json

from clstr.src.settings.parameter import Parameter


class ParameterFileReader:
    """
    The ParameterFileReader class reads a JSON parameter file and creates Parameter objects.

    Attributes:
    - file_path: The file path of the parameter file to be read.

    Methods:
    - __init__(self, file_path): Initializes a ParameterFileReader instance with the specified file path.
    - read_file(self): Reads the content of the parameter file.
    - create_parameters(self): Creates Parameter objects from the content of the parameter file.
    """

    def __init__(self, file_path):
        """
        Initializes a ParameterFileReader object with the specified file path.

        Parameters:
        - file_path: The file path of the parameter file to be read.
        """
        self.file_path = file_path

    def read_file(self):
        """
        Reads the content of the parameter file.

        Returns:
        - content: The content of the parameter file.
        """
        try:
            with open(self.file_path, "r") as file:
                content = json.load(file)
            return content
        except FileNotFoundError:
            print("File not found or unable to read the file.")
            return None

    def create_parameters(self):
        """
        Creates Parameter objects from the content of the parameter file.

        Returns:
        - parameters: List of Parameter objects created from the file content.
        """
        content = self.read_file()
        if content is not None:
            parameters = []
            for name, value in content.items():
                parameter = Parameter(name, value)
                parameters.append(parameter)
            return parameters
        else:
            print(
                "Failed to create parameters. Please check the file path or file content."
            )
            return None

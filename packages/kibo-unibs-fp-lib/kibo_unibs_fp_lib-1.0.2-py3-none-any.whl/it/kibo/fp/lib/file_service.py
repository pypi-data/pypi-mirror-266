"""Module representing the file_service class"""

# Standard Libraries
import pickle

# Internal Libraries
from it.kibo.fp.lib.ansi_colors import ansi_colors


class FileService:
    """
    This class has useful methods to serialize/deserialize objects and save/load them to/from a 
    file.
    """

    _RED_ATTENTION = f"{ansi_colors["red"]}Attention!{ansi_colors["reset"]}"
    _FILE_NOT_FOUND_ERROR = f"{_RED_ATTENTION}\nCan't find the file "
    _READING_ERROR = f"{_RED_ATTENTION}\nProblem reading the file "
    _WRITING_ERROR = f"{_RED_ATTENTION}\nProblem writing the file "

    def __init__(self) -> None:
        """Prevents instantiation of this class

        Raises:
            NotImplementedError
        """

        raise NotImplementedError()

    @staticmethod
    def serialize_object(file_path: str, to_save: object) -> None:
        """Serialize whatever object is given.

        Params:
            file_path -> The file path where to save the serialized object.

            to_save -> The object to serialize and save.
        """

        try:
            with open(file_path, "wb") as f:
                pickle.dump(to_save, f)
        except IOError as e:
            print(FileService._WRITING_ERROR + file_path)
            print(e)

    @staticmethod
    def deserialize_object(file_path: str, object_class: type) -> object:
        """Deserialize whatever object is saved in the given file. The deserialized file will be 
        cast into the given class.

        Params:
            file_path -> The file path where to find the serialized object.
            
            object_class -> The class to cast the serialized object into.

        Returns:
            An instance of the deserialized object.
        """

        try:
            with open(file_path, "rb") as f:
                read = pickle.load(f)
        except FileNotFoundError:
            print(FileService._FILE_NOT_FOUND_ERROR + file_path)
        except (IOError, pickle.UnpicklingError) as e:
            print(FileService._READING_ERROR + file_path)
            print(e)

        return object_class(read) if read else None

import os
import platform
from pathlib import Path


class PathUtil:
        
    @staticmethod
    def get_prj_root_path() -> str:
        return os.path.dirname(Path(__file__).parent.parent.parent)

    @staticmethod
    def join_prj_root_path(path: str) -> str:
        def __convert_to_window_format() -> str:
            return path.replace('/', '\\') if platform.system() not in ('Darwin', 'Linux') else path
        return os.path.join(PathUtil.get_prj_root_path(), __convert_to_window_format())

    @staticmethod
    def is_path_correct(path: str) -> bool:
        return os.path.exists(path)
    
    @staticmethod
    def get_full_prj_path() -> str:
        """This is extend from the get_prj_root_path 
        Since it only return the root of this project so when ipmorting to other project it can't be completed.
        Which mean get_prj_root_path will be used as internal func for core amd this func will help to return to 1 more level up to use as external lib.

        Returns:
            str: path
        """
        return os.path.dirname(Path(__file__).parent.parent.parent.parent)
    
    @staticmethod
    def join_full_prj_root_path(path: str) -> str:
        def __convert_to_window_format() -> str:
            return path.replace('/', '\\') if platform.system() not in ('Darwin', 'Linux') else path
        return os.path.join(PathUtil.get_full_prj_path(), __convert_to_window_format())
    

import os 
from abc import ABC, abstractmethod
import multiprocessing as mp
abs_path = os.path.abspath\
    (os.path.join(os.path.dirname(__file__), ".."))


class AppInterface(ABC):
    """ Interface for application """

    @abstractmethod
    def set_queue_data(self, queue:mp.Queue) -> None:
        """ Set queue for data medium between threads """
        pass 

    @abstractmethod
    def run(self) -> None:
        """ Run the main of application 
            in infinite loop.
        """
        pass 

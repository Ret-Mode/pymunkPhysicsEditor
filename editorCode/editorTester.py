import subprocess
import sys

class Tester:

    _instance: "Tester" = None

    @staticmethod
    def getInstance() -> "Tester":
        if Tester._instance == None:
            Tester._instance = Tester()
        return Tester._instance


    def __init__(self):
        pass

    def execute(self, testedObjectPath:str):
        subprocess.run([sys.executable, testedObjectPath])
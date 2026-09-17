from PyNite import FEModel3D
import csv

def calc_shear_modulus(nu:float, E:float) -> float:
    """
    Returns the shear modulus calculated from 'nu' and 'E'
    """
    G = E / (2 * (1+nu))
    return G

#Reading data from the text file
def read_beam_file(filename: str) -> list[list[str]]:
    
    """
    Returna a list of list of strings representing the text data in the file at
    'filename'
    """
    csv_acc = [] # File data goes here
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            csv_acc.append(line)
            
    return csv_acc
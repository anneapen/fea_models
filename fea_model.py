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

#Converting the string to float type
def str_to_float(s:str) -> float|str:
    """
    Converts a string(or a list of strings) to float type.
    if the string passed to the function cannot be converted into a float, then the original string is returned instead.
    """
    try:
        return float(s)
    except ValueError:
        return s

def convert_to_numeric(file_data:list[list[str]])->list[list[float]]:
    """
    Converts all of the numeric data into numbers
    """
    
    numeric_data_final=[]
    
    for data in file_data:
        numeric_data=[]
        for line in data:
            a = str_to_float(line.replace(","," "))
            numeric_data.append(a)
        numeric_data_final.append(numeric_data)

    return numeric_data_final
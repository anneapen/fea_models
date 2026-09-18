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

#Parsing the support details from the data
def parse_supports(data:list[str])->dict[float,str]:
    """
    Returns a list of suppport details into a dictionary with support locations as keys and support types
    as values where support types can be P(pinned),R(roller) or F(fixed)
    """
    acc={}
    for item in data:
        loc,support = item.split(":")
        acc.update({str_to_float(loc):support})
    return acc

#Parsing the load details from the data
def parse_loads(data:list[list[str|float]])->list[dict]:

    """
    Returns the load data in a structured form as list of dicts
    """
    acc=[]
    for item in data:
        type, dirn = item[0].split(":")
        case = item[-1].split(":")[-1]
        if type == "POINT":
            mag=item[1]
            loc=item[2]
            acc.append({"Type": type.title(),
                    "Direction": dirn.title(),
                    "Magnitude": mag,
                    "Location": loc,
                    "Case": case})
            
        elif type == "DIST":
            start_mag=item[1]
            end_mag=item[2]
            start_loc=item[3]
            end_loc=item[4]
            acc.append({"Type": type.title(),
                    "Direction": dirn.title(),
                    "Start Magnitude": start_mag,
                    "End Magnitude": end_mag,
                    "Start Location": start_loc,
                    "End Location": end_loc,
                    "Case": case})
            
    return acc  

#Parsing the beam details from the data
def parse_beam_attributes(data:list[float])->dict[str,float]:
    """
    Returns the list of length and section/material properties of the beam into
    a dictionary which includes L,E,Iz,Iy,A,J,nu,rho
    """
    
    attributes=['L','E','Iz','Iy','A','J','nu','rho']
    acc={}
    for idx,attr in enumerate(attributes):
        try:
            acc.update({attr:data[idx]})
        except IndexError:
            acc.update({attr:1.0})
    return acc

def get_structured_beam_data(raw_data: list[list[str]]) -> dict:
    """
    Returns a dictionary that has string keys describing the attributes of a beam for analysis.
    """
    numeric_beam_data = convert_to_numeric(raw_data)
    beam_name = raw_data[0][0]
    beam_attributes = parse_beam_attributes(numeric_beam_data[1])
    supports = numeric_beam_data[2]
    loads = numeric_beam_data[3:]
    structured_data = {}
    structured_data['Name'] = beam_name
    structured_data.update(beam_attributes)
    structured_data['Supports'] = parse_supports(supports)
    structured_data['Loads'] = parse_loads(loads)
    return structured_data


def get_node_locations(beam_length:float,supports:list[float])->dict[str,float]:
        
        """
        Returns a dict representing the node number and the node coordinates for the provided 
        support locations and beam length.
        """
        new_nodes = supports[:]
        if 0.0 not in supports:
            new_nodes.append(0.0)
        if beam_length not in supports:
            new_nodes.append(beam_length)
        
        node_locations = {}
        for idx,loc in enumerate(sorted(new_nodes)):
            node_locations.update({f"N{idx}":loc})
        return node_locations

def build_beam (beam_data:dict)->FEModel3D:
    """
    Returns a beam finite element model for the data in 'beam_data' 
    """
    
    beam_model=FEModel3D()
    L = beam_data["L"]
    E = beam_data["E"]
    I = beam_data["Iz"]
    Iy=beam_data["Iy"]
    J = beam_data["J"]
    A = beam_data["A"]
    nu=beam_data["nu"]
    rho=beam_data["rho"]
          
    G=calc_shear_modulus(nu,E)
    beam_model.add_material('default',E,G,nu,rho)

    support_loc=list(beam_data['Supports'].keys())
    beam_data['Nodes'] = get_node_locations(L,support_loc)
    node_dict=beam_data['Nodes']
    for node_no, node_loc in node_dict.items():
        beam_model.add_node(node_no,node_loc,0,0)
        support_type = beam_data['Supports'].get(node_loc, None)
        if support_type == "P":
            beam_model.def_support(node_no, True, True, True, True, False, False)
        elif support_type == "R":
            beam_model.def_support(node_no, False, True, True, False, False, False)
        elif support_type == "F":
            beam_model.def_support(node_no, True, True, True, True, True, True)

    
    beam_model.add_member(beam_data['Name'],"N0",node_no,'default',Iy,I,J,A)
    
    load_cases = []
    for load in beam_data['Loads']:
        if load['Type'] == "Point":
            beam_model.add_member_pt_load(
                beam_data['Name'],
                load['Direction'],
                load['Magnitude'],
                load['Location'],
                case=load["Case"],
            )
            if load['Case'] not in load_cases:
                load_cases.append(load['Case'])
        elif load['Type'] == "Dist":
            beam_model.add_member_dist_load(
                beam_data['Name'],
                load['Direction'],
                load['Start Magnitude'],
                load['End Magnitude'],
                load['Start Location'],
                load['End Location'],
                case=load['Case']
            )
            if load['Case'] not in load_cases:
                load_cases.append(load['Case'])

    for load_case in load_cases:
        beam_model.add_load_combo(load_case, {load_case: 1.0})
    return beam_model

def beam_results(filename:str):
    """
    Returns the bending moment,shear force diagram and deflection values for the given beam
    """
    sample=read_beam_file(filename)
    data=get_structured_beam_data(sample)
    model=build_beam (data)
    model.analyze()

    print("Load combinations:", model.LoadCombos.keys())
    print("Member:", data["Name"])

    member = model.Members[data["Name"]]

    print("Midspan moment:",
          member.moment(
              "Mz",
              data["L"]/2,
              "Dead"
          ))
    print("Deflection:",
          member.min_deflection(
              "dy",
              "Dead"
          ))

    member.plot_moment(
        Direction="Mz",
        combo_name="Dead",
        n_points=100
    )

    member.plot_shear(
        Direction="Fy",
        combo_name="Dead",
        n_points=100
    )

    return model
        

from tika import parser
import glob
import csv
import datetime
import os
import re

file_list=glob.glob("pdf/*.pdf")
file_list=[file_path.replace('pdf\\','pdf/') for file_path in file_list]

def is_first_cvtype(data):
    hasPersonalInfo="SUMMARY" in data
    return hasPersonalInfo    

def extract_second_format(data,file_path):
    name_to_split=file_path.split('.pdf')[0]
    name_to_split=name_to_split.split('/')[1].split('-application')[0]
    separator=" "
    #return [name, phone,email,address,ssn,birth,speciality,travel_experience]

    name=separator.join(name_to_split.split('-')) #full name get it

    #references index
    reference_index=data.index("REFERENCES")
    exp_index=data.index("EXPERIENCE")
    start_index=data.index("AVAILABLE TO START")

    phone=None
    email=None
    address=None
    ssn=None
    birth=None
    speciality=None 
    travel_experience=None
    if "SPECIALTY" in data:
        specialty_index=data.index("SPECIALTY")+1
        licenses_index= data.index("LICENSES")
            #separator for speciality
        separator=" "
        speciality=separator.join(data[specialty_index:licenses_index])

    for index,attribute in enumerate(data):
        if re.search('\\(\\d{3}\\)\\s\\d{3}-\\d{4}',attribute) and index<=reference_index:
            phone=attribute

        if re.search('^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$',attribute) and index<= reference_index:
            email=attribute
        if re.search(", [A-Z]{2} [0-9]{5}",attribute) and index<= exp_index:
            address=attribute
        if re.search("^[*]{3}-[*]{2}-[0-9]{4}",attribute):
            ssn=attribute.split('***-**-')[1]
        if re.search("[0-9]{2}/[0-9]{2}/[0-9]{2}",attribute) and index <= start_index:
            birth=attribute

    
    return [name, phone,email,address,ssn,birth,speciality,travel_experience]

def extract_first_format(data,file_path):
        #get personal data
    name_to_split=file_path.split('.pdf')[0]
    name_to_split=name_to_split.split('/')[1].split('-application')[0]
    separator=" "
    #return [name, phone,email,address,ssn,birth,speciality,travel_experience]

    name=separator.join(name_to_split.split('-')) #full name get it

    #indexes valid
    reference_index=data.index("REFERENCES")
    ssn_index=data.index("SSN")

    phone=None
    email=None
    address=None
    ssn=None
    birth=None
    speciality=None
    travel_experience=None

    if("ADDRESS" in data):
        address_start_index=data.index("ADDRESS")+1
        address_end_index=data.index("SSN")
        address=" ".join(data[address_start_index:address_end_index])

    if("SSN" in data):
        ssn_index= data.index("SSN")+1
        ssn=data[ssn_index]
        if(ssn == "DATE OF BIRTH"):
            ssn=None
        
        

    if("TRAVEL EXPERIENCE" in data):
        travel_experience=True
    else:
        travel_experience=False

    if("SPECIALTY" in data):
        speciality_start_index=data.index("SPECIALTY")+1

        if("TRAVEL EXPERIENCE" in data):
            speciality_end_index=data.index("TRAVEL EXPERIENCE")
        elif("LICENSES" in data):
            speciality_end_index=data.index("LICENSES")
        speciality=" ".join(data[speciality_start_index:speciality_end_index])
    else:
        speciality="Specialty not Avaible"

    for index,attribute in enumerate(data):
        if re.search('\\(\\d{3}\\)\\s\\d{3}-\\d{4}',attribute) and index <=reference_index :
            phone=attribute
        if re.search('^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$',attribute) and index<= reference_index:
            email=attribute
        if re.search("[0-9]{2}/[0-9]{2}/[0-9]{2}",attribute) and index > ssn_index and index <= ssn_index+2:
            birth=attribute

    return [name, phone,email,address,ssn,birth,speciality,travel_experience]


#in case at least one pdf exists, the csv timestamp name will be created 
if(file_list):
    file_csv_name=datetime.datetime.now().strftime('nursefly-%Y-%m-%d-%H-%M-%S.csv')
    with open("./data/"+file_csv_name, "w+") as file_output:
        csv_output = csv.writer(file_output)
        csv_output.writerow(["Name", "Phone","Email","Address","SSN","Date of Birth","Speciality","Travel Experience",'CV type'])

#the csv listed ordered by datetime of creation    
csv_list=glob.glob("data/*.csv")
csv_list=[file_path.replace('data\\','data/') for file_path in csv_list]


list_s=[]
count=0
for file_path in file_list:
    raw = parser.from_file(file_path)
    #focused on content
    raw = str(raw['content'])
    raw_lines=raw.splitlines()
    CRED = '\033[91m'   
    CEND = '\033[0m'
    #here the data will be filter avoiding empty strings
    data= list(filter(None,raw_lines))
    # print(data)
    if is_first_cvtype(data):
        row=extract_first_format(data,file_path)
        row.append('1')
    else:
        row=extract_second_format(data,file_path)
        row.append("2")
    
        
        
    


    with open(csv_list[-1], "a") as file_output:
        csv_output = csv.writer(file_output)
        csv_output.writerow(row)
        

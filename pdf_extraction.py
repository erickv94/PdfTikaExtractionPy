from tika import parser
import glob
import csv
import datetime

file_list=glob.glob("pdf/*.pdf")
file_list=[file_path.replace('pdf\\','pdf/') for file_path in file_list]


#in case at least one pdf exists, the csv timestamp name will be created 
if(file_list):
    file_csv_name=datetime.datetime.now().strftime('nursefly-%Y-%m-%d-%H-%M-%S.csv')
    with open("./data/"+file_csv_name, "w+") as file_output:
        csv_output = csv.writer(file_output)
        csv_output.writerow(["Name", "Phone","Email","Address","SSN","Date of Birth","Speciality","Travel Experience"])

#the csv listed ordered by datetime of creation    
csv_list=glob.glob("data/*.csv")
csv_list=[file_path.replace('data\\','data/') for file_path in csv_list]


for file_path in file_list:
    raw = parser.from_file(file_path)
    #focused on content
    raw = str(raw['content'])
    raw_lines=raw.splitlines()

    #here the data will be filter avoiding empty strings
    data= list(filter(None,raw_lines))
    

    #get personal data
    name=data[0]
    if("PHONE" in data):
        phone_index=data.index("PHONE")+1
        phone=data[phone_index]
    else:
        phone="Phone not Avaible"

    if("EMAIL" in data):
        email_index=data.index("EMAIL")+1
        email=data[email_index]
    else:
        email="Email not Avaible"

    if("ADDRESS" in data):
        address_start_index=data.index("ADDRESS")+1
        address_end_index=data.index("SSN")
        address=" ".join(data[address_start_index:address_end_index])
    else:
        address="Address not Avaible"

    if("SSN" in data):
        ssn_index= data.index("SSN")+1
        ssn=data[ssn_index]
        if(ssn == "DATE OF BIRTH"):
            ssn="SSN not Avaible"
    else:
        ssn="SSN not Avaible"
        
    if("DATE OF BIRTH" in data):
        birth_index=data.index("DATE OF BIRTH")+1
        birth=data[birth_index]
        if(birth == "HIGHLIGHTS"):
            birth="Date not Avaible"
    else:
        birth="Date not Avaible"

    if("SPECIALTY" in data):
        speciality_start_index=data.index("SPECIALTY")+1

        if("TRAVEL EXPERIENCE" in data):
            speciality_end_index=data.index("TRAVEL EXPERIENCE")
        elif("LICENSES" in data):
            speciality_end_index=data.index("LICENSES")
        

        
        speciality=" ".join(data[speciality_start_index:speciality_end_index])
    else:
        speciality="Specialty not Avaible"
    
    if("TRAVEL EXPERIENCE" in data):
        travel_experience=True
    else:
        travel_experience=False
    name=data[0]
    if("PHONE" in data):
        phone_index=data.index("PHONE")+1
        phone=data[phone_index]
    else:
        phone="Phone not Avaible"

    if("EMAIL" in data):
        email_index=data.index("EMAIL")+1
        email=data[email_index]
    else:
        email="Email not Avaible"

    if("ADDRESS" in data):
        address_start_index=data.index("ADDRESS")+1
        address_end_index=data.index("SSN")
        address=" ".join(data[address_start_index:address_end_index])
    else:
        address="Address not Avaible"

    if("SSN" in data):
        ssn_index= data.index("SSN")+1
        ssn=data[ssn_index]
        if(ssn == "DATE OF BIRTH"):
            ssn="SSN not Avaible"
    else:
        ssn="SSN not Avaible"
        
    if("DATE OF BIRTH" in data):
        birth_index=data.index("DATE OF BIRTH")+1
        birth=data[birth_index]
        if(birth == "HIGHLIGHTS"):
            birth="Date not Avaible"
    else:
        birth="Date not Avaible"

    if("SPECIALTY" in data):
        speciality_start_index=data.index("SPECIALTY")+1

        if("TRAVEL EXPERIENCE" in data):
            speciality_end_index=data.index("TRAVEL EXPERIENCE")
        elif("LICENSES" in data):
            speciality_end_index=data.index("LICENSES")
        

        
        speciality=" ".join(data[speciality_start_index:speciality_end_index])
    else:
        speciality="Specialty not Avaible"
    
    if("TRAVEL EXPERIENCE" in data):
        travel_experience=True
    else:
        travel_experience=False

        

        
    


    with open(csv_list[-1], "a") as file_output:
        csv_output = csv.writer(file_output)
        csv_output.writerow([name, phone,email,address,ssn,birth,speciality,travel_experience])
        
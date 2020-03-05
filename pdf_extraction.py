from tika import parser
import glob
import csv
import datetime
import os
import re
import requests
import json

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

    if ("CERTIFICATIONS" in data):
        crt_index = data.index("CERTIFICATIONS") + 1
        temp = True
        certification = []
        while (temp):
            save = True
            if ("EDUCATION" in data[crt_index]):
                temp = False

            else:
                temp2 = data[crt_index].split()[0]
                #print(temp2)
                for item in certification:
                    if(temp2== item):

                        save=False
                if(save):
                    certification.append(temp2)
                crt_index = crt_index + 1
    if ("LICENSES" in data):
        licences_index = data.index("LICENSES") + 1
        temp = True
        licences = []
        while (temp):
            save = True
            if ("CERTIFICATIONS" in data[licences_index]):
                temp = False
            else:
                temp2 = data[licences_index].split(",")[0]

                for item in licences:
                    if (temp2 == item):
                        save = False
                if (save):
                    licences.append(temp2)
                licences_index = licences_index + 1

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

    
    return [name, phone,email,address,ssn,birth,speciality,travel_experience,certification,licences]

def extract_first_format(data,file_path):
        #get personal data
    name_to_split=file_path.split('.pdf')[0]
    name_to_split=name_to_split.split('/')[1].split('-application')[0]
    separator=" "

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
    if("CERTIFICATIONS" in data):
        crt_index = data.index("CERTIFICATIONS") + 1
        temp = True
        certification = []
        while (temp):
            save = True
            if ("EDUCATION" in data[crt_index]):
                temp = False

            else:
                temp2 = data[crt_index].split()[0]
                # print(temp2)
                for item in certification:
                    if (temp2 == item):
                        
                        save = False
                if (save):
                    certification.append(temp2)
                crt_index = crt_index + 1

    if ("LICENSES" in data):
            licences_index = data.index("LICENSES") + 1
            temp = True
            licences = []
            while (temp):
                save = True
                if ("CERTIFICATIONS" in data[licences_index]):
                    temp = False
                else:
                    temp2 = data[licences_index].split(",")[0]

                    for item in licences:
                        if (temp2 == item):
                            save = False
                    if (save):
                        licences.append(temp2)
                    licences_index = licences_index + 1



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

    return [name, phone,email,address,ssn,birth,speciality,travel_experience,certification,licences]

def get_specialities(text):

    # the dictionary bellow has all the possible matches of specialty text
    # some anotations bellow
    # cbr: could be replaced
    specialities_availables={
        'emergency department': 'ER | Emergency Room',#cbr
        'hospital administration': 'ADM | Hospital Administration', #cbr
        'cardiovasculta intensive care':'CVICU | Cardiovascular Intensive Care Unit', #cbr
        'nicu': 'NICU | Neonatal Intensive Care Unit',
        'med surg':'MedSurg | Medical/SurgicalICU',
        'intensive care unit': 'ICU | Intensive Care Unit',
        'registered nurse':'RN | Registered Nurse',
        'charge nurse': 'CHRG | Charge Nurse',
        'small town':'ER-Critical Access | Small Town ER (Rural ER)',
        'cma':'CMA | Certified Medical Assistant',
        'cna':'CNA | Certified Nursing Assistant',
        'dialysis':'DIA | Dialysis',
        'skilled': 'SKL | Skilled Nursing',
        'long term care': 'LTC | Long Term Care',
        'nights':'Nights |',
        'psychiatric':'PSYCH | Psychiatric Unit Nurse',
        'floating':'FLOAT | Floating',
        'rehabilitation': 'RHB | Inpatient Rehab',
        'progressive care':'PCU | Progressive Care Unit',
        'home health':'HH | Home Health',
        'orthopedics':'ORTHO | Orthopedic Unit',
        'pacu':'PACU | Post Anesthesia Care Unit',
        'telemetry':'TELE | Telemetry',
        'technical specialist':'TECH | Technical Specialist',
        'flight nurse':'FLIGHT | Flight Nurse',
        'obstetrics':'OB | Obstetrics',
        'minimum data set':'MDS | Minimum Data Set',
        'picu':'PICU | Pediatric ICU',
        'pediatricmid':'PED | PediatricMID',
        'midwife':'MID | Nurse-Midwife ',
        'nurse anesthetist':'CRNA | Certified Registered Nurse Anesthetist',
        'lpn':'LPN | Licensed Practical Nurse',
        'flu':'FLU/Wellness Clinic | Flu',
        'step down unit':'STPDN | Step Down Unit',
        'dialysis licensed practical nurse':'CDLPN | Certified Dialysis Licensed Practical Nurse',
        'manager':'MGR | Manager',
        'nurse practitioner': 'NP | Nurse Practitioner',
        'oncology':'ONC | Oncology',
        'respiratory therapist': 'RRT | Registered Respiratory Therapist',
        'pre-operation':'PREOP | Pre-Operation',
        'labor and delivery':'L&D | Labor & Delivery',
        'electronic intensive care':'eICU | Electronic Intensive Care Unit',
        'surgical intensive care':'SICU | Surgical intensive care unit',
        'catheter laboratory':"CATH | Catheter Laboratory RN",
        'occupational health':'OCC | Occupational Health',
        'phd':'Phd |',
        'office clerk':'CLRK | Office Clerk',
        'medical unit':'MDAS | Medical Assistant',
        'certified medical-surgical':'CMSRN | Certified Medical-Surgical Registered Nurse',
        'med lab tech':'MLT | Med Lab Tech',
        'per diem':'PD | Per Diem',
        'wound care':'CWCN | Wound Care',
        'outpatient infusion':'INF | Outpatient Infusion',
        'ambulatory care':'RNBC | Ambulatory Care Nursing',
        'allied':'AL | Allied',
        'perfusionist':'CCP | Certified Cardiovascular Perfusionist',
        'phlebotomist':'Phlebo | Phlebotomist',
        'trauma':'TCRN | Trauma Certified Registered Nurse',
        'sterile processing tech':'SPT | Sterile Processing Tech'
    }
    speciality_list=[]
    
    if not text:
        return []

    for speciality in specialities_availables.keys():
        if speciality in text.lower():
            speciality_list.append(specialities_availables[speciality])

    if not speciality_list:
        speciality_list.append('Other')

    return speciality_list

def get_experience_years(text):
    start_indexes=[]
    end_indexes=[]
    years_list=[]

    if not text:
        return None

    for match in re.finditer('\(',text):
        start_indexes.append(match.start()+1)

    for match in re.finditer(' years\)',text):
        end_indexes.append(match.start())

    for index in range(len(start_indexes)):
        years=text[start_indexes[index]:end_indexes[index]]
        years= float(years)
        years_list.append(years)
        
    return sum(years_list)

def get_fulladdress(text):
    if not text:
        return None

    full_address=text.split(',')[0]
    return full_address

def get_addres(text):
    if not text:
        return None
    if (len(text.split(','))>=3):
        addres=text.split(',')[2]
    else:
        addres=text.split(',')[1]

    state = addres.split()[0]
    zip = addres.split()[1]
    return [state, zip]

def get_state(text):

  control=False
  state_list= {
        "649",
        " ID",
        " IL",
        " MD ",
        " MN ",
        " OR ",
        "AK",
        "AL",
        "Albany",
        "AR",
        "AZ",
        "Boise",
        "CA",
        "CO",
        "CT",
        "DE",
        "Fct",
        "FL",
        "FL ",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MD",
        "MI",
        "Mill",
        "MN",
        "MO",
        "MS",
        "NC",
        "ND",
        "NE",
        "NV",
        "NY",
        "NY ",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "Sacramento",
        "SanBernardino",
        "SC",
        "TN",
        "TX",
        "TX ",
        "UT",
        "VA",
        "WA",
        "WI",
        "Wilsonville",
        "WV",
        "WY",
        "VI",
        "MA",
        "AU",
        "NJ",
        "VT",
        "AE",
        "SD",
        "MT",
        "GR",
        "NM",
        "AP",
        "CN",
        "AB",
        "B."
}
  if not text:
      return None

  for index in state_list:
        if (index == text):
            control=True
  if(control):
    value=text
  else:
      value=None
  return value

def get_profesional_license(text):
     control=False
     temporal_variable=[]
     license_list={
         "RN | Registered Nurse",
         "Other |",
         "BSN | Bachelors of Registered Nursing",
         "CMA | Certified Medical Assistant",
         "CNA | Certified Nursing Assistant",
         "CNM |",
         "CRNA | Certified Registered Nurse Anesthetists",
         "First Assist |",
         "LPN/LVN | Licensed Practical Nurse",
         "NP | Nurse Practitioner",
         "Surg Tech | Surgery Technician",
         "PERF | Perfusionist",
         "CCP | Certified Cardiovascular Perfusionist",
         "RN",
         "OTHER",
         "LPN",
         "Certified nursing assistant"  }
     if not text:
         return None
     for index in license_list:
         for x in text:
             if(index.split()[0] == x):
                control = True
                temporal_variable.append(index)
     if (control):
         value = temporal_variable
     else:
         value = text
         value.append("Other")
     return value

def get_licensed_state(text):
    control=False
    list=[]
    if not text:
        return None
    licensed_states={
            "California":"CA",
            "Idaho":"ID",
            "Oregon":"OR",
            "Utah":"UT",
            "Georgia":"GA",
            "Connecticut":"CT",
            "Massachusetts":"MA",
            "Florida":"FL",
            "New York":"NY",
            "Alaska":"AK",
            "Hawaii":"HI",
            "New Mexico":"NM",
            "Kentucky":"KY",
            "Missouri":"MO",
            "Oklahoma":"OK",
            "Ohio":"OH",
            "Texas":"TX",
            "Tennesse":"TN",
            "Colorado":"CO",
            "South Carolina":"SC",
            "Vermont":"VT",
            "West Virginia":"WV",
            "Virginia":"VA",
            "South Dakota":"SD",
            "North Dakota":"ND",
            "Nebraska":"NE",
            "Rhode Island":"RI",
            "Wisconsin":"WI",
            "Washington":"WA",
            "Iowa":"IA",
            "Illinois":"IL",
            "Mississippi":"MS",
            "North Carolina":"NC",
            "Pennsylvania":"PA",
            "Minnesota":"MN",
            "Louisana":"LA",
            "Montana":"MT",
            "Michigan":"MI",
            "Nevada":"NV",
            "Maine":"ME",
            "New Hampshire":"NH",
            "Alabama":"AL",
            "Wyoming":"WY",
            "Maryland":"MD",
            "Arizona":"AZ",
            "Kansas":"KS",
            "Indiana":"IN",
            "Arkansas":"AR",
            "Delaware":"DE",
           "New Jersey":"NJ"
    }


    return list

def post_data(list):

    test_data = {
        'fields': {
            'Nurse Full Name': list[0],
            'Phone': list[1],
            'Email': list[2],
            'First Name': 'Francisco',
            'Last Name': 'Mendoza',
            'Nursa Status': '2 | Outreach',
            'Source': 'NurseFly'
        },
    }



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
    raw = parser.from_file("C:/Users/ferna/OneDrive/Desktop/PdfTikaExtractionPy/"+file_path)
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
    else:
        row=extract_second_format(data,file_path)

    #return [name, phone,email,address,ssn,birth,speciality,travel_experience]
    #specific data to convert into another piece of data
    speciality=row[6]

    #json data formed
    fullname=row[0]    
    phone=row[1]
    email=row[2]
    full_address=get_fulladdress(row[3])
    speciality_list=get_specialities(text=speciality)
    experience_years=get_experience_years(text=speciality)
    notes=speciality
    addres=get_addres(row[3])
    if addres is not None:
        state=addres[0]
        zip= addres[1]
    else:
        state=None
        zip=None
    firstname=fullname.split()[0]
    lastname=fullname.split()[1]
    certifications=row[8]
    licences=row[9]

    true_certifications=get_profesional_license(certifications)
    true_state=get_state(state)
    print(fullname,licences)

   # print(fullname,firstname,lastname,full_address,state,zip)

    #list_post.append(fullname,phone,email,'NurseFly')

   # with open(csv_list[-1], "a") as file_output:
    #    csv_output = csv.writer(file_output)
     #   csv_output.writerow(row)
        

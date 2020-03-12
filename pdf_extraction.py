from tika import parser
import glob
import csv
import datetime
import os
import re
import requests
import json
from jsonmerge import merge

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
        'med surg':"MedSurg | Medical/Surgical",
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
    other_list=[]

    if not text:
        return None


    for speciality in specialities_availables.keys():
        if speciality in text.lower():
            speciality_list.append(specialities_availables[speciality])

    if not speciality_list:
        speciality_list.append("Other")
        other_list.append(text)


    return [speciality_list,other_list ]

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
     other=[]
     license_list={
         "RN":"RN | Registered Nurse",
         "Other":"Other |",
         "BSN":"BSN | Bachelors of Registered Nursing",
         "BSN":"CMA | Certified Medical Assistant",
         "CNA":"CNA | Certified Nursing Assistant",
         "CNM":"CNM |",
         "CRNA":"CRNA | Certified Registered Nurse Anesthetists",
         "First Assist":"First Assist |",
         "Nurse Practitioner":"NP | Nurse Practitioner",
         "Surg Tech":"Surg Tech | Surgery Technician",
         "Perfusionist:":"PERF | Perfusionist",
         "Certified Cardiovascular Perfusionist":"CCP | Certified Cardiovascular Perfusionist",
         "RN:":"RN",
         "OTHER":"OTHER",
         "LPN":"LPN",
         "Certified nursing assistant":"Certified nursing assistant"  }
     if not text:
         return None
     for x in text:
        for index in license_list.keys():
             variable=x
             if(index == x):
                temporal_variable.append(license_list[index])
                control=True
        if(control==False):
            variable2=False
            for serch in temporal_variable:
             if ("Other" in serch):
               variable2=True

            if(variable2==False):
                temporal_variable.append("Other |")
            other.append(variable)
        control=False

     return [temporal_variable,other]

def get_licensed_state(text):
    control=False
    list=[]
    other=[]
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
            "Louisiana":"LA",
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

    if not text:
        return None

    for x in text:

        for index in licensed_states.keys():
            variable=x
            if ( index in  x ):
                list.append(licensed_states[index])
                control=True
        if(control==False):
            if("Lic:" in variable or "Exp:"in variable ):
               save=False
            else:
                save=True
            if(save):
                other.append(variable)

        control=False
    return [list,other]

def get_state(text):

    if not text:
        return None
    list_states={
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
    variable=None
    for index in list_states:
        if(text==index):
            variable=True

    if(variable):
        value=text
    else:
        value=None
    return value

def post_data(list):
    apikey = {'api_key': 'keyFt0iUCIPncgJA6'}
    url = 'https://api.airtable.com/v0/appIap7xPyOplHI7c/NursaDbAvalogics'
     # 'Profession License':[list[4]],
    if(list[4] is not None):
        professional=professional_licensed_post(list[4])
    else:
        professional=None

    if(list[9] is not None):
        specility=specility_post(list[9])
    else:
        specility=None
    if (list[8] is not None):
     licenced_state=licenced_state_post(list[8])
    else:
        licenced_state=None


    if(list[14] is  None or list[14]=="" or list[14]==[]):
        test_data = {
            'fields': {
                'Nurse Full Name': list[0],
                'Phone': list[1],
                'Email': list[2],
                'Source': list[3],
                # 'Profession License':[list[4]],
                'First Name':list[5],
                'Last Name':list[6],
               # 'Notes':list[7],
              #'Licensed States':[list[8]],
                #'Specialty':[list[9]],
                'Experience (In Years)':list[10],
                'Full Address':list[11],
                'State':list[12],
                'Zip':list[13]

            },
         }
    else:

        test_data = {
            'fields': {
                'Nurse Full Name': list[0],
                'Phone': list[1],
                'Email': list[2],
                'Source': list[3],
                # 'Profession License':[list[4]],
                'First Name': list[5],
                'Last Name': list[6],
                 'Notes':list[7],
                # 'Licensed States':[list[8]],
                # 'Specialty':[list[9]],
                'Experience (In Years)': list[10],
                'Full Address': list[11],
                'State': list[12],
                'Zip': list[13],
                'SSN': int(list[14])
            },
        }

    if(professional is not None):
        if(specility is not None):
            if(licenced_state is not None):
                result = merge(test_data, specility)
                result2 = merge(result,professional )
                result3 = merge(result2, licenced_state)
                data_post=result3
            else:
                result = merge(test_data, professional)
                result2 = merge(result, specility)
                data_post = result2
        else:
            if (licenced_state is not None):
                result = merge(test_data, professional)
                result2 = merge(result, licenced_state)
                data_post = result2
            else:
                result = merge(test_data, professional)
                data_post = result
    else:
        if(specility is not None):
            if(licenced_state is not None):
                result = merge(test_data, specility)
                result2 = merge(result, licenced_state)
                data_post=result2
            else:
                result = merge(test_data, specility)
                data_post = result

        else:
            if(licenced_state is not None):
                result = merge(test_data, licenced_state)
                data_post=result
            else:
                data_post=test_data





    try:
        r = requests.post(url, params=apikey, json=data_post)
        print(r.json())
    except:
        print("Error in post Data check to end point.")

def professional_licensed_post(list):
    apikey = {'api_key': 'keyFt0iUCIPncgJA6'}
    url = 'https://api.airtable.com/v0/appIap7xPyOplHI7c/NursaDbAvalogics' + "/rec0lKECTVOYBlppb",

    if list is  None:
        return None
    if list==[]:
        return None

    index=len(list)

    if index==1:
        test_data={
            'fields': {
             'Profession License':
                [
                  list[0]
                ]
            },
        }
    else:
        if index==2:
            test_data = {
                'fields': {
                    'Profession License':
                        [
                            list[0],
                            list[1]
                        ]
                },
            }
        else:
            if index==3:
                test_data = {
                    'fields': {

                        'Profession License':
                            [
                                list[0],
                                list[1],
                                list[2]
                            ]
                    },
                }
            else:
                if index==4:
                    test_data = {
                        'fields': {

                            'Profession License':
                                [
                                    list[0],
                                    list[1],
                                    list[2],
                                    list[3]
                                ]
                        },
                    }
                else:
                   if index==5:
                        test_data = {
                            'fields': {

                                'Profession License':
                                    [
                                        list[0],
                                        list[1],
                                        list[2],
                                        list[3],
                                        list[4]
                                    ]
                            },

                    }
                   else:
                       if index==6:
                           test_data = {
                               'fields': {

                                   'Profession License':
                                       [
                                           list[0],
                                           list[1],
                                           list[2],
                                           list[3],
                                           list[4],
                                           list[5]
                                       ]
                               },
                           }
                       else:
                           if index==7:
                               test_data = {
                                   'fields': {

                                           [
                                               list[0],
                                               list[1],
                                               list[2],
                                               list[3],
                                               list[4],
                                               list[5],
                                               list[6]
                                           ]
                                   },
                               }
                           else:
                               if index==8:
                                   test_data = {
                                       'fields': {

                                           'Profession License':
                                               [
                                                   list[0],
                                                   list[1],
                                                   list[2],
                                                   list[3],
                                                   list[4],
                                                   list[5],
                                                   list[6],
                                                   list[7]
                                               ]
                                       },
                                   }
                               else:
                                   if index==9:
                                       test_data = {
                                           'fields': {

                                               'Profession License':
                                                   [
                                                       list[0],
                                                       list[1],
                                                       list[2],
                                                       list[3],
                                                       list[4],
                                                       list[5],
                                                       list[6],
                                                       list[7],
                                                       list[8]
                                                   ]
                                           },
                                       }
                                   else:
                                       if index==10:
                                           test_data = {
                                               'fields': {

                                                   'Profession License':
                                                       [
                                                           list[0],
                                                           list[1],
                                                           list[2],
                                                           list[3],
                                                           list[4],
                                                           list[5],
                                                           list[6],
                                                           list[7],
                                                           list[8],
                                                           list[9]
                                                       ]
                                               },
                                           }

    return test_data

def specility_post(list):
    if list is None:
        return None
    if list == []:
        return None
    index = len(list)

    if index == 1:
        test_data = {
            'fields': {
                'Specialty':
                    [
                        list[0]
                    ]
            },
        }
    else:
        if index == 2:
            test_data = {
                'fields': {
                    'Specialty':
                        [
                            list[0],
                            list[1]
                        ]
                },
            }
        else:
            if index == 3:
                test_data = {
                    'fields': {

                        'Specialty':
                            [
                                list[0],
                                list[1],
                                list[2]
                            ]
                    },
                }
            else:
                if index == 4:
                    test_data = {
                        'fields': {

                            'Specialty':
                                [
                                    list[0],
                                    list[1],
                                    list[2],
                                    list[3]
                                ]
                        },
                    }
                else:
                    if index == 5:
                        test_data = {
                            'fields': {

                                'Specialty':
                                    [
                                        list[0],
                                        list[1],
                                        list[2],
                                        list[3],
                                        list[4]
                                    ]
                            },

                        }
                    else:
                        if index == 6:
                            test_data = {
                                'fields': {

                                    'Specialty':
                                        [
                                            list[0],
                                            list[1],
                                            list[2],
                                            list[3],
                                            list[4],
                                            list[5]
                                        ]
                                },
                            }
                        else:
                            if index == 7:
                                test_data = {
                                    'fields': {
                                    'Specialty':
                                        [
                                            list[0],
                                            list[1],
                                            list[2],
                                            list[3],
                                            list[4],
                                            list[5],
                                            list[6]
                                        ]
                                    },
                                }
                            else:
                                if index == 8:
                                    test_data = {
                                        'fields': {

                                            'Specialty':
                                                [
                                                    list[0],
                                                    list[1],
                                                    list[2],
                                                    list[3],
                                                    list[4],
                                                    list[5],
                                                    list[6],
                                                    list[7]
                                                ]
                                        },
                                    }
                                else:
                                    if index == 9:
                                        test_data = {
                                            'fields': {

                                                'Specialty':
                                                    [
                                                        list[0],
                                                        list[1],
                                                        list[2],
                                                        list[3],
                                                        list[4],
                                                        list[5],
                                                        list[6],
                                                        list[7],
                                                        list[8]
                                                    ]
                                            },
                                        }
                                    else:
                                        if index == 10:
                                            test_data = {
                                                'fields': {

                                                    'Specialty':
                                                        [
                                                            list[0],
                                                            list[1],
                                                            list[2],
                                                            list[3],
                                                            list[4],
                                                            list[5],
                                                            list[6],
                                                            list[7],
                                                            list[8],
                                                            list[9]
                                                        ]
                                                },
                                            }

    return test_data

def licenced_state_post(list):
    if list is None:
        return None
    if list == []:
        return None
    index = len(list)
    if(index==0):
        return None

    if index == 1:
        test_data = {
            'fields': {
                'Licensed States':
                    [
                        list[0]
                    ]
            },
        }
    else:
        if index == 2:
            test_data = {
                'fields': {
                    'Licensed States':
                        [
                            list[0],
                            list[1]
                        ]
                },
            }
        else:
            if index == 3:
                test_data = {
                    'fields': {

                        'Licensed States':
                            [
                                list[0],
                                list[1],
                                list[2]
                            ]
                    },
                }
            else:
                if index == 4:
                    test_data = {
                        'fields': {

                            'Licensed States':
                                [
                                    list[0],
                                    list[1],
                                    list[2],
                                    list[3]
                                ]
                        },
                    }
                else:
                    if index == 5:
                        test_data = {
                            'fields': {

                                'Licensed States':
                                    [
                                        list[0],
                                        list[1],
                                        list[2],
                                        list[3],
                                        list[4]
                                    ]
                            },

                        }
                    else:
                        if index == 6:
                            test_data = {
                                'fields': {

                                    'Licensed States':
                                        [
                                            list[0],
                                            list[1],
                                            list[2],
                                            list[3],
                                            list[4],
                                            list[5]
                                        ]
                                },
                            }
                        else:
                            if index == 7:
                                test_data = {
                                    'fields': {
                                    'Licensed States':
                                        [
                                            list[0],
                                            list[1],
                                            list[2],
                                            list[3],
                                            list[4],
                                            list[5],
                                            list[6]
                                        ]
                                    },
                                }
                            else:
                                if index == 8:
                                    test_data = {
                                        'fields': {

                                            'Licensed States':
                                                [
                                                    list[0],
                                                    list[1],
                                                    list[2],
                                                    list[3],
                                                    list[4],
                                                    list[5],
                                                    list[6],
                                                    list[7]
                                                ]
                                        },
                                    }
                                else:
                                    if index == 9:
                                        test_data = {
                                            'fields': {

                                                'Licensed States':
                                                    [
                                                        list[0],
                                                        list[1],
                                                        list[2],
                                                        list[3],
                                                        list[4],
                                                        list[5],
                                                        list[6],
                                                        list[7],
                                                        list[8]
                                                    ]
                                            },
                                        }
                                    else:
                                        if index == 10:
                                            test_data = {
                                                'fields': {

                                                    'Licensed States':
                                                        [
                                                            list[0],
                                                            list[1],
                                                            list[2],
                                                            list[3],
                                                            list[4],
                                                            list[5],
                                                            list[6],
                                                            list[7],
                                                            list[8],
                                                            list[9]
                                                        ]
                                                },
                                            }
                                        else:
                                            if index==11:
                                                test_data = {
                                                    'fields': {

                                                        'Licensed States':
                                                            [
                                                                list[0],
                                                                list[1],
                                                                list[2],
                                                                list[3],
                                                                list[4],
                                                                list[5],
                                                                list[6],
                                                                list[7],
                                                                list[8],
                                                                list[9],
                                                                list[10]
                                                            ]
                                                    },
                                                }
                                            else:
                                                if index==12:
                                                    test_data = {
                                                        'fields': {

                                                            'Licensed States':
                                                                [
                                                                    list[0],
                                                                    list[1],
                                                                    list[2],
                                                                    list[3],
                                                                    list[4],
                                                                    list[5],
                                                                    list[6],
                                                                    list[7],
                                                                    list[8],
                                                                    list[9],
                                                                    list[10],
                                                                    list[11]
                                                                ]
                                                        },
                                                    }
                                                else:
                                                    if index==13:
                                                        test_data = {
                                                            'fields': {

                                                                'Licensed States':
                                                                    [
                                                                        list[0],
                                                                        list[1],
                                                                        list[2],
                                                                        list[3],
                                                                        list[4],
                                                                        list[5],
                                                                        list[6],
                                                                        list[7],
                                                                        list[8],
                                                                        list[9],
                                                                        list[10],
                                                                        list[11],
                                                                        list[12]
                                                                    ]
                                                            },
                                                        }
                                                    else:
                                                        if index==14:
                                                            test_data = {
                                                                'fields': {

                                                                    'Licensed States':
                                                                        [
                                                                            list[0],
                                                                            list[1],
                                                                            list[2],
                                                                            list[3],
                                                                            list[4],
                                                                            list[5],
                                                                            list[6],
                                                                            list[7],
                                                                            list[8],
                                                                            list[9],
                                                                            list[10],
                                                                            list[11],
                                                                            list[12],
                                                                            list[13]
                                                                        ]
                                                                },
                                                            }
                                                        else:
                                                            if index==15:
                                                                test_data = {
                                                                    'fields': {

                                                                        'Licensed States':
                                                                            [
                                                                                list[0],
                                                                                list[1],
                                                                                list[2],
                                                                                list[3],
                                                                                list[4],
                                                                                list[5],
                                                                                list[6],
                                                                                list[7],
                                                                                list[8],
                                                                                list[9],
                                                                                list[10],
                                                                                list[11],
                                                                                list[12],
                                                                                list[13],
                                                                                list[14]
                                                                            ]
                                                                    },
                                                                }
                                                            else:
                                                                if index==16:
                                                                    test_data = {
                                                                        'fields': {

                                                                            'Licensed States':
                                                                                [
                                                                                    list[0],
                                                                                    list[1],
                                                                                    list[2],
                                                                                    list[3],
                                                                                    list[4],
                                                                                    list[5],
                                                                                    list[6],
                                                                                    list[7],
                                                                                    list[8],
                                                                                    list[9],
                                                                                    list[10],
                                                                                    list[11],
                                                                                    list[12],
                                                                                    list[13],
                                                                                    list[14],
                                                                                    list[15]
                                                                                ]
                                                                        },
                                                                    }
                                                                else:
                                                                    if index==17:
                                                                        test_data = {
                                                                            'fields': {

                                                                                'Licensed States':
                                                                                    [
                                                                                        list[0],
                                                                                        list[1],
                                                                                        list[2],
                                                                                        list[3],
                                                                                        list[4],
                                                                                        list[5],
                                                                                        list[6],
                                                                                        list[7],
                                                                                        list[8],
                                                                                        list[9],
                                                                                        list[10],
                                                                                        list[11],
                                                                                        list[12],
                                                                                        list[13],
                                                                                        list[14],
                                                                                        list[15],
                                                                                        list[16]
                                                                                    ]
                                                                            },
                                                                        }
                                                                    else:
                                                                        if index==18:
                                                                            test_data = {
                                                                                'fields': {

                                                                                    'Licensed States':
                                                                                        [
                                                                                            list[0],
                                                                                            list[1],
                                                                                            list[2],
                                                                                            list[3],
                                                                                            list[4],
                                                                                            list[5],
                                                                                            list[6],
                                                                                            list[7],
                                                                                            list[8],
                                                                                            list[9],
                                                                                            list[10],
                                                                                            list[11],
                                                                                            list[12],
                                                                                            list[13],
                                                                                            list[14],
                                                                                            list[15],
                                                                                            list[16],
                                                                                            list[17]
                                                                                        ]
                                                                                },
                                                                            }
                                                                        else:
                                                                            if index==19:
                                                                                test_data = {
                                                                                    'fields': {

                                                                                        'Licensed States':
                                                                                            [
                                                                                                list[0],
                                                                                                list[1],
                                                                                                list[2],
                                                                                                list[3],
                                                                                                list[4],
                                                                                                list[5],
                                                                                                list[6],
                                                                                                list[7],
                                                                                                list[8],
                                                                                                list[9],
                                                                                                list[10],
                                                                                                list[11],
                                                                                                list[12],
                                                                                                list[13],
                                                                                                list[14],
                                                                                                list[15],
                                                                                                list[16],
                                                                                                list[17],
                                                                                                list[18]
                                                                                            ]
                                                                                    },
                                                                                }
                                                                            else:
                                                                                test_data = {
                                                                                    'fields': {

                                                                                        'Licensed States':
                                                                                            [
                                                                                                list[0],
                                                                                                list[1],
                                                                                                list[2],
                                                                                                list[3],
                                                                                                list[4],
                                                                                                list[5],
                                                                                                list[6],
                                                                                                list[7],
                                                                                                list[8],
                                                                                                list[9],
                                                                                                list[10],
                                                                                                list[11],
                                                                                                list[12],
                                                                                                list[13],
                                                                                                list[14],
                                                                                                list[15],
                                                                                                list[16],
                                                                                                list[17],
                                                                                                list[18],
                                                                                                list[19]
                                                                                            ]
                                                                                    },
                                                                                }

    return test_data

def extract_data():
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



            speciality=row[6]

            #json data formed
            fullname=row[0]
            phone=row[1]
            email=row[2]
            full_address=get_fulladdress(row[3])

            if (speciality is not None):
                speciality_list=get_specialities(text=speciality)[0]
                notes = get_specialities(text=speciality)[1]
                if(speciality_list is not None):
                    if(len(speciality_list)>=2):
                        notes_especial=speciality
                    else:
                        notes_especial=None
            else:
                speciality_list=None
                notes=None
            experience_years=get_experience_years(text=speciality)
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
            SSN=row[4]

            if certifications is None  or certifications==[] :
                professional_license = None
                notes2 = None
            else:
                professional_license = get_profesional_license(certifications)[0]
                notes2 = get_profesional_license(certifications)[1]


            true_state=get_state(state)

            if licences is None  or licences==[] :
                licenced_state = None
                notes3 = None
            else:
                licenced_state = get_licensed_state(licences)[0]

                notes3=get_licensed_state(licences)[1]
            if(notes==[]):
                notes=None
            if(notes2==[]):
                notes2=None
            if(notes3==[]):
                notes3= None
            text="Specility Notes (Not contained in the dictionary): "
            text2 ="Professional License Notes (Not contained in the dictionary): "
            text3="Licenced State Notes (Not contained in the dictionary): "
            state_variable = get_state(state)
            notes_final=""

            if notes is not None:
                for index in notes:
                    text=text + index + " "
                notes_final=notes_final+text

            if notes2 is not None:
                 for item in notes2:
                     text2=text2 + item + " "
                 notes_final = notes_final + text2
            if notes3 is not None:
                for index in notes3:
                    text3 = text3 + index + " "
                notes_final = notes_final + text3

            if(notes_especial is not None):
              notes_final=notes_final+" ; Specialty Info for Two or more specialty: "+notes_especial




            post_data([fullname, phone, email, 'NurseFly', professional_license, firstname, lastname,
                             notes_final,licenced_state,speciality_list,experience_years,full_address,state_variable,zip,SSN])



extract_data()
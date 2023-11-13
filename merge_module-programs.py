import pandas as pd
import numpy as np
import os

print('loading in data...')
modules = pd.read_csv('Modules/modules.csv',delimiter=';',encoding='cp1252')
programmes = pd.read_csv('Modules/programmes.csv',delimiter=';',encoding='cp1252') #load in programmes dataframe
programme_relations = pd.read_csv('Modules/programmerelationship.csv',delimiter=';') #load in programme_relations dataframe
schools = pd.read_csv('Modules/schools.csv',delimiter=';')


#some dataset tidying. - for NLP we want  'Aims', 'OutlineOfSyllabus', 'IntendedKnowledgeOutcomes', 'IntendedSkillOutcomes'- ignore for now while we get relations
modules2023 = modules[modules['AcademicYear']==2023] #select only modules taught in 2023...
#filter modules to data we require
rel_columns = ['Module_Id', 'ModuleCode', 'Title', 'FheqLevel', 'SchoolCode']#, 'Aims', 'OutlineOfSyllabus', 'IntendedKnowledgeOutcomes', 'IntendedSkillOutcomes']
modules2023 = modules2023[rel_columns]
modules2023 = modules2023.rename(columns={'Module_Id':'ModuleId','Title':'ModuleTitle','SchoolCode':'ModuleSchoolCode'})

#remove un needed columns from programmes and programme relations
programmes = programmes.drop(columns=['SapObjectId','ProgrammeType_id','School_id'])
programmes = programmes.rename(columns={'Id':'ProgrammeId','Title':'ProgrammeTitle','Code':'ProgrammeCode'})
programme_relations = programme_relations.drop(columns=['Id','StageTo']) #drop ivvelivent columns
programme_relations = programme_relations.rename(columns={'Module_id':'ModuleId','Programme_id':'ProgrammeId','Title':'ProgrammeTitle','School_id':'SchoolId'})#rename column to match main dataframe...
schools = schools.drop(columns=['SapObjectId'])
schools = schools.rename(columns={'Id':'SchoolId','Faculty_id':'FacultyId','Code':'ProgrammeSchoolCode','Name':'ProgrammeSchoolName'})

#some data checking.
#make sure all ModuleCode follow the format LLLNNNN where LLL forms a 3 letter module name and NNNN is numberical code
import re #do this via regex
module_codes = modules2023['ModuleCode'].values
wrong = 0
for module_code in module_codes:
    if not re.match ('^[A-Z]{3}[0-9]{4}',module_code):
        wrong +=1
print('there are {} incorrectly formated module codes'.format(wrong))

#we will remove any modules with a SchoolCode of D-HSSO as these seem to be dummy modules for pre-registration.
before = len(modules2023)
modules2023 = modules2023[modules2023['ModuleSchoolCode']!='D-HSSO']
print('removed {} entries with module code D-HSSO'.format(before - len(modules2023)))


print('there are a total of {} modules <-> programme pairings in the modules <-> programme list from all years.'.format(programme_relations.shape[0]))

#merge the 2023 module and programme_relations datasets based on Module_Id
merged_dataset = pd.merge(modules2023,programme_relations,on='ModuleId',how='inner') #we loose about 2000 modules from this which have summaries, but dont appear in the programmes list...
print('there are a total of {} modules <-> programme pairings in the modules <-> programme taught in 2023.'.format(merged_dataset.shape[0]))


#merge the new dataset with the programs dataset to get matching programme codes aswell as School_id - which will alow us to match to schools.csv
merged_dataset = pd.merge(merged_dataset,programmes,on='ProgrammeId',how='inner')
print('there are a total of {} modules <-> programme pairings in the modules <-> programme taught in 2023 with a programme id present in programme_relations.csv'.format(merged_dataset.shape[0]))

#final merge with schools to get the name of the schools.
final_dataset = pd.merge(merged_dataset,schools,on='SchoolId',how='inner')
print('there are a total of {} modules <-> programme pairings in the modules <-> programme taught in 2023 with a programme school_id present in schools.csv'.format(merged_dataset.shape[0]))

final_dataset.to_csv('module_program_school_relations.csv',index=False)

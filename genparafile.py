#####
# In dit script moet code komen te staan die het volgende doet
# Als input neemt het een lijst/dict van de vorm:
# {"PARAMETER": [LOW, HIGH, STEP]} 
# Vervolgens maakt het een script run1.sh run2.sh etc
# Met elke runi.sh een run van een script met een parameter.
#####

import itertools
import numpy as np



def generate_files(FOLDER, input):
    parameters = list(input.keys())
    def general_structure_of_file():
        with open(f"{FOLDER}/template_job_file",'r') as file:
            out = file.readlines()
        return out
    
    
    def set_parameterfiles(data_folder,parameterfile):
        t=[ 
         f"DATADIR={data_folder}\n"
        ]
        data_folder="${DATADIRPATH}"+data_folder + '/'
        t.extend([
         f"echo \"datadir = {data_folder}\" >> {parameterfile}.par\n" ,
         f"echo \"ECM_write_path='{data_folder}'\" >> {parameterfile}.py\n",
         f"echo \"log_prefix='{data_folder}out_'\" >> {parameterfile}.py\n",
         f"echo \"parfile = '{parameterfile}.par'\" >> {parameterfile}.py\n",
        ])
        return t
        out=""
        for T in t:
            out+=T
            if T!=t[-1]:
                out+='\n'
        return out 
        
    
    def replace_line(line, name,par):
        if (line == "newtemplate"):
            return [f"newtemplate=para_{name}"]
        if (line == "DATADIR"):
            return set_parameterfiles(f"data-{name}", f"para_{name}")
        if (line == "TAR"):
            return [f"TAR=run{name}"]
        if (line == "PARAMETERS"):
            out =[]
            for i,p in enumerate(par):
                if parameters[i][:3] == 'par':
                    out.append(f"echo \"{parameters[i][3:]} = {p}\" >> " + "${newtemplate}.par\n")
                else:
                    out.append(f"echo \"{parameters[i]}={p}\" >> " + "${newtemplate}.py\n")
            return out
    
    ranges =[]
    for key in parameters:
        ranges.append(input[key]) 
    product = list(itertools.product(*ranges))
    
    jobs_file = []
    
    for par in product:
        print(par)
        FILE=general_structure_of_file()
        data_folder="$1/tst/data"
        unique_name = ""
        for i,p in enumerate(par):
            unique_name+= f"{parameters[i]}{p}"
        unique_name=unique_name.replace('.', '_')
        jobs_file.append(f"./sim{unique_name}.sh\n")
    #    print(unique_name)
    #    print(set_parameterfiles(data_folder+unique_name, unique_name))
        for i,line in enumerate(FILE):
            if line[0] == '!':
                FILE[i] = '\n' # replace ! with enter as we write to FILE and also read from it. smth smth inf loop...
                FILE[i:i] = replace_line(line[1:-1], unique_name, par)
        with open(f"{FOLDER}/sim{unique_name}.sh", 'w') as file:
            file.writelines(FILE)
    with open(f"{FOLDER}/jobs", 'w') as file:
        file.writelines(jobs_file)

if __name__ == '__main__':
    FOLDER = "."
    input={ 
    	"num_init_crosslinks": [500, 1000,1500, 2000, 3000],
    	"iteration": range(1),
    }
    generate_files(FOLDER, input)

import sys, tempfile, os
from subprocess import call
from distutils.dir_util import copy_tree
import editor


try:
    PATH_TO_FOLDER = sys.argv[1]
    COPY_FOLDER = sys.argv[2]
except:
    COPY_FOLDER = "empty_template_simulatie"
    PATH_TO_FOLDER = './'
if not os.path.isdir(PATH_TO_FOLDER + COPY_FOLDER):
    print(f"I cannot find {PATH_TO_FOLDER + COPY_FOLDER!r}. Exiting...")
    exit()

EDITOR = os.environ.get('EDITOR','vim') 

print(f"Selected {COPY_FOLDER!r} located at {PATH_TO_FOLDER!r} as base.")
name = input(f"Name of project: ")

def edit_file(filename, initial_message= "# WRITE FIXED PARAMETERS IN THIS FILE\n"):
    with open(f"{PATH_TO_FOLDER}{COPY_FOLDER}/{filename}") as f:
        initial_message += f.read()
    return editor.edit(contents=initial_message)
parameterfile = edit_file('template.py')
parameterfile_par = edit_file('template.par')
templatejobfile = edit_file('template_job_file', initial_message="# SKIM IF CORRECT\n")
jobfile =edit_file("job.slurm", initial_message='# SET RIGHT TIME AND COMPUTER \n')
#initial_message = "# WRITE FIXED PARAMETERS IN THIS FILE"
#with open(f"{PATH_TO_FOLDER}{COPY_FOLDER}/template.py") as f:
#    initial_message += f.read()
#parameterfile = editor.edit(contents=initial_message)
#initial_message = "# WRITE FIXED PARAMETERS IN THIS FILE"
#with open(f"{PATH_TO_FOLDER}{COPY_FOLDER}/template.par") as f:
#    initial_message += f.read()
#parameterfile_par = editor.edit(contents=initial_message)

print(f"Parameters that are for TST should start with 'par'. Changing lambda should be writen as parlambda")
parameters = input("Name parameters that you will be searcing (seperated by a ','):\n").split(',')
para_dict = {}
for parameter in parameters:
    values = input(f"Input parameters for '{parameter}' to test (seperated by a ','): ").split(',')
    para_dict[parameter] = values

print(f"We will created a folder {name} and generate simulation files according to this data {para_dict}")

yes_or_no = ''
while not(yes_or_no == 'y' or yes_or_no == 'n'):
    yes_or_no = input("Proceed (y/n)?")
if yes_or_no=='n':
    print("Goodbye!")
    exit()
print("Doing stuff")
copy_tree(f"{PATH_TO_FOLDER}{COPY_FOLDER}", f"{PATH_TO_FOLDER}{name}")
with open(f"{PATH_TO_FOLDER}{name}/template.py", 'bw') as f:
    f.write(parameterfile)
with open(f"{PATH_TO_FOLDER}{name}/template.par", 'bw') as f:
    f.write(parameterfile_par)
with open(f"{PATH_TO_FOLDER}{name}/template_job_file", 'bw') as f:
    f.write(templatejobfile)
with open(f"{PATH_TO_FOLDER}{name}/job.slurm", 'bw') as f:
    f.write(jobfile)
from genparafile import generate_files
generate_files(f"{PATH_TO_FOLDER}{name}", para_dict)
print("Done!")
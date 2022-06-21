import sys, tempfile, os
from subprocess import call
from distutils.dir_util import copy_tree
import editor
EDITOR = os.environ.get('EDITOR','vim') 

name = input(f"Name of project: ")

initial_message = "# WRITE FIXED PARAMETERS IN THIS FILE"
with open("./empty_template_simulatie/template.py") as f:
    initial_message += f.read()
parameterfile = editor.edit(contents=initial_message)
#with tempfile.NamedTemporaryFile(suffix='.tmp', mode='a') as tf:
#    tf.writelines(initial_message)
#    tf.flush()
#    call([EDITOR, tf.name])
#    tf.seek(0)
#    parameterfile = tf.read()


parameters = input("Name parameters that you will be searcing (seperated by a ','):\n").split(',')
para_dict = {}
for parameter in parameters:
    print(f"Parameters that are for TST should start with 'par'. Changing lambda should be writen as parlambda")
    values = input(f"Input parameters for '{parameter}' to test (seperated by a ','): ").split(',')
    para_dict[parameter] = values

print(f"We will created a folder {name} and generate simulation files according to this data {para_dict}")

yes_or_no = ''
while not(yes_or_no == 'y' or yes_or_no == 'n'):
    yes_or_no = input("Proceed (y/n)?")
if yes_or_no=='n':
    print("Exit")
    exit()
print("Doing stuff")
copy_tree(f"./empty_template_simulatie", f"./{name}")
with open(f"./{name}/template.py", 'bw') as f:
    f.write(parameterfile)
from genparafile import generate_files
generate_files(f"./{name}", para_dict)
print("Done!")
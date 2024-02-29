from generatesimulationstructure import SimulationGenerator, Parameters
from generatesimulationstructure.tst import rr_Alice_shell, gr_Alice_slurm
from pathlib import Path

sg = SimulationGenerator(Path(__file__).parent)

sg.add_template('par', "template.par")
sg.add_template('sh', "template.sh")
sg.add_template('slurm', "job.slurm")

sg.add_replacement_rule('sh', rr_Alice_shell())
sg.add_global_rule('slurm', gr_Alice_slurm())

import itertools
sg.parameters = list(itertools.product(Parameters("lambda", [1, 2, 4]).values, Parameters("it", list(range(3))).values))

sg.generate()

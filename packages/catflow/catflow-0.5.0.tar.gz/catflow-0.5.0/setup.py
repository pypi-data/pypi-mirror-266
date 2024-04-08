# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['catflow',
 'catflow.analyzer',
 'catflow.analyzer.atomic',
 'catflow.analyzer.graph',
 'catflow.analyzer.metad',
 'catflow.analyzer.structure',
 'catflow.analyzer.tesla',
 'catflow.analyzer.tesla.ai2_kit',
 'catflow.analyzer.tesla.base',
 'catflow.analyzer.tesla.dpgen',
 'catflow.cmdline',
 'catflow.cmdline.calculation',
 'catflow.cmdline.workflow',
 'catflow.tasker',
 'catflow.tasker.calculation',
 'catflow.tasker.code',
 'catflow.tasker.flows',
 'catflow.tasker.resources',
 'catflow.tasker.runner',
 'catflow.tasker.tasks',
 'catflow.tasker.tasks.defaults',
 'catflow.utils']

package_data = \
{'': ['*'], 'catflow.tasker': ['configs/workflow/*']}

install_requires = \
['ai2-kit>=0.9.0',
 'ase>=3.21.1,<4.0.0',
 'click',
 'dpdata',
 'dpdispatcher>=0.5.6,<0.6.0',
 'dpgen>=0.11.1,<0.12.0',
 'dscribe>=1.2.2,<2.0.0',
 'dynaconf',
 'fire>=0.5.0,<0.6.0',
 'h5py>=3.10.0,<4.0.0',
 'matplotlib>=3.7.1,<4.0.0',
 'mdanalysis>=2.2,<3.0',
 'numpy>=1.18,<1.24',
 'pandas>=1.3.3,<2.0.0',
 'pymatgen>=2023.5.10,<2024.0.0',
 'ruamel-yaml>=0.17.21,<0.18.0',
 'scipy>=1.10.1,<2.0.0',
 'seaborn>=0.12.2,<0.13.0']

entry_points = \
{'console_scripts': ['catflow = catflow.cmdline.base:main']}

setup_kwargs = {
    'name': 'catflow',
    'version': '0.5.0',
    'description': 'Analyzing tool for deep learning based chemical research.',
    'long_description': '# CatFlow\n\n> Parts of the code to be open source.\n\n[![Python package](https://github.com/Cloudac7/CatFlow/actions/workflows/ci.yml/badge.svg)](https://github.com/Cloudac7/CatFlow/actions/workflows/ci.yml)\n[![Coverage Status](https://coveralls.io/repos/github/Cloudac7/CatFlow/badge.svg?branch=master)](https://coveralls.io/github/Cloudac7/CatFlow?branch=master)\n\n\nMachine learning aided catalysis reaction free energy calculation and post-analysis workflow, thus, analyzer for catalysis.\n\nAs is known to all, cat is fluid and thus cat flows. 🐱\n\n> Former Miko-Analyzer and Miko-Tasker\n> This repository is a temporary branch of original CatFlow.\n> It would be merged into main repo after active refactor.\n\n## Analyzer\n\n### Installation\n\nTo install, clone the repository:\n\n```\ngit clone https://github.com/chenggroup/catflow.git\n```\n\nand then install with `pip`:\n\n```\ncd catflow\npip install .\n```\n\n### Acknowledgement\nThis project is inspired by and built upon the following projects:\n- [ai2-kit](https://github.com/chenggroup/ai2-kit): A toolkit featured artificial intelligence × ab initio for computational chemistry research.\n- [DP-GEN](https://github.com/deepmodeling/dpgen): A concurrent learning platform for the generation of reliable deep learning based potential energy models.\n- [ASE](https://wiki.fysik.dtu.dk/ase/): Atomic Simulation Environment.\n- [DPDispatcher](https://github.com/deepmodeling/dpdispatcher): Generate and submit HPC jobs.\n- [Metadynminer](https://github.com/spiwokv/metadynminer): Reading, analysis and visualization of metadynamics HILLS files produced by Plumed. As well as its Python implementation [Metadynminer.py](https://github.com/Jan8be/metadynminer.py).\n- [stringmethod](https://github.com/apallath/stringmethod): Python implementation of the string method to compute the minimum energy path.\n\n## Tasker\n\n### Potential of Mean Force Calculation\n\nA simple workflow designed for free energy calculation from Potential of Mean Force (PMF).\n\n### Usage\n\n#### Commandline\n\nFirst, prepare a yaml file for workflow settings in detial. For example, `config.yaml`.\n\n\n```yaml\njob_config:\n  work_path: "/some/place"\n  machine_name: "machine_name"\n  resources:\n    number_node: 1\n    cpu_per_node: 1\n    gpu_per_node: 1\n    queue_name: gpu\n    group_size: 1\n    module_list:\n      - ...\n    envs:\n      ...\n  command: "cp2k.ssmp -i input.inp"\n\n  reaction_pair: [0, 1] # select indexes of atoms who would be constrained\n  steps: 10000000 # MD steps\n  timestep: 0.5 # unit: fs\n  restart_steps: 10000000 # extra steps run in each restart\n  dump_freq: 100 # dump frequency\n  cell: [24.0, 24.0, 24.0] # set box size for initial structure\n  type_map: # should be unified with DeePMD potential\n    O: 0\n    Pt: 1\n  model_path: "/place/of/your/graph.pb"\n  backward_files:\n    - ...\n\nflow_config:\n  coordinates: ... # a list of coordinations to be constrained at\n  t_min: 300.0 # under limit of simulation temperature\n  cluster_component:\n    - Pt # select elements of cluster\n  lindemann_n_last_frames: 20000 # use last 20000 steps to judge convergence by calculate Lindemann index\n  init_artifact:\n    - coordinate: 1.4\n      structure_path: "/place/of/your/initial_structure.xyz"\n    - coordinate: 3.8\n      structure_path: "/place/of/your/initial_structure.cif"\njob_type: "dp_pmf" # dp_pmf when using DeePMD\n```\n\nThen, just type command like this:\n\n```bash\ncatflow tasker pmf config.yaml\n```\n\nAnd enjoy it!\n',
    'author': 'Cloudac7',
    'author_email': 'scottryuu@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/chenggroup/CatFlow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)

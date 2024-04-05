# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['centrex_trajectories']

package_data = \
{'': ['*'], 'centrex_trajectories': ['saved_data/*']}

install_requires = \
['joblib>=1.2.0,<2.0.0',
 'matplotlib>=3.6.2,<4.0.0',
 'numpy>=1.23.4,<2.0.0',
 'scipy>=1.9.3,<2.0.0']

setup_kwargs = {
    'name': 'centrex-trajectories',
    'version': '0.2.0',
    'description': '',
    'long_description': '[![Python versions on PyPI](https://img.shields.io/pypi/pyversions/centrex-trajectories.svg)](https://pypi.python.org/pypi/centrex-trajectories/)\n[![CeNTREX-TlF version on PyPI](https://img.shields.io/pypi/v/centrex-trajectories.svg "CeNTREX-TlF on PyPI")](https://pypi.python.org/pypi/centrex-trajectories/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n\n# CeNTREX-trajectories\nCode for simulating CeNTREX trajectories\n\n## Installation\nClone repo and install with `pip` or directly install from GitHub with:  \n```\npip install git+https://github.com/ograsdijk/CeNTREX-trajectories\n```\n\n## Sections\nThe beamline is split into sections specified with `Section`, which can be used as follows:\n```Python\nsections = [\n    fourK = Section(\n        name = "4K shield",\n        objects = [CircularAperture(x=0, y=0, z=5e-3)],\n        start = 0,\n        stop = 10e-2,\n        save_collisions = False,\n        propagation_type=PropagationType.ballistic,\n    )\n]\n```\nThis defines a section called `4K shield`, which runs from `z = 0 m -> 10e-2 m`. Collisions aren\'t\nsaved, the `propagation_type` is ballistic and it contains a single circular aperture centered around\nthe z axis with a radius of 5 mm.\n\n## Collision objects\nCurrently two type of apertures are defined for collisions:\n* `CircularAperture(x: float,y: float,r: float)`\n* `RectangularAperture(x: float,y: float,wx: float,wy: float)`\n\nCustom collision objects can be defined; apertures should inherit from `Aperture`, and each custom\ncollision object should have two functions:\n* `check_in_bounds(start: float, stop: float)` which returns a boolean specifying whether the object fully resides inside the section\n* `get_acceptance(coordinates: Coordinates)` which returns a boolean arrays specifiying which trajectories make it through the aperture\n\n## Propagation types\nThere is support for ballistic and ODE solver trajectories, which is specified on a per section basis through `Section.propagation_type`\n* `PropagationType.ballistic` assumes a constant velocity and constant gravitational acceleration\n* `PropagationType.ode` needs a defined force function in the section and uses `scipy.integrate.solve_ivp` to calculate the trajectory\n\n## Working example\n```Python\nimport numpy as np\nfrom centrex_trajectories import (\n    Coordinates,\n    Velocities,\n    Force,\n    PropagationType,\n    propagate_trajectories,\n    PropagationOptions,\n)\n\nfrom centrex_trajectories.beamline_objects import CircularAperture, Section\nfrom centrex_trajectories.particles import TlF\n\nin_to_m = 0.0254\n\nfourK = Section(\n    name="4K shield",\n    objects=[CircularAperture(x=0, y=0, z=1.75 * in_to_m, r=1 / 2 * in_to_m)],\n    start=0,\n    stop=2 * in_to_m,\n    save_collisions=False,\n    propagation_type=PropagationType.ballistic,\n)\nfourtyK = Section(\n    name="40K shield",\n    objects=[\n        CircularAperture(x=0, y=0, z=fourK.stop + 1.25 * in_to_m, r=1 / 2 * in_to_m)\n    ],\n    start=fourK.stop,\n    stop=fourK.stop + 1.5 * in_to_m,\n    save_collisions=False,\n    propagation_type=PropagationType.ballistic,\n)\nbbexit = Section(\n    name="Beamsource Exit",\n    objects=[CircularAperture(0, 0, fourtyK.stop + 2.5 * in_to_m, 2 * in_to_m)],\n    start=fourtyK.stop,\n    stop=fourtyK.stop + 3.25 * in_to_m,\n    save_collisions=False,\n    propagation_type=PropagationType.ballistic,\n)\n\nsections = [fourK, fourtyK, bbexit]\n\nn_trajectories = 100_000\ncoordinates_init = Coordinates(\n    x=np.random.randn(n_trajectories) * 1.5e-3,\n    y=np.random.randn(n_trajectories) * 1.5e-3,\n    z=np.zeros(n_trajectories),\n)\nvelocities_init = Velocities(\n    vx=np.random.randn(n_trajectories) * 39.4,\n    vy=np.random.randn(n_trajectories) * 39.4,\n    vz=np.random.randn(n_trajectories) * 16 + 184,\n)\n\noptions = PropagationOptions(n_cores=6, verbose=False)\ngravity = Force(0, -9.81, 0)\nparticle = TlF()\n\nsection_data, trajectories = propagate_trajectories(\n    sections,\n    coordinates_init,\n    velocities_init,\n    particle,\n    force=gravity,\n    options=options,\n)\n\n```',
    'author': 'ograsdijk',
    'author_email': 'o.grasdijk@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.10',
}


setup(**setup_kwargs)

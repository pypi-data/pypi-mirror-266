## PROBE (Python Repo)
<!--Platform for Real-time Optogenetic & Behavior Experiments-->
<!-- Line 0 Title... Working title is WeRDumb but something better would be nice-->
<!-- Line 1 Badges... PyPi, Downloads, Maintained, Coverage, Documentation -->
<!-- Line 2 Badges... Python Versions, PyPi Status, License, Contributors -->
![PyPI](https://img.shields.io/pypi/v/WeRDumb)
![PyPI - Downloads](https://img.shields.io/pypi/dm/WeRDumb)
![Maintenance](https://img.shields.io/maintenance/yes/2023)
[![Coverage Status](https://coveralls.io/repos/github/darikoneil/WeRDumb/badge.svg?branch=master)](https://coveralls.io/github/darikoneil/WeRDumb?branch=master)
[![Documentation Status](https://readthedocs.org/projects/WeRDumb/badge/?version=latest)](https://WeRDumb.readthedocs.io/en/latest/?badge=latest)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/WeRDumb?)
![PyPI - Status](https://img.shields.io/pypi/status/WeRDumb)
![GitHub](https://img.shields.io/github/license/darikoneil/WeRDumb)
[![Contributors](https://img.shields.io/github/contributors-anon/darikoneil/WeRDumb)](https://github.com/darikoneil/WeRDumb/graphs/contributors)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/darikoneil/WeRDumb/WeRDumb_lint_test_action.yml)

PROBE is an open-source software-hardware system for behavioral experiments in head-fixed rodents using a low-cost, modular experimental rig. The software is primarily written in python to allow easy distribution, use, and end-user modification with bits of C/C++ glued in for low-latency performance. An optional GUI is largely handled by your GPU to allow real-time streaming of ongoing behavior and data acquisition without disrupting your experiments. Currently PROBE is only supported on windows. Triggers dependent on neural activity require access to a raw-stream of imaging data. PROBE only offers native support for PrairieView at this time, but if you have a raw stream it should work. In constrast, software communication with spatial light modulators or hardware-triggered stimulation for optogenetic actions should be platform-independent.

More information on hardware implementation can be found here.

Integration Tests
Make sure to launch prairie_mock_server.exe if conducting integration tests with PrairieView. This is automatically launched if calling prairie_probe_test.exe but NOT any other testing application/suite including google tests

Software Reminders
These things aren't listed in TODOs
Remember to test on Prairie-1 Workstation-3. It has an old Xeon processer so it will be a good test of performance of single-thread performance on a slow processor.
Remember to double-check for potential race conditions.
Remember to refactor GUI aesthetic and import logo before pushing here from WRD repo
Remember to update badge links before ever making public--just placeholders from WRD repo. Figure out whether I need to do anything special for distribution of C++ lib, executables, & Node.js in a pypi package. Figure out whether anti-viruses will get grumpy from having an executable in a pypi package.

Hardware Reminders
The sucrose preference robotic spout-swapper has not been tested.
Try to test on a nicer NI-DAQ. Might be able to achieve higher best-case performance since they have hardware-timed digital I/O and I won't have to call those in-between analog-input callbacks.
Take a second look at the PCB scheme and see if I can simplify the connection from / to DAQ. I probably won't re-fabricate since I did that out-of-pocket, but some optimization there will make building much simpler/more flexible.

##### Development Statistics (PyCharm Repo)
~75,000 Lines
~75% Coverage
0 Linting Errors

##### Developmentn Statistics (CLion Repo)
~25,000 Lines
~20% Coverage
0 Linting Errors

##### Supported Pre-Configured Behaviors
|    Module     |           Task           |                 Description                 | Recipe | Pilot
|:-------------:|:------------------------:|:-------------------------------------------:|:------:|:----:|
| Disk or Wheel |        Locomotion        |       Hyperactivity & Motor Function        | x      | x    |
|               |     Acoustic Startle     |    Hearing, Habituation, & Sensitization    | x      | x    |
|               |   Pre-Pulse Inhibition   |             Sensorimotor Gating             | x      | x    |
|               |         Go No-Go         |               Learning & Memory             |        |      |
|  Linear Track |       Navigation         |               Learning & Memory             |        |      |
|    Burrow     |     Shelter Seeking      |                   Anxiety                   |        |      |
|               |    Sucrose Preference    |                  Anhedonia                  |        |      |
|               | Attentional Set-Shifting |           Behavioral Flexibility            |        |      |
|               |         Go No-Go         |              Learning & Memory              |        |      |
|               | Trace Fear Conditioning  |              Learning & Memory              |        |      |
|               |  Delay Fear Conditioning |              Learning & Memory              |        |      |
|               |  Instrumental Learning   |              Learning & Memory              |        |      |

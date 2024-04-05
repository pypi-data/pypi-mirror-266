# Data Reduction System of SPIAKID

This project contains the **Data Reduction System** (DRS) of **SPIAKID**.

The **SPIAKID** (SpectroPhotometric Imaging in Astronomy with Kinetic Inductance Detectors) project aims at designing, building and deploying on the sky a spectrophotometric imager based on Kinetic Inductance detectors. More information can be found on the [SPIAKID project homepage](https://www.observatoiredeparis.psl.eu/spiakid.html).

The SPIAKID DRS is composed by Python code. 

## User documentation

User documentation of the DRS can be found [here](https://spiakid.pages.obspm.fr/DRS/index.html).

## Instructions for DRS developers

Instructions and resources to guide the development of the DRS can be found in the [wiki pages](https://gitlab.obspm.fr/spiakid/DRS/-/wikis/home).

## Installation

Stable versions of SPIAKID DRS are packaged and distributed via **pip**. Before installing the SPIAKID DRS, create a virtual environment like:
```
pip install virtualenv # Install virtualenv
virtualenv venv_DRS # Create a virtual environment for the DRS
source venv_DRS/bin/activate # Activate the virtual environment for the DRS
```
then, install the SPIAKID DRS with pip:
```
pip install spiakid-drs
```
or, if **virtualenvwrapper** is already installed, you can use
```
mkvirtualenv -i spiakid-drs -p python3 DRS 
```
An other way to use DRS is in a Docker container. You can find indications [here](https://spiakid.pages.obspm.fr/DRS/usage.html#docker).

Latest version of DRS can be downloaded from this Gitlab with **git** command:
```
git clone https://gitlab.obspm.fr/spiakid/DRS.git
```
or

```
git clone git@gitlab.obspm.fr:spiakid/DRS.git
```
### Requirements
The SPIAKID DRS requires Python 3.8 or later.

### Example

You can find examples [here](https://spiakid.pages.obspm.fr/DRS/usage.html#example-1-mkid-feature-review).

## Authors
The DRS is developped by Pasquale Panuzzo, Sebastien Faes, ...


## Project status and roadmap
The DRS is in a prototyping stage



## Support



## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


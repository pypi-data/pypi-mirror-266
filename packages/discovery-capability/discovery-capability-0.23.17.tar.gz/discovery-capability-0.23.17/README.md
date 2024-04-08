# Project Hadron
## Overview

**Project Hadron** is an open-source application framework for in-memory preprocessing, where
data analysis, machine learning, and other data-intensive tasks require efficiency and speed.
With :Apache Arrow as its canonical, and a more directed use of pandas,
**Project Hadron** offers effective data management, extensive interoperability, improved memory
management and hardware optimization.

At its concept, **Project Hadron** was conceived with a desire to improve the availability of
objective relevant data, increase the transparency and traceability of data lineage and facilitate
knowledge transfer, retrieval and reuse.

At its core **Project Hadron** is a selection of capabilities that
represent an encapsulated set of actions that act upon a given set of features or dataset. An
example of this would be FeatureSelection, a capability class, encapsulating cleaning data by
removing uninformative columns.

For the complete documentation [read-the-docs](https://discovery-capability.readthedocs.io/en/latest/)

## Installation

### Python version
We recommend using the latest version of Python. Project Hadron supports Python 3.8 and newer.

### Package installation
The best way to install the component packages is directly from the 
[Python Package Index](https://pip.pypa.io/en/stable/) using pip.

The component package is discovery-capability and pip installed with:

```bash
pip install discovery-capability
```


if you want to upgrade your current version then using pip install upgrade with:

```bash
pip install -U discovery-capability
```

This will also install or update dependent third party packages. The dependencies are limited to
Python, PyArrow and related Data manipulation tooling such as Pandas, Numpy, scipy, scikit-learn
and visual packages matplotlib and seaborn, and thus have a limited footprint and non-disruptive
installation in a data processing environment.

## Next Steps
For next steps [read-the-docs](https://discovery-capability.readthedocs.io/en/latest/)

## License
Distributed under the MIT License. See `LICENSE.txt` for more information or reference
[MIT](https://choosealicense.com/licenses/mit/)

## Contributing

Contributions are what make the open source community such an amazing place to learn, 
inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a 
pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

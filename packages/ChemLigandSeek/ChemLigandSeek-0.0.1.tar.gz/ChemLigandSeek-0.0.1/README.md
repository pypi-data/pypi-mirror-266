ChemoBiolysis Python Package
Overview
ChemoBiolysis is a versatile Python package designed for chemical and biological analysis. Whether you are conducting Quantitative Structure-Property Relationship (QSPR) analysis, exploring molecular structures, or performing virtual screening, this package provides a comprehensive set of tools to meet your needs.

Features
QSPR Analysis
Perform QSPR analysis on CSV files.
Calculate molecular descriptors.
Save results and obtain a model summary.
Chemical Assay Exploration
Display active and inactive chemicals based on Assay ID.
Retrieve compound CIDs and sample SIDs by Assay ID.
Molecular Structure Analysis
Perform virtual screening on a file with specified SMILES strings.
Display the maximum common substructure of a list of molecular structures.
Identify and display chiral centers in molecular structures.
Explore bond types, stereochemistry, and more.
Structure Comparison and Visualization
Highlight the differences between two molecular structures.
Draw a list of SMILES representations.
Display Gasteiger charges for a list of molecular structures.
Substructure Analysis
Mark atoms matching a given substructure represented by SMILES.
Check if a substructure is present in a list of compounds.
Delete a specified substructure from a list of compounds.
Installation
bash
Copy code
pip install chemobolysis
Usage
python
Copy code
import chemobolysis

# Example: QSPR Analysis
chemobolysis.qspr_analysis("path/to/csv_file.csv", "dependent_variable_column")

# Example: Virtual Screening
chemobolysis.virtual_screening("path/to/file.txt", "SMILES1", "SMILES2", ...)

# Example: Highlight Difference
chemobolysis.highlight_difference("mol1", "mol2")
For detailed documentation and examples, refer to the ChemoBiolysis Documentation.

Contribution
Contributions are welcome! If you encounter any issues or have suggestions for improvement, please open an issue or submit a pull request.

License
This project is licensed under the MIT License.







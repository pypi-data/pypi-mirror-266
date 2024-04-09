transformapy: A Toolkit for Identifying Transformation Product Structures of Emerging Contaminants Using HRMS Data
==================================================================================================================

transformapy is a Python toolkit engineered to process molecular structures, pinpointing potential transformation products of specified compounds by leveraging observed monoisotopic masses.

Contributor: Rui Wang
=====================

First release date: Feb.28.2024

Update
======

April.09.2024: transformapy 0.0.4

1. **Updated `remove_2H` Function**: Modifications have been made to improve the performance and accuracy of the `remove_2H` function.
2. **New Helper Functions**: Added `check_bad_valance_Hidx` and `remove_additional_H` functions, which are now utilized internally by `remove_2H` to enhance its functionality.
3. **Added `add_missing_H` Function**: Introduced a new function to automatically add missing hydrogen atoms to molecules to correct their valency.
4. **Enhanced `reaction_type` Checks**: Integrated the `add_missing_H` and `remove_additional_H` functions into the `reaction_type` function to ensure molecule structures are correctly adjusted during reactions.
5. **Introduced `stepwise_reaction` Function**: A new function to facilitate the stepwise application of reaction steps on a target molecule, allowing more detailed control over complex reaction pathways.
6. **Improvements to `generate_possible_TP_structures`**: Significant updates have been made to this function to optimize the generation of possible transformation product structures based on modified chemical reaction processes.


Dependencies
============

transformapy requires the following major dependencies:

- rdkit
- pyhrms

Features
========

transformapy provides the following functions:

- Identifying Transformation Product Structures of Emerging Contaminants Using HRMS Data

Paper Published Utilizing transformapy
=======================================

- Preparing

Licensing
=========

The package is open source and can be utilized under the MIT license. Please find the detail in the license file.

transformapy Documentation
===========================

**Getting Started with transformapy**

.. code-block:: python

    from transformapy.transformapy import *

**Project Structure:**

.. code-block:: none

    transformapy/
    |- from_mass_to_formula
    |- generate_possible_TP_structures
       |- modify_chemical_formula
       |- generate_fragments
       |- calculate_formula_differences
       |- combine_two_frags
       |- calculate_changed_num
          |- parse_formula
       |- stepwise_reaction
          |- reaction_type
             |- combine_fragments_and_generate_smiles
             |- replace_dummies_with_hydrogens
             |- replace_hydrogen_with_substituent
             |- split_molecule_at_bond
             |- Remove_2H
                |- is_atom_in_double_bond
                |- add_or_modify_bond
                |- has_hydrogen_count
             |- Add_2H
             |- remove_additional_H
                |- check_bad_valance_Hidx
             |- add_missing_H
    |- remove_explicit_hydrogens
    |- draw_molecule_with_atom_indices
    |- GetIdxOfDummy
    |- adjust_valence_by_removing_hydrogen

Acknowledgment
==============

During the development of this package, Liu Huangrui from the South China Institute of Environmental Science offered essential support by conducting comprehensive tests on its functionality.

Note
====

Please note that the documentation is currently a work in progress, and there is more content that is being written. I apologize for any inconvenience this may cause, but rest assured that I am continually updating the documentation to provide you with the most comprehensive guide to using transformapy.

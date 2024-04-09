from rdkit import Chem
from rdkit.Chem import AllChem, Draw, rdchem, rdmolops
import numpy as np
import pandas as pd
from rdkit.Chem.rdMolDescriptors import CalcMolFormula
from rdkit.Chem.Descriptors import ExactMolWt
from collections import defaultdict
import itertools
import re
from rdkit.Chem.Draw import rdMolDraw2D
from IPython.display import SVG
import rdkit
from pyhrms.pyhrms import *


def add_missing_H(mol):
    """
    Adds missing hydrogen atoms to the first encountered under-saturated carbon (C), nitrogen (N),
    or oxygen (O) atom in a given molecule. This function is designed to ensure that these atoms reach
    their typical valency: C (up to 4), N (up to 3), and O (up to 2).

    Parameters:
    - mol (Chem.Mol): The RDKit molecule object that will be modified. This molecule should be in a format
                      that allows for valency checks and modifications.

    Returns:
    - Chem.Mol: The molecule with hydrogens added to the first found under-saturated atom of type C, N, or O.
                Hydrogens are added only to the first such atom encountered that needs them to reach standard valency.

    This function processes the input molecule by initially adding explicit hydrogens to all atoms. It then checks
    each atom's type and current valency. If it finds an atom that is under-saturated (C, N, or O), it converts the
    molecule to an editable format, adds a hydrogen atom, and forms a single bond. This modification stops after
    correcting the first such atom found. Finally, it converts all hydrogens back to the implicit representation.
    """

    mol = Chem.AddHs(mol)
    for atom in mol.GetAtoms():

        if (atom.GetSymbol() == 'C' and atom.GetExplicitValence() < 4):
            mol = Chem.EditableMol(mol)
            h_idx = mol.AddAtom(Chem.Atom(1))
            mol.AddBond(atom.GetIdx(), h_idx, Chem.BondType.SINGLE)
            mol = mol.GetMol()
            break
        if (atom.GetSymbol() == 'N' and atom.GetExplicitValence() < 3):
            mol = Chem.EditableMol(mol)
            h_idx = mol.AddAtom(Chem.Atom(1))
            mol.AddBond(atom.GetIdx(), h_idx, Chem.BondType.SINGLE)
            mol = mol.GetMol()
            break
        if (atom.GetSymbol() == 'O' and atom.GetExplicitValence() < 2):
            mol = Chem.EditableMol(mol)
            h_idx = mol.AddAtom(Chem.Atom(1))
            mol.AddBond(atom.GetIdx(), h_idx, Chem.BondType.SINGLE)
            mol = mol.GetMol()
            break

    mol = Chem.RemoveHs(mol)
    return mol


def check_bad_valance_Hidx(test1):
    """
    Adds missing hydrogen atoms to under-saturated carbon (C), nitrogen (N), or oxygen (O) atoms in a molecule.
    This function first adds explicit hydrogen atoms to all potential sites, then specifically targets the first
    under-saturated C, N, or O found and manually adjusts their hydrogen count to satisfy typical valency rules:
    C (valency up to 4), N (up to 3), O (up to 2).

    Parameters:
    - mol (Chem.Mol): An RDKit molecule object that potentially has under-saturated atoms.

    Returns:
    - Chem.Mol: The modified molecule with added hydrogen atoms, ensuring that the valency rules are met for C, N, and O.

    The function modifies the molecule by adding hydrogen atoms to reach the standard valency and then reverts to
    implicit hydrogen representation. It will stop and return after modifying the first eligible atom found.
    """
    H_idx = []
    for atom in test1.GetAtoms():
        if atom.GetSymbol() == 'C':
            if atom.GetExplicitValence() > 4:
                for bond in atom.GetBonds():
                    if bond.GetOtherAtom(atom).GetSymbol() == 'H':
                        H_idx.append(bond.GetOtherAtom(atom).GetIdx())
                        break
    for atom in test1.GetAtoms():
        if atom.GetSymbol() == 'N':
            if atom.GetExplicitValence() > 3:
                for bond in atom.GetBonds():
                    if bond.GetOtherAtom(atom).GetSymbol() == 'H':
                        H_idx.append(bond.GetOtherAtom(atom).GetIdx())
                        break
    for atom in test1.GetAtoms():
        if atom.GetSymbol() == 'O':
            if atom.GetExplicitValence() > 2:
                for bond in atom.GetBonds():
                    if bond.GetOtherAtom(atom).GetSymbol() == 'H':
                        H_idx.append(bond.GetOtherAtom(atom).GetIdx())
                        break
    return H_idx


# Check the valence
def remove_additional_H(modified_mol):
    """
    Removes two hydrogen atoms from a molecule where a single bond has been transformed into a double bond.
    This function identifies hydrogen atoms that are incorrectly maintaining single bonds where double bonds
    should exist due to a previous modification. It removes these hydrogen atoms to correct the molecular structure.

    Parameters:
    - modified_mol (Chem.Mol): An RDKit molecule object potentially containing incorrect single bonds due
                               to improperly placed hydrogen atoms after a structural modification.

    Returns:
    - Chem.Mol: The modified molecule with excess hydrogens removed and the molecular structure corrected to
                accurately reflect the intended valency and bonding.

    The function first adds explicit hydrogens to identify any incorrectly bonded hydrogen atoms. It then iteratively
    removes these atoms, one at a time, until the structure adheres to proper valency rules. The molecule is sanitized
    to update its chemical properties after the removals.
    """
    test1 = Chem.AddHs(modified_mol)
    bad_Hidx = check_bad_valance_Hidx(test1)
    if len(bad_Hidx) == 0:
        test1 = modified_mol
    else:
        test1 = Chem.EditableMol(test1)  # 转换成可以编辑的结构
        test1.RemoveAtom(bad_Hidx[0])
        test1 = test1.GetMol()  # 重新获得新的结构
        bad_Hidx = check_bad_valance_Hidx(test1)  # 重新查找bad H idx
        test1 = Chem.EditableMol(test1)
        test1.RemoveAtom(bad_Hidx[-1])
        test1 = test1.GetMol()  # 重新获得新的结构
        test1 = Chem.RemoveHs(test1)
        Chem.SanitizeMol(test1, Chem.SanitizeFlags.SANITIZE_PROPERTIES)

    return test1


def stepwise_reaction(target_mol, rxn_s1):
    """
    Performs a series of chemical reactions on a given molecule step-by-step, based on specified reaction types and counts.

    Args:
        target_mol (mol object): The molecule object that is subjected to the reactions.
        rxn_s1 (dict): Dictionary mapping reaction types (keys) to their respective counts (values).
            Positive counts indicate forward reactions, and negative counts indicate reverse reactions.

    Returns:
        list: A list of molecule objects that represent the potential outcomes after applying all specified reactions stepwise.

    The function executes each reaction as specified in 'rxn_s1', starting from 'target_mol'. If the sequence of reactions is longer than three steps, a prompt is printed to simplify the reactions or break them into manageable steps.
    """
    final_tps = []
    # 1. 先把有多少步反应讲清楚
    dict1 = rxn_s1
    keys_list = []
    values_list = []
    for key, value in dict1.items():
        if value > 0:
            keys_list.extend([key] * value)
            values_list.extend([1] * value)
        elif value < 0:
            keys_list.extend([key] * abs(value))
            values_list.extend([-1] * abs(value))

    # 2. 再一步步进行解析
    if len(keys_list) >= 1:
        tps1 = reaction_type(target_mol, rxn_type=keys_list[0], num=values_list[0])
        if len(keys_list) == 1:
            final_tps.extend(tps1)  # 如果只有一步就直接extend了
        else:
            # 继续第二步
            tps2 = []
            for tp1 in tps1:
                tps2_ = reaction_type(tp1, rxn_type=keys_list[1], num=values_list[1])  # 第二步了，所以都是【1】
                tps2.extend(tps2_)
            # 判断是不是只有两步
            if len(keys_list) == 2:
                final_tps.extend(tps2)
            else:
                # 继续第三步
                tps3 = []
                for tp2 in tps2:
                    tp3_ = reaction_type(tp2, rxn_type=keys_list[2], num=values_list[2])
                    tps3.extend(tp3_)
                if len(keys_list) == 3:
                    final_tps.extend(tps3)
                else:
                    print('Please simplify the reaction or break it down into multiple steps.')
    return final_tps


def generate_possible_TP_structures(parent_mol, TP_formula, mode='pos'):
    """
    Generates possible transformation product (TP) structures by modifying a parent molecule
    based on a target transformation product formula and reaction mode.

    This function identifies potential sites for modification in the parent molecule, applies
    chemical transformations based on the specified target TP formula, and considers the reaction
    mode (positive or negative ion mode) to adjust the molecular structure accordingly. The goal
    is to explore plausible structural changes that align with the target TP formula, generating
    a set of potential TP structures.

    Parameters:
    - parent_mol (Chem.Mol): The RDKit molecule object representing the parent molecule.
    - TP_formula (str): The chemical formula of the target transformation product.
    - mode (str, optional): The ionization mode, either 'pos' for positive or 'neg' for negative.
      Default is 'pos'. This affects how the molecular structure is adjusted to match the target
      TP formula.

    Returns:
    - list of Chem.Mol: A list of RDKit molecule objects representing potential TP structures
      that match the target TP formula.

    Steps:
    1. Identify atoms in the parent molecule that have hydrogen atoms available for substitution.
    2. Adjust the target TP formula based on the reaction mode to account for ionization effects.
    3. Compare the parent molecule's formula with the target TP formula to identify differences.
    4. Fragment the parent molecule and evaluate each fragment for potential modifications.
    5. Generate a series of reaction types based on the identified differences and apply these
       to the parent molecule or its fragments to generate potential TP structures.

    Note:
    - The function assumes that the parent molecule and the target TP formula represent chemically
      valid structures.
    - The generated TP structures are theoretical and may require further validation to ensure
      their chemical plausibility.
    """

    formula = CalcMolFormula(parent_mol)

    possible_TPs = {}
    # Step 0. 看看哪些原子上有H，这样可以取代
    atoms_with_H = []
    for atom in parent_mol.GetAtoms():
        if has_hydrogen_count(atom):
            atoms_with_H.append(atom.GetIdx())

    # step 1. 根据正负离子模式转化成中性分子
    if mode == 'pos':
        TP_formula = modify_chemical_formula(TP_formula, '-H')
    if mode == 'neg':
        TP_formula = modify_chemical_formula(TP_formula, '+H')

    # step 2. 对比一下和母体结构差异
    structures_dict = {}  # 创建一个新的字典
    reduced_part, added_part = calculate_formula_differences(formula, TP_formula)
    num = calculate_changed_num(reduced_part, added_part)
    structures_dict[parent_mol] = num

    # Step 3. 打碎分子并存储
    frags = generate_fragments(parent_mol)
    frags = [replace_dummies_with_hydrogens(frag) for frag in frags]
    frag_smis = list(set([Chem.MolToSmiles(frag) for frag in frags]))
    frags1 = [Chem.MolFromSmiles(frag_smi) for frag_smi in frag_smis]

    # Step 3.1 补充那些两两组合的
    frags = generate_fragments(parent_mol)
    pairs = list(itertools.combinations(list(np.arange(len(frags))), 2))
    for pair in tqdm(pairs, desc='Combine different frags'):
        mol1 = frags[pair[0]]
        mol2 = frags[pair[1]]
        new_mol = combine_two_frags(mol1, mol2)
        frags1.append(new_mol)

    # Step 4. 计算分子式总的改变个数,确定在哪个碎片上进行加工 (要重新写，考虑同样分子式的情况)

    for frag in tqdm(frags1, desc='Finding the most relavent structure'):
        frag_formula = CalcMolFormula(frag)
        reduced_part, added_part = calculate_formula_differences(frag_formula, TP_formula)
        frag_total_num = calculate_changed_num(reduced_part, added_part)
        structures_dict[frag] = frag_total_num

    # Step 5. 将要修改的parent/frag与TP的分子式对比，生成series
    sub_rxn = ['NH', 'O', 'CH2', 'H-1NO2', 'H2', 'H-1Cl', 'H-1Br', 'H-1F', 'H-1I']
    s = pd.Series(structures_dict).sort_values()
    s1 = s[s == s.min()]
    target_mols = list(s1.index)
    # 去除重复的
    target_mols_smi = list(set([Chem.MolToSmiles(i) for i in target_mols]))
    target_mols = [Chem.MolFromSmiles(i) for i in target_mols_smi]
    for target_mol in target_mols:
        print(f'First Step TP: {Chem.MolToSmiles(target_mol)}')
        print(f'----------------------------------------------')
        frag_formula = CalcMolFormula(target_mol)
        reduced_part, added_part = calculate_formula_differences(frag_formula, TP_formula)
        print(f'reduced_part:{reduced_part}, added_part:{added_part}')
        s1 = pd.Series(parse_formula(reduced_part), dtype=object) * -1
        s2 = pd.Series(parse_formula(added_part), dtype=object)
        change_s = pd.concat([s1, s2])
        if len(change_s) == 0:  # 说明和碎片相同
            possible_TPs[target_mol] = 'Frag'
        else:
            # 开始处理每个元素
            atoms = ['C', 'H', 'O', 'N', 'Cl', 'Br', 'F', 'I']
            atoms_not_present = [i for i in atoms if i not in change_s.index]
            unpresent_s = pd.Series(np.zeros(len(atoms_not_present)).astype(int), atoms_not_present)
            change_s1 = pd.concat([change_s, unpresent_s])
            # 确定范围
            ranges = [range(min([0, change_s1['N']]), max([0, change_s1['N']]) + 1),
                      range(min([0, change_s1['O']]), max([0, change_s1['O']]) + 1),
                      range(min([0, change_s1['C']]), max([0, change_s1['C']]) + 1),
                      range(min([0, change_s1['N']]), max([0, change_s1['N']]) + 1),
                      range(-5, 5),
                      range(min([0, change_s1['Cl']]), max([0, change_s1['Cl']]) + 1),
                      range(min([0, change_s1['Br']]), max([0, change_s1['Br']]) + 1),
                      range(min([0, change_s1['F']]), max([0, change_s1['F']]) + 1),
                      range(min([0, change_s1['I']]), max([0, change_s1['I']]) + 1)]
            patterns_list = list(itertools.product(*ranges))
            # 开始做匹配
            rxn_s = None
            for pattern in patterns_list:
                a, b, c, d, e, f, g, h, i = pattern  # a*NH, b*O, c*CH2, d*H-1NO2, e*H2, f*H-1Cl, g*H-1Br, h*H-1F, i*H-1I
                N_num = a + d  # a
                O_num = b + 2 * d  # b
                C_num = c  # c
                Cl_num = f
                Br_num = g
                F_num = h
                I_num = i
                H_num = a + 2 * c - d + 2 * e - f - g - h - i
                if (N_num == change_s1['N']) & (O_num == change_s1['O']) & (C_num == change_s1['C']) & (
                        Cl_num == change_s1['Cl']) & (Br_num == change_s1['Br']) & (F_num == change_s1['F']) & (
                        I_num == change_s1['I']) & (H_num == change_s1['H']):
                    rxn_s = pd.Series([a, b, c, d, e, f, g, h, i], sub_rxn)
                    # 开始处理该分子
                    rxn_s1 = rxn_s[rxn_s != 0]  # 去掉那些没有用的
                    rxn_s1 = pd.concat([rxn_s1[['H2']], rxn_s1.drop('H2')]) if 'H2' in rxn_s1.index else rxn_s1
                    rxn_s1_dict = rxn_s1.to_dict()
                    print(rxn_s1_dict)
                    # 先关注第一步的结构
                    print(Chem.MolToSmiles(target_mol))
                    possible_tp_list = stepwise_reaction(target_mol, rxn_s1)

                    for rxn_tp in possible_tp_list:
                        possible_TPs[rxn_tp] = str(rxn_s1_dict)

        print(f'===============================================')
    tp_list = [k for k, v in possible_TPs.items()]
    tp_list = [i for i in tp_list if CalcMolFormula(i) == TP_formula]  # 去掉不符合formula的
    tp_smiles = list(set([Chem.MolToSmiles(i) for i in tp_list]))  # 去重
    tp_list = [Chem.MolFromSmiles(i) for i in tp_smiles]
    return tp_list


def from_mass_to_formula(parent_mol, observed_mz, mode, iso_info, ms_error=10, iso_score=0.7, addition_element={}):
    """
    Convert an observed mass to a chemical formula based on a parent molecule and additional criteria.

    Args:
        parent_mol (Mol): The parent molecule (RDKit Mol object) from which to derive the formula.
        observed_mz (float): The observed mass/charge (m/z) ratio.
        mode (str): The ionization mode, either 'pos' for positive or 'neg' for negative.
        iso_info (dict): Isotope information used for scoring isotope patterns.
        ms_error (float, optional): The mass spectrometry error tolerance (default is 10 ppm).
        iso_score (float, optional): The minimum isotope score to consider a formula reasonable (default is 0.7).
        addition_element (dict, optional): Additional elements to consider in the formula calculation. Keys are element symbols
            and values are the maximum number of atoms allowed for each element (default is an empty dict).

    Returns:
        DataFrame: A pandas DataFrame containing the possible formulas, sorted by the number of changes and
        the number of elements involved in the change. Additional columns include:
        - 'formula': Possible molecular formula.
        - 'reasonable': Boolean indicating if the formula is reasonable based on isotope pattern scoring.
        - 'formula_neutral': The neutral molecular formula after adjusting for ionization mode.
        - 'added part': Elements added to the parent molecule to get the possible formula.
        - 'reduced part': Elements removed from the parent molecule to get the possible formula.
        - 'Changed Num': The number of atoms changed (added or removed) to get the possible formula.
        - 'element Num': The number of distinct elements involved in the change.
        - 'iso_score': The isotope pattern score for the formula.

    This function calculates possible chemical formulas based on an observed m/z value and a parent molecule. It takes
    into account the ionization mode, additional elements to consider, and isotope information for scoring. The function
    adjusts formulas for ionization, evaluates their reasonableness based on isotope patterns, and identifies changes
    relative to the parent molecule.
    """
    # 获得基础信息
    parent_formula = CalcMolFormula(parent_mol)
    formula_dict = parse_formula(parent_formula)
    atoms = [k for k, v in formula_dict.items()] + [k for k, v in addition_element.items()]
    mz_difference = ExactMolWt(parent_mol) - observed_mz  # 看看差别了多少

    # 获得检索的元素和数量范围
    max_C = int(observed_mz / 14)  # 考虑CnH2n+2
    min_C = int(observed_mz / 100)  # 考虑C-I
    atom_n = []
    for k, v in formula_dict.items():
        if k == 'C':
            atom_n.append([min_C, max_C])
        elif k == 'H':
            atom_n.append([max(min_C * 2 + 2, v - 20), v + 20])
        elif k == 'N':
            atom_n.append([max(0, v - 10), v + 5])
        elif k == 'O':
            atom_n.append([max(0, v - 10), v + 10])
        elif k == 'P':
            atom_n.append([max(0, v - 5), v + 2])
        elif k == 'S':
            atom_n.append([max(0, v - 5), v + 2])
        else:
            atom_n.append([0, v])
    atom_n = atom_n + [[0, v] for k, v in addition_element.items()]
    # 获得所有可能的分子式
    result = formula_prediction(observed_mz, mode, atoms, atom_n)
    result['reasonable'] = result['formula'].apply(is_valid_formula)  # 看看哪些分子式合理
    result1 = result[result['reasonable'] == True].reset_index(drop=True)

    # 对pos和neg下的分子式进行修改
    result1['formula_neutral'] = result1['formula'].apply(modify_chemical_formula,
                                                          args=['-H'] if mode == 'pos' else ['+H'])

    # 看看这些合理的分子式相对于母体的变化
    for i in range(len(result1)):
        formula = result1.loc[i, 'formula_neutral']
        reduced_part, added_part = calculate_formula_differences(parent_formula, formula)
        result1.loc[i, 'added part'] = added_part
        result1.loc[i, 'reduced part'] = reduced_part
        result1.loc[i, 'Changed Num'] = int(calculate_changed_num(added_part, reduced_part))
        result1.loc[i, 'element Num'] = len(parse_formula(added_part)) + len(parse_formula(reduced_part))
        if isinstance(iso_info, dict):
            iso_score = isotope_score(iso_info, formula, mode=mode)
            result1.loc[i, 'iso_score'] = iso_score

    result1['Changed Num'] = result1['Changed Num'].astype(int)
    result1['element Num'] = result1['element Num'].astype(int)
    result2 = result1.sort_values(by=['Changed Num', 'element Num']).reset_index(drop=True)
    return result2


def is_valid_formula(formula):
    """
    Determines if a given chemical formula is valid based on specific elemental ratios and counts.

    This function checks if the provided formula adheres to common organic chemistry rules regarding the relative
    quantities of certain elements (C, H, N, O, P, S, F, Cl, Br, I) to carbon. The criteria used for validation are:
    - The sum of P, S, N, O, H, I, Br, Cl, F counts should not exceed the count of carbon atoms.
    - Carbon should have enough hydrogen bonds (2C + 2) to cover the halogens and nitrogen present.
    - The nitrogen count should not be more than 1.3 times the carbon count.
    - The oxygen count should not exceed 1.2 times the carbon count.
    - The sulfur count should be less than or equal to 0.8 times the carbon count.
    - The phosphorus count should be less than or equal to 0.3 times the carbon count.

    Args:
        formula (str): The chemical formula to be evaluated.

    Returns:
        bool: True if the formula is considered valid, False otherwise.

    The function parses the formula to count each element's occurrences and applies the validation rules to determine
    if the formula could represent a plausible organic molecule.
    """

    element_counts = parse_formula(formula)
    # 计算C数量
    C_count = element_counts['C']
    # 计算各个元素的数量
    F_count = element_counts['F'] if 'F' in [k for k, v in element_counts.items()] else 0
    Cl_count = element_counts['Cl'] if 'Cl' in [k for k, v in element_counts.items()] else 0
    Br_count = element_counts['Br'] if 'Br' in [k for k, v in element_counts.items()] else 0
    I_count = element_counts['I'] if 'I' in [k for k, v in element_counts.items()] else 0

    H_count = element_counts['H'] if 'H' in [k for k, v in element_counts.items()] else 0
    O_count = element_counts['O'] if 'O' in [k for k, v in element_counts.items()] else 0
    N_count = element_counts['N'] if 'N' in [k for k, v in element_counts.items()] else 0
    S_count = element_counts['S'] if 'S' in [k for k, v in element_counts.items()] else 0
    P_count = element_counts['P'] if 'P' in [k for k, v in element_counts.items()] else 0

    if (P_count + S_count + N_count + O_count + H_count + I_count + Br_count + Cl_count + F_count > C_count) & (
            2 * C_count + 2 >= I_count + Br_count + Cl_count + F_count + H_count + N_count) & (
            N_count <= 1.3 * C_count) & (O_count <= 1.2 * C_count) & (
            S_count <= 0.8 * C_count) & (P_count <= 0.3 * C_count):
        return True
    else:
        return False


def combine_two_frags(frag1, frag2):
    """
    Combines two molecular fragments into a single molecule by creating a bond between dummy atoms.

    This function takes two molecular fragments, each possibly containing dummy atoms (atoms with atomic number 0),
    and combines them into a single molecule. It specifically looks for dummy atoms in the combined molecule,
    assumes these dummy atoms are meant to represent points of connection, and replaces them with a single bond
    between the atoms adjacent to the original dummy atoms. Finally, it removes the dummy atoms from the molecule.

    Args:
        frag1 (Mol): The first fragment, an RDKit Mol object.
        frag2 (Mol): The second fragment, an RDKit Mol object.

    Returns:
        Mol: A new RDKit Mol object representing the combined molecule after connecting the fragments and removing
        the dummy atoms.

    The function is particularly useful in cheminformatics workflows involving the construction of complex molecules
    from simpler components, such as in synthetic chemistry and drug discovery applications.

    Note: The function currently assumes that there are exactly two dummy atoms, one in each fragment, and that
    these are the atoms to be connected. Adjustments may be necessary for different scenarios.
    """
    # Combine the molecules
    combined_mol = rdmolops.CombineMols(frag1, frag2)

    # Create an editable molecule for further modifications
    emol = Chem.EditableMol(combined_mol)
    dummy_atoms = []
    # Identify all dummy atoms
    for atom in combined_mol.GetAtoms():
        if atom.GetAtomicNum() == 0:
            dummy_atoms.append(atom)
    target_atoms_idx = []
    # Find neighbors of dummy atoms to connect
    for dummy_atom in dummy_atoms:
        target_atom = dummy_atom.GetNeighbors()[0]
        target_atoms_idx.append(target_atom.GetIdx())
    # Connect the target atoms with a single bond
    emol.AddBond(target_atoms_idx[0], target_atoms_idx[1], order=Chem.rdchem.BondType.SINGLE)
    new_mol = emol.GetMol()  # Intermediate molecule with dummy atoms still present

    # Remove all dummy atoms
    target_dummy_idx = [atom.GetIdx() for atom in new_mol.GetAtoms() if atom.GetAtomicNum() == 0]
    target_dummy_idx.sort(reverse=True)  # Remove from highest index to avoid reindexing issues
    for idx in target_dummy_idx:
        emol.RemoveAtom(idx)
    new_mol = emol.GetMol()  # Final molecule without dummy atoms

    return new_mol


def adjust_valence_by_removing_hydrogen(mol, target_atom_symbol):
    """
    Adjusts the valence of specified atoms within a molecule by removing a hydrogen atom if the atom's valence is not in the acceptable range.

    This function iterates over the atoms of a given molecule. If an atom of the specified type has a valence that is not within the defined valid range for its element, the function attempts to remove one hydrogen atom bonded to it. This adjustment is done to bring the atom's valence within a reasonable range according to common valency rules.

    Args:
        mol (Chem.Mol): The RDKit molecule object from which the atom's valence will be checked and adjusted.
        target_atom_symbol (str): The symbol of the atom (e.g., 'C', 'N', 'O') whose valence needs to be checked and potentially adjusted.

    Returns:
        Chem.Mol: An RDKit molecule object after the valence adjustment process. Hydrogen atoms may have been removed to correct the valence of specified atom types.

    Note:
        This function modifies the input molecule by potentially removing hydrogen atoms to correct valences. The valid valences for common elements are predefined within the function.
    """
    reasonable = True
    emol = Chem.RWMol(mol)
    valid_valence = {'C': [4], 'N': [3], 'O': [2], 'F': [1], 'Cl': [1], 'Br': [1], 'I': [1], 'P': [5], 'S': [2, 6]}
    for k, v in valid_valence.items():
        if target_atom_symbol == k:
            for atom in emol.GetAtoms():
                if (atom.GetSymbol() == k) and (atom.GetExplicitValence() not in v):
                    for bond in atom.GetBonds():
                        if bond.GetOtherAtom(atom).GetSymbol() == 'H':
                            atom1_idx = bond.GetBeginAtomIdx()
                            atom2_idx = bond.GetEndAtomIdx()
                            H_idx = atom1_idx if emol.GetAtomWithIdx(atom1_idx).GetSymbol() == 'H' else atom2_idx

                            emol.RemoveBond(atom1_idx, atom2_idx)
                            emol.RemoveAtom(H_idx)
                            break
                    break
    return emol.GetMol()


def generate_fragments(mol):
    """
    Generates molecular fragments by breaking each single bond in the molecule.

    This function iterates over all the bonds in a given molecule and, for each single bond,
    creates a new set of fragments by breaking that bond. The process is repeated for all single
    bonds, and the resulting fragments are collected. Each fragment is treated as a separate molecule.

    Parameters:
    - mol (Chem.Mol): The RDKit molecule object from which to generate fragments.

    Returns:
    - list of Chem.Mol: A list containing the molecular fragments as individual molecule objects.
      Each fragment corresponds to a molecule generated by breaking a single bond in the original molecule.

    Note:
    - Only single bonds are considered for fragmentation in this implementation, for simplicity.
    - The original molecule is not modified; instead, a copy is made for each fragmentation process.

    Example:
    >>> mol = Chem.MolFromSmiles('CCO')
    >>> fragments = generate_fragments(mol)
    >>> len(fragments)
    2
    >>> [Chem.MolToSmiles(frag) for frag in fragments]
    ['[CH3].[CH2]O', '[CH3].[OH]']

    The example shows the generation of fragments from ethanol ('CCO'). Breaking each of the single bonds
    results in two sets of fragments: one for breaking the C-C bond and another for the C-O bond.
    """
    fragments = []
    for bond in mol.GetBonds():
        # Only consider single bonds for simplicity
        if bond.GetBondType() == rdchem.BondType.SINGLE:
            # Create a copy of the molecule for each bond breakage
            fragmented_mol = Chem.FragmentOnBonds(mol, [bond.GetIdx()])
            # Convert fragments into separate molecules
            frags = Chem.GetMolFrags(fragmented_mol, asMols=True)
            fragments.extend(frags)
    return fragments


def split_molecule_at_bond(mol, bond_index):
    """
    Splits a molecule at a specified bond, resulting in two separate molecule objects.

    This function identifies and breaks a specified bond within a molecule, effectively
    dividing the molecule into two distinct fragments. These fragments are then returned
    as a list of molecule objects, each representing a separate piece of the original molecule.

    Parameters:
    - mol (Chem.Mol): An RDKit molecule object representing the original molecule.
    - bond_index (int): The index of the bond to be broken.

    Returns:
    - list of Chem.Mol: A list containing the two molecule objects derived from the original molecule
      after the specified bond has been broken.

    Note:
    The bond index is based on the internal enumeration of bonds within the RDKit molecule object,
    starting from 0. Ensure the specified bond_index corresponds to the correct bond intended for splitting.
    """
    # Create an editable copy of the molecule
    emol = Chem.EditableMol(mol)

    # Remove the specified bond
    bond = mol.GetBondWithIdx(bond_index)
    emol.RemoveBond(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())

    # Obtain the modified molecule
    modified_mol = emol.GetMol()

    # Use GetMolFrags to find connected components, returning them as separate molecule objects
    frags = Chem.GetMolFrags(modified_mol, asMols=True)

    return frags


def is_atom_in_double_bond(atom):
    """
    Determines whether the specified atom is part of a double bond.

    This function iterates through all bonds associated with the given atom
    and checks if any of these bonds are double bonds. It returns True if at least
    one double bond is found, indicating that the atom is indeed part of a double bond.

    Parameters:
    - atom (Chem.Atom): An RDKit Atom object to be evaluated.

    Returns:
    - bool: True if the atom is part of a double bond, False otherwise.

    Example:
    >>> mol = Chem.MolFromSmiles('C=C')
    >>> atom = mol.GetAtomWithIdx(0)  # Get the first atom (Carbon)
    >>> is_atom_in_double_bond(atom)
    True
    """
    for bond in atom.GetBonds():
        if bond.GetBondType() == Chem.rdchem.BondType.DOUBLE:
            return True
    return False


def add_or_modify_bond(editable_mol, atom_idx1, atom_idx2, bond_type):
    """
    Adds a new bond between two atoms in an editable molecule or modifies an existing bond.

    This function first checks if there is an existing bond between the two specified atoms.
    If an existing bond is found, it is removed. Then, a new bond of the specified type is added
    between the two atoms. This operation is performed on an editable molecule, which allows for
    direct modification of the molecule's structure.

    Parameters:
    - editable_mol (Chem.EditableMol): The editable molecule to which the bond will be added or modified.
    - atom_idx1 (int): The index of the first atom in the bond.
    - atom_idx2 (int): The index of the second atom in the bond.
    - bond_type (Chem.rdchem.BondType): The type of the bond to be added. This should be one of the
      bond types available in RDKit, such as Chem.rdchem.BondType.SINGLE or Chem.rdchem.BondType.DOUBLE.

    Note:
    - The molecule must be converted to an editable molecule (Chem.EditableMol) before using this function.
    - The atom indices and bond type must be valid, or an error may occur during the modification process.

    Example:
    >>> mol = Chem.MolFromSmiles("CC")
    >>> editable_mol = Chem.EditableMol(mol)
    >>> add_or_modify_bond(editable_mol, 0, 1, Chem.rdchem.BondType.DOUBLE)
    >>> modified_mol = editable_mol.GetMol()
    >>> Chem.MolToSmiles(modified_mol)
    'C=C'
    """
    # Check if bond exists
    existing_bond = editable_mol.GetMol().GetBondBetweenAtoms(atom_idx1, atom_idx2)
    if existing_bond is not None:
        # Remove the existing bond
        editable_mol.RemoveBond(atom_idx1, atom_idx2)

    # Add the new bond
    editable_mol.AddBond(atom_idx1, atom_idx2, bond_type)


def has_hydrogen_count(atom):
    """
    Determines if an atom has any associated hydrogen atoms, either explicit or implicit.

    This function calculates the total number of hydrogen atoms connected to a given atom
    by summing up both explicit and implicit hydrogen counts. Explicit hydrogens are those
    represented as separate atoms in the molecular structure, while implicit hydrogens are
    not individually represented but are implied by the valency and bonding of the atom.

    Parameters:
    - atom (Chem.Atom): The RDKit Atom object to be evaluated.

    Returns:
    - bool: True if the atom is associated with one or more hydrogen atoms (either explicit or implicit),
      False otherwise.

    Example:
    >>> mol = Chem.MolFromSmiles("CC")
    >>> atom = mol.GetAtomWithIdx(0)  # Get the first carbon atom
    >>> has_hydrogen_count(atom)
    True

    Note:
    The function returns True even if only implicit hydrogens are present, reflecting the
    atom's potential to form bonds with hydrogen atoms not explicitly shown in the structure.
    """
    # Get explicit hydrogen count (if hydrogens are explicitly represented in the structure)
    explicit_h_count = atom.GetNumExplicitHs()

    # Get implicit hydrogen count (hydrogens not explicitly represented but implied)
    implicit_h_count = atom.GetNumImplicitHs()

    return explicit_h_count + implicit_h_count > 0


def replace_dummies_with_hydrogens(mol):
    """
    Replaces all dummy atoms in a molecule with hydrogen atoms.

    This function scans a molecule for dummy atoms (atoms with an atomic number of 0) and replaces
    each one with a hydrogen atom. The replacement involves removing the dummy atom and adding a new
    hydrogen atom that is connected to the former dummy atom's neighbors with a single bond.

    Parameters:
    - mol (Chem.Mol): The RDKit molecule object to be processed.

    Returns:
    - Chem.Mol: A new molecule object with all dummy atoms replaced by hydrogen atoms.

    Note:
    - The function makes a copy of the original molecule to avoid modifying it directly.
    - If a dummy atom has multiple neighbors, a hydrogen atom will be added and connected to each neighbor.
    - The molecule is sanitized after the replacement to ensure its chemical validity.

    Example:
    >>> mol = Chem.MolFromSmiles('[*]C')
    >>> new_mol = replace_dummies_with_hydrogens(mol)
    >>> Chem.MolToSmiles(new_mol)
    'C'

    In this example, a molecule with a dummy atom connected to a carbon atom is processed. The dummy atom
    is replaced with a hydrogen atom, resulting in methane ('C').
    """
    # Make a copy of the molecule
    new_mol = Chem.RWMol(mol)

    # Find dummy atoms (atoms with atomic number 0)
    dummy_atoms = [atom.GetIdx() for atom in new_mol.GetAtoms() if atom.GetAtomicNum() == 0]

    # For each dummy atom, find the atom it's connected to,
    # remove the dummy atom, and add a hydrogen atom connected to that atom.
    for idx in sorted(dummy_atoms, reverse=True):  # Reverse to avoid index shifting
        # Find neighbors of the dummy atom
        atom_neighbors = new_mol.GetAtomWithIdx(idx).GetNeighbors()

        # Remove the dummy atom
        new_mol.RemoveAtom(idx)

        for neighbor in atom_neighbors:
            # Add a hydrogen atom
            h_idx = new_mol.AddAtom(Chem.Atom(1))

            # Connect the hydrogen atom to the neighbor
            new_mol.AddBond(neighbor.GetIdx(), h_idx, Chem.BondType.SINGLE)

    # Update molecule properties
    Chem.SanitizeMol(new_mol)
    return new_mol.GetMol()


def parse_formula(formula):
    """
    Parses a chemical formula string and returns a dictionary of elements and their counts.

    This function uses a regular expression to identify all elements within the formula,
    along with their respective counts. Elements are identified by their standard chemical
    symbols (one uppercase letter followed by zero or more lowercase letters), and counts
    are indicated by the numbers following each element symbol. If an element symbol is not
    followed by a number, its count is assumed to be 1.

    Parameters:
    - formula (str): A string representing the chemical formula to be parsed.

    Returns:
    - dict: A dictionary where keys are element symbols (str) and values are the counts (int)
      of those elements in the formula.

    Example:
    >>> parse_formula('H2O')
    {'H': 2, 'O': 1}
    >>> parse_formula('C6H12O6')
    {'C': 6, 'H': 12, 'O': 6}

    Note:
    - The function assumes that the input formula is correctly formatted. Incorrect or
      unconventional formula representations may lead to unexpected results or errors.
    """
    # Use a regular expression to find all elements and their counts
    # The pattern looks for sequences of an uppercase letter followed by lowercase letters (element symbols)
    # followed optionally by a number (count). The count is optional to match elements with a single atom.
    pattern = r'([A-Z][a-z]*)(\d*)'
    matches = re.findall(pattern, formula)

    result = {}
    for element, count in matches:
        # If count is empty, it means the element count is 1
        if count == '':
            count = 1
        else:
            count = int(count)
        result[element] = count

    return result


def calculate_changed_num(reduced_part, added_part):
    """
    Calculates the total change in atom count between the reduced and added parts of a reaction.

    This function computes the total number of atoms involved in the transformation process
    of a chemical reaction, considering both the reduced part and the added part. It uses
    the `parse_formula` function to convert chemical formulas into dictionaries of elements
    and their counts, then sums the absolute values of atom counts in both parts to determine
    the total change.

    Parameters:
    - reduced_part (str): A string representing the chemical formula of the reduced part of the reaction.
    - added_part (str): A string representing the chemical formula of the added part of the reaction.

    Returns:
    - int: The total number of atoms involved in the change, calculated as the sum of absolute values
      of atom counts from both the reduced and added parts.

    Example:
    >>> calculate_changed_num('H2', 'O2')
    4
    >>> calculate_changed_num('CO2', 'C6H12O6')
    24

    Note:
    - The function assumes that the input formulas are correctly formatted according to chemical
      notation standards. Incorrect or unconventional formula representations may lead to unexpected
      results or errors.
    - The function is designed to work with simple molecular formulas and does not account for
      more complex structures or stoichiometry beyond basic composition.
    """
    reduced_part_dict = parse_formula(reduced_part)
    added_part_dict = parse_formula(added_part)
    total_num = abs(sum([v for k, v in reduced_part_dict.items()])) + abs(sum([v for k, v in added_part_dict.items()]))
    return total_num


def calculate_formula_differences(formula1, formula2):
    """
    Calculates the elemental differences between two chemical formulas.

    This function compares two chemical formulas and determines the excess elements
    in each formula relative to the other. It effectively parses each formula into
    a dictionary of element counts, computes the difference in counts for each element,
    and then constructs new formulas representing the excess elements in each original formula.

    Parameters:
    - formula1 (str): The first chemical formula as a string.
    - formula2 (str): The second chemical formula as a string.

    Returns:
    - reduced_part, added_part

    Example:
    >>> calculate_formula_differences('H2O', 'H2O2')
    ('', 'O')
    >>> calculate_formula_differences('C6H12O6', 'C6H6')
    ('H6O6', '')

    Note:
    - The function assumes that the input formulas are correctly formatted according to standard
      chemical notation. Incorrect or unconventional formula representations may lead to unexpected
      results.
    - Elements with a count of 1 in the excess formulas are represented without a number (e.g., 'H'
      instead of 'H1').
    """

    def parse_formula(formula):
        """Parse chemical formula into a dict of element counts."""
        return {element: int(count) if count else 1 for element, count in re.findall('([A-Z][a-z]*)(\\d*)', formula)}

    counts1 = parse_formula(formula1)
    counts2 = parse_formula(formula2)

    excess_in_formula1 = defaultdict(int)
    excess_in_formula2 = defaultdict(int)

    for element in set(counts1) | set(counts2):  # Union of elements in both formulas
        diff = counts1.get(element, 0) - counts2.get(element, 0)
        if diff > 0:
            excess_in_formula1[element] = diff
        elif diff < 0:
            excess_in_formula2[element] = -diff  # Make the difference positive

    # Construct and return the difference formulas
    reduced_part = ''.join(
        f"{element}{excess_in_formula1[element] if excess_in_formula1[element] > 1 else ''}" for element in
        sorted(excess_in_formula1))
    added_part = ''.join(
        f"{element}{excess_in_formula2[element] if excess_in_formula2[element] > 1 else ''}" for element in
        sorted(excess_in_formula2))

    return reduced_part, added_part


def modify_chemical_formula(formula, modification):
    """
    Modifies a chemical formula based on a specified modification command.

    This function takes a chemical formula and a modification command (to add or remove elements)
    and applies the modification to produce a new chemical formula. The modification command must
    be in the format of '+ElementCount' to add or '-ElementCount' to remove elements, where 'Element'
    is the chemical symbol of the element and 'Count' is the number of atoms to be added or removed.

    Parameters:
    - formula (str): The original chemical formula to be modified.
    - modification (str): The modification command, starting with '+' or '-' followed by the element
      symbol and an optional count. If no count is specified, 1 is assumed.

    Returns:
    - str: The modified chemical formula.

    Raises:
    - ValueError: If the modification command is not in the correct format or if the modification
      attempts to remove more of an element than is present in the original formula.

    Example:
    >>> modify_chemical_formula('H2O', '+H2')
    'H4O'
    >>> modify_chemical_formula('C6H12O6', '-H2O')
    'C6H10O5'
    >>> modify_chemical_formula('C6H6', '-C7')
    ValueError: Cannot subtract 7 of C from formula; not enough present.

    Note:
    - The function does not validate the chemical correctness of the resulting formula.
    - Elements in the returned formula are sorted alphabetically.
    """
    # Parse the original formula into a dictionary of element counts
    element_counts = defaultdict(int)
    for element, count in re.findall(r'([A-Z][a-z]*)(\d*)', formula):
        element_counts[element] += int(count) if count else 1

    # Attempt to parse the modification command
    match = re.match(r'([+-])([A-Z][a-z]*)(\d*)', modification)
    if not match:
        raise ValueError(f"Modification '{modification}' is not in the correct format.")

    mod_action, mod_element, mod_count = match.groups()
    mod_count = int(mod_count) if mod_count else 1  # Default to 1 if no count is specified

    # Apply the modification
    if mod_action == '+':
        element_counts[mod_element] += mod_count
    elif mod_action == '-':
        if element_counts[mod_element] >= mod_count:
            element_counts[mod_element] -= mod_count
            if element_counts[mod_element] == 0:
                del element_counts[mod_element]  # Remove the element if its count drops to 0
        else:
            raise ValueError(f"Cannot subtract {mod_count} of {mod_element} from formula; not enough present.")

    # Construct and return the modified formula
    return ''.join(f"{element}{count if count > 1 else ''}" for element, count in sorted(element_counts.items()))


def Remove_2H(mol):
    """
    Removes two hydrogen atoms from a molecule and generates possible structures by forming new bonds.

    This function explores two main strategies to modify the input molecule:
    1. Converting single bonds between two atoms, each having at least one hydrogen, into double bonds.
    2. Connecting two atoms that are not currently bonded but each has at least one hydrogen atom.

    The function ensures that the modifications do not result in unreasonable structures, such as those
    violating basic chemical valency rules or creating overly strained rings.

    Parameters:
    - mol (Chem.Mol): The RDKit molecule object to be modified.

    Returns:
    - list of Chem.Mol: A list of RDKit molecule objects representing reasonable structures after
      removing two hydrogen atoms and making the corresponding modifications.

    Note:
    - The function assumes that the input molecule is fully saturated (i.e., all atoms are bonded
      in a way that satisfies their valency with single bonds and implicit hydrogens).
    - The resulting molecules are checked for chemical reasonableness, particularly regarding ring
      strain and valency rules.
    - This function does not guarantee the preservation of stereochemistry in the generated structures.
    """
    # Step1: 先找到所有可能的Smiles
    new_smis = []
    # 检查单健是否可以改成双健
    bonds = []
    for bond in mol.GetBonds():
        bonds.append(bond)
        if bond.GetBondType() == Chem.BondType.SINGLE:
            idx1 = bond.GetBeginAtomIdx()
            idx2 = bond.GetEndAtomIdx()
            atom1 = mol.GetAtomWithIdx(idx1)
            atom2 = mol.GetAtomWithIdx(idx2)
            # 如果两个原子上都有H原子，就可以相连
            if (has_hydrogen_count(atom1) & has_hydrogen_count(atom2) & (not is_atom_in_double_bond(atom1)) & (
                    not is_atom_in_double_bond(atom2))):
                editable_mol = Chem.EditableMol(mol)
                add_or_modify_bond(editable_mol, idx1, idx2, Chem.BondType.DOUBLE)
                modified_mol = editable_mol.GetMol()
                modified_mol = remove_additional_H(modified_mol)  # 去掉多余的H
                Chem.SanitizeMol(modified_mol, Chem.SanitizeFlags.SANITIZE_PROPERTIES)
                modified_smi = Chem.MolToSmiles(modified_mol)
                new_smis.append(modified_smi)

    # 检查两两是否可以相连
    ring_info = mol.GetRingInfo()
    atoms_to_connect = []
    for atom in mol.GetAtoms():
        if has_hydrogen_count(atom):
            atoms_to_connect.append(atom.GetIdx())

    combinations = list(itertools.combinations(atoms_to_connect, 2))
    bond_atoms_idx = [tuple(sorted((bond.GetBeginAtom().GetIdx(), bond.GetEndAtom().GetIdx()))) for bond in bonds]
    possible_connections = [i for i in combinations if i not in bond_atoms_idx]

    possible_connections1 = []
    for pair in possible_connections:
        atom_idx1 = pair[0]  # 第一个原子的索引
        atom_idx2 = pair[1]  # 第二个原子的索引
        if any(atom_idx1 in ring and atom_idx2 in ring for ring in ring_info.AtomRings()):
            pass
        else:
            possible_connections1.append(pair)

    for pair in possible_connections1:
        try:
            editable_mol = Chem.EditableMol(mol)
            add_or_modify_bond(editable_mol, pair[0], pair[1], Chem.BondType.SINGLE)
            # Convert back to a regular molecule
            modified_mol = editable_mol.GetMol()
            modified_mol = remove_additional_H(modified_mol)
            Chem.SanitizeMol(modified_mol, Chem.SanitizeFlags.SANITIZE_PROPERTIES)
            modified_smi = Chem.MolToSmiles(modified_mol)
            new_smis.append(modified_smi)
        except Exception as e:
            print(f"Error with pair {pair}: {e}")

    # Step 2: 判断smiles是否合理
    mols = [Chem.MolFromSmiles(i) for i in set(new_smis)]

    reasonable_mols = []
    for mol1 in mols:
        ring_info = mol1.GetRingInfo()
        reasonable = True
        ring_num = []
        for ring in ring_info.AtomRings():
            ring_num.append(np.array(ring))
        if len(ring_num) > 1:
            compare_num = [i for i in itertools.combinations(np.arange(len(ring_num)), 2)]
            ring_intersect_info = []
            for compare in compare_num:
                num_intersect = np.intersect1d(ring_num[compare[0]], ring_num[compare[1]])
                ring_intersect_info.append([len(ring_num[compare[0]]), len(ring_num[compare[1]]), len(num_intersect)])
            compare_info = pd.DataFrame(ring_intersect_info, columns=['ring1', 'ring2', 'common'])
            if len(compare_info[compare_info['common'] >= 3]) > 0:
                reasonable = False
            else:
                compare_info1 = compare_info[(compare_info['ring1'] == 3) | (compare_info['ring2'] == 3)]
                if len(compare_info1) > 0:
                    if len(compare_info1[compare_info1['common'] >= 2]) > 0:
                        reasonable = False
        else:
            pass

        if reasonable:
            reasonable_mols.append(mol1)
    return reasonable_mols


def Add_2H(mol):
    """
    Adds two hydrogen atoms to a molecule by modifying existing bonds.

    This function explores two strategies for adding hydrogens to the molecule:
    1. Converting double bonds to single bonds, effectively adding two hydrogens to the involved atoms.
    2. Removing single bonds within rings, which implicitly adds hydrogens to maintain valency.

    The modifications aim to generate plausible molecular structures by ensuring that each atom's valency
    is satisfied without violating basic chemical principles.

    Parameters:
    - mol (Chem.Mol): The RDKit molecule object to be modified.

    Returns:
    - list of Chem.Mol: A list of RDKit molecule objects representing possible structures after adding
      two hydrogen atoms through the specified modifications.

    Note:
    - The function attempts to modify the molecule in a chemically reasonable manner, but the resulting
      structures should be evaluated for their plausibility in the specific chemical context.
    - Modifications that involve changing bond types or removing bonds are made conservatively to avoid
      creating chemically unreasonable structures.
    - This function does not explicitly add hydrogen atoms; instead, it modifies the molecular structure
      in a way that the addition of hydrogens is implied to satisfy valency requirements.
    """
    new_smis = []
    # Check if double bonds can be converted to single bonds
    for bond in mol.GetBonds():
        if bond.GetBondType() == Chem.BondType.DOUBLE:
            idx1, idx2 = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
            # Modify the bond
            editable_mol = Chem.EditableMol(mol)
            add_or_modify_bond(editable_mol, idx1, idx2, Chem.BondType.SINGLE)
            modified_mol = editable_mol.GetMol()
            Chem.SanitizeMol(modified_mol, Chem.SanitizeFlags.SANITIZE_PROPERTIES)
            modified_smi = Chem.MolToSmiles(modified_mol)
            new_smis.append(modified_smi)
        elif bond.GetBondType() == Chem.BondType.SINGLE and bond.IsInRing():
            # Create an editable copy of the molecule
            emol = Chem.EditableMol(mol)
            # Remove the bond
            emol.RemoveBond(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())
            modified_mol = emol.GetMol()
            Chem.SanitizeMol(modified_mol, Chem.SanitizeFlags.SANITIZE_PROPERTIES)
            modified_smi = Chem.MolToSmiles(modified_mol)
            new_smis.append(modified_smi)

    mols = [Chem.MolFromSmiles(i) for i in new_smis]
    return mols


def recursive_reaction(target_mols, rxn_s1, current_step=0, possible_TPs=[]):
    """
    Recursively apply reaction steps to generate possible transformation products (TPs).

    Parameters:
    - target_mols: List of starting molecule(s) for the current step.
    - rxn_s1: DataFrame or similar structure with reaction types and their counts.
    - current_step: The current step index in the reaction sequence.
    - possible_TPs: Accumulator for possible transformation products across all steps.

    Returns:
    - A list of possible transformation products after applying all reaction steps.
    """
    # Base case: If the current step equals the number of steps, return the accumulated TPs.
    if current_step == len(rxn_s1.index):
        return possible_TPs

    # Get the reaction type for the current step.
    rxn_type = rxn_s1.index[current_step]

    # Initialize a container for TPs generated in this step.
    new_TPs = []

    # Apply the reaction to each target molecule.
    for mol in target_mols:
        step_TPs = reaction_type(mol, rxn_type=rxn_type, num=rxn_s1[rxn_type])
        new_TPs.extend(step_TPs)

    # If this is the last step, add the new TPs to the possible_TPs list.
    if current_step == len(rxn_s1.index) - 1:
        possible_TPs.extend(new_TPs)
    else:
        # Otherwise, proceed to the next step with the new TPs.
        return recursive_reaction(new_TPs, rxn_s1, current_step + 1, possible_TPs)

    return possible_TPs


def reaction_type(mol, rxn_type='H2', num=-1):
    """
    Generates possible transformation products (TPs) of a molecule based on specified reaction types.

    This function identifies and applies specific types of chemical modifications to a given molecule,
    such as adding or removing functional groups (e.g., halogens, nitro groups) or changing bond types.
    The modifications are determined by the reaction type specified and can result in multiple potential
    transformation products.

    Parameters:
    - mol (Chem.Mol): The RDKit molecule object to be modified.
    - rxn_type (str): A string indicating the type of reaction to apply. Supported types include 'H2',
      'H-1Br', 'H-1Cl', 'H-1F', 'H-1I', 'H-1NO2', 'O', 'CH2', and 'NH'. The prefix 'H-1' indicates the
      removal of a hydrogen atom along with the addition of the specified group.
    - num (int): Indicates whether to add (+num) or remove (-num) the specified group. A positive value
      adds the group, while a negative value removes it.

    Returns:
    - list of Chem.Mol: A list of RDKit molecule objects representing the possible transformation products
      after applying the specified reaction type.

    Note:
    - The function is designed to handle a variety of simple substitution and addition reactions. It may not
      accurately predict the outcome of more complex reactions involving significant rearrangements or
      reactions that are not purely additive or subtractive in nature.
    - The resulting molecules are not guaranteed to be chemically viable or stable; they represent
      theoretical outcomes based on the specified reaction type.
    """
    C_F = []
    C_Cl = []
    C_Br = []
    C_I = []
    C_CH2 = []
    C_NH = []
    C_NO2 = []
    C_O = []
    for bond in mol.GetBonds():
        bond_type = bond.GetBondType()
        atom1 = bond.GetBeginAtom()
        atom2 = bond.GetEndAtom()
        neighbors1 = atom1.GetNeighbors()
        neighbors2 = atom2.GetNeighbors()
        if (bond_type == rdkit.Chem.rdchem.BondType.SINGLE) & ((atom1.GetSymbol() == 'F') | (atom2.GetSymbol() == 'F')):
            C_F.append(bond)
        if (bond_type == rdkit.Chem.rdchem.BondType.SINGLE) & (
                (atom1.GetSymbol() == 'Cl') | (atom2.GetSymbol() == 'Cl')):
            C_Cl.append(bond)
        if (bond_type == rdkit.Chem.rdchem.BondType.SINGLE) & (
                (atom1.GetSymbol() == 'Br') | (atom2.GetSymbol() == 'Br')):
            C_Br.append(bond)
        if (bond_type == rdkit.Chem.rdchem.BondType.SINGLE) & ((atom1.GetSymbol() == 'I') | (atom2.GetSymbol() == 'I')):
            C_I.append(bond)
        if (bond_type == rdkit.Chem.rdchem.BondType.SINGLE):
            if ((atom1.GetSymbol() == 'C') & (atom2.GetSymbol() == 'C')):  # C-CH3
                if (len([i.GetSymbol() for i in neighbors1]) == 1) | (len([i.GetSymbol() for i in neighbors2]) == 1):
                    C_CH2.append(bond)
            if ({atom1.GetSymbol(), atom2.GetSymbol()} == {'C', 'N'}):  # C-NH2
                if (len([i.GetSymbol() for i in neighbors1]) == 1) | (len([i.GetSymbol() for i in neighbors2]) == 1):
                    C_NH.append(bond)
                n_atom = atom1 if atom1.GetSymbol() == 'N' else atom2
                neighbors = n_atom.GetNeighbors()
                # 初始化计数器
                count_C = 0
                count_O = 0
                # 遍历邻居原子，计数C和O原子的数量
                for neighbor in neighbors:
                    if neighbor.GetSymbol() == 'C':
                        count_C += 1
                    elif neighbor.GetSymbol() == 'O':
                        count_O += 1
                # 检查是否满足条件：一个C和两个O
                if count_C == 1 and count_O == 2:
                    C_NO2.append(bond)
            if ({atom1.GetSymbol(), atom2.GetSymbol()} == {'C', 'O'}):
                if (len([i.GetSymbol() for i in neighbors1]) == 1) | (len([i.GetSymbol() for i in neighbors2]) == 1):
                    C_O.append(bond)
    # 用来接收结构
    possible_TPs = []
    # 看看哪些原子有H
    atoms_with_H = []
    for atom in mol.GetAtoms():
        if has_hydrogen_count(atom):
            atoms_with_H.append(atom.GetIdx())

    # 开始处理结构
    if rxn_type == 'H2':
        if num > 0:
            mols = Add_2H(mol)
        else:
            mols = Remove_2H(mol)
        possible_TPs.extend(mols)

    if num > 0:
        if rxn_type == 'H-1Br':
            for idx in atoms_with_H:
                modified_mol = replace_hydrogen_with_substituent(mol, idx, 'Br')
                possible_TPs.append(modified_mol)
        if rxn_type == 'H-1Cl':
            for idx in atoms_with_H:
                modified_mol = replace_hydrogen_with_substituent(mol, idx, 'Cl')
                possible_TPs.append(modified_mol)
        if rxn_type == 'H-1F':
            for idx in atoms_with_H:
                modified_mol = replace_hydrogen_with_substituent(mol, idx, 'F')
                possible_TPs.append(modified_mol)
        if rxn_type == 'H-1I':
            for idx in atoms_with_H:
                modified_mol = replace_hydrogen_with_substituent(mol, idx, 'I')
                possible_TPs.append(modified_mol)
        if rxn_type == 'H-1NO2':
            for idx in atoms_with_H:
                modified_mol = Chem.MolFromSmiles(
                    combine_fragments_and_generate_smiles(Chem.MolToSmiles(mol), '[N+](=O)[O-]', idx, 0))
                possible_TPs.append(modified_mol)
        if rxn_type == 'O':
            for idx in atoms_with_H:
                modified_mol = replace_hydrogen_with_substituent(mol, idx, 'O')
                possible_TPs.append(modified_mol)
        if rxn_type == 'CH2':
            for idx in atoms_with_H:
                modified_mol = replace_hydrogen_with_substituent(mol, idx, 'C')
                possible_TPs.append(modified_mol)
        if rxn_type == 'NH':
            for idx in atoms_with_H:
                modified_mol = replace_hydrogen_with_substituent(mol, idx, 'N')
                possible_TPs.append(modified_mol)
    if num < 0:
        if rxn_type == 'H-1Br':
            for bond in C_Br:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'HBr'])
        if rxn_type == 'H-1Cl':
            for bond in C_Cl:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'HCl'])
        if rxn_type == 'H-1F':
            for bond in C_F:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'HF'])
        if rxn_type == 'H-1I':
            for bond in C_I:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'HI'])
        if rxn_type == 'CH2':
            for bond in C_CH2:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'CH4'])
        if rxn_type == 'NH':
            for bond in C_NH:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'NH3'])
        if rxn_type == 'H-1NO2':
            for bond in C_NO2:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'NO2'])
        if rxn_type == 'O':
            for bond in C_O:
                possible_TPs.extend(
                    [mol for mol in split_molecule_at_bond(mol, bond.GetIdx()) if CalcMolFormula(mol) != 'H2O'])
    possible_TPs = [add_missing_H(i) for i in possible_TPs]
    possible_TPs = [remove_additional_H(i) for i in possible_TPs]
    return possible_TPs


def remove_explicit_hydrogens(smiles):
    """
    Converts explicit hydrogen atoms in a molecule to implicit hydrogens.

    Parameters:
    - smiles (str): A SMILES string of the molecule with explicit hydrogens.

    Returns:
    - str: A SMILES string of the molecule with hydrogens made implicit.
    """
    # Convert the SMILES string to an RDKit molecule object
    mol = Chem.MolFromSmiles(smiles)

    # Remove explicit hydrogens
    mol_no_h = Chem.RemoveHs(mol)

    # Convert back to SMILES
    smiles_no_h = Chem.MolToSmiles(mol_no_h)

    return smiles_no_h


def GetIdxOfDummy(frag_smi):
    mol = Chem.MolFromSmiles(frag_smi)
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 0:  # Dummy atom found
            connected_atom = atom.GetNeighbors()[0]  # Assuming only one atom connected to the dummy
            break
    target_neighbors = sorted([i.GetSymbol() for i in connected_atom.GetNeighbors() if i.GetAtomicNum() != 0])
    index = None
    mol1 = replace_dummies_with_hydrogens(mol)
    # Remove explicit hydrogens
    mol_no_h = Chem.RemoveHs(mol1)
    mol_no_h = Chem.MolFromSmiles(Chem.MolToSmiles(mol_no_h))  # refresh the structures
    for atom in mol_no_h.GetAtoms():
        if atom.GetSymbol() == connected_atom.GetSymbol():
            if atom.IsInRing() == connected_atom.IsInRing():
                if is_atom_in_double_bond(atom) == is_atom_in_double_bond(connected_atom):
                    if atom.GetTotalNumHs() == connected_atom.GetTotalNumHs() + 1:
                        neighbors = sorted([i.GetSymbol() for i in atom.GetNeighbors()])
                        if neighbors == target_neighbors:
                            index = atom.GetIdx()

    return mol_no_h, index


def combine_fragments_and_generate_smiles(fragment1_smiles, fragment2_smiles, fragment1_connect_atom_idx,
                                          fragment2_connect_atom_idx):
    """
    Combines two molecular fragments, represented by their SMILES strings, into a single molecule by forming a bond
    between specified atoms from each fragment.

    This function takes the SMILES strings of two molecular fragments and the indices of the atoms (within each fragment)
    that should be connected. It then combines these fragments into a single molecule by forming a single bond between
    the specified atoms. The resulting molecule is returned as a SMILES string.

    Parameters:
    - fragment1_smiles (str): The SMILES string representing the first molecular fragment.
    - fragment2_smiles (str): The SMILES string representing the second molecular fragment.
    - fragment1_connect_atom_idx (int): The zero-based index of the atom in the first fragment to be connected.
    - fragment2_connect_atom_idx (int): The zero-based index of the atom in the second fragment to be connected.

    Returns:
    - str: The SMILES string representing the combined molecule after connecting the specified atoms.

    Example:
    >>> combine_fragments_and_generate_smiles('CCO', 'N', 2, 0)
    'CCON'

    Note:
    - The indices of the connecting atoms are based on the order of atoms in their respective SMILES strings.
    - The function assumes valid SMILES strings and valid atom indices are provided. Invalid inputs may lead to
      unexpected results or errors.
    - The bond formed between the fragments is a single bond. Modifications are needed to form other types of bonds.
    """
    # Create molecule objects from the SMILES strings
    fragment1_mol = Chem.MolFromSmiles(fragment1_smiles)
    fragment2_mol = Chem.MolFromSmiles(fragment2_smiles)

    # Combine the molecules
    combined_mol = rdmolops.CombineMols(fragment1_mol, fragment2_mol)

    # Create an editable molecule for further modifications
    editable_mol = Chem.EditableMol(combined_mol)

    # Calculate the index of the first atom in fragment2 within the combined molecule
    fragment2_start_idx = fragment1_mol.GetNumAtoms()

    # Add a bond between the specified atoms
    # The index of the connecting atom in fragment2 needs to be adjusted to its new index in the combined molecule
    editable_mol.AddBond(fragment1_connect_atom_idx, fragment2_start_idx + fragment2_connect_atom_idx,
                         order=Chem.rdchem.BondType.SINGLE)

    # Convert back to a regular Mol object
    final_mol = editable_mol.GetMol()

    for atom in final_mol.GetAtoms():
        atom.SetNumExplicitHs(0)
    # Sanitize the molecule
    Chem.SanitizeMol(final_mol)

    # Generate and return the SMILES of the combined molecule
    final_smiles = Chem.MolToSmiles(final_mol, isomericSmiles=True)
    return final_smiles


def draw_molecule_with_atom_indices(mol):
    """
    Draws an RDKit molecule object with atom indices.

    Parameters:
    - mol (Chem.Mol): The RDKit molecule object to be drawn.

    Returns:
    - IPython.core.display.SVG: SVG representation of the molecule with atom indices.
    """
    # Create a drawer with specific dimensions (400x200)
    drawer = rdMolDraw2D.MolDraw2DSVG(400, 200)
    # Enable atom index drawing
    drawer.drawOptions().addAtomIndices = True
    # Draw the molecule
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    # Get the SVG from the drawer
    svg = drawer.GetDrawingText().replace('svg:', '')

    # Return the SVG for display
    return SVG(svg)


def replace_hydrogen_with_substituent(mol, atom_idx, substituent_symbol):
    """
    Replaces all hydrogen atoms attached to a specified atom in a molecule with a substituent atom.

    This function identifies all hydrogen atoms bonded to a specified atom within a given molecule
    and replaces them with a specified substituent atom. The operation is performed on a copy of the
    original molecule, ensuring that the original molecule remains unchanged.

    Parameters:
    - mol (Chem.Mol): An RDKit molecule object.
    - atom_idx (int): The index of the atom in the molecule where hydrogens are to be replaced.
    - substituent_symbol (str): The symbol of the substituent atom with which to replace the hydrogens
      (e.g., 'Cl' for chlorine, 'Br' for bromine).

    Returns:
    - Chem.Mol: A new RDKit molecule object with the specified hydrogen atoms replaced by the substituent atoms.

    Example:
    >>> mol = Chem.MolFromSmiles('CCO')
    >>> new_mol = replace_hydrogen_with_substituent(mol, 0, 'Cl')
    >>> print(Chem.MolToSmiles(new_mol))
    CClCO

    Note:
    - The function adds explicit hydrogens to the molecule if necessary to ensure all hydrogens are visible
      for replacement. These explicit hydrogens are removed from the final molecule if they were not part
      of the original input molecule.
    - The molecule's stereochemistry and coordinates are updated after the modification.
    """

    # Add explicit hydrogens to the molecule to ensure all hydrogens are visible for replacement
    mol_with_h = Chem.AddHs(mol)

    # Create an editable molecule for modifications
    edit_mol = Chem.EditableMol(mol_with_h)

    # Find all hydrogens attached to the specified atom
    target_atom = mol_with_h.GetAtomWithIdx(atom_idx)
    hydrogens_to_replace = [neighbor.GetIdx() for neighbor in target_atom.GetNeighbors() if neighbor.GetSymbol() == 'H']

    # Replace hydrogens by removing them and adding substituent atoms
    for h_idx in sorted(hydrogens_to_replace, reverse=True):
        edit_mol.RemoveAtom(h_idx)
        substituent_idx = edit_mol.AddAtom(Chem.Atom(substituent_symbol))
        edit_mol.AddBond(atom_idx, substituent_idx, order=Chem.rdchem.BondType.SINGLE)
        break

    # Generate the modified molecule
    modified_mol = edit_mol.GetMol()

    # Remove explicit hydrogens if they were not part of the original molecule
    final_mol = Chem.RemoveHs(modified_mol)

    # Update the molecule's stereochemistry and coordinates
    Chem.SanitizeMol(final_mol)
    AllChem.Compute2DCoords(final_mol)

    return final_mol
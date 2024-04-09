import os
import unittest

import pandas as pd
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure
from pymatgen.io.cif import CifWriter

from pyecif import CifBlock, LoadEcif, WriteEcif


class TestECIFPandasTools(unittest.TestCase):

    def test_WriteEcif(self):
        # 创建一个测试的DataFrame
        df = pd.DataFrame({
            'ID': ['test1', 'test2'],
            'CIF': [Structure(Lattice.cubic(4.225), ["Na"], [[0, 0, 0]]),
                    Structure(Lattice.cubic(3.61), ["Cu", "Cu", "Cu", "Cu"], [[0, 0, 0], [0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]])
                    ],
            'prop1': [1, 2],
            'prop2': [3, 4]
        })

        # 写入ECIF文件
        WriteEcif(df, 'test.ecif', properties=['prop1', 'prop2'])

        # 确保文件已经被创建
        self.assertTrue(os.path.exists('test.ecif'))

        # 清理测试文件
        os.remove('test.ecif')

    def test_LoadEcif(self):
        # 创建一个测试的ECIF文件
        with open('test.ecif', 'w') as f:
            f.write("""
<ID> (0)
0

<CIF> (0)
# generated using pymatgen
data_Na
_symmetry_space_group_name_H-M   'P 1'
_cell_length_a   4.22500000
_cell_length_b   4.22500000
_cell_length_c   4.22500000
_cell_angle_alpha   90.00000000
_cell_angle_beta   90.00000000
_cell_angle_gamma   90.00000000
_symmetry_Int_Tables_number   1
_chemical_formula_structural   Na
_chemical_formula_sum   Na1
_cell_volume   75.41889062
_cell_formula_units_Z   1
loop_
 _symmetry_equiv_pos_site_id
 _symmetry_equiv_pos_as_xyz
  1  'x, y, z'
loop_
 _atom_site_type_symbol
 _atom_site_label
 _atom_site_symmetry_multiplicity
 _atom_site_fract_x
 _atom_site_fract_y
 _atom_site_fract_z
 _atom_site_occupancy
  Na  Na0  1  0.00000000  0.00000000  0.00000000  1

<prop1> (0)
1
<prop2> (0)
3

$$$$

<ID> (1)
1

<CIF> (1)
# generated using pymatgen
data_Cu
_symmetry_space_group_name_H-M   'P 1'
_cell_length_a   3.61000000
_cell_length_b   3.61000000
_cell_length_c   3.61000000
_cell_angle_alpha   90.00000000
_cell_angle_beta   90.00000000
_cell_angle_gamma   90.00000000
_symmetry_Int_Tables_number   1
_chemical_formula_structural   Cu
_chemical_formula_sum   Cu4
_cell_volume   47.04588100
_cell_formula_units_Z   4
loop_
 _symmetry_equiv_pos_site_id
 _symmetry_equiv_pos_as_xyz
  1  'x, y, z'
loop_
 _atom_site_type_symbol
 _atom_site_label
 _atom_site_symmetry_multiplicity
 _atom_site_fract_x
 _atom_site_fract_y
 _atom_site_fract_z
 _atom_site_occupancy
  Cu  Cu0  1  0.00000000  0.00000000  0.00000000  1
  Cu  Cu1  1  0.50000000  0.50000000  0.00000000  1
  Cu  Cu2  1  0.50000000  0.00000000  0.50000000  1
  Cu  Cu3  1  0.00000000  0.50000000  0.50000000  1

<prop1> (1)
2
<prop2> (1)
4

$$$$


"""
                    )

        # 加载ECIF文件
        df = LoadEcif('test.ecif')

        # 确保DataFrame包含正确的数据
        self.assertEqual(df.loc['0', 'prop1'], 1)
        self.assertEqual(df.loc['0', 'prop2'], 3)
        self.assertEqual(df.loc['1', 'prop1'], 2)
        self.assertEqual(df.loc['1', 'prop2'], 4)

        # 清理测试文件
        os.remove('test.ecif')

    def test_CifBlock(self):
        # 创建一个CifBlock
        block = CifBlock()
        block.SetProp('key', 'value')
        block.AddCifLine('cif_line')

        # 确保属性和CIF行被正确设置
        self.assertEqual(block.GetProp('key'), 'value')
        self.assertEqual(block.GetCif(), ['cif_line'])

if __name__ == '__main__':
    unittest.main()
import os
import re

import numpy as np
import pandas as pd
from pymatgen.core.structure import Structure
from pymatgen.io.cif import CifParser, CifWriter


def WriteEcif(df, out, idName='ID', cifColName='CIF', properties=None):
    """
    Write a pandas dataframe to an ECIF file
    """

    if cifColName not in df.columns:
        raise ValueError("No column named %s in dataframe" % cifColName)
    
    for cif in df[cifColName]:
        if not isinstance(cif, Structure):
            raise ValueError("Column %s is not a list of pymatgen Structures" % cifColName)
    
    if properties is None:
        properties = []
    else:
        properties = list(properties)

    if cifColName in properties:
        properties.remove(cifColName)
    if idName in properties:
        properties.remove(idName)

    if os.path.exists(out):
        print("Warning: %s already exists. Overwriting." % out)
    
    with open(out, 'w') as file:

        for num, row in enumerate(df.iterrows()):
            cifblock = CifBlock()
            if idName is not None:
                if idName == 'ID':
                    cifblock.SetProp('_Name', str(row[0]))
                else:
                    cifblock.SetProp('_Name', str(row[1][idName]))

            structure = row[1][cifColName]
            cifblock.AddCifFromPymatgen(structure)

            for prop in properties:
                cell_value = row[1][prop]
                # Make sure float does not get formatted in E notation
                if np.issubdtype(type(cell_value), np.floating):
                    s = '{:f}'.format(cell_value).rstrip("0")  # "f" will show 7.0 as 7.00000
                    if s[-1] == ".":
                        s += "0"  # put the "0" back on if it's something like "7."
                    cifblock.SetProp(prop, s)
                else:
                    cifblock.SetProp(prop, str(cell_value))

            cif_block = cifblock.GetBlock()
            num_cif_block = re.sub(r'(<.*?>)(.*?)(?=\s|$)', fr'\1 ({num})', cif_block)
            file.write(num_cif_block)
            file.write('\n\n$$$$\n\n')
        


def LoadEcif(ecif_file, idName='ID', cifColName='CIF'):
    """
    Load ECIF file into a pandas dataframe
    """
        
    with open(ecif_file, 'r') as file:
        lines = file.readlines()
    
    df = pd.DataFrame()
    block = []
    for line in lines:
        if line.strip() == '$$$$':
            cifblock = CifBlock()
            cifblock.AddBlock('\n'.join(block))
            block = []
            row = _CifBlockToRow(cifblock, cifColName)
            df = df._append(row, ignore_index=True)

        else:
            block.append(line)
    if idName in df.columns:
        df.set_index(idName, inplace=True)

    for col in df.columns:
        if col != cifColName:
            df[col] = pd.to_numeric(df[col], errors='ignore')

    return df

def _CifBlockToRow(cifblock, cifColName):
    row = {}
    for key, value in cifblock._props.items():
        row[key] = value
    row[cifColName] = cifblock.GetPymatgenStructure()
    return row

class CifBlock:
    def __init__(self):
        self._props = {}
        self._cif = []
    
    def SetProp(self, key, value):
        self._props[key] = value
    
    def GetProp(self, key):
        return self._props[key]
    
    def AddCifLine(self, line):
        self._cif.append(line)
    
    def AddCifFromPymatgen(self, structure):
        cif_writer = CifWriter(structure)
        cif_string = cif_writer.__str__()
        cif_string = cif_string.split('\n')
        for line in cif_string:
            self._cif.append(line)   

    def GetCif(self):
        return self._cif
    
    def GetBlock(self):
        block = []
        block.append('<ID>\n%s\n' % self._props['_Name'])
        block.append('<CIF>')
        for line in self._cif:
            block.append(line)
        for key, value in self._props.items():
            if key != '_Name':
                block.append('<%s>\n%s' % (key, value))
        block_str = '\n'.join(block)
        return block_str
    
    def GetPymatgenStructure(self):
        cif_str = '\n'.join(self._cif)
        cif_parser = CifParser.from_str(cif_str)
        return cif_parser.get_structures(on_error='ignore')[0]

    def AddBlock(self, block):
        pattern = re.compile(r'<(.*?)>\s\(\d+\)\n(.*?)(?=<|$)', re.DOTALL)
        matches = pattern.findall(block)

        # 创建一个字典来存储key-value对
        block_dict = {key: value.strip() for key, value in matches}

        self._cif = block_dict['CIF'].split('\n')
        for key, value in block_dict.items():
            if key != 'CIF':
                self._props[key] = value

    def WriteCif(self, filename):
        with open(filename, 'w') as f:
            for key, value in self._props.items():
                f.write('_%s\n%s\n' % (key, value))
            f.write('\n')
            for line in self._cif:
                f.write(line + '\n')

if __name__ == '__main__':
    #df = LoadEcif('example/mb-jdft2d.ecif')
    #WriteEcif(df, 'output.ecif', properties=df.columns)
    from pymatgen.core import Lattice
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
    df = LoadEcif('test.ecif')
    df
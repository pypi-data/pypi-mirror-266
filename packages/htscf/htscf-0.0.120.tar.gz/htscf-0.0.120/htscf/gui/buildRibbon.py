import warnings
from copy import deepcopy
from enum import Enum
from io import BytesIO
from itertools import chain
from pprint import pprint
from typing import Union, List
import ase
import numpy as np
from ase.atoms import Atom
from ase.build import make_supercell, cut
from ase.data import covalent_radii, chemical_symbols
from ase.io.cif import parse_cif_ase
from htscf.utils import vdwbulk

warnings.filterwarnings("ignore")


class RIBBON(Enum):
    """获取边界原子的方向"""
    LEFT = 0
    RIGHT = 1


class F:
    """
    Some helpful Functions for build nano-ribbons.
    """

    @staticmethod
    def get_distance(pos1, pos2):
        """Calculate the distance of two positions."""
        return np.sqrt(np.sum(np.square(pos1 - pos2)))

    @staticmethod
    def find_indexes(atoms, positions):
        """
        Find the atom index from atoms object by their position and return a series of indexes.
        """
        atom_indexes = []
        if isinstance(positions, list):
            for pos in positions:
                for atom in atoms:
                    if (pos == atom.position).all():
                        atom_indexes.append(atom.index)
                        break
            return atom_indexes
        else:
            for atom in atoms:
                if (positions == atom.position).all():
                    return atom.index

    @staticmethod
    def get_covalent_radii(symbol):
        """
        Get covalent_radii by symbol
        :param symbol:symbol,such as 'H'
        """
        if isinstance(symbol, str):
            index = chemical_symbols.index(symbol)
            return covalent_radii[index]
        elif isinstance(symbol, (tuple, set, list)):
            radius = []
            for i in symbol:
                index = chemical_symbols.index(i)
                radius.append(covalent_radii[index])
            return radius

    @staticmethod
    def layered(atoms, axis: int = 0, tol: float = 0.0, pos_type="cartesian") -> List[list]:
        """
        Determine atomic layers based on coordinates
        :param atoms:
        :param pos_type:
        :param axis: Axis of coordinates
        :param tol:Position tolerance
        :return:Layered positions
        """
        if pos_type == "fractional":
            positions = sorted(atoms.get_scaled_positions(), key=lambda x: x[axis])
        else:
            positions = sorted(atoms.positions, key=lambda x: x[axis])

        if axis > len(positions[0]) - 1:
            raise ValueError("The axis greater than positions[0]")
        li = [[positions.pop(0)]]
        while positions:
            element = positions.pop(0)
            last = li[-1][0][axis]
            if abs(element[axis] - last) <= tol:
                li[-1].append(element)
            else:
                li.append([element])
        return li

    @staticmethod
    def find_neighbor_list(atoms):
        neighbor_list = []
        length = len(atoms)
        for i in range(length):
            tmp = set()
            atom1 = atoms[i]
            for j in range(i):
                atom2 = atoms[j]
                symbol1, symbol2 = atom1.symbol, atom2.symbol
                distance = F.get_distance(atom1.position, atom2.position)
                r1, r2 = F.get_covalent_radii(symbol1), F.get_covalent_radii(symbol2)
                if 0 <= distance < r1 + r2:
                    tmp.add(atom1)
                    tmp.add(atom2)
            if tmp:
                neighbor_list.append(tmp)
        return neighbor_list

    @staticmethod
    def extend_vector(a, b, scale=1.0):
        """
        Extend the vector ab and return the point new_b
        """
        return a + (b - a) * scale

    @staticmethod
    def diff(arr1, arr2):
        """
        Find the difference set of two lists, arr1 - arr2.
        """
        if not isinstance(arr1, np.ndarray):
            arr1 = np.array(arr1)
        if not isinstance(arr2, np.ndarray):
            arr2 = np.array(arr2)
        tmp_index = []
        index = []
        for i in range(arr1.shape[0]):
            tmp = arr1[i]
            for j in arr2:
                if (tmp == j).all():
                    tmp_index.append(i)
        for i in range(arr1.shape[0]):
            if i not in tmp_index:
                index.append(i)
        return arr1[index]

    @staticmethod
    def find_conn(arr1, arr2, d=2):
        tmp = []
        for i in arr1:
            for j in arr2:
                distance = F.get_distance(i, j)
                if distance < d:
                    tmp.append([i, j])
        return tmp

    @staticmethod
    def find_indexes_by_scale(atoms: ase.Atoms, positions: Union[np.ndarray, list]) -> Union[int, list]:
        """
        Find the atom index from atoms object by their position and return a series of indexes.
        :param atoms:
        :param positions:
        :return:
        """
        atom_indexes = []
        positions = np.array(positions)
        fracs = atoms.get_scaled_positions()
        for pos in positions:
            for i, pos2 in enumerate(fracs):
                pos = np.round(pos, decimals=2)
                pos2 = np.round(pos2, decimals=2)
                if (pos == pos2).all():
                    atom_indexes.append(i)
        return atom_indexes

    @staticmethod
    def get_edge_pbc_positions(atoms):
        scaled_positions = atoms.get_scaled_positions()  # 获取分数坐标
        sp1 = scaled_positions.copy()  # 分数坐标副本
        sp1 = np.round(sp1, decimals=2)  # 分数坐标保留2位数
        sp1[:, 0] -= 1  # 分数坐标减一
        edge_pbc_positions = []
        for pos in sp1:
            if (pos <= 1).all() and (pos >= 0).all():
                edge_pbc_positions.append(pos)
        if edge_pbc_positions:
            edge_pbc_positions = np.array(edge_pbc_positions)
            orig_positions = []
            epp1 = edge_pbc_positions.copy()
            epp1[:, 0] += 1
            for pos in epp1:
                if (pos <= 1).all() and (pos >= 0).all():
                    orig_positions.append(pos)
            return np.array(orig_positions), edge_pbc_positions
        else:
            return None, None

    @staticmethod
    def layered2atom(atoms, axis: int = 0, tol: float = 0.0):
        """
        Determine atomic layers based on coordinates
        :param atoms:
        :param axis: Axis of coordinates
        :param tol:Position tolerance
        :return:Layered atom list
        """
        atoms_list = sorted((atom for atom in atoms), key=lambda x: x.position[axis])
        layer_list = [[atoms_list.pop(0)]]
        while atoms_list:
            element = atoms_list.pop(0)
            last = layer_list[-1][0].position[axis]
            if abs(element.position[axis] - last) <= tol:
                layer_list[-1].append(element)
            else:
                layer_list.append([element])
        pprint(layer_list)
        return layer_list

    @staticmethod
    def get_edge_atom_indices(atoms, direction: RIBBON = RIBBON.LEFT):
        """获取纳米带x方向指定边界的原子编号"""
        indices = []
        origin_scaled = atoms.get_scaled_positions().copy()
        if direction == RIBBON.LEFT:
            origin_scaled[:, 0] += 1  # 原子整体右移，获取左边界原子
        elif direction == RIBBON.RIGHT:
            origin_scaled[:, 0] -= 1  # 原子整体左移，获取右边界原子
        for i, pos in enumerate(origin_scaled):
            if 0 <= pos[0] <= 1:
                indices.append(i)
        return indices

    @staticmethod
    def add_vacuum(atoms, vacuum=10, axis=2):
        """
        Add vacuum layer to the atoms.
        :param atoms:
        :param vacuum: float. The thickness of the vacuum layer (in Angstrom).
        :param axis: int, 0|1|2. The direction of the vacuum layer
        """
        cell = atoms.get_cell()
        positions = F.layered(atoms, axis=axis)
        width = np.sqrt(np.sum(np.square(positions[0][0] - positions[-1][0])))
        axis_length = np.sqrt(np.dot(cell[axis], cell[axis]))
        orig_vacuum = axis_length - width
        new_vacuum = vacuum - orig_vacuum
        x, y, z = cell
        vectors = [[x, y, z], [y, z, x], [z, x, y]]
        vector0, vector1, vector2 = vectors[axis]
        normal = np.cross(vector1, vector2)
        costheta = np.dot(normal, vector0) / np.sqrt(np.dot(normal, normal) * np.dot(vector0, vector0))
        length = np.sqrt(np.dot(vector0, vector0))
        newlength = length + new_vacuum / costheta
        vector0 *= newlength / length
        atoms.set_cell(cell)
        atoms.center(axis=axis)
        return atoms

    @staticmethod
    def move_edge(atoms):
        """
        用于将正好在右边界的原子移动到左侧，以便于加氢。
        """
        orig, new_pos = F.get_edge_pbc_positions(atoms)
        if isinstance(orig, np.ndarray):
            index = F.find_indexes_by_scale(atoms, orig)
            pbc_atoms = atoms[index]
            del atoms[index]
            scaled = pbc_atoms.get_scaled_positions()
            scaled[:, 0] -= 1
            pbc_atoms.set_scaled_positions(scaled)
            atoms.extend(pbc_atoms)


class RibbonBuilder:
    @staticmethod
    def surface(atoms, milerIndex=((1, 0, 0), (0, 1, 0), (0, 0, 1)), super_cell=None, connectivity=(0.1, 1.3)):
        """
        切割三维材料为二维材料，并改变晶胞形状
        """
        a, b, c = milerIndex
        atoms = atoms.copy()
        if not super_cell:
            super_cell = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        atoms = cut(atoms, a, b, c, nlayers=15)
        atoms.edit()
        cluster = vdwbulk.VdwBulk(atoms, connectivity=connectivity).get_cluster()
        len_cluster = [len(c) for c in cluster]
        index = len_cluster.index(max(len_cluster))
        drop_index = []
        for i, v in enumerate(cluster):
            if i != index:
                drop_index.extend(v)
        del atoms[drop_index]
        atoms = make_supercell(atoms, super_cell)
        with BytesIO() as b1:  # reload structure from cif
            atoms.write(b1, "cif")
            b1.seek(0)
            cif_block = parse_cif_ase(b1)
            atoms = list(cif_block)[0].get_atoms()
        return atoms

    @staticmethod
    def cut_ribbon(atoms, layer, origo, ribbon_tol, axis=1):
        atoms = atoms.copy()
        positions_layered = F.layered(atoms, axis, ribbon_tol)  # Layering 2D material's positions along a specific axis
        saved_layer_numbers = int(
            len(positions_layered) - layer)  # Number of nano-ribbon layers retained after cutting
        saved_positions = positions_layered[origo:-saved_layer_numbers + origo]
        saved_positions = [j for i in saved_positions for j in i]  # 降维
        atom_indexes = F.find_indexes(atoms, saved_positions)
        atoms = atoms[atom_indexes]
        return atoms

    @staticmethod
    def edge_del(atoms, tol=0, axis=1, direction=2):
        positions = F.layered(atoms, axis=axis, tol=tol)
        if direction == 2:
            indexes = F.find_indexes(atoms, positions[0]) + F.find_indexes(atoms, positions[-1])
        elif direction == 1:
            indexes = F.find_indexes(atoms, positions[-1])
        else:
            indexes = F.find_indexes(atoms, positions[0])
        del atoms[indexes]
        return atoms

    @staticmethod
    def get_ribbon_width(atoms):
        positions = F.layered(atoms, axis=1)
        return np.sqrt(np.sum(np.square(positions[0][0] - positions[-1][0])))

    @staticmethod
    def terminate(atoms, symbol="H", side=0, connectivity_opts=(0.6, 1.3), tol=0.):
        _atoms = atoms.copy()
        if side == 2:  # Used to control hydrogenation position
            _atoms = RibbonBuilder.terminate(_atoms, symbol=symbol, side=0, connectivity_opts=connectivity_opts,
                                             tol=tol)
            _atoms.edit()
            _atoms = RibbonBuilder.terminate(_atoms, symbol=symbol, side=1, connectivity_opts=connectivity_opts,
                                             tol=tol)
            _atoms.edit()
            return _atoms
        directions = [[0, 1], [-1, -2]][side]
        a = _atoms.cell[0]
        edge_left, edge_right = _atoms.copy(), _atoms.copy()
        for atom in edge_left:
            atom.position += a
        for atom in edge_right:
            atom.position -= a
        full = chain(_atoms.copy(), edge_left, edge_right)  # Add the periodic atoms on the left and right
        atom_layer = F.layered2atom(full, axis=1, tol=tol)  # Layer atoms
        edge, inner = atom_layer[directions[0]], atom_layer[directions[1]]  # Get boundary and sublayer atoms
        r_new_atom = F.get_covalent_radii(symbol)  # Gets the atomic radius used for passivation
        for atom1 in inner:
            for atom2 in edge:
                # Obtain the covalent bond length between the sublayer and outermost atom
                r1, r2 = F.get_covalent_radii([atom1.symbol, atom2.symbol])
                distance = F.get_distance(atom1.position, atom2.position)
                if (r1 + r2) * connectivity_opts[0] < distance < (r1 + r2) * connectivity_opts[1]:
                    bond_length = r_new_atom + r1
                    terminate_position = F.extend_vector(atom1.position, atom2.position, scale=bond_length / distance)
                    atom = Atom(symbol, position=terminate_position)
                    _atoms.extend(atom)
        del _atoms[[i.index for i in edge]]  # Delete the outermost atoms
        return _atoms

    @staticmethod
    def add_vacuum(atoms, vacuums):
        # _atoms = F.add_vacuum(atoms, vacuums[0], axis=0)
        _atoms = F.add_vacuum(atoms, vacuums[1], axis=1)
        _atoms = F.add_vacuum(_atoms, vacuums[2], axis=2)
        return _atoms

    @staticmethod
    def build(atoms, layer, origo=0, ribbon_tol=0, axis=1, milerIndex=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
              super_cell=((1, 0, 0), (0, 50, 0), (0, 0, 1)), vacuums=(0, 15, 15), connectivity=(0.1, 1.6)):
        _atoms = RibbonBuilder.surface(atoms, milerIndex, super_cell=super_cell, connectivity=connectivity)
        _atoms = RibbonBuilder.cut_ribbon(_atoms, layer, origo, ribbon_tol, axis)
        _atoms = RibbonBuilder.add_vacuum(_atoms, vacuums)
        return _atoms


if __name__ == '__main__':
    # import yaml
    # from htsct.utils.tools import parse_cif_ase_string
    #
    # fp = r"E:\Projects\Work\HighThroughputScreen\htsct\core\1139.C2F2_dff996350a424697ce2eb7eb736a0349.yacif"
    # with open(fp) as fd:
    #     cif = yaml.load(fd, Loader=yaml.FullLoader)["cif"]
    # atoms = parse_cif_ase_string(cif)
    # atoms = RibbonBuilder.build(atoms, layer=13, milerIndex=((1, 1, 0), (1, -1, 0), (0, 0, -1)))
    # RibbonBuilder.terminate(atoms).edit()
    pass

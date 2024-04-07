from copy import deepcopy
import numpy as np
from ase import Atoms
from ase.build import make_supercell
from ase.io import read
from ase.data import covalent_radii, chemical_symbols


class VdwBulk:
    """
    A class used to determine which is a Van der Waals interaction of bulk material
    """

    def __init__(self, atoms, connectivity=(0.6, 1.3)):
        self.adj_list = {}
        self.atoms = atoms
        self.clusters = None
        self.connectivity = connectivity
        self._adj_list()

    @staticmethod
    def __get_covalent_radii(symbol):
        '''
        根据元素符号获取元素半径
        :param symbol:symbol,such as 'H'
        '''
        index = chemical_symbols.index(symbol)
        return covalent_radii[index]

    def _adj_list(self):
        """
        A function helps to create a Adjacency list
        """
        symbols = self.atoms.symbols
        positions = self.atoms.positions
        l1 = []
        for i in positions:
            tmp = []
            for j in positions:
                res = np.sqrt(np.sum(np.square(i - j)))
                tmp.append(res)
            l1.append(deepcopy(tmp))
            tmp.clear()
        for i, v in enumerate(l1):
            element = symbols[i]
            tmp = []
            for j, v2 in enumerate(v):
                element2 = symbols[j]
                r1 = self.__get_covalent_radii(element)
                r2 = self.__get_covalent_radii(element2)
                if (r1 + r2) * self.connectivity[0] < v2 < (r1 + r2) * self.connectivity[1]:
                    tmp.append(j)
            self.adj_list[i] = deepcopy(tmp)
            tmp.clear()

    def __search(self, node, adj_list):
        """
        A simplified Depth First Search algorithm
        :param node: the number of node
        :param adj_list: Adjacency list
        :return: all adj_lists which associated with the node
        """
        l1 = adj_list.pop(node)
        for i in l1:
            if i in self.adj_list.keys():
                for i in self.__search(i, adj_list):
                    yield i
            else:
                yield l1
        yield l1

    def __find_cluster_indexes(self, adj_list):
        """
        get all connected graphs
        """
        while self.adj_list.keys():
            node_index = list(adj_list.keys())[0]
            l1 = list(self.__search(node_index, adj_list))
            s1 = {j for i in l1 for j in i}
            yield deepcopy(s1)
            s1.clear()

    def get_cluster(self):
        self.clusters = list(self.__find_cluster_indexes(self.adj_list))
        return self.clusters

    def get_1layer(self):
        """
        Obtain a layer of the bulk material
        :return:one layer of atoms
        """
        if not self.clusters:
            self.get_cluster()
        cluster1 = self.clusters[0]
        atoms_new = Atoms(cell=self.atoms.get_cell())
        for index in cluster1:
            atoms_new.extend(self.atoms[index])
        return atoms_new

    def get_cluster_count(self):
        """
        Get the number of clusters
        """
        if not self.clusters:
            self.get_cluster()
        return len(self.clusters)

    @classmethod
    def dimension_classification(cls, atoms):
        """
        According to the value of count2 / count1,the bulk structure can be classified into five types.
        count2 / count1 == 1: Three dimensional compound
                        == 2: Two dimensional layered compound
                        == 4: One dimensional compound
                        == 8: Zero dimensional compound
                        == other: mixed
        :param atoms:ase.Atoms object
        """
        vdwbulk1 = cls(atoms)
        atoms2x2 = make_supercell(vdwbulk1.atoms, [[2, 0, 0], [0, 2, 0], [0, 0, 2]])
        vdwbulk2 = cls(atoms2x2)
        count1 = vdwbulk1.get_cluster_count()
        count2 = vdwbulk2.get_cluster_count()
        return count2 / count1

    def merge_cluster(self):
        """
        Merge associated clusters.
        """
        cluster = self.get_cluster()
        a, b, c = self.atoms.cell
        print(a, b, c)


if __name__ == '__main__':
    atoms = read('../test/ribbon_test/InBrO_mp-27703_primitive.cif')
    v = VdwBulk(atoms)
    # rt = v.get_cluster()
    print(v.adj_list)

########################################################################################################################

__doc__ = \
    """
    This add the oddity fixing functionality. Generally odd corner cases.
    Formerly part of collapse_ring.py
    """

########################################################################################################################

from rdkit import Chem
from rdkit.Geometry import Point3D

from ._base import _RectifierBase


class _RectifierOdd(_RectifierBase):

    def prevent_oddities(self):
        self._prevent_allene()

    # ====== Private methods ===========================================================================================

    def _prevent_allene(self):
        for atom in self.rwmol.GetAtoms():
            if atom.GetAtomicNum() < 14:
                n = []
                for bond in atom.GetBonds():
                    if bond.GetBondType().name in ('DOUBLE', 'TRIPLE'):
                        n.append(bond)
                    else:
                        pass
                if len(n) > 2:
                    # this is a mess!
                    self.log.info(f'Allene issue: {n} double bonds on {atom.GetSymbol()} atom {atom.GetIdx()}!')
                    for bond in n:
                        bond.SetBondType(Chem.BondType().SINGLE)
                elif len(n) == 2:
                    # downgrade the higher bonded one!
                    others = [a for bond in n for a in (bond.GetBeginAtom(), bond.GetEndAtom()) if
                              a.GetIdx() != atom.GetIdx()]
                    others = sorted(others, key=lambda atom: sum([b.GetBondTypeAsDouble() for b in atom.GetBonds()]))
                    self.log.info(f'Allene removed between {atom.GetIdx()} and {[a.GetIdx() for a in others]}')
                    self.rwmol.GetBondBetweenAtoms(atom.GetIdx(), others[-1].GetIdx()).SetBondType(Chem.BondType.SINGLE)
                else:
                    pass
            else:
                continue
        self.log.debug(f'Storing molecule #{len(self.modifications)} in `.modifications`')
        self.modifications[f'no_allene-inter{self._iterations_done}'] = self.mol

    def _prevent_overclose(self):
        pass

    def blank_nan_positions(self, shift=0.5):
        """
        This is problematic. I am unsure why this happens occasionally on linkers to _certain_ hit molecules.
        This issue is from AllChem.AddHs addCoords not working properly.
        """
        if not self.has_conformer:
            return
        conf: Chem.Conformer = self.rwmol.GetConformer()
        self.rwmol.BeginBatchEdit()  # in case there is a rogue Hs
        for i in range(self.rwmol.GetNumAtoms()):
            if str(conf.GetAtomPosition(i).x) == 'nan':
                symbol = self.rwmol.GetAtomWithIdx(i).GetSymbol()
                self.log.info(f'nan atom position: {symbol} {i} -> {conf.GetAtomPosition(i)}')
                neighbor_idxs = [a.GetIdx() for a in self.rwmol.GetAtomWithIdx(i).GetNeighbors()]
                neighbor_xyzs = [conf.GetAtomPosition(idx) for idx in neighbor_idxs]
                if len(neighbor_idxs) == 0:
                    self.log.info(f'No neighbors for {symbol} {i}')
                    self.rwmol.RemoveAtom(i)
                elif len(neighbor_idxs) == 1:
                    self.log.debug(f'One neighbor for {symbol} {i}')
                    new_xyz = Point3D(neighbor_xyzs[0].x + shift + i/100,
                                      neighbor_xyzs[0].y + shift + i/100,
                                      neighbor_xyzs[0].z + shift + i/100)
                    conf.SetAtomPosition(i, new_xyz)
                else:
                    self.log.debug(f'Multiple neighbors for {symbol} {i}')
                    new_xyz = Point3D(sum([xyz.x for xyz in neighbor_xyzs]) / len(neighbor_xyzs),
                                      sum([xyz.y for xyz in neighbor_xyzs]) / len(neighbor_xyzs),
                                      sum([xyz.z for xyz in neighbor_xyzs]) / len(neighbor_xyzs))
                    conf.SetAtomPosition(i, new_xyz)
            self.rwmol.CommitBatchEdit()
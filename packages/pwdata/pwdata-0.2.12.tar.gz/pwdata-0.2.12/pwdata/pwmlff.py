import numpy as np
import os, glob
from tqdm import tqdm
from pwdata.image import Image

class PWNPY(object):
    def __init__(self, files):
        self.image_list:list[Image] = []
        self.load_files(files)

        assert len(self.image_list) > 0, "No data loaded!"

    def get(self):
        return self.image_list
    
    def load_files(self, files):
        # Search for .npy files in the current directory
        npy_files = glob.glob(os.path.join(files, "*.npy"))
        if not npy_files:
            npy_files = glob.glob(os.path.join(files, "*/*.npy"))

        atom_type, atomic_energy, Ep, force, atom_types_image, lattice, coord, stress, image_nums, atom_nums = self.load_npy(npy_files)
        lattice = lattice.reshape(-1, 3, 3)
        coord = coord.reshape(-1, atom_nums, 3)
        force = force.reshape(-1, atom_nums, 3)
        for i in tqdm(range(image_nums), desc="Loading data"):
            image = Image(lattice=lattice[i], position=coord[i], force=force[i], Ep=Ep[i], stress=stress[i],
                          cartesian=False, image_nums=i, atom_nums=atom_nums,
                          atomic_energy=atomic_energy[i], atom_type=atom_type, atom_types_image=atom_types_image) 
            self.image_list.append(image)

    def load_npy(self, npy_files):
        atomic_energy = None
        Ep = None
        force = None
        lattice = None
        stress = None
        coord = None
        for npy_file in npy_files:
            if "atom_type" in npy_file:
                atom_type = np.load(npy_file).squeeze()
            elif "ei" in npy_file:
                atomic_energy = np.load(npy_file) if atomic_energy is None else np.concatenate((atomic_energy, np.load(npy_file)))
            elif "energies" in npy_file:
                Ep = np.load(npy_file) if Ep is None else np.concatenate((Ep, np.load(npy_file)))
            elif "forces" in npy_file:
                force = np.load(npy_file) if force is None else np.concatenate((force, np.load(npy_file)))
            elif "image_type" in npy_file:
                atom_types_image = np.load(npy_file).squeeze()
            elif "lattice" in npy_file:
                lattice = np.load(npy_file) if lattice is None else np.concatenate((lattice, np.load(npy_file)))
            elif "virials" in npy_file:
                stress = np.load(npy_file) if stress is None else np.concatenate((stress, np.load(npy_file)))
            elif "position" in npy_file:
                coord = np.load(npy_file) if coord is None else np.concatenate((coord, np.load(npy_file)))

        image_nums = len(Ep)
        atom_nums = len(atom_types_image)
        stress = stress.reshape(-1, 3, 3) if stress is not None else None

        return atom_type, atomic_energy.squeeze(), Ep.squeeze(), force.squeeze(), atom_types_image, lattice.squeeze(), coord.squeeze(), stress, image_nums, atom_nums

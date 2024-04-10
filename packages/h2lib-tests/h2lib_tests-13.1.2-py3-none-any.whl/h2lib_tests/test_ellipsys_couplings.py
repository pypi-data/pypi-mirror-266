from h2lib._h2lib import MultiH2Lib
import numpy as np
from wetb.hawc2.htc_file import HTCFile
from numpy import newaxis as na
from h2lib_tests.test_files import tfp


class Ellipsys():
    def __init__(self):
        self.time = 0

    def get_uvw(self, pos_xyz_lst):
        uvw = np.array(pos_xyz_lst) * 0
        uvw[:, :, 0] = 6
        return uvw.tolist()

    def step(self):
        self.time += .2
        return self.time

    def set_fxyz(self, pos_xyz, fxyz):
        print(self.time, np.shape(pos_xyz), np.shape(fxyz))
        pass


def test_ellipsys_dummy_workflow():

    N = 4
    with MultiH2Lib(N, suppress_output=True) as h2:
        el = Ellipsys()
        htc = HTCFile(tfp + 'DTU_10_MW/htc/DTU_10MW_RWT.htc')
        for i in range(N):
            htc.set_name(f'wt{i}')
            htc.save()

        h2.read_input(htc_path=[f'htc/wt{i}.htc' for i in range(N)],
                      model_path=tfp + 'DTU_10_MW')
        wt_pos = np.array([[0, 0, 0], [0, 500, 0], [0, 1000, 0], [0, 1500, 0]])

        h2.init()

        while True:
            t = el.step()
            h2.run(t)
            pos_gl_xyz = np.array(h2.get_aerosections_position(), order='F') + wt_pos[:, na, na, :]
            uvw = np.asfortranarray(el.get_uvw(pos_gl_xyz))
            h2.set_aerosections_windspeed(uvw)
            frc_gl_xyz = h2.get_aerosections_forces()
            el.set_fxyz(pos_gl_xyz, frc_gl_xyz)
            if t == 1:
                break

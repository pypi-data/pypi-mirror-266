from h2lib._h2lib import H2Lib, MultiH2Lib

from numpy import testing as npt
import pytest
from wetb.gtsdf import gtsdf

from h2lib_tests.dtu10mw import DTU10MW
from h2lib_tests.test_files import tfp
import matplotlib.pyplot as plt
import numpy as np


def get_h2(htc_path='htc/DTU_10MW_RWT.htc'):
    h2 = H2Lib(suppress_output=True)
    h2.read_input(htc_path=htc_path, model_path=tfp + 'DTU_10_MW')
    return h2


@pytest.fixture(scope='module')
def h2():
    h2 = get_h2()
    h2.init()
    h2.step()
    yield h2
    h2.close()


def test_get_nxxx(h2):
    assert h2.get_rotor_dims() == [[50, 50, 50]]


def test_get_bem_grid_dim(h2):
    assert h2.get_bem_grid_dim() == [16, 50]


def test_get_bem_grid(h2):
    azi, rad = h2.get_bem_grid()

    npt.assert_array_almost_equal(np.roll(np.linspace(-np.pi, np.pi, 17)[1:], 9), azi)
    npt.assert_array_almost_equal([3.09929662, 11.4350243, 33.76886193, 60.8641887, 82.01217305], rad[::10])


def test_induction(h2):
    h2.suppress_output = False
    azi, rad = h2.get_bem_grid()
    induc_grid = h2.get_induction_polargrid()
    induc_axisymmetric = h2.get_induction_axisymmetric()
    induc_rotoravg = h2.get_induction_rotoravg()
    if 0:
        Azi, Rad = np.meshgrid(azi, rad)
        ax = plt.gcf().add_subplot(111, polar=True)
        ax.set_theta_zero_location('S')
        ax.set_theta_direction(-1)
        cntf = ax.contourf(Azi, Rad, induc_grid.T, 50)
        plt.colorbar(cntf)
        plt.figure()
        plt.plot(rad, induc_axisymmetric)
        plt.axhline(induc_rotoravg, color='k')
        plt.show()

    npt.assert_array_almost_equal(np.mean(induc_grid, 0), induc_axisymmetric)
    npt.assert_array_almost_equal(np.sum(np.r_[0, np.diff(rad / rad[-1])] * induc_axisymmetric), induc_rotoravg, 3)


def test_rotor_orientation_multi_instance():
    dtu10 = DTU10MW()
    dtu10.output.buffer = 1
    dtu10.output.data_format = 'gtsdf64'
    dtu10.set_name('tmp_5_0')

    dtu10.save()

    tilt_ref, yaw_ref = 6, 10
    dtu10.set_tilt_cone_yaw(tilt=tilt_ref, cone=0, yaw=yaw_ref)
    dtu10.set_name('tmp_6_10')
    dtu10.save()
    with MultiH2Lib(2, suppress_output=True) as mh2:
        mh2.read_input(['htc/tmp_5_0.htc', 'htc/tmp_6_10.htc'], model_path=tfp + "DTU_10_MW")
        # h2.suppress_output = False
        s_id = mh2.add_sensor('aero power')[0]
        mh2.init()
        yaw, tilt, _ = zip(*mh2.get_rotor_orientation())
        np.testing.assert_almost_equal(np.rad2deg(yaw), [0, 10])
        np.testing.assert_almost_equal(np.rad2deg(tilt), [5, 6])
        yaw, tilt, _ = zip(*mh2.get_rotor_orientation(deg=True))
        np.testing.assert_almost_equal(yaw, [0, 10])
        np.testing.assert_almost_equal(tilt, [5, 6])
        h2 = mh2[0]
        res = []
        for t in np.arange(0, 2.5, .01):
            h2.run(t)
            res.append([h2.get_rotor_orientation(deg=True)[0][2], h2.get_sensor_values(s_id)[0][0]] +
                       h2.get_rotor_position()[0].tolist())

        data = gtsdf.load(h2.model_path[0] + '/res/tmp_5_0.hdf5')[1]
        res = np.array(res)
        npt.assert_allclose(data[:, 0], res[1:-1, 0] % 360 - 180, rtol=0.002)  # azi
        npt.assert_array_almost_equal(data[:, 10], res[1:-1, 1])  # power
        npt.assert_array_almost_equal(data[:, 15:18], res[1:-1, 2:5])  # rotor position


def test_rotor_avg_windspeed():
    h2 = get_h2()
    h2.init_windfield(Nxyz=(2, 2, 2), dxyz=(200, 200, 200), box_offset_yz=(-100, -19), transport_speed=6)
    h2.init()
    u = np.zeros((2, 2, 2))
    u[:, 1, :] = 10  # 0 in one side, 10 in other, 5 in avg
    h2.set_windfield(np.asfortranarray([u, u * 0, u * 0]), -100)
    h2.step()
    npt.assert_almost_equal(h2.get_rotor_avg_wsp(1), [0, 5, 0])
    npt.assert_almost_equal(h2.get_rotor_avg_uvw(), [5, 0, 0])

    h2.close()


def test_aerosections():
    plot = False
    h2 = get_h2()
    # blade 1, global coo, r>30
    pos_ids = [h2.add_sensor(f'aero position 3 1 {xyz} 30')[0] for xyz in [1, 2, 3]]
    wsp_ids = [h2.add_sensor(f'aero windspeed 3 1 {xyz} 30')[0] for xyz in [1, 2, 3]]
    frc_ids = [h2.add_sensor(f'aero secforce 1 {xyz} 30 3')[0] for xyz in [1, 2, 3]]
    mom_ids = [h2.add_sensor(f'aero secmoment 1 {xyz} 30 3')[0] for xyz in [1, 2, 3]]
    h2.init()

    a = h2.get_aerosections_position()
    if plot:
        ax = plt.figure().add_subplot(projection='3d')
        for b in a:
            ax.plot(*b.T)
        plt.show()

    assert a.shape == (3, 50, 3)

    r = np.sqrt(np.sum((a[0, :] - a[0, 0])**2, 1))
    i = np.searchsorted(r, 30)

    h2.step()
    name, unit, desc = h2.get_sensor_info(pos_ids[-1])
    assert str(np.round(r[i], 2)) in desc
    assert str(np.round(r[i], 1)) in name
    assert unit == 'm'

    a = h2.get_aerosections_position()
    npt.assert_array_almost_equal(a[0, i], [h2.get_sensor_values(id) for id in pos_ids])
    uvw = a * 0
    uvw[:, :, 0] = 6
    uvw[0, i, 0] = 12
    h2.run(3)
    npt.assert_array_equal(h2.get_sensor_values(wsp_ids), [0, 6, 0])
    npt.assert_array_almost_equal(h2.get_sensor_values(frc_ids), h2.get_aerosections_forces()[0, i] / 1000)

    frc_before = h2.get_aerosections_forces()

    if plot:
        plt.figure()
        plt.plot(frc_before[:, :, 1].T)

    h2.set_aerosections_windspeed(uvw)
    h2.step()
    frc_after = h2.get_aerosections_forces()
    mom_after = h2.get_aerosections_moments()
    if plot:
        plt.plot(frc_after[:, :, 1].T, '--')
        plt.show()

    # Fy in section with u=12 instead of u=6m/s more than doubled
    assert frc_before[0, i, 1] * 2 < frc_after[0, i, 1]

    # rest is similar (within 7N/m, max Fxyz along blade is [331 , 378, 288]
    frc_after[0, i, :] = frc_before[0, i, :]
    npt.assert_allclose(frc_before, frc_after, atol=7)
    h2.close()


def test_iea15MW():
    with H2Lib(suppress_output=True) as h2:
        h2.read_input(htc_path='htc/IEA_15MW_RWT_Onshore.htc', model_path=tfp + 'IEA-15-240-RWT-Onshore')
        h2.init()
        h2.step()
        npt.assert_allclose(h2.get_diameter(), 240.806, atol=0.001)

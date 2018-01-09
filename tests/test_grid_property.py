import pytest
import os
from timeit import default_timer as timer

from xtgeo.grid3d import Grid
from xtgeo.grid3d import GridProperty
from xtgeo.common import XTGeoDialog

from .test_xtg import assert_equal, assert_almostequal

path = 'TMP'
try:
    os.makedirs(path)
except OSError:
    if not os.path.isdir(path):
        raise

# set default level
xtg = XTGeoDialog()

logger = xtg.basiclogger(__name__)

# =============================================================================
# Do tests
# =============================================================================

testfile1 = '../xtgeo-testdata/3dgrids/gfb/gullfaks2_poro.roff'
testfile2 = '../xtgeo-testdata/3dgrids/eme/1/emerald_hetero.roff'
testfile3 = '../xtgeo-testdata/3dgrids/bri/B.GRID'
testfile4 = '../xtgeo-testdata/3dgrids/bri/B.INIT'
testfile5 = '../xtgeo-testdata/3dgrids/gfb/GULLFAKS.EGRID'
testfile6 = '../xtgeo-testdata/3dgrids/gfb/GULLFAKS.INIT'
testfile7 = '../xtgeo-testdata/3dgrids/gfb/gullfaks2_zone.roff'
testfile8 = '../xtgeo-testdata/3dgrids/gfb/gullfaks2.roff'
testfile9 = '../xtgeo-testdata/3dgrids/gfb/gullfaks2_poro.roff'
testfile10 = '../xtgeo-testdata/3dgrids/bri/b_grid.roff'
testfile11 = '../xtgeo-testdata/3dgrids/bri/b_poro.roff'
testfile12 = '../xtgeo-testdata/3dgrids/gfb/GULLFAKS_R003B-0.EGRID'
testfile13 = '../xtgeo-testdata/3dgrids/gfb/GULLFAKS_R003B-0.INIT'
testfile14 = '../xtgeo-testdata/3dgrids/gfb/GULLFAKS_R003B-0.UNRST'


def test_create():
    x = GridProperty()
    assert x.ncol == 5, 'NCOL'
    assert x.nrow == 12, 'NROW'

    m = GridProperty(discrete=True)
    (repr(m.values))


def test_roffbin_import1():

    logger.info('Name is {}'.format(__name__))

    x = GridProperty()
    logger.info("Import roff...")
    x.from_file(testfile1, fformat="roff", name='PORO')

    logger.info(repr(x.values))
    logger.info(x.values.dtype)
    logger.info("Mean porosity is {}".format(x.values.mean()))
    assert x.values.mean() == pytest.approx(0.26256, abs=0.001)


def test_roffbin_import2():
    """Import roffbin, with several props in one file."""

    logger.info('Name is {}'.format(__name__))
    dz = GridProperty()
    logger.info("Import roff...")
    dz.from_file(testfile2, fformat="roff", name='Z_increment')

    logger.info(repr(dz.values))
    logger.info(dz.values.dtype)
    logger.info("Mean DZ is {}".format(dz.values.mean()))

    hc = GridProperty()
    logger.info("Import roff...")
    hc.from_file(testfile2, fformat="roff", name='Oil_HCPV')

    logger.info(repr(hc.values))
    logger.info(hc.values.dtype)
    logger.info(hc.values3d.shape)
    ncol, nrow, nlay = hc.values3d.shape

    assert nrow == 100, 'NROW from shape (Emerald)'

    logger.info("Mean HCPV is {}".format(hc.values.mean()))


def test_eclinit_import():
    """Property import from Eclipse. Needs a grid object first. Eclipse GRID"""

    logger.info('Name is {}'.format(__name__))
    gg = Grid(testfile3, fformat="grid")
    po = GridProperty()
    logger.info("Import INIT...")
    po.from_file(testfile4, fformat="init", name='PORO', grid=gg,
                 apiversion=2)

    assert po.ncol == 20, 'NX from B.INIT'

    logger.debug(po.values[0:400])
    assert float(po.values3d[1:2, 13:14, 0:1]) == \
        pytest.approx(0.17146, abs=0.001), 'PORO in cell 2 14 1'

    # discrete prop
    eq = GridProperty(testfile4, fformat="init", name='EQLNUM', grid=gg)
    logger.info(eq.values[0:400])
    assert eq.values3d[12:13, 13:14, 0:1] == 3, 'EQLNUM in cell 13 14 1'


def test_eclinit_import_gull():
    """Property import from Eclipse. Gullfaks"""

    # let me guess the format (shall be egrid)
    gg = Grid(testfile5, fformat='egrid')
    assert gg.ncol == 99, "Gullfaks NX"

    logger.info("Import INIT...")
    po = GridProperty(testfile6, name='PORO', grid=gg)

    logger.info(po.values.mean())
    logger.info(po.values[500:900])
    assert po.values.mean() == pytest.approx(0.261157181168, abs=0.0001)

    pv = GridProperty(testfile6, name='PORV', grid=gg)
    logger.info(pv.values.mean())
    logger.info(pv.values[500:900])


def test_eclunrst_import_gull():
    """Property UNRST import from Eclipse. Gullfaks"""

    gg = Grid(testfile12, fformat='egrid')

    logger.info("Import RESTART (UNIFIED) ...")
    press = GridProperty(testfile14, name='PRESSURE', fformat='unrst',
                         date=19950101, grid=gg)

    assert_almostequal(press.values.mean(), 279.8029, 0.0001)

def test_export_roff():
    """Property import from Eclipse. Then export to roff."""

    gg = Grid()
    gg.from_file(testfile3, fformat="grid")
    po = GridProperty()
    logger.info("Import INIT...")
    po.from_file(testfile4, fformat="init", name='PORO', grid=gg, apiversion=2)

    po.to_file('TMP/bdata.roff', name='PORO')
    pox = GridProperty('TMP/bdata.roff', name='PORO')

    print(po.values.mean())

    assert po.values.mean() == pytest.approx(pox.values.mean(), abs=0.0001)


def test_io_roff_discrete():
    """Import ROFF discrete property; then TODO! export to ROFF int."""

    logger.info('Name is {}'.format(__name__))
    po = GridProperty()
    po.from_file(testfile7, fformat="roff", name='Zone')

    logger.info("\nCodes ({})\n{}".format(po.ncodes, po.codes))

    # tests:
    assert po.ncodes == 18
    logger.debug(po.codes[17])
    assert po.codes[17], "SEQ2"

    # export to ROFF ...TODO!
    # po.to_file("TMP/zone.roff")


def test_get_all_corners():
    """Get X Y Z for all corners as XTGeo GridProperty objects"""

    grid = Grid(testfile8)
    allc = grid.get_xyz_corners()

    x0 = allc[0]
    y0 = allc[1]
    z0 = allc[2]
    x1 = allc[3]
    y1 = allc[4]
    z1 = allc[5]

    # top of cell layer 2 in cell 41 41 (if 1 index start as RMS)
    assert x0.values3d[40, 40, 1] == pytest.approx(455116.76, abs=0.01)
    assert y0.values3d[40, 40, 1] == pytest.approx(6787710.22, abs=0.01)
    assert z0.values3d[40, 40, 1] == pytest.approx(1966.31, abs=0.01)

    assert x1.values3d[40, 40, 1] == pytest.approx(455215.26, abs=0.01)
    assert y1.values3d[40, 40, 1] == pytest.approx(6787710.60, abs=0.01)
    assert z1.values3d[40, 40, 1] == pytest.approx(1959.87, abs=0.01)


def test_get_cell_corners():
    """Get X Y Z for one cell as tuple"""

    grid = Grid(testfile8)
    clist = grid.get_xyz_cell_corners(ijk=(40, 40, 1))


def test_get_xy_values_for_webportal():
    """Get lists on webportal format"""

    grid = Grid(testfile8)
    prop = GridProperty(testfile9, grid=grid, name='PORO')

    start = timer()
    logger.info('Start time: {}'.format(start))
    coord, valuelist = prop.get_xy_value_lists(grid=grid)
    end = timer()
    logger.info('End time: {}. Elapsed {}'.format(end, end - start))

    grid = Grid(testfile10)
    prop = GridProperty(testfile11, grid=grid, name='PORO')

    coord, valuelist = prop.get_xy_value_lists(grid=grid, mask=False)

    logger.info('Cell 1 1 1 coords\n{}.'.format(coord[0][0]))
    assert coord[0][0][0] == (454.875, 318.5)
    assert valuelist[0][0] == -999.0


def test_get_xy_values_for_webportal_ecl():
    """Get lists on webportal format (Eclipse input)"""

    grid = Grid(testfile12)
    prop = GridProperty(testfile13, grid=grid, name='PORO')

    start = timer()
    logger.info('Start time: {}'.format(start))
    coord, valuelist = prop.get_xy_value_lists(grid=grid)
    end = timer()
    logger.info('End time: {}. Elapsed {}'.format(end, end - start))

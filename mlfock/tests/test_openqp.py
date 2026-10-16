"""Tests against a real OpenQP install (skipped when pyoqp is missing)."""

import numpy as np
import scipy.linalg
import pytest

oqp = pytest.importorskip("oqp", reason="OpenQP (pyoqp) not installed")

from mlfock.basis import BasisLayout
from mlfock.extract import (record_from_openqp, fock_from_orbitals, write_simple_mrsf_reference,
                            read_simple_mrsf_reference)
from mlfock.oqp_bridge import OpenQPOracle, rohf_config
from tests.synthetic import random_rotation

ANG = 1.0 / 0.52917721067
WATER = np.array([[0.0, 0.0, 0.1173], [0.0, 0.7572, -0.4692], [0.0, -0.7572, -0.4692]]) * ANG
Z = np.array([8, 1, 1])


@pytest.fixture(scope="module")
def oracle(tmp_path_factory):
    return OpenQPOracle(rohf_config("bhhlyp", "6-31g*"), workdir=str(tmp_path_factory.mktemp("oqp")))


@pytest.fixture(scope="module")
def water(oracle):
    return oracle(Z, WATER, tag="water")


def test_record_is_consistent(water):
    rec = water
    assert rec.F_ref.shape == (3, 19, 19) and rec.shells[8][-1] == (2, "cart")
    eps, C = scipy.linalg.eigh(rec.F_ref[0], rec.S)
    assert np.allclose(eps, rec.eps, atol=1e-8)
    assert rec.n_occ_alpha == 6 and rec.n_occ_beta == 4
    assert np.abs(rec.F_ref[1] - rec.F_ref[2]).max() > 0.1          # open shell: alpha != beta
    assert np.allclose(rec.F_base, rec.F_base.T)


def test_layout_rotation_matches_openqp(oracle, water):
    R = random_rotation(np.random.RandomState(5))
    rot = oracle(Z, WATER @ R.T, tag="rot")
    D = water.layout().full_rotation(R)
    assert np.allclose(D @ water.S @ D.T, rot.S, atol=1e-10)
    assert np.allclose(D @ water.F_base @ D.T, rot.F_base, atol=1e-8)
    assert np.allclose(D @ water.F_ref[1] @ D.T, rot.F_ref[1], atol=2e-4)   # SCF/grid noise


def test_reference_file_roundtrip(water, tmp_path):
    rec = water
    eps, C = scipy.linalg.eigh(rec.F_ref[0], rec.S)
    path = tmp_path / "ref.bin"
    write_simple_mrsf_reference(path, rec.S, C, eps, rec.F_ref[1], rec.F_ref[2], rec.layout(),
                                rec.n_occ_alpha, rec.n_occ_beta)
    r = read_simple_mrsf_reference(path)
    assert np.allclose(r["S"], rec.S) and np.allclose(r["Fa"], rec.F_ref[1])
    assert list(r["ao_atom"][:15]) == [1] * 15 and list(r["ao_l"][:15]) == [0, 0, 1, 1, 1, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2]
    assert r["occ_a"].sum() == 6 and r["occ_b"].sum() == 4

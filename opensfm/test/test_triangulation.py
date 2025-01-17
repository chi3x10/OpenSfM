import numpy as np
from opensfm import io
from opensfm import pygeometry
from opensfm import pymap
from opensfm import reconstruction


def test_track_triangulator_spherical() -> None:
    """Test triangulating tracks of spherical images."""
    tracks_manager = pymap.TracksManager()
    tracks_manager.add_observation("im1", "1", pymap.Observation(0, 0, 1.0, 0, 0, 0, 0))
    tracks_manager.add_observation(
        "im2", "1", pymap.Observation(-0.1, 0, 1.0, 0, 0, 0, 1)
    )

    rec = io.reconstruction_from_json(
        {
            "cameras": {
                "theta": {
                    "projection_type": "spherical",
                    "width": 800,
                    "height": 400,
                }
            },
            "shots": {
                "im1": {
                    "camera": "theta",
                    "rotation": [0.0, 0.0, 0.0],
                    "translation": [0.0, 0.0, 0.0],
                },
                "im2": {
                    "camera": "theta",
                    "rotation": [0, 0, 0.0],
                    "translation": [-1, 0, 0.0],
                },
            },
            "points": {},
        }
    )

    triangulator = reconstruction.TrackTriangulator(
        rec, reconstruction.TrackHandlerTrackManager(tracks_manager, rec)
    )
    triangulator.triangulate("1", 0.01, 2.0, 10)
    assert "1" in rec.points
    p = rec.points["1"].coordinates
    assert np.allclose(p, [0, 0, 1.3763819204711])
    assert len(rec.points["1"].get_observations()) == 2


def unit_vector(x: object):
    return np.array(x) / np.linalg.norm(x)


def test_triangulate_bearings_dlt() -> None:
    rt1 = np.append(np.identity(3), [[0], [0], [0]], axis=1)
    rt2 = np.append(np.identity(3), [[-1], [0], [0]], axis=1)
    b1 = unit_vector([0.0, 0, 1])
    b2 = unit_vector([-1.0, 0, 1])
    max_reprojection = 0.01
    min_ray_angle = np.radians(2.0)
    res, X = pygeometry.triangulate_bearings_dlt(
        # pyre-fixme[6]: For 2nd param expected `ndarray` but got `List[typing.Any]`.
        [rt1, rt2], [b1, b2], max_reprojection, min_ray_angle
    )
    assert np.allclose(X, [0, 0, 1.0])
    assert res is True


def test_triangulate_bearings_midpoint() -> None:
    o1 = np.array([0.0, 0, 0])
    b1 = unit_vector([0.0, 0, 1])
    o2 = np.array([1.0, 0, 0])
    b2 = unit_vector([-1.0, 0, 1])
    max_reprojection = 0.01
    min_ray_angle = np.radians(2.0)
    valid_triangulation, X = pygeometry.triangulate_bearings_midpoint(
        # pyre-fixme[6]: For 1st param expected `ndarray` but got `List[ndarray]`.
        # pyre-fixme[6]: For 2nd param expected `ndarray` but got `List[typing.Any]`.
        [o1, o2], [b1, b2], 2 * [max_reprojection], min_ray_angle
    )
    assert np.allclose(X, [0, 0, 1.0])
    assert valid_triangulation is True


def test_triangulate_two_bearings_midpoint() -> None:
    o1 = np.array([0.0, 0, 0])
    b1 = unit_vector([0.0, 0, 1])
    o2 = np.array([1.0, 0, 0])
    b2 = unit_vector([-1.0, 0, 1])
    # pyre-fixme[6]: For 1st param expected `ndarray` but got `List[ndarray]`.
    # pyre-fixme[6]: For 2nd param expected `ndarray` but got `List[typing.Any]`.
    ok, X = pygeometry.triangulate_two_bearings_midpoint([o1, o2], [b1, b2])
    assert ok is True
    assert np.allclose(X, [0, 0, 1.0])


def test_triangulate_two_bearings_midpoint_failed() -> None:
    o1 = np.array([0.0, 0, 0])
    b1 = unit_vector([0.0, 0, 1])
    o2 = np.array([1.0, 0, 0])

    # almost parralel. 1e-5 will make it triangulate again.
    b2 = b1 + np.array([-1e-10, 0, 0])

    # pyre-fixme[6]: For 1st param expected `ndarray` but got `List[ndarray]`.
    # pyre-fixme[6]: For 2nd param expected `ndarray` but got `List[typing.Any]`.
    ok, X = pygeometry.triangulate_two_bearings_midpoint([o1, o2], [b1, b2])
    assert ok is False

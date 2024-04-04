import os
from tempfile import NamedTemporaryFile

from skimage.io import load_sift, load_surf

from skimage._shared.testing import assert_equal


def test_load_sift():
    with NamedTemporaryFile(delete=False) as f:
        fname = f.name

    with open(fname, 'wb') as f:
        f.write(
            b'''2 128
    133.92 135.88 14.38 -2.732
    3 12 23 38 10 15 78 20 39 67 42 8 12 8 39 35 118 43 17 0
    0 1 12 109 9 2 6 0 0 21 46 22 14 18 51 19 5 9 41 52
    65 30 3 21 55 49 26 30 118 118 25 12 8 3 2 60 53 56 72 20
    7 10 16 7 88 23 13 15 12 11 11 71 45 7 4 49 82 38 38 91
    118 15 2 16 33 3 5 118 98 38 6 19 36 1 0 15 64 22 1 2
    6 11 18 61 31 3 0 6 15 23 118 118 13 0 0 35 38 18 40 96
    24 1 0 13 17 3 24 98
    132.36 99.75 11.45 -2.910
    94 32 7 2 13 7 5 23 121 94 13 5 0 0 4 59 13 30 71 32
    0 6 32 11 25 32 13 0 0 16 51 5 44 50 0 3 33 55 11 9
    121 121 12 9 6 3 0 18 55 60 48 44 44 9 0 2 106 117 13 2
    1 0 1 1 37 1 1 25 80 35 15 41 121 3 0 2 14 3 2 121
    51 11 0 20 93 6 0 20 109 57 3 4 5 0 0 28 21 2 0 5
    13 12 75 119 35 0 0 13 28 14 37 121 12 0 0 21 46 5 11 93
    29 0 0 3 14 4 11 99'''
        )

    # Check whether loading by filename works
    load_sift(fname)

    with open(fname) as f:
        features = load_sift(f)
    os.remove(fname)

    assert_equal(len(features), 2)
    assert_equal(len(features['data'][0]), 128)
    assert_equal(features['row'][0], 133.92)
    assert_equal(features['column'][1], 99.75)


def test_load_surf():
    with NamedTemporaryFile(delete=False) as f:
        fname = f.name

    with open(fname, 'wb') as f:
        f.write(
            b'''65
2
38.3727 62.0491 0.0371343 0 0.0371343 -1 -0.0705589 0.0130983 -0.00460534 0.132168 -0.0718833 0.0320583 -0.0134032 0.0988654 -0.0542241 0.0171002 -0.00135754 0.105755 -0.0362088 0.0151748 -0.00694272 0.0610017 -0.247091 0.109605 -0.0337623 0.0813307 -0.24185 0.278548 -0.0494523 0.107804 -0.166312 0.0691584 -0.0288199 0.138476 -0.110956 0.0280772 -0.0752509 0.0736344 -0.22667 0.164226 -0.0544717 0.0388139 -0.30194 0.33065 -0.0537507 0.0596398 -0.245395 0.110925 -0.0603322 0.0239389 -0.18726 0.0374145 -0.0355872 0.0140762 -0.129022 0.135104 -0.0703396 0.0374049 -0.24256 0.222544 -0.0536354 0.0501252 -0.209004 0.0971316 -0.0550094 0.0229767 -0.125547 0.0317879 -0.0291574 0.0124569
68.5773 61.474 0.0313267 0 0.0313267 1 -0.10198 0.130987 -0.0321845 0.0487543 -0.0900435 0.121113 -0.100917 0.0444702 -0.0151742 0.107604 -0.0542035 0.014069 -0.00594097 0.0339933 -0.00994295 0.0127262 -0.125613 0.192551 -0.0174399 0.0433488 -0.272698 0.164641 -0.0676735 0.0467444 -0.0527907 0.258005 -0.0818114 0.0440569 -0.0104433 0.0548934 -0.0323454 0.0145296 -0.112357 0.199223 -0.0532903 0.0332622 -0.342481 0.207469 -0.0526129 0.0741355 -0.256234 0.402708 -0.108296 0.117362 -0.0560274 0.128856 -0.123509 0.0510046 -0.0198793 0.0775934 -0.103863 0.00406679 -0.10264 0.1312 -0.108244 0.0812913 -0.127868 0.182924 -0.0680942 0.071913 -0.0858004 0.144806 -0.0176522 0.0686146'''
        )

    # Check whether loading by filename works
    load_surf(fname)

    with open(fname) as f:
        features = load_surf(f)
    os.remove(fname)

    assert_equal(len(features), 2)
    assert_equal(len(features['data'][0]), 64)
    assert_equal(features['column'][1], 68.5773)
    assert_equal(features['row'][0], 62.0491)

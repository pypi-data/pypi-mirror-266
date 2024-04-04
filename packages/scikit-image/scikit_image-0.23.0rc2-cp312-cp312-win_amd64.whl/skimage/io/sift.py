import numpy as np

__all__ = ['load_sift', 'load_surf']


def _sift_read(filelike, mode='SIFT'):
    """Read SIFT or SURF features from externally generated file.

    This routine reads SIFT or SURF files generated by binary utilities from
    http://people.cs.ubc.ca/~lowe/keypoints/ and
    http://www.vision.ee.ethz.ch/~surf/.

    This routine *does not* generate SIFT/SURF features from an image. These
    algorithms are patent encumbered. Please use :obj:`skimage.feature.CENSURE`
    instead.

    Parameters
    ----------
    filelike : string or open file
        Input file generated by the feature detectors from
        http://people.cs.ubc.ca/~lowe/keypoints/ or
        http://www.vision.ee.ethz.ch/~surf/ .
    mode : {'SIFT', 'SURF'}, optional
        Kind of descriptor used to generate `filelike`.

    Returns
    -------
    data : record array with fields
        - row: int
            row position of feature
        - column: int
            column position of feature
        - scale: float
            feature scale
        - orientation: float
            feature orientation
        - data: array
            feature values

    """
    if isinstance(filelike, str):
        f = open(filelike)
        filelike_is_str = True
    else:
        f = filelike
        filelike_is_str = False

    if mode == 'SIFT':
        nr_features, feature_len = map(int, f.readline().split())
        datatype = np.dtype(
            [
                ('row', float),
                ('column', float),
                ('scale', float),
                ('orientation', float),
                ('data', (float, feature_len)),
            ]
        )
    else:
        mode = 'SURF'
        feature_len = int(f.readline()) - 1
        nr_features = int(f.readline())
        datatype = np.dtype(
            [
                ('column', float),
                ('row', float),
                ('second_moment', (float, 3)),
                ('sign', float),
                ('data', (float, feature_len)),
            ]
        )

    data = np.fromfile(f, sep=' ')
    if data.size != nr_features * datatype.itemsize / np.dtype(float).itemsize:
        raise OSError(f'Invalid {mode} feature file.')

    # If `filelike` is passed to the function as filename - close the file
    if filelike_is_str:
        f.close()

    return data.view(datatype)


def load_sift(f):
    return _sift_read(f, mode='SIFT')


def load_surf(f):
    return _sift_read(f, mode='SURF')


load_sift.__doc__ = _sift_read.__doc__
load_surf.__doc__ = _sift_read.__doc__

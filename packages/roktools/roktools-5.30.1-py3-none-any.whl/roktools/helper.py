import numpy


def add_field_in_numpy_array(a: numpy.array, descr) -> numpy.array:
    """Return a new array that is like "a", but has additional fields.

    Arguments:
      a     -- a structured numpy array
      descr -- a numpy type description of the new fields

    The contents of "a" are copied over to the appropriate fields in
    the new array, whereas the new fields are uninitialized.  The
    arguments are not modified.

    >>> sa = numpy.array([(1, 'Foo'), (2, 'Bar')], dtype=[('id', '<i8'), ('name', '|S3')])
    >>> sa.dtype.descr
    [('id', '<i8'), ('name', '|S3')]

    >>> sb = add_field_in_numpy_array(sa, [('score', '<f8')])
    >>> sb.dtype.descr
    [('id', '<i8'), ('name', '|S3'), ('score', '<f8')]

    >>> numpy.all(sa['id'] == sb['id'])
    True
    >>> numpy.all(sa['name'] == sb['name'])
    True
    """
    if a.dtype.fields is None:
        raise ValueError("'A' must be a structured numpy array")
    b = numpy.empty(a.shape, dtype=a.dtype.descr + descr)
    for name in a.dtype.names:
        b[name] = a[name]
    return b

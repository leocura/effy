from Effy.filesystem import RWops

def test_rwops_read():
    rw = RWops(data=b"hello world")
    rw2, data = rw.read(5)
    assert data == b"hello"
    assert rw2.position == 5

def test_rwops_write():
    rw = RWops(data=b"hello")
    rw2 = rw.seek(0, 2) # seek to end
    rw3 = rw2.write(b" world")
    assert rw3.data == b"hello world"
    assert rw3.position == 11

def test_rwops_seek():
    rw = RWops(data=b"hello world")
    rw2 = rw.seek(6, 0)
    assert rw2.position == 6
    rw3, data = rw2.read(5)
    assert data == b"world"

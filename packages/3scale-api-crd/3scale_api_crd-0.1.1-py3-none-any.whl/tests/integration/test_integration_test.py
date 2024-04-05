import pytest

@pytest.fixture(scope='module')
def back():
    print("\nsetup back")
    yield object()
    print("\nteardown back")

@pytest.fixture(scope='module')
def mapp(back):
    print("\nsetup mapp")
    yield object()
    print("\nteardown mapp")

def test_test(back, mapp):
    assert True
    print("\ntest")

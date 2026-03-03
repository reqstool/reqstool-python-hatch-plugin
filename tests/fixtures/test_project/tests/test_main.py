from reqstool_python_decorators.decorators.decorators import SVCs

from mypackage.main import hello


@SVCs("SVC_001")
def test_hello():
    assert hello() == "hello"

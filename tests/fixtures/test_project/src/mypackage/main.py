from reqstool_python_decorators.decorators.decorators import Requirements


@Requirements("REQ_001")
def hello():
    return "hello"

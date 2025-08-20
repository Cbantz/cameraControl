filename = "hello"

def test(addition : str = None):
    filepath = f"{filename}/{addition}" if addition else filename
    print(filepath)

test()
test("world")



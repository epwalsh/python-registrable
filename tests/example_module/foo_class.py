from registrable import Registrable


class Foo(Registrable):
    def do_something(self):
        raise NotImplementedError

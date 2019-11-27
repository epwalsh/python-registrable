from example_module.foo_class import Foo


class FooUnregistered(Foo):
    def do_something(self):
        return "Am I registered?"

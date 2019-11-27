from example_module.foo_class import Foo


@Foo.register("foo_a")
class FooA(Foo):
    def do_something(self):
        return "a"

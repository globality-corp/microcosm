from microcosm.opaque import Opaque

opaque = Opaque()

print "first example: ==============="
print opaque.data_func()

def special_opaque_data(some, stuff):
    return "{} {}".format(some, stuff)

some = "some"
stuff = "stuff"

with opaque.opaque_data(special_opaque_data, some, stuff):
    print opaque.data_func()

print opaque.data_func()

print "second example: ============="

class Mouse(object):
    def __init__(self, opaque):
        self.opaque = opaque

    def do_something_and_log_something(self):
        print "I am doing something. Extra info: {}".format(
            self.opaque.data_func()
        )

mouse = Mouse(opaque)
mouse.do_something_and_log_something()

with opaque.opaque_data(special_opaque_data, some, stuff):
    mouse.do_something_and_log_something()

mouse.do_something_and_log_something()

print "decorator example ======="

mouse.do_something_and_log_something()
opaque.opaque_data(special_opaque_data, some, stuff)(mouse.do_something_and_log_something)()
mouse.do_something_and_log_something()

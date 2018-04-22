from pynini import Scope, parent_scope

class Network(Scope):
    def __init__(self):
        super().__init__()

    @classmethod
    def fits(cls, obj):
        return True


@parent_scope(Network)
class Rhost(Scope):
    def __init__(self):
        super().__init__()

    @classmethod
    def fits(cls, obj):
        return 'ip' in obj

    @staticmethod
    def get_bin_value(obj):
        return obj['ip']

    @classmethod
    def why_not_fit(cls, obj):
        return "does not contain an 'ip' member"


@parent_scope(Rhost)
class Process(Scope):
    def __init__(self):
        super().__init__()

    @classmethod
    def fits(cls, obj):
        return 'pid' in obj

    @staticmethod
    def get_bin_value(obj):
        return obj['pid']

    @classmethod
    def why_not_fit(cls, obj):
        return "does not contain a 'pid' member"

@parent_scope(Process)
class Module(Scope):
    def __init__(self):
        super().__init__()

    @classmethod
    def fits(cls, obj):
        return 'filepath' in obj

    @staticmethod
    def get_bin_value(obj):
        return obj['filepath']

    @classmethod
    def why_not_fit(cls, obj):
        return "does not contain a 'filepath' member"


@parent_scope(Rhost)
class File(Scope):
    def __init__(self):
        super().__init__()

    @classmethod
    def fits(cls, obj):
        return 'filepath' in obj

    @staticmethod
    def get_bin_value(obj):
        return obj['filepath']

    @classmethod
    def why_not_fit(cls, obj):
        return "does not contain a 'filepath' member"


if __name__ == '__main__':
    n = Network()

    # print(Network.get_subscopes())
    # print(Rhost.get_subscopes())

    n.add_object({'ip': '123.456.789.0', 'pid': 123, 'port': 80})
    n.add_object({'ip': '123.456.789.0', 'pid': 123, 'hash': 'xyz'})
    n.add_object({'ip': '123.456.789.1', 'pid': 123, 'filepath': '/a/b/c'})

    print(
        "Object {'pid': 123} cannot be *properly* sorted as a Module because:")
    for source, reason in Module.reasons_for_no_fit({'pid': 123}):
        print("    Cannot be a/an {} because it {}".format(source.__name__,
                                                           reason))

    n.add_object({'pid': 123})

    print(n)
    # print(len(n))

    # print([
    #     proc.flatten()
    #     for proc in n.get_all(Process, 123)
    # ])

    # print([
    #     proc.flatten(use_set=True)
    #     for proc in n.get_all(Process, {'port': 80})
    # ])

    # print(n[Rhost]['123.456.789.0'][Process][123])

    import json
    print(json.dumps(n.flatten(use_set=True), indent=2))

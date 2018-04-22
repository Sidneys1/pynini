def parent_scope(parent_cls):
    def inner(cls):
        cls.add_parent_scope(parent_cls)
        parent_cls.add_subscope(cls)
        return cls
    return inner


class Scope(object):
    def __init__(self):
        self.__bins = {}
        self.__ownobjs = []
        for subscope in self.get_subscopes():
            self.__bins[subscope] = {}

    @classmethod
    def add_subscope(cls, subscope):
        if not hasattr(cls, 'SUBSCOPES'):
            cls.SUBSCOPES = []
        cls.SUBSCOPES.append(subscope)

    @classmethod
    def add_parent_scope(cls, pscope):
        if not hasattr(cls, 'PARENT_SCOPES'):
            cls.PARENT_SCOPES = []
        cls.PARENT_SCOPES.append(pscope)

    def add_object(self, obj):
        scopes = self.get_subscopes()
        added = False
        for subscope in scopes:
            if subscope.rfits(obj):
                if subscope.fits(obj):
                    binvalue = subscope.get_bin_value(obj)
                else:
                    binvalue = None
                if binvalue not in self.__bins[subscope]:
                    self.__bins[subscope][binvalue] = subscope()
                self.__bins[subscope][binvalue].add_object(obj)
                added = True
        if not scopes or not added:
            self.__ownobjs.append(obj)
            return

    @classmethod
    def fits(cls, obj):
        pass

    @classmethod
    def rfits(cls, obj):
        if cls.fits(obj):
            return True
        for subscope in cls.get_subscopes():
            if subscope.rfits(obj):
                return True
        return False

    @classmethod
    def reasons_for_no_fit(cls, obj):
        reasons = []
        for pscope in cls.get_parent_scopes():
            r = pscope.reasons_for_no_fit(obj)
            for reason in r:
                reasons.append(reason)
        if not cls.fits(obj):
            reasons.append((cls, cls.why_not_fit(obj)))
        return reasons

    @classmethod
    def why_not_fit(cls, obj):
        pass

    @staticmethod
    def get_bin_value(obj):
        '''Returns a binning value from `obj`'''
        pass

    @classmethod
    def get_subscopes(cls):
        if not hasattr(cls, 'SUBSCOPES'):
            cls.SUBSCOPES = []
        return cls.SUBSCOPES

    @classmethod
    def get_parent_scopes(cls):
        if not hasattr(cls, 'PARENT_SCOPES'):
            cls.PARENT_SCOPES = []
        return cls.PARENT_SCOPES

    def __len__(self):
        return (len(self.__ownobjs) +
                sum([len(y)
                     for x in self.__bins.values()
                     for y in x.values()]))

    def as_dict(self):
        ret = {}
        if self.__ownobjs:
            ret['objs'] = self.__ownobjs
        if self.__bins:
            ret.update({
                k.__name__: {
                    x: y.as_dict() for x, y in v.items()
                } for k, v in self.__bins.items()
            })

        return ret



    def __repr__(self):
        import json

        return json.dumps(self.as_dict(), indent=2)

    def matches(self, obj):
        flat = self.flatten()
        for k, v in obj.items():
            if k not in flat:
                return False
            if v not in flat[k]:
                return False
        return True

    def get_all(self, cls, uniq=None):
        if cls in self.__bins:
            if uniq is not None:
                if isinstance(uniq, dict):
                    return [
                        x
                        for x in self.__bins[cls].values()
                        if x.matches(uniq)
                    ]
                if uniq not in self.__bins[cls]:
                    return []
                return [self.__bins[cls][uniq]]
            return self.__bins[cls].values()
        ret = [match
               for bins in self.__bins.values()
               for bin in bins.values()
               for match in bin.get_all(cls, uniq)]
        return ret

    def get_kv(self):
        for o in self.__ownobjs:
            for k, v in o.items():
                yield k, v
        for bins in self.__bins.values():
            for bin in bins.values():
                for i in bin.get_kv():
                    yield i

    def flatten(self, use_set=False):
        ret = {}
        for k,v in self.get_kv():
            if k not in ret:
                ret[k] = set() if use_set else []
            if use_set:
                ret[k].add(v)
            else:
                ret[k].append(v)
        if use_set:
            return { k: list(v) for k, v in ret.items() }
        return ret

    def __getitem__(self, key):
        return self.__bins[key]




__all__ = ['parent_scope', 'Scope']

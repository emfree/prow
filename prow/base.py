import copy
import attr



def type_(objtype=None):
    if objtype is None:
        return attr.ib()

    return attr.ib(validator=objtype.validate,
                   convert=objtype.inflate)


def array(eltype=None):
    def validate(inst, attr, value):
        for item in value:
            if not isinstance(value, eltype):
                eltype.validate(inst, attr, item)

    def inflate(value):
        return map(eltype.inflate, value)

    return attr.ib(validator=validate, convert=inflate)


class String(object):
    @classmethod
    def validate(cls, inst, attr, value):
        if not isinstance(value, basestring):
            raise TypeError(
                'Expected value of string type for attribute {name}, '
                'got value {value!r} of type {actual!r}'
                .format(name=attr.name, actual=value.__class__, value=value)
            )

    @classmethod
    def inflate(cls, value):
        return value


class Integer(object):
    @classmethod
    def validate(cls, inst, attr, value):
        if not any(isinstance(value, type_) for type_ in (int, long)):
            raise TypeError(
                'Expected value of number type for attribute {name}, '
                'got value {value!r} of type {actual!r}'
                .format(name=attr.name, actual=value.__class__, value=value)
            )

    @classmethod
    def inflate(cls, value):
        return value



def schema(cls):
    def wrap(cl):
        _add_inflate(cl)
        _add_validate(cl)
        _add_serialize(cl)
        return attr.s(cl)
    return wrap(cls)


def _add_inflate(cls):
    if not hasattr(cls, 'inflate'):
        def inflate(cl, value):
            if isinstance(value, cl):
                return value
            return cl(**value)
        cls.inflate = classmethod(inflate)


def _add_validate(cls):
    if not hasattr(cls, 'validate'):
        def validate(cl, inst, attr, value):
            pass
        cls.validate = classmethod(validate)


def _add_serialize(cls):
    if not hasattr(cls, 'serialize'):
        def serialize(self):
            return attr.asdict(self)
        cls.serialize = serialize


# examples


@schema
class Address(object):
    name = type_(String)
    email = type_(String)


@schema
class Message(object):
    from_addr = array(Address)
    to_addr = array(Address)
    cc_addr = array(Address)
    message_id_header = type_(String)

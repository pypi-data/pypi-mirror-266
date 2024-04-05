from types import GenericAlias


def is_list(klass_type: type):
    return klass_type is list or \
        (isinstance(klass_type, GenericAlias) and issubclass(klass_type.__origin__, list))


def is_set(klass_type: type):
    return issubclass(klass_type, set) or \
        (isinstance(klass_type, GenericAlias) and issubclass(klass_type.__origin__, set))


def is_dictionary(klass_type: type):
    return issubclass(klass_type, dict) or \
        (isinstance(klass_type, GenericAlias) and issubclass(klass_type.__origin__, dict))

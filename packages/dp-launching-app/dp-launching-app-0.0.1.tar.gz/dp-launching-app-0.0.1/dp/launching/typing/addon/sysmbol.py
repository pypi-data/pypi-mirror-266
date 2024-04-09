class BasicRelationalOperator:
    @classmethod
    def __get_operator_name__(cls):
        return cls.__name__


class BasicLogicalOperator:
    @classmethod
    def __get_operator_name__(cls):
        return cls.__name__


class BasicFunction:
    @classmethod
    def __get_operator_name__(cls):
        return cls.__name__


class BasicUI:
    @classmethod
    def __get_operator_name__(cls):
        return cls.__name__


# 关系运算符
class Equal(BasicRelationalOperator):
    ...


class NotEqual(BasicRelationalOperator):
    ...


class Exists(BasicRelationalOperator):
    ...


class NotExists(BasicRelationalOperator):
    ...


class GreaterThan(BasicRelationalOperator):
    ...


class LessThan(BasicRelationalOperator):
    ...


class GreaterThanOrEqual(BasicRelationalOperator):
    ...


class LessThanOrEqual(BasicRelationalOperator):
    ...

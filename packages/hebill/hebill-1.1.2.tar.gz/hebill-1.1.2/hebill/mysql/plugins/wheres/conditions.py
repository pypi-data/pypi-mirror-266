from .condition import Condition


class Conditions(dict):
    def __init__(self, logic="AND"):
        super(Conditions, self).__init__({
            'logic': 'AND' if logic.upper == 'AND' else 'OR',
            'children': []
        })

    @property
    def logic(self): return self["logic"]

    @logic.setter
    def logic(self, logic: str): self["logic"] = logic
    def set_logic_and(self): self.logic = 'AND'
    def set_logic_or(self): self.logic = 'OR'

    @property
    def children(self): return self["children"]

    def add_condition(self, column=None, value=None, judge="=", logic="AND", like_left=False, like_right=False):
        c = Condition(column, value, judge, logic, like_left, like_right)
        self.children.append(c)
        return c

    def add_condition_and_equal(self, column, value=None):
        return self.add_condition(column, value, "=", "AND")

    def add_condition_or_equal(self, column, value=None):
        return self.add_condition(column, value, "=", "OR")

    def add_condition_and_not_equal(self, column, value=None):
        return self.add_condition(column, value, "!=", "AND")

    def add_condition_and_more_than(self, column, value=None):
        return self.add_condition(column, value, ">", "AND")

    def add_condition_and_not_more_than(self, column, value=None):
        return self.add_condition(column, value, "<=", "AND")

    def add_condition_and_less_than(self, column, value=None):
        return self.add_condition(column, value, "<", "AND")

    def add_condition_and_not_less_than(self, column, value=None):
        return self.add_condition(column, value, ">=", "AND")

    def add_condition_and_like(self, column, value=None, like_left=False, like_right=False):
        return self.add_condition(column, value, "LIKE", "AND", like_left, like_right)

    def add_condition_or_like(self, column, value=None, like_left=False, like_right=False):
        return self.add_condition(column, value, "LIKE", "OR", like_left, like_right)

    def add_conditions(self, logic="AND"):
        c = Conditions(logic)
        self.children.append(c)
        return c

    def add_conditions_and(self):
        return self.add_conditions("AND")

    def add_conditions_or(self):
        return self.add_conditions("OR")

    def output(self, logic_bridge_required=False):
        s = ""
        for ss in self.children:
            s += ss.output(bool(s))
        if not s.strip():
            return ""
        if not logic_bridge_required:
            return " " + s
        return f" {self.logic} ({s})"

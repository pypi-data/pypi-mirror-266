from .conditions import Conditions


class Wheres(Conditions):
    def output(self, logic_bridge_required=False):
        string = super().output()
        return f' WHERE{string}' if string else ""

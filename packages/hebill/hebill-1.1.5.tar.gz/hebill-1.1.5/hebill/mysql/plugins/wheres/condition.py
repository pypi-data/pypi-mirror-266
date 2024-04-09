class Condition(dict):
    def __init__(self, column, value, judge="=", logic="AND", left_blurred=False, right_blurred=False):
        super(Condition, self).__init__({
            "column": column,
            "value": value,
            "judge": judge,
            "logic": 'AND' if logic.upper == 'AND' else 'OR',
            "left_blurred": left_blurred,
            "right_blurred": right_blurred
        })

    @property
    def column(self): return self["column"]

    @column.setter
    def column(self, column: str): self["column"] = column

    @property
    def value(self): return self["value"]

    @value.setter
    def value(self, value: str | int | float): self["value"] = value

    @property
    def judge(self): return self["judge"]

    def set_judge_equal(self): self.judge = '='
    def set_judge_un_equal(self): self.judge = '!='
    def set_judge_less_than(self): self.judge = '<'
    def set_judge_more_than(self): self.judge = '>'
    def set_judge_un_less_than(self): self.judge = '>='
    def set_judge_un_more_than(self): self.judge = '<='
    def set_judge_like(self): self.judge = 'LIKE'
    def set_judge_regexp(self): self.judge = 'REGEXP'
    def set_judge_in_null(self): self.judge = 'IS NULL'
    def set_judge_is_not_null(self): self.judge = 'IS NOT NULL'
    # TODO 需要更新解析语言
    def set_judge_in(self): self.judge = 'IN'
    # TODO 需要更新解析语言
    def set_judge_not_in(self): self.judge = 'NOT IN'
    # TODO 需要更新解析语言
    def set_judge_between_and(self): self.judge = 'BETWEEN AND'
    # TODO 需要更新解析语言
    def set_judge_spatial(self): self.judge = 'SPATIAL'
    # TODO 需要更新解析语言
    def set_judge_sounds_like(self): self.judge = 'SOUNDS LIKE'

    @judge.setter
    def judge(self, judge: str): self["judge"] = judge

    @property
    def logic(self): return self["logic"]

    @logic.setter
    def logic(self, logic: str): self["logic"] = logic
    def set_logic_and(self): self.logic = 'AND'
    def set_logic_or(self): self.logic = 'OR'

    @property
    def left_blurred(self): return self["left_blurred"]

    @left_blurred.setter
    def left_blurred(self, blurred: bool): self["left_blurred"] = blurred
    def set_left_blurred(self): self.left_blurred = True
    def set_un_left_blurred(self): self.left_blurred = False

    @property
    def right_blurred(self): return self["right_blurred"]

    @right_blurred.setter
    def right_blurred(self, blurred: bool): self["right_blurred"] = blurred
    def set_right_blurred(self): self.right_blurred = True
    def set_un_right_blurred(self): self.right_blurred = False

    def output(self, logic_bridge_required=False):
        if not self.column:
            return " "
        s = f'`{self.column}` {self.judge} "'
        if self.judge == "LIKE" and self.left_blurred:
            s += "%"
        s += str(self.value)
        if self.judge == "LIKE" and self.right_blurred:
            s += "%"
        s += '"'
        if logic_bridge_required:
            s += " " + self.logic + " " + s
        return s

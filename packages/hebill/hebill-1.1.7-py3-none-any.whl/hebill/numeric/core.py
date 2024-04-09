from .constants import *
import decimal


class Numeric:
    def __init__(self, number: int | float | decimal.Decimal | str):
        self._input = number
        self._error = ''
        try:
            self._number = round(decimal.Decimal(number), 3)
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            self._number = 0
            self._error = e
        self._decimal_str = None
        self._integer_str = None
        self._capitalize_decimal_cn_num = None
        self._capitalize_decimal_cn_xxx = None
        self._capitalize_integer_cn_num = None
        self._capitalize_integer_cn_xxx = None
        self._ten_thousands_breaks = None
        self._thousands_breaks = None
        self._capitalize_cn_num = None
        self._capitalize_cn_xxx = None
        self._capitalize_cn_cny = None
        self._capitalize_cn_usd = None
        self._capitalize_cn_eur = None
        self._capitalize_decimal_en_num = None
        self._capitalize_decimal_en_xxx = None
        self._capitalize_decimal_en_usd = None
        self._capitalize_integer_en_num = None
        self._capitalize_integer_en_xxx = None
        self._capitalize_integer_en_cny = None
        self._capitalize_integer_en_usd = None
        self._capitalize_en_num = None
        self._capitalize_en_xxx = None
        self._capitalize_en_cny = None
        self._capitalize_en_usd = None
        self._capitalize_en_eur = None

    @property
    def input(self):
        return self._input

    @property
    def number(self):
        return self._number

    @property
    def error(self):
        return self._error

    # 分解整数和小数部分字符串
    def _generate_integer_decimal_str(self):
        n = str(self._number)
        self._integer_str, self._decimal_str = n.split('.') if '.' in n else [n, '']
        self._decimal_str = self._decimal_str.rstrip('0')

    @property  # 小数部分字符串
    def decimal_str(self):
        if self._decimal_str is None:
            self._generate_integer_decimal_str()
        return self._decimal_str

    @property  # 整数部分字符串
    def integer_str(self):
        if self._integer_str is None:
            self._generate_integer_decimal_str()
        return self._integer_str

    @property  # 万分位分组
    def ten_thousands_breaks(self):
        if self._ten_thousands_breaks is None:
            groups = []
            for i in range(len(self.integer_str), 0, -4):
                groups.append(self.integer_str[max(i - 4, 0):i])
            if len(groups) > len(CN_DECIMAL_4S_UNITS) + 1:
                self._error = f'Number "{self.number}" is exceed the limit.'
            # 分组正向
            groups.reverse()
            # 第一组不足4位时在前面用0补齐
            groups[0] = f"{groups[0]:0>4}"
            self._ten_thousands_breaks = groups
        return self._ten_thousands_breaks

    @property  # 千分位分组
    def thousands_breaks(self):
        if self._thousands_breaks is None:
            groups = []
            for i in range(len(self.integer_str), 0, -3):
                groups.append(self.integer_str[max(i - 3, 0):i])
            if len(groups) > len(EN_DECIMAL_3S_UNITS) + 1:
                self._error = f'Number "{self.number}" is exceed the limit.'
            # 分组正向
            groups.reverse()
            # 第一组不足4位时在前面用0补齐
            groups[0] = f"{groups[0]:0>3}"
            self._thousands_breaks = groups
        return self._thousands_breaks

    # 从万分位分组中取数字转为中文大写
    def _generate_capital_cn_by_group_serial_number_serial(self, group_serial_number, number_serial_number):
        capital = f'{CN_INTEGER_0_TO_9[int(self.ten_thousands_breaks[group_serial_number][number_serial_number])]}'
        if self.ten_thousands_breaks[group_serial_number][number_serial_number] != '0' and number_serial_number < 3:
            capital += f'{CN_DECIMAL_UNITS[2 - number_serial_number]}'
        return capital

    @property  # 数字小数中文大写
    def capitalize_decimal_cn_num(self):
        if self._capitalize_decimal_cn_num is None:
            self._capitalize_decimal_cn_num = ''
            for i in range(0, len(self._decimal_str)):
                self._capitalize_decimal_cn_num += CN_INTEGER_0_TO_9[int(self._decimal_str[i])]
        return self._capitalize_decimal_cn_num

    @property  # 数字整数中文大写
    def capitalize_integer_cn_num(self):
        if self._capitalize_integer_cn_num is None:
            # 设定前面判断字符是不是非0
            first_zero = True
            last_zero = False
            self._capitalize_integer_cn_num = ''
            groups_quantity = len(self.ten_thousands_breaks)
            for group_serial_number in range(0, groups_quantity):
                capitals = ''
                group = self.ten_thousands_breaks[group_serial_number]
                for number_serial_number in range(4):
                    if group[number_serial_number] != '0':
                        if last_zero and not first_zero:
                            capitals += CN_INTEGER_0_TO_9[0]
                        capitals += self._generate_capital_cn_by_group_serial_number_serial(
                            group_serial_number, number_serial_number)
                        first_zero = False
                        last_zero = False
                    else:
                        last_zero = True
                self._capitalize_integer_cn_num += capitals
                if group_serial_number < groups_quantity - 1:
                    self._capitalize_integer_cn_num += \
                        f'{CN_DECIMAL_4S_UNITS[groups_quantity - group_serial_number - 2]}'
        return self._capitalize_integer_cn_num

    @property  # 数字中文大写
    def capitalize_cn_num(self):
        if self._capitalize_cn_num is None:
            self._capitalize_cn_num = self.capitalize_integer_cn_num
            if self.capitalize_decimal_cn_num != '':
                self._capitalize_cn_num += CN_POINT_NAME + self.capitalize_decimal_cn_num
        return self._capitalize_cn_num

    @property  # 货币小数中文大写
    def capitalize_decimal_cn_xxx(self):
        if self._capitalize_decimal_cn_xxx is None:
            self._capitalize_decimal_cn_xxx = ''
            for i in range(0, len(self.decimal_str)):
                self._capitalize_decimal_cn_xxx += CN_INTEGER_0_TO_9[int(self.decimal_str[i])] + CN_POINTS_UNITS[i]
            if len(self.decimal_str) == 1:
                self._capitalize_decimal_cn_xxx += CN_INTEGER_0_TO_9[0] + CN_POINTS_UNITS[1]
        return self._capitalize_decimal_cn_xxx

    @property  # 货币整数中文大写
    def capitalize_integer_cn_xxx(self):
        if self._capitalize_integer_cn_xxx is None:
            self._capitalize_integer_cn_xxx = f'{self.capitalize_integer_cn_num}{CN_CURRENCY_UNIT}'
            if self.capitalize_decimal_cn_xxx == '':
                self._capitalize_integer_cn_xxx += CN_ONLY_NAME
        return self._capitalize_integer_cn_xxx

    @property  # 货币中文大写
    def capitalize_cn_xxx(self):
        if self._capitalize_cn_xxx is None:
            self._capitalize_cn_xxx = f'{self.capitalize_integer_cn_xxx}{self.capitalize_decimal_cn_xxx}'
        return self._capitalize_cn_xxx

    @property  # 人民币中文大写
    def capitalize_cn_cny(self):
        if self._capitalize_cn_cny is None:
            self._capitalize_cn_cny = f'{CN_CNY_NAME}{self.capitalize_cn_xxx}'
        return self._capitalize_cn_cny

    @property  # 美元中文大写
    def capitalize_cn_usd(self):
        if self._capitalize_cn_usd is None:
            self._capitalize_cn_usd = f'{CN_USD_NAME}{self.capitalize_cn_xxx}'
        return self._capitalize_cn_usd

    @property  # 欧元中文大写
    def capitalize_cn_eur(self):
        if self._capitalize_cn_eur is None:
            self._capitalize_cn_eur = f'{CN_EUR_NAME}{self.capitalize_cn_xxx}'
        return self._capitalize_cn_eur

    @property  # 数字小数英文大写
    def capitalize_decimal_en_num(self):
        if self._capitalize_decimal_en_num is None:
            data = []
            for i in range(0, len(self._decimal_str)):
                data.append(EN_INTEGER_0_TO_9[int(self._decimal_str[i])])
            self._capitalize_decimal_en_num = ' '.join(data)
        return self._capitalize_decimal_en_num

    def _generate_capital_en_check_add_and(self, group_serial_number, number_serial_number):
        g = self.thousands_breaks[group_serial_number]
        for i in range(number_serial_number + 1, 2):
            if g[i] != '0':
                return True
        if group_serial_number < len(self.thousands_breaks) - 1:
            for i in range(group_serial_number + 1, len(self._decimal_str)):
                for j in self.thousands_breaks[i]:
                    if j != 0:
                        return True
        return False

    def _generate_capital_en_by_group(self, group_serial_number):
        g = self.thousands_breaks[group_serial_number]
        caps = []
        if g[0] != '0':
            caps.append(EN_INTEGER_0_TO_9[int(g[0])])
            caps.append(EN_HUNDRED_NAME)
            if self._generate_capital_en_check_add_and(group_serial_number, 0):
                caps.append('and')
            caps.extend(self._generate_capital_en_by_group_2(group_serial_number))
        else:
            caps.extend(self._generate_capital_en_by_group_2(group_serial_number))
        return caps

    def _generate_capital_en_by_group_2(self, group_serial_number):
        g = self.thousands_breaks[group_serial_number]
        caps = []
        if int(g[1]) >= 2:
            caps.append(EN_INTEGER_2NS[int(g[1]) - 2])
            caps.extend(self._generate_capital_en_by_group_1(group_serial_number))
        elif g[1] == '1':
            caps.append(EN_INTEGER_1NS[int(g[2])])
        else:
            caps.extend(self._generate_capital_en_by_group_1(group_serial_number))
        return caps

    def _generate_capital_en_by_group_1(self, group_serial_number):
        g = self.thousands_breaks[group_serial_number]
        caps = []
        if g[2] != '0':
            caps.append(EN_INTEGER_0_TO_9[int(g[2])])
        return caps

    @property  # 数字整数英文大写
    def capitalize_integer_en_num(self):
        groups_quantity = len(self.thousands_breaks)
        if self._capitalize_integer_en_num is None:
            caps = []
            for i in range(0, len(self.thousands_breaks)):
                caps.extend(self._generate_capital_en_by_group(i))
                if i < groups_quantity - 1:
                    caps.append(EN_DECIMAL_3S_UNITS[groups_quantity - i - 2])
            self._capitalize_integer_en_num = ' '.join(caps)
        return self._capitalize_integer_en_num

    @property  # 数字英文大写
    def capitalize_en_num(self):
        if self._capitalize_en_num is None:
            self._capitalize_en_num = self.capitalize_integer_en_num
            if self.capitalize_decimal_en_num != '':
                self._capitalize_en_num += f' {EN_POINT_NAME} {self.capitalize_decimal_en_num}'
        return self._capitalize_en_num

    @property
    def capitalize_integer_en_xxx(self):
        return self.capitalize_integer_en_num

    @property
    def capitalize_decimal_en_xxx(self):
        if self._capitalize_decimal_en_xxx is None:
            self._capitalize_decimal_en_xxx = ''
            caps = []
            qnt = len(self.decimal_str)
            for i in range(0, qnt):
                if qnt > 1 and i == qnt - 1:
                    caps.append('and')
                if qnt > 2 and i == 1:
                    caps[-1] = caps[-1] + ','
                caps.append(EN_INTEGER_0_TO_9[int(self.decimal_str[i])])
                caps.append(EN_POINTS_UNITS[i])
                if int(self.decimal_str[i]) > 1:
                    caps[-1] = caps[-1] + 's'
            self._capitalize_decimal_en_xxx = ' '.join(caps)
        return self._capitalize_decimal_en_xxx

    @property
    def capitalize_en_xxx(self):
        if self._capitalize_en_xxx is None:
            self._capitalize_en_xxx = self.capitalize_integer_en_xxx
            if self.capitalize_decimal_en_xxx != '':
                self._capitalize_en_xxx += f' and {self.capitalize_decimal_en_xxx}'
        return self._capitalize_en_xxx

    @property
    def capitalize_en_cny(self):
        if self._capitalize_en_cny is None:
            self._capitalize_en_cny = f'{EN_CNY_NAME} {self.capitalize_en_xxx}'
        return self._capitalize_en_cny

    @property
    def capitalize_en_usd(self):
        if self._capitalize_en_usd is None:
            self._capitalize_en_usd = f'{EN_USD_NAME} {self.capitalize_en_xxx}'
        return self._capitalize_en_usd

    @property
    def capitalize_en_eur(self):
        if self._capitalize_en_eur is None:
            self._capitalize_en_eur = f'{EN_EUR_NAME} {self.capitalize_en_xxx}'
        return self._capitalize_en_eur

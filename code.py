#!/usr/bin/env python3
import sys

class Term:
    """项：表示 a * x^b * sin^c(x) * cos^d(x)"""
    __slots__ = ('a', 'b', 'c', 'd')

    def __init__(self, a: int = 0, b: int = 0, c: int = 0, d: int = 0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __eq__(self, other) -> bool:
        return self.b == other.b and self.c == other.c and self.d == other.d

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Poly:
    """多项式：由若干 Term 组成"""
    __slots__ = ('terms',)

    def __init__(self, size_or_terms=None):
        if isinstance(size_or_terms, int):
            self.terms = [Term() for _ in range(size_or_terms)]
        elif isinstance(size_or_terms, list):
            self.terms = size_or_terms[:]
        else:
            self.terms = []

    def __len__(self) -> int:
        return len(self.terms)

    def simplify(self) -> None:
        """合并同类项"""
        self.terms.sort(key=lambda t: (t.b, t.c, t.d), reverse=True)

        if not self.terms:
            return

        merged = []
        i = 0
        while i < len(self.terms):
            current = Term(self.terms[i].a, self.terms[i].b, self.terms[i].c, self.terms[i].d)
            j = i + 1
            while j < len(self.terms) and self.terms[j] == current:
                current.a += self.terms[j].a
                j += 1
            if current.a != 0:
                merged.append(current)
            i = j

        self.terms = merged

    def __add__(self, other: 'Poly') -> 'Poly':
        result_terms = [Term(t.a, t.b, t.c, t.d) for t in self.terms]
        result_terms.extend([Term(t.a, t.b, t.c, t.d) for t in other.terms])
        result = Poly(result_terms)
        result.simplify()
        return result

    def __sub__(self, other: 'Poly') -> 'Poly':
        result_terms = [Term(t.a, t.b, t.c, t.d) for t in self.terms]
        result_terms.extend([Term(-t.a, t.b, t.c, t.d) for t in other.terms])
        result = Poly(result_terms)
        result.simplify()
        return result

    def __mul__(self, other: 'Poly') -> 'Poly':
        result_terms = []
        for t1 in self.terms:
            for t2 in other.terms:
                new_term = Term(
                    t1.a * t2.a,
                    t1.b + t2.b,
                    t1.c + t2.c,
                    t1.d + t2.d
                )
                result_terms.append(new_term)

        result = Poly(result_terms)
        result.simplify()
        return result

    def __copy__(self) -> 'Poly':
        return Poly([Term(t.a, t.b, t.c, t.d) for t in self.terms])

    def derivate(self) -> 'Poly':
        """对多项式求导"""
        result_terms = []

        for t in self.terms:
            if t.b > 0:
                result_terms.append(Term(t.a * t.b, t.b - 1, t.c, t.d))
            if t.c > 0:
                result_terms.append(Term(t.a * t.c, t.b, t.c - 1, t.d + 1))
            if t.d > 0:
                result_terms.append(Term(-t.a * t.d, t.b, t.c + 1, t.d - 1))

        result = Poly(result_terms)
        result.simplify()
        return result


class Frac:
    """分式：p / q"""
    __slots__ = ('p', 'q')

    def __init__(self, arg1=None, arg2=None):
        if arg1 is None:
            self.p = Poly()
            self.q = Poly()
        elif isinstance(arg1, int):
            self.p = Poly([Term(arg1, 0, 0, 0)])
            self.q = Poly([Term(1, 0, 0, 0)])
        elif isinstance(arg1, Term):
            self.p = Poly([Term(arg1.a, arg1.b, arg1.c, arg1.d)])
            self.q = Poly([Term(1, 0, 0, 0)])
        elif isinstance(arg1, Poly) and isinstance(arg2, Poly):
            self.p = arg1.__copy__()
            self.q = arg2.__copy__()
        else:
            raise TypeError("Invalid Frac constructor arguments")

    def __add__(self, other: 'Frac') -> 'Frac':
        new_p = self.p * other.q + other.p * self.q
        new_q = self.q * other.q
        return Frac(new_p, new_q)

    def __sub__(self, other: 'Frac') -> 'Frac':
        new_p = self.p * other.q - other.p * self.q
        new_q = self.q * other.q
        return Frac(new_p, new_q)

    def __mul__(self, other: 'Frac') -> 'Frac':
        new_p = self.p * other.p
        new_q = self.q * other.q
        return Frac(new_p, new_q)

    def __truediv__(self, other: 'Frac') -> 'Frac':
        new_p = self.p * other.q
        new_q = self.q * other.p
        return Frac(new_p, new_q)

    def derivate(self) -> 'Frac':
        p_prime = self.p.derivate()
        q_prime = self.q.derivate()
        new_p = p_prime * self.q - q_prime * self.p
        new_q = self.q * self.q
        return Frac(new_p, new_q)

    def output(self) -> str:
        def format_term(t: Term) -> str:
            parts = []

            if t.b == 0 and t.c == 0 and t.d == 0:
                return str(abs(t.a))
            elif abs(t.a) != 1:
                parts.append(str(abs(t.a)))

            if t.b > 0:
                if t.b == 1:
                    parts.append('x')
                else:
                    parts.append(f'x^{t.b}')

            if t.c > 0:
                if t.c == 1:
                    parts.append('sinx')
                else:
                    parts.append(f'sin^{t.c}x')

            if t.d > 0:
                if t.d == 1:
                    parts.append('cosx')
                else:
                    parts.append(f'cos^{t.d}x')

            return ''.join(parts)

        def format_poly(poly: Poly) -> str:
            if not poly.terms:
                return '0'

            result = []
            for i, t in enumerate(poly.terms):
                term_str = format_term(t)
                if i == 0:
                    if t.a < 0:
                        result.append('-' + term_str)
                    else:
                        result.append(term_str)
                else:
                    if t.a < 0:
                        result.append('-' + term_str)
                    else:
                        result.append('+' + term_str)

            return ''.join(result)

        if not self.p.terms:
            return '0'

        p_str = format_poly(self.p)

        if len(self.q.terms) == 1 and self.q.terms[0].a == 1 and \
           self.q.terms[0].b == 0 and self.q.terms[0].c == 0 and self.q.terms[0].d == 0:
            return p_str

        q_str = format_poly(self.q)

        if len(self.p.terms) > 1:
            p_str = f'({p_str})'
        if len(self.q.terms) > 1:
            q_str = f'({q_str})'

        return f'{p_str}/{q_str}'


def parse_term(s: str, start: int, end: int) -> Term:
    """解析一个项 s[start:end]"""
    i = start

    # 解析系数
    coeff = 1
    neg = False

    if i < end and s[i] == '-':
        neg = True
        i += 1
    elif i < end and s[i] == '+':
        i += 1

    # 读取数字系数
    num_start = i
    while i < end and s[i].isdigit():
        i += 1

    if i > num_start:
        coeff = int(s[num_start:i])

    if neg:
        coeff = -coeff

    # 解析 x, sinx, cosx
    b, c, d = 0, 0, 0

    while i < end:
        if i + 4 <= end and s[i:i+4] == 'sinx':
            i += 4
            if i < end and s[i] == '^':
                i += 1
                exp_start = i
                while i < end and s[i].isdigit():
                    i += 1
                c = int(s[exp_start:i])
            else:
                c = 1
        elif i + 4 <= end and s[i:i+4] == 'cosx':
            i += 4
            if i < end and s[i] == '^':
                i += 1
                exp_start = i
                while i < end and s[i].isdigit():
                    i += 1
                d = int(s[exp_start:i])
            else:
                d = 1
        elif s[i] == 'x':
            i += 1
            if i < end and s[i] == '^':
                i += 1
                exp_start = i
                while i < end and s[i].isdigit():
                    i += 1
                b = int(s[exp_start:i])
            else:
                b = 1
        else:
            i += 1

    # 如果没有任何变量，系数部分已经包含全部
    if b == 0 and c == 0 and d == 0 and num_start == start:
        # 这是纯常数
        pass

    return Term(coeff, b, c, d)


def parse_poly(s: str, l: int, r: int) -> Poly:
    """解析多项式（加减项）"""
    terms = []
    i = l

    while i < r:
        # 找下一个加减号（不在括号内）
        j = i
        if i < r and s[i] in '+-':
            j = i + 1
        else:
            j = i

        # 向后查找，直到遇到下一个 +- 或结束
        while j < r and s[j] not in '+-':
            j += 1

        # 解析 s[i:j]
        if i < j:
            term = parse_term(s, i, j)
            terms.append(term)

        i = j

    poly = Poly(terms)
    poly.simplify()
    return poly


def find_paren(s: str, pos: int) -> int:
    """找到与 pos 处左括号匹配的右括号"""
    depth = 1
    i = pos + 1
    while i < len(s):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(s) - 1


def find_op(s: str, l: int, r: int, ops: list) -> int:
    """从右向左找第一个不在括号内的运算符"""
    depth = 0
    for i in range(r - 1, l - 1, -1):
        if s[i] == ')':
            depth += 1
        elif s[i] == '(':
            depth -= 1
        elif depth == 0 and s[i] in ops:
            return i
    return -1


def dfs(s: str, l: int, r: int) -> Frac:
    """递归下降解析"""
    # 去掉外层括号
    while l < r and s[l] == '(' and find_paren(s, l) == r - 1:
        l += 1
        r -= 1

    # 找 + -
    pos = find_op(s, l, r, ['+', '-'])
    if pos != -1:
        left = dfs(s, l, pos)
        right = dfs(s, pos + 1, r)
        return left + right if s[pos] == '+' else left - right

    # 找 * /
    pos = find_op(s, l, r, ['*', '/'])
    if pos != -1:
        left = dfs(s, l, pos)
        right = dfs(s, pos + 1, r)
        return left * right if s[pos] == '*' else left / right

    # 基础情况
    poly = parse_poly(s, l, r)
    return Frac(poly, Poly([Term(1, 0, 0, 0)]))


def solve(s: str) -> None:
    n = len(s)
    frac = dfs(s, 0, n)
    print(frac.output())

    frac_prime = frac.derivate()
    print(frac_prime.output())


def main():
    expr = sys.stdin.readline().strip()
    solve(expr)


if __name__ == "__main__":
    main()

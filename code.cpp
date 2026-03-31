#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <cstring>
using namespace std;

struct Term {
    int a, b, c, d;  // a * x^b * sin^c(x) * cos^d(x)

    Term(int _a = 0, int _b = 0, int _c = 0, int _d = 0) : a(_a), b(_b), c(_c), d(_d) {}

    bool operator==(const Term& other) const {
        return b == other.b && c == other.c && d == other.d;
    }

    bool operator<(const Term& other) const {
        if (b != other.b) return b > other.b;
        if (c != other.c) return c > other.c;
        return d > other.d;
    }
};

struct Poly {
    vector<Term> terms;

    void simplify() {
        sort(terms.begin(), terms.end());
        vector<Term> result;

        for (int i = 0; i < terms.size(); ) {
            Term cur = terms[i];
            int j = i + 1;
            while (j < terms.size() && terms[j] == cur) {
                cur.a += terms[j].a;
                j++;
            }
            if (cur.a != 0) {
                result.push_back(cur);
            }
            i = j;
        }

        terms = result;
    }

    Poly operator+(const Poly& other) const {
        Poly result;
        result.terms = terms;
        result.terms.insert(result.terms.end(), other.terms.begin(), other.terms.end());
        result.simplify();
        return result;
    }

    Poly operator-(const Poly& other) const {
        Poly result;
        result.terms = terms;
        for (const auto& t : other.terms) {
            result.terms.push_back(Term(-t.a, t.b, t.c, t.d));
        }
        result.simplify();
        return result;
    }

    Poly operator*(const Poly& other) const {
        Poly result;
        for (const auto& t1 : terms) {
            for (const auto& t2 : other.terms) {
                result.terms.push_back(Term(t1.a * t2.a, t1.b + t2.b, t1.c + t2.c, t1.d + t2.d));
            }
        }
        result.simplify();
        return result;
    }

    Poly derivate() const {
        Poly result;
        for (const auto& t : terms) {
            if (t.b > 0) {
                result.terms.push_back(Term(t.a * t.b, t.b - 1, t.c, t.d));
            }
            if (t.c > 0) {
                result.terms.push_back(Term(t.a * t.c, t.b, t.c - 1, t.d + 1));
            }
            if (t.d > 0) {
                result.terms.push_back(Term(-t.a * t.d, t.b, t.c + 1, t.d - 1));
            }
        }
        result.simplify();
        return result;
    }
};

struct Frac {
    Poly p, q;

    Frac() {}
    Frac(const Poly& _p, const Poly& _q) : p(_p), q(_q) {}

    Frac operator+(const Frac& other) const {
        Frac result;
        result.p = p * other.q + other.p * q;
        result.q = q * other.q;
        return result;
    }

    Frac operator-(const Frac& other) const {
        Frac result;
        result.p = p * other.q - other.p * q;
        result.q = q * other.q;
        return result;
    }

    Frac operator*(const Frac& other) const {
        Frac result;
        result.p = p * other.p;
        result.q = q * other.q;
        return result;
    }

    Frac operator/(const Frac& other) const {
        Frac result;
        result.p = p * other.q;
        result.q = q * other.p;
        return result;
    }

    Frac derivate() const {
        Frac result;
        Poly p_prime = p.derivate();
        Poly q_prime = q.derivate();
        result.p = p_prime * q - q_prime * p;
        result.q = q * q;
        return result;
    }

    void output() const {
        auto format_term = [](const Term& t) -> string {
            if (t.b == 0 && t.c == 0 && t.d == 0) {
                return to_string(abs(t.a));
            }

            string result;
            if (abs(t.a) != 1) {
                result += to_string(abs(t.a));
            }

            if (t.b > 0) {
                result += "x";
                if (t.b > 1) {
                    result += "^" + to_string(t.b);
                }
            }

            if (t.c > 0) {
                if (t.c > 1) {
                    result += "sin^" + to_string(t.c);
                } else {
                    result += "sin";
                }
                result += "x";
            }

            if (t.d > 0) {
                if (t.d > 1) {
                    result += "cos^" + to_string(t.d);
                } else {
                    result += "cos";
                }
                result += "x";
            }

            return result;
        };

        auto format_poly = [&](const Poly& poly) -> string {
            if (poly.terms.empty()) {
                return "0";
            }

            string result;
            for (int i = 0; i < poly.terms.size(); i++) {
                const auto& t = poly.terms[i];
                string term_str = format_term(t);

                if (i == 0) {
                    if (t.a < 0) {
                        result += "-" + term_str;
                    } else {
                        result += term_str;
                    }
                } else {
                    if (t.a < 0) {
                        result += "-" + term_str;
                    } else {
                        result += "+" + term_str;
                    }
                }
            }

            return result;
        };

        if (p.terms.empty()) {
            cout << "0\n";
            return;
        }

        string p_str = format_poly(p);

        if (q.terms.size() == 1 && q.terms[0].a == 1 &&
            q.terms[0].b == 0 && q.terms[0].c == 0 && q.terms[0].d == 0) {
            cout << p_str << "\n";
            return;
        }

        string q_str = format_poly(q);

        if (p.terms.size() > 1) {
            p_str = "(" + p_str + ")";
        }
        if (q.terms.size() > 1) {
            q_str = "(" + q_str + ")";
        }

        cout << p_str << "/" << q_str << "\n";
    }
};

string s;

int get_number(int l, int r) {
    if (l >= r) return 1;

    bool neg = false;
    int start = l;

    if (s[l] == '-') {
        neg = true;
        start = l + 1;
    } else if (s[l] == '+') {
        start = l + 1;
    }

    int num = 0;
    bool hasDigit = false;
    for (int i = start; i < r && isdigit(s[i]); i++) {
        num = num * 10 + (s[i] - '0');
        hasDigit = true;
    }

    if (!hasDigit) return neg ? -1 : 1;
    return neg ? -num : num;
}

Term get_term(int l, int r) {
    int i = l;

    // Parse coefficient
    int start = i;
    if (i < r && (s[i] == '-' || s[i] == '+')) {
        i++;
    }
    while (i < r && isdigit(s[i])) {
        i++;
    }

    int coeff = get_number(start, i);

    // Parse x, sin, cos
    int b = 0, c = 0, d = 0;

    while (i < r) {
        if (i + 3 <= r && s.substr(i, 3) == "sin") {
            i += 3;
            if (i < r && s[i] == '^') {
                i++;
                int exp_start = i;
                while (i < r && isdigit(s[i])) {
                    i++;
                }
                c = stoi(s.substr(exp_start, i - exp_start));
            } else {
                c = 1;
            }
            if (i < r && s[i] == 'x') {
                i++;
            }
        } else if (i + 3 <= r && s.substr(i, 3) == "cos") {
            i += 3;
            if (i < r && s[i] == '^') {
                i++;
                int exp_start = i;
                while (i < r && isdigit(s[i])) {
                    i++;
                }
                d = stoi(s.substr(exp_start, i - exp_start));
            } else {
                d = 1;
            }
            if (i < r && s[i] == 'x') {
                i++;
            }
        } else if (s[i] == 'x') {
            i++;
            if (i < r && s[i] == '^') {
                i++;
                int exp_start = i;
                while (i < r && isdigit(s[i])) {
                    i++;
                }
                b = stoi(s.substr(exp_start, i - exp_start));
            } else {
                b = 1;
            }
        } else {
            i++;
        }
    }

    return Term(coeff, b, c, d);
}

Poly parse_poly(int l, int r) {
    Poly result;

    int i = l;
    while (i < r) {
        int j = i;
        if (i < r && (s[i] == '+' || s[i] == '-')) {
            j = i + 1;
        } else {
            j = i;
        }

        while (j < r && s[j] != '+' && s[j] != '-') {
            j++;
        }

        if (i < j) {
            result.terms.push_back(get_term(i, j));
        }

        i = j;
    }

    result.simplify();
    return result;
}

int find_paren(int pos) {
    int depth = 1;
    int i = pos + 1;
    while (i < s.length()) {
        if (s[i] == '(') depth++;
        else if (s[i] == ')') {
            depth--;
            if (depth == 0) return i;
        }
        i++;
    }
    return s.length() - 1;
}

int find_op(int l, int r, const string& ops) {
    int depth = 0;
    for (int i = r - 1; i >= l; i--) {
        if (s[i] == ')') depth++;
        else if (s[i] == '(') depth--;
        else if (depth == 0 && ops.find(s[i]) != string::npos) {
            return i;
        }
    }
    return -1;
}

Frac dfs(int l, int r) {
    // Remove outer parentheses
    while (l < r && s[l] == '(' && find_paren(l) == r - 1) {
        l++;
        r--;
    }

    // Find + or -
    int pos = find_op(l, r, "+-");
    if (pos != -1) {
        Frac left = dfs(l, pos);
        Frac right = dfs(pos + 1, r);
        return s[pos] == '+' ? left + right : left - right;
    }

    // Find * or /
    pos = find_op(l, r, "*/");
    if (pos != -1) {
        Frac left = dfs(l, pos);
        Frac right = dfs(pos + 1, r);
        return s[pos] == '*' ? left * right : left / right;
    }

    // Base case
    Poly p = parse_poly(l, r);
    Poly q;
    q.terms.push_back(Term(1, 0, 0, 0));
    return Frac(p, q);
}

void solve() {
    Frac frac = dfs(0, s.length());
    frac.output();

    Frac frac_prime = frac.derivate();
    frac_prime.output();
}

int main() {
    getline(cin, s);
    solve();
    return 0;
}

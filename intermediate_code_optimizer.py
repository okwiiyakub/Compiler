import re


class IntermediateCodeOptimizer:
    """
    Performs basic optimization on three-address intermediate code.

    Optimizations included:
    1. Constant folding
       Example: t1 = 4 * 2  ->  t1 = 8

    2. Algebraic simplification
       Example: t2 = x + 0  ->  t2 = x
       Example: t3 = y * 1  ->  t3 = y
       Example: t4 = z * 0  ->  t4 = 0

    3. Simple copy propagation
       Example:
           t1 = x
           y = t1
       Can become:
           t1 = x
           y = x

    4. Removes repeated blank/empty instructions.
    """

    BINARY_PATTERN = re.compile(
        r"^(?P<target>[A-Za-z_]\w*)\s*=\s*(?P<left>-?\d+(?:\.\d+)?|[A-Za-z_]\w*)\s*"
        r"(?P<op>\+|-|\*|/|%|==|!=|<=|>=|<|>|&&|\|\|)\s*"
        r"(?P<right>-?\d+(?:\.\d+)?|[A-Za-z_]\w*)$"
    )

    ASSIGN_PATTERN = re.compile(
        r"^(?P<target>[A-Za-z_]\w*)\s*=\s*(?P<value>-?\d+(?:\.\d+)?|[A-Za-z_]\w*)$"
    )

    def __init__(self):
        self.original_code = []
        self.optimized_code = []
        self.optimization_notes = []

    def optimize(self, code):
        self.original_code = list(code)
        self.optimized_code = []
        self.optimization_notes = []

        simplified = []
        for instruction in self.original_code:
            instruction = instruction.strip()
            if not instruction:
                continue
            simplified.append(self.optimize_instruction(instruction))

        self.optimized_code = self.copy_propagation(simplified)
        return self.optimized_code

    def optimize_instruction(self, instruction):
        match = self.BINARY_PATTERN.match(instruction)
        if not match:
            return instruction

        target = match.group("target")
        left = match.group("left")
        op = match.group("op")
        right = match.group("right")

        if self.is_number(left) and self.is_number(right):
            folded = self.constant_fold(left, op, right)
            if folded is not None:
                new_instruction = f"{target} = {folded}"
                self.optimization_notes.append(
                    f"Constant folding: '{instruction}' -> '{new_instruction}'"
                )
                return new_instruction

        simplified = self.algebraic_simplify(target, left, op, right)
        if simplified != instruction:
            self.optimization_notes.append(
                f"Algebraic simplification: '{instruction}' -> '{simplified}'"
            )
            return simplified

        return instruction

    def copy_propagation(self, instructions):
        replacements = {}
        result = []

        for instruction in instructions:
            updated = self.apply_replacements(instruction, replacements)

            assign_match = self.ASSIGN_PATTERN.match(updated)
            if assign_match:
                target = assign_match.group("target")
                value = assign_match.group("value")

                if target != value and not self.is_number(target):
                    if target.startswith("t") and not self.is_number(value):
                        replacements[target] = value

                self.remove_invalid_replacements(replacements, target)

            result.append(updated)

        return result

    def apply_replacements(self, instruction, replacements):
        updated = instruction
        for temporary, replacement in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            new_updated = re.sub(rf"\b{re.escape(temporary)}\b", replacement, updated)
            if new_updated != updated:
                self.optimization_notes.append(
                    f"Copy propagation: '{updated}' -> '{new_updated}'"
                )
                updated = new_updated
        return updated

    def remove_invalid_replacements(self, replacements, assigned_target):
        if assigned_target in replacements:
            del replacements[assigned_target]

        to_delete = []
        for temporary, replacement in replacements.items():
            if replacement == assigned_target:
                to_delete.append(temporary)

        for temporary in to_delete:
            del replacements[temporary]

    def algebraic_simplify(self, target, left, op, right):
        if op == "+" and right == "0":
            return f"{target} = {left}"
        if op == "+" and left == "0":
            return f"{target} = {right}"

        if op == "-" and right == "0":
            return f"{target} = {left}"

        if op == "*" and right == "1":
            return f"{target} = {left}"
        if op == "*" and left == "1":
            return f"{target} = {right}"
        if op == "*" and (left == "0" or right == "0"):
            return f"{target} = 0"

        if op == "/" and right == "1":
            return f"{target} = {left}"
        if op == "/" and left == "0":
            return f"{target} = 0"

        if op == "%" and left == "0":
            return f"{target} = 0"

        return f"{target} = {left} {op} {right}"

    def constant_fold(self, left, op, right):
        left_value = self.to_number(left)
        right_value = self.to_number(right)

        try:
            if op == "+":
                result = left_value + right_value
            elif op == "-":
                result = left_value - right_value
            elif op == "*":
                result = left_value * right_value
            elif op == "/":
                if right_value == 0:
                    return None
                result = left_value / right_value
            elif op == "%":
                if right_value == 0:
                    return None
                result = left_value % right_value
            elif op == "==":
                result = int(left_value == right_value)
            elif op == "!=":
                result = int(left_value != right_value)
            elif op == "<":
                result = int(left_value < right_value)
            elif op == ">":
                result = int(left_value > right_value)
            elif op == "<=":
                result = int(left_value <= right_value)
            elif op == ">=":
                result = int(left_value >= right_value)
            elif op == "&&":
                result = int(bool(left_value) and bool(right_value))
            elif op == "||":
                result = int(bool(left_value) or bool(right_value))
            else:
                return None
        except Exception:
            return None

        return self.format_number(result)

    def is_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def to_number(self, value):
        if "." in value:
            return float(value)
        return int(value)

    def format_number(self, value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def format_code(self):
        if not self.optimized_code:
            return "<no optimized code generated>"
        return "\n".join(
            f"{index:>3}: {instruction}"
            for index, instruction in enumerate(self.optimized_code, 1)
        )

    def format_optimization_notes(self):
        if not self.optimization_notes:
            return "No optimization changes were needed."
        return "\n".join(f"- {note}" for note in self.optimization_notes)

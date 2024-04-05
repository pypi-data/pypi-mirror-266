def partOne(valueDictionary):
    calculatedValues = {}

    def evaluate_expression(expression):
        operators = ['+', '-']
        tokens = expression.split()
        stack = []
        operator = '+'
        for token in tokens:
            if token in operators:
                operator = token
            else:
                if token in calculatedValues:
                    value = calculatedValues[token]
                else:
                    value = int(token)
                if operator == '+':
                    stack.append(value)
                elif operator == '-':
                    stack.append(-value)
        return sum(stack)

    for k, v in valueDictionary.items():
        calculatedValues[k] = evaluate_expression(v)

    return calculatedValues

if __name__ == "__main__":
    evaluationDictionary = {"A": "1 + 2 - -7", "B": "A + 2", "C": "A + 2 - B - B"}
    result = partOne(evaluationDictionary)
    for key, value in result.items():
        print(f'"{key}": {value}')
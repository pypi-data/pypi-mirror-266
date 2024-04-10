class SyntaxDirectedTranslator:
    def __init__(self, text):
        self.text = text
        self.index = 0

    def get_next_token(self):
        if self.index >= len(self.text):
            return None
        token = self.text[self.index]
        self.index += 1
        return token

    def translate(self):
        result, operators = '', []
        while True:
            token = self.get_next_token()
            if token is None:
                break
            if token.isdigit():
                result += token + ' '
            elif token in '+-*/':
                while operators and operators[-1] in '*/' and token in '+-':
                    result += operators.pop() + ' '
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators[-1] != '(':
                    result += operators.pop() + ' '
                operators.pop()
        result += ' '.join(operators[::-1])
        return result.strip()

def main():
    while True:
        try:
            text = input('Enter an arithmetic expression: ')
        except EOFError:
            break
        if not text:
            continue
        translator = SyntaxDirectedTranslator(text)
        postfix_code = translator.translate()
        print('Postfix code:', postfix_code)

if __name__ == '__main__':
    main()

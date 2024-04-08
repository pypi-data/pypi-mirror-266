class Lexer:
  def __init__(self, text):
      self.text = text
      self.pos = 0

  def get_next_token(self):
      if self.pos >= len(self.text):
          return None

      current_char = self.text[self.pos]

      if current_char.isdigit():
          self.pos += 1
          return int(current_char)

      if current_char in ['+', '-', '*', '/']:
          self.pos += 1
          return current_char

      if current_char == '(' or current_char == ')':
          self.pos += 1
          return current_char

      self.pos += 1
      return None

class SyntaxDirectedTranslator:
  def __init__(self, lexer):
      self.lexer = lexer
      self.current_token = self.lexer.get_next_token()

  def translate(self):
      return self.expr()

  def expr(self):
      result = ''
      operator_stack = []

      while self.current_token is not None:
          if isinstance(self.current_token, int):
              result += str(self.current_token) + ' '

          elif self.current_token in ['+', '-']:
              while operator_stack and operator_stack[-1] in ['*', '/']:
                  result += operator_stack.pop() + ' '
              operator_stack.append(self.current_token)

          elif self.current_token in ['*', '/']:
              operator_stack.append(self.current_token)

          elif self.current_token == '(':
              operator_stack.append(self.current_token)

          elif self.current_token == ')':
              while operator_stack[-1] != '(':
                  result += operator_stack.pop() + ' '
              operator_stack.pop()  # Discard the '('

          self.current_token = self.lexer.get_next_token()

      while operator_stack:
          result += operator_stack.pop() + ' '

      return result.strip()

def main():
  while True:
      try:
          text = input('Enter an arithmetic expression: ')
      except EOFError:
          break

      if not text:
          continue

      lexer = Lexer(text)
      translator = SyntaxDirectedTranslator(lexer)
      postfix_code = translator.translate()
      print('Postfix code:', postfix_code)

if __name__ == '__main__':
  main()

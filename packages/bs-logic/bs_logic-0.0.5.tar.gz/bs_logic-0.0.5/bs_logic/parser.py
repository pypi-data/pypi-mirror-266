
import re

def tokenize(expression):
    # Define token patterns for the new symbols
    token_patterns = [
        (r'\s+', None),  # whitespace (ignored)
        (r'\&', 'AND'),
        (r'\|', 'OR'),
        (r'->|>-', 'IMP'),
        (r'-|~', 'NEG'),
        (r'\[\]|<>|\[\*\]|<\*\>', 'MODAL'),
        (r'\(', 'LPAR'),
        (r'\)', 'RPAR'),
        (r'[a-zA-Z]+', 'ATOM'),
    ]

    tokens = []
    position = 0
    while position < len(expression):
        match = None
        for pattern, token_type in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(expression, position)
            if match:
                text = match.group(0)
                if token_type:  # If the token is not whitespace
                    tokens.append((text, token_type))
                position = match.end(0)
                break
        if not match:
            raise SyntaxError(f"Unknown symbol: {expression[position]}")
    return tokens

# formula1 = "(-(P & Q) -> (R & -S))"
#formula2 = "([*]~P & <> -Q) >- R "
#formula3 = "P -> Q"
#tokens = tokenize(formula3)
#display(tokens)
#parse_expression(tokens)


def parse(tokens):
    def parse_implies(tokens):
        left, tokens = parse_or(tokens)
        if tokens and tokens[0][1] == 'IMP':
            tok = tokens[0][0]
            _, tokens = tokens[0], tokens[1:]  # Consume '->'
            right, tokens = parse_implies(tokens)  # Right-associativity
            return ((left, tok, right), tokens)
        return left, tokens

    def parse_or(tokens):
        left, tokens = parse_and(tokens)
        while tokens and tokens[0][1] == 'OR':
            tok = tokens[0][0]
            _, tokens = tokens[0], tokens[1:]  # Consume '|'
            right, tokens = parse_and(tokens)
            left = (left, tok, right)
        return left, tokens

    def parse_and(tokens):
        left, tokens = parse_unary(tokens)
        while tokens and tokens[0][1] == 'AND':
            tok = tokens[0][0]
            _, tokens = tokens[0], tokens[1:]  # Consume '&'
            right, tokens = parse_unary(tokens)
            left = ( left, tok, right)
        return left, tokens

    def parse_unary(tokens):
        #print("parse_unary:", tokens)
        tok, toktype = tokens[0]
        if tokens and (toktype == 'NEG' or toktype == 'MODAL'):
            _, tokens = tokens[0], tokens[1:]  # Consume unary operator
            expr, tokens = parse_unary(tokens)  # Unary, applies directly
            return ((tok, expr), tokens)
        return parse_atom_or_parenthesis(tokens)

    def parse_atom_or_parenthesis(tokens):
        #print("parse_atom_or_parenthesis:", tokens)
        if tokens[0][1]=='ATOM':
            return tokens[0][0] , tokens[1:]  # Variable
        elif tokens[0][1] == 'LPAR':
            _, tokens = tokens[0], tokens[1:]  # Consume '('
            expr, tokens = parse_implies(tokens)
            if tokens[0][1] == 'RPAR':
                _, tokens = tokens[0], tokens[1:]  # Consume ')'
                return expr, tokens
            else:
                raise ValueError("Expected ')'")
        else:
            raise ValueError("Unexpected token:", tokens[0])

    # Start parsing from the top-level function, assuming 'IMPLIES' has the lowest precedence
    expr, remaining_tokens = parse_implies(tokens)
    if remaining_tokens:  # No tokens should be remaining if the expression is well-formed
        raise SyntaxError( f"Unexpected tokens remaining after parsing", f"'{tokens}'",
                           "Remaining tokens: ", remaining_tokens)
    return expr

# Example usage
#tokens = ['P', '&', 'Q', '&', '(', 'R', '|', 'S', ')']
PARSE_TESTS = [
    "-> P",
    "P | Q | R -> A & B & C",
    "(P -> Q) & R",
    "A & (P -> Q)",
    "(-~P & Q) -> []R | <*>prop",
    "(P & Q & R -> S) -> T "]

def test_parse():
  for i, f in enumerate(PARSE_TESTS):
      print("------------------")
      print( f"{i:>3}: {f}")
      toks = tokenize(f)
      print(toks)
      parsef = parse(toks)
      print(parsef)
#test_parse()

def parse_sf_string( sf_string ):
  sign_map =  {'true':True, 'false': False, 't':True, 'f':False}
  sf_list = sf_string.split(',')
  sf_list = [f.strip() for f in sf_list]
  parsed = []
  for sf in sf_list:
      s_f = sf.split(':')
      if len(s_f)!=2:
          raise SyntaxError(f"Signed formula '{sf}' does not have exactly 1 ':' symbol!")
      s, f = s_f
      s, f =  (s.strip(), f.strip())
      sraw = s
      s = s.lower()
      if not s in sign_map:
        raise SyntaxError(f"Found sign: '{sraw}' --- Sign must be True, False, T or F.")
      sign = sign_map[s]
      pf = parse(tokenize(f))
      parsed.append((sign,pf))
  return parsed

#sf_string = "true :P, True: P -> (Q & R), False:R"
#parse_sf_string(sf_string)









from flask import Flask, request, jsonify, render_template
import ply.lex as lex

# Configurar Flask
app = Flask(__name__)

# Configurar el analizador léxico
tokens = [
    'PROGRAMA', 'FIN', 'LEER', 'IMPRIMIR', 'ENTERO', 'IDENTIFICADOR',
    'NUMERO', 'PARENIZQ', 'PARENDER', 'LLAVEIZQ', 'LLAVEDER',
    'PUNTOCOMA', 'COMA', 'ASIGNACION', 'MAS', 'LA', 'ES', 'VAR', 'CADENA'
]

reserved = {
    'programa': 'PROGRAMA', 'end': 'FIN', 'read': 'LEER', 'printf': 'IMPRIMIR',
    'int': 'ENTERO', 'la': 'LA', 'es': 'ES'
}

identificadores_especificos = ['suma', 'resta', 'multiplicación', 'división']

t_ignore = ' \t'
t_PARENIZQ = r'\('
t_PARENDER = r'\)'
t_LLAVEIZQ = r'\{'
t_LLAVEDER = r'\}'
t_PUNTOCOMA = r';'
t_COMA = r','
t_ASIGNACION = r'='
t_MAS = r'\+'

def t_CADENA(t):
    r'\"([^\\"]|\\.)*\"'
    cadena = t.value[1:-1]  # remove the double quotes
    palabras = cadena.split()
    new_tokens = []
    for palabra in palabras:
        if palabra in reserved:
            new_tokens.append((reserved[palabra], palabra))
        elif palabra in identificadores_especificos:
            new_tokens.append(('IDENTIFICADOR', palabra))
        else:
            new_tokens.append(('CADENA', palabra))
    t.value = new_tokens
    t.type = 'CADENA'
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    elif t.value in identificadores_especificos:
        t.type = 'IDENTIFICADOR'
    else:
        t.type = 'VAR'
    return t

def t_error(t):
    print("Carácter ilegal '%s'" % t.value[0])
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

lexer = lex.lex()

def analyze_code(code):
    lexer.lineno = 1  # Reiniciar el número de línea
    lexer.input(code)

    tokens_list = []
    for tok in lexer:
        if not tok:
            continue
        if tok.type == 'CADENA':
            for sub_token in tok.value:
                tokens_list.append((tok.lineno, sub_token[1], sub_token[0]))
        else:
            tokens_list.append((tok.lineno, tok.value, tok.type))

    return tokens_list

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.endswith('.txt'):
        code = file.read().decode('utf-8')
        tokens = analyze_code(code)
        return jsonify({
            'tokens': tokens,
            'reserved': reserved,
            'identificadores': identificadores_especificos
        })
    else:
        return jsonify({'error': 'Invalid file type'})

if __name__ == '__main__':
    app.run(debug=True)

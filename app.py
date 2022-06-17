from flask import Flask

app= Flask(__name__)


@app.route('/')
def index():
    return ('<h3>naujas puslapis</h3><br><p>cia mano puslapio atnaujinimas</p>')


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)





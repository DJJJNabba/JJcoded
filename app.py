from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/AtomicDawn')
def atomic_dawn():
    return render_template('AtomicDawn.html')

@app.route('/Certificate')
def certificate():
    return render_template('Certificate.html')

@app.route('/KeyGenie')
def key_genie():
    return render_template('KeyGenie.html')

@app.route('/MUMC')
def mumc():
    return render_template('mumc.html')

if __name__ == '__main__':
    app.run(debug=True)

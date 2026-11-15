from flask import Flask
from routes.inband_routes import inband_bp
from routes.blind_routes import blind_bp

app = Flask(__name__)

# Register blueprints for each variant
app.register_blueprint(inband_bp)
app.register_blueprint(blind_bp)

@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

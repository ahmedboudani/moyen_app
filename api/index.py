from app import app
from flask import jsonify

# هذا للتوافق مع Vercel
def handler(environ, start_response):
    return app(environ, start_response)

# للتعامل مع طلبات API
@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

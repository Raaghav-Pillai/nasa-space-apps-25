from flask import Flask, request, jsonify
from flask_cors import CORS
from prediction.predict import get_weather_prediction, get_recommendation

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/api/report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        
        # Extract data from request
        location = data.get('location', {})
        profile = data.get('profile', {})
        dates = data.get('dates', {})
        
        # Call prediction functions
        weather_data = get_weather_prediction(
            location=location,
            dates=dates
        )
        
        recommendation = get_recommendation(
            weather_data=weather_data,
            profile=profile
        )
        
        # Return combined results
        return jsonify({
            'success': True,
            'weather': weather_data,
            'recommendation': recommendation,
            'message': 'Report generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

// Azure Static Web App API Function
const { predict_hourly } = require('../../backend/prediction/predict_simple');

module.exports = async function (context, req) {
    context.log('Predict function triggered');

    if (req.method === 'POST') {
        try {
            const { date, hour = 12 } = req.body;
            
            // Call Python prediction (we'll need to use child_process)
            const { spawn } = require('child_process');
            
            const python = spawn('python', [
                'backend/prediction/predict_simple.py',
                '--date', date,
                '--hour', hour.toString()
            ]);

            let result = '';
            python.stdout.on('data', (data) => {
                result += data.toString();
            });

            python.on('close', (code) => {
                if (code === 0) {
                    context.res = {
                        status: 200,
                        body: JSON.parse(result)
                    };
                } else {
                    context.res = {
                        status: 500,
                        body: { error: 'Prediction failed' }
                    };
                }
            });
        } catch (error) {
            context.res = {
                status: 500,
                body: { error: error.message }
            };
        }
    } else {
        context.res = {
            status: 405,
            body: { error: 'Method not allowed' }
        };
    }
};

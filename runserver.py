import os
from intro_to_flask import app

port = int(os.environ.get("PORT", 3002))
app.run(debug=True, host='0.0.0.0', port=port)

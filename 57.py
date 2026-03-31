from flask import Flask, request, jsonify
import hmac
import hashlib
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key for HMAC validation (should be stored securely, e.g., in environment variables)
SECRET_KEY = os.getenv('PAYMENT_GATEWAY_SECRET_KEY', 'your_default_secret_key')

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get the signature sent by the payment gateway
    signature_header = request.headers.get('X-Payment-Signature')
    
    # Get the raw request body
    request_body = request.get_data()

    # Validate the HMAC signature
    if not validate_signature(request_body, signature_header):
        logger.warning("Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400

    # Process the transaction (e.g., log it)
    transaction = request.json
    logger.info(f"Received transaction: {transaction}")

    # Return a success response
    return jsonify({'status': 'success'}), 200

def validate_signature(request_body, signature_header):
    # Create the HMAC signature using the secret key
    expected_signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).hexdigest()

    # Compare the expected signature with the provided signature
    return hmac.compare_digest(expected_signature, signature_header)

if __name__ == '__main__':
    app.run(debug=True)
import logging
import threading
from flask import Flask, render_template, jsonify, request

class AnimationServer:
    """
    A Flask-based web server to provide the OBS browser source with animation states.
    """
    def __init__(self, host='127.0.0.1', port=8080):
        self.app = Flask(__name__, static_folder='static', template_folder='templates')
        self.host = host
        self.port = port
        self.state = {'state': 'idle'}
        self.lock = threading.Lock()

        # Define routes
        self.app.route('/')(self.index)
        self.app.route('/get_state')(self.get_state)
        self.app.route('/set_state', methods=['POST'])(self.set_state_route)

    def index(self):
        """Serves the main animation page."""
        return render_template('index.html')

    def get_state(self):
        """Endpoint for the browser to poll the current animation state."""
        with self.lock:
            return jsonify(self.state)

    def set_state_route(self):
        """Endpoint for the main application to set the animation state."""
        data = request.json
        if data and 'state' in data:
            new_state = data['state']
            if new_state in ['idle', 'speaking']:
                with self.lock:
                    self.state['state'] = new_state
                logging.info(f"Animation state set to: {new_state}")
                return jsonify({'success': True, 'message': f'State set to {new_state}'})
        return jsonify({'success': False, 'message': 'Invalid state provided'}), 400

    def run(self):
        """Runs the Flask server."""
        # Use a production-ready WSGI server in a real application,
        # but this is fine for a local-only tool.
        # Running in debug mode is not recommended for threaded apps,
        # so we set it to False.
        self.app.run(host=self.host, port=self.port, debug=False)

    def start_in_thread(self):
        """Starts the Flask server in a separate daemon thread."""
        server_thread = threading.Thread(target=self.run)
        server_thread.daemon = True
        server_thread.start()
        logging.info(f"Animation server started in a separate thread at http://{self.host}:{self.port}")
        return server_thread

# Example of how to use it (for direct testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server = AnimationServer()
    server.start_in_thread()

    # Keep the main thread alive to see the server running
    try:
        while True:
            # In a real app, the main thread would be doing other work (like running the bot)
            pass
    except KeyboardInterrupt:
        logging.info("Shutting down main thread.")

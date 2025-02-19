from waitress import serve
from src.dashboard.app import app
from src.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info(f"Starting production server on port {Config.DASHBOARD_PORT}")
    serve(
        app.server,
        host='0.0.0.0',  # Allow external connections
        port=Config.DASHBOARD_PORT,
        threads=4
    ) 
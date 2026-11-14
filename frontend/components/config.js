const localApiHost = window.location.hostname === 'localhost' ? 'localhost' : '127.0.0.1';
window.RESEARCH_API_URL = `http://${localApiHost}:8000`;

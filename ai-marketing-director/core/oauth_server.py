"""Simple HTTP server to handle OAuth callbacks"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from typing import Optional
from core.oauth import OAuthManager


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback requests"""

    oauth_manager = OAuthManager()
    received_token = None

    def do_GET(self):
        """Handle GET requests from OAuth providers"""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        # Determine platform from path
        if "/oauth/linkedin/callback" in parsed_path.path:
            platform = "linkedin"
        elif "/oauth/twitter/callback" in parsed_path.path:
            platform = "twitter"
        else:
            self.send_error(404, "Unknown OAuth callback path")
            return

        # Check for authorization code
        if "code" not in query_params or "state" not in query_params:
            self.send_error(400, "Missing code or state parameter")
            return

        code = query_params["code"][0]
        state = query_params["state"][0]

        try:
            # Exchange code for token
            token_data = self.oauth_manager.exchange_code_for_token(
                platform=platform,
                code=code,
                state=state
            )

            # Save token
            self.oauth_manager.save_token(token_data)

            # Store for CLI to retrieve
            OAuthCallbackHandler.received_token = token_data

            # Send success response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            success_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Authorization Successful</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }}
        .success-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}
        h1 {{
            color: #2d3748;
            margin-bottom: 1rem;
        }}
        p {{
            color: #4a5568;
            line-height: 1.6;
        }}
        .platform {{
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            display: inline-block;
            margin-top: 1rem;
            font-weight: 600;
        }}
        .instructions {{
            background: #f7fafc;
            padding: 1.5rem;
            border-radius: 8px;
            margin-top: 1.5rem;
            text-align: left;
        }}
        code {{
            background: #edf2f7;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Authorization Successful!</h1>
        <p>You've successfully connected your account to AI Marketing Director.</p>
        <div class="platform">{platform.upper()}</div>

        <div class="instructions">
            <p><strong>Next Steps:</strong></p>
            <ol style="text-align: left; color: #4a5568;">
                <li>Your access token has been saved securely</li>
                <li>You can now close this window</li>
                <li>Return to your terminal to continue</li>
            </ol>

            <p style="margin-top: 1rem;"><strong>Test your connection:</strong></p>
            <code>python -m agents.social_media_agent</code>
        </div>

        <p style="margin-top: 2rem; font-size: 0.875rem; color: #718096;">
            You can safely close this window now.
        </p>
    </div>
</body>
</html>
            """

            self.wfile.write(success_html.encode())

            # Print to server console
            print(f"\n✅ Successfully authorized {platform}!")
            print(f"📝 Access token: {token_data['access_token'][:20]}...")
            print(f"💾 Token saved to .oauth_tokens.json")
            print("\n🎉 You can now use the {platform} integration!")
            print("\nPress Ctrl+C to stop the server.")

        except Exception as e:
            self.send_error(500, f"Error processing OAuth callback: {str(e)}")
            print(f"\n❌ Error: {e}")

    def log_message(self, format, *args):
        """Suppress default logging except for errors"""
        pass


def start_callback_server(port: int = 8888) -> None:
    """
    Start OAuth callback server

    Args:
        port: Port to listen on (default: 8888)
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, OAuthCallbackHandler)

    print(f"\n🌐 OAuth callback server started on http://localhost:{port}")
    print(f"📡 Waiting for authorization callback...")
    print(f"\n💡 Make sure your OAuth redirect URIs are set to:")
    print(f"   - LinkedIn: http://localhost:{port}/oauth/linkedin/callback")
    print(f"   - Twitter:  http://localhost:{port}/oauth/twitter/callback")
    print(f"\nPress Ctrl+C to stop the server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Server stopped.")
        httpd.shutdown()


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    start_callback_server(port)

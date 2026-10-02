"""Local development server that serves static files and the Vercel API route."""

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from api.generate_idea import handler as IdeaHandler


class DevHandler(SimpleHTTPRequestHandler, IdeaHandler):
    """Serve the same POST API handler locally without a separate framework."""

    def do_GET(self):
        if self.path.startswith("/api/"):
            return IdeaHandler.do_GET(self)
        return SimpleHTTPRequestHandler.do_GET(self)


def main():
    port = int(os.environ.get("PORT", "3000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), DevHandler)
    print(f"SparkIdea AI local preview: http://0.0.0.0:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

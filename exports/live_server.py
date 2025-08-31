import streamlit as st
import http.server
import socketserver
import threading
import webbrowser
import tempfile
import os
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
from exports.html_exporter import export_dashboard_html


def serve_dashboard_live(figures: Dict[str, go.Figure],
                        dashboard_title: str = "Business Intelligence Dashboard",
                        company_name: str = "Your Company",
                        description: str = "Comprehensive data insights and performance metrics",
                        watermark_text: str = "",
                        footer_text: str = "",
                        footer_contact: str = "",
                        chart_specs: Optional[List[Dict]] = None,
                        df: Optional[pd.DataFrame] = None) -> None:
    """Serve the dashboard as a live website instead of downloading HTML file."""

    # Generate HTML content
    html_content = export_dashboard_html(
        figures=figures,
        filename="",
        dashboard_title=dashboard_title,
        company_name=company_name,
        description=description,
        watermark_text=watermark_text,
        footer_text=footer_text,
        footer_contact=footer_contact,
        chart_specs=chart_specs,
        df=df,
        include_insights=True,
        include_data_summary=True
    )

    # Create a temporary directory and HTML file
    with tempfile.TemporaryDirectory() as temp_dir:
        html_file = os.path.join(temp_dir, "dashboard.html")

        # Write the HTML content to temporary file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Start HTTP server
        port = 8000
        handler = http.server.SimpleHTTPRequestHandler

        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        # If port 8000 is in use, try next ports
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                httpd = socketserver.TCPServer(("", port), handler)
                break
            except OSError as e:
                if e.errno == 48: 
                    port += 1
                    if attempt == max_attempts - 1:
                        st.error(f"Could not find an available port after {max_attempts} attempts. Please close some applications and try again.")
                        return
                else:
                    raise e
        else:
            st.error("Could not start server - no available ports found.")
            return

        try:
            with httpd:
                server_url = f"http://localhost:{port}/dashboard.html"

                # Open browser
                def open_browser():
                    import time
                    time.sleep(1) 
                    webbrowser.open(server_url)

                browser_thread = threading.Thread(target=open_browser)
                browser_thread.daemon = True
                browser_thread.start()

                st.success(f"Dashboard served at: {server_url}")
                st.info("The dashboard has been opened in your default web browser. The server will run until you close this tab.")

                # Keep server running until user interrupts
                httpd.serve_forever()

        except KeyboardInterrupt:
            st.info("Server stopped.")
        finally:
            os.chdir(original_cwd)

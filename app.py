"""
app.py

This is the entrypoint for the Site Visit Report tool, packaged as a Flask
application suitable for deployment on Render or any other Python web
hosting platform.  It reuses the implementation previously provided in
``site_visit_report_app.py`` and renames the module and variables to
conform to typical deployment conventions.  The app collects site visit
information from Solution Engineers, calls an MCP agent (placeholder),
and generates a Word document report based on the Cloud Inventory site
survey template.

To run this app locally, install the requirements and execute

    python app.py

On Render, the service can be configured to install the requirements
from ``requirements.txt`` and start the web service using Gunicorn with
``gunicorn app:app``.
"""

import os
import uuid
from datetime import datetime

from flask import Flask, render_template_string, request, send_file
from docx import Document
from docx.shared import Inches


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB upload limit
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploaded_photos')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def call_mcp_agent(summary: str) -> str:
    """Placeholder for calling the Cloud Inventory MCP agent.

    In a real implementation, this function would send the ``summary``
    (e.g., a description of the business area or issue) to your MCP
    agent API and return the agent’s response.  Here we simply return
    a canned response for demonstration purposes.

    Args:
        summary: A text summary of observations and issues.

    Returns:
        A descriptive string explaining how Cloud Inventory can address
        the identified problems.
    """
    return (
        "Based on the information provided, Cloud Inventory can streamline "
        "your operations by automating receiving and putaway via RF "
        "scanners, implementing directed picking and packing workflows, "
        "and offering real-time inventory visibility through dashboards "
        "and cycle counting. This will reduce manual data entry errors and "
        "improve order accuracy."
    )


def generate_word_report(data: dict, image_paths: list[str], mcp_response: str) -> str:
    """Generate a Word document for the site visit report.

    The report includes sections based on the site survey template and
    embeds uploaded images.  It returns the path to the generated file.

    Args:
        data: Dictionary of form data from the site visit submission.
        image_paths: List of file paths to uploaded images.
        mcp_response: The response text from the MCP agent.

    Returns:
        The absolute path to the generated ``.docx`` file.
    """
    filename = f"site_survey_report_{uuid.uuid4().hex}.docx"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    doc = Document()
    doc.add_heading('Site Survey Report', level=0)
    # Cover page
    doc.add_paragraph(
        f"Survey location: {data.get('survey_location','')}\n"
        f"Survey conducted on: {data.get('survey_date','')}\n"
        f"Company name: {data.get('company_name','')}\n"
        f"Generated on: {datetime.now().strftime('%Y-%m-%d')}"
    )
    doc.add_page_break()
    # Company & Site Profile
    doc.add_heading('1. Company & Site Profile', level=1)
    doc.add_paragraph(data.get('company_profile', ''))
    # Master Data & Inventory Information
    doc.add_heading('2. Master Data & Inventory Information', level=1)
    doc.add_paragraph(data.get('inventory_info', ''))
    # IT & Systems Landscape
    doc.add_heading('3. IT & Systems Landscape', level=1)
    doc.add_paragraph(data.get('it_systems', ''))
    # Operations Overview
    doc.add_heading('4. Operations Overview', level=1)
    doc.add_paragraph(data.get('operations_overview', ''))
    # Observations & Pain Points
    doc.add_heading('5. Observations & Pain Points', level=1)
    doc.add_paragraph(data.get('observations', ''))
    doc.add_paragraph(f"Root cause: {data.get('root_cause','')}")
    doc.add_paragraph(f"Business impact: {data.get('business_impact','')}")
    # Proposed Solution & Benefits
    doc.add_heading('6. Proposed Solution & Benefits', level=1)
    doc.add_paragraph(mcp_response)
    # In‑Scope & Out‑of‑Scope
    doc.add_heading('7. In‑Scope & Out‑of‑Scope Requirements', level=1)
    doc.add_paragraph(f"In scope: {data.get('in_scope','')}")
    doc.add_paragraph(f"Out of scope: {data.get('out_scope','')}")
    # Value Summary & Metrics
    doc.add_heading('8. Value Summary & Metrics', level=1)
    doc.add_paragraph(data.get('value_summary',''))
    # Attach images
    if image_paths:
        doc.add_heading('9. Photos', level=1)
        for img_path in image_paths:
            try:
                doc.add_picture(img_path, width=Inches(5))
                doc.add_paragraph('')
            except Exception:
                pass
    # Sign-Off
    doc.add_heading('10. Sign‑Off', level=1)
    doc.add_paragraph('Customer representative signature: ________________')
    doc.add_paragraph('Solution Engineer signature: ________________')
    doc.save(filepath)
    return filepath


FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>New Site Survey Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    input[type=text], textarea { width: 100%; padding: 0.5rem; margin-top: 0.2rem; margin-bottom: 1rem; }
    label { font-weight: bold; display: block; margin-top: 1rem; }
    .section { margin-bottom: 2rem; }
  </style>
</head>
<body>
  <h1>Create Site Survey Report</h1>
  <form method="post" enctype="multipart/form-data">
    <div class="section">
      <label>Survey location:</label>
      <input type="text" name="survey_location" required>
      <label>Survey conducted on (YYYY‑MM‑DD):</label>
      <input type="text" name="survey_date" required>
      <label>Company name:</label>
      <input type="text" name="company_name" required>
    </div>
    <div class="section">
      <label>Company & Site Profile:</label>
      <textarea name="company_profile" rows="4"></textarea>
    </div>
    <div class="section">
      <label>Master Data & Inventory Information:</label>
      <textarea name="inventory_info" rows="4"></textarea>
    </div>
    <div class="section">
      <label>IT & Systems Landscape:</label>
      <textarea name="it_systems" rows="4"></textarea>
    </div>
    <div class="section">
      <label>Operations Overview:</label>
      <textarea name="operations_overview" rows="4"></textarea>
    </div>
    <div class="section">
      <label>Observations & Pain Points:</label>
      <textarea name="observations" rows="4" placeholder="Describe issues observed during the site visit."></textarea>
      <label>Root cause:</label>
      <textarea name="root_cause" rows="2"></textarea>
      <label>Business impact:</label>
      <textarea name="business_impact" rows="2"></textarea>
      <label>Upload photos (optional):</label>
      <input type="file" name="photos" multiple accept="image/*">
    </div>
    <div class="section">
      <label>In‑Scope Requirements:</label>
      <textarea name="in_scope" rows="3"></textarea>
      <label>Out‑of‑Scope Requirements:</label>
      <textarea name="out_scope" rows="3"></textarea>
    </div>
    <div class="section">
      <label>Value Summary & Metrics (optional):</label>
      <textarea name="value_summary" rows="4" placeholder="Baseline metrics, target improvements, ROI assumptions."></textarea>
    </div>
    <button type="submit">Generate Report</button>
  </form>
</body>
</html>
"""


@app.route('/new', methods=['GET', 'POST'])
def new_report():
    if request.method == 'POST':
        form_data = {
            'survey_location': request.form.get('survey_location', '').strip(),
            'survey_date': request.form.get('survey_date', '').strip(),
            'company_name': request.form.get('company_name', '').strip(),
            'company_profile': request.form.get('company_profile', '').strip(),
            'inventory_info': request.form.get('inventory_info', '').strip(),
            'it_systems': request.form.get('it_systems', '').strip(),
            'operations_overview': request.form.get('operations_overview', '').strip(),
            'observations': request.form.get('observations', '').strip(),
            'root_cause': request.form.get('root_cause', '').strip(),
            'business_impact': request.form.get('business_impact', '').strip(),
            'in_scope': request.form.get('in_scope', '').strip(),
            'out_scope': request.form.get('out_scope', '').strip(),
            'value_summary': request.form.get('value_summary', '').strip(),
        }
        image_paths: list[str] = []
        photos = request.files.getlist('photos') or []
        for photo in photos:
            if photo.filename:
                ext = os.path.splitext(photo.filename)[1]
                unique_name = f"{uuid.uuid4().hex}{ext}"
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                photo.save(img_path)
                image_paths.append(img_path)
        summary_parts = [
            form_data['company_profile'],
            form_data['operations_overview'],
            form_data['observations'],
            form_data['business_impact'],
        ]
        summary = '\n'.join([p for p in summary_parts if p])
        mcp_response = call_mcp_agent(summary)
        report_path = generate_word_report(form_data, image_paths, mcp_response)
        return send_file(report_path, as_attachment=True)
    return render_template_string(FORM_TEMPLATE)


@app.route('/')
def index():
    return (
        "<h2>Site Survey Report Tool</h2>"
        "<p>Use <a href='/new'>/new</a> to create a new site survey report.</p>"
    )


if __name__ == '__main__':
    # For local development.  Render runs the app using Gunicorn.
    app.run(debug=True)
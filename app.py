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

from flask import Flask, render_template_string, request, send_file, redirect, url_for
from docx import Document
from docx.shared import Inches


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB upload limit
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploaded_photos')
app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(__file__), 'records')

# Ensure upload and data directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)


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


# -----------------------------------------------------------------------------
# Data persistence helpers
#
def _record_filepath(record_id: str) -> str:
    """Return the full path to the JSON file for a given record ID."""
    return os.path.join(app.config['DATA_FOLDER'], f"{record_id}.json")


def save_record(record_id: str, data: dict) -> None:
    """Persist a record to disk as JSON.

    Args:
        record_id: Unique identifier for the record.
        data: All data fields to save, including images list.
    """
    import json
    filepath = _record_filepath(record_id)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_record(record_id: str) -> dict | None:
    """Load a record from disk if it exists.

    Args:
        record_id: Unique identifier.

    Returns:
        The loaded dictionary or None if the file does not exist.
    """
    import json
    filepath = _record_filepath(record_id)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def list_records() -> list[dict]:
    """Return a list of minimal information about all saved records.

    Each record is represented as a dictionary with keys 'id',
    'company_name' and 'se_name'. Additional keys may be present in
    future but are not used by the index page.
    """
    import json
    records = []
    for filename in os.listdir(app.config['DATA_FOLDER']):
        if not filename.endswith('.json'):
            continue
        record_id = filename[:-5]
        filepath = os.path.join(app.config['DATA_FOLDER'], filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            records.append({
                'id': record_id,
                'company_name': data.get('company_name', ''),
                'se_name': data.get('se_name', ''),
                'survey_date': data.get('survey_date', ''),
            })
        except Exception:
            continue
    return records


# HTML templates for the list page and record page.
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Site Survey Reports</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; background-color: #0F2C45; color: #FFFFFF; }
    header { display: flex; align-items: center; padding: 1rem 2rem; background-color: #001F3F; }
    header img { height: 36px; margin-right: 1rem; }
    header h1 { font-size: 1.5rem; margin: 0; }
    .container { padding: 2rem; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .toolbar input[type="text"] { padding: 0.5rem; width: 50%; border-radius: 4px; border: none; }
    .toolbar a { padding: 0.5rem 1rem; background-color: #00B3C7; color: #0F2C45; text-decoration: none; border-radius: 4px; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #324A6D; }
    th { background-color: #001F3F; }
    tr:hover { background-color: #183A59; }
    a.record-link { color: #00B3C7; text-decoration: none; }
  </style>
</head>
<body>
  <header>
    <img src="{{ url_for('static', filename=logo_filename) }}" alt="Cloud Inventory Logo">
    <h1>Site Survey Reports</h1>
  </header>
  <div class="container">
    <div class="toolbar">
      <form method="get" style="width: 100%;">
        <input type="text" name="q" placeholder="Search by company or SE name" value="{{ search_query }}">
      </form>
      <a href="{{ url_for('record_page', record_id='new') }}">Add New</a>
    </div>
    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>SE Name</th>
          <th>Survey Date</th>
        </tr>
      </thead>
      <tbody>
        {% for rec in records %}
        <tr>
          <td><a class="record-link" href="{{ url_for('record_page', record_id=rec.id) }}">{{ rec.company_name or '(No Name)' }}</a></td>
          <td>{{ rec.se_name or '-' }}</td>
          <td>{{ rec.survey_date or '-' }}</td>
        </tr>
        {% else %}
        <tr>
          <td colspan="3">No records found.</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


RECORD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ 'New' if record_id == 'new' else 'Edit' }} Site Survey Report</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; background-color: #0F2C45; color: #FFFFFF; }
    header { display: flex; align-items: center; padding: 1rem 2rem; background-color: #001F3F; }
    header img { height: 36px; margin-right: 1rem; }
    header h1 { font-size: 1.5rem; margin: 0; }
    .container { padding: 2rem; max-width: 800px; margin: 0 auto; }
    label { font-weight: bold; display: block; margin-top: 1rem; }
    input[type=text], textarea, input[type=date] { width: 100%; padding: 0.5rem; margin-top: 0.25rem; border-radius: 4px; border: none; }
    textarea { resize: vertical; }
    input[type=file] { margin-top: 0.5rem; }
    button { margin-top: 1.5rem; padding: 0.75rem 1.5rem; background-color: #00B3C7; color: #0F2C45; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
    .images-list { margin-top: 1rem; }
    .images-list img { max-width: 120px; margin-right: 0.5rem; margin-top: 0.5rem; border: 2px solid #324A6D; border-radius: 4px; }
    a.back-link { display: inline-block; margin-bottom: 1rem; color: #00B3C7; text-decoration: none; }
  </style>
</head>
<body>
  <header>
    <img src="{{ url_for('static', filename=logo_filename) }}" alt="Cloud Inventory Logo">
    <h1>{{ 'New' if record_id == 'new' else 'Edit' }} Site Survey Report</h1>
  </header>
  <div class="container">
    <a class="back-link" href="{{ url_for('index_page') }}">&larr; Back to list</a>
    <form method="post" enctype="multipart/form-data">
      <label>Solution Engineer Name:</label>
      <input type="text" name="se_name" required value="{{ data.get('se_name','') }}">
      <label>Survey location:</label>
      <input type="text" name="survey_location" required value="{{ data.get('survey_location','') }}">
      <label>Survey conducted on:</label>
      <input type="text" name="survey_date" required value="{{ data.get('survey_date','') }}" placeholder="YYYY-MM-DD">
      <label>Company name:</label>
      <input type="text" name="company_name" required value="{{ data.get('company_name','') }}">
      <label>Company & Site Profile:</label>
      <textarea name="company_profile" rows="3">{{ data.get('company_profile','') }}</textarea>
      <label>Master Data & Inventory Information:</label>
      <textarea name="inventory_info" rows="3">{{ data.get('inventory_info','') }}</textarea>
      <label>IT & Systems Landscape:</label>
      <textarea name="it_systems" rows="3">{{ data.get('it_systems','') }}</textarea>
      <label>Operations Overview:</label>
      <textarea name="operations_overview" rows="3">{{ data.get('operations_overview','') }}</textarea>
      <label>Observations & Pain Points:</label>
      <textarea name="observations" rows="3" placeholder="Describe issues observed during the site visit.">{{ data.get('observations','') }}</textarea>
      <label>Root cause:</label>
      <textarea name="root_cause" rows="2">{{ data.get('root_cause','') }}</textarea>
      <label>Business impact:</label>
      <textarea name="business_impact" rows="2">{{ data.get('business_impact','') }}</textarea>
      <label>Upload photos (optional):</label>
      <input type="file" name="photos" multiple accept="image/*">
      {% if images %}
      <div class="images-list">
        {% for img in images %}
        <img src="{{ url_for('static', filename=img) }}" alt="Uploaded image">
        {% endfor %}
      </div>
      {% endif %}
      <label>In‑Scope Requirements:</label>
      <textarea name="in_scope" rows="2">{{ data.get('in_scope','') }}</textarea>
      <label>Out‑of‑Scope Requirements:</label>
      <textarea name="out_scope" rows="2">{{ data.get('out_scope','') }}</textarea>
      <label>Value Summary & Metrics (optional):</label>
      <textarea name="value_summary" rows="3" placeholder="Baseline metrics, target improvements, ROI assumptions.">{{ data.get('value_summary','') }}</textarea>
      <button type="submit">Save & Download Report</button>
    </form>
  </div>
</body>
</html>
"""


@app.route('/new')
def new_redirect():
    """Redirect the legacy /new path to the new record page."""
    return redirect(url_for('record_page', record_id='new'))


@app.route('/')
def index_page():
    """Display a list of existing records with search and an option to create new."""
    # Choose the negative logo for dark background
    logo_filename = 'ci-negative.png'
    # Extract search query from query parameters
    search_query = request.args.get('q', '').strip().lower()
    records = list_records()
    # Filter records based on search query (match company or SE name)
    if search_query:
        records = [r for r in records if search_query in (r.get('company_name','').lower() + r.get('se_name','').lower())]
    # Sort records by survey_date descending
    records.sort(key=lambda r: r.get('survey_date', ''), reverse=True)
    return render_template_string(INDEX_TEMPLATE, records=records, logo_filename=logo_filename, search_query=search_query)

@app.route('/record/<record_id>', methods=['GET', 'POST'])
def record_page(record_id: str):
    """Create or edit a site survey record.

    Args:
        record_id: 'new' for a new record or an existing record ID.
    """
    logo_filename = 'ci-negative.png'
    if request.method == 'POST':
        # Gather form inputs
        data = {
            'se_name': request.form.get('se_name','').strip(),
            'survey_location': request.form.get('survey_location','').strip(),
            'survey_date': request.form.get('survey_date','').strip(),
            'company_name': request.form.get('company_name','').strip(),
            'company_profile': request.form.get('company_profile','').strip(),
            'inventory_info': request.form.get('inventory_info','').strip(),
            'it_systems': request.form.get('it_systems','').strip(),
            'operations_overview': request.form.get('operations_overview','').strip(),
            'observations': request.form.get('observations','').strip(),
            'root_cause': request.form.get('root_cause','').strip(),
            'business_impact': request.form.get('business_impact','').strip(),
            'in_scope': request.form.get('in_scope','').strip(),
            'out_scope': request.form.get('out_scope','').strip(),
            'value_summary': request.form.get('value_summary','').strip(),
        }
        # Determine a new record ID if this is a new record
        if record_id == 'new':
            record_id = uuid.uuid4().hex
        # Load existing record if editing
        existing = load_record(record_id)
        saved_images = existing.get('images', []) if existing else []
        # Handle file uploads
        photos = request.files.getlist('photos') or []
        # Ensure a static directory exists for this record
        record_static_dir = os.path.join(app.static_folder, record_id)
        os.makedirs(record_static_dir, exist_ok=True)
        for photo in photos:
            if photo.filename:
                ext = os.path.splitext(photo.filename)[1]
                unique_name = f"{uuid.uuid4().hex}{ext}"
                img_path = os.path.join(record_static_dir, unique_name)
                photo.save(img_path)
                rel_path = f"{record_id}/{unique_name}"
                saved_images.append(rel_path)
        # Generate summary for MCP agent
        summary_parts = [
            data['company_profile'],
            data['operations_overview'],
            data['observations'],
            data['business_impact'],
        ]
        summary = '\n'.join([p for p in summary_parts if p])
        mcp_response = call_mcp_agent(summary)
        # Save record
        data_for_save = data.copy()
        data_for_save['images'] = saved_images
        save_record(record_id, data_for_save)
        # Convert relative paths to absolute for report generation
        abs_paths = [os.path.join(app.static_folder, rel) for rel in saved_images]
        report_path = generate_word_report(data, abs_paths, mcp_response)
        return send_file(report_path, as_attachment=True)
    else:
        # GET request: load record or create blank for new
        record_data = load_record(record_id) if record_id != 'new' else None
        if not record_data:
            record_data = {
                'se_name': '', 'survey_location': '', 'survey_date': '', 'company_name': '',
                'company_profile': '', 'inventory_info': '', 'it_systems': '',
                'operations_overview': '', 'observations': '', 'root_cause': '',
                'business_impact': '', 'in_scope': '', 'out_scope': '', 'value_summary': '',
                'images': [],
            }
        images = record_data.get('images', [])
        return render_template_string(RECORD_TEMPLATE, record_id=record_id, data=record_data, images=images, logo_filename=logo_filename)


if __name__ == '__main__':
    # For local development.  Render runs the app using Gunicorn.
    app.run(debug=True)
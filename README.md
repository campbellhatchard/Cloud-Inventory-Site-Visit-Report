# Site Visit Report Tool

This repository contains a simple Flask application that allows Solution
Engineers to capture the details of a customer site visit and
automatically generate a polished Word report based on the Cloud
Inventory® site survey template.  The app collects information about
the customer’s operations, pain points, root causes and business
impact, uploads photos, calls an MCP agent (placeholder stub), and
embeds the response into the final report.

## Features

* Web form aligned to the site survey template (company profile,
  master data & inventory, IT systems, operations, observations,
  in‑scope/out‑of‑scope requirements, value summary and more).
* Upload multiple photos per report; images are resized and embedded in
  the generated report.
* Placeholder function (`call_mcp_agent`) to integrate with the Cloud
  Inventory MCP agent for automated solution recommendations.
* Generates a professional Word document (`.docx`) using
  `python‑docx`.
* Ready for deployment on Render via a `render.yaml` blueprint or via
  the Render dashboard.

## Getting Started Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/site-visit-report-tool.git
   cd site-visit-report-tool
   ```

2. **Create a virtual environment (optional but recommended)**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**

   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to `http://localhost:5000/new` to
   create a new site survey report.  After submitting the form, a Word
   document will download automatically.

## Deployment on Render

This repository is configured to deploy on [Render](https://render.com)
using either the infrastructure‑as‑code blueprint (`render.yaml`) or
the Render dashboard.

### Using `render.yaml` (recommended)

1. Commit and push this repository to GitHub.
2. In the Render dashboard, select **New → Blueprint** and connect
   your GitHub repository.
3. Render will detect the `render.yaml` file and create a new web
   service named `site-visit-report` using the free plan.  Adjust the
   plan name if you need more resources.
4. Click **Apply** to deploy.  Render will install the
   dependencies (`pip install -r requirements.txt`) and start the app
   using Gunicorn (`gunicorn app:app`).

### Using the Render Dashboard

1. Commit and push this repository to GitHub.
2. In the Render dashboard, click **New → Web Service** and choose
   **Python 3** as the language.
3. Connect your repository and branch.
4. Set the **Build Command** to:

   ```bash
   pip install -r requirements.txt
   ```

5. Set the **Start Command** to:

   ```bash
   gunicorn app:app
   ```

6. Click **Create Web Service**.  The app will be deployed and
   accessible at a `*.onrender.com` URL.

## Customisation

* **MCP agent integration** – Replace the `call_mcp_agent` function
  in `app.py` with an API call to your Cloud Inventory MCP agent to
  return real recommendations based on the site summary.
* **Authentication & persistence** – Add authentication (e.g., via SSO
  or Flask‑Login) and a database (e.g., PostgreSQL) if you need to
  store reports permanently.
* **Styling & templates** – Replace the inline HTML with Jinja2
  templates and add CSS for a more polished UI.  You can also embed
  your company logo and branding into the generated Word document.

## License

This project is provided as a proof of concept.  Adapt it to meet your
organisation’s needs and internal policies.
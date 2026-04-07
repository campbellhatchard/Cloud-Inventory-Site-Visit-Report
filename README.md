# Site Visit Report Tool

This repository contains a Flask application that allows Solution
Engineers to capture the details of a customer site visit and
automatically generate a polished Word report based on the Cloud
Inventory® site survey template.  The app collects detailed
information about the customer’s operations (broken down by
Receiving, Putaway, Replenishment, Order Management, Picking,
Packing, Staging, Shipping and General), pain points, root causes,
and business impacts.  It also records stakeholders from both the
customer and Cloud Inventory, uploads photos, calls an MCP agent
(placeholder stub), and embeds the response into the final report.
Records are persisted to disk so that reports can be edited or
generated at any time, and a searchable list of existing reports is
shown on the home page.

## Features

* **Persistent records** – All submitted surveys are stored as JSON files on
  the server’s disk.  The home page lists existing reports with their
  company names, solution engineer names and survey dates.  A search
  box filters records by company or engineer name, and an **Add New**
  button starts a new survey.
* **Branded user interface** – The pages use a dark theme with accent
  colours inspired by Cloud Inventory®’s branding and embed the
  provided full‑colour and negative logos for light and dark
  backgrounds.
* **Solution Engineer drop‑down with add‑new** – A drop‑down menu
  populates with existing Solution Engineers, and an adjacent field
  allows you to add a new name on the fly.  Names are persisted for
  future visits.
* **Stakeholder tables** – Record multiple company representatives and
  Cloud Inventory representatives, each with a name and title.  Add
  additional rows dynamically as needed.
* **Detailed operations capture** – For each key warehouse function
  (Receiving, Putaway, Replenishment, Order Management, Picking,
  Packing, Staging, Shipping and General) you can enter a pain
  point, root cause, business impact and upload a supporting photo.
* **Photo uploads** – Upload multiple images per report; images are
  stored and displayed when editing, and they’re automatically
  embedded into the generated Word report.  Operations photos are
  attached under their respective sections in the report.
* **MCP integration stub** – A placeholder `call_mcp_agent` function
  demonstrates how to call out to a Cloud Inventory MCP agent.  Replace
  this with your real API call to get personalised recommendations.
* **Word report generation** – Using `python‑docx`, the app
  produces a professional `.docx` file summarising all inputs and the
  MCP response.  The report includes sections for stakeholders and
  operations details, along with sign‑off areas for the customer and
  Solution Engineer.
* **Render ready** – A `render.yaml` blueprint and a sensible
  `requirements.txt` allow one‑click deployment to Render.  Persistent
  disks on Render ensure your records and images are retained between
  deploys.

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
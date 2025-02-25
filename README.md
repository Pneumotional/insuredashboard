

# Interactive Custom Insurance Data Dashboard with Dash and Plotly Powered with AI Agent

This project is an interactive data dashboard built using Dash and Plotly, designed to provide insightful visualizations and summaries of your data. It allows users to upload data as CSV files, apply various filters, and interact with dynamic charts and summary statistics. 

## Key Features:
- **CSV Data Upload**: Upload your dataset in CSV format for real-time analysis and visualization.
- **Filters**: Apply filters to your data to focus on specific aspects and gain tailored insights.
- **Summary Cards**: Display key metrics and aggregated values as summary cards for quick reference.
- **Interactive Charts**: Explore your data visually with responsive and interactive charts powered by Plotly.
- **Data Management**: Delete or download filtered data for offline use, making it easy to manage and export your datasets.
- **AI-Powered Insights**: Ask AI-driven questions on the dataset for intuitive and advanced data exploration.

This dashboard is ideal for anyone looking to visualize, analyze, and interact with their data in a highly flexible and user-friendly environment.



Here’s a "How to Run the Project" guide for your GitHub repo:

---

## How to Run the Project

### Prerequisites
Before running the project, ensure you have Python installed on your machine. You can download Python from [here](https://www.python.org/downloads/).

### Step 1: Clone the Repository
First, clone the project repository to your local machine:
```bash
git clone https://github.com/Pneumotional/insuredashboard.git
```
Navigate to the project directory

### Step 2: Install Dependencies
To install the required Python libraries, use the following command:
```bash
pip install -r requirements.txt
```

Your `requirements.txt` file should look like this:
```
dash
dash-iconify
dash-bootstrap-components
plotly
pandas
chardet
SQLAlchemy
requests
selenium
phidata
groq
```
Any error drop a mail

### Step 3: Run the Project

1. **Run the Dashboard Application:**
   ```bash
   python app.py
   ```
   This will start the Dash Plotly interactive dashboard.

2. **Run the AI Integration (for Data Querying):**
   ```bash
   python ai_app.py
   ```
   This will start the AI service for asking questions about the data.

### Step 4: Access the Dashboard

Once the project is running, open your web browser and go to `http://127.0.0.1:8050` (or the address provided in the console output) to view the dashboard.


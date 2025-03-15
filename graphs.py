from fastapi import APIRouter, Query
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
import seaborn as sns
router = APIRouter()

#1. Job market data (static for now, can be updated dynamically later)
def generate_pie_chart():
    """
    Fetches job market demand data and generates a pie chart as a Base64-encoded image.
    """
    
    job_data = {
        "Tech": 15,
        "Healthcare": 10,
        "Finance": 12,
        "Education": 7,
        "Retail": 14,
        "Telecom": 11,
        "Advertising & PR": 6,
        "Logistics & Transportation": 5,
        "Automotive": 3,
        "Energy": 2,
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))
    labels = list(job_data.keys())
    sizes = list(job_data.values())
    colors = plt.cm.Paired(range(len(labels)))
    
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.set_title("Job Market Demand by Industry (2025)", fontsize=14)
    
    # Convert figure to Base64 image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return image_base64

@router.get("/analytics/job_market_pie_chart")
async def get_job_market_pie_chart():
    """
    Returns the job market demand pie chart as a base64 encoded image.
    """
    image_base64 = generate_pie_chart()
    return {"image": f"data:image/png;base64,{image_base64}"}


#2. Different top 10 trending careers for each year (2015 - 2024)
job_trends = {
    2015: {"Software Engineer": 50000, "Teacher": 45000, "Civil Engineer": 30000, "Retail Manager": 35000, "Pharmacist": 32000,
           "HR Specialist": 29000, "Graphic Designer": 27000, "Construction Manager": 25000, "Accountant": 23000, "Sales Executive": 22000},

    2016: {"Software Engineer": 52000, "Nurse": 48000, "Financial Analyst": 31000, "Marketing Executive": 33000, "Cybersecurity Analyst": 28000,
           "HR Specialist": 27000, "Graphic Designer": 26000, "Construction Manager": 24000, "Data Entry Operator": 22000, "Mechanical Engineer": 21000},

    2017: {"Data Scientist": 55000, "Nurse": 49000, "Digital Marketer": 35000, "Cybersecurity Analyst": 30000, "AI Engineer": 27000,
           "Software Engineer": 26000, "Accountant": 25000, "Teacher": 24000, "HR Manager": 23000, "Architect": 22000},

    2018: {"AI Engineer": 60000, "Data Scientist": 57000, "Software Developer": 45000, "Doctor": 42000, "Content Creator": 32000,
           "Social Media Manager": 31000, "Blockchain Developer": 29000, "Pharmacist": 27000, "Teacher": 25000, "Automotive Engineer": 23000},

    2019: {"Cybersecurity Analyst": 65000, "AI Engineer": 60000, "Digital Marketer": 48000, "Software Engineer": 45000, "Doctor": 40000,
           "Nurse": 39000, "Data Analyst": 37000, "HR Manager": 35000, "Web Developer": 33000, "Retail Manager": 31000},

    2020: {"Cloud Engineer": 70000, "AI Engineer": 65000, "Cybersecurity Analyst": 60000, "Software Developer": 55000, "Nurse": 50000,
           "Doctor": 48000, "Content Creator": 45000, "Pharmacist": 40000, "Digital Marketer": 35000, "Social Worker": 30000},

    2021: {"AI Engineer": 80000, "Data Scientist": 75000, "Software Engineer": 70000, "Machine Learning Engineer": 67000, "Cybersecurity Expert": 64000,
           "Doctor": 60000, "Nurse": 57000, "Cloud Engineer": 55000, "Marketing Manager": 50000, "E-commerce Specialist": 48000},

    2022: {"Blockchain Developer": 85000, "AI Engineer": 80000, "Cybersecurity Expert": 75000, "Software Engineer": 70000, "Data Scientist": 67000,
           "Doctor": 65000, "Machine Learning Engineer": 63000, "Nurse": 60000, "Cloud Engineer": 58000, "FinTech Specialist": 56000},

    2023: {"AI Engineer": 90000, "Cybersecurity Expert": 85000, "Blockchain Developer": 80000, "Machine Learning Engineer": 75000, "Data Analyst": 70000,
           "Software Engineer": 67000, "Doctor": 65000, "E-commerce Specialist": 60000, "UX/UI Designer": 57000, "Cloud Security Engineer": 55000},

    2024: {"Quantum Computing Engineer": 95000, "AI Engineer": 90000, "Blockchain Developer": 85000, "Cybersecurity Expert": 80000, "Machine Learning Engineer": 78000,
           "Software Engineer": 75000, "Data Scientist": 70000, "Bioinformatics Specialist": 67000, "Cloud Engineer": 65000, "Doctor": 60000},
}

def generate_career_trend_graph(year: int, chart_type: str):
    """
    Generates a bar or line chart showing the top 10 trending careers in a given year.
    """
    if year not in job_trends:
        return None  # Year not available

    careers = list(job_trends[year].keys())
    opportunities = list(job_trends[year].values())

    # Plot the graph
    plt.figure(figsize=(10, 6))

    if chart_type == "bar":
        plt.bar(careers, opportunities, color="skyblue")
    else:
        plt.plot(careers, opportunities, marker="o", linestyle="-", color="blue")

    plt.xlabel("Careers")
    plt.ylabel("Job Opportunities")
    plt.title(f"Top 10 Trending Careers in {year}")
    plt.xticks(rotation=45)

    # Convert to Base64 image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64

@router.get("/analytics/trending_careers")
async def get_trending_careers(year: int = Query(2024, description="Select a year"), chart_type: str = Query("bar", description="Select chart type (bar/line)")):
    """
    Returns a graph (bar/line) for the top 10 trending careers in a selected year.
    """
    image_base64 = generate_career_trend_graph(year, chart_type)

    if not image_base64:
        return {"error": "Data not available for the selected year"}

    return {"image": f"data:image/png;base64,{image_base64}"}

#3. stacked chart for remote vs. on-site jobs
job_data = {
    "Software Engineer": ("Tech", 70, 30),
    "Data Scientist": ("Tech", 65, 35),
    "Cybersecurity Analyst": ("Tech", 60, 40),
    "AI/ML Engineer": ("Tech", 75, 25),
    "Cloud Engineer": ("Tech", 72, 28),
    "Digital Marketer": ("Marketing", 80, 20),
    "UX/UI Designer": ("Design", 78, 22),
    "Content Creator": ("Media", 85, 15),
    "Financial Analyst": ("Finance", 50, 50),
    "Accountant": ("Finance", 55, 45),
    "Healthcare Professional": ("Healthcare", 20, 80),
    "Nurse": ("Healthcare", 10, 90),
    "Doctor": ("Healthcare", 5, 95),
    "Teacher": ("Education", 30, 70),
    "Professor (University)": ("Education", 40, 60),
    "Sales Manager": ("Sales", 50, 50),
    "Retail Manager": ("Retail", 25, 75),
    "Logistics Manager": ("Supply Chain", 30, 70),
    "Civil Engineer": ("Engineering", 15, 85),
    "Mechanical Engineer": ("Engineering", 20, 80),
    "Automotive Engineer": ("Automotive", 25, 75),
    "Construction Manager": ("Construction", 10, 90),
    "Lawyer": ("Legal", 35, 65),
    "Social Worker": ("Non-Profit", 20, 80),
    "Customer Support Rep.": ("Customer Service", 60, 40),
}

def generate_remote_vs_onsite_chart():
    """
    Generates a stacked bar chart for remote vs. on-site job distributions.
    """
    careers = list(job_data.keys())
    remote_percentages = [job_data[career][1] for career in careers]
    onsite_percentages = [job_data[career][2] for career in careers]

    plt.figure(figsize=(12, 6))
    plt.bar(careers, remote_percentages, label="Remote Jobs", color="skyblue")
    plt.bar(careers, onsite_percentages, bottom=remote_percentages, label="On-Site Jobs", color="orange")

    plt.xlabel("Careers", fontsize=12)
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.title("Remote vs. On-Site Jobs by Career", fontsize=14)
    plt.xticks(rotation=75, fontsize=10)
    plt.legend()

    # Convert to Base64 image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64

@router.get("/analytics/remote_vs_onsite")
async def get_remote_vs_onsite_chart():
    """
    Returns a stacked bar chart for remote vs. on-site job percentages across different careers.
    """
    image_base64 = generate_remote_vs_onsite_chart()
    return {"image": f"data:image/png;base64,{image_base64}"}

# 4. Recession Impact Graph
recession_data = {
    "Tech": [10, 15, 25],
    "Finance": [20, 10, 15],
    "Retail": [15, 30, 10],
    "Construction": [25, 20, 12],
    "Manufacturing": [18, 22, 10],
    "Hospitality": [12, 40, 8],
    "Healthcare": [5, 8, 4],
    "Education": [3, 5, 2],
}

years = ["2008 Recession", "2020 COVID", "2023 Tech Layoffs"]
industries = list(recession_data.keys())
values = np.array(list(recession_data.values()))

def generate_recession_graph():
    """
    Generates a grouped bar chart showing job losses in different industries across recessions.
    """
    bar_width = 0.2
    x = np.arange(len(industries))

    plt.figure(figsize=(12, 6))
    
    for i, year in enumerate(years):
        plt.bar(x + i * bar_width, values[:, i], width=bar_width, label=year)

    plt.xlabel("Industries")
    plt.ylabel("Job Loss Percentage (%)")
    plt.title("Industries Most Affected During Recessions")
    plt.xticks(x + bar_width, industries, rotation=45, ha="right")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Convert plot to Base64
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64

@router.get("/analytics/recession_impact")
async def get_recession_graph():
    """
    Endpoint to return the recession impact graph as a base64 image.
    """
    image_base64 = generate_recession_graph()
    return {"image": f"data:image/png;base64,{image_base64}"}


# Career data graph
careers = [
    ("Data Scientist", 50, 10, 1.5),
    ("AI Engineer", 50, 5, 0.8),
    ("Accountant", 20, 69, 1.4),
    ("Retail Cashier", 10, 81, 3.3),
    ("Factory Worker", 8, 78, 12.5),
    ("Medical Doctor", 60, 2, 1.2),
    ("Lawyer", 40, 23, 1.0),
    ("Software Engineer", 50, 4, 1.8),
    ("Graphic Designer", 30, 47, 0.3),
    ("Construction Worker", 45, 88, 7.4),
    ("Administrative Assistant", 15, 96, 2.6),
    ("Financial Analyst", 35, 23, 0.3),
    ("Pharmacist", 40, 3, 0.3),
    ("Teacher", 35, 1, 3.8),
]

# Extract values for plotting
career_names, lifespans, automation_risks, workers = zip(*careers)

# Normalize bubble sizes (for better visualization)
bubble_sizes = [w * 100 for w in workers]

# Plot the Bubble Chart
plt.figure(figsize=(12, 8))
sns.scatterplot(x=lifespans, y=automation_risks, size=bubble_sizes, sizes=(50, 1000), hue=career_names, palette="tab10", alpha=0.7, edgecolor="black")

# Labels and title
plt.xlabel("Career Lifespan (Years)", fontsize=12)
plt.ylabel("Automation Risk (%)", fontsize=12)
plt.title("Career Lifespan vs. Automation Risk", fontsize=14)
plt.legend(loc="upper right", bbox_to_anchor=(1.35, 1), title="Careers")
plt.grid(True, linestyle="--", alpha=0.5)

# Show plot
plt.show()

import csv
from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Function to load jobs from the CSV
def load_jobs():
    jobs = []
    with open('jobs.csv', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            jobs.append({
                'job_title': row['Job Title'],
                'company': row['Company'],
                'location': row['Location'],  # Added location
                'skills': row['Required Skills']
            })
    return jobs

# Function to recommend jobs based on user input
def recommend_jobs(user_skills, top_n, job_title_filter):
    jobs = load_jobs()
    recommendations = []
    user_skills_set = set(skill.strip().lower() for skill in user_skills.split(','))
    skill_count = {}

    for job in jobs:
        # Apply the job title filter (if provided)
        if job_title_filter and job_title_filter.lower() not in job['job_title'].lower():
            continue

        job_skills_set = set(skill.strip().lower() for skill in job['skills'].split(';'))
        match_percentage = len(user_skills_set.intersection(job_skills_set)) / len(job_skills_set) * 100

        if match_percentage > 0:
            recommendations.append({
                'job_title': job['job_title'],
                'company': job['company'],
                'location': job['location'],  # Added location
                'skills': job['skills'],
                'match_percentage': round(match_percentage, 2)
            })
            for skill in job_skills_set:
                skill_count[skill] = skill_count.get(skill, 0) + 1

    recommendations = sorted(recommendations, key=lambda x: x['match_percentage'], reverse=True)[:top_n]

    if skill_count:
        draw_pie_chart(skill_count)

    return recommendations

# Function to draw pie chart of top skills
def draw_pie_chart(skill_count):
    top_skills = dict(sorted(skill_count.items(), key=lambda item: item[1], reverse=True)[:5])
    labels = list(top_skills.keys())
    sizes = list(top_skills.values())

    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Top In-Demand Skills')
    chart_path = os.path.join('static', 'piechart.png')
    plt.savefig(chart_path)
    plt.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_skills = request.form['skills']
    top_n = int(request.form['top_n'])
    job_title_filter = request.form.get('job_title', '')
    recommendations = recommend_jobs(user_skills, top_n, job_title_filter)
    return render_template('recommendations.html', recommendations=recommendations, show_chart=True)

if __name__ == '__main__':
    app.run(debug=True)

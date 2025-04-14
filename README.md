# PlacementHub - Campus Placement Management System

![David (path)](https://img.shields.io/github/package-json/v/plankanban/planka)

The PlacementHub permits the Student to login/sign-up into the application and view current job
opportunities available. The System would store all the academic as well as personal details of the
students who wish to be placed and the Companies who offer jobs to the students. Students can
apply for the jobs if they are eligible. The admin can manage the database and post upcoming job or
internship opportunity which can be viewed by the students who are eligible for it. Admin can also
view the Statistics of Current Placement Drive.

## Project Overview

PlacementHub is a comprehensive web-based placement management system designed to streamline the campus recruitment process. It connects students, recruiters, and faculty/administrators on a single platform to facilitate efficient job matching and application tracking.

### Key Features

- **Multi-user Role System**: Different interfaces for students, recruiters, faculty, and administrators
- **Student Profile Management**: Complete academic and personal details tracking
- **Job Posting and Matching**: Automatic job eligibility matching based on qualifications
- **Application Tracking**: End-to-end monitoring of application status
- **Interview Scheduling**: Tools for scheduling and managing interviews
- **Placement Statistics**: Real-time analytics and reporting on placement activities
- **Faculty Feedback System**: Communication channel between faculty and students

### User Roles

1. **Students**: Create profiles, browse eligible jobs, apply for positions, track applications
2. **Recruiters**: Post job opportunities, review applications, schedule interviews
3. **Faculty**: Monitor student progress, provide feedback, track placement statistics
4. **Administrators**: Manage users, view analytics, oversee the entire placement process

## Use case Diagram for Admin

![](https://drive.google.com/uc?export=view&id=1k7Uj3gT8WWLKUqxmDgOpdDFrXL2ONUXG)

## Use case Diagram for Student

![](https://drive.google.com/uc?export=view&id=1WGbVplOH2d4jLUAgo5tU7Then3U5bYUP)

## ER Diagram

![](https://drive.google.com/uc?export=view&id=1OD723ztBDV9PeBr5sL458cqaZXQ_7cXl)

## Schema Diagram

![](https://drive.google.com/uc?export=view&id=19WOQ-9P2KNQTbqCW1lFkDb8B47qaX9uq)

## Installation and Project Startup Guide

### Prerequisites

- Python 3.7 or higher
- MySQL Database
- pip (Python package installer)

### Step 1: Clone or Download the Repository

Clone this repository or download it to your local machine.

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Navigate to the project directory
cd "path/to/placement management"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

If requirements.txt is not available, install the following packages:

```bash
pip install flask flask-mysqldb flask-wtf flask-login python-dotenv
```

### Step 4: Database Setup

1. Create a MySQL database for the project

```sql
CREATE DATABASE placement_hub;
USE placement_hub;
```

2. Import the provided SQL schema (if available) or create the required tables manually

```bash
mysql -u username -p placement_hub < database_schema.sql
```

3. Configure environment variables by updating the .env file in the project root:

```
DB_NAME=placement
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
```

### Step 5: Run the Application

```bash
# Navigate to the placement folder
cd placement

# Run the Flask application
python app.py
```

The server will start, typically at http://127.0.0.1:5000/

![](https://drive.google.com/uc?export=view&id=1W1C8ITwn6f7QwhmTXD8mj8n35D6hnq-s)

Now open any browser and access the URL provided in the running server (http://127.0.0.1:5000).

### Default Admin Login

- Username: admin
- Password: 12345678

### Database Structure Overview

The system uses the following main tables:

- Users: Stores user credentials and roles
- Students: Contains student profile information
- Companies: Lists registered companies
- Jobs: Details of job/internship postings
- Applications: Tracks student applications to jobs
- Feedback: Faculty feedback on student profiles

### Troubleshooting

1. Database Connection Issues:

   - Verify MySQL is running
   - Check the credentials in your .env file
   - Ensure the database exists

2. Module Import Errors:

   - Make sure all dependencies are installed
   - Activate the virtual environment if using one

3. Server Start Problems:
   - Check if the port is already in use
   - Review error logs for specific issues

## Demo

![](https://drive.google.com/uc?export=view&id=1CjfH1l3MMG3K1BJqnLM85uGLQcb3j4Q-)
![](https://drive.google.com/uc?export=view&id=1DIe4-bzPp72ZIffNnjhLkYF7IkrsuPau)
![](https://drive.google.com/uc?export=view&id=18EEVucrqF1S5vap-dCeP_9pmk__KrLxH)
![](https://drive.google.com/uc?export=view&id=11xMqUymGn6-3mkFR0dCudyV4owpEMuU6)
![](https://drive.google.com/uc?export=view&id=1c5NzHFDtbyJMdHLP6g5PYbkk_WSU82qR)
![](https://drive.google.com/uc?export=view&id=1FXl0yPYMTALenTzOTMrDI8-6qHIWTSsO)
![](https://drive.google.com/uc?export=view&id=1d2xDVjl6qpgYDJQMNQp9XSDdWmIwUpZ6)
![](https://drive.google.com/uc?export=view&id=1t_2vrxQAMqZ_RyDZ7twa20QSVdKb2_fg)
![](https://drive.google.com/uc?export=view&id=1dFGMYY2LYGg3KLiWNRBw6DQsPDla8uGN)
![](https://drive.google.com/uc?export=view&id=1BWZKt85bO3BruQRuZ4jRgUc3ElJjGicQ)
![](https://drive.google.com/uc?export=view&id=1jj0OFFE3WoWm4ig4h5tb2NPP14Etln5o)
![](https://drive.google.com/uc?export=view&id=14E8b0Tz0GA5aTwjearsbCkSKQXA2EAD9)

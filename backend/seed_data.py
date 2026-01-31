"""
Seed script to populate database with sample data
Run with: python seed_data.py
"""
from app.database import SessionLocal, engine, Base
from app.models import User, JobDescription, Question
from app.services.auth_service import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_data():
    # Create admin/recruiter user
    recruiter = db.query(User).filter(User.email == "recruiter@cygnusa.com").first()
    if not recruiter:
        recruiter = User(
            email="recruiter@cygnusa.com",
            full_name="HR Recruiter",
            hashed_password=get_password_hash("password123"),
            role="recruiter"
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)
        print("✓ Created recruiter user")

    # Create sample job
    job = db.query(JobDescription).filter(JobDescription.title == "Full Stack Developer").first()
    if not job:
        job = JobDescription(
            recruiter_id=recruiter.id,
            title="Full Stack Developer",
            description="Looking for a skilled Full Stack Developer with experience in React and Python.",
            required_skills=["Python", "JavaScript", "React", "SQL", "REST API"],
            preferred_skills=["TypeScript", "Docker", "AWS", "PostgreSQL"],
            min_experience_years=2,
            education_requirements=["Bachelor's in Computer Science", "B.Tech"]
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        print("✓ Created sample job")

    # Create sample questions
    existing_questions = db.query(Question).count()
    if existing_questions == 0:
        questions = [
            # Technical MCQs
            Question(
                job_id=job.id,
                question_type="mcq",
                category="technical",
                difficulty="easy",
                question_text="What is the output of: print(type([]) == list)",
                options=["True", "False", "Error", "None"],
                correct_answer="0",
                max_score=5,
                time_limit_seconds=60,
                skill_tags=["Python"]
            ),
            Question(
                job_id=job.id,
                question_type="mcq",
                category="technical",
                difficulty="medium",
                question_text="Which HTTP method is idempotent?",
                options=["POST", "PATCH", "PUT", "All of the above"],
                correct_answer="2",
                max_score=5,
                time_limit_seconds=60,
                skill_tags=["REST API"]
            ),
            Question(
                job_id=job.id,
                question_type="mcq",
                category="technical",
                difficulty="medium",
                question_text="In React, what hook is used to manage side effects?",
                options=["useState", "useEffect", "useContext", "useReducer"],
                correct_answer="1",
                max_score=5,
                time_limit_seconds=60,
                skill_tags=["React", "JavaScript"]
            ),
            Question(
                job_id=job.id,
                question_type="mcq",
                category="technical",
                difficulty="hard",
                question_text="What is the time complexity of searching in a balanced BST?",
                options=["O(n)", "O(log n)", "O(n log n)", "O(1)"],
                correct_answer="1",
                max_score=10,
                time_limit_seconds=90,
                skill_tags=["Data Structures", "Algorithms"]
            ),
            
            # Coding Questions
            Question(
                job_id=job.id,
                question_type="coding",
                category="technical",
                difficulty="easy",
                question_text="Write a Python function that returns the sum of two numbers. The function should be named 'add' and take two parameters 'a' and 'b'.\n\nExample:\nadd(2, 3) should return 5",
                test_cases=[
                    {"input": "print(add(2, 3))", "expected_output": "5"},
                    {"input": "print(add(-1, 1))", "expected_output": "0"},
                    {"input": "print(add(100, 200))", "expected_output": "300"}
                ],
                max_score=15,
                time_limit_seconds=300,
                skill_tags=["Python", "Functions"]
            ),
            Question(
                job_id=job.id,
                question_type="coding",
                category="technical",
                difficulty="medium",
                question_text="Write a Python function 'is_palindrome' that checks if a string is a palindrome (reads the same forwards and backwards). Ignore case and spaces.\n\nExample:\nis_palindrome('A man a plan a canal Panama') should return True",
                test_cases=[
                    {"input": "print(is_palindrome('racecar'))", "expected_output": "True"},
                    {"input": "print(is_palindrome('hello'))", "expected_output": "False"},
                    {"input": "print(is_palindrome('A man a plan a canal Panama'))", "expected_output": "True"}
                ],
                max_score=20,
                time_limit_seconds=600,
                skill_tags=["Python", "Strings", "Algorithms"]
            ),
            Question(
                job_id=job.id,
                question_type="coding",
                category="technical",
                difficulty="hard",
                question_text="Write a Python function 'find_duplicates' that takes a list of integers and returns a list of duplicates in the order they first appear.\n\nExample:\nfind_duplicates([1, 2, 3, 2, 4, 3, 5]) should return [2, 3]",
                test_cases=[
                    {"input": "print(find_duplicates([1, 2, 3, 2, 4, 3, 5]))", "expected_output": "[2, 3]"},
                    {"input": "print(find_duplicates([1, 1, 1, 1]))", "expected_output": "[1]"},
                    {"input": "print(find_duplicates([1, 2, 3, 4, 5]))", "expected_output": "[]"}
                ],
                max_score=25,
                time_limit_seconds=900,
                skill_tags=["Python", "Arrays", "Algorithms"]
            ),
            
            # Text Response Questions
            Question(
                job_id=job.id,
                question_type="text",
                category="technical",
                difficulty="medium",
                question_text="Explain the difference between REST and GraphQL APIs. When would you choose one over the other?",
                max_score=15,
                time_limit_seconds=600,
                skill_tags=["REST API", "GraphQL", "System Design"]
            ),
            Question(
                job_id=job.id,
                question_type="text",
                category="technical",
                difficulty="medium",
                question_text="Describe how you would optimize a slow database query. What tools and techniques would you use?",
                max_score=15,
                time_limit_seconds=600,
                skill_tags=["SQL", "Database", "Performance"]
            ),
            
            # Psychometric - Scenario MCQs
            Question(
                question_type="mcq",
                category="psychometric",
                difficulty="medium",
                question_text="Your team is behind schedule on a critical project. A team member suggests cutting corners on testing. How do you respond?",
                options=[
                    "Agree to skip testing to meet the deadline",
                    "Refuse completely and insist on full testing",
                    "Propose a risk-based testing approach focusing on critical features",
                    "Escalate to management without discussing with the team"
                ],
                correct_answer="2",  # Best answer
                max_score=10,
                time_limit_seconds=120,
                skill_tags=["leadership", "decision_making", "teamwork"]
            ),
            Question(
                question_type="mcq",
                category="psychometric",
                difficulty="medium",
                question_text="You receive critical feedback about your code during a review. What is your first reaction?",
                options=[
                    "Defend your code and explain why your approach is correct",
                    "Accept the feedback without discussion",
                    "Thank the reviewer and ask for specific suggestions for improvement",
                    "Request a different reviewer who better understands your work"
                ],
                correct_answer="2",
                max_score=10,
                time_limit_seconds=120,
                skill_tags=["resilience", "emotional_intelligence", "communication"]
            ),
            Question(
                question_type="mcq",
                category="psychometric",
                difficulty="medium",
                question_text="A colleague is struggling with a task you're familiar with. You have your own deadlines. What do you do?",
                options=[
                    "Focus on your own work - they need to figure it out themselves",
                    "Take over their task completely to ensure quality",
                    "Share resources and offer brief guidance while prioritizing your work",
                    "Complain to the manager about team skill gaps"
                ],
                correct_answer="2",
                max_score=10,
                time_limit_seconds=120,
                skill_tags=["teamwork", "leadership", "time_management"]
            ),
            
            # Psychometric - Slider Questions
            Question(
                question_type="slider",
                category="psychometric",
                difficulty="easy",
                question_text="On a scale of 1-5, how comfortable are you with taking initiative on projects without being asked?",
                max_score=10,
                time_limit_seconds=30,
                skill_tags=["leadership", "initiative"]
            ),
            Question(
                question_type="slider",
                category="psychometric",
                difficulty="easy",
                question_text="On a scale of 1-5, how well do you handle unexpected changes in project requirements?",
                max_score=10,
                time_limit_seconds=30,
                skill_tags=["adaptability", "resilience"]
            ),
            Question(
                question_type="slider",
                category="psychometric",
                difficulty="easy",
                question_text="On a scale of 1-5, how important is work-life balance to you?",
                max_score=10,
                time_limit_seconds=30,
                skill_tags=["culture_fit", "values"]
            ),
            Question(
                question_type="slider",
                category="psychometric",
                difficulty="easy",
                question_text="On a scale of 1-5, how comfortable are you giving constructive feedback to teammates?",
                max_score=10,
                time_limit_seconds=30,
                skill_tags=["communication", "teamwork"]
            ),
        ]
        
        for q in questions:
            db.add(q)
        
        db.commit()
        print(f"✓ Created {len(questions)} sample questions")
    
    print("\n✅ Seed data complete!")
    print("\nTest credentials:")
    print("  Recruiter: recruiter@cygnusa.com / password123")
    print("\nAPI docs: http://localhost:8000/docs")

if __name__ == "__main__":
    seed_data()
    db.close()

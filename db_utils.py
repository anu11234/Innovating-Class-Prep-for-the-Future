from app import db, User, Lesson, Resource, UserResource
import json
from datetime import datetime

def seed_database():
    """Seed the database with sample data"""
    # Clear existing data
    UserResource.query.delete()
    Lesson.query.delete()
    Resource.query.delete()
    User.query.delete()
    
    # Create sample user
    user = User(username="teacher", email="teacher@example.com")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    
    # Create sample lessons
    lessons = [
        {
            "title": "Introduction to Photosynthesis",
            "subject": "Science",
            "grade_level": "5th Grade",
            "duration": "45 minutes",
            "objectives": "Students will understand the process of photosynthesis",
            "materials": json.dumps(["Plant leaves", "Microscopes", "Worksheets"]),
            "introduction": "Begin by asking students what they know about how plants get their food.",
            "main_activities": json.dumps([
                "Introduce the term 'photosynthesis'",
                "Use a diagram to show the basic inputs and outputs",
                "Have students examine real leaves",
                "Guide students in creating their own labeled diagram"
            ]),
            "conclusion": "Summarize the key points of photosynthesis.",
            "assessment": "Students will be assessed on their diagram accuracy and participation.",
            "extensions": json.dumps([
                "Research environmental factors affecting photosynthesis",
                "Create a model of photosynthesis"
            ]),
            "standards": json.dumps([
                "NGSS 5-LS1-1",
                "NGSS 5-PS3-1"
            ]),
            "status": "Complete",
            "user_id": user.id
        },
        {
            "title": "Fractions and Decimals",
            "subject": "Math",
            "grade_level": "4th Grade",
            "duration": "60 minutes",
            "objectives": "Students will convert between fractions and decimals",
            "materials": json.dumps(["Fraction strips", "Calculators", "Worksheets"]),
            "introduction": "Review what students know about fractions and decimals.",
            "main_activities": json.dumps([
                "Demonstrate conversion methods",
                "Practice with simple examples",
                "Work through more complex problems",
                "Apply to real-world scenarios"
            ]),
            "conclusion": "Review key conversion strategies.",
            "assessment": "Students will complete a worksheet with conversion problems.",
            "extensions": json.dumps([
                "Work with more complex fractions",
                "Apply to measurement problems"
            ]),
            "standards": json.dumps([
                "CCSS.MATH.CONTENT.4.NF.C.6",
                "CCSS.MATH.CONTENT.4.NF.C.7"
            ]),
            "status": "Draft",
            "user_id": user.id
        }
    ]
    
    for lesson_data in lessons:
        lesson = Lesson(**lesson_data)
        db.session.add(lesson)
    
    # Create sample resources
    resources = [
        {
            "title": "Photosynthesis Interactive Diagram",
            "description": "An interactive diagram that allows students to explore the process of photosynthesis step by step.",
            "resource_type": "Interactive",
            "subject": "Science",
            "grade_level": "5th Grade",
            "format": "Web App",
            "url": "https://example.com/photosynthesis",
            "rating": 4.8,
            "downloads": 1245
        },
        {
            "title": "Fraction to Decimal Conversion Worksheet",
            "description": "A printable worksheet with practice problems for converting fractions to decimals and vice versa.",
            "resource_type": "Worksheet",
            "subject": "Math",
            "grade_level": "4th Grade",
            "format": "PDF",
            "url": "https://example.com/fractions",
            "rating": 4.5,
            "downloads": 2189
        },
        {
            "title": "American Revolution Timeline Activity",
            "description": "A collaborative activity where students create a timeline of key events in the American Revolution.",
            "resource_type": "Activity",
            "subject": "History",
            "grade_level": "5th Grade",
            "format": "PDF",
            "url": "https://example.com/revolution",
            "rating": 4.7,
            "downloads": 1876
        },
        {
            "title": "Poetry Analysis Framework",
            "description": "A structured framework to help students analyze and interpret different types of poetry.",
            "resource_type": "Template",
            "subject": "English",
            "grade_level": "5th Grade",
            "format": "Word Document",
            "url": "https://example.com/poetry",
            "rating": 4.6,
            "downloads": 1543
        }
    ]
    
    for resource_data in resources:
        resource = Resource(**resource_data)
        db.session.add(resource)
    
    db.session.commit()
    
    # Create user-resource relationships
    user_resources = [
        {"user_id": user.id, "resource_id": 2, "is_favorite": True},
        {"user_id": user.id, "resource_id": 4, "is_favorite": True}
    ]
    
    for ur_data in user_resources:
        ur = UserResource(**ur_data)
        db.session.add(ur)
    
    db.session.commit()
    
    print("Database seeded successfully!")

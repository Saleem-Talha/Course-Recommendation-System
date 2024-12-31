import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def fetch_course_names():
    """Fetch course names from both tables and return as a list"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="talha_db"
        )
        cursor = connection.cursor()
        
        # Get courses from both tables
        cursor.execute("SELECT course_name FROM course_status")
        status_courses = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT name FROM own_course")
        own_courses = [row[0] for row in cursor.fetchall()]
        
        # Combine and remove duplicates while maintaining order
        all_courses = []
        seen = set()
        for course in status_courses + own_courses:
            if course not in seen:
                seen.add(course)
                all_courses.append(course)
                
        return all_courses
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_course_recommendations(csv_file, course_names):
    """Get top 5 recommendations for each course"""
    # Load dataset
    df = pd.read_csv(csv_file)
    
    # Prepare the text for comparison
    df['combined'] = df['Course Name'] + " " + df['Course Description'] + " " + df['Skills']
    
    # Create corpus with input courses
    course_corpus = course_names + df['combined'].tolist()
    
    # Vectorize
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(course_corpus)
    
    # Calculate similarities
    similarities = cosine_similarity(tfidf_matrix[:len(course_names)], tfidf_matrix[len(course_names):])
    
    all_recommendations = {}
    
    # Process each course
    for idx, course in enumerate(course_names):
        print(f"\nTop 5 Recommendations for: {course}")
        print("-" * 80)
        
        # Get top 5 similar courses
        course_similarities = similarities[idx]
        top_5_indices = course_similarities.argsort()[-5:][::-1]
        
        recommendations = []
        for i, index in enumerate(top_5_indices, 1):
            course_info = {
                'Course Name': df.iloc[index]['Course Name'],
                'University': df.iloc[index]['University'],
                'Difficulty': df.iloc[index]['Difficulty Level'],
                'Rating': df.iloc[index]['Course Rating'],
                'URL': df.iloc[index]['Course URL'],
                'Skills': df.iloc[index]['Skills']
            }
            recommendations.append(course_info)
            
            # Print formatted recommendation
            print(f"\nRecommendation #{i}:")
            print(f"Course: {course_info['Course Name']}")
            print(f"University: {course_info['University']}")
            print(f"Difficulty: {course_info['Difficulty']}")
            print(f"Rating: {course_info['Rating']}")
            print(f"Skills: {course_info['Skills']}")
            print(f"URL: {course_info['URL']}")
        
        all_recommendations[course] = recommendations
        print("-" * 80)
    
    return all_recommendations

def main():
    # Get all courses from database
    course_names = fetch_course_names()
    
    if not course_names:
        print("No courses found in the database!")
        return
    
    print(f"Found {len(course_names)} courses in database:")
    for i, course in enumerate(course_names, 1):
        print(f"{i}. {course}")
    
    # Get recommendations
    try:
        recommendations = get_course_recommendations("Coursera.csv", course_names)
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return

if __name__ == "__main__":
    main()
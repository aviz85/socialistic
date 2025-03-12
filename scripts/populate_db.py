#!/usr/bin/env python
"""
Script to populate the database with fake data for development and testing.
"""
import os
import sys
import random
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialistic.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Django after setting up environment
import django
django.setup()

from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from users.models import Skill, ProgrammingLanguage, Follow
from posts.models import Post, Comment, PostLike, CommentLike
from projects.models import Project, ProjectCollaborator, CollaborationRequest
from notifications.models import Notification
from faker import Faker

User = get_user_model()
fake = Faker()

# Configuration
NUM_USERS = 20
NUM_SKILLS = 15
NUM_PROGRAMMING_LANGUAGES = 10
NUM_POSTS_PER_USER = (2, 8)  # Min, Max
NUM_COMMENTS_PER_POST = (1, 5)  # Min, Max
NUM_PROJECTS_PER_USER = (1, 3)  # Min, Max
FOLLOW_PROBABILITY = 0.3  # 30% chance a user follows another user
LIKE_PROBABILITY = 0.4  # 40% chance a user likes a post
COMMENT_LIKE_PROBABILITY = 0.3  # 30% chance a user likes a comment
COLLABORATION_PROBABILITY = 0.2  # 20% chance a user requests collaboration on a project


def create_users(num_users):
    """Create random users."""
    print(f"Creating {num_users} users...")
    users = []
    
    # Create admin user if it doesn't exist
    if not User.objects.filter(email='admin@example.com').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            full_name='Admin User',
            bio=fake.paragraph()
        )
        users.append(admin)
        print("Created admin user: admin@example.com / adminpassword")
    
    # Create regular users
    for i in range(num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@example.com"
        
        if User.objects.filter(email=email).exists():
            continue
            
        user = User.objects.create_user(
            username=username[:30],  # Ensure username is not too long
            email=email,
            password='password123',
            full_name=f"{first_name} {last_name}",
            bio=fake.paragraph()
        )
        users.append(user)
    
    return users


def create_skills(num_skills):
    """Create programming skills."""
    print(f"Creating {num_skills} skills...")
    skills = []
    
    categories = ['frontend', 'backend', 'mobile', 'data science', 'devops', 'database']
    frontend_skills = ['React', 'Angular', 'Vue.js', 'HTML5', 'CSS3', 'Sass', 'JavaScript', 'TypeScript']
    backend_skills = ['Django', 'Flask', 'FastAPI', 'Express.js', 'Spring Boot', 'Ruby on Rails', 'Laravel']
    mobile_skills = ['React Native', 'Flutter', 'Kotlin', 'Swift', 'Xamarin']
    data_science_skills = ['Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'scikit-learn', 'R']
    devops_skills = ['Docker', 'Kubernetes', 'Jenkins', 'GitHub Actions', 'AWS', 'Azure', 'Google Cloud']
    database_skills = ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'ElasticSearch', 'Firebase']
    
    all_skills = {
        'frontend': frontend_skills,
        'backend': backend_skills,
        'mobile': mobile_skills,
        'data science': data_science_skills,
        'devops': devops_skills,
        'database': database_skills
    }
    
    for category in categories:
        for skill_name in all_skills[category]:
            if len(skills) >= num_skills:
                break
                
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': category}
            )
            skills.append(skill)
    
    # If we need more skills, create random ones
    while len(skills) < num_skills:
        category = random.choice(categories)
        skill_name = fake.word().capitalize() + " " + fake.word().capitalize()
        
        skill, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={'category': category}
        )
        if created:
            skills.append(skill)
    
    return skills


def create_programming_languages(num_languages):
    """Create programming languages."""
    print(f"Creating {num_languages} programming languages...")
    languages = []
    
    language_names = ['Python', 'JavaScript', 'TypeScript', 'Java', 'C#', 'C++', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin']
    
    for language_name in language_names[:num_languages]:
        language, created = ProgrammingLanguage.objects.get_or_create(name=language_name)
        languages.append(language)
    
    return languages


def create_follows(users):
    """Create follow relationships between users."""
    print("Creating follow relationships...")
    follows = []
    
    for follower in users:
        for following in users:
            if follower != following and random.random() < FOLLOW_PROBABILITY:
                follow, created = Follow.objects.get_or_create(
                    follower=follower,
                    following=following
                )
                if created:
                    follows.append(follow)
                    # Create notification with content_type for Follow model
                    Notification.objects.get_or_create(
                        recipient=following,
                        sender=follower,
                        type='follow',
                        text=f"{follower.username} started following you.",
                        content_type=ContentType.objects.get_for_model(Follow),
                        object_id=follow.id
                    )
    
    print(f"Created {len(follows)} follow relationships")
    return follows


def create_posts(users, languages):
    """Create posts for users."""
    print("Creating posts...")
    posts = []
    
    for user in users:
        num_posts = random.randint(*NUM_POSTS_PER_USER)
        for _ in range(num_posts):
            has_code = random.random() > 0.5
            language = random.choice(languages) if has_code else None
            
            post = Post.objects.create(
                author=user,
                content=fake.paragraph(),
                code_snippet=fake.text(max_nb_chars=200) if has_code else "",
                programming_language=language
            )
            posts.append(post)
    
    print(f"Created {len(posts)} posts")
    return posts


def create_comments(users, posts):
    """Create comments on posts."""
    print("Creating comments...")
    comments = []
    
    for post in posts:
        num_comments = random.randint(*NUM_COMMENTS_PER_POST)
        for _ in range(num_comments):
            user = random.choice(users)
            
            comment = Comment.objects.create(
                author=user,
                post=post,
                content=fake.paragraph(nb_sentences=2)
            )
            comments.append(comment)
            
            # Create notification for post author if commenter is not the author
            if user != post.author:
                Notification.objects.get_or_create(
                    recipient=post.author,
                    sender=user,
                    type='comment',
                    content_type=ContentType.objects.get_for_model(post),
                    object_id=post.id,
                    text=f"{user.username} commented on your post"
                )
    
    print(f"Created {len(comments)} comments")
    return comments


def create_likes(users, posts, comments):
    """Create likes for posts and comments."""
    print("Creating likes...")
    post_likes = []
    comment_likes = []
    
    # Post likes
    for post in posts:
        for user in users:
            if user != post.author and random.random() < LIKE_PROBABILITY:
                like, created = PostLike.objects.get_or_create(
                    user=user,
                    post=post
                )
                if created:
                    post_likes.append(like)
                    # Create notification
                    if user != post.author:
                        Notification.objects.get_or_create(
                            recipient=post.author,
                            sender=user,
                            type='like',
                            content_type=ContentType.objects.get_for_model(post),
                            object_id=post.id,
                            text=f"{user.username} liked your post"
                        )
    
    # Comment likes
    for comment in comments:
        for user in users:
            if user != comment.author and random.random() < COMMENT_LIKE_PROBABILITY:
                like, created = CommentLike.objects.get_or_create(
                    user=user,
                    comment=comment
                )
                if created:
                    comment_likes.append(like)
                    # Create notification
                    if user != comment.author:
                        Notification.objects.get_or_create(
                            recipient=comment.author,
                            sender=user,
                            type='like',
                            content_type=ContentType.objects.get_for_model(comment),
                            object_id=comment.id,
                            text=f"{user.username} liked your comment"
                        )
    
    print(f"Created {len(post_likes)} post likes and {len(comment_likes)} comment likes")
    return post_likes, comment_likes


def create_projects(users, skills):
    """Create projects."""
    print("Creating projects...")
    projects = []
    
    # Project statuses
    statuses = ['active', 'completed', 'planning']
    
    for user in users:
        num_projects = random.randint(*NUM_PROJECTS_PER_USER)
        for _ in range(num_projects):
            # Create project
            project = Project.objects.create(
                creator=user,
                title=fake.sentence(nb_words=4)[:-1],  # Remove period
                description=fake.paragraph(),
                repo_url=f"https://github.com/{user.username}/{fake.word()}-{fake.word()}",
                status=random.choice(statuses)
            )
            
            # Add tech stack (1-5 random skills)
            project_skills = random.sample(skills, random.randint(1, min(5, len(skills))))
            project.tech_stack.set(project_skills)
            
            # Add creator as collaborator
            ProjectCollaborator.objects.create(
                project=project,
                user=user,
                role='creator'
            )
            
            projects.append(project)
    
    print(f"Created {len(projects)} projects")
    return projects


def create_collaborations(users, projects):
    """Create collaboration requests."""
    print("Creating collaboration requests...")
    collaboration_requests = []
    
    for project in projects:
        for user in users:
            # Skip if user is already a collaborator
            if ProjectCollaborator.objects.filter(project=project, user=user).exists():
                continue
                
            if user != project.creator and random.random() < COLLABORATION_PROBABILITY:
                status = random.choice(['pending', 'approved', 'rejected'])
                request = CollaborationRequest.objects.create(
                    user=user,
                    project=project,
                    message=fake.paragraph(nb_sentences=1),
                    status=status
                )
                collaboration_requests.append(request)
                
                # Create notification for project creator
                Notification.objects.get_or_create(
                    recipient=project.creator,
                    sender=user,
                    type='project_request',
                    content_type=ContentType.objects.get_for_model(project),
                    object_id=project.id,
                    text=f"{user.username} requested to collaborate on your project '{project.title}'"
                )
                
                # If accepted, add user as collaborator
                if status == 'approved':
                    ProjectCollaborator.objects.get_or_create(
                        project=project,
                        user=user,
                        role='contributor'
                    )
                    
                    # Create notification for requester
                    Notification.objects.get_or_create(
                        recipient=user,
                        sender=project.creator,
                        type='project_accepted',
                        content_type=ContentType.objects.get_for_model(project),
                        object_id=project.id,
                        text=f"Your request to collaborate on '{project.title}' was accepted"
                    )
    
    print(f"Created {len(collaboration_requests)} collaboration requests")
    return collaboration_requests


@transaction.atomic
def main():
    """Main function to populate the database."""
    print("Starting database population...")
    
    # Create basic data
    users = create_users(NUM_USERS)
    skills = create_skills(NUM_SKILLS)
    languages = create_programming_languages(NUM_PROGRAMMING_LANGUAGES)
    
    # Assign random skills to users
    print("Assigning skills to users...")
    for user in users:
        user_skills = random.sample(skills, random.randint(1, min(5, len(skills))))
        user.skills.set(user_skills)
    
    # Create relationships and content
    follows = create_follows(users)
    posts = create_posts(users, languages)
    comments = create_comments(users, posts)
    post_likes, comment_likes = create_likes(users, posts, comments)
    projects = create_projects(users, skills)
    collaboration_requests = create_collaborations(users, projects)
    
    print("Database population completed successfully!")
    print(f"Created {len(users)} users")
    print(f"Created {len(skills)} skills")
    print(f"Created {len(languages)} programming languages")
    print(f"Created {len(follows)} follow relationships")
    print(f"Created {len(posts)} posts")
    print(f"Created {len(comments)} comments")
    print(f"Created {len(post_likes)} post likes")
    print(f"Created {len(comment_likes)} comment likes")
    print(f"Created {len(projects)} projects")
    print(f"Created {len(collaboration_requests)} collaboration requests")
    print(f"Created {Notification.objects.count()} notifications")


if __name__ == '__main__':
    main() 
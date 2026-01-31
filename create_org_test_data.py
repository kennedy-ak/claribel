"""
Script to create test organization with mentors and mentees.
Run this to set up a demonstration of the organization-based mentorship system.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentorship_platform.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile, Organization, MentorAssignment


def create_test_data():
    print("="*60)
    print("Creating Organization Test Data")
    print("="*60)

    # Create admin user (superuser)
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@mentorship.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"✓ Created admin: {admin.username}")
    else:
        admin = User.objects.get(username='admin')
        print("✗ Admin already exists")

    # Create organization
    org_name = "Tech Mentorship Academy"
    organization, created = Organization.objects.get_or_create(
        name=org_name,
        defaults={
            'description': 'A leading technology mentorship program connecting experienced professionals with aspiring developers.',
            'created_by': admin,
            'is_active': True
        }
    )

    if created:
        print(f"\n✓ Created organization: {organization.name}")
        print(f"  Join Code: {organization.join_code}")
    else:
        print(f"\n✗ Organization '{org_name}' already exists")
        print(f"  Join Code: {organization.join_code}")

    # Create mentors
    mentors_data = [
        {
            'username': 'john_mentor',
            'email': 'john@techacademy.com',
            'password': 'mentor123',
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'Senior Software Engineer with 10 years of experience in full-stack development. Passionate about teaching and mentoring.'
        },
        {
            'username': 'sarah_mentor',
            'email': 'sarah@techacademy.com',
            'password': 'mentor123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'bio': 'Data Scientist and ML Engineer. Love helping others transition into tech careers.'
        },
        {
            'username': 'mike_mentor',
            'email': 'mike@techacademy.com',
            'password': 'mentor123',
            'first_name': 'Mike',
            'last_name': 'Williams',
            'bio': 'DevOps Engineer specializing in cloud infrastructure and automation.'
        }
    ]

    mentors = []
    for mentor_data in mentors_data:
        username = mentor_data['username']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=mentor_data['email'],
                password=mentor_data['password'],
                first_name=mentor_data['first_name'],
                last_name=mentor_data['last_name']
            )
            user.profile.role = 'mentor'
            user.profile.organization = organization
            user.profile.bio = mentor_data['bio']
            user.profile.save()
            mentors.append(user.profile)
            print(f"✓ Created mentor: {user.get_full_name()} ({username})")
        else:
            user = User.objects.get(username=username)
            if user.profile.organization != organization:
                user.profile.organization = organization
                user.profile.save()
            mentors.append(user.profile)
            print(f"✗ Mentor already exists: {username}")

    # Create mentees
    mentees_data = [
        {
            'username': 'alice_mentee',
            'email': 'alice@gmail.com',
            'password': 'mentee123',
            'first_name': 'Alice',
            'last_name': 'Brown',
            'bio': 'Aspiring web developer looking to learn React and Python.'
        },
        {
            'username': 'bob_mentee',
            'email': 'bob@gmail.com',
            'password': 'mentee123',
            'first_name': 'Bob',
            'last_name': 'Davis',
            'bio': 'Career changer interested in data science and machine learning.'
        },
        {
            'username': 'carol_mentee',
            'email': 'carol@gmail.com',
            'password': 'mentee123',
            'first_name': 'Carol',
            'last_name': 'Miller',
            'bio': 'CS student wanting to learn DevOps and cloud technologies.'
        },
        {
            'username': 'david_mentee',
            'email': 'david@gmail.com',
            'password': 'mentee123',
            'first_name': 'David',
            'last_name': 'Garcia',
            'bio': 'Self-taught programmer seeking mentorship in software architecture.'
        },
        {
            'username': 'emma_mentee',
            'email': 'emma@gmail.com',
            'password': 'mentee123',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'bio': 'Marketing professional transitioning to tech sales.'
        },
        {
            'username': 'frank_mentee',
            'email': 'frank@gmail.com',
            'password': 'mentee123',
            'first_name': 'Frank',
            'last_name': 'Taylor',
            'bio': 'High school student interested in learning programming.'
        }
    ]

    mentees = []
    for mentee_data in mentees_data:
        username = mentee_data['username']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=mentee_data['email'],
                password=mentee_data['password'],
                first_name=mentee_data['first_name'],
                last_name=mentee_data['last_name']
            )
            user.profile.role = 'mentee'
            user.profile.organization = organization
            user.profile.bio = mentee_data['bio']
            user.profile.save()
            mentees.append(user.profile)
            print(f"✓ Created mentee: {user.get_full_name()} ({username})")
        else:
            user = User.objects.get(username=username)
            if user.profile.organization != organization:
                user.profile.organization = organization
                user.profile.save()
            mentees.append(user.profile)
            print(f"✗ Mentee already exists: {username}")

    # Assign mentees to mentors (round-robin)
    print("\n" + "="*60)
    print("Assigning Mentees to Mentors")
    print("="*60)

    # Clear existing assignments for these mentees
    MentorAssignment.objects.filter(mentee__in=mentees).update(is_active=False)

    for i, mentee in enumerate(mentees):
        # Assign in round-robin fashion
        mentor = mentors[i % len(mentors)]

        # Create assignment
        MentorAssignment.objects.create(
            mentee=mentee,
            mentor=mentor,
            assigned_by=admin,
            notes="Initial assignment for test data"
        )

        print(f"✓ Assigned {mentee.user.get_full_name()} → {mentor.user.get_full_name()}")

    # Summary
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print(f"\nOrganization: {organization.name}")
    print(f"Join Code: {organization.join_code}")
    print(f"\nMentors: {len(mentors)}")
    print(f"Mentees: {len(mentees)}")
    print(f"\nTotal Users Created: {len(mentors) + len(mentees) + 1}")

    print("\n" + "="*60)
    print("Login Credentials")
    print("="*60)
    print("\n┌────────────┬──────────────┬────────────┬────────────────┐")
    print("│ Type       │ Username     │ Password   │ Name           │")
    print("├────────────┼──────────────┼────────────┼────────────────┤")
    print("│ Admin      │ admin        │ admin123   │ Admin User     │")
    print("│ Mentor     │ john_mentor  │ mentor123  │ John Smith     │")
    print("│ Mentor     │ sarah_mentor │ mentor123  │ Sarah Johnson  │")
    print("│ Mentor     │ mike_mentor  │ mentor123  │ Mike Williams  │")
    print("│ Mentee     │ alice_mentee │ mentee123  │ Alice Brown    │")
    print("│ Mentee     │ bob_mentee   │ mentee123  │ Bob Davis      │")
    print("│ Mentee     │ carol_mentee │ mentee123  │ Carol Miller   │")
    print("│ Mentee     │ david_mentee │ mentee123  │ David Garcia   │")
    print("│ Mentee     │ emma_mentee  │ mentee123  │ Emma Wilson    │")
    print("│ Mentee     │ frank_mentee │ mentee123  │ Frank Taylor   │")
    print("└────────────┴──────────────┴────────────┴────────────────┘")

    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)
    print("\n1. Start the server:")
    print("   python manage.py runserver")
    print("\n2. Login to the application:")
    print("   http://127.0.0.1:8000/accounts/login/")
    print("\n3. Explore the organization:")
    print(f"   Use join code: {organization.join_code}")
    print("\n4. Test the mentorship workflow:")
    print("   - Login as a mentee and create todos/reports")
    print("   - Login as a mentor and review submissions")
    print("   - Send messages between mentors and mentees")
    print("\n5. View the organization dashboard:")
    print(f"   http://127.0.0.1:8000/accounts/organization/{organization.id}/")

    print("\n" + "="*60)


if __name__ == '__main__':
    create_test_data()

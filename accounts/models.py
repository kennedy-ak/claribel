from django.db import models
from django.contrib.auth.models import User
import random
import string


def generate_join_code():
    """Generate a unique 8-character join code."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Organization.objects.filter(join_code=code).exists():
            return code


class Organization(models.Model):
    """Organization/Company that contains multiple mentors and mentees."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    join_code = models.CharField(max_length=8, unique=True, default=generate_join_code)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_orgs')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_mentors(self):
        """Get all mentors in this organization."""
        return self.user_profiles.filter(role='mentor')

    def get_mentees(self):
        """Get all mentees in this organization."""
        return self.user_profiles.filter(role='mentee')


class UserProfile(models.Model):
    ROLE_CHOICES = [('mentor', 'Mentor'), ('mentee', 'Mentee')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='user_profiles',
                                      null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email_notifications_enabled = models.BooleanField(default=True)
    sms_notifications_enabled = models.BooleanField(default=False)
    bio = models.TextField(blank=True, help_text="Tell us about yourself")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        org_name = self.organization.name if self.organization else "No Org"
        return f"{self.user.username} - {self.get_role_display()} ({org_name})"

    def get_current_mentor(self):
        """Get the currently assigned mentor for this mentee."""
        if self.role == 'mentee':
            assignment = self.mentee_assignments.filter(is_active=True).select_related('mentor').first()
            return assignment.mentor if assignment else None
        return None

    def get_mentees(self):
        """Get all mentees currently assigned to this mentor."""
        if self.role == 'mentor':
            return UserProfile.objects.filter(
                mentee_assignments__mentor=self,
                mentee_assignments__is_active=True
            )
        return UserProfile.objects.none()


class MentorAssignment(models.Model):
    """Tracks mentor-mentee assignments within an organization."""
    mentee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='mentee_assignments',
                               limit_choices_to={'role': 'mentee'})
    mentor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='mentor_assignments',
                               limit_choices_to={'role': 'mentor'})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Reason for assignment or reassignment")

    class Meta:
        verbose_name = "Mentor Assignment"
        verbose_name_plural = "Mentor Assignments"
        ordering = ['-assigned_at']

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.mentee.user.username} → {self.mentor.user.username} ({status})"

    def save(self, *args, **kwargs):
        # Ensure both users are in the same organization
        if self.mentee.organization != self.mentor.organization:
            raise ValueError("Mentor and mentee must be in the same organization")

        # Deactivate other active assignments for this mentee
        if self.is_active:
            MentorAssignment.objects.filter(
                mentee=self.mentee,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)

        super().save(*args, **kwargs)

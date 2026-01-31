from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Organization, MentorAssignment
from .forms import RegistrationForm, OrganizationForm, MentorAssignmentForm


def register_view(request):
    """User registration with organization code for mentees."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Get form data
            role = form.cleaned_data['role']
            join_code = form.cleaned_data.get('join_code', '').strip().upper()
            org_name = form.cleaned_data.get('org_name', '').strip()
            org_description = form.cleaned_data.get('org_description', '').strip()

            user = form.save()

            # Handle organization assignment
            if role == 'mentee' and join_code:
                try:
                    organization = Organization.objects.get(join_code=join_code, is_active=True)
                    user.profile.organization = organization
                    user.profile.role = 'mentee'
                    user.profile.save()

                    # Assign to a mentor automatically if available
                    available_mentors = organization.get_mentors()
                    if available_mentors.exists():
                        # Simple round-robin: assign to mentor with fewest mentees
                        mentors_with_count = []
                        for mentor in available_mentors:
                            mentee_count = mentor.get_mentees().count()
                            mentors_with_count.append((mentor, mentee_count))

                        # Sort by mentee count and assign to the one with fewest
                        mentors_with_count.sort(key=lambda x: x[1])
                        assigned_mentor = mentors_with_count[0][0]

                        MentorAssignment.objects.create(
                            mentee=user.profile,
                            mentor=assigned_mentor,
                            notes="Auto-assigned on registration"
                        )

                    messages.success(request, f'Successfully joined {organization.name}!')
                except Organization.DoesNotExist:
                    messages.warning(request, 'Invalid organization code. You can join an organization later from your profile.')
                    user.profile.role = 'mentee'
                    user.profile.save()

            elif role == 'mentor':
                user.profile.role = 'mentor'
                user.profile.save()

                # Create organization if mentor provided org name
                if org_name:
                    organization = Organization.objects.create(
                        name=org_name,
                        description=org_description or '',
                        created_by=user,
                        is_active=True
                    )
                    user.profile.organization = organization
                    user.profile.save()
                    messages.success(request, f'Organization "{organization.name}" created successfully! Your join code is: {organization.join_code}')
                else:
                    messages.info(request, 'Mentor account created! Please ask an administrator to add you to an organization, or create your own organization.')

            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """View user profile with organization info."""
    context = {
        'user_profile': request.user.profile
    }

    if request.user.profile.role == 'mentee':
        context['current_mentor'] = request.user.profile.get_current_mentor()

    return render(request, 'accounts/profile.html', context)


@login_required
def mentor_dashboard_view(request):
    """Mentor dashboard showing assigned mentees."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Access restricted to mentors.')
        return redirect('accounts:profile')

    if not request.user.profile.organization:
        messages.warning(request, 'You are not assigned to any organization.')
        return redirect('accounts:profile')

    mentees = request.user.profile.get_mentees()
    organization = request.user.profile.organization

    context = {
        'mentees': mentees,
        'organization': organization
    }
    return render(request, 'accounts/mentor_dashboard.html', context)


@login_required
def mentee_dashboard_view(request):
    """Mentee dashboard showing current mentor."""
    if request.user.profile.role != 'mentee':
        return redirect('accounts:profile')

    current_mentor = request.user.profile.get_current_mentor()
    organization = request.user.profile.organization

    context = {
        'mentor': current_mentor,
        'organization': organization
    }
    return render(request, 'accounts/mentee_dashboard.html', context)


@login_required
def organization_create_view(request):
    """Create a new organization."""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.created_by = request.user
            organization.save()

            # Add creator as a mentor in the organization
            request.user.profile.organization = organization
            request.user.profile.role = 'mentor'
            request.user.profile.save()

            messages.success(request, f'Organization "{organization.name}" created successfully!')
            messages.info(request, f'Your organization join code is: {organization.join_code}')
            return redirect('accounts:organization_detail', org_id=organization.id)
    else:
        form = OrganizationForm()

    return render(request, 'accounts/organization_create.html', {'form': form})


@login_required
def organization_detail_view(request, org_id):
    """View organization details and manage mentors/mentees."""
    organization = get_object_or_404(Organization, id=org_id)

    # Check if user belongs to this organization
    if request.user.profile.organization != organization:
        messages.error(request, 'You do not have permission to view this organization.')
        return redirect('accounts:profile')

    is_admin = organization.created_by == request.user or request.user.is_superuser
    is_mentee = request.user.profile.role == 'mentee'
    is_mentor = request.user.profile.role == 'mentor'

    mentors = organization.get_mentors()

    # Filter mentees based on user role
    if is_mentee:
        # Mentees only see themselves in the list
        mentees = organization.get_mentees().filter(user=request.user)
    else:
        # Mentors and admins see all mentees
        mentees = organization.get_mentees()

    context = {
        'organization': organization,
        'mentors': mentors,
        'mentees': mentees,
        'is_admin': is_admin,
        'is_mentee': is_mentee,
        'is_mentor': is_mentor
    }
    return render(request, 'accounts/organization_detail.html', context)


@login_required
def organization_join_view(request):
    """Join an organization using a code."""
    if request.user.profile.organization:
        messages.warning(request, 'You are already a member of an organization.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        join_code = request.POST.get('join_code', '').strip().upper()
        try:
            organization = Organization.objects.get(join_code=join_code, is_active=True)

            if request.user.profile.role == 'mentor':
                request.user.profile.organization = organization
                request.user.profile.save()
                messages.success(request, f'Joined {organization.name} as a mentor!')
            else:
                # Assign to a mentor
                request.user.profile.organization = organization
                request.user.profile.save()

                available_mentors = organization.get_mentors()
                if available_mentors.exists():
                    mentors_with_count = []
                    for mentor in available_mentors:
                        mentee_count = mentor.get_mentees().count()
                        mentors_with_count.append((mentor, mentee_count))

                    mentors_with_count.sort(key=lambda x: x[1])
                    assigned_mentor = mentors_with_count[0][0]

                    MentorAssignment.objects.create(
                        mentee=request.user.profile,
                        mentor=assigned_mentor,
                        notes="Auto-assigned on joining organization"
                    )
                    messages.success(request, f'Joined {organization.name} and assigned to {assigned_mentor.user.username}!')
                else:
                    messages.warning(request, f'Joined {organization.name}, but no mentors available yet.')

            return redirect('accounts:profile')

        except Organization.DoesNotExist:
            messages.error(request, 'Invalid organization code. Please check and try again.')

    return render(request, 'accounts/organization_join.html')


@login_required
def mentor_assign_view(request, mentee_id):
    """Assign or reassign a mentee to a mentor."""
    mentee = get_object_or_404(UserProfile, id=mentee_id, role='mentee')

    # Check permissions: must be org admin or superuser
    org = mentee.organization
    if not org or (org.created_by != request.user and not request.user.is_superuser):
        messages.error(request, 'You do not have permission to assign mentors.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = MentorAssignmentForm(request.POST, organization=org)
        if form.is_valid():
            mentor = form.cleaned_data['mentor']
            notes = form.cleaned_data.get('notes', 'Reassigned by admin')

            MentorAssignment.objects.create(
                mentee=mentee,
                mentor=mentor,
                assigned_by=request.user,
                notes=notes
            )

            messages.success(request, f'{mentee.user.username} assigned to {mentor.user.username}')
            return redirect('accounts:organization_detail', org_id=org.id)
    else:
        current_mentor = mentee.get_current_mentor()
        form = MentorAssignmentForm(organization=org, initial={'mentor': current_mentor})

    context = {
        'form': form,
        'mentee': mentee,
        'organization': org
    }
    return render(request, 'accounts/mentor_assign.html', context)

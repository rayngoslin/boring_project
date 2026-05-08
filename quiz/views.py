from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q

from .models import Quiz, Question, Answer, Participation
from .forms import QuizForm, QuestionForm, AnswerFormSet, ProfileForm, JoinQuizForm


def home(request):
    query = request.GET.get('q', '').strip()
    base_qs = Quiz.objects.annotate(num_participations=Count('participations'))
    if query:
        base_qs = base_qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    popular_quizzes = base_qs.order_by('-num_participations')[:6]
    new_quizzes = base_qs.order_by('-created_at')[:6]
    join_form = JoinQuizForm()
    return render(request, 'quiz/home.html', {
        'popular_quizzes': popular_quizzes,
        'new_quizzes': new_quizzes,
        'join_form': join_form,
        'query': query,
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'quiz/signup.html', {'form': form})


@login_required
def profile(request):
    participations = (
        request.user.participations.select_related('quiz').order_by('-completed_at')
    )
    return render(request, 'quiz/profile.html', {'participations': participations})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'quiz/profile_edit.html', {'form': form})


def quiz_list(request):
    query = request.GET.get('q', '').strip()
    quizzes = Quiz.objects.select_related('created_by').order_by('-created_at')
    if query:
        quizzes = quizzes.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes, 'query': query})


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    top_scores = (
        Participation.objects.filter(quiz=quiz)
        .select_related('user')
        .order_by('-score', 'completed_at')[:10]
    )
    can_edit = request.user.is_authenticated and (
        request.user == quiz.created_by or request.user.is_staff
    )
    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
        'top_scores': top_scores,
        'can_edit': can_edit,
    })


def quiz_detail_by_code(request, invite_code):
    quiz = get_object_or_404(Quiz, invite_code=invite_code.upper())
    return quiz_detail(request, quiz.id)


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.prefetch_related('answers').all())
    if request.method == 'POST':
        score = 0
        total = len(questions)
        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected:
                try:
                    answer = Answer.objects.get(id=int(selected))
                    if answer.is_correct:
                        score += 1
                except (Answer.DoesNotExist, ValueError):
                    pass
        Participation.objects.create(user=request.user, quiz=quiz, score=score, total=total)
        return redirect('quiz_result', quiz_id=quiz.id)
    return render(request, 'quiz/take_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    participation = (
        Participation.objects.filter(user=request.user, quiz=quiz)
        .order_by('-completed_at')
        .first()
    )
    top_scores = (
        Participation.objects.filter(quiz=quiz)
        .select_related('user')
        .order_by('-score', 'completed_at')[:10]
    )
    return render(request, 'quiz/quiz_result.html', {
        'quiz': quiz,
        'participation': participation,
        'top_scores': top_scores,
    })


def join_quiz(request):
    if request.method == 'POST':
        form = JoinQuizForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['invite_code'].strip().upper()
            quiz = Quiz.objects.filter(invite_code=code).first()
            if quiz:
                return redirect('quiz_detail_by_code', invite_code=quiz.invite_code)
            messages.error(request, f'No quiz found with code "{code}".')
    return redirect('home')


@login_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, 'Quiz created! Now add your questions.')
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'quiz/create_quiz.html', {'form': form})


@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not (request.user == quiz.created_by or request.user.is_staff):
        messages.error(request, 'You do not have permission to edit this quiz.')
        return redirect('quiz_detail', quiz_id=quiz.id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated.')
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    questions = quiz.questions.prefetch_related('answers').all()
    return render(request, 'quiz/edit_quiz.html', {
        'quiz': quiz,
        'form': form,
        'questions': questions,
    })


@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not (request.user == quiz.created_by or request.user.is_staff):
        return redirect('quiz_detail', quiz_id=quiz.id)
    if request.method == 'POST':
        q_form = QuestionForm(request.POST, request.FILES)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            question.order = quiz.questions.count()
            question.save()
            formset = AnswerFormSet(request.POST, instance=question)
            if formset.is_valid():
                formset.save()
            messages.success(request, 'Question added.')
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        q_form = QuestionForm()
        formset = AnswerFormSet()
    return render(request, 'quiz/add_question.html', {
        'quiz': quiz,
        'q_form': q_form,
        'formset': formset,
    })


@login_required
def delete_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    if not (request.user == quiz.created_by or request.user.is_staff):
        return redirect('quiz_detail', quiz_id=quiz.id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted.')
    return redirect('edit_quiz', quiz_id=quiz.id)


@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not (request.user == quiz.created_by or request.user.is_staff):
        messages.error(request, 'You do not have permission to delete this quiz.')
        return redirect('quiz_detail', quiz_id=quiz.id)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted.')
        return redirect('quiz_list')
    return render(request, 'quiz/delete_quiz_confirm.html', {'quiz': quiz})

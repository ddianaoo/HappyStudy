from django.db import models
from accounts.models import CustomUser, CLASSES_CHOICES


class Subject(models.Model):
    title = models.CharField(max_length=255)
    school_year = models.CharField(max_length=10, choices=CLASSES_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'school_year'], name='unique_subject_per_year')
        ]

    def __str__(self):
        return f"{self.title} [{self.school_year}]"


class Quiz(models.Model):
    title = models.CharField(max_length=255, unique=True)

    subject = models.ForeignKey(Subject, related_name='quizzes', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.TextField(max_length=255)
    image = models.ImageField(upload_to='questions_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)

    def __str__(self):
        return self.title[:50] 

    def get_correct_answer(self):
        return self.answers.filter(is_correct=True).first()


class Answer(models.Model):
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class UsersQuizzes(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.firstname} - {self.quiz.title} [started at: {self.started_at}]'


class Result(models.Model):
    user_quiz = models.ForeignKey(UsersQuizzes, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f'Result for {self.user_quiz.user.firstname} in {self.user_quiz.quiz.title}'

from django.db import models
from django.utils import timezone


class Task(models.Model):
    title      = models.CharField(max_length=200)
    completed  = models.BooleanField(default=False)
    due_date   = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', 'due_date', 'created_at']

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Return True if the task is past its due date and not completed."""
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False
# blog/forms.py — Module 06 example
from django import forms
from .models import Post, Comment


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(label='Your Email')
    subject = forms.CharField(max_length=200)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your message…'}),
        min_length=20,
    )
    subscribe = forms.BooleanField(required=False, label='Subscribe to newsletter')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if 'spam.com' in email:
            raise forms.ValidationError("We don't accept that email domain.")
        return email


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'tags', 'body', 'status']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters.")
        return title


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Leave a comment…'}),
        }

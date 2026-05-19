# Module 06 — Forms & User Input

## Learning Objectives
- Create Django `Form` and `ModelForm` classes
- Render forms in templates
- Validate and process form data securely
- Display validation errors
- Handle file uploads in forms

---

## 6.1 Why Use Django Forms?

Django Forms handle three things automatically:
1. **Rendering** HTML input fields
2. **Validation** of submitted data
3. **Cleaning** (converting raw strings to Python types)

---

## 6.2 Basic Form

```python
# blog/forms.py
from django import forms
from .models import Post, Comment


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(label='Your Email')
    subject = forms.CharField(max_length=200)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your message…'}),
    )
    subscribe = forms.BooleanField(required=False, label='Subscribe to newsletter')

    def clean_email(self):
        """Custom validation for the email field."""
        email = self.cleaned_data.get('email', '').lower()
        if 'spam.com' in email:
            raise forms.ValidationError("We don't accept that email domain.")
        return email

    def clean(self):
        """Cross-field validation."""
        cleaned = super().clean()
        name = cleaned.get('name', '')
        message = cleaned.get('message', '')
        if name.lower() in message.lower():
            raise forms.ValidationError("Don't put your name in the message body.")
        return cleaned
```

### Processing a Form in a View

```python
# blog/views.py
from django.contrib import messages
from .forms import ContactForm


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Access cleaned (validated) data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message_text = form.cleaned_data['message']
            # TODO: send email, save to DB, etc.
            messages.success(request, f"Thanks {name}, we'll be in touch!")
            return redirect('contact')
    else:
        form = ContactForm()   # empty form for GET request

    return render(request, 'blog/contact.html', {'form': form})
```

---

## 6.3 ModelForm — Forms Backed by a Model

```python
# blog/forms.py
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'tags', 'body', 'status']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10, 'class': 'rich-editor'}),
            'tags': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'body': 'Post Content',
        }
        help_texts = {
            'slug': 'Auto-filled from title. Letters, numbers, hyphens only.',
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
```

### Using ModelForm in a View

```python
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)   # don't save to DB yet
            post.author = request.user       # set the author manually
            post.save()
            form.save_m2m()                  # save ManyToMany fields (tags)
            messages.success(request, 'Post created!')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Create'})


def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)   # bind instance for edit
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Edit'})
```

---

## 6.4 Rendering Forms in Templates

```html
<!-- blog/templates/blog/post_form.html -->
{% extends 'base.html' %}
{% block title %}{{ action }} Post{% endblock %}

{% block content %}
<h1>{{ action }} Post</h1>

<form method="post" novalidate>
  {% csrf_token %}

  {% if form.non_field_errors %}
    <div class="alert alert-danger">
      {% for error in form.non_field_errors %}
        <p>{{ error }}</p>
      {% endfor %}
    </div>
  {% endif %}

  {% for field in form %}
    <div class="form-group {% if field.errors %}has-error{% endif %}">
      {{ field.label_tag }}
      {{ field }}
      {% if field.help_text %}
        <small class="help-text">{{ field.help_text }}</small>
      {% endif %}
      {% for error in field.errors %}
        <span class="error-message">{{ error }}</span>
      {% endfor %}
    </div>
  {% endfor %}

  <button type="submit" class="btn btn-primary">{{ action }} Post</button>
  <a href="{% url 'blog:post-list' %}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

### Rendering Individual Fields

```html
<!-- Manual control over layout -->
<form method="post">
  {% csrf_token %}
  <div class="row">
    <div class="col">
      <label for="{{ form.title.id_for_label }}">{{ form.title.label }}</label>
      {{ form.title }}
      {{ form.title.errors }}
    </div>
    <div class="col">
      {{ form.category.label_tag }}
      {{ form.category }}
    </div>
  </div>
  {{ form.body.label_tag }}
  {{ form.body }}
  {{ form.body.errors }}
  <button type="submit">Save</button>
</form>
```

---

## 6.5 File Uploads

```python
# forms.py
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
```

```python
# views.py
def profile_edit(request):
    if request.method == 'POST':
        # Pass request.FILES for file uploads
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile_form.html', {'form': form})
```

```html
<!-- Template: must add enctype -->
<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Update Profile</button>
</form>
```

---

## 6.6 CSRF Protection

Django automatically adds CSRF protection. Always include `{% csrf_token %}` inside every `<form method="post">`. Omitting it will result in a `403 Forbidden` error.

---

## Exercises

1. Create a `ContactForm` with name, email, subject, and message fields. Validate that the message is at least 20 characters.
2. Build a `PostForm` as a `ModelForm` — render it in a template and test creating a new post.
3. Add an edit view that pre-fills the form with existing post data using `instance=`.
4. Add file upload to a `Profile` model with an `avatar` ImageField.
5. **Bonus:** Create a form with a `clean()` method that rejects posts if the title already exists.

---

**Next:** [Module 07 — Admin Interface →](../07-admin-interface/README.md)

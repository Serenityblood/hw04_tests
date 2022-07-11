from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Текст сюда', 'group': 'Любую или никакую группу'}
        help_text = {'text': 'Всё что угодно', 'group': 'Из предложеных :)'}

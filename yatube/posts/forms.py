from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'group': 'Группа',
            'text': 'Текст поста',
        }
        help_texts = {
            'group': 'Выберите группу из предложенных',
            'text': 'Введите текст поста',
        }

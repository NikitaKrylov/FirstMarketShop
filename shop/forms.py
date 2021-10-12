from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from .models import Comment, Mark
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from .const import BAD_NAME_SIMBOL


class CommentForm(forms.Form):
    # mark = forms.ChoiceField(choices=((i, i)for i in range(1, 11)), label='Оценка')
    visual = forms.ChoiceField(choices=((i, i)for i in range(1, 11)),
                               widget=forms.TextInput(attrs={"class": 'slider1', "onchange": "changeMark(this)", 'oninput': 'changeMark(this)', 'type': 'range', 'min': '1', 'max': '10', 'step': '1'}), label='Внешний вид')
    # качество
    quality = forms.ChoiceField(choices=((i, i)for i in range(1, 11)),
                                widget=forms.TextInput(attrs={"class": 'slider1', "onchange": "changeMark(this)", 'oninput': 'changeMark(this)', 'type': 'range', 'min': '1', 'max': '10', 'step': '1'}), label='Качество')
    # удобство
    convenience = forms.ChoiceField(choices=((i, i)for i in range(1, 11)),
                                    widget=forms.TextInput(attrs={"class": 'slider1', "onchange": "changeMark(this)", 'oninput': 'changeMark(this)', 'type': 'range', 'min': '1', 'max': '10', 'step': '1'}), label='Удобство')
    price = forms.ChoiceField(choices=((i, i)for i in range(1, 11)),
                              widget=forms.TextInput(attrs={"class": 'slider1', "onchange": "changeMark(this)", 'oninput': 'changeMark(this)', 'type': 'range', 'min': '1', 'max': '10', 'step': '1'}), label='Цена')
    text = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 6, "cols": 20, 'class': 'form-input'}), label='Текст комментария')
    user_model = User

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        # new_comment = Comment.objects.create(
        #     author=kwargs['user'],
        #     text=data['text'],
        #     content_object=kwargs['content_object'],
        #     mark=Mark.objects.create(evaluating=kwargs['user'], evaluation=int(data['mark'])))

        new_comment = Comment.objects.create(
            author=kwargs['user'],
            text=data['text'],
            content_object=kwargs['content_object']
        )
        new_comment.mark = Mark.objects.create(visual=data['visual'],
                                               quality=data['quality'],
                                               price=data['price'],
                                               convenience=data['convenience']
                                               )
        new_comment.save()
        print('Коментарий сохранен')
        return new_comment

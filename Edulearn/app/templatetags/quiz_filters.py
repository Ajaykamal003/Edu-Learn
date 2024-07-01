from django import template

register = template.Library()

@register.filter
def get_answer_index(choice_set):
    for i, choice in enumerate(choice_set):
        if choice.is_correct:  
            return i
    return -1  

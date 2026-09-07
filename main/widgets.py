from django import forms
from django.utils.safestring import mark_safe

class DragDropImageWidget(forms.ClearableFileInput):
    template_name = 'widgets/dragdrop_image_widget.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['is_image'] = True  # optional
        return context

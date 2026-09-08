from django import forms


class DragDropImageWidget(forms.ClearableFileInput):
    """
    A widget that renders a drag-and-drop zone for file/image uploads.
    Works with HTMX if present on the page, but degrades gracefully
    to a plain (styled) file input if it isn't.
    """
    template_name = 'widgets/dragdrop_image_widget.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        attrs = context['widget']['attrs']
        attrs.setdefault('id', f'dropzone-{name}')
        attrs['accept'] = attrs.get('accept', 'image/*')
        return context

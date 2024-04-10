from django.db import transaction


class FormsetsInsideFormMixin:
    """
    A mixin to be used with Django forms to manage inline formsets and atomic
    transactions in an integrated manner. This mixin provides functionality to handle 
    both the saving of the main form's instance and its associated inline formsets 
    within a single atomic transaction, ensuring data integrity and consistency.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formsets = self.get_formsets(instance=self.instance)

    def get_formsets(self, formsets={}, instance=None, *args, **kwargs):

        if hasattr(self, 'formsets') is False:
            self.formsets = formsets
            for formset_name, formset in self.formsets.items():
                setattr(self, formset_name, formset)
        return self.formsets

    def is_valid(self):
        if not super().is_valid():
            return False

        formsets = self.get_formsets()
        formset_errors = {}
        for formset_name, formset in formsets.items():
            if not formset.is_valid():
                formset_errors[formset_name] = formset.errors

        if formset_errors:
            self.errors['formset_errors'] = formset_errors
            return False

        return True

    @transaction.atomic
    def save(self, commit=True, *args, **kwargs):
        instance = self.save_instance(commit=commit)
        if instance and instance.pk:
            self.save_formsets(instance)
        return instance
    
    def save_instance(self, commit=True, *args, **kwargs):
        return super().save(commit=commit, *args, **kwargs)

    def save_formsets(self, instance, *args, **kwargs):
        formsets = self.get_formsets(instance=instance)
        for formset in formsets.values():   
            formset.save()
from django.contrib import admin


class ModelAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None, **kwargs):
        fields = super().get_readonly_fields(request, obj, **kwargs)
        fields = fields + tuple([field for field in ['created_at', 'updated_at'] if hasattr(self.model, field)])
        return fields
    

class UUIDModelAdmin(ModelAdmin):
    readonly_fields = ('uuid',)

    def get_fields(self, request, obj=None, **kwargs):
        fields = super().get_fields(request, obj, **kwargs)
        fields.remove('uuid')
        fields.insert(0, 'uuid')
        return fields
    

class SlugModelAdmin(ModelAdmin):
    def get_fields(self, request, obj=None, **kwargs):
        fields = super().get_fields(request, obj, **kwargs)
        fields.remove('slug')
        fields.insert(fields.index(self.model.SLUG_FIELD) + 1, 'slug')
        return fields


class RegisterAdminMixin:
    def register_model_admins(self):
        models_to_ignore = [
            'admin.LogEntry',
            'contenttypes.ContentType',
            'sessions.Session',
            'authtoken.TokenProxy',
            'authtoken.Token',
        ]
        for model in self.get_models():
            try:
                if model._meta.label in models_to_ignore:
                    continue
                admin_class = ModelAdmin
                if hasattr(model, 'uuid'):
                    admin_class = UUIDModelAdmin
                elif hasattr(model, 'slug'):
                    admin_class = SlugModelAdmin
                admin.site.register(model, admin_class)
            except admin.sites.AlreadyRegistered:
                pass

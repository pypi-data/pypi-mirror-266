from djangoldp.permissions import LDPBasePermission
from django.db.models.query import QuerySet
import logging 

logger = logging.getLogger(__name__)

class RegionalReferentPermissions(LDPBasePermission):
    permissions = {'view', 'add', 'change', 'control'}
    """Gives write permissions to regional referents and read permissions to everyone"""
    def check_permission(self, user, model, obj):
      if user.is_anonymous:
        return False

      if not obj.__class__.__name__ == 'Community':
        assert getattr(model._meta, 'community_path', False), f'Community path not defined for model {model.__name__}'

        # We need to loop through the object class meta path provided
        for field in model._meta.community_path.split('.'):
          obj = getattr(obj, field)

      return bool(set.intersection(set(user.regions.all()), set(obj.tzcld_profile.regions.all())))

    def has_object_permission(self, request, view, obj=None):
        return self.check_permission(request.user, view.model, obj)

    def get_permissions(self, user, model, obj=None):
        if not obj or self.check_permission(user, model, obj):
            return self.permissions
        return set()

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the property.
        return obj.owner == request.user

class IsAgentOrOwner(permissions.BasePermission):
    """
    Custom permission to allow agents or owners to manage properties.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow if user is staff/admin
        if request.user.is_staff:
            return True
        
        # Allow if user has agent profile
        if hasattr(request.user, 'profile') and request.user.profile.is_agent:
            return True
        
        return True

    def has_object_permission(self, request, view, obj):
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # Owner can do anything
        if obj.owner == request.user:
            return True
        
        # Agent can edit if they are assigned to the property
        if obj.agent == request.user:
            return True
        
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False

class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile.
    """
    def has_object_permission(self, request, view, obj):
        # Users can only edit their own profile
        return obj.user == request.user

class CanContactProperty(permissions.BasePermission):
    """
    Custom permission to allow users to contact property owners.
    """
    def has_permission(self, request, view):
        # Anyone can contact property owners
        return True

class CanViewProperty(permissions.BasePermission):
    """
    Custom permission to allow viewing of properties.
    """
    def has_permission(self, request, view):
        # Anyone can view properties
        return True

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff

class CanManageFavorites(permissions.BasePermission):
    """
    Custom permission to allow users to manage their own favorites.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Users can only manage their own favorites
        return obj.user == request.user

class CanReviewProperty(permissions.BasePermission):
    """
    Custom permission to allow users to review properties they've interacted with.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Users can only edit their own reviews
        return obj.user == request.user

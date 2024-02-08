from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Request-level permission to only allow owners of an object and admin users to read it.
    Assumes the request instance has an `user_id` parameter argument.

    When the authenticstion is not provided, the request.user will be an instance of AnonymousUser.
    """

    def has_permission(self, request, view):
        # if user is admin, allow
        if request.user.is_staff:
            return True
        # check the request.user.id against the user_id of the request argument
        return request.user.id == int(view.kwargs.get("user_id"))

    def has_object_permission(self, request, view, obj):
        # if user is admin, allow
        if request.user.is_staff:
            return True
        # check the request.user.id against the user_id of the request argument
        return request.user.id == obj.user_id

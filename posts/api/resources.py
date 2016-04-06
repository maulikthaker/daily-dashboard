from tastypie.resources import ModelResource
from posts.models import RecentAddresses


class MyModelResource(ModelResource):
    class Meta:
        queryset = RecentAddresses.objects.all()
        resource_name = 'recentadd'
        filtering = {'address' : 'contains'}
        # print(queryset)
        # allowed_methods = ['get']
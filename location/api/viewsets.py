from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import *


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_nearby_agents(request):
    """
    Get a list of nearby agents
    """
    if request.method == 'GET':
        serializer = AgentLocationSerializer()
        return Response(serializer.data,
                        status=status.HTTP_200_OK)
    if request.method == 'POST':
        print(request.data)
        serializer = AgentLocationSerializer(data=request.data)
        if serializer.is_valid():
            # Get Data
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            # get location
            location = Point(longitude, latitude, srid=4326)
            # Get nearby agents
            agents = Agent.objects.filter(is_active=True).annotate(
                distance=Distance('location', location)
            ).order_by('distance')[0:5]
            if agents:
                data = AgentSerializer(agents, many=True)

                # data = serializers.serialize('json', agents)
                print(data)
                return Response(data=data.data, status=status.HTTP_200_OK)
            else:
                data = 'No Agents are Available'
                return Response(data=data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

from rest_framework import serializers
from location.models import Agent


class AgentLocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class AgentSerializer(serializers.ModelSerializer):
    agent_data = serializers.SerializerMethodField('get_agent_data')

    class Meta:
        model = Agent
        fields = ['agent_data', 'location']

    def get_agent_data(self, obj):
        agent = obj
        data = {
            'name': agent.user.full_name,
            'phone_number': agent.user.phone_number
        }
        return data

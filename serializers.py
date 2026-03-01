from rest_framework import serializers
from .models import ResumeAnalysis

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    improvement_plan = serializers.JSONField(required=False)

    class Meta:
        model = ResumeAnalysis
        fields = '__all__'

class ResumeUploadSerializer(serializers.Serializer):
    resume_file = serializers.FileField()
    target_role = serializers.CharField(max_length=255)

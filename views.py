from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ResumeUploadSerializer, ResumeAnalysisSerializer
from .pdf_parser import extract_text_from_pdf
from .llm_engine import analyze_resume_with_llm
from .models import ResumeAnalysis, RoleSkill
from .caching import get_cached_analysis, set_cached_analysis
from jobs.adzuna_service import fetch_live_jobs
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, "index.html")

class AnalyzeResumeView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        client_ip = request.META.get('REMOTE_ADDR')
        if cache.get(f"rate_limit_{client_ip}"):
            return Response({"error": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(f"rate_limit_{client_ip}", True, 5)

        serializer = ResumeUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_file = serializer.validated_data['resume_file']
        target_role = serializer.validated_data['target_role']

        try:
            resume_text = extract_text_from_pdf(resume_file)
            if not resume_text:
                return Response({"error": "PDF extraction failed"}, status=status.HTTP_400_BAD_REQUEST)

            cached = get_cached_analysis(resume_text, target_role)
            if cached:
                return Response(cached, status=status.HTTP_200_OK)

            analysis_data = analyze_resume_with_llm(resume_text, target_role)
            
            # Fetch Live Jobs
            live_jobs = fetch_live_jobs(target_role)
            analysis_data['live_jobs'] = live_jobs

            analysis = ResumeAnalysis.objects.create(
                resume_file=resume_file,
                target_role=target_role,
                extracted_skills=analysis_data['extracted_skills'],
                matched_skills=analysis_data['matched_skills'],
                missing_skills=analysis_data['missing_skills'],
                match_percentage=analysis_data['match_percentage'],
                readiness_score=analysis_data['readiness_score'],
                roadmap=analysis_data['roadmap'],
                confidence_score=analysis_data.get('confidence_score', 0.0),
                resume_embedding=analysis_data.get('resume_embedding')
            )

            result = ResumeAnalysisSerializer(analysis).data
            
            # Append non-model data
            result['improvement_plan'] = analysis_data.get('improvement_plan')
            result['dashboard_summary'] = analysis_data.get('dashboard_summary')
            result['live_jobs'] = analysis_data.get('live_jobs')
            result['role_profile_version'] = analysis_data.get('role_profile_version')
                
            set_cached_analysis(resume_text, target_role, result)

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"API Error: {e}")
            return Response({"error": "Processing failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleProfileListView(APIView):
    def get(self, request):
        profiles = RoleSkill.objects.all().order_by('-created_at')
        data = [{
            "role": p.role_name,
            "skills": p.required_skills,
            "version": p.version,
            "locked": p.is_locked
        } for p in profiles]
        return Response(data)

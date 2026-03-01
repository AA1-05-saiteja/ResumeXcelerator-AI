from django.db import models

class RoleMarketBenchmark(models.Model):
    role = models.CharField(max_length=100, unique=True)
    core_skills = models.JSONField()
    advanced_skills = models.JSONField()
    experience_expectation = models.TextField()
    project_expectation = models.TextField()
    version = models.CharField(max_length=20, default="v1.0")
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.role} ({self.version})"

class ResumeAnalysis(models.Model):
    resume_file = models.FileField(upload_to='resumes/')
    target_role = models.CharField(max_length=255)
    extracted_skills = models.JSONField(default=list)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    match_percentage = models.FloatField()
    readiness_score = models.FloatField()
    roadmap = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    resume_embedding = models.JSONField(null=True, blank=True)
    role_profile_version = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Resume Analyses"

    def __str__(self):
        return f"{self.target_role} - {self.created_at}"

class RoleSkill(models.Model):
    role_name = models.CharField(max_length=255, unique=True)
    required_skills = models.JSONField(default=list)
    version = models.IntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.role_name} (v{self.version})"

class CandidateAnalysis(models.Model):
    candidate_id = models.CharField(max_length=100)
    role_match_data = models.JSONField()
    improvement_plan = models.JSONField()
    dashboard_summary = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

from rest_framework import serializers
from .models import Category, Lesson, UserLessonProgress

class LessonSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'duration', 'completed', 'image']

    def get_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserLessonProgress.objects.get(user=request.user, lesson=obj)
                return progress.completed
            except UserLessonProgress.DoesNotExist:
                return False
        return False

    def get_duration(self, obj):
        return f"{obj.duration} min"

class CategorySerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'slug', 'title', 'description','image','lessons']

    def get_lessons(self, obj):
        lessons = obj.lessons.all().order_by('id')
        return LessonSerializer(lessons, many=True, context=self.context).data 
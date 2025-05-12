from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import requests
from django.http import JsonResponse
from django.core.cache import cache
import requests
from django.utils import timezone
from .models import Category, Lesson, UserLessonProgress
from .serializers import CategorySerializer, LessonSerializer
from users.utils import Autherize

class CategoryFetch(APIView):
    @Autherize()
    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get('id')
        lessons_flag = request.query_params.get('lessons')
        if not category_id:
            return Response(
                {"error": "Category id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if category_id == 'all':
                data = Category.objects.all().order_by('id')
                serialized_data = CategorySerializer(data, many=True).data
                return Response(serialized_data)
                
            category = Category.objects.get(id=category_id)
            if lessons_flag == 'all':
                lessons = category.lessons.all().order_by('id')
                lessons_data = [
                    {
                        'id': str(lesson.id),
                        'title': lesson.title,
                        'description': lesson.description,
                        'duration': f"{lesson.duration} min",
                        'progress': self._get_lesson_progress(request.user, lesson),
                        'image': lesson.image or ""
                    }
                    for lesson in lessons
                ]
                return Response(lessons_data)
            if not lessons_flag:
                data = {
                    'title': category.title,
                    'description': category.description,
                    'image': category.image or "",
                    'slug': category.slug,
                    'progress': 100,
                }
                return Response(data)
            else:
                try:
                    lesson = category.lessons.get(id=lessons_flag)
                except Lesson.DoesNotExist:
                    return Response(
                        {"error": "Lesson not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                lesson_data = {
                    'id': str(lesson.id),
                    'title': lesson.title,
                    'description': lesson.description,
                    'duration': f"{lesson.duration} min",
                    'progress': self._get_lesson_progress(request.user, lesson),
                    'image': lesson.image or "",
                    'steps': [
                        {
                            'id': str(step.id),
                            'step_number': step.step_number,
                            'sign_name': step.sign_name,
                            'image': step.image or "",
                            'video': step.video or ""
                        }
                        for step in lesson.steps.all().order_by('step_number')
                    ]
                }
                return Response(lesson_data)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_lesson_progress(self, user, lesson):
        if user.is_authenticated:
            try:
                progress = UserLessonProgress.objects.get(user=user, lesson=lesson)
                return 100 if progress.completed else 0
            except UserLessonProgress.DoesNotExist:
                return 0
        return 0

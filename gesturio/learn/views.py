from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Lesson, UserLessonProgress
from .serializers import CategorySerializer
from users.utils import Autherize
from .utils import get_category_completed_data

class CategoryFetch(APIView):
    
    @Autherize()
    def get(self, request, **kwargs):
        
        user = kwargs['user']
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
                completed_data = get_category_completed_data(user)
                
                completion_dict = {item['id']: item for item in completed_data}
                
                for category in serialized_data:
                    category_id = str(category['id'])
                    if category_id in completion_dict:
                        category.update(completion_dict[category_id])
                
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
                        'image': lesson.image or "",
                        'completed': UserLessonProgress.objects.filter(
                            user=user,
                            lesson=lesson,
                            category=category
                        ).exists(),
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
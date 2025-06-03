
from .models import Category, UserLessonProgress

def get_category_completed_data(user):
   
    categories = Category.objects.all()
    completed_categories = []
    
    for category in categories:
        lessons = category.lessons.all()
        total_lessons = lessons.count()
        
        if total_lessons == 0:
            continue
            
        completed_lessons = UserLessonProgress.objects.filter(
            user=user,
            lesson__in=lessons,
            completed=True
        ).count()
        
        completion_percentage = (completed_lessons / total_lessons) * 100
        
        completed_categories.append({
            'id': str(category.id),
            'title': category.title,
            'slug': category.slug,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_percentage': round(completion_percentage, 2),
            'is_fully_completed': completed_lessons == total_lessons
        })
    
    return completed_categories


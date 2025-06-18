import PyPDF2
import re
import io
from difflib import SequenceMatcher
from django.db.models import Q
from .models import Curriculum, CurriculumSubject, Subject

def parse_transcript_pdf(pdf_file):
    """
    Парсит PDF транскрипта студента и извлекает список предметов с кредитами
    Возвращает список словарей вида {'name': 'Название', 'credits': float}
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = "\n".join([page.extract_text() for page in pdf_reader.pages])
        
        # Улучшенное регулярное выражение для разных форматов транскриптов
        pattern = re.compile(
            r'(?P<name>[А-Яа-яA-Za-z].+?)\s+'  # Название предмета
            r'(?P<credits>\d+\.?\d*)\s*'        # Кредиты
            r'(?:кр|credits|ECTS)',             # Варианты обозначения кредитов
            re.IGNORECASE
        )
        
        subjects = []
        for match in pattern.finditer(text):
            try:
                subjects.append({
                    'name': match.group('name').strip(),
                    'credits': float(match.group('credits'))
                })
            except (ValueError, IndexError):
                continue
                
        return subjects
        
    except Exception as e:
        print(f"Error parsing transcript PDF: {e}")
        return []

def parse_curriculum_pdf(pdf_file, curriculum):
    """
    Парсит PDF учебного плана и создает CurriculumSubject
    Возвращает количество созданных предметов
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = "\n".join([page.extract_text() for page in pdf_reader.pages])
        
        # Шаблон для учебных планов (может потребоваться адаптация)
        pattern = re.compile(
            r'(?P<code>[A-Z0-9.]+)\s+'         # Код предмета
            r'(?P<name>.+?)\s+'                 # Название
            r'(?P<credits>\d+\.?\d*)\s*'        # Кредиты
            r'(?P<semester>\d+)\s+'             # Семестр
            r'(?P<type>[ОФ]?)',                 # Тип (О - обязательный, Ф - факультативный)
            re.IGNORECASE
        )
        
        created = 0
        for match in pattern.finditer(text):
            try:
                subject, _ = Subject.objects.get_or_create(
                    name=match.group('name').strip(),
                    defaults={'code': match.group('code').strip()}
                )
                
                CurriculumSubject.objects.create(
                    curriculum=curriculum,
                    subject=subject,
                    credits=float(match.group('credits')),
                    semester=int(match.group('semester')),
                    is_required=match.group('type').upper() == 'О'
                )
                created += 1
            except Exception as e:
                print(f"Error creating curriculum subject: {e}")
                continue
                
        return created
        
    except Exception as e:
        print(f"Error parsing curriculum PDF: {e}")
        return 0

def match_subject(subject_name, curriculum_subjects):
    """
    Находит наиболее подходящий предмет в учебном плане по названию
    Использует алгоритм схожести строк
    """
    best_match = None
    highest_ratio = 0
    
    for cs in curriculum_subjects:
        ratio = SequenceMatcher(
            None, 
            subject_name.lower(), 
            cs.subject.name.lower()
        ).ratio()
        
        if ratio > highest_ratio and ratio > 0.6:  # Порог схожести 60%
            highest_ratio = ratio
            best_match = cs
    
    return best_match

def calculate_credit_transfer(student_subjects, curriculum_subjects):
    """
    Расширенная версия функции подсчета кредитов:
    - student_subjects: список словарей {'name': str, 'credits': float}
    - curriculum_subjects: QuerySet CurriculumSubject
    Возвращает детализированный результат сравнения
    """
    results = []
    total_required = sum(cs.credits for cs in curriculum_subjects)
    total_has = 0
    total_missing = 0
    
    # Сначала проверяем точные соответствия
    unmatched_student = []
    for ss in student_subjects:
        matched = False
        for cs in curriculum_subjects:
            if ss['name'].lower() == cs.subject.name.lower():
                credit_diff = max(0, cs.credits - ss['credits'])
                status = 'full' if credit_diff == 0 else 'partial'
                
                results.append({
                    'subject': cs.subject.name,
                    'required': cs.credits,
                    'has': ss['credits'],
                    'difference': credit_diff,
                    'status': status
                })
                
                total_has += ss['credits']
                total_missing += credit_diff
                matched = True
                break
        
        if not matched:
            unmatched_student.append(ss)
    
    # Затем проверяем похожие предметы (для оставшихся)
    for ss in unmatched_student:
        best_match = match_subject(ss['name'], curriculum_subjects)
        if best_match:
            credit_diff = max(0, best_match.credits - ss['credits'])
            status = 'full' if credit_diff == 0 else 'partial'
            
            results.append({
                'subject': f"{best_match.subject.name} (~{ss['name']})",
                'required': best_match.credits,
                'has': ss['credits'],
                'difference': credit_diff,
                'status': status,
                'is_approximate': True
            })
            
            total_has += ss['credits']
            total_missing += credit_diff
    
    # Добавляем полностью отсутствующие предметы
    matched_curriculum_ids = [r.get('curriculum_subject_id') for r in results if 'curriculum_subject_id' in r]
    for cs in curriculum_subjects:
        if cs.id not in matched_curriculum_ids:
            results.append({
                'subject': cs.subject.name,
                'required': cs.credits,
                'has': 0,
                'difference': cs.credits,
                'status': 'missing'
            })
            total_missing += cs.credits
    
    # Расчет процента выполнения
    completion = round((total_has / total_required * 100), 2) if total_required > 0 else 0
    
    return {
        'results': sorted(results, key=lambda x: x['subject']),
        'total_required': total_required,
        'total_has': total_has,
        'total_missing': total_missing,
        'completion_percentage': completion,
        'is_complete': total_missing == 0
    }

def get_curriculum_summary(curriculum):
    """
    Генерирует сводку по учебному плану
    """
    subjects = curriculum.subjects.all()
    return {
        'total_subjects': subjects.count(),
        'total_credits': sum(s.credits for s in subjects),
        'by_semester': {
            sem: {
                'credits': sum(s.credits for s in subjects if s.semester == sem),
                'subjects': [s.subject.name for s in subjects if s.semester == sem]
            }
            for sem in range(1, 9)  # Для 8 семестров
        }
    }
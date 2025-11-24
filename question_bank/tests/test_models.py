from django.test import TestCase
from django.contrib.auth import get_user_model
from question_bank.models import ExamName, Subject, Area, PartName, ChapterName, TopicName, QuestionBank, Report
from django.utils import timezone

User = get_user_model()

class ExamNameTestCase(TestCase):
    def setUp(self):
        self.exam = ExamName.objects.create(name="UPSC")

    def test_exam_str_method(self):
        self.assertEqual(str(self.exam), "UPSC")

class SubjectTestCase(TestCase):
    def setUp(self):
        self.exam = ExamName.objects.create(name="UPSC")
        self.subject = Subject.objects.create(name="History", exam=self.exam)

    def test_subject_str_method(self):
        self.assertEqual(str(self.subject), "History --> (UPSC)")

class AreaTestCase(TestCase):
    def setUp(self):
        self.exam = ExamName.objects.create(name="UPSC")
        self.subject = Subject.objects.create(name="History", exam=self.exam)
        self.area = Area.objects.create(name="Ancient History", subject=self.subject)

    def test_area_str_method(self):
        self.assertEqual(str(self.area), "Ancient History --> (History - UPSC)")

class PartNameTestCase(TestCase):
    def setUp(self):
        self.exam = ExamName.objects.create(name="UPSC")
        self.subject = Subject.objects.create(name="History", exam=self.exam)
        self.area = Area.objects.create(name="Ancient History", subject=self.subject)
        self.part = PartName.objects.create(name="Part 1", area=self.area)

    def test_part_str_method(self):
        self.assertEqual(str(self.part), "Part 1 (Ancient History - History - UPSC)")

class ChapterNameTestCase(TestCase):
    def setUp(self):
        self.exam = ExamName.objects.create(name="UPSC")
        self.subject = Subject.objects.create(name="History", exam=self.exam)
        self.area = Area.objects.create(name="Ancient History", subject=self.subject)
        self.part = PartName.objects.create(name="Part 1", area=self.area)
        self.chapter = ChapterName.objects.create(name="Chapter 1", part=self.part)

    def test_chapter_str_method(self):
        self.assertEqual(str(self.chapter), "Chapter 1 (Part 1 - Ancient History - History)")

class TopicNameTestCase(TestCase):
    def setUp(self):
        self.exam = ExamName.objects.create(name="UPSC")
        self.subject = Subject.objects.create(name="History", exam=self.exam)
        self.area = Area.objects.create(name="Ancient History", subject=self.subject)
        self.part = PartName.objects.create(name="Part 1", area=self.area)
        self.chapter = ChapterName.objects.create(name="Chapter 1", part=self.part)
        self.topic = TopicName.objects.create(name="Topic 1", chapter=self.chapter)

    def test_topic_str_method(self):
        self.assertEqual(str(self.topic), "Topic 1 (Chapter 1 - Part 1)")

class QuestionBankTestCase(TestCase):
    def setUp(self):
        self.exam = ExamName.objects.create(name="UPSC")
        self.subject = Subject.objects.create(name="History", exam=self.exam)
        self.area = Area.objects.create(name="Ancient History", subject=self.subject)
        self.part = PartName.objects.create(name="Part 1", area=self.area)
        self.chapter = ChapterName.objects.create(name="Chapter 1", part=self.part)
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')

        self.question = QuestionBank.objects.create(
            type_of_question='mcq1',
            exam_stage='Prelims',
            exam_year=2020,
            language='English',
            degree_of_difficulty='Moderate',
            question_sub_type='simple_type',
            question_part="What is the capital of India?",
            marks=2.0,
            negative_marks=0.5,
            created_by=self.user,
            created_at=timezone.now()  # Use timezone-aware datetime
        )
        self.question.exam_name.add(self.exam)
        self.question.subject_name.add(self.subject)
        self.question.area_name.add(self.area)
        self.question.part_name.add(self.part)
        self.question.chapter_name.add(self.chapter)

    def test_question_creation(self):
        self.assertEqual(self.question.exam_year, 2020)
        self.assertEqual(self.question.question_part, "What is the capital of India?")
        self.assertEqual(self.question.language, 'English')
        self.assertEqual(self.question.marks, 2.0)
        self.assertEqual(self.question.created_by.email, 'testuser@example.com')

    def test_question_str_method(self):
        exam_names = ', '.join([exam.name for exam in self.question.exam_name.all()])
        self.assertEqual(str(self.question), f"Question {self.question.question_number} - {exam_names} {self.question.exam_year}")

class ReportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='admin@example.com', password='testpass')
        self.report = Report.objects.create(
            report_type='this_week',
            created_by=self.user,
            total_questions=10,
            total_phrases=5,
            total_suggestions=3,
            simple_type_count=4,
            list_1_type_count=2,
            list_2_type_count=1,
            ra_type_count=2,
            true_false_type_count=1,
            fill_blank_count=0,
            report_date=timezone.now()  # Use timezone-aware datetime for the report date
        )

    def test_report_creation(self):
        self.assertEqual(self.report.total_questions, 10)
        self.assertEqual(self.report.created_by.email, 'admin@example.com')

    def test_report_str_method(self):
        report_type_display = dict(Report.REPORT_TYPE_CHOICES).get(self.report.report_type, 'Unknown Report')
        self.assertEqual(str(self.report), f"{report_type_display} - {self.report.report_date}")

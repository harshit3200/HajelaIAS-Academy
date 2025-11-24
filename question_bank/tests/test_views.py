from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from question_bank.models import QuestionBank, Report
from io import BytesIO
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class GenerateQuestionsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')

    def test_generate_questions_view(self):
        response = self.client.get(reverse('generate_questions'))
        self.assertEqual(response.status_code, 200)


class AnalyticsDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')

    def test_analytics_dashboard_view(self):
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)


class GenerateReportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')

    def test_generate_this_week_csv(self):
        response = self.client.get(reverse('generate_this_week_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_generate_earlier_week_csv(self):
        response = self.client.get(reverse('generate_earlier_week_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')


class UploadFileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')

    def test_upload_file_view(self):
        # Create a sample Excel file
        excel_content = BytesIO()
        df = pd.DataFrame({
            'question_sub_type': ['simple_type'],
            'exam_name': ['UPSC'],
            'subject_name': ['General Studies'],
            'area_name': ['Indian History'],
            'marks': [10],
            'negative_marks': [0],
            'exam_year1': [2022],
        })
        df.to_excel(excel_content, index=False)
        excel_content.seek(0)

        # Upload the file
        excel_file = SimpleUploadedFile('testfile.xlsx', excel_content.read(), content_type='application/vnd.ms-excel')
        response = self.client.post(reverse('upload-file'), {'file': excel_file})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect on success


class AddQuestionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')

    def test_add_simple_type_question_view(self):
        response = self.client.get(reverse('add-simple-type-question'))
        self.assertEqual(response.status_code, 200)

    def test_add_r_and_a_type_question_view(self):
        response = self.client.get(reverse('add-r-and-a-type-question'))
        self.assertEqual(response.status_code, 200)

    def test_add_list_type_1_question_view(self):
        response = self.client.get(reverse('add-list-type-1-question'))
        self.assertEqual(response.status_code, 200)

    def test_add_list_type_2_question_view(self):
        response = self.client.get(reverse('add-list-type-2-question'))
        self.assertEqual(response.status_code, 200)

    def test_add_true_and_false_type_question_view(self):
        response = self.client.get(reverse('add-true-and-false-type-question'))
        self.assertEqual(response.status_code, 200)

    def test_add_fill_in_the_blank_question_view(self):
        response = self.client.get(reverse('add-fill-in-the-blank-question'))
        self.assertEqual(response.status_code, 200)


class InputSuggestionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')

    def test_add_input_suggestion_view(self):
        response = self.client.get(reverse('add-input-suggestion'))
        self.assertEqual(response.status_code, 200)

    def test_input_suggestion_list_view(self):
        response = self.client.get(reverse('input-suggestion-list'))
        self.assertEqual(response.status_code, 200)

# Write by kamlesh lovewanshi
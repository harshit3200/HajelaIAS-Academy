from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User  # Import the User model
from django.conf import settings
from django.utils import timezone
import uuid
from ckeditor.fields import RichTextField


# Custom Manager for Subject to handle creating subjects for all exams
class AreaManager(models.Manager):
    def create_hierarchy(self, area_name, part_name, chapter_name, topic_name, subtopic_name=None):
        """
        Create a hierarchy starting from an Area and linking to PartName, ChapterName, TopicName, and optionally SubTopicName.
        """
        # Create the Area
        area = self.create(name=area_name)
        
        # Create the Section linked to the Area
        section = Section.objects.create(name=f"{area_name} Section", section_unit_si="Default SI", area=area)
        
        # Create the Part linked to the Section
        part = PartName.objects.create(name=part_name, part_serial="Default Serial", section=section)
        
        # Create the Chapter linked to the Part
        chapter = ChapterName.objects.create(name=chapter_name, chapter_number="Default Chapter", part=part)
        
        # Create the Topic linked to the Chapter
        topic = TopicName.objects.create(name=topic_name, chapter=chapter)
        
        # Optionally create a SubTopic linked to the Topic
        if subtopic_name:
            SubTopicName.objects.create(name=subtopic_name, sub_topic_si_number="Default SI", 
                                         sub_topic_code_non_ctpl="Default Non-CTPL", 
                                         sub_topic_code_ctpl="Default CTPL", topic=topic)

        return area




from django.core.exceptions import ValidationError
import uuid


class Area(models.Model):
    area_SI_Code = models.CharField(max_length=50, primary_key=True, editable=True)
    area_Short_Code = models.CharField(max_length=50)
    area_Colour_Hex = models.CharField(max_length=50, default='#FFFFFF')
    area_Serial = models.CharField(max_length=50)
    mppsc_para = models.CharField(max_length=255, default='MPPSC PARA')
    upsc_para = models.CharField(max_length=255, default='UPSC PARA')
    name = models.CharField(max_length=255)

    def clean(self):
        try:
            float(self.area_SI_Code)
        except ValueError:
            raise ValidationError({'area_SI_Code': 'Must be a valid float-like string (e.g., "1.0").'})

    def __str__(self):
        return self.name


class Section(models.Model):
    section_Unit_SI = models.CharField(max_length=50, primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='sections')

    def clean(self):
        try:
            float(self.section_Unit_SI)
        except ValueError:
            raise ValidationError({'section_Unit_SI': 'Must be a valid float-like string (e.g., "1.0").'})

    def __str__(self):
        return f"{self.name} --> ({self.area.name})"


class PartName(models.Model):
    part_serial = models.CharField(max_length=50, primary_key=True, editable=True)
    part_short_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='parts')

    def clean(self):
        try:
            float(self.part_serial)
        except ValueError:
            raise ValidationError({'part_serial': 'Must be a valid float-like string (e.g., "1.0").'})

    def __str__(self):
        return f"{self.name} ({self.section.name} - {self.section.area.name})"


class ChapterName(models.Model):
    chapter_number = models.CharField(max_length=50, primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    part = models.ForeignKey(PartName, on_delete=models.CASCADE, related_name='chapters')

    def clean(self):
        try:
            float(self.chapter_number)
        except ValueError:
            raise ValidationError({'chapter_number': 'Must be a valid float-like string (e.g., "1.0").'})

    def __str__(self):
        return f"{self.name} ({self.part.name} - {self.part.section.name} - {self.part.section.area.name})"


class TopicName(models.Model):
    topic_SI_number = models.CharField(max_length=50, primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    chapter = models.ForeignKey(ChapterName, on_delete=models.CASCADE, related_name='topics', null=True, blank=True)

    def clean(self):
        try:
            float(self.topic_SI_number)
        except ValueError:
            raise ValidationError({'topic_SI_number': 'Must be a valid float-like string (e.g., "1.0").'})

    def __str__(self):
        chapter_name = self.chapter.name if self.chapter else "No Chapter"
        part_name = self.chapter.part.name if self.chapter and self.chapter.part else "No Part"
        return f"{self.name} ({chapter_name} - {part_name})"



from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class SubTopicName(models.Model):
    sub_topic_SI_Number = models.CharField(max_length=50, primary_key=True, editable=True)
    sub_topic_Code_Non_CTPL = models.CharField(max_length=255)
    sub_topic_Code_CTPL = models.CharField(max_length=255)
    sub_topic_short_Code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(TopicName, on_delete=models.CASCADE, related_name='sub_topics', null=True, blank=True)

    exams = models.ManyToManyField('ExamName', related_name='subtopics', blank=True)
    evergreenindex = models.ManyToManyField('EvergreenIndexName', related_name='subtopics', blank=True)
    hashtags = models.ManyToManyField('HashtagsName', related_name='subtopics', blank=True)

    def clean(self):
        try:
            float(self.sub_topic_SI_Number)
        except ValueError:
            raise ValidationError({'sub_topic_SI_Number': 'Must be a valid float-like string (e.g., "1.0").'})

    def __str__(self):
        if self.topic:
            return f"{self.name} ({self.topic.name} - {self.topic.chapter.part.section.area.name})"
        return self.name

from django.utils.text import slugify

class HashtagsName(models.Model):
    hashtags_SI_Number = models.SlugField(max_length=50, primary_key=True, editable=True)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.hashtags_SI_Number = slugify(self.hashtags_SI_Number)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.name} ({self.hashtags_SI_Number})"


class MicroSubTopicName(models.Model):
    micro_sub_topic_SI_number = models.CharField(max_length=50, primary_key=True, editable=True)
    name = models.CharField(max_length=255)
    subtopics = models.ForeignKey(SubTopicName, on_delete=models.CASCADE, related_name='microsubtopic', null=True, blank=True)

    def clean(self):
        try:
            float(self.micro_sub_topic_SI_number)
        except ValueError:
            raise ValidationError({'micro_sub_topic_SI_number': 'Must be a valid float-like string (e.g., "1.0").'})

    def __str__(self):
        if self.subtopics:
            return f"{self.name} ({self.subtopics.name} - {self.subtopics.topic.chapter.part.section.area.name})"
        return self.name

from django.db import models
from django.utils import timezone


class KeywordName(models.Model):
    """
    Stores high-signal keywords for tagging questions and subtopics.
    Each keyword (e.g., 'Fiscal Policy') can be linked to multiple SubTopics
    and MicroSubTopics (e.g., Economy, Governance).
    """

    # 🏷 Keyword text
    name = models.CharField(max_length=255, db_index=True)

    # 🌐 Language tag
    language = models.CharField(
        max_length=10,
        choices=(("EN", "English"), ("HI", "Hindi")),
        default="EN"
    )

    # 🔗 Many-to-many: one keyword → many SubTopics
    subtopics = models.ManyToManyField(
        "SubTopicName",
        blank=True,
        related_name="keywords"
    )

    # 🔗 Many-to-many: one keyword → many MicroSubTopics
    micro_subtopics = models.ManyToManyField(
        "MicroSubTopicName",
        blank=True,
        related_name="keywords"
    )

    # 📊 Metadata
    relevance_score = models.FloatField(default=1.0)
    created_at = models.DateTimeField(default=timezone.now)
    source = models.CharField(
        max_length=20,
        choices=(
            ("manual", "Manual Entry"),
            ("ai", "AI Generated"),
            ("merged", "Merged"),
        ),
        default="manual",
    )

    class Meta:
        ordering = ["name", "language"]
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"
        indexes = [
            models.Index(fields=["name", "language"]),
        ]
        unique_together = ("name", "language")  # ✅ Prevent duplicate language pairs

    def __str__(self):
        """
        Display keyword + up to 3 subtopic short codes for context.
        """
        subs = ", ".join(
            [s.sub_topic_short_Code for s in self.subtopics.all()[:3] if s.sub_topic_short_Code]
        ) or "NoSubtopic"
        return f"{self.name} [{self.language}] → {subs}"

    # ✅ Safe linking helper
    def link_to_subtopic(self, subtopic_obj):
        """
        Safely link this keyword to one or more subtopics (many-to-many).
        """
        if not subtopic_obj:
            return
        if isinstance(subtopic_obj, (list, tuple, set)):
            for st in subtopic_obj:
                if st:
                    self.subtopics.add(st)
        else:
            self.subtopics.add(subtopic_obj)
        self.save(update_fields=[])



class ExamName(models.Model):
    exam_SI_Number = models.CharField(max_length=50, primary_key=True, editable=True)
    exam_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

class EvergreenIndexName(models.Model):
    evergreen_index_SI_Number = models.CharField(max_length=50, primary_key=True, editable=True)
    evergreen_index_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

import random
from django.db import models
from django.utils import timezone
from django.conf import settings

class QuestionBank(models.Model):
    QUESTION_SOURCES = (
        ('pyq', 'PYQ'),
        ('moq', 'Model Question'),
        ('osq', 'Other Source Question'),
    )

    QUESTION_TYPES = (
        ('simple_type', 'Simple Type'),
        ('r_and_a_type', 'R & A Type'),
        ('list_type_1', 'List Type 1'),
        ('list_type_2', 'List Type 2'),
        ('true_and_false_type', 'True & False'),
        ('fill_in_the_blank_type', 'Fill in the Blank'),
        ('statement_type', 'Statement Type'),   # ✅ New type
    )

    type_of_question = models.CharField(max_length=10, choices=QUESTION_SOURCES, default='moq')
    language = models.CharField(max_length=1, choices=(('e', 'English'), ('h', 'Hindi')), default='e')
    base_question_id = models.PositiveIntegerField(null=True, blank=True)
    question_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    area_name = models.ManyToManyField('Area', related_name='questions')
    section_name = models.ManyToManyField('Section', related_name='questions')
    part_name = models.ManyToManyField('PartName', related_name='questions')
    chapter_name = models.ManyToManyField('ChapterName', related_name='questions', blank=True)
    topic_name = models.ManyToManyField('TopicName', related_name='questions', blank=True)
    subtopic_name = models.ManyToManyField('SubTopicName', related_name='questions', blank=True)
    exam_name = models.ManyToManyField('ExamName', related_name='questions', blank=True)
    evergreenindex_name = models.ManyToManyField('EvergreenIndexName', related_name='questions', blank=True)
    key_words = models.TextField(blank=True, null=True, help_text="Comma separated keywords for search & analysis")


    # ✅ NEW FIELDS for AI & bilingual keyword support
    key_words_en = models.TextField(
        blank=True,
        null=True,
        help_text="English keywords generated or matched for AI tagging"
    )

    key_words_hi = models.TextField(
        blank=True,
        null=True,
        help_text="Hindi keywords generated or matched for AI tagging"
    )

    ai_matched_subtopic = models.ForeignKey(
        'SubTopicName',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_tagged_questions',
        help_text="Subtopic matched or predicted by AI keyword logic"
    )


    exam_stage = models.CharField(max_length=100, blank=True, null=True)
    exam_year = models.IntegerField(blank=True, null=True) 
    script = models.TextField(blank=True, null=True)
    # evergreen_index = models.PositiveIntegerField(default=5, null=True, blank=True)
    marks = models.FloatField(default=0.0)
    negative_marks = models.FloatField(default=0.0)
    degree_of_difficulty = models.CharField(max_length=100)
    elim_tactics_degree = models.CharField(max_length=100)
    current_relevance = models.CharField(max_length=100)
    current_relevance_topic = models.TextField(blank=True, null=True)
    question_sub_type = models.CharField(max_length=100, choices=QUESTION_TYPES, default='simple_type')

    question_number = models.PositiveIntegerField(blank=True, null=True)
    question_part = models.TextField(blank=True, null=True)
    question_part_hi = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    reason_hi = models.TextField(blank=True, null=True)
    assertion = models.TextField(blank=True, null=True)
    assertion_hi = models.TextField(blank=True, null=True)
    question_part_first = models.TextField(blank=True, null=True)
    question_part_first_hi = models.TextField(blank=True, null=True)
    question_part_third = models.TextField(blank=True, null=True)
    question_part_third_hi = models.TextField(blank=True, null=True)

    list_1_name = models.CharField(max_length=100, blank=True, null=True)
    list_1_name_hi = models.CharField(max_length=100, blank=True, null=True)
    list_2_name = models.CharField(max_length=100, blank=True, null=True)
    list_2_name_hi = models.CharField(max_length=100, blank=True, null=True)

    list_1_row1 = models.CharField(max_length=255, blank=True, null=True)
    list_1_row2 = models.CharField(max_length=255, blank=True, null=True)
    list_1_row3 = models.CharField(max_length=255, blank=True, null=True)
    list_1_row4 = models.CharField(max_length=255, blank=True, null=True)
    list_1_row5 = models.CharField(max_length=255, blank=True, null=True)
    list_1_row6 = models.CharField(max_length=255, blank=True, null=True)
    list_1_row7 = models.CharField(max_length=255, blank=True, null=True)
    list_1_row8 = models.CharField(max_length=255, blank=True, null=True)

    list_2_row1 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row2 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row3 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row4 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row5 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row6 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row7 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row8 = models.CharField(max_length=255, blank=True, null=True)
    list_2_row9 = models.CharField(max_length=255, blank=True, null=True)
    

    list_1_row1_hi = models.CharField(max_length=255, blank=True, null=True)
    list_1_row2_hi = models.CharField(max_length=255, blank=True, null=True)
    list_1_row3_hi = models.CharField(max_length=255, blank=True, null=True)
    list_1_row4_hi = models.CharField(max_length=255, blank=True, null=True)
    list_1_row5_hi = models.CharField(max_length=255, blank=True, null=True)
    list_1_row6_hi = models.CharField(max_length=255, blank=True, null=True)
    list_1_row7_hi = models.CharField(max_length=255, blank=True, null=True)
    list_1_row8_hi = models.CharField(max_length=255, blank=True, null=True)

    list_2_row1_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row2_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row3_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row4_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row5_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row6_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row7_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row8_hi = models.CharField(max_length=255, blank=True, null=True)
    list_2_row9_hi = models.CharField(max_length=255, blank=True, null=True)

    stmt_line_row1 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row2 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row3 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row4 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row5 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row6 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row7 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row8 = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row9 = models.CharField(max_length=255, blank=True, null=True)

    # Hindi versions
    stmt_line_row1_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row2_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row3_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row4_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row5_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row6_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row7_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row8_hi = models.CharField(max_length=255, blank=True, null=True)
    stmt_line_row9_hi = models.CharField(max_length=255, blank=True, null=True)


    answer_option_a = models.TextField(blank=True, null=True)
    answer_option_b = models.TextField(blank=True, null=True)
    answer_option_c = models.TextField(blank=True, null=True)
    answer_option_d = models.TextField(blank=True, null=True)

    answer_option_a_hi = models.TextField(blank=True, null=True)
    answer_option_b_hi = models.TextField(blank=True, null=True)
    answer_option_c_hi = models.TextField(blank=True, null=True)
    answer_option_d_hi = models.TextField(blank=True, null=True)

    correct_answer_choice = models.CharField(max_length=255, blank=True, null=True)
    correct_answer_description = models.TextField(blank=True, null=True)
    correct_answer_description_hi = models.TextField(blank=True, null=True)

    table_head_a = models.CharField(max_length=100, null=True, blank=True)
    table_head_b = models.CharField(max_length=100, null=True, blank=True)
    table_head_c = models.CharField(max_length=100, null=True, blank=True)
    table_head_d = models.CharField(max_length=100, null=True, blank=True)

    table_head_a_hi = models.CharField(max_length=100, null=True, blank=True)
    table_head_b_hi = models.CharField(max_length=100, null=True, blank=True)
    table_head_c_hi = models.CharField(max_length=100, null=True, blank=True)
    table_head_d_hi = models.CharField(max_length=100, null=True, blank=True)

    head_a_data1 = models.CharField(max_length=100, null=True, blank=True)
    head_a_data2 = models.CharField(max_length=100, null=True, blank=True)
    head_a_data3 = models.CharField(max_length=100, null=True, blank=True)
    head_a_data4 = models.CharField(max_length=100, null=True, blank=True)
    head_b_data1 = models.CharField(max_length=100, null=True, blank=True)
    head_b_data2 = models.CharField(max_length=100, null=True, blank=True)
    head_b_data3 = models.CharField(max_length=100, null=True, blank=True)
    head_b_data4 = models.CharField(max_length=100, null=True, blank=True)
    head_c_data1 = models.CharField(max_length=100, null=True, blank=True)
    head_c_data2 = models.CharField(max_length=100, null=True, blank=True)
    head_c_data3 = models.CharField(max_length=100, null=True, blank=True)
    head_c_data4 = models.CharField(max_length=100, null=True, blank=True)
    head_d_data1 = models.CharField(max_length=100, null=True, blank=True)
    head_d_data2 = models.CharField(max_length=100, null=True, blank=True)
    head_d_data3 = models.CharField(max_length=100, null=True, blank=True)
    head_d_data4 = models.CharField(max_length=100, null=True, blank=True)

    head_a_data1_hi = models.CharField(max_length=100, null=True, blank=True)
    head_a_data2_hi = models.CharField(max_length=100, null=True, blank=True)
    head_a_data3_hi = models.CharField(max_length=100, null=True, blank=True)
    head_a_data4_hi = models.CharField(max_length=100, null=True, blank=True)
    head_b_data1_hi = models.CharField(max_length=100, null=True, blank=True)
    head_b_data2_hi = models.CharField(max_length=100, null=True, blank=True)
    head_b_data3_hi = models.CharField(max_length=100, null=True, blank=True)
    head_b_data4_hi = models.CharField(max_length=100, null=True, blank=True)
    head_c_data1_hi = models.CharField(max_length=100, null=True, blank=True)
    head_c_data2_hi = models.CharField(max_length=100, null=True, blank=True)
    head_c_data3_hi = models.CharField(max_length=100, null=True, blank=True)
    head_c_data4_hi = models.CharField(max_length=100, null=True, blank=True)
    head_d_data1_hi = models.CharField(max_length=100, null=True, blank=True)
    head_d_data2_hi = models.CharField(max_length=100, null=True, blank=True)
    head_d_data3_hi = models.CharField(max_length=100, null=True, blank=True)
    head_d_data4_hi = models.CharField(max_length=100, null=True, blank=True)

    image = models.ImageField(upload_to='Question Images', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # ✅ Only assign if not already manually set
        if self.question_number is None:
            last = QuestionBank.objects.order_by('-question_number').first()
            self.question_number = last.question_number + 1 if last else 1

        if not self.base_question_id:
            while True:
                rand_id = random.randint(100000, 999999)
                if not QuestionBank.objects.filter(base_question_id=rand_id).exists():
                    self.base_question_id = rand_id
                    break

        self.question_id = f"{self.type_of_question}_{self.base_question_id}_{self.language}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.question_id} - Q{self.question_number}"

    @property
    def list_1_items(self):
        return [item for item in [
            self.list_1_row1, self.list_1_row2, self.list_1_row3, self.list_1_row4,
            self.list_1_row5, self.list_1_row6, self.list_1_row7, self.list_1_row8
        ] if item]

    @property
    def list_2_items(self):
        return [item for item in [
            self.list_2_row1, self.list_2_row2, self.list_2_row3, self.list_2_row4,
            self.list_2_row5, self.list_2_row6, self.list_2_row7, self.list_2_row8
        ] if item]

    @property
    def list_1_items(self):
        return [item for item in [
            self.list_1_row1, self.list_1_row2, self.list_1_row3, self.list_1_row4,
            self.list_1_row5, self.list_1_row6, self.list_1_row7, self.list_1_row8
        ] if item]

    @property
    def list_2_items(self):
        return [item for item in [
            self.list_2_row1, self.list_2_row2, self.list_2_row3, self.list_2_row4,
            self.list_2_row5, self.list_2_row6, self.list_2_row7, self.list_2_row8
        ] if item]

    @property
    def list_1_items_hi(self):
        return [item for item in [
            self.list_1_row1_hi, self.list_1_row2_hi, self.list_1_row3_hi, self.list_1_row4_hi,
            self.list_1_row5_hi, self.list_1_row6_hi, self.list_1_row7_hi, self.list_1_row8_hi
        ] if item]

    @property
    def list_2_items_hi(self):
        return [item for item in [
            self.list_2_row1_hi, self.list_2_row2_hi, self.list_2_row3_hi, self.list_2_row4_hi,
            self.list_2_row5_hi, self.list_2_row6_hi, self.list_2_row7_hi, self.list_2_row8_hi
        ] if item]
    
    @property
    def stmt_lines(self):
        return [item for item in [
            self.stmt_line_row1, self.stmt_line_row2, self.stmt_line_row3,
            self.stmt_line_row4, self.stmt_line_row5, self.stmt_line_row6,
            self.stmt_line_row7, self.stmt_line_row8, self.stmt_line_row9
        ] if item]

    @property
    def stmt_lines_hi(self):
        return [item for item in [
            self.stmt_line_row1_hi, self.stmt_line_row2_hi, self.stmt_line_row3_hi,
            self.stmt_line_row4_hi, self.stmt_line_row5_hi, self.stmt_line_row6_hi,
            self.stmt_line_row7_hi, self.stmt_line_row8_hi, self.stmt_line_row9_hi
        ] if item]


# LectureNote Models

from django.db import models
from django.conf import settings
from django.utils import timezone

class LectureNote(models.Model):
    NOTE_TYPE_CHOICES = (
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('pptx', 'PowerPoint'),
        ('other', 'Other'),
    )

    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('hi', 'Hindi'),
    )

    CTPL_CHOICES = [
        ('UPSC', 'UPSC'),
        ('MPPSC', 'MPPSC'),
        ('BOTH', 'UPSC & MPPSC Both'),
    ]

    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    description = models.TextField(blank=True, null=True)
    note_file = models.FileField(upload_to='lecture_notes/', blank=True, null=True)
    note_type = models.CharField(max_length=10, choices=NOTE_TYPE_CHOICES, default='pdf')
    ctpl = models.CharField(max_length=10, choices=CTPL_CHOICES, default='UPSC')

    # ✅ Hierarchical associations
    area = models.ForeignKey('Area', on_delete=models.CASCADE, related_name='lecture_notes')
    part = models.ForeignKey('PartName', on_delete=models.CASCADE, related_name='lecture_notes')
    chapter = models.ForeignKey('ChapterName', on_delete=models.CASCADE, related_name='lecture_notes')
    topic = models.ForeignKey('TopicName', on_delete=models.CASCADE, related_name='lecture_notes', blank=True, null=True)
    subtopic = models.ForeignKey('SubTopicName', on_delete=models.CASCADE, related_name='lecture_notes', blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.chapter.name} ({self.get_language_display()})"


# Input Suggestion Model
from django.db import models
from django.conf import settings
from django.utils import timezone

from django.db import models
from django.conf import settings
from django.utils import timezone
from ckeditor.fields import RichTextField  # If you’re using CKEditor

class InputSuggestion(models.Model):
    SOURCE_CHOICES = [
        ('social_media', 'Social Media (SM)'),
        ('print_media', 'Print Media'),
        ('electronic_media', 'Electronic Media (other than SM)'),
        ('self', 'Self'),
        ('others', 'Others'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending_faculty', 'Pending with Faculty'),
        ('pending_director', 'Pending with Director'),
        ('approved', 'Approved'),
        ('approved_with_modification', 'Approved with Modification'),
        ('rejected', 'Rejected'),
    ]

    language = models.CharField(max_length=100, default='', blank=True, null=True)
    brief_description = RichTextField()
    details = RichTextField()
    question_video = models.FileField(upload_to='input_suggestion/videos/', blank=True, null=True)
    question_link = models.URLField(max_length=255, blank=True, null=True)
    other_text = models.TextField(blank=True, null=True)
    current_relevance = models.CharField(max_length=100)
    current_relevance_topic = models.TextField(blank=True, null=True)

    # ✅ NEW: Credit / Courtesy
    credit_or_courtesy = models.CharField(max_length=255, blank=True, null=True)

    area_name = models.ManyToManyField('Area', related_name='input_suggestions')
    part_name = models.ManyToManyField('PartName', related_name='input_suggestions')
    chapter_name = models.ManyToManyField('ChapterName', related_name='input_suggestions', blank=True)
    topic_name = models.ManyToManyField('TopicName', related_name='input_suggestions', blank=True)
    subtopic_name = models.ManyToManyField('SubTopicName', related_name='input_suggestions', blank=True)
    exams = models.ManyToManyField('ExamName', related_name='input_suggestions', blank=True)
    hashtags = models.ManyToManyField('HashtagsName', related_name='input_suggestions', blank=True)


    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='self')

    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='pending_faculty')
    approved_or_rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_or_rejected_input_suggestions'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    def approval_status_display(self):
        if self.approval_status == 'rejected' and self.approved_or_rejected_by:
            return f"Rejected ({self.approved_or_rejected_by.get_full_name() or self.approved_or_rejected_by.email})"
        else:
            return dict(self.APPROVAL_STATUS_CHOICES).get(self.approval_status, 'Unknown')

    def __str__(self):
        return self.brief_description[:50]

class InputSuggestionImage(models.Model):
    question = models.ForeignKey(InputSuggestion, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='input_suggestion/images/')


class InputSuggestionDocument(models.Model):
    question = models.ForeignKey(InputSuggestion, related_name='documents', on_delete=models.CASCADE)
    document = models.FileField(upload_to='input_suggestion/documents/')


class QuoteIdiomPhrase(models.Model):
    TYPE_CHOICES = (
        ('quote', 'Quote'),
        ('idiom', 'Idiom'),
        ('phrase', 'Phrase'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('staff_approved', 'Staff Approved'),
        ('admin_approved', 'Admin Approved'),
        ('rejected', 'Rejected'),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content = models.TextField()
    meaning = models.TextField(blank=True, null=True)  # Meaning for idioms and phrases
    author = models.CharField(max_length=255, blank=True, null=True)  # Optional field for author or source
    
    areas = models.ManyToManyField('Area', blank=True)
    section = models.ManyToManyField('section', blank=True)
    parts = models.ManyToManyField('PartName', blank=True)
    chapters = models.ManyToManyField('ChapterName', blank=True)
    topics = models.ManyToManyField('TopicName', blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Timezone-aware datetime
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    staff_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='staff_approved_quotes', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    admin_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='admin_approved_quotes', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    rejected_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_display()}: {self.content[:50]}..."



class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('this_week', 'This Week Report'),
        ('earlier', 'Earlier Report'),
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    report_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_questions = models.IntegerField(default=0)
    total_phrases = models.IntegerField(default=0)
    total_suggestions = models.IntegerField(default=0)
    simple_type_count = models.IntegerField(default=0)
    list_1_type_count = models.IntegerField(default=0)
    list_2_type_count = models.IntegerField(default=0)
    ra_type_count = models.IntegerField(default=0)
    true_false_type_count = models.IntegerField(default=0)
    fill_blank_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.report_date}"



class Batch(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class BatchGeneratedQuestion(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)



class GeneratedImage(models.Model):
    prompt = models.TextField()
    image = models.ImageField(upload_to='generated_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for: {self.prompt[:30]}"
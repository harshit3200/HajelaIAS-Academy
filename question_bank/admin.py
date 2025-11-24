from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin
from import_export import resources
from import_export import resources, fields

from import_export.admin import ImportExportModelAdmin
from .models import (
    Area, Section, PartName, ChapterName, TopicName, SubTopicName, ExamName, QuestionBank,KeywordName,
    InputSuggestion, InputSuggestionImage, InputSuggestionDocument, QuoteIdiomPhrase,
    Batch, BatchGeneratedQuestion, GeneratedImage,  EvergreenIndexName, MicroSubTopicName, HashtagsName ,LectureNote # ✅ Include GeneratedImage
)
import logging
import re

# Set up logging for debugging
logger = logging.getLogger(__name__)

# Helper function for validation
def validate_flexible_code(value, field_name):
    valid_pattern = r'^-?\d+(\.\d+)?$|^[a-zA-Z0-9.\-]+$'
    if not re.match(valid_pattern, value):
        raise ValidationError(f"Invalid {field_name}: {value}. Must be a float-like or alphanumeric pattern.")

# ============================
# Resources for Import/Export
# ============================

class AreaResource(resources.ModelResource):
    class Meta:
        model = Area
        fields = (
            'area_SI_Code', 'name', 'area_Short_Code', 'area_Colour_Hex',
            'area_Serial', 'mppsc_para', 'upsc_para'
        )
        export_order = fields
        import_id_fields = ['area_SI_Code']

    def before_import_row(self, row, **kwargs):
        if 'area_SI_Code' in row:
            row['area_SI_Code'] = str(row['area_SI_Code']).strip()
            validate_flexible_code(row['area_SI_Code'], "area_SI_Code")
        return super().before_import_row(row, **kwargs)

class SectionResource(resources.ModelResource):
    class Meta:
        model = Section
        fields = ('section_Unit_SI', 'name', 'area')
        export_order = fields
        import_id_fields = ['section_Unit_SI']

    def before_import_row(self, row, **kwargs):
        if 'section_Unit_SI' in row:
            row['section_Unit_SI'] = str(row['section_Unit_SI']).strip()
            validate_flexible_code(row['section_Unit_SI'], "section_Unit_SI")
        return super().before_import_row(row, **kwargs)

class PartNameResource(resources.ModelResource):
    class Meta:
        model = PartName
        fields = ('part_serial', 'name', 'part_short_code', 'section')
        export_order = fields
        import_id_fields = ['part_serial']

    def before_import_row(self, row, **kwargs):
        if 'part_serial' in row:
            row['part_serial'] = str(row['part_serial']).strip()
            validate_flexible_code(row['part_serial'], "part_serial")
        return super().before_import_row(row, **kwargs)

class ChapterNameResource(resources.ModelResource):
    class Meta:
        model = ChapterName
        fields = ('chapter_number', 'name', 'part')
        export_order = fields
        import_id_fields = ['chapter_number']

    def before_import_row(self, row, **kwargs):
        if 'chapter_number' in row:
            row['chapter_number'] = str(row['chapter_number']).strip()
            validate_flexible_code(row['chapter_number'], "chapter_number")
        return super().before_import_row(row, **kwargs)

class TopicNameResource(resources.ModelResource):
    class Meta:
        model = TopicName
        fields = ('topic_SI_number', 'name', 'chapter')
        export_order = fields
        import_id_fields = ['topic_SI_number']

    def before_import_row(self, row, **kwargs):
        if 'topic_SI_number' in row:
            row['topic_SI_number'] = str(row['topic_SI_number']).strip()
            validate_flexible_code(row['topic_SI_number'], "topic_SI_number")
        return super().before_import_row(row, **kwargs)

from import_export import resources, fields
from .models import SubTopicName, ExamName, EvergreenIndexName, MicroSubTopicName, HashtagsName

# ===============================
# ✅ SubTopicName Resource
# ===============================

class SubTopicNameResource(resources.ModelResource):
    exam_ids = fields.Field(column_name='exam_ids')
    hashtag_slugs = fields.Field(column_name='hashtag_slugs')

    class Meta:
        model = SubTopicName
        fields = (
            'sub_topic_SI_Number',
            'name',
            'sub_topic_short_Code',  # ✅ NEW FIELD
            'sub_topic_Code_Non_CTPL',
            'sub_topic_Code_CTPL',
            'topic',
            'exam_ids',
            'hashtag_slugs'
        )
        export_order = fields
        import_id_fields = ['sub_topic_SI_Number']
        skip_unchanged = True


    def before_import_row(self, row, **kwargs):
        row['sub_topic_SI_Number'] = str(row.get('sub_topic_SI_Number', '')).strip()
        return super().before_import_row(row, **kwargs)

    def before_save_instance(self, instance, row, **kwargs):
        instance._row_cache = row  # Save row for use later

    def after_save_instance(self, instance, row, **kwargs):
        row = getattr(instance, '_row_cache', None)
        if not row:
            return

        # ✅ Link Exams
        exam_ids_str = row.get('exam_ids')
        if exam_ids_str:
            exam_ids = [eid.strip() for eid in exam_ids_str.split(',') if eid.strip()]
            exams = ExamName.objects.filter(exam_SI_Number__in=exam_ids)
            instance.exams.set(exams)

        # ✅ Link Hashtags
        hashtag_slugs = row.get('hashtag_slugs')
        if hashtag_slugs:
            hashtag_keys = [h.strip() for h in hashtag_slugs.split(',') if h.strip()]
            hashtags = HashtagsName.objects.filter(hashtags_SI_Number__in=hashtag_keys)
            instance.hashtags.set(hashtags)

# ===============================
# ✅ MicroSubTopicName Resource
# ===============================

class MicroSubTopicNameResource(resources.ModelResource):
    class Meta:
        model = MicroSubTopicName
        fields = ('micro_sub_topic_SI_number', 'name', 'subtopics')
        export_order = fields
        import_id_fields = ['micro_sub_topic_SI_number']

    def before_import_row(self, row, **kwargs):
        if 'micro_sub_topic_SI_number' in row:
            row['micro_sub_topic_SI_number'] = str(row['micro_sub_topic_SI_number']).strip()
            validate_flexible_code(row['micro_sub_topic_SI_number'], "micro_sub_topic_SI_number")
        return super().before_import_row(row, **kwargs)

# ===============================
# ✅ ExamName Resource
# ===============================

class ExamNameResource(resources.ModelResource):
    class Meta:
        model = ExamName
        fields = ('exam_SI_Number', 'name', 'exam_code')
        export_order = fields
        import_id_fields = ['exam_SI_Number']

    def before_import_row(self, row, **kwargs):
        if 'exam_SI_Number' in row:
            row['exam_SI_Number'] = str(row['exam_SI_Number']).strip()
            validate_flexible_code(row['exam_SI_Number'], "exam_SI_Number")
        return super().before_import_row(row, **kwargs)

# ===============================
# ✅ EvergreenIndexName Resource
# ===============================

class EvergreenIndexNameResource(resources.ModelResource):
    class Meta:
        model = EvergreenIndexName
        fields = ('evergreen_index_SI_Number', 'name', 'evergreen_index_code')
        export_order = fields
        import_id_fields = ['evergreen_index_SI_Number']

    def before_import_row(self, row, **kwargs):
        if 'evergreen_index_SI_Number' in row:
            row['evergreen_index_SI_Number'] = str(row['evergreen_index_SI_Number']).strip()
            validate_flexible_code(row['evergreen_index_SI_Number'], "evergreen_index_SI_Number")
        return super().before_import_row(row, **kwargs)

# ===============================
# ✅ HashtagsName Resource
# ===============================

class HashtagsNameResource(resources.ModelResource):
    class Meta:
        model = HashtagsName
        fields = ('hashtags_SI_Number', 'name')
        export_order = fields
        import_id_fields = ['hashtags_SI_Number']

    def before_import_row(self, row, **kwargs):
        if 'hashtags_SI_Number' in row:
            row['hashtags_SI_Number'] = str(row['hashtags_SI_Number']).strip()
            validate_flexible_code(row['hashtags_SI_Number'], "hashtags_SI_Number")
        return super().before_import_row(row, **kwargs)

class GeneratedImageResource(resources.ModelResource):
    class Meta:
        model = GeneratedImage
        fields = ('id', 'prompt', 'image', 'created_at')
        export_order = fields

# ===================
# Custom Admin Forms
# ===================

class SectionAdminForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'

    def clean_area(self):
        area = self.cleaned_data.get('area')
        if not area:
            raise ValidationError("No Area selected in the form.")
        return area

# ======================
# Admin Model Registers
# ======================

@admin.register(Area)
class AreaAdmin(ImportExportModelAdmin):
    resource_class = AreaResource
    list_display = ('area_SI_Code', 'name', 'area_Short_Code', 'area_Colour_Hex', 'area_Serial', 'mppsc_para', 'upsc_para')
    search_fields = ('name', 'area_Short_Code', 'area_SI_Code')
    list_filter = ('mppsc_para', 'upsc_para')

@admin.register(Section)
class SectionAdmin(ImportExportModelAdmin):
    resource_class = SectionResource
    form = SectionAdminForm
    list_display = ('section_Unit_SI', 'name', 'area')
    search_fields = ('name', 'area__name')
    list_filter = ('area',)

@admin.register(PartName)
class PartNameAdmin(ImportExportModelAdmin):
    resource_class = PartNameResource
    list_display = ('part_serial', 'name', 'part_short_code', 'section')
    search_fields = ('name', 'part_short_code', 'section__name')
    list_filter = ('section',)

@admin.register(ChapterName)
class ChapterNameAdmin(ImportExportModelAdmin):
    resource_class = ChapterNameResource
    list_display = ('chapter_number', 'name', 'part')
    search_fields = ('name', 'part__name')
    list_filter = ('part',)

@admin.register(TopicName)
class TopicNameAdmin(ImportExportModelAdmin):
    resource_class = TopicNameResource
    list_display = ('topic_SI_number', 'name', 'chapter')
    search_fields = ('name', 'chapter__name')
    list_filter = ('chapter',)


from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import SubTopicName, ExamName, EvergreenIndexName, MicroSubTopicName, HashtagsName
# from .resources import (
#     SubTopicNameResource, ExamNameResource,
#     EvergreenIndexNameResource, MicroSubTopicNameResource, HashtagsNameResource
# )

# ===================
# ✅ Inlines for M2M
# ===================

class MicroSubTopicInline(admin.TabularInline):
    model = MicroSubTopicName
    extra = 1

class SubTopicExamsInline(admin.TabularInline):
    model = SubTopicName.exams.through
    extra = 1

class SubTopicEvergreenIndexInline(admin.TabularInline):
    model = SubTopicName.evergreenindex.through
    extra = 1

class SubTopicHashtagsInline(admin.TabularInline):
    model = SubTopicName.hashtags.through
    extra = 1

# =======================
# ✅ SubTopicName Admin
# =======================

@admin.register(SubTopicName)
class SubTopicNameAdmin(ImportExportModelAdmin):
    resource_class = SubTopicNameResource
    list_display = (
        'sub_topic_SI_Number',
        'name',
        'sub_topic_short_Code',  # ✅ NEW FIELD
        'sub_topic_Code_Non_CTPL',
        'sub_topic_Code_CTPL',
        'topic'
    )
    search_fields = (
        'name',
        'topic__name',
        'sub_topic_SI_Number',
        'sub_topic_short_Code'  # ✅ for search
    )
    list_filter = ('topic',)
    inlines = [
        MicroSubTopicInline,
        SubTopicExamsInline,
        SubTopicEvergreenIndexInline,
        SubTopicHashtagsInline
    ]
    filter_horizontal = ('exams', 'evergreenindex', 'hashtags')


# ============================
# ✅ MicroSubTopic Admin
# ============================

@admin.register(MicroSubTopicName)
class MicroSubTopicNameAdmin(ImportExportModelAdmin):
    resource_class = MicroSubTopicNameResource
    list_display = ('micro_sub_topic_SI_number', 'name', 'get_subtopic')

    def get_subtopic(self, obj):
        return obj.subtopics.name if obj.subtopics else "-"
    get_subtopic.short_description = 'SubTopic'

# ============================
# ✅ ExamName Admin
# ============================

@admin.register(ExamName)
class ExamNameAdmin(ImportExportModelAdmin):
    resource_class = ExamNameResource
    list_display = ('exam_SI_Number', 'name', 'exam_code', 'get_subtopics')
    inlines = [SubTopicExamsInline]

    def get_subtopics(self, obj):
        return ", ".join([s.name for s in obj.subtopics.all()])
    get_subtopics.short_description = 'SubTopics'

# ================================
# ✅ EvergreenIndexName Admin
# ================================

@admin.register(EvergreenIndexName)
class EvergreenIndexNameAdmin(ImportExportModelAdmin):
    resource_class = EvergreenIndexNameResource
    list_display = ('evergreen_index_SI_Number', 'name', 'evergreen_index_code', 'get_subtopics')
    inlines = [SubTopicEvergreenIndexInline]

    def get_subtopics(self, obj):
        return ", ".join([s.name for s in obj.subtopics.all()])
    get_subtopics.short_description = 'SubTopics'

# =======================
# ✅ HashtagsName Admin
# =======================

@admin.register(HashtagsName)
class HashtagsNameAdmin(ImportExportModelAdmin):
    resource_class = HashtagsNameResource
    list_display = ('hashtags_SI_Number', 'name', 'get_subtopics')
    inlines = [SubTopicHashtagsInline]

    def get_subtopics(self, obj):
        return ", ".join([s.name for s in obj.subtopics.all()])
    get_subtopics.short_description = 'SubTopics'

from django.contrib import admin
from .models import QuestionBank, KeywordName
from import_export.admin import ImportExportModelAdmin
from .admin_resources import QuestionBankResource



@admin.register(QuestionBank)
class QuestionBankAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = QuestionBankResource  # ✅ enable import/export

    # ---------------------------------------------------
    # 🔹 Display Columns
    # ---------------------------------------------------
    list_display = (
        'question_id', 'base_question_id', 'language', 'created_at', 'created_by',
        'question_number', 'get_question', 'get_areas', 'get_exams', 'exam_year',
        'type_of_question', 'question_sub_type', 'marks', 'current_relevance',
        'key_words_en', 'key_words_hi', 'get_ai_subtopic'
    )

    search_fields = (
        'question_id', 'base_question_id', 'question_number',
        'area_name__name', 'part_name__name', 'chapter_name__name',
        'topic_name__name', 'subtopic_name__name', 'exam_name__name',
        'question_part_first', 'question_part_first_hi',
        'correct_answer_choice', 'current_relevance_topic',
        'stmt_line_row1', 'stmt_line_row2', 'stmt_line_row3',
        'stmt_line_row4', 'stmt_line_row5', 'stmt_line_row6',
        'stmt_line_row7', 'stmt_line_row8', 'stmt_line_row9',
        'stmt_line_row1_hi', 'stmt_line_row2_hi', 'stmt_line_row3_hi',
        'stmt_line_row4_hi', 'stmt_line_row5_hi', 'stmt_line_row6_hi',
        'stmt_line_row7_hi', 'stmt_line_row8_hi', 'stmt_line_row9_hi',
        'key_words', 'key_words_en', 'key_words_hi'
    )

    list_filter = (
        'exam_year', 'type_of_question', 'question_sub_type', 'degree_of_difficulty',
        'current_relevance', 'language', 'area_name', 'part_name', 'chapter_name',
        'topic_name', 'subtopic_name', 'exam_name', 'ai_matched_subtopic'
    )

    readonly_fields = ('question_id', 'base_question_id', 'question_number')
    date_hierarchy = 'created_at'
    ordering = ('question_number', 'language')
    filter_horizontal = (
        'area_name', 'section_name', 'part_name',
        'chapter_name', 'topic_name', 'subtopic_name', 'exam_name', 'evergreenindex_name'
    )

    # ---------------------------------------------------
    # 🔹 Fieldsets (Organized Admin Form Sections)
    # ---------------------------------------------------
    fieldsets = (
        ("Identification", {
            'fields': ('question_id', 'base_question_id', 'question_number',
                       'type_of_question', 'language', 'question_sub_type')
        }),
        ("Classification", {
            'fields': ('exam_stage', 'exam_year', 'degree_of_difficulty',
                       'marks', 'negative_marks', 'elim_tactics_degree',
                       'current_relevance', 'current_relevance_topic')
        }),
        ("English Content", {
            'fields': ('question_part', 'assertion', 'reason',
                       'question_part_first', 'question_part_third',
                       'answer_option_a', 'answer_option_b',
                       'answer_option_c', 'answer_option_d',
                       'correct_answer_choice', 'correct_answer_description')
        }),
        ("Hindi Content", {
            'fields': ('question_part_hi', 'assertion_hi', 'reason_hi',
                       'question_part_first_hi', 'question_part_third_hi',
                       'answer_option_a_hi', 'answer_option_b_hi',
                       'answer_option_c_hi', 'answer_option_d_hi',
                       'correct_answer_description_hi')
        }),
        ("Statement Lines (EN/HI)", {
            'classes': ('collapse',),
            'fields': (
                'stmt_line_row1','stmt_line_row2','stmt_line_row3','stmt_line_row4','stmt_line_row5',
                'stmt_line_row6','stmt_line_row7','stmt_line_row8','stmt_line_row9',
                'stmt_line_row1_hi','stmt_line_row2_hi','stmt_line_row3_hi','stmt_line_row4_hi','stmt_line_row5_hi',
                'stmt_line_row6_hi','stmt_line_row7_hi','stmt_line_row8_hi','stmt_line_row9_hi',
            )
        }),
        ("Matching Lists", {
            'fields': (
                'list_1_name','list_2_name',
                'list_1_row1','list_1_row2','list_1_row3','list_1_row4',
                'list_1_row5','list_1_row6','list_1_row7','list_1_row8',
                'list_2_row1','list_2_row2','list_2_row3','list_2_row4',
                'list_2_row5','list_2_row6','list_2_row7','list_2_row8','list_2_row9',
                'list_1_row1_hi','list_1_row2_hi','list_1_row3_hi','list_1_row4_hi',
                'list_1_row5_hi','list_1_row6_hi','list_1_row7_hi','list_1_row8_hi',
                'list_2_row1_hi','list_2_row2_hi','list_2_row3_hi','list_2_row4_hi',
                'list_2_row5_hi','list_2_row6_hi','list_2_row7_hi','list_2_row8_hi','list_2_row9_hi',
            )
        }),
        ("Table Data", {
            'fields': (
                'table_head_a','table_head_b','table_head_c','table_head_d',
                'table_head_a_hi','table_head_b_hi','table_head_c_hi','table_head_d_hi',
                'head_a_data1','head_a_data2','head_a_data3','head_a_data4',
                'head_b_data1','head_b_data2','head_b_data3','head_b_data4',
                'head_c_data1','head_c_data2','head_c_data3','head_c_data4',
                'head_d_data1','head_d_data2','head_d_data3','head_d_data4',
                'head_a_data1_hi','head_a_data2_hi','head_a_data3_hi','head_a_data4_hi',
                'head_b_data1_hi','head_b_data2_hi','head_b_data3_hi','head_b_data4_hi',
                'head_c_data1_hi','head_c_data2_hi','head_c_data3_hi','head_c_data4_hi',
                'head_d_data1_hi','head_d_data2_hi','head_d_data3_hi','head_d_data4_hi',
            )
        }),
        ("Tagging & Keywords", {
            'fields': (
                'area_name','section_name','part_name','chapter_name',
                'topic_name','subtopic_name','exam_name','evergreenindex_name',
                'key_words', 'key_words_en', 'key_words_hi', 'ai_matched_subtopic'
            )
        }),
        ("Additional Info", {'fields': ('image', 'script', 'created_by', 'created_at')}),
    )

    # ---------------------------------------------------
    # 🔹 Custom Display Helpers
    # ---------------------------------------------------
    def get_question(self, obj):
        return obj.question_part_first or getattr(obj, 'stmt_line_row1', None) or obj.question_part
    get_question.short_description = 'Question'

    def get_areas(self, obj):
        return ", ".join([a.name for a in obj.area_name.all()])
    get_areas.short_description = 'Areas'

    def get_exams(self, obj):
        return ", ".join([e.name for e in obj.exam_name.all()]) or "-"
    get_exams.short_description = 'Exams'

    def get_ai_subtopic(self, obj):
        """Show AI-matched subtopic with short code if available."""
        if obj.ai_matched_subtopic:
            return f"{obj.ai_matched_subtopic.name} ({obj.ai_matched_subtopic.sub_topic_short_Code})"
        return "-"
    get_ai_subtopic.short_description = "AI Subtopic"

from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import KeywordName, SubTopicName, MicroSubTopicName


# ============================================================
# 🔹 KeywordName Resource for Import–Export
# ============================================================
class KeywordNameResource(resources.ModelResource):
    """
    Handles full import/export with hierarchy.
    ✅ Supports multiple subtopics per keyword (via name or short code).
    ✅ Auto-fills created_at, links M2M safely.
    ✅ Compatible with all django-import-export versions.
    """

    subtopic = fields.Field(column_name="subtopic")
    subtopic_code = fields.Field(column_name="subtopic short code")
    area = fields.Field(column_name="area")
    section = fields.Field(column_name="section")
    part = fields.Field(column_name="part")
    chapter = fields.Field(column_name="chapter")
    topic = fields.Field(column_name="topic")

    current_row_data = {}

    # ---------------------------------------------------
    # 🔹 Auto-fill created_at if missing
    # ---------------------------------------------------
    def before_import_row(self, row, **kwargs):
        if not row.get("created_at") or str(row.get("created_at")).strip() == "":
            row["created_at"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_row_data = dict(row)

    # ---------------------------------------------------
    # 🔹 Handle duplicates (case-insensitive)
    # ---------------------------------------------------
    def get_instance(self, instance_loader, row):
        """
        Handles duplicates (case-insensitive) safely across import-export versions.
        Avoids NoneType errors when _meta.model is not bound yet.
        """
        name = (row.get("name") or "").strip()
        lang = (row.get("language") or "EN").strip()
        if not name:
            return None

        Model = getattr(self._meta, "model", None)
        if Model is None:
            from .models import KeywordName
            Model = KeywordName

        try:
            return Model.objects.get(name__iexact=name, language__iexact=lang)
        except Model.MultipleObjectsReturned:
            return Model.objects.filter(name__iexact=name, language__iexact=lang).first()
        except Model.DoesNotExist:
            return None
        except Exception as e:
            print(f"⚠️ get_instance error for {name}: {e}")
            return None

    # ---------------------------------------------------
    # 🔹 Universal after_save_instance (cross-version)
    # ---------------------------------------------------
    def after_save_instance(self, *args, **kwargs):
        """
        Works across import-export versions and auto-matches subtopics
        by numeric short code or by name. Supports safe normalization.
        """
        import re
        from .models import SubTopicName

        instance = None
        row = None
        dry_run = kwargs.get("dry_run", False)

        # Safely extract instance and row depending on import_export version
        if len(args) >= 2:
            instance = args[1]
        if len(args) >= 5 and isinstance(args[4], dict):
            row = args[4]
        elif len(args) >= 3 and isinstance(args[2], dict):
            row = args[2]
        elif "row" in kwargs:
            row = kwargs["row"]

        if dry_run or not instance or not row:
            return

        raw_codes = (row.get("subtopic short code") or "").strip()
        raw_names = (row.get("subtopic") or "").strip()

        code_list = [c.strip() for c in re.split(r"[;,\\n]", raw_codes) if c.strip()]
        name_list = [n.strip() for n in re.split(r"[;,\\n]", raw_names) if n.strip()]

        linked_any = False

        # ------------------------------------------------------------
        # 🔹 Normalization helpers
        # ------------------------------------------------------------
        def normalize_code(code: str):
            """Extracts numeric part from mixed code like 'HIS_001' → '1'"""
            import re
            if not code:
                return ""
            digits = re.findall(r"\d+", str(code))
            return digits[0] if digits else str(code).strip().lower()

        def normalize_text(val: str):
            """Clean and lowercase text."""
            import re
            return re.sub(r"[^a-zA-Z0-9]", "", (val or "").strip().lower())

        # ------------------------------------------------------------
        # 🔹 Preload all subtopics once
        # ------------------------------------------------------------
        subtopic_objects = list(SubTopicName.objects.all())

        # ------------------------------------------------------------
        # 🔹 Match by numeric short code
        # ------------------------------------------------------------
        for code in code_list:
            norm_code = normalize_code(code)
            match_obj = None
            for st_obj in subtopic_objects:
                st_code = str(st_obj.sub_topic_short_Code or "").strip().lower()
                if st_code == norm_code or normalize_code(st_code) == norm_code:
                    match_obj = st_obj
                    break

            if match_obj:
                instance.subtopics.add(match_obj)
                linked_any = True
                print(f"✅ Linked by code: {code} → {match_obj.sub_topic_short_Code}")
            else:
                print(f"⚠️ No DB match for code: '{code}' → normalized '{norm_code}'")

        # ------------------------------------------------------------
        # 🔹 Match by name if not already linked
        # ------------------------------------------------------------
        for name in name_list:
            norm_name = normalize_text(name)
            match_obj = None
            for st_obj in subtopic_objects:
                if normalize_text(st_obj.name) == norm_name:
                    match_obj = st_obj
                    break

            if match_obj:
                instance.subtopics.add(match_obj)
                linked_any = True
                print(f"✅ Linked by name: {name} → {match_obj.name}")
            else:
                print(f"⚠️ No DB match for name: '{name}'")

        # ------------------------------------------------------------
        # 🔹 Save keyword only if linked
        # ------------------------------------------------------------
        if linked_any:
            instance.save(update_fields=[])
            print(f"💾 Saved Keyword: {instance.name} → {instance.subtopics.count()} linked subtopics.")
        else:
            print(f"⚠️ No subtopics linked for: {instance.name}")

    # ---------------------------------------------------
    # 🔹 Export Formatting (Readable Hierarchy)
    # ---------------------------------------------------
    def dehydrate_subtopic(self, obj):
        return ", ".join(sorted({s.name for s in obj.subtopics.all()})) or ""

    def dehydrate_subtopic_code(self, obj):
        return ", ".join(sorted({
            s.sub_topic_short_Code for s in obj.subtopics.all() if s.sub_topic_short_Code
        })) or ""

    def dehydrate_area(self, obj):
        return ", ".join(sorted({
            s.topic.chapter.part.section.area.name
            for s in obj.subtopics.all() if s.topic and s.topic.chapter
        })) or ""

    def dehydrate_section(self, obj):
        return ", ".join(sorted({
            s.topic.chapter.part.section.name
            for s in obj.subtopics.all() if s.topic and s.topic.chapter
        })) or ""

    def dehydrate_part(self, obj):
        return ", ".join(sorted({
            s.topic.chapter.part.name
            for s in obj.subtopics.all() if s.topic and s.topic.chapter
        })) or ""

    def dehydrate_chapter(self, obj):
        return ", ".join(sorted({
            s.topic.chapter.name
            for s in obj.subtopics.all() if s.topic
        })) or ""

    def dehydrate_topic(self, obj):
        return ", ".join(sorted({
            s.topic.name
            for s in obj.subtopics.all() if s.topic
        })) or ""

    # ---------------------------------------------------
    # 🔹 Meta Configuration
    # ---------------------------------------------------
    class Meta:
        model = KeywordName

        # Use name + language as unique identifiers
        import_id_fields = ["name", "language"]

        # Import/export behavior
        skip_unchanged = True
        report_skipped = True
        use_bulk = False
        use_transactions = True
        raise_errors = False

        # Match Excel headers
        fields = (
            "name",             # Keyword text
            "language",         # EN / HI
            "source",           # manual / ai / merged
            "relevance_score",  # importance weight
            "area",
            "section",
            "part",
            "chapter",
            "topic",
            "subtopic",         # readable names (comma-separated)
            "subtopic_code",    # subtopic short code(s)
            "created_at",       # auto-filled if blank
        )

        # Export order
        export_order = fields



# ============================================================
# 🔹 Merge Duplicate Keywords
# ============================================================
@admin.action(description="🧹 Merge Duplicate Keywords (case-insensitive)")
def merge_duplicate_keywords(modeladmin, request, queryset):
    merged_count = 0
    with transaction.atomic():
        duplicates = {}
        for row in KeywordName.objects.values("name", "language"):
            key = (row["name"].strip().lower(), row["language"].strip().lower())
            duplicates.setdefault(key, []).append(row)

        for key, rows in duplicates.items():
            if len(rows) > 1:
                same_set = KeywordName.objects.filter(
                    name__iexact=key[0], language__iexact=key[1]
                )
                keep = same_set.first()
                for dup in same_set.exclude(pk=keep.pk):
                    keep.subtopics.add(*dup.subtopics.all())
                    keep.micro_subtopics.add(*dup.micro_subtopics.all())
                    dup.delete()
                merged_count += 1

    msg = f"✅ Merged {merged_count} duplicate keyword groups successfully!" if merged_count else "🎉 No duplicates found!"
    messages.success(request, msg)


# ============================================================
# 🔹 Admin Configuration
# ============================================================
@admin.register(KeywordName)
class KeywordNameAdmin(ImportExportModelAdmin):
    """
    Keyword management with hierarchy view, import/export, and merge action.
    """
    resource_class = KeywordNameResource

    list_display = (
        "name",
        "language",
        "source",
        "relevance_score",
        "get_areas",
        "get_linked_subtopics",
        "created_at",
    )
    search_fields = (
        "name",
        "subtopics__name",
        "subtopics__sub_topic_short_Code",
        "subtopics__topic__chapter__part__section__area__name",
    )
    list_filter = ("language", "source")
    filter_horizontal = ("subtopics",)
    readonly_fields = ("created_at",)
    list_per_page = 50
    ordering = ("name",)

    fieldsets = (
        ("Keyword Info", {"fields": ("name", "language", "source", "relevance_score")}),
        ("Linkages", {"fields": ("subtopics",)}),
        ("Timestamps", {"fields": ("created_at",)}),
    )

    def get_areas(self, obj):
        try:
            return ", ".join(sorted({
                s.topic.chapter.part.section.area.name
                for s in obj.subtopics.all()
                if s.topic
            })) or "-"
        except Exception:
            return "-"
    get_areas.short_description = "Areas"

    def get_linked_subtopics(self, obj):
        subs = [f"{s.name} ({s.sub_topic_short_Code})" for s in obj.subtopics.all()]
        return ", ".join(subs) if subs else "-"
    get_linked_subtopics.short_description = "Linked Subtopics"

    actions = [merge_duplicate_keywords]


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(BatchGeneratedQuestion)
class BatchGeneratedQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'question', 'generated_at')
    search_fields = ('batch__name', 'question__question_number')
    list_filter = ('batch', 'generated_at')

@admin.register(GeneratedImage)
class GeneratedImageAdmin(ImportExportModelAdmin):
    resource_class = GeneratedImageResource
    list_display = ('id', 'prompt', 'image_preview', 'created_at')
    readonly_fields = ('image_preview', 'created_at')
    search_fields = ('prompt',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" style="object-fit:cover;border:1px solid #ccc;">'
        return "No Image"

    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

# ================
# Simple Registers
# ================

# admin.site.register(InputSuggestion)
admin.site.register(InputSuggestionImage)
admin.site.register(InputSuggestionDocument)
admin.site.register(QuoteIdiomPhrase)


from django.utils.html import format_html

class InputSuggestionImageInline(admin.TabularInline):
    model = InputSuggestionImage
    extra = 1

class InputSuggestionDocumentInline(admin.TabularInline):
    model = InputSuggestionDocument
    extra = 1

@admin.register(InputSuggestion)
class InputSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'brief_description',
        'language',
        'created_by',
        'created_at',
        'get_areas',
        'get_parts',
        'get_exams',
        'source',
        'approval_status_badge',
    )
    search_fields = (
        'brief_description',
        'details',
        'created_by__email',
        'area_name__name',
        'part_name__name',
        'exams__name',
    )
    list_filter = (
        'approval_status',
        'source',
        'created_at',
        'area_name',
        'part_name',
        'exams',
    )
    inlines = [InputSuggestionImageInline, InputSuggestionDocumentInline]
    filter_horizontal = ('area_name', 'part_name', 'chapter_name', 'topic_name', 'subtopic_name', 'exams')

    readonly_fields = ('created_at', 'created_by')

    def get_areas(self, obj):
        return ", ".join([a.name for a in obj.area_name.all()])
    get_areas.short_description = "Areas"

    def get_parts(self, obj):
        return ", ".join([p.name for p in obj.part_name.all()])
    get_parts.short_description = "Parts"

    def get_exams(self, obj):
        return ", ".join([e.name for e in obj.exams.all()])
    get_exams.short_description = "Exams"

    def approval_status_badge(self, obj):
        if obj.approval_status == 'approved':
            color = 'green'
        else:
            color = 'red'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.approval_status_display())
    approval_status_badge.short_description = "Approval Status"


@admin.register(LectureNote)
class LectureNoteAdmin(admin.ModelAdmin):
    list_display = [
        'chapter',
        'language',
        'ctpl',          # ✅ added CTPL field
        'area',
        'part',
        'subtopic',
        'topic',
        'note_type',
        'created_at'
    ]
    list_filter = ['language', 'ctpl', 'area', 'part', 'note_type']  # ✅ added ctpl in filters
    search_fields = ['description']


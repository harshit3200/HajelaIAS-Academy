# question_bank/admin_resources.py
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, IntegerWidget, FloatWidget
from .models import (
    QuestionBank, Area, Section, PartName, ChapterName,
    TopicName, SubTopicName, ExamName, EvergreenIndexName
)

SEPARATOR = "|"  # safer than comma for text fields

class QuestionBankResource(resources.ModelResource):
    # ----- Extra “code” columns for M2M (import/export as pipe-separated codes) -----
    area_codes = fields.Field(
        column_name="area_codes",
        attribute="area_name",
        widget=ManyToManyWidget(Area, field="area_SI_Code", separator=SEPARATOR),
    )
    section_codes = fields.Field(
        column_name="section_codes",
        attribute="section_name",
        widget=ManyToManyWidget(Section, field="section_Unit_SI", separator=SEPARATOR),
    )
    part_codes = fields.Field(
        column_name="part_codes",
        attribute="part_name",
        widget=ManyToManyWidget(PartName, field="part_serial", separator=SEPARATOR),
    )
    chapter_codes = fields.Field(
        column_name="chapter_codes",
        attribute="chapter_name",
        widget=ManyToManyWidget(ChapterName, field="chapter_number", separator=SEPARATOR),
    )
    topic_codes = fields.Field(
        column_name="topic_codes",
        attribute="topic_name",
        widget=ManyToManyWidget(TopicName, field="topic_SI_number", separator=SEPARATOR),
    )
    subtopic_codes = fields.Field(
        column_name="subtopic_codes",
        attribute="subtopic_name",
        widget=ManyToManyWidget(SubTopicName, field="sub_topic_SI_Number", separator=SEPARATOR),
    )
    exam_codes = fields.Field(
        column_name="exam_codes",
        attribute="exam_name",
        widget=ManyToManyWidget(ExamName, field="exam_SI_Number", separator=SEPARATOR),
    )
    evergreenindex_codes = fields.Field(
        column_name="evergreenindex_codes",
        attribute="evergreenindex_name",
        widget=ManyToManyWidget(EvergreenIndexName, field="id", separator=SEPARATOR),
    )

    # Read-only helpers in export
    created_by_email = fields.Field(column_name="created_by_email")
    def dehydrate_created_by_email(self, obj):
        return getattr(getattr(obj, "created_by", None), "email", "") or ""

    class Meta:
        model = QuestionBank
        # Identify rows (update vs create) by base_question_id + language pair
        import_id_fields = ("base_question_id", "language")
        # Skip large/binary or system-maintained fields on import
        exclude = ("image", "created_at", "created_by", "question_id", "question_number")
        skip_unchanged = True
        report_skipped = True
        use_transactions = True

    def before_import_row(self, row, **kwargs):
        """
        Normalize blanks to None/empty; let model .save() auto-assign ids if missing.
        """
        # base_question_id: if blank -> None; model will assign random unique
        bqid = str(row.get("base_question_id", "")).strip()
        row["base_question_id"] = int(bqid) if bqid.isdigit() else None

        # Optional numeric coercions (safe):
        for k in ("exam_year", "marks", "negative_marks"):
            v = row.get(k, "")
            if k in ("marks", "negative_marks"):
                try:
                    row[k] = float(v) if str(v).strip() not in ("", "None", "nan") else 0.0
                except Exception:
                    row[k] = 0.0
            else:
                try:
                    row[k] = int(v) if str(v).strip() not in ("", "None", "nan") else None
                except Exception:
                    row[k] = None

        # Allow empty degree/current relevance fields
        for k in ("degree_of_difficulty", "elim_tactics_degree", "current_relevance"):
            if str(row.get(k, "")).strip() in ("None", "nan"):
                row[k] = ""

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Attach creator if not set, using importing request (available in context).
        """
        request = (self.context or {}).get("request")
        if request and not instance.created_by_id:
            instance.created_by = request.user

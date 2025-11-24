import random
import logging
from .models import QuestionBank

logger = logging.getLogger(__name__)

def sanitize_text(text):
    """Clean smart quotes and normalize input."""
    if text:
        return (
            text.replace("“", '"')
                .replace("”", '"')
                .replace("‘", "'")
                .replace("’", "'")
                .replace("–", "-")
                .replace("—", "-")
                .replace("\u200c", "")  # Zero-width non-joiner
                .strip()
        )
    return text

def save_bilingual_question_pair(
    question_number,
    en_data,
    hi_data,
    question_sub_type='simple_type',
    type_of_question='moq',
    created_by=None,
    marks=2.0,
    current_relevance=1,
    exam_year=None,
    area_objs=None,
    section_objs=None,
    part_objs=None,
    chapter_objs=None,
    topic_objs=None,
    subtopic_objs=None
):
    try:
        # ✅ Generate unique base_question_id
        while True:
            base_id = random.randint(100000, 999999)
            if not QuestionBank.objects.filter(base_question_id=base_id).exists():
                break

        print(f"Generated base_id: {base_id} for question_number: {question_number}")

        # ✅ English Question
        en_q = QuestionBank(
            question_number=question_number,
            base_question_id=base_id,
            question_sub_type=question_sub_type,
            type_of_question=type_of_question,
            language='e',
            marks=marks,
            current_relevance=current_relevance,
            exam_year=exam_year,
            created_by=created_by,
        )

        for k, v in en_data.items():
            if hasattr(en_q, k):
                setattr(en_q, k, sanitize_text(v))

        en_q.save()

        if area_objs: en_q.area_name.set(area_objs)
        if section_objs: en_q.section_name.set(section_objs)
        if part_objs: en_q.part_name.set(part_objs)
        if chapter_objs: en_q.chapter_name.set(chapter_objs)
        if topic_objs: en_q.topic_name.set(topic_objs)
        if subtopic_objs: en_q.subtopic_name.set(subtopic_objs)

        print(f"✅ English Question Saved: {en_q.question_id}")

        # ✅ Hindi Question
        hi_q = None
        if hi_data:
            hi_q = QuestionBank(
                question_number=question_number,
                base_question_id=base_id,
                question_sub_type=question_sub_type,
                type_of_question=type_of_question,
                language='h',
                marks=marks,
                current_relevance=current_relevance,
                exam_year=exam_year,
                created_by=created_by,
            )

            for k, v in hi_data.items():
                if hasattr(hi_q, k):
                    setattr(hi_q, k, sanitize_text(v))

            hi_q.save()

            if area_objs: hi_q.area_name.set(area_objs)
            if section_objs: hi_q.section_name.set(section_objs)
            if part_objs: hi_q.part_name.set(part_objs)
            if chapter_objs: hi_q.chapter_name.set(chapter_objs)
            if topic_objs: hi_q.topic_name.set(topic_objs)
            if subtopic_objs: hi_q.subtopic_name.set(subtopic_objs)

            print(f"✅ Hindi Question Saved: {hi_q.question_id}")

        logger.info(f"✅ Saved EN: {en_q.question_id} and HI: {hi_q.question_id if hi_q else 'None'}")
        return en_q, hi_q

    except Exception as e:
        logger.error(f"⚠️ Error saving bilingual question pair: {e}", exc_info=True)
        print(f"❌ Exception during save: {e}")
        return None, None



def parse_and_save_ai_questions(response_text, created_by, starting_qn_number=101, question_sub_type='simple_type', type_of_question='moq', exam_year=None, area_objs=None):
    blocks = [b.strip() for b in response_text.split('---') if b.strip()]
    grouped_blocks = [(blocks[i], blocks[i + 1]) for i in range(0, len(blocks), 2)]

    saved = []

    for idx, (en_block, hi_block) in enumerate(grouped_blocks):
        en_data = extract_fields_from_block(en_block, lang='en')
        hi_data = extract_fields_from_block(hi_block, lang='hi')
        question_number = f"Q{starting_qn_number + idx}"

        en_q, hi_q = save_bilingual_question_pair(
            question_number=question_number,
            en_data=en_data,
            hi_data=hi_data,
            question_sub_type=question_sub_type,
            type_of_question=type_of_question,
            created_by=created_by,
            exam_year=exam_year,
            area_objs=area_objs
        )
        saved.append((en_q, hi_q))

    return saved

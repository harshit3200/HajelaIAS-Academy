from modeltranslation.translator import register, TranslationOptions
from .models import Area, Section, PartName, ChapterName, TopicName, SubTopicName

@register(Area)
class AreaTranslationOptions(TranslationOptions):
    fields = ('name',)  # 'name' and 'name_hi' will be handled automatically


@register(Section)
class SectionTranslationOptions(TranslationOptions):
    fields = ('name',)  # Only 'name' is needed, do not add 'name_hi'

@register(PartName)
class PartNameTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(ChapterName)
class ChapterNameTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(TopicName)
class TopicNameTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(SubTopicName)
class SubTopicNameTranslationOptions(TranslationOptions):
    fields = ('name',)

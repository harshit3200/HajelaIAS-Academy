from django.urls import path
from . import views


urlpatterns = [
    # --------------------------------------
    # 🔹 File upload and question generation
    # --------------------------------------
    path('upload-file/', views.upload_file, name='upload-file'),
    path('generate-questions-document/', views.generate_questions_document, name='generate-questions-document'),
    path('generate-questions/', views.generate_questions, name='generate_questions'),
    path('generate-classplus-doc/', views.generate_classplus_doc_view, name='generate_classplus_doc'),

    # --------------------------------------
    # 🔹 Add Questions
    # --------------------------------------
    path('add/simple/question/', views.add_simple_type_question, name='add-simple-type-question'),
    path('add/r-and-a/question/', views.add_r_and_a_type_question, name='add-r-and-a-type-question'),
    path('add/list-1/question/', views.add_list_type_1_question, name='add-list-type-1-question'),
    path('add/list-2/question/', views.add_list_type_2_question, name='add-list-type-2-question'),
    path('add/true-and-false/question/', views.add_true_and_false_type_question, name='add-true-and-false-type-question'),
    path('add/fill-in-the-blank/question/', views.add_fill_in_the_blank_question, name='add-fill-in-the-blank-question'),
    path('add/statement/question/', views.add_statement_type_question, name='add-statement-type-question'),  # ✅ NEW

    # --------------------------------------
    # 🔹 Edit Questions
    # --------------------------------------
    path('edit/simple/question/<int:pk>/', views.edit_simple_type_question, name='edit-simple-type-question'),
    path('edit/r-and-a/question/<int:pk>/', views.edit_r_and_a_type_question, name='edit-r-and-a-type-question'),
    path('edit/list-1/question/<int:pk>/', views.edit_list_type_1_question, name='edit-list-type-1-question'),
    path('edit/list-2/question/<int:pk>/', views.edit_list_type_2_question, name='edit-list-type-2-question'),
    path('edit/true-and-false/question/<int:pk>/', views.edit_true_and_false_type_question, name='edit-true-and-false-type-question'),
    path('edit/fill-in-the-blank/question/<int:pk>/', views.edit_fill_in_the_blank_question, name='edit-fill-in-the-blank-question'),
    path('edit/statement/question/<int:pk>/', views.edit_statement_type_question, name='edit-statement-type-question'),

    # --------------------------------------
    # 🔹 Delete Questions
    # --------------------------------------
    path('delete/simple/question/<int:pk>/', views.delete_simple_type_question, name='delete-simple-type-question'),
    path('delete/r-and-a/question/<int:pk>/', views.delete_r_and_a_type_question, name='delete-r-and-a-type-question'),
    path('delete/list-1/question/<int:pk>/', views.delete_list_type_1_question, name='delete-list-type-1-question'),
    path('delete/list-2/question/<int:pk>/', views.delete_list_type_2_question, name='delete-list-type-2-question'),
    path('delete/true-and-false/question/<int:pk>/', views.delete_true_and_false_type_question, name='delete-true-and-false-type-question'),
    path('delete/fill-in-the-blank/question/<int:pk>/', views.delete_fill_in_the_blank_question, name='delete-fill-in-the-blank-question'),

    # --------------------------------------
    # 🔹 Input Suggestions
    # --------------------------------------
    path('add-input-suggestion/', views.add_input_suggestion, name='add-input-suggestion'),
    path('input-suggestion-list/', views.view_input_suggestion, name='input-suggestion-list'),
    path('view-input-suggestion/<int:question_id>/', views.question_blog_view, name='view-input-suggestion'),
    
    # --------------------------------------
    # 🔹 AI Hashtags Generator
    # --------------------------------------
    path('generate-ai-hashtags/', views.generate_ai_hashtags, name='generate_ai_hashtags'),
    path('save-ai-hashtags/', views.save_ai_hashtags, name='save-ai-hashtags'),

    # --------------------------------------
    # 🔹 Dynamic dropdown data fetch views
    # --------------------------------------
    path('get-areas/', views.get_areas, name='get_areas'),
    path('get-sections-list/', views.get_sections_list, name='get_sections_list'),
    path('get-parts-list/', views.get_parts_list, name='get_parts_list'),
    path('get-parts-by-area/', views.get_parts_by_area, name='get_parts_by_area'),
    path('get-chapters-list/', views.get_chapters_list, name='get_chapters_list'),
    path('get-topics-list/', views.get_topics_list, name='get_topics_list'),
    path('get-subtopics-list/', views.get_subtopics_list, name='get_subtopics_list'),
    path('get-exams-list/', views.get_exams_list, name='get_exams_list'),
    path('get-hashtags-list/', views.get_hashtags_list, name='get_hashtags_list'),
    path('hashtags/<slug:slug>/', views.hashtag_detail, name='hashtag_detail'),
    path('get-hierarchy-from-shortcode/', views.get_hierarchy_from_shortcode, name='get_hierarchy_from_shortcode'),

    # --------------------------------------
    # 🔹 Question viewing and filtering
    # --------------------------------------
    path('view-questions/', views.view_questions, name='view_questions'),
    path('filter-questions/', views.question_filter_view, name='question_filter_view'),

    # --------------------------------------
    # 🔹 Quotes, idioms, and phrases
    # --------------------------------------
    path('add-quote-idiom-phrase/', views.add_quote_idiom_phrase, name='add_quote_idiom_phrase'),
    path('quotes-idioms-phrases/', views.quotes_idioms_phrases_view, name='quotes_idioms_phrases'),

    # --------------------------------------
    # 🔹 Dashboards
    # --------------------------------------
    path('dashboard/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('new-dashboard/', views.new_dashboard_view, name='new_dashboard_view'),

    # --------------------------------------
    # 🔹 Report generation
    # --------------------------------------
    path('generate_this_week_csv/', views.generate_this_week_csv, name='generate_this_week_csv'),
    path('generate_earlier_week_csv/', views.generate_earlier_week_csv, name='generate_earlier_week_csv'),

    # --------------------------------------
    # 🔹 AI Question Generation and Saving
    # --------------------------------------
    path('generate-alternate-question/', views.generate_alternate_question, name='generate_alternate_question'),
    path('generate-pyq-keywords/', views.generate_pyq_keywords, name='generate_pyq_keywords'),
    path('save-alternate-question/', views.save_alternate_question, name='save_alternate_question'),
    path('view_ai_generated_questions/', views.view_ai_generated_questions, name='view_ai_generated_questions'),

    # --------------------------------------
    # 🔹 Batch Test Generation
    # --------------------------------------
    path('generate-test/', views.generate_test_form, name='generate_test_form'),
    path('generate-test-file/', views.generate_test, name='generate_test'),

    # --------------------------------------
    # 🔹 Image Generation Chat System
    # --------------------------------------
    path('generate-image/', views.generate_image_view, name='generate_image'),
    path('clear-image-chat/', views.clear_image_chat, name='clear_image_chat'),
    path('new-image-chat/', views.new_image_chat, name='new_image_chat'),
    path('hierarchy/', views.hierarchy_view, name='hierarchy'),

    # --------------------------------------
    # 🔹 UPSC Notes Generator
    # --------------------------------------
    path('generate-upsc-notes/', views.generate_notes, name='generate_upsc_notes'),

    # --------------------------------------
    # 🔹 Lecture Notes
    # --------------------------------------
    path('upload-lecture-note/', views.upload_lecture_note_view, name='upload_lecture_note'),
    path("lecture-notes/", views.list_lecture_notes, name="list_lecture_notes"),
    path("lecture-note/<int:pk>/", views.view_lecture_note_detail, name="view_lecture_note_detail"),

    # --------------------------------------
    # 🔹 Database and Content Hierarchy
    # --------------------------------------
    path("database/", views.database, name="database"),
    path("content/", views.content_by_subtopic, name="content_by_subtopic"),

    # --------------------------------------
    # 🔹 SubTopic Keyword Generator (NEW FEATURE)
    # --------------------------------------
    path('subtopics/', views.subtopic_list_view, name='subtopic_list'),
    path('subtopics/<path:subtopic_id>/generate_keywords/', views.generate_keywords_view, name='generate_keywords'),
    path("update-question-keywords/", views.update_question_keywords, name="update_question_keywords"),

    # 🧭 New refinement + selection endpoints
    path("api/refine_subtopics_by_scope/", views.refine_subtopics_by_scope, name="refine_subtopics_by_scope"),
    path("api/get_scope_list/", views.get_scope_list, name="get_scope_list"),
    path("update-question-subtopics/", views.update_question_subtopics, name="update_question_subtopics"),  # ✅ fixed path
    
    
    # path('fetch-tagged-subtopics/<int:question_id>/', views.fetch_tagged_subtopics, name='fetch_tagged_subtopics'),


]

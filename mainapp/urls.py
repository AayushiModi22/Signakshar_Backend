from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from mainapp import views
from django.urls import path,include
from . import views
from .myviews import user_views
from .myviews.user_views import LoginView, logoutview,Registerview,UserView,UserUpdateView,FetchUserDetailsView,CurrentUserView,CheckEmailView,googleLogIn,google_auth_callback,google_auth,login
from .myviews.otp_views import sendOtp,verifyOtp,forgetPassword
from .myviews import document_views
from .myviews.document_views import DocumentTableViewset,DocumentByDocId,DocAllRecipientById,GetDraggedDataByDocRec,EmailListAPIView,DocumentRecipientDetailAPIView,FetchRecipientFullDetails,trigger_delete_expired_documents
from .myviews.document_views import send_email,sequence_email_approval,get_doc
from .myviews.template_views import TemplateViewSet,TemplateDraggedDataViewset,GetDraggedDataByTempRec,deleteTemplate,TemplateRecipientViewset,UseTemplateRecipientViewSet,use_template_recipient_didTidCid,TemplateRecipientByTemplateId,TemplateByTemplateId,updateTemplateDraggedData
from .myviews.aws_views import upload_file_to_s3,upload_template_file_to_s3,fetch_pdf_from_s3,generate_presigned_url,delete_file_from_s3,fetch_templateFile_from_s3,delete_template_from_s3,fetch_and_convert_pdf_from_s3
from .myviews.dashboard_views import getRecipientCount,getPendingRecipientCount,getRecipientDetails,getStatus,deleteDocumentView,DocumentView2,CombinedDocumentView
from .myviews import bulkpdfsigning_views
# from .myviews.apilog_views import ApiLogViewset

urlpatterns = [
    # user
    path('register/', Registerview.as_view()),
    path('login/', LoginView.as_view(),name='login'),
    path('googleLogIn/',user_views.googleLogIn, name="googleLogIn"),
    path('logout/', logoutview.as_view(),name="logout"),
    path('user/', UserView.as_view()),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user-details/<int:user_id>/', FetchUserDetailsView.as_view(), name='fetch_user_details'),
    path('current-user/',CurrentUserView.as_view(),name='current-user'),
    path('checkEmail/', CheckEmailView.as_view(), name='check_email'),

    # otp
    path('sendOtp/',sendOtp,name="sendOtp"),
    path('verifyOtp/',verifyOtp,name="verifyOtp"),
    path('forgetPassword/',forgetPassword,name="forgetPassword"),
    
    # template
    path('templateapi/', TemplateViewSet.as_view({'get': 'list', 'post': 'create'}), name='template_api'),
    path('templateDraggedDataApi/', TemplateDraggedDataViewset.as_view({'get': 'list', 'post': 'create'}), name='draggeddata_api'),
    path('templateDraggedDataApi/<int:pk>/', TemplateDraggedDataViewset.as_view({'delete': 'destroy'}), name='draggeddata_delete_api'),
    path('getDraggedDataByTempRec/<int:template_rec_id>/', GetDraggedDataByTempRec.as_view(), name='get_dragged_data_by_temp_rec'),
    path('deleteTemplate/',deleteTemplate.as_view()),
    path('TemplateRecipient/', TemplateRecipientViewset.as_view({'get': 'list', 'post': 'create'}), name='tempRec_api'),
    path('useTemplateRecipientApi/', UseTemplateRecipientViewSet.as_view({'get': 'list', 'post': 'create'}), name='usetempRec_api'),
    path('use_template_recipient_didTidCid/<int:document_id>/<int:template_id>/<int:creator_id>/', use_template_recipient_didTidCid),
    path('TemplateRecipientByTemplateId/<int:template_id>/', TemplateRecipientByTemplateId.as_view(), name='template_by_template_id'),
    path('TemplateByTemplateId/<int:template_id>/', TemplateByTemplateId.as_view(), name='template_rec_by_template_id'),
    path('updateTemplateDraggedData/<int:pk>/', updateTemplateDraggedData),
    
    # document (all)
    path('DocumentTableapi/', DocumentTableViewset.as_view({'get': 'list', 'post': 'create'}), name='docTable_api'),
    path('DocumentByDocId/<int:doc_id>/', DocumentByDocId.as_view(), name='doc_by_doc_id'),
    path("save_doc/",document_views.save_doc),
    path("get_doc/",document_views.get_doc),
    path("save_doc_positions/",document_views.save_recipient_position_data),
    path('DocAllRecipientById/<int:Doc_id>/', DocAllRecipientById.as_view(), name='DocAllRecipientById'),
    path('DocApprove/', document_views.sequence_email_approval, name='DocApprove'),
    path('GetDraggedDataByDocRec/<int:docId>/<int:docRecipientdetails_id>', GetDraggedDataByDocRec.as_view(), name='GetDraggedDataByDocRec'),
    path('email-list/<int:docId>/<str:recEmail>/', EmailListAPIView.as_view(),name='email-list-api'),
    path('document-recipient-detail/<int:docId>/<str:recEmail>/', DocumentRecipientDetailAPIView.as_view(), name='document-recipient-detail-api'),
    path('recipient-details/<int:recipient_id>/', FetchRecipientFullDetails.as_view(), name='fetch-recipient-full-details'),
    path('trigger_delete_expired_documents/', trigger_delete_expired_documents, name='trigger_delete_expired_documents'),
    # path('delete_recipients_byDocId/<int:doc_id>/', DeleteRecipientByDocIdView.as_view(), name='delete_recipients_by_doc_id'),

    # celery
    path('send-email/', send_email, name='send_email'),
    path('',document_views.test,name="test"),
    path('sendmail/',document_views.send_mail_to_all,name="sendmail"),
    path('get_email_list/', document_views.get_email_list, name='get_email_list'),
    
    # aws
    path('upload_file_to_s3/', upload_file_to_s3, name='upload_file_to_s3'),
    path('upload_template_file_to_s3/', upload_template_file_to_s3, name='upload_template_file_to_s3'),
    path('fetch_pdf_from_s3/<str:bucket_name>/<str:file_name>/', fetch_pdf_from_s3, name='fetch_pdf_from_s3'),
    path('fetch_templateFile_from_s3/<str:bucket_name>/<str:template_bucket_name>/<str:file_name>/', fetch_templateFile_from_s3, name='fetch_templateFile_from_s3'),
    path('generate_presigned_url/<str:bucket_name>/<str:file_name>/', generate_presigned_url, name='generate_presigned_url'),
    path('delete_file_from_s3/', delete_file_from_s3, name='delete_file_from_s3'),
    path('delete_template_from_s3/', delete_template_from_s3, name='delete_template_from_s3'),
    path('fetch_TemplatePdfs/<str:user_bucket_name>/', fetch_and_convert_pdf_from_s3, name='fetch_and_convert_pdf_from_s3'),


    # dashboard
    path('getRecipientCount/',getRecipientCount.as_view()),
    path('getPendingRecipientCount/',getPendingRecipientCount.as_view()),
    path('getRecipientDetails/',getRecipientDetails.as_view()),
    path('getStatus/',getStatus.as_view()),
    path('deleteDocument/',deleteDocumentView.as_view()),
    path('getDocuments/',DocumentView2.as_view()),

    #bulk pdf signing
    path('save_multiple_doc/',bulkpdfsigning_views.save_multiple_doc),

    path('getCombinedDocuments/',CombinedDocumentView.as_view()),

    
    # Log
    # path('apilog/', ApiLogViewset.as_view({'get': 'list', 'post': 'create'}), name='apilog'),
    # path('apilog/', ApiLogViewset.as_view({'get': 'list', 'post': 'create'}), name='apilog'),
]
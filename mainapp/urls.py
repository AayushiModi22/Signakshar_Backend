from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from mainapp import views
from django.urls import path,include
from .views import Registerview
from . import views
from .views import LoginView,logoutview,updateTemplateDraggedData,FetchUserDetailsView
from .views import UserView,TemplateViewSet,TemplateDraggedDataViewset,trigger_delete_expired_documents
# from .views import UserDataView
from .views import google_auth_callback
 
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from mainapp import views
from django.urls import path,include
from .views import Registerview
from . import views
from .views import LoginView,logoutview,updateTemplateDraggedData,DocumentTableViewset,UseTemplateRecipientViewSet,DocumentByDocId,use_template_recipient_didTidCid,fetch_pdf_from_s3
from .views import UserView,TemplateViewSet,TemplateRecipientViewset,TemplateDraggedDataViewset,TemplateRecipientByTemplateId,TemplateByTemplateId,GetDraggedDataByTempRec,send_email,sendOtp,verifyOtp,forgetPassword,CurrentUserView,DocAllRecipientById,GetDraggedDataByDocRec,sequence_email_approval,DocumentView2,deleteDocumentView,EmailListAPIView,DocumentRecipientDetailAPIView
from .views import deleteTemplate,googleLogIn,UserUpdateView,getRecipientCount,getPendingRecipientCount,getRecipientDetails,getStatus
from .views import get_doc,upload_file_to_s3,generate_presigned_url,save_multiple_doc,delete_file_from_s3
# ,GoogleLoginApi
 
urlpatterns = [

     # //////// sakshi urls
    path('getRecipientCount/',getRecipientCount.as_view()),
    path('getPendingRecipientCount/',getPendingRecipientCount.as_view()),
    path('getRecipientDetails/',getRecipientDetails.as_view()),
    path('getStatus/',getStatus.as_view()),
    path('save_multiple_doc/',views.save_multiple_doc),
    # /////////////

    path('register/', Registerview.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
 
    # otp
    path('sendOtp/',sendOtp,name="sendOtp"),
    path('verifyOtp/',verifyOtp,name="verifyOtp"),
    path('forgetPassword/',forgetPassword,name="forgetPassword"),
 
 
    path('DocumentTableapi/', DocumentTableViewset.as_view({'get': 'list', 'post': 'create'}), name='docTable_api'),
   
    path('templateapi/', TemplateViewSet.as_view({'get': 'list', 'post': 'create'}), name='template_api'),
    path('templateDraggedDataApi/', TemplateDraggedDataViewset.as_view({'get': 'list', 'post': 'create'}), name='draggeddata_api'),
    path('getDraggedDataByTempRec/<int:template_rec_id>/', GetDraggedDataByTempRec.as_view(), name='get_dragged_data_by_temp_rec'),
    path('deleteTemplate/',deleteTemplate.as_view()),


    path('TemplateRecipient/', TemplateRecipientViewset.as_view({'get': 'list', 'post': 'create'}), name='tempRec_api'),
    path('useTemplateRecipientApi/', UseTemplateRecipientViewSet.as_view({'get': 'list', 'post': 'create'}), name='usetempRec_api'),
    path('use_template_recipient_didTidCid/<int:document_id>/<int:template_id>/<int:creator_id>/', use_template_recipient_didTidCid),
 
    path('TemplateRecipientByTemplateId/<int:template_id>/', TemplateRecipientByTemplateId.as_view(), name='template_by_template_id'),
   
    path('TemplateByTemplateId/<int:template_id>/', TemplateByTemplateId.as_view(), name='template_rec_by_template_id'),
    path('DocumentByDocId/<int:doc_id>/', DocumentByDocId.as_view(), name='doc_by_doc_id'),
    # path('template_dragged_data/<int:template_id>/', TemplateDraggedDataByTemplateId.as_view(), name='template_dragged_data_by_template_id'),
    path('updateTemplateDraggedData/<int:pk>/', updateTemplateDraggedData),
 
#sendemail
    path('send-email/', send_email, name='send_email'),
 
    # path('testData/<int:item_id>/', getItem, name='get_item'),
    # path('user/', UserDataView.as_view()),
    path('logout/', logoutview.as_view()),
    # path('social-auth/',include('social_django.urls',namespace='social')),
    # path('auth/', include('social_django.urls', namespace='social')),
    # path('auth/google/callback/', google_auth_callback, name='google_auth_callback'),
    # path('auth/api/login/google/', GoogleLoginApi.as_view(), name="GoogleLoginApi"),

    #//--------------profile
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
 
#//=================== aws
    path('upload_file_to_s3/', upload_file_to_s3, name='upload_file_to_s3'),
    # path('create_bucket/', create_bucket, name='create_bucket'),
    # path('upload_file_to_existing_bucket/', upload_file_to_existing_bucket, name='upload_file_to_existing_bucket'),
    path('fetch_pdf_from_s3/<str:bucket_name>/<str:file_name>/', fetch_pdf_from_s3, name='fetch_pdf_from_s3'),
    path('generate_presigned_url/<str:bucket_name>/<str:file_name>/', generate_presigned_url, name='generate_presigned_url'),
    path('delete_file_from_s3/', delete_file_from_s3, name='delete_file_from_s3'),


    path('user-details/<int:user_id>/', FetchUserDetailsView.as_view(), name='fetch_user_details'),

# ===================================================================================
# celery
# ===================================================================================
    path('',views.test,name="test"),
    path('sendmail/',views.send_mail_to_all,name="sendmail"),
    # path('schedulemail/',views.schedule_mail,name="schedulemail"),
    # path('schedule_email/', views.schedule_email, name='schedule_email'),
    # path('send_emails/', views.send_emails, name='send_emails'),
    # path('email_approval/<int:email_id>/', views.email_approval, name='email_approval'),
    path('get_email_list/', views.get_email_list, name='get_email_list'),


    path("save_doc/",views.save_doc),
    path("get_doc/",views.get_doc),
    path("save_doc_positions/",views.save_recipient_position_data),
    path('current-user/',CurrentUserView.as_view(),name='current-user'),
    path('DocAllRecipientById/<int:Doc_id>/', DocAllRecipientById.as_view(), name='DocAllRecipientById'),
    path('DocApprove/', views.sequence_email_approval, name='DocApprove'),


    path('GetDraggedDataByDocRec/<int:docId>/<int:docRecipientdetails_id>', GetDraggedDataByDocRec.as_view(), name='GetDraggedDataByDocRec'),

# Home page changes of backend
    path('deleteDocument/',deleteDocumentView.as_view()),
    path('getDocuments/',DocumentView2.as_view()),

# Google Loin
    path('googleLogIn/',views.googleLogIn, name="googleLogIn"),
    path('trigger_delete_expired_documents/', trigger_delete_expired_documents, name='trigger_delete_expired_documents'),

    path('email-list/<int:docId>/<str:recEmail>/', EmailListAPIView.as_view(),name='email-list-api'),
    path('document-recipient-detail/<int:docId>/<str:recEmail>/', DocumentRecipientDetailAPIView.as_view(), name='document-recipient-detail-api'),


]


    
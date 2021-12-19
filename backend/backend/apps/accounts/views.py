"""account view"""
import datetime
import logging
import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models.models import CustomUser, ProvisionalUser
from .serializers import ChangePasswordSerializer, CreateUserSerializer, NativeLoginSerializer, \
    ProvisionalUserSerializer, UserSerializer
from ...commons.error_format import format_error
from ...commons.response import failure_response, success_response

logger = logging.getLogger('django')


# NO CONTENT と言っておきながら実際には '{}'というデータを返しているので正しくない
@api_view(['GET', 'DELETE'])
def empty_dict_response_with_204(request):
    """Test of 204 no content response"""
    return Response({}, status=status.HTTP_204_NO_CONTENT)


# 正しい
@api_view(['GET', 'DELETE'])
def just_empty_response_with_204(request):
    """Test of 204 no content response"""
    return Response(status=status.HTTP_204_NO_CONTENT)


# 正しい
@api_view(['GET', 'DELETE'])
def empty_dict_response_with_200(request):
    """Test of 204 no content response"""
    return Response({}, status=status.HTTP_200_OK)


# 正しい（200でNO CONTENTは、仕様上間違いではない）
@api_view(['GET', 'DELETE'])
def just_empty_response_with_200(request):
    """Test of 204 no content response"""
    return Response(status=status.HTTP_200_OK)


@ensure_csrf_cookie
def set_csrf_token(request):
    """Set csrf token by set-cookie"""
    return JsonResponse({'detail': 'CSRF cookie set'}, status=status.HTTP_200_OK)


class Login(APIView):
    """Login view"""

    @swagger_auto_schema(responses={200: UserSerializer()}, request_body=NativeLoginSerializer)
    def post(self, request):
        """Login."""
        serializer = NativeLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({'errors': {'__all__': 'Please enter both username and password'}},
                                status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=serializer.validated_data['email'],
                            password=serializer.validated_data['password'])
        if user is not None:
            user_detail: CustomUser = CustomUser.objects.get_by_natural_key(
                username=user)
            login(request, user)
            return JsonResponse({'user': UserSerializer(user_detail).data},
                                status=status.HTTP_200_OK)

        return JsonResponse({
            'detail': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class AccountViewBase(APIView):
    """Base class of account views in session."""
    permission_classes = [IsAuthenticated]


class UserViews(AccountViewBase):
    """User detail view"""

    def get(self, _req):
        """retrieve user detail"""

        return Response({'user': UserSerializer(self.request.user).data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserSerializer)
    def put(self, request):
        """update user detail"""
        user = self.request.user
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    """Change password view"""

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def put(self, request):
        """Change password."""
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not user.check_password(old_password):
                return Response({"old_password": ["パスワードが間違っています。"]},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.save()

            # Forcibly logout after changing password
            logout(request)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailAddress(APIView):
    """Change email address view"""

    # TODO: ChangePassword のように、メアド変更APIを作成
    # やること
    # 1. シリアライザーを実装（ChangePasswordSerializerを参考に）
    # 2. ChangeEmailAddressを実装
    # 3. 動作確認（ルーティングはすでに urls.py に書かれている。またはswaggerで確認。）


class APIViewWithoutAnyAuthentication(APIView):
    """For views those don't require authentication nor csrf check"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]


class Logout(APIViewWithoutAnyAuthentication):
    """Logout view"""

    def post(self, request):
        """Logout from current session."""
        logout(request)
        return Response(success_response({}, name='Logout', message='Logged out'))


class ProvisionalSignup(APIViewWithoutAnyAuthentication):
    """Provisional signup view"""

    @swagger_auto_schema(request_body=ProvisionalUserSerializer)
    def post(self, request):
        """provisional signup request
        1. provisional signup with email address
        2. generate signup link and send the link to the user via email
        """

        # Try logout to make sure to remove session cookie and csrf cookie
        logout(request)

        serializer = ProvisionalUserSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning('Provisional registration failed, %s', f'{serializer.errors}')
            # Give no any feedback to the client for security
            return JsonResponse(success_response({}))

        email = serializer.validated_data['email']

        try:
            provisional_user = ProvisionalUser.objects.create(email=email)
        except IntegrityError:
            # recreate and overwrite fields if already exist
            provisional_user = ProvisionalUser(email=email)
            provisional_user.save()

        current_site = get_current_site(self.request)
        domain = current_site.domain
        domain = re.sub(r'^api\.', '', domain)

        message_template = get_template('signup-link-message.txt')
        context = {
            'domain': settings.DOMAIN_FOR_SEND_EMAIL,
            'link_str': provisional_user.link_str,
        }

        subject = '【SurpassOne】仮登録のお知らせ／本登録のお願い'
        message = message_template.render(context)
        from_email = settings.EMAIL_HOST_USER
        mail_to = [provisional_user.email]
        send_mail(subject, message, from_email, mail_to)

        return JsonResponse(success_response({}))


class ProceedSignup(APIView):
    """Proceed signup view"""

    # set csrf token before signup
    @method_decorator(ensure_csrf_cookie)
    def get(self, _req, uuid4=None):
        """proceed signup if valid
        1. validate signup link
        2. validate if within expiration datetime
        3. return temporarily registered email address
        """

        invalid_link_response = JsonResponse(
            failure_response('InvalidLink', 'This URL is invalid.'),
            status=status.HTTP_400_BAD_REQUEST)

        if uuid4 is None:
            return invalid_link_response

        try:
            provisional_user: ProvisionalUser = ProvisionalUser.objects.get(link_str=uuid4)

        except ProvisionalUser.DoesNotExist:
            return invalid_link_response

        # Timezone must be the same as of settings.
        if datetime.datetime.now(datetime.timezone.utc) > provisional_user.expired_at:
            return JsonResponse(failure_response('ExpiredLink', 'This URL is expired.'),
                                status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(success_response({'email': provisional_user.email}),
                            status=status.HTTP_200_OK)


class Signup(APIView):
    """Signup view"""

    # FIXME: カスタムヘッダー付与できない問題が解決したら復活させる
    # refs: https://github.com/aitit-inc/q-it/issues/232
    # @method_decorator(csrf_protect)
    @swagger_auto_schema(responses={200: UserSerializer()}, request_body=CreateUserSerializer)
    def post(self, request):
        """signup post request
        1. validate that this provisional user exists and is within expiration datetime
        2. signup
        2. authenticate
        3. login
        """
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(
                failure_response(
                    'InvalidFields',
                    'Invalid values found in the request data.',
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email'].strip()
        password = serializer.validated_data['password'].strip()
        password_confirmation = serializer.validated_data['password_confirmation'].strip()
        name = serializer.validated_data['first_name'].strip()

        if password != password_confirmation:
            return JsonResponse(failure_response('UnmatchedPassword', 'Passwords don\'t match.'),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            provisional_user = ProvisionalUser.objects.get(email=email)
        except ProvisionalUser.DoesNotExist:
            msg = f'This email address, `{email}`, is not authenticated.'
            logger.error(msg)
            return JsonResponse(failure_response('UnauthenticatedProvisionalUser', msg),
                                status=status.HTTP_400_BAD_REQUEST)

        # Timezone must be the same as of settings.
        if datetime.datetime.now(datetime.timezone.utc) > provisional_user.expired_at:
            msg = 'This provisional user is expired.'
            logger.warning(msg)
            return JsonResponse(
                failure_response('ExpiredProvisionalUser', msg),
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            CustomUser.objects.create_user(email, password, name)
        except IntegrityError as err:
            return JsonResponse(failure_response('UserAlreadyExists',
                                                 f'This email address, `{email}`, already exists.',
                                                 format_error(err)),
                                status=status.HTTP_400_BAD_REQUEST)

        user_identifier: str = authenticate(username=email, password=password)
        if user_identifier is None:
            return JsonResponse(failure_response('InvalidCredential', 'Invalid credential'
                                                 ), status=status.HTTP_401_UNAUTHORIZED)

        user_detail: CustomUser = CustomUser.objects.get_by_natural_key(username=user_identifier)
        login(request, user_identifier)
        return Response(UserSerializer(user_detail).data, status=status.HTTP_201_CREATED)


class DebugLogView(APIView):
    """ debug view"""

    def get(self, _req):
        # FIXME: 一時的なデバッグ用ログ
        req_info = {
            'path': _req.path,
            'method': _req.method,
            'encoding': _req.encoding,
            'get parameters': [v for v in _req.GET.lists()],
            'post data': [v for v in _req.POST.lists()],
            'cookies': _req.COOKIES,
            'files': [f.name for f in _req.FILES],
            'meta': _req.META,
            'user': _req.user,
        }

        # logger.debug(req_info)
        logger.info(req_info)
        # logger.warning(req_info)

        return Response({}, status=status.HTTP_200_OK)

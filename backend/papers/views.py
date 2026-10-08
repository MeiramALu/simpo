from django.http import FileResponse, Http404
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.emails import notify_organizers, send_localized
from config.i18n import tr
from siteconfig.models import SiteSettings, closed_message

from .models import Paper, PublicationFee
from .serializers import PaperSerializer, PaperUpdateSerializer


class IsEmailVerified(permissions.BasePermission):
    @property
    def message(self):
        return tr('need_verified_email')

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or not SiteSettings.load().require_verified_email:
            return True
        return request.user.is_authenticated and request.user.email_verified


class PaperListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/papers/ — мои статьи
    POST /api/papers/ — подать статью (multipart/form-data с полем file)
    """
    serializer_class = PaperSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Paper.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not SiteSettings.load().papers_is_open:
            return Response({'detail': closed_message('papers')}, status=status.HTTP_403_FORBIDDEN)
        target = request.data.get('target', Paper.Target.PROCEEDINGS)
        if PublicationFee.objects.filter(target=target, is_active=False).exists():
            return Response({'target': [tr('target_closed')]}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        p = serializer.save(user=self.request.user)
        u = self.request.user
        send_localized('paper_received', u.email, u.lang, name=u.full_name, title=p.title)
        notify_organizers(f'Новая статья: {p.title}',
                          f'Автор: {u.full_name} <{u.email}>\nАвторы: {p.authors}\nИздание: {p.get_target_display()}\n'
                          f'Направление: {p.direction}\n\nАннотация:\n{p.abstract}')


class PaperDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/papers/<id>/
    PATCH /api/papers/<id>/ — правка, пока статья «Подана» или «Нужна доработка».
          После доработки статус возвращается в «Подана».
    """
    serializer_class = PaperUpdateSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        return Paper.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        p = self.get_object()
        if p.status not in Paper.EDITABLE_STATUSES:
            return Response({'detail': tr('paper_locked')}, status=status.HTTP_400_BAD_REQUEST)
        was_revision = p.status == Paper.Status.REVISION
        response = super().update(request, *args, partial=True)
        if was_revision:
            p.refresh_from_db()
            p.status = Paper.Status.SUBMITTED
            p.save(update_fields=['status', 'updated_at'])
            notify_organizers(f'Доработанная статья: {p.title}', f'Автор загрузил исправленную версию статьи #{p.pk}.')
            response.data = self.get_serializer(p).data
        return response


class PaperWithdrawView(APIView):
    """POST /api/papers/<id>/withdraw/"""
    def post(self, request, pk):
        p = Paper.objects.filter(user=request.user, pk=pk).first()
        if not p:
            raise Http404
        if p.status in (Paper.Status.PUBLISHED, Paper.Status.WITHDRAWN) or p.is_paid:
            return Response({'detail': tr('paper_no_withdraw')}, status=status.HTTP_400_BAD_REQUEST)
        p.status = Paper.Status.WITHDRAWN
        p.save(update_fields=['status', 'updated_at'])
        notify_organizers(f'Статья отозвана: {p.title}', f'Автор отозвал статью #{p.pk}.')
        return Response(PaperSerializer(p, context={'request': request}).data)


class PaperFileView(APIView):
    """GET /api/papers/<id>/file/ — скачать рукопись (автор или сотрудник оргкомитета)."""
    def get(self, request, pk):
        qs = Paper.objects.all() if request.user.has_perm('papers.view_paper') else Paper.objects.filter(user=request.user)
        p = qs.filter(pk=pk).first()
        if not p or not p.file:
            raise Http404
        return FileResponse(p.file.open('rb'), as_attachment=True, filename=p.original_filename or p.file.name.rsplit('/', 1)[-1])

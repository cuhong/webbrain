from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('필수 항목입니다.')
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email=CustomUserManager.normalize_email(email),
                                name=name,
                                password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = verbose_name

    email = models.EmailField(
        verbose_name='이메일',
        max_length=255,
        unique=True,
        db_index=True
    )
    name = models.CharField(
        verbose_name='이름',
        max_length=30,
    )
    is_active = models.BooleanField(
        verbose_name='활성화',
        default=True,
        help_text='사용자를 삭제하는 대신 활성화를 해제하세요.'
    )
    date_joined = models.DateTimeField(
        verbose_name='가입일',
        auto_now_add=True
    )
    is_staff = models.BooleanField(
        verbose_name='관리자',
        default=False
    )
    is_researcher = models.BooleanField(
        verbose_name='연구자',
        default=False
    )
    is_researcher_accepted_at = models.DateTimeField(
        verbose_name='연구자 승인 일시',
        null=True, blank=True, editable=False
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('name', )

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return "{name}({email})".format(name=self.name, email=self.email)


class StaffUser(CustomUser):
    class Meta:
        verbose_name = '관리자'
        verbose_name_plural = verbose_name
        proxy = True


class ResearcherUser(CustomUser):
    class Meta:
        verbose_name = '연구자'
        verbose_name_plural = verbose_name
        proxy = True


class ParticipantUser(CustomUser):
    class Meta:
        verbose_name = '참여자'
        verbose_name_plural = verbose_name
        proxy = True

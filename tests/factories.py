import factory
from django.contrib.auth import get_user_model
from users.models import Skill, ProgrammingLanguage, Follow
from posts.models import Post, Comment, PostLike, CommentLike
from projects.models import Project, ProjectCollaborator, CollaborationRequest
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    full_name = factory.Faker('name')
    bio = factory.Faker('paragraph', nb_sentences=3)
    is_active = True


class ProgrammingLanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgrammingLanguage
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f'Language {n}')


class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f'Skill {n}')
    category = factory.Iterator(['frontend', 'backend', 'devops', 'mobile', 'data'])


class FollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Follow

    follower = factory.SubFactory(UserFactory)
    following = factory.SubFactory(UserFactory)


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    content = factory.Faker('paragraph')
    code_snippet = factory.Faker('text', max_nb_chars=200)
    programming_language = factory.SubFactory(ProgrammingLanguageFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    content = factory.Faker('text', max_nb_chars=100)


class PostLikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostLike

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)


class CommentLikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentLike

    user = factory.SubFactory(UserFactory)
    comment = factory.SubFactory(CommentFactory)


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    creator = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=5)
    description = factory.Faker('paragraph')
    repo_url = factory.Faker('url')
    status = 'active'

    @factory.post_generation
    def tech_stack(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for skill in extracted:
                self.tech_stack.add(skill)
        else:
            # Add 3 default skills
            for _ in range(3):
                self.tech_stack.add(SkillFactory())


class ProjectCollaboratorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectCollaborator

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    role = 'contributor'


class CollaborationRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CollaborationRequest

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    message = factory.Faker('paragraph', nb_sentences=2)
    status = 'pending'


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    recipient = factory.SubFactory(UserFactory)
    sender = factory.SubFactory(UserFactory)
    type = factory.Iterator(['like', 'comment', 'follow', 'mention', 'project_invite', 'project_request'])
    is_read = False
    text = factory.LazyAttribute(lambda obj: f"{obj.sender.username} performed action {obj.type}")

    @factory.lazy_attribute
    def content_type(self):
        if self.type in ['like', 'comment', 'mention']:
            return ContentType.objects.get_for_model(Post)
        elif self.type in ['project_invite', 'project_request']:
            return ContentType.objects.get_for_model(Project)
        else:  # follow
            return ContentType.objects.get_for_model(User)

    @factory.lazy_attribute
    def object_id(self):
        if self.type in ['like', 'comment', 'mention']:
            return PostFactory().id
        elif self.type in ['project_invite', 'project_request']:
            return ProjectFactory().id
        else:  # follow
            return UserFactory().id 
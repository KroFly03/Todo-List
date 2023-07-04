from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.models import User
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.editable_roles)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')

    def validate_user(self, user: User):
        if self.context['request'].user == user:
            raise ValidationError('Failed to change your role')
        return user


class BoardWithParticipantSerializer(BoardSerializer):
    participants = BoardParticipantSerializer(many=True)

    def update(self, instance: Board, validated_data):
        request = self.context['request']

        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=request.user).delete()
            BoardParticipant.objects.bulk_create([
                BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                for participant in validated_data.get('participants', [])],
                ignore_conflicts=True
            )

            if title := validated_data.get('title'):
                instance.title = title

            instance.save()

        return instance


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def validate_board(self, board: Board):
        if board.is_deleted:
            raise ValidationError('Board is deleted')

        if not BoardParticipant.objects.filter(board_id=board.id,
                                               role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                                               user_id=self.context['request'].user).exists():
            raise PermissionDenied

        return board


class GoalCategoryWithUserSerializer(GoalCategorySerializer):
    user = UserSerializer(read_only=True)


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, category: GoalCategory):
        if category.is_deleted:
            raise ValidationError('Category is deleted.')

        if not BoardParticipant.objects.filter(board_id=category.board_id,
                                               role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                                               user_id=self.context['request'].user).exists():
            raise PermissionDenied

        return category


class GoalWithUserSerializer(GoalSerializer):
    user = UserSerializer(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def validate_goal(self, goal: Goal):
        if goal.status == Goal.Status.archived:
            raise ValidationError('Goal not found')

        if not BoardParticipant.objects.filter(board_id=goal.category.board_id,
                                               role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                                               user_id=self.context['request'].user).exists():
            raise PermissionDenied

        return goal


class GoalCommentWithUserSerializer(GoalCommentSerializer):
    user = UserSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)

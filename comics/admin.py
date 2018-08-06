from django.contrib import admin

from .models import Creator, Credits, Issue, Publisher, Series, Settings


UNREAD = 0
READ = 2


def create_msg(rows_updated):
    if rows_updated == 1:
        message_bit = "1 item was"
    else:
        message_bit = "%s items were" % rows_updated

    return message_bit


@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('cvid', 'cvurl')
    actions = ['refresh_creator_metadata']
    fieldsets = (
        (None, {
            'fields': ('cvid', 'cvurl', 'name', 'slug', 'desc', 'image')
        }),
    )


@admin.register(Credits)
class RolesAdmin(admin.ModelAdmin):
    search_fields = ('issue__series__name', 'issue__number')
    list_filter = ('issue__import_date', 'role')
    list_display = ('issue', 'creator')
    ordering = ('issue', 'creator')
    filter_horizontal = ['role']
    autocomplete_fields = ['issue', 'creator']
    # form view
    fieldsets = (
        (None, {'fields': ('issue', 'creator')}),
        ('Related', {'fields': ('role',)}),
    )


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    search_fields = ('series__name',)
    readonly_fields = ('file', 'cvid', 'cvurl', 'series', 'number')
    list_display = ('__str__', 'status', 'import_date')
    list_filter = ('import_date', 'date', 'status')
    list_select_related = ('series',)
    date_hierarchy = 'date'
    actions = ['mark_as_read', 'mark_as_unread']
    fieldsets = (
        (None, {
            'fields': ('series', 'number', 'cvid', 'cvurl', 'name',
                       'slug', 'date', 'desc', 'image', 'status')
        }),
    )

    def get_queryset(self, request):
        queryset = (
            Issue.objects
            .select_related('series')
        )
        return queryset

    def mark_as_read(self, request, queryset):
        rows_updated = queryset.update(status=READ)
        message_bit = create_msg(rows_updated)
        self.message_user(
            request, "%s successfully marked as read." % message_bit)
    mark_as_read.short_description = 'Mark selected issues as read'

    def mark_as_unread(self, request, queryset):
        rows_updated = queryset.update(status=UNREAD)
        message_bit = create_msg(rows_updated)
        self.message_user(
            request, "%s successfully marked as unread." % message_bit)
    mark_as_unread.short_description = 'Mark selected issues as unread'


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'series_count',)
    readonly_fields = ('cvid', 'cvurl')
    fieldsets = (
        (None, {
            'fields': ('cvid', 'cvurl', 'name', 'slug', 'desc', 'image')
        }),
    )

    def get_queryset(self, request):
        queryset = (
            Publisher.objects
            .prefetch_related('series_set')
        )
        return queryset


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'year', 'issue_count')
    list_filter = ('publisher',)
    readonly_fields = ('cvid', 'cvurl')
    actions = ['mark_as_read', 'mark_as_unread']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('cvid', 'cvurl', 'name', 'slug', 'desc')
        }),
    )

    def get_queryset(self, request):
        queryset = (
            Series.objects
            .select_related('publisher')
            .prefetch_related('issue_set')
        )
        return queryset

    def mark_as_read(self, request, queryset):
        issues_count = 0
        for i in range(queryset.count()):
            issues_updated = Issue.objects.filter(
                series=queryset[i]).update(status=READ)
            issues_count += issues_updated
        message_bit = create_msg(issues_count)
        self.message_user(
            request, "%s successfully marked as read." % message_bit)
    mark_as_read.short_description = 'Mark selected Series as read'

    def mark_as_unread(self, request, queryset):
        issues_count = 0
        for i in range(queryset.count()):
            issues_updated = Issue.objects.filter(
                series=queryset[i]).update(status=UNREAD)
            issues_count += issues_updated
        message_bit = create_msg(issues_count)
        self.message_user(
            request, "%s successfully marked as unread." % message_bit)
    mark_as_unread.short_description = 'Mark selected Series as unread'


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    fieldsets = ((None, {'fields': ('api_key', 'comics_directory')}),)

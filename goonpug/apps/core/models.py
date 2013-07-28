# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, \
    UserManager
from django.utils import timezone


class Match(models.Model):

    STATUS_UNKNOWN = 0
    STATUS_PENDING = 1
    STATUS_LIVE = 2
    STATUS_COMPLETE = 3
    STATUS_CANCELLED = 4
    STATUS = (
        (STATUS_UNKNOWN, 'Unknown'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_LIVE, 'Live'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    RULESET_CUSTOM = 0
    RULESET_ESEA = 1
    RULESET_CEVO = 2
    RULESET = (
        (RULESET_CUSTOM, 'Custom'),
        (RULESET_ESEA, 'ESEA/ESL'),
        (RULESET_CEVO, 'CEVO'),
    )

    MAP_MODE_BO1 = 0
    MAP_MODE_BO2 = 1
    MAP_MODE_BO3 = 2
    MAP_MODE = (
        (MAP_MODE_BO1, 'Standard'),
        (MAP_MODE_BO2, 'Best of 2'),
        (MAP_MODE_BO3, 'Best of 3'),
    )

    TEAM_OTHER = 0
    TEAM_A = 1
    TEAM_B = 2
    TEAM = (
        (TEAM_OTHER, 'Other'),
        (TEAM_A, 'Team A'),
        (TEAM_B, 'Team B'),
    )

    SIDE_OTHER = 0
    SIDE_CT = 1
    SIDE_T = 2
    SIDE = (
        (SIDE_OTHER, 'Other'),
        (SIDE_CT, 'CT'),
        (SIDE_T, 'T'),
    )

    name = models.CharField(max_length=64, blank=True)
    server = models.ForeignKey('Server')
    season = models.ForeignKey('Season')
    team_a = models.ForeignKey('Team', related_name='match_team_a')
    team_b = models.ForeignKey('Team', related_name='match_team_b')
    status = models.IntegerField(choices=STATUS, default=STATUS_PENDING)
    paused = models.BooleanField(default=False)
    score_a = models.IntegerField()
    score_b = models.IntegerField()
    ruleset = models.IntegerField(choices=RULESET, default=RULESET_ESEA)
    config_ot = models.BooleanField(default=True)
    config_knife_round = models.BooleanField(default=False)
    config_password = models.CharField(max_length=64, blank=True)
    map_mode = models.IntegerField(choices=MAP_MODE, default=MAP_MODE_BO1)
    current_map = models.IntegerField()
    start_time = models.DateTimeField()


class MatchMap(models.Model):

    match = models.ForeignKey('Match')
    map_name = models.CharField(max_length=64)
    score_1 = models.IntegerField()
    score_2 = models.IntegerField()
    current_period = models.IntegerField()
    zip_url = models.CharField(max_length=256)
    sha1sum = models.CharField(max_length=40, unique=True)
    has_demo = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class MatchMapScore(models.Model):

    SCORE_TYPE_REGULATION = 0
    SCORE_TYPE_OT = 1
    SCORE_TYPE = (
        (SCORE_TYPE_REGULATION, 'Regulation'),
        (SCORE_TYPE_OT, 'OT')
    )

    match_map = models.ForeignKey('MatchMap')
    score_type = models.IntegerField(choices=SCORE_TYPE,
                                     default=SCORE_TYPE_REGULATION)
    score1_half1 = models.IntegerField()
    score1_half2 = models.IntegerField()
    score2_half1 = models.IntegerField()
    score2_half2 = models.IntegerField()


class Player(AbstractBaseUser, PermissionsMixin):

    # django auth fields
    username = models.CharField(max_length=64)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['steamid']

    # steam community fields
    steamid = models.BigIntegerField(unique=True)
    profileurl = models.CharField(max_length=256)
    avatar = models.CharField(max_length=256)
    avatarmedium = models.CharField(max_length=256)
    avatarfull = models.CharField(max_length=256)

    # goonpug specific fields
    is_banned = models.BooleanField(default=False)
    reputation = models.IntegerField(default=0)
    rating = models.FloatField(default=25.0)
    rating_variance = models.FloatField(default=8.333)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class PlayerBan(models.Model):

    player = models.ForeignKey('Player')
    start = models.DateField()
    end = models.DateField()
    reason = models.CharField(max_length=256)
    link = models.CharField(max_length=256)


class PlayerIp(models.Model):

    player = models.ForeignKey('Player')
    ip = models.CharField(max_length=16)

    class Meta:
        unique_together = (('player', 'ip'),)


class PlayerKill(models.Model):

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    round = models.ForeignKey('Round')
    killer = models.ForeignKey(
        'Player', related_name='playerkill_player_killer')
    killer_team = models.IntegerField(choices=Match.SIDE)
    victim = models.ForeignKey(
        'Player', related_name='playerkill_player_victim')
    victim_team = models.IntegerField(choices=Match.SIDE)
    weapon = models.CharField(max_length=64)
    headshot = models.BooleanField()


class PlayerMatch(models.Model):

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    player = models.ForeignKey('Player')
    team = models.IntegerField(choices=Match.TEAM, default=Match.TEAM_OTHER)
    first_side = models.IntegerField(choices=Match.SIDE)
    current_side = models.IntegerField(choices=Match.SIDE)
    nickname = models.CharField(max_length=256)
    kills = models.IntegerField()
    assists = models.IntegerField()
    deaths = models.IntegerField()
    score = models.IntegerField()
    hsp = models.FloatField()
    defuses = models.IntegerField()
    plants = models.IntegerField()
    tks = models.IntegerField()
    clutch_v1 = models.IntegerField()
    clutch_v2 = models.IntegerField()
    clutch_v3 = models.IntegerField()
    clutch_v4 = models.IntegerField()
    clutch_v5 = models.IntegerField()
    k1 = models.IntegerField()
    k2 = models.IntegerField()
    k3 = models.IntegerField()
    k4 = models.IntegerField()
    k5 = models.IntegerField()
    adr = models.FloatField()
    rws = models.FloatField()
    rounds_won = models.IntegerField()
    rounds_lost = models.IntegerField()
    rounds_tied = models.IntegerField()


class PlayerMatchWeapons(models.Model):

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    player = models.ForeignKey('Player')
    weapon = models.CharField(max_length=64)
    headshots = models.IntegerField()
    hits = models.IntegerField()
    damage = models.IntegerField()
    kills = models.IntegerField()
    deaths = models.IntegerField()


class PlayerRound(models.Model):

    round = models.ForeignKey('Round')
    player = models.ForeignKey('Player')
    first_side = models.IntegerField(choices=Match.SIDE)
    current_side = models.IntegerField(choices=Match.SIDE)
    kills = models.IntegerField()
    assists = models.IntegerField()
    deaths = models.IntegerField()
    defuses = models.IntegerField()
    plants = models.IntegerField()
    tks = models.IntegerField()
    clutch_v1 = models.IntegerField()
    clutch_v2 = models.IntegerField()
    clutch_v3 = models.IntegerField()
    clutch_v4 = models.IntegerField()
    clutch_v5 = models.IntegerField()
    k1 = models.IntegerField()
    k2 = models.IntegerField()
    k3 = models.IntegerField()
    k4 = models.IntegerField()
    k5 = models.IntegerField()
    damage = models.IntegerField()
    rws = models.FloatField()


class PlayerSeason(models.Model):

    player = models.ForeignKey('Player')
    season = models.ForeignKey('Season')
    kills = models.IntegerField()
    assists = models.IntegerField()
    deaths = models.IntegerField()
    score = models.IntegerField()
    hsp = models.FloatField('headshot percentage')
    defuses = models.IntegerField('bomb defusals')
    plants = models.IntegerField()
    tks = models.IntegerField()
    clutch_v1 = models.IntegerField()
    clutch_v2 = models.IntegerField()
    clutch_v3 = models.IntegerField()
    clutch_v4 = models.IntegerField()
    clutch_v5 = models.IntegerField()
    k1 = models.IntegerField()
    k2 = models.IntegerField()
    k3 = models.IntegerField()
    k4 = models.IntegerField()
    k5 = models.IntegerField()
    adr = models.FloatField()
    rws = models.FloatField()
    rounds_won = models.IntegerField()
    rounds_lost = models.IntegerField()
    rounds_tied = models.IntegerField()
    matches_won = models.IntegerField()
    matches_lost = models.IntegerField()
    matches_tied = models.IntegerField()


class PlayerSeasonWeapons(models.Model):

    player = models.ForeignKey('Player')
    season = models.ForeignKey('Season')
    weapon = models.CharField(max_length=64)
    headshots = models.IntegerField()
    hits = models.IntegerField()
    damage = models.IntegerField()
    kills = models.IntegerField()
    deaths = models.IntegerField()


class Round(models.Model):

    WIN_TYPE_NORMAL = 0
    WIN_TYPE_DEFUSED = 1
    WIN_TYPE_EXPLODED = 2
    WIN_TYPE_SAVED = 3
    WIN_TYPE = (
        (WIN_TYPE_NORMAL, 'Normal'),
        (WIN_TYPE_DEFUSED, 'Bomb was defused'),
        (WIN_TYPE_EXPLODED, 'Bomb was exploded'),
        (WIN_TYPE_SAVED, 'Bomb site was saved')
    )

    match = models.ForeignKey('Match')
    match_map = models.ForeignKey('MatchMap')
    round_number = models.IntegerField()
    bomb_planted = models.BooleanField()
    bomb_defused = models.BooleanField()
    bomb_exploded = models.BooleanField()
    win_type = models.IntegerField(choices=WIN_TYPE, default=WIN_TYPE_NORMAL)
    team_win = models.IntegerField(choices=Match.TEAM)
    ct_win = models.BooleanField()
    t_win = models.BooleanField()
    score_a = models.IntegerField()
    score_b = models.IntegerField()
    backup_file_name = models.CharField(max_length=256)


class Season(models.Model):

    name = models.CharField(max_length=64)
    event = models.CharField(max_length=64)
    start = models.DateField()
    end = models.DateField()
    link = models.CharField(max_length=128)
    logo = models.CharField(max_length=256)
    is_active = models.BooleanField()


class Server(models.Model):

    name = models.CharField(max_length=128)
    ip = models.CharField(max_length=16)
    port = models.IntegerField(default=27015)
    gotv_ip = models.CharField(max_length=16, blank=True)
    gotv_port = models.IntegerField(default=27020)
    rcon = models.CharField(max_length=64, blank=True)

    class Meta:
        unique_together = (('ip', 'port'),)


class Team(models.Model):

    name = models.CharField(max_length=128)
    shorthandle = models.CharField(max_length=64)
    link = models.CharField(max_length=128)


class TeamSeason(models.Model):

    team = models.ForeignKey('Team')
    season = models.ForeignKey('Season')

#!/bin/env python3
# -*- coding: UTF-8 -*-

import os
import pathlib
import tempfile
from configparser import ConfigParser

config = ConfigParser()
path = ''
conf_path = str(pathlib.Path(os.path.abspath(__file__)).parent.parent) + "/conf.cfg" if len(str(path)) == 0 else path
config.read(os.path.abspath(conf_path), encoding="UTF-8")


def get_temp_dir_from_config():
    """
    从配置中获取临时存储目录，如果没有配置则使用默认目录
    """
    temp_dir = config['App']['temp_dir']
    return temp_dir


class ApiConfig:
    """A ApiConfig Class"""
    oauth2_uri = config['API']['oauth2_uri']
    token = config['API']['token']
    project_id = config['API']['project_id']

    @classmethod
    def update_token(cls, new_token):
        """Update token"""
        cls.token = new_token


class SSLConfig:
    """SSL证书校验"""
    verify = config['SSL']['verify']


class BaseConfig:
    """A BaseConfig Class"""
    timezone = 'Asia/Shanghai'
    # 所有事件都有的事件属性
    attr_all = ["$session", "$path", "$title", "$referrer_path", "$textValue", "$index", "$xpath",
                "$hyperlink",
                "$duration", "$page_count", "$package", "$platform", "$referrer_domain",
                "$utm_source",
                "$utm_medium", "$utm_campaign", "$utm_term", "$utm_content", "$ads_id",
                "$key_word",
                "$country_code", "$country_name", "$region", "$city", "$browser",
                "$browser_version", "$os",
                "$os_version", "$client_version", "$channel", "$device_brand", "$device_model",
                "$device_type",
                "$device_orientation", "$resolution", "$language", "$referrer_type",
                "$account_id",
                "$domain",
                "$ip", "$user_agent", "$sdk_version", "$location_latitude",
                "$location_longitude",
                "$bot_id", "eventId", "$query",
                "$traffic_source", "$traffic_source_session", "$utm_source_session", "$utm_medium_session",
                "$utm_campaign_session", "$utm_term_session", "$utm_content_session", "$share_title",
                "$target", "$from", "$share_path", "$share_query", "$defer", "$timezone_offset"
                ]


class FTPConfig:
    namespace = config['FTP']['ftp_namespace']
    host = config['FTP']['ftp_host']
    user = config['FTP']['ftp_user']
    password = config['FTP']['ftp_password']
    port = config['FTP']['ftp_port']


class SaasConfig:
    uri = config['SAAS']['saas_uri']
    token = config['SAAS']['saas_token']
    uid = config['SAAS']['saas_uid']